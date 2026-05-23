"""StructureChecker — check word count, page count, and section structure compliance."""

from __future__ import annotations

import logging
import re
import shutil
import subprocess
from pathlib import Path

from lanes_ceo.workflows.manuscript_tracker.checkers.base import BaseChecker, CheckItem, CheckResult
from lanes_ceo.workflows.manuscript_tracker.config import DEFAULT_CONFIG

logger = logging.getLogger("lanes_ceo.manuscript_tracker.structure")


class StructureChecker(BaseChecker):
    """Check manuscript structure: word count, page count, required sections."""

    name = "structure"

    def check(self, project: "LaTeXProject", profile: "JournalProfile") -> CheckResult:  # noqa: F821
        config = DEFAULT_CONFIG
        items: list[CheckItem] = []

        # Resolve article type constraints
        try:
            art_type = profile.get_article_type(project.article_type)
        except ValueError:
            return self._skip(f"未知文章类型: {project.article_type}")

        # 1. Word count via texcount
        word_count = self._count_words(project)
        if word_count is not None:
            items.append(CheckItem(
                code="STRUC_WORD_COUNT",
                description=f"字数统计: {word_count} 词",
                status="pass",
                detail=f"texcount 统计结果",
            ))

            if art_type.max_words and word_count > art_type.max_words:
                over = word_count - art_type.max_words
                items.append(CheckItem(
                    code="STRUC_WORD_OVER",
                    description=f"字数超限: {word_count} / {art_type.max_words} (+{over})",
                    status="fail",
                    detail=f"超出 {over} 词",
                    fix_suggestion=f"缩减文字至 {art_type.max_words} 词以内，优先压缩方法描述和补充材料",
                ))

        else:
            items.append(CheckItem(
                code="STRUC_NO_TEXCOUNT",
                description="无法统计字数（texcount 不可用）",
                status="skip",
            ))

        # 2. Page count via pdfinfo
        pdf_path = project.project_dir / f"{project.main_tex.stem}.pdf"
        if pdf_path.exists():
            page_count = self._count_pages(pdf_path)
            if page_count is not None:
                items.append(CheckItem(
                    code="STRUC_PAGE_COUNT",
                    description=f"页数: {page_count} 页",
                    status="pass",
                ))
                if art_type.max_pages and page_count > art_type.max_pages:
                    over = page_count - art_type.max_pages
                    items.append(CheckItem(
                        code="STRUC_PAGE_OVER",
                        description=f"页数超限: {page_count} / {art_type.max_pages} (+{over})",
                        status="fail",
                        detail=f"超出 {over} 页",
                        fix_suggestion=f"将页数缩减至 {art_type.max_pages} 页以内",
                    ))

        # 3. Section structure check
        required_sections = art_type.required_sections or []
        if required_sections:
            sections_found = self._detect_sections(project, profile)

            for req_sec in required_sections:
                # Normalize section name matching
                normalized = req_sec.lower().replace("_", " ").replace("-", " ")
                found = self._match_section(normalized, sections_found)

                if found:
                    items.append(CheckItem(
                        code="STRUC_SECTION_FOUND",
                        description=f"必需章节已找到: {req_sec}",
                        status="pass",
                        detail=f"匹配到: {found}",
                    ))
                else:
                    # IEEE template heuristic for abstract
                    if profile.citation_style == "ieee" and "abstract" in normalized:
                        if self._has_abstract_content(project, config.ieee_abstract_heuristic_words):
                            items.append(CheckItem(
                                code="STRUC_ABSTRACT_HEURISTIC",
                                description=f"IEEE 模板检测到摘要内容（启发式，前{config.ieee_abstract_heuristic_words}词）",
                                status="pass",
                                detail="IEEE双栏模板未使用 standalone abstract 环境，但正文开头检测到摘要内容",
                            ))
                            continue

                    items.append(CheckItem(
                        code="STRUC_SECTION_MISSING",
                        description=f"缺少必需章节: {req_sec}",
                        status="fail" if req_sec not in ("methods", "materials_and_methods") else "warn",
                        detail=f"未在稿件中找到与 '{req_sec}' 匹配的章节标题",
                        fix_suggestion=f"添加 '{req_sec}' 章节",
                    ))

        # 4. Table count (heuristic)
        table_count = self._count_tables(project)
        if table_count > 0:
            items.append(CheckItem(
                code="STRUC_TABLE_COUNT",
                description=f"表格数量: {table_count}",
                status="pass",
            ))
            if profile.max_tables and table_count > profile.max_tables:
                over = table_count - profile.max_tables
                items.append(CheckItem(
                    code="STRUC_TABLE_OVER",
                    description=f"表格数量超限: {table_count} / {profile.max_tables} (+{over})",
                    status="fail",
                    detail=f"超出 {over} 个表格",
                    fix_suggestion=f"将超出部分的表格移至补充材料",
                ))

        # Build result
        fail_count = sum(1 for i in items if i.status == "fail")
        if fail_count > 0:
            return self._fail(
                items=items,
                summary=f"结构检查: {fail_count} 项不符合要求",
            )

        return self._pass(
            items=items,
            summary=f"结构检查通过 (字数={word_count or '?'}, 页数=见PDF)",
        )

    # ── word count ──

    def _count_words(self, project: "LaTeXProject") -> int | None:  # noqa: F821
        """Count words in main tex using texcount."""
        if shutil.which("texcount") is None:
            return None

        try:
            proc = subprocess.run(
                ["texcount", "-1", "-sum", "-utf8", str(project.main_tex)],
                capture_output=True, text=True, timeout=30,
                cwd=str(project.project_dir),
            )
            if proc.returncode == 0:
                # Output is just the total number
                return int(proc.stdout.strip().split()[0])
        except (ValueError, subprocess.TimeoutExpired, FileNotFoundError):
            logger.debug("texcount word count failed, trying alternative")

        return None

    # ── page count ──

    def _count_pages(self, pdf_path: Path) -> int | None:
        """Count pages in PDF using pdfinfo."""
        if shutil.which("pdfinfo") is None:
            return self._count_pages_fallback(pdf_path)

        try:
            proc = subprocess.run(
                ["pdfinfo", str(pdf_path)],
                capture_output=True, text=True, timeout=15,
            )
            if proc.returncode == 0:
                for line in proc.stdout.split("\n"):
                    if line.startswith("Pages:"):
                        return int(line.split(":")[1].strip())
        except (ValueError, subprocess.TimeoutExpired, FileNotFoundError):
            logger.debug("pdfinfo page count failed, trying alternative")

        return self._count_pages_fallback(pdf_path)

    def _count_pages_fallback(self, pdf_path: Path) -> int | None:
        """Fallback page counting: try PyPDF2, then regex heuristic."""
        try:
            from PyPDF2 import PdfReader
            reader = PdfReader(str(pdf_path))
            return len(reader.pages)
        except ImportError:
            logger.debug("PyPDF2 not installed, using raw byte heuristic")
        except Exception:
            logger.debug("PyPDF2 page count failed, using raw byte heuristic")

        # Last-resort heuristic: count /Type/Page occurrences in raw bytes
        try:
            with open(pdf_path, "rb") as f:
                content = f.read()
            pages = len(re.findall(rb'/Type\s*/\s*Page\b', content))
            return pages if pages > 0 else None
        except Exception:
            return None

    # ── section detection ──

    def _detect_sections(self, project: "LaTeXProject", profile: "JournalProfile") -> list[str]:  # noqa: F821
        """Detect section headings from .tex source."""
        sections: list[str] = []

        tex_files = [project.main_tex] + project.include_files
        for tex_file in tex_files:
            try:
                content = tex_file.read_text(encoding="utf-8", errors="replace")
                # Match \section{...}, \section*{...}, \subsection{...}
                pattern = r'\\(?:section|subsection|chapter)\*?\s*\{([^}]+)\}'
                for match in re.finditer(pattern, content):
                    title = match.group(1).strip().lower()
                    sections.append(title)

                # Also detect \\begin{abstract} ... \\end{abstract}
                if re.search(r'\\begin\{abstract\}', content):
                    sections.append("abstract")
            except Exception:
                continue

        return sections

    def _match_section(self, required: str, found: list[str]) -> str | None:
        """Fuzzy-match a required section name against detected headings.

        Returns the matched heading string, or None.
        """
        # Map of common aliases
        aliases = {
            "abstract": ["abstract", "summary"],
            "introduction": ["introduction", "intro"],
            "results": ["results", "experimental results", "result"],
            "discussion": ["discussion", "discussions"],
            "methods": ["methods", "method", "materials and methods", "materials_and_methods",
                       "experimental methods", "experimental section", "methodology"],
            "materials_and_methods": ["materials and methods", "materials & methods",
                                     "methods", "method", "experimental methods"],
            "conclusion": ["conclusion", "conclusions", "concluding remarks", "summary and conclusions"],
            "references": ["references", "bibliography", "literature cited", "works cited"],
            "body": ["body"],  # IEEE generic — always pass
            "acknowledgments": ["acknowledgments", "acknowledgements", "acknowledgment"],
            "data availability": ["data availability", "data and code availability"],
        }

        # For "body" in IEEE style, always pass (it's not a real section)
        if required == "body":
            return "[IEEE 正文]"

        candidates = aliases.get(required, [required])

        for found_sec in found:
            for candidate in candidates:
                if candidate in found_sec or found_sec in candidate:
                    return found_sec

        return None

    def _has_abstract_content(self, project: "LaTeXProject", word_threshold: int = 200) -> bool:  # noqa: F821
        """Heuristic: check if the beginning of main tex has abstract-like content.

        Used for IEEE double-column templates that embed abstract in the body text.
        """
        try:
            content = project.main_tex.read_text(encoding="utf-8", errors="replace")
            # Remove LaTeX commands and comments
            clean = re.sub(r'\\.*?(\{.*?\})?', ' ', content)
            clean = re.sub(r'%.*$', '', clean, flags=re.MULTILINE)
            clean = re.sub(r'\{|\}', '', clean)
            clean = re.sub(r'\s+', ' ', clean).strip()

            # Take first N words
            words = clean.split()[:word_threshold]
            first_chunk = " ".join(words).lower()

            # Check for abstract keywords
            abstract_signals = ["abstract", "摘要", "this paper", "this work", "we propose",
                               "we present", "herein"]
            signal_count = sum(1 for s in abstract_signals if s in first_chunk[:500])

            return signal_count >= 2
        except Exception:
            return False

    # ── table counting ──

    def _count_tables(self, project: "LaTeXProject") -> int:
        """Count top-level LaTeX table environments (avoid double-counting tabular inside table)."""
        count = 0

        tex_files = [project.main_tex] + project.include_files
        for tex_file in tex_files:
            try:
                content = tex_file.read_text(encoding="utf-8", errors="replace")
                # Count only top-level float environments, not inline tabular
                for env in ("table", "longtable"):
                    pattern = re.compile(rf'\\begin\{{{env}\}}')
                    count += len(pattern.findall(content))
            except Exception:
                continue

        return count
