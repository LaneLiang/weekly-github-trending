"""Literature survey workflow — end-to-end literature review pipeline.

9-stage pipeline:
  1. NL parsing + CN→EN keyword translation
  2. Multi-source search (IEEE Xplore, Google Scholar, arXiv)
  3. Dedup + relevance ranking
  4. Batch full-text download (IEEE CARSI + arXiv direct)
  5. LLM batch summarization (5 papers/batch)
  6. Literature matrix (CSV + JSON)
  7. Research gap analysis
  8. BibTeX generation
  9. Review draft (optional)
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import logging
import os
import re
import subprocess
import time
import uuid
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

import yaml

from lanes_ceo.contracts import Artifact, CriticReview, Job
from lanes_ceo.workflows.utils import HUMANIZER_SUFFIX, PROJECT_OUTPUT_BASE, llm_chat, get_artifact_dir

logger = logging.getLogger("lanes_ceo.literature_survey")

ACTOR_SYSTEM = """你是 Lane 的学术文献调研助手。你需要执行一条完整的文献调研管线。

输入：用户自然语言描述的调研需求（可能含中文）
输出：结构化的文献矩阵、研究缺口分析、BibTeX 引用

重要约束：
- IEEE Xplore / Google Scholar / arXiv 三个源尽量覆盖
- 去重基于 title 归一化（小写/去标点/trim）
- 下载失败不阻塞管线，标记 pdf_path=null
- LLM 摘要 5 篇/批次
- 缺口分析至少识别 3 个研究空白"""

CRITIC_SYSTEM = """你是学术文献调研的审查员。请从以下维度审查调研报告的完整性和质量：

1. 检索覆盖面（25%）：所有可用源均尝试，failed_sources 不超 50%
2. 去重准确率（20%）：title 归一化后无重复条目
3. 摘要质量（25%）：每篇 ≤200 字，方法/贡献/局限标签齐全
4. 缺口分析深度（20%）：至少 3 个研究空白，每个有方向说明
5. BibTeX 格式（10%）：必填字段不缺失

输出：0-100 评分 + 问题清单。评分标准：全部达标=90+，有遗漏=扣分。"""

# ── config loading ──

def _load_config() -> dict:
    """Load literature_survey config, falling back to built-in defaults."""
    config_paths = [
        Path("config/literature_survey.yaml"),
        Path(__file__).parent.parent.parent.parent.parent.parent / "config" / "literature_survey.yaml",
    ]
    for p in config_paths:
        if p.exists():
            try:
                return yaml.safe_load(p.read_text(encoding="utf-8"))
            except Exception as exc:
                logger.warning("Failed to load config from %s: %s", p, exc)

    logger.warning("literature_survey.yaml not found, using built-in defaults")
    return {
        "search_sources": {
            "ieee": {"priority": 1, "enabled": True, "max_results": 30},
            "scholar": {"priority": 2, "enabled": True, "max_results": 20},
            "arxiv": {"priority": 3, "enabled": True, "max_results": 20},
        },
        "pipeline": {
            "default_max_papers": 30,
            "llm_batch_size": 5,
            "download_retries": 3,
            "download_timeout_seconds": 60,
            "idempotency_window_minutes": 30,
        },
    }


# ── Step 1: NL parsing + CN→EN translation ──

def _parse_nl_message(message: str) -> dict:
    """Extract keywords, year range, journals from natural language message.
    Handles Chinese input by translating keywords to English for API search."""
    result: dict[str, Any] = {
        "query_cn": message,
        "query_en": message,
        "keywords_en": [],
        "year_from": None,
        "journals": [],
        "max_papers": 30,
        "download_fulltext": True,
        "generate_review_draft": False,
    }

    # Detect review draft trigger words
    review_triggers = ["写综述", "生成综述", "综述草稿", "review draft", "write review", "literature review"]
    if any(t in message.lower() for t in review_triggers):
        result["generate_review_draft"] = True

    # Extract year constraints
    year_match = re.search(r"(\d{4})\s*年\s*后|since\s+(\d{4})|after\s+(\d{4})", message, re.IGNORECASE)
    if year_match:
        year = int(year_match.group(1) or year_match.group(2) or year_match.group(3) or "2020")
        result["year_from"] = year

    # Extract journal abbreviations
    journal_pattern = r"\b(TPE|TIE|JSSC|ISSCC|TCAS-I|TCAS-II|APEC|ECCE|Nature|Science)\b"
    result["journals"] = list(set(re.findall(journal_pattern, message, re.IGNORECASE)))

    # Extract paper count
    count_match = re.search(r"(\d+)\s*篇|至少\s*(\d+)|at\s+least\s+(\d+)", message)
    if count_match:
        result["max_papers"] = int(count_match.group(1) or count_match.group(2) or count_match.group(3) or "30")

    # CN→EN keyword translation via LLM
    if re.search(r"[一-鿿]", message):
        translation_prompt = (
            "请将以下中文科研调研需求中的核心关键词翻译为英文（空格分隔，仅输出关键词）：\n\n"
            f"{message}\n\n"
            "关键词（英文）："
        )
        translated = llm_chat("你是一个电力电子领域术语翻译助手。仅输出英文关键词，不做其他回复。", translation_prompt)
        if translated:
            result["query_en"] = translated.strip()
            result["keywords_en"] = [kw.strip() for kw in re.split(r"[,;\s]+", translated.strip()) if kw.strip()]
    else:
        result["keywords_en"] = [kw.strip() for kw in re.split(r"[,;\s]+", message) if kw.strip()]

    return result


# ── Step 2: Multi-source search ──

def _search_arxiv(keywords: list[str], max_results: int = 20) -> list[dict]:
    """Search arXiv API."""
    papers = []
    if not keywords:
        return papers
    query = "+AND+".join(f"all:{kw}" for kw in keywords[:3])
    url = f"http://export.arxiv.org/api/query?search_query={query}&max_results={max_results}&sortBy=relevance"
    try:
        import urllib.request
        import xml.etree.ElementTree as ET
        req = urllib.request.Request(url, headers={"User-Agent": "LiteratureSurvey/1.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            xml_data = resp.read().decode("utf-8")
        root = ET.fromstring(xml_data)
        ns = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
        for entry in root.findall("atom:entry", ns):
            title_el = entry.find("atom:title", ns)
            summary_el = entry.find("atom:summary", ns)
            arxiv_id_el = entry.find("atom:id", ns)
            papers.append({
                "title": (title_el.text or "").strip().replace("\n", " ") if title_el is not None else "",
                "authors": ", ".join(
                    (a.find("atom:name", ns).text or "").strip()
                    for a in entry.findall("atom:author", ns) if a is not None
                ),
                "year": int((entry.find("atom:published", ns).text or "2000")[:4]) if entry.find("atom:published", ns) is not None else 0,
                "abstract": (summary_el.text or "").strip()[:500] if summary_el is not None else "",
                "source": "arxiv",
                "doi": "",
                "journal": "arXiv preprint",
                "pdf_url": (arxiv_id_el.text or "").replace("abs", "pdf") if arxiv_id_el is not None else "",
            })
    except Exception as exc:
        logger.warning("arXiv search failed: %s", exc)
    return papers


def _search_ieee(keywords: list[str], max_results: int = 30, year_from: int | None = None) -> list[dict]:
    """Search IEEE Xplore via HTTP API."""
    papers = []
    if not keywords:
        return papers
    query = " ".join(keywords[:4])
    params = {"querytext": query, "max_records": min(max_results, 50), "format": "json"}
    if year_from:
        params["start_year"] = str(year_from)
    url = "https://ieeexplore.ieee.org/rest/search"
    try:
        import urllib.request
        data = json.dumps(params).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json", "User-Agent": "LiteratureSurvey/1.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))
        articles = result.get("articles", [])
        for a in articles:
            papers.append({
                "title": (a.get("title", "") or "").strip(),
                "authors": ", ".join(
                    f"{au.get('preferred_name','')} {au.get('last_name','')}".strip()
                    for au in (a.get("authors", {}).get("authors", []) or [])
                ),
                "year": int(a.get("publication_year", 0) or 0),
                "abstract": (a.get("abstract", "") or "")[:500],
                "source": "ieee",
                "doi": a.get("doi", ""),
                "journal": a.get("publication_title", ""),
                "citation_count": int(a.get("citing_paper_count", 0) or 0),
                "pdf_url": f"https://ieeexplore.ieee.org/document/{a.get('article_number','')}" if a.get("article_number") else "",
            })
        time.sleep(1)  # Rate limit
    except urllib.error.HTTPError as exc:
        if exc.code == 429:
            for retry in range(3):
                wait = 4 * (2 ** retry)
                logger.warning("IEEE API rate limited (429), retry %d/3 after %ds", retry + 1, wait)
                time.sleep(wait)
                try:
                    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json", "User-Agent": "LiteratureSurvey/1.0"})
                    with urllib.request.urlopen(req, timeout=30) as resp2:
                        result = json.loads(resp2.read().decode("utf-8"))
                    articles = result.get("articles", [])
                    for a in articles:
                        papers.append({
                            "title": (a.get("title", "") or "").strip(),
                            "authors": ", ".join(
                                f"{au.get('preferred_name','')} {au.get('last_name','')}".strip()
                                for au in (a.get("authors", {}).get("authors", []) or [])
                            ),
                            "year": int(a.get("publication_year", 0) or 0),
                            "abstract": (a.get("abstract", "") or "")[:500],
                            "source": "ieee",
                            "doi": a.get("doi", ""),
                            "journal": a.get("publication_title", ""),
                            "citation_count": int(a.get("citing_paper_count", 0) or 0),
                            "pdf_url": f"https://ieeexplore.ieee.org/document/{a.get('article_number','')}" if a.get("article_number") else "",
                        })
                    break  # Success, exit retry loop
                except Exception:
                    continue
            else:
                logger.warning("IEEE API rate limited after 3 retries, giving up")
        else:
            logger.warning("IEEE search failed (HTTP %s): %s", exc.code, exc)
    except Exception as exc:
        logger.warning("IEEE search failed: %s", exc)
    return papers


def _search_scholar(keywords: list[str], max_results: int = 20) -> list[dict]:
    """Search Google Scholar via scholarly library or fallback approaches.

    Tries, in order:
      1. scholarly library (Python) — best results, but rate-limited
      2. nature-academic-search skill via subprocess — if in Claude Code env
      3. Returns empty list with logging as last resort
    """
    query = " ".join(keywords)
    papers: list[dict] = []

    # ── Approach 1: scholarly library ──
    try:
        from scholarly import scholarly, ProxyGenerator
        pg = ProxyGenerator()
        success = pg.FreeProxies()
        if success:
            scholarly.use_proxy(pg)
        search_query = scholarly.search_pubs(query)
        count = 0
        for result in search_query:
            if count >= max_results:
                break
            try:
                bib = result.get("bib", {})
                papers.append({
                    "title": bib.get("title", ""),
                    "authors": bib.get("author", ""),
                    "year": int(bib.get("pub_year", 0) or 0),
                    "journal": bib.get("journal", ""),
                    "abstract": bib.get("abstract", ""),
                    "citation_count": result.get("num_citations", 0),
                    "pdf_url": bib.get("eprint_url", ""),
                    "source": "scholar",
                    "doi": bib.get("doi", ""),
                    "relevance_score": 0,
                })
                count += 1
            except Exception:
                continue
        if papers:
            logger.info("Scholar search via scholarly returned %d results", len(papers))
            return papers
    except ImportError:
        logger.debug("scholarly not installed, trying subprocess fallback")
    except Exception as exc:
        logger.warning("scholarly search failed: %s", exc)

    # ── Approach 2: subprocess-based fallback ──
    try:
        result = subprocess.run(
            ["python", "-c",
             "import json, sys; "
             "from scholarly import scholarly; "
             f"search = scholarly.search_pubs({json.dumps(query)}); "
             "results = []; "
             "[results.append({'title': r.get('bib',{}).get('title',''), "
             "'authors': r.get('bib',{}).get('author',''), "
             "'year': str(r.get('bib',{}).get('pub_year','') or ''), "
             "'source': 'scholar'}) "
             f"for i, r in enumerate(search) if i < {max_results}]; "
             "print(json.dumps(results))"],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode == 0 and result.stdout.strip():
            try:
                papers = json.loads(result.stdout)
                if papers:
                    logger.info("Scholar subprocess returned %d results", len(papers))
                    return papers
            except json.JSONDecodeError:
                logger.warning("Failed to parse scholar subprocess output")
        else:
            logger.debug("Scholar subprocess failed: %s", result.stderr[:200])
    except (subprocess.TimeoutExpired, FileNotFoundError) as exc:
        logger.debug("Scholar subprocess not available: %s", exc)
    except Exception as exc:
        logger.warning("Scholar subprocess unexpected error: %s", exc)

    logger.info("Google Scholar search returned 0 results (scholarly unavailable, skill requires Claude Code)")
    return []


# ── Step 3: Dedup + ranking ──

def _normalize_title(title: str) -> str:
    """Normalize title for dedup comparison."""
    return re.sub(r"[^a-z0-9]", "", title.lower().strip())


def _dedup_and_rank(papers: list[dict], keywords: list[str], target_journals: list[str]) -> list[dict]:
    """Remove duplicates (by normalized title) and rank by relevance."""
    seen = set()
    unique = []
    for p in papers:
        norm = _normalize_title(p.get("title", ""))
        if norm in seen or len(norm) < 10:
            continue
        seen.add(norm)
        unique.append(p)

    # Compute relevance score with multi-factor weighting
    current_year = datetime.now().year
    for p in unique:
        title_lower = (p.get("title", "") or "").lower()
        abstract_lower = (p.get("abstract", "") or "").lower()

        # Keyword match: title matches weighted 3x, abstract 1x
        title_matches = sum(1 for kw in keywords if kw.lower() in title_lower)
        abstract_matches = sum(1 for kw in keywords if kw.lower() in abstract_lower)
        kw_score = min(title_matches * 3 + abstract_matches, 10)

        # Journal bonus: exact match > partial match
        journal_lower = (p.get("journal", "") or "").lower()
        journal_bonus = 2 if any(j.lower() == journal_lower for j in target_journals) else \
                        1 if any(j.lower() in journal_lower for j in target_journals) else 0

        # Citation count: log-scale normalization (0→0, 1→1, 10→2, 100→3, 1000→4)
        citations = p.get("citation_count", 0) or 0
        import math
        citation_score = math.log2(citations + 1) / 2  # capped: 0→0, 1000→~5

        # Recency boost: published in last 3 years → +1, last year → +2
        year = p.get("year", 0) or 0
        recency = 2 if year >= current_year else 1 if year >= current_year - 2 else 0

        p["relevance_score"] = round(kw_score + journal_bonus + citation_score + recency, 1)

    unique.sort(key=lambda p: p.get("relevance_score", 0), reverse=True)
    return unique


# ── Step 4: Batch download ──

def _download_pdf(paper: dict, output_dir: Path, retries: int = 3) -> str | None:
    """Download a single paper PDF. Returns local path or None."""
    source = paper.get("source", "")
    pdf_url = paper.get("pdf_url", "")
    doi = paper.get("doi", "")

    # Build safe filename
    first_author = (paper.get("authors", "Unknown").split(",")[0].strip().split()[-1] or "Unknown")
    year = paper.get("year", "0000")
    title_words = re.sub(r"[^\w\s]", "", paper.get("title", "untitled")[:50])
    safe_title = "-".join(title_words.split()[:5])
    filename = f"{first_author}_{year}_{safe_title}.pdf"
    filepath = output_dir / filename

    if filepath.exists():
        return str(filepath)

    for attempt in range(retries):
        try:
            if source == "arxiv" and pdf_url:
                import urllib.request
                req = urllib.request.Request(pdf_url, headers={"User-Agent": "LiteratureSurvey/1.0"})
                with urllib.request.urlopen(req, timeout=60) as resp:
                    filepath.write_bytes(resp.read())
                return str(filepath)

            elif source == "ieee" and doi:
                # Try seu-ieee-downloader skill via subprocess
                result = subprocess.run(
                    ["python", "-m", "seu_ieee_downloader", "--doi", doi, "--output", str(output_dir)],
                    capture_output=True, text=True, timeout=120,
                )
                if result.returncode != 0:
                    logger.warning("seu_ieee_downloader failed for %s (rc=%d): %s",
                                   doi, result.returncode, result.stderr[:200])
                # Check if downloaded file exists in output dir
                downloaded = list(output_dir.glob(f"*{doi.split('/')[-1]}*.pdf"))
                if downloaded:
                    return str(downloaded[0])
                # Try CARSI download with environment variables
                seu_user = os.environ.get("SEU_USERNAME", "")
                seu_pass = os.environ.get("SEU_PASSWORD", "")
                if seu_user and seu_pass:
                    # Construct CARSI-authenticated download URL
                    pdf_path = _try_carsi_download(doi, output_dir, seu_user, seu_pass)
                    if pdf_path:
                        return pdf_path

        except subprocess.TimeoutExpired:
            logger.warning("Download timeout for %s (attempt %d)", doi or pdf_url, attempt + 1)
        except Exception as exc:
            logger.warning("Download failed for %s (attempt %d): %s", doi or pdf_url, attempt + 1, exc)
        time.sleep(2)  # Delay between retries

    return None


def _try_carsi_download(doi: str, output_dir: Path, username: str, password: str) -> str | None:
    """Attempt CARSI-authenticated IEEE download. Returns path or None."""
    try:
        import urllib.request
        import urllib.error
        # CARSI SP-initiated SSO flow for IEEE
        ieee_url = f"https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber={doi.split('/')[-1]}"
        # This is a simplified attempt; full CARSI flow requires session management
        req = urllib.request.Request(ieee_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            # Check if we got a PDF (magic bytes) or HTML redirect
            data = resp.read()
            if data[:4] == b"%PDF":
                filename = output_dir / f"{doi.split('/')[-1]}.pdf"
                filename.write_bytes(data)
                return str(filename)
    except Exception as exc:
        logger.debug("CARSI download attempt failed: %s", exc)
    return None


# ── Step 5: LLM batch summarization ──

def _summarize_batch(papers: list[dict], batch_size: int = 5) -> list[dict]:
    """LLM summarization in batches."""
    for i in range(0, len(papers), batch_size):
        batch = papers[i:i + batch_size]
        papers_text = "\n\n---\n\n".join(
            f"### {j+1}. {p['title']}\n"
            f"Authors: {p.get('authors','?')}\n"
            f"Year: {p.get('year','?')}\n"
            f"Journal: {p.get('journal','?')}\n"
            f"DOI: {p.get('doi','?')}\n"
            f"Abstract: {p.get('abstract','?')}"
            for j, p in enumerate(batch)
        )

        # Load prompt from config if available, else use hardcoded default
        config_prompt = ""
        try:
            cfg = _load_config()
            config_prompt = cfg.get("prompts", {}).get("summarization", "")
        except Exception:
            logger.debug("Config prompt load failed, using default summarization prompt")
        prompt_template = config_prompt if config_prompt else (
            "请为以下每篇论文生成结构化摘要。输出 JSON 数组：\n\n"
            "{papers_text}\n\n"
            "输出格式（JSON）：\n"
            '[{"index": 1, "summary_cn": "一句话中文摘要(≤80字)", '
            '"method_tags": ["方法1","方法2"], '
            '"contribution_tags": ["贡献1"], '
            '"limitation_tags": ["局限1"], '
            '"relevance_score": 8}]'
        )
        prompt = prompt_template.replace("{papers_text}", papers_text)

        response = llm_chat("你是电力电子领域研究者。仅输出要求的JSON格式，不做其他回复。", prompt)
        if response:
            try:
                # First try extracting from markdown code fence
                fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", response)
                json_str = fence_match.group(1).strip() if fence_match else ""
                if not json_str:
                    # Fallback: find first JSON array with balanced bracket matching
                    start = response.find("[")
                    if start >= 0:
                        depth = 0
                        end = start
                        for ci in range(start, len(response)):
                            if response[ci] == "[":
                                depth += 1
                            elif response[ci] == "]":
                                depth -= 1
                                if depth == 0:
                                    end = ci + 1
                                    break
                        json_str = response[start:end]
                if json_str:
                    summaries = json.loads(json_str)
                    for s in summaries:
                        idx = s.get("index", 0) - 1
                        if 0 <= idx < len(batch):
                            batch[idx]["llm_summary"] = s.get("summary_cn", "")
                            batch[idx]["method_tags"] = s.get("method_tags", [])
                            batch[idx]["contribution_tags"] = s.get("contribution_tags", [])
                            batch[idx]["limitation_tags"] = s.get("limitation_tags", [])
                            batch[idx]["llm_relevance"] = s.get("relevance_score", 5)
            except (json.JSONDecodeError, KeyError) as exc:
                logger.warning("Failed to parse LLM summarization response: %s", exc)
                for p in batch:
                    p.setdefault("llm_summary", "[LLM解析失败]")
                    p.setdefault("method_tags", [])
                    p.setdefault("contribution_tags", [])
                    p.setdefault("limitation_tags", [])
        else:
            for p in batch:
                p.setdefault("llm_summary", "[LLM不可用]")
                p.setdefault("method_tags", [])
                p.setdefault("contribution_tags", [])
                p.setdefault("limitation_tags", [])

        if i + batch_size < len(papers):
            time.sleep(2)  # Rate limit between batches

    return papers


# ── Step 6: Literature matrix ──

def _build_matrix(papers: list[dict], session_id: str, query_info: dict, output_dir: Path) -> tuple[Path, Path]:
    """Generate literature_matrix.csv and literature_matrix.json."""
    # CSV
    csv_path = output_dir / "literature_matrix.csv"
    fieldnames = [
        "title", "authors", "year", "journal", "doi", "abstract",
        "citation_count", "source", "pdf_path", "llm_summary",
        "method_tags", "contribution_tags", "limitation_tags", "relevance_score",
    ]
    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for p in papers:
            row = {k: p.get(k, "") for k in fieldnames}
            # Convert lists to strings for CSV
            for list_field in ["method_tags", "contribution_tags", "limitation_tags"]:
                if isinstance(row.get(list_field), list):
                    row[list_field] = "; ".join(row[list_field])
            writer.writerow(row)

    # JSON (structured for downstream consumers)
    json_path = output_dir / "literature_matrix.json"
    matrix_json = {
        "session_id": session_id,
        "query": query_info.get("query_cn", ""),
        "query_en": query_info.get("query_en", ""),
        "generated_at": datetime.now().isoformat(),
        "total_found": len(papers),
        "total_downloaded": sum(1 for p in papers if p.get("pdf_path")),
        "papers": papers,
    }
    json_path.write_text(json.dumps(matrix_json, ensure_ascii=False, indent=2), encoding="utf-8")

    return csv_path, json_path


# ── Step 7: Gap analysis ──

def _gap_analysis(papers: list[dict], query_info: dict, output_dir: Path) -> Path:
    """LLM-driven research gap analysis."""
    gap_path = output_dir / "gap_analysis.md"

    # Prepare matrix summary
    lines = [f"## 调研主题: {query_info.get('query_cn','')}", "", "### 文献列表", ""]
    for i, p in enumerate(papers[:20]):
        lines.append(
            f"{i+1}. **{p['title']}** ({p.get('year','?')}) — "
            f"{', '.join(p.get('method_tags', []))} / "
            f"{', '.join(p.get('contribution_tags', []))} / "
            f"局限: {', '.join(p.get('limitation_tags', []))}"
        )

    config_prompt = ""
    try:
        cfg = _load_config()
        config_prompt = cfg.get("prompts", {}).get("gap_analysis", "")
    except Exception:
        logger.debug("Config prompt load failed, using default gap_analysis prompt")
    default_prompt = (
        "请分析以下文献矩阵，识别研究缺口：\n\n"
        + "\n".join(lines) +
        "\n\n请输出（Markdown格式）：\n"
        "## 已覆盖方向\n列出当前文献主要覆盖的3-5个研究方向\n\n"
        "## 研究空白\n至少3个明显空白，每项说明为什么是缺口\n\n"
        "## 突破思路\n每个空白的潜在突破方向（1-2句）\n\n"
        "## 方法对比表\n| 方法 | 优势 | 劣势 | 代表文献 |\n|------|------|------|----------|"
    )
    prompt = config_prompt if config_prompt else default_prompt

    analysis = llm_chat("你是电力电子领域资深研究者。做严谨的文献缺口分析。", prompt)
    gap_path.write_text(analysis or "[LLM不可用，无法生成缺口分析]", encoding="utf-8")
    return gap_path


# ── Step 8: BibTeX generation ──

def _generate_bibtex(papers: list[dict], output_dir: Path) -> Path:
    """Generate references.bib from paper metadata."""
    bib_path = output_dir / "references.bib"
    entries = []
    for i, p in enumerate(papers):
    # Safe author extraction: take first author's last name
        authors_str = p.get("authors", "")
        if authors_str:
            first_author = authors_str.split(",")[0].strip()
            last_name = first_author.split()[-1] if first_author.split() else "anon"
            # Sanitize: remove non-alphanumeric
            last_name = re.sub(r"[^a-zA-Z]", "", last_name) or "anon"
        else:
            last_name = "anon"
        cite_key = f"ref{i+1}_{last_name}_{p.get('year','0000')}"
        entry_type = "article" if "preprint" not in p.get("journal", "").lower() else "misc"
        entry_lines = [f"@{entry_type}{{{cite_key},"]
        if p.get("title"):
            entry_lines.append(f"  title = {{{p['title']}}},")
        if p.get("authors"):
            entry_lines.append(f"  author = {{{p['authors']}}},")
        if p.get("year"):
            entry_lines.append(f"  year = {{{p['year']}}},")
        if p.get("journal"):
            entry_lines.append(f"  journal = {{{p['journal']}}},")
        if p.get("doi"):
            entry_lines.append(f"  doi = {{{p['doi']}}},")
        entry_lines.append("}")
        entries.append("\n".join(entry_lines))

    bib_path.write_text("\n\n".join(entries), encoding="utf-8")
    return bib_path


# ── Step 9: Review draft (optional) ──

def _generate_review_draft(papers: list[dict], gap_path: Path, query_info: dict, output_dir: Path) -> Path:
    """Generate a structured review draft."""
    draft_path = output_dir / "review_draft.md"

    gap_content = gap_path.read_text(encoding="utf-8") if gap_path.exists() else ""
    papers_text = "\n".join(
        f"[{i+1}] {p.get('authors','?')}. **{p['title']}**. {p.get('journal','?')}, {p.get('year','?')}."
        for i, p in enumerate(papers[:15])
    )

    config_prompt = ""
    try:
        cfg = _load_config()
        config_prompt = cfg.get("prompts", {}).get("review_draft", "")
    except Exception:
        logger.debug("Config prompt load failed, using default review_draft prompt")
    default_prompt = (
        f"## 调研主题: {query_info.get('query_cn','')}\n\n"
        f"## 文献列表\n{papers_text}\n\n"
        f"## 缺口分析\n{gap_content}\n\n"
        "请基于以上材料撰写一篇综述草稿。结构：\n"
        "1) 引言（研究背景+范围）\n"
        "2) 方法分类学\n"
        "3) 各分支代表性工作对比\n"
        "4) 开放问题与未来方向\n"
        "5) 结论\n"
        "字数约2000字中文，学术风格，引用用 [1][2] 标注。"
    )
    prompt = config_prompt if config_prompt else default_prompt

    draft = llm_chat("你是电力电子领域资深研究者，撰写严谨的综述草稿。", prompt)
    draft_path.write_text(draft or "[LLM不可用，无法生成综述草稿]", encoding="utf-8")
    return draft_path


# ── session management ──

def _get_idempotency_key(message: str) -> str:
    """Generate idempotency key from query content."""
    return hashlib.sha256(message.encode()).hexdigest()[:16]


def _check_recent_execution(idemp_key: str, window_minutes: int = 30) -> bool:
    """Check if this query was executed recently."""
    marker_dir = PROJECT_OUTPUT_BASE / "literature_survey" / ".idempotency"
    marker_dir.mkdir(parents=True, exist_ok=True)
    marker_file = marker_dir / f"{idemp_key}.json"
    if marker_file.exists():
        try:
            data = json.loads(marker_file.read_text())
            last_run = datetime.fromisoformat(data["timestamp"])
            if datetime.now() - last_run < timedelta(minutes=window_minutes):
                return True
        except Exception:
            logger.debug("Dedup window check failed, assuming no recent run")
    return False


def _mark_execution(idemp_key: str) -> None:
    """Record execution timestamp."""
    marker_dir = PROJECT_OUTPUT_BASE / "literature_survey" / ".idempotency"
    marker_dir.mkdir(parents=True, exist_ok=True)
    (marker_dir / f"{idemp_key}.json").write_text(
        json.dumps({"timestamp": datetime.now().isoformat()})
    )


# ── workflow class ──

class LiteratureSurveyWorkflow:
    role_group = "literature_survey"
    actor_name = "literature-survey-actor"
    critic_name = "literature-survey-critic"

    def run_actor(self, job: Job) -> Artifact:
        logger.info("LiteratureSurvey actor starting, job=%s", job.job_id)
        session_id = uuid.uuid4().hex[:12]
        config = _load_config()
        pipeline_cfg = config.get("pipeline", {})

        # Parse message
        message = job.input.get("message", "") if hasattr(job, "input") else getattr(job, "message", "")
        query_info = _parse_nl_message(message)
        max_papers = query_info.get("max_papers", pipeline_cfg.get("default_max_papers", 30))
        year_from = query_info.get("year_from")
        target_journals = query_info.get("journals", [])
        keywords = query_info.get("keywords_en", [])

        # Idempotency check
        idemp_key = _get_idempotency_key(message)
        if _check_recent_execution(idemp_key, pipeline_cfg.get("idempotency_window_minutes", 30)):
            logger.info("Duplicate query detected, attempting to return cached results")
            # Try to find the most recent session for this query
            survey_base = get_artifact_dir("literature_survey")
            sessions = sorted([d for d in survey_base.iterdir() if d.is_dir() and d.name != ".idempotency"],
                            key=lambda d: d.stat().st_mtime, reverse=True)
            for sdir in sessions[:5]:
                summary_path = sdir / "session_summary.md"
                if summary_path.exists() and sdir.stat().st_mtime > (time.time() - pipeline_cfg.get("idempotency_window_minutes", 30) * 60 - 120):
                    return Artifact(
                        artifact_id=f"artifact-{job.job_id}",
                        job_id=job.job_id,
                        artifact_type="literature_survey",
                        summary=f"复用最近调研结果（30分钟内）。原查询：「{message[:100]}」\n\n{summary_path.read_text(encoding='utf-8')[:500]}",
                        artifact_paths=[str(p) for p in sdir.glob("*") if p.is_file()],
                        sources=["idempotency_cache", "previous_session"],
                        risks=["返回的是缓存结果，如需重新调研请等待窗口过期"],
                        user_confirmations=[],
                    )
            return Artifact(
                artifact_id=f"artifact-{job.job_id}",
                job_id=job.job_id,
                artifact_type="literature_survey",
                summary=f"重复查询（30分钟内），session_id={session_id}。原查询：「{message[:100]}」",
                artifact_paths=[],
                sources=["idempotency_cache"],
                risks=["此次为重复执行拦截"],
                user_confirmations=[],
            )

        # Prepare output directory
        output_dir = get_artifact_dir("literature_survey") / session_id
        output_dir.mkdir(parents=True, exist_ok=True)
        pdf_dir = output_dir / "pdfs"
        pdf_dir.mkdir(exist_ok=True)
        abstracts_dir = output_dir / "abstracts"
        abstracts_dir.mkdir(exist_ok=True)

        failed_sources: list[str] = []
        all_papers: list[dict] = []
        search_log_entries: list[dict] = []

        # Step 1: Already done (_parse_nl_message above)

        # Step 2: Multi-source search
        sources_cfg = config.get("search_sources", {})
        for src_name, src_cfg in sorted(sources_cfg.items(), key=lambda x: x[1].get("priority", 99)):
            if not src_cfg.get("enabled", True):
                continue
            src_max = src_cfg.get("max_results", 20)
            logger.info("Searching %s (max=%d, keywords=%s)", src_name, src_max, keywords[:4])

            try:
                if src_name == "ieee":
                    papers = _search_ieee(keywords, max_results=src_max, year_from=year_from)
                elif src_name == "arxiv":
                    papers = _search_arxiv(keywords, max_results=src_max)
                elif src_name == "scholar":
                    papers = _search_scholar(keywords, max_results=src_max)
                else:
                    papers = []

                search_log_entries.append({
                    "name": src_name, "hits": len(papers),
                    "status": "success", "error": None,
                })
                all_papers.extend(papers)
                logger.info("  %s: %d results", src_name, len(papers))
            except Exception as exc:
                logger.warning("  %s: FAILED (%s)", src_name, exc)
                search_log_entries.append({
                    "name": src_name, "hits": 0,
                    "status": "failed", "error": str(exc)[:200],
                })
                failed_sources.append(src_name)

        # Step 3: Dedup + rank
        all_papers = _dedup_and_rank(all_papers, keywords, target_journals)

        # Apply year filter
        if year_from:
            all_papers = [p for p in all_papers if p.get("year", 0) >= year_from]

        # Cap to max_papers
        all_papers = all_papers[:max_papers]

        # Step 4: Batch download
        gaps: list[dict] = []
        for paper in all_papers:
            try:
                pdf_path = _download_pdf(paper, pdf_dir, retries=pipeline_cfg.get("download_retries", 3))
                paper["pdf_path"] = pdf_path or ""
                if not pdf_path and (paper.get("doi") or paper.get("pdf_url")):
                    gaps.append({
                        "paper_title": paper.get("title", ""),
                        "doi": paper.get("doi"),
                        "fail_stage": "download",
                        "error": "All retries exhausted",
                        "retry_count": pipeline_cfg.get("download_retries", 3),
                        "timestamp": datetime.now().isoformat(),
                    })
            except Exception as exc:
                paper["pdf_path"] = ""
                gaps.append({
                    "paper_title": paper.get("title", ""),
                    "doi": paper.get("doi"),
                    "fail_stage": "download",
                    "error": str(exc)[:200],
                    "retry_count": 0,
                    "timestamp": datetime.now().isoformat(),
                })

        # Step 5: LLM batch summarization
        llm_available = bool(os.environ.get("LANES_CEO_LLM_API_KEY"))
        if llm_available:
            all_papers = _summarize_batch(all_papers, batch_size=pipeline_cfg.get("llm_batch_size", 5))
        else:
            logger.warning("LANES_CEO_LLM_API_KEY not set, skipping LLM summarization")
            for p in all_papers:
                p.setdefault("llm_summary", "[LLM不可用]")
                p.setdefault("method_tags", [])
                p.setdefault("contribution_tags", [])
                p.setdefault("limitation_tags", [])

        # Step 6: Literature matrix
        csv_path, json_path = _build_matrix(all_papers, session_id, query_info, output_dir)

        # Step 7: Gap analysis (only if LLM available and we have papers)
        gap_path = output_dir / "gap_analysis.md"
        if llm_available and len(all_papers) >= 5:
            gap_path = _gap_analysis(all_papers, query_info, output_dir)
        else:
            msg = "[LLM不可用]" if not llm_available else "文献少于5篇，无法生成有意义的缺口分析"
            gap_path.write_text(f"# 缺口分析\n\n{msg}", encoding="utf-8")

        # Step 8: BibTeX
        bib_path = _generate_bibtex(all_papers, output_dir)

        # Step 9: Review draft (optional)
        review_path: Path | None = None
        if query_info.get("generate_review_draft"):
            if llm_available and len(all_papers) >= 5:
                review_path = _generate_review_draft(all_papers, gap_path, query_info, output_dir)
            else:
                msg = "[LLM不可用]" if not llm_available else "文献少于5篇，无法生成有意义的综述草稿"
                placeholder = output_dir / "review_draft.md"
                placeholder.write_text(f"# 综述草稿\n\n{msg}", encoding="utf-8")
                review_path = placeholder

        # Save search_log.json
        search_log = {
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "query_cn": query_info["query_cn"],
            "query_en": query_info["query_en"],
            "filters": {"year_from": year_from, "journals": target_journals},
            "sources": search_log_entries,
            "failed_sources": failed_sources,
            "warnings": [],
        }
        (output_dir / "search_log.json").write_text(json.dumps(search_log, ensure_ascii=False, indent=2), encoding="utf-8")

        # Save gaps.json
        (output_dir / "gaps.json").write_text(json.dumps(gaps, ensure_ascii=False, indent=2), encoding="utf-8")

        # Save individual abstracts
        for p in all_papers:
            if p.get("llm_summary") and p["llm_summary"] not in ("[LLM不可用]", "[LLM解析失败]"):
                safe_name = re.sub(r"[^\w\s-]", "", p.get("title", "untitled")[:30])
                abs_file = abstracts_dir / f"{safe_name.strip()}.md"
                abs_file.write_text(
                    f"# {p['title']}\n\n"
                    f"**摘要**: {p['llm_summary']}\n\n"
                    f"**方法**: {', '.join(p.get('method_tags', []))}\n\n"
                    f"**贡献**: {', '.join(p.get('contribution_tags', []))}\n\n"
                    f"**局限**: {', '.join(p.get('limitation_tags', []))}\n\n"
                    f"**相关度**: {p.get('relevance_score', 'N/A')}/10",
                    encoding="utf-8",
                )

        # Session summary
        hits_summary = ', '.join(f'{s["name"]}: {s["hits"]}' for s in search_log_entries)
        summary_lines = [
            f"# 文献调研报告 — {date.today().isoformat()}",
            f"**Session ID**: {session_id}",
            f"**查询**: {query_info['query_cn']}",
            f"**英文关键词**: {query_info['query_en']}",
            "",
            f"## 统计",
            f"- 各源命中: {hits_summary}",
            f"- 去重后: {len(all_papers)} 篇",
            f"- 全文下载成功: {sum(1 for p in all_papers if p.get('pdf_path'))} 篇",
            f"- 下载失败: {len(gaps)} 篇",
            f"- 研究空白: 见 gap_analysis.md",
            "",
            f"## 产出文件",
            f"- 文献矩阵: literature_matrix.csv / .json",
            f"- 缺口分析: gap_analysis.md",
            f"- BibTeX: references.bib",
            f"- 检索记录: search_log.json",
        ]
        if review_path and review_path.exists():
            summary_lines.append(f"- 综述草稿: review_draft.md")
        # Add key findings from top papers
        top_methods = set()
        top_limitations = set()
        for p in all_papers[:5]:
            for tag in p.get("method_tags", []):
                top_methods.add(tag)
            for tag in p.get("limitation_tags", []):
                top_limitations.add(tag)
        summary_lines.extend([
            "",
            "## 关键发现",
            f"- 主要方法: {', '.join(top_methods) if top_methods else '待LLM分析'}",
            f"- 常见局限: {', '.join(top_limitations) if top_limitations else '待LLM分析'}",
        ])
        summary_text = "\n".join(summary_lines)
        (output_dir / "session_summary.md").write_text(summary_text, encoding="utf-8")

        # Mark execution
        _mark_execution(idemp_key)

        return Artifact(
            artifact_id=f"artifact-{job.job_id}",
            job_id=job.job_id,
            artifact_type="literature_survey",
            summary=summary_text,
            artifact_paths=[
                str(output_dir / "session_summary.md"),
                str(csv_path),
                str(json_path),
                str(gap_path),
                str(bib_path),
            ] + ([str(review_path)] if review_path else []),
            sources=["ieee", "arxiv", "scholar", "llm-summarization", "llm-gap-analysis"],
            risks=[
                f"failed_sources: {failed_sources}" if failed_sources else "",
                f"下载失败 {len(gaps)} 篇，详见 gaps.json" if gaps else "",
                "IEEE API 可能受认证限制；CARSI 下载依赖 SEU_USERNAME/SEU_PASSWORD 环境变量",
                "LLM 摘要质量取决于 API 模型，Critic 检查可拦截低质量输出",
            ],
            user_confirmations=(
                [f"确认处理 {len(gaps)} 篇下载失败的论文?"] if gaps else []
            ),
        )

    def run_critic(self, job: Job, artifact: Artifact) -> CriticReview:
        issues: list[str] = []

        # 1. Artifact completeness
        if len(artifact.artifact_paths) < 3:
            issues.append("产物文件不完整（至少需要 session_summary + matrix + gap_analysis）")
        if len(artifact.sources) < 3:
            issues.append("检索源覆盖不足（至少应包含 3 个来源）")
        if not artifact.summary or len(artifact.summary) < 100:
            issues.append("调研摘要过短或缺失")

        # 2. Validate CSV matrix contents
        csv_files = [p for p in artifact.artifact_paths if p.endswith('.csv')]
        if csv_files:
            try:
                csv_path = Path(csv_files[0])
                if csv_path.exists():
                    content = csv_path.read_text(encoding='utf-8')
                    lines = content.strip().split('\n')
                    if len(lines) < 2:
                        issues.append("文献矩阵CSV为空（无数据行）")
                    reader = csv.reader(io.StringIO(content))
                    header = next(reader, [])
                    required_cols = {'title', 'authors', 'year'}
                    missing_cols = required_cols - set(c.lower() for c in header)
                    if missing_cols:
                        issues.append(f"文献矩阵缺少必要列: {missing_cols}")
                    row_count = sum(1 for _ in reader)
                    if row_count < 3:
                        issues.append(f"文献矩阵记录太少（{row_count}条，至少3条）")
            except Exception as exc:
                issues.append(f"无法解析文献矩阵CSV: {exc}")

        # 3. Validate gap analysis content
        gap_files = [p for p in artifact.artifact_paths if 'gap' in p.lower()]
        if gap_files:
            try:
                gap_path = Path(gap_files[0])
                if gap_path.exists():
                    gap_text = gap_path.read_text(encoding='utf-8')
                    if len(gap_text) < 100:
                        issues.append("缺口分析内容过短（<100字符）")
                    # Check for numbered research gaps
                    gap_sections = re.findall(r'(?:研究空白|Gap|缺口|方向)\s*\d', gap_text, re.IGNORECASE)
                    if len(gap_sections) < 2:
                        issues.append("缺口分析至少应识别2个以上研究空白/方向")
            except Exception as exc:
                issues.append(f"无法读取缺口分析: {exc}")

        # 4. Validate BibTeX file
        bib_files = [p for p in artifact.artifact_paths if p.endswith('.bib')]
        if bib_files:
            try:
                bib_path = Path(bib_files[0])
                if bib_path.exists():
                    bib_text = bib_path.read_text(encoding='utf-8')
                    entries = re.findall(r'@\w+\{', bib_text)
                    if len(entries) < 2:
                        issues.append(f"BibTeX条目太少（{len(entries)}条，至少2条）")
                    required_fields = ['author', 'title', 'year']
                    for entry_match in re.finditer(r'@\w+\{.*?\}', bib_text, re.DOTALL):
                        entry = entry_match.group()
                        for field in required_fields:
                            if field not in entry.lower():
                                issues.append(f"BibTeX条目缺少{field}字段")
                                break
            except Exception as exc:
                issues.append(f"无法读取BibTeX文件: {exc}")

        # 5. LLM quality review
        sources_str = ', '.join(artifact.sources)
        risks_str = ', '.join([r for r in artifact.risks if r])
        review_text = llm_chat(
            CRITIC_SYSTEM,
            f"## 调研摘要\n{artifact.summary}\n\n"
            f"## 来源\n{sources_str}\n\n"
            f"## 风险\n{risks_str}",
        )

        # Parse LLM review for additional issues
        if review_text:
            quality_indicators = [
                ("摘要质量不足", r"(?:摘要|summary).*?(?:不足|缺失|过于|太)"),
                ("缺口分析深度不够", r"(?:缺口|gap).*?(?:不够|不足|浅|少)"),
                ("检索覆盖不足", r"(?:覆盖|coverage|检索).*?(?:不足|不够|缺)"),
                ("BibTeX格式问题", r"(?:bib|引用|格式).*?(?:错误|问题|缺失|不完整)"),
            ]
            for label, pattern in quality_indicators:
                if re.search(pattern, review_text, re.IGNORECASE):
                    issues.append(label)

        # Score calculation
        base_score = 95
        simple_issues = sum(1 for i in issues if not i.startswith("无法"))
        deep_issues = sum(1 for i in issues if i.startswith("无法"))
        score = base_score - simple_issues * 10 - deep_issues * 15
        approved = len(issues) == 0

        return CriticReview(
            review_id=f"review-{job.job_id}",
            job_id=job.job_id,
            review_result="approved" if approved else "returned",
            score=max(score, 0),
            issues=issues,
            approved=approved,
            return_to_actor=not approved,
            handoff_note=review_text[:500] if review_text else "审核完成",
        )
