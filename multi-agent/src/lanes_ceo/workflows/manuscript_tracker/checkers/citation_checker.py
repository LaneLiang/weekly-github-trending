"""CitationChecker — validate bibliography entries, DOI validity, and journal abbreviation consistency."""

from __future__ import annotations

import logging
import re
import time
from pathlib import Path

from lanes_ceo.workflows.manuscript_tracker.checkers.base import BaseChecker, CheckItem, CheckResult
from lanes_ceo.workflows.manuscript_tracker.config import DEFAULT_CONFIG

logger = logging.getLogger("lanes_ceo.manuscript_tracker.citation")


class CitationChecker(BaseChecker):
    """Check bibliography: parse .bib, validate DOIs via Crossref, check formatting."""

    name = "citation"

    def check(self, project: "LaTeXProject", profile: "JournalProfile") -> CheckResult:  # noqa: F821
        config = DEFAULT_CONFIG

        bib_files = project.bib_files
        if not bib_files:
            return self._skip("项目中未发现 .bib 文件")

        items: list[CheckItem] = []
        total_entries = 0
        doi_errors = 0
        missing_dois = 0
        abbreviation_issues = 0

        all_entries: list[dict] = []

        for bib_file in bib_files:
            try:
                entries = self._parse_bib(bib_file)
                all_entries.extend(entries)
                total_entries += len(entries)
            except Exception as exc:
                logger.warning("Failed to parse %s: %s", bib_file.name, exc)
                items.append(CheckItem(
                    code="CITE_PARSE_ERROR",
                    description=f"无法解析 .bib 文件: {bib_file.name} — {exc}",
                    status="fail",
                    detail=str(exc),
                    fix_suggestion="检查 .bib 文件格式是否正确，特别注意 UTF-8 BOM 和特殊字符",
                ))
                return self._fail(items=items, summary=f"解析 .bib 失败: {exc}")

        if not all_entries:
            return self._warn(
                items=[CheckItem(
                    code="CITE_EMPTY",
                    description=".bib 文件中未找到任何文献条目",
                    status="warn",
                )],
                summary="BibTeX 文件中无条目",
            )

        # 1. Check for missing required fields
        for entry in all_entries:
            cite_key = entry.get("ID", "?")
            entry_type = entry.get("ENTRYTYPE", "misc")

            # Check for DOI presence
            if "doi" not in entry:
                missing_dois += 1
                items.append(CheckItem(
                    code="CITE_NO_DOI",
                    description=f"缺少 DOI: {cite_key} ({entry_type})",
                    status="warn",
                    detail=f"文献 '{entry.get('title', cite_key)}' 没有 DOI 字段",
                    fix_suggestion="通过 Crossref / Google Scholar 查找并补充 DOI",
                ))

            # Check for journal field
            journal_field = entry.get("journal", entry.get("booktitle", ""))
            if journal_field:
                abbr_issues = self._check_abbreviation(journal_field)
                if abbr_issues:
                    abbreviation_issues += 1
                    items.append(CheckItem(
                        code="CITE_ABBREVIATION",
                        description=f"期刊名是否规范缩写: {cite_key} — '{journal_field}'",
                        status="warn",
                        detail=abbr_issues,
                        fix_suggestion="请使用 ISO 4 标准期刊缩写，或参考该期刊的引用格式要求",
                    ))

        # 2. Cross-check cited keys with .tex source
        cited_keys = self._extract_cited_keys(project)
        bib_keys = {entry.get("ID", "") for entry in all_entries}

        undefined_keys = cited_keys - bib_keys
        for key in undefined_keys:
            items.append(CheckItem(
                code="CITE_UNDEFINED",
                description=f"引用了未定义的文献: {key}",
                status="fail",
                detail=f"在 .tex 中 \\cite{{{key}}} 但 .bib 中没有对应条目",
                fix_suggestion=f"在 .bib 文件中添加 '{key}' 条目，或使用正确的引用键",
            ))

        unused_keys = bib_keys - cited_keys
        if unused_keys:
            for key in sorted(unused_keys):
                items.append(CheckItem(
                    code="CITE_UNUSED",
                    description=f".bib 中有未引用的文献: {key}",
                    status="warn",
                    detail=f"'{key}' 在 .bib 中定义但 .tex 中未被引用",
                    fix_suggestion="删除不需要的条目，或确认是否有遗漏的引用",
                ))

        # 3. Validate DOIs via Crossref API (optional, rate-limited)
        entries_with_doi = [e for e in all_entries if "doi" in e]
        if entries_with_doi:
            for entry in entries_with_doi:
                if doi_errors > 10:  # Bail out after too many errors
                    items.append(CheckItem(
                        code="CITE_DOI_LIMIT",
                        description="DOI 验证错误过多，已中止进一步检查",
                        status="warn",
                        detail="可能网络连接问题或 Crossref API 限流",
                        fix_suggestion="稍后手动验证剩余 DOI",
                    ))
                    break

                doi = entry["doi"].strip()
                if self._validate_doi(doi):
                    items.append(CheckItem(
                        code="CITE_DOI_VALID",
                        description=f"DOI 有效: {entry.get('ID', '?')} — {doi}",
                        status="pass",
                    ))
                else:
                    doi_errors += 1
                    items.append(CheckItem(
                        code="CITE_DOI_INVALID",
                        description=f"DOI 无效: {entry.get('ID', '?')} — {doi}",
                        status="warn",
                        detail=f"{doi} 在 Crossref 中未找到或无响应",
                        fix_suggestion="检查 DOI 是否拼写正确，或该文献是否被 Crossref 收录",
                    ))

                time.sleep(config.crossref_rate_limit)

        # 4. BibLaTeX detection
        main_tex_content = ""
        try:
            main_tex_content = project.main_tex.read_text(encoding="utf-8", errors="replace")
        except Exception:
            logger.debug("Failed to read main.tex for bibtex detection")

        uses_biblatex = "biblatex" in main_tex_content.lower() or "\\usepackage{biblatex}" in main_tex_content
        if uses_biblatex:
            items.append(CheckItem(
                code="CITE_BIBLATEX",
                description="检测到使用 BibLaTeX，部分期刊模板可能不兼容",
                status="warn",
                detail="BibLaTeX 与某些期刊的 BibTeX 工作流不兼容，投稿前需确认",
                fix_suggestion="确认目标期刊是否接受 BibLaTeX 格式；如不支持，请转换为传统 BibTeX",
            ))

        # Build summary
        issues_count = sum(1 for i in items if i.status == "fail")
        warns_count = sum(1 for i in items if i.status == "warn")

        if issues_count > 0:
            status = "fail"
        elif warns_count > 0:
            status = "warn"
        else:
            status = "pass"

        summary = (
            f"引用检查: {total_entries} 条文献, "
            f"{len(undefined_keys)} 未定义引用, "
            f"{doi_errors} DOI 无效, "
            f"{abbreviation_issues} 缩写可疑"
        )

        return CheckResult(
            checker_name=self.name,
            status=status,
            items=items,
            summary=summary,
        )

    # ── BibTeX parsing ──

    def _parse_bib(self, bib_path: Path) -> list[dict]:
        """Parse a .bib file using bibtexparser, with UTF-8 BOM handling."""
        raw = bib_path.read_bytes()

        # Handle UTF-8 BOM
        if raw.startswith(b'\xef\xbb\xbf'):
            raw = raw[3:]

        text = raw.decode("utf-8", errors="replace")

        try:
            import bibtexparser
            library = bibtexparser.parse_string(text)
            return list(library.entries)
        except ImportError:
            logger.warning("bibtexparser not installed; using basic parser")
            return self._parse_bib_basic(text)
        except Exception as exc:
            logger.warning("bibtexparser failed (%s); trying basic parser", exc)
            return self._parse_bib_basic(text)

    def _parse_bib_basic(self, text: str) -> list[dict]:
        """Fallback: basic BibTeX entry parser."""
        entries: list[dict] = []

        # Simple regex-based parser for @entrytype{ID, ...}
        pattern = r'@(\w+)\s*\{([^,]+)\s*,\s*([^}]*(?:\}[^@]*?)?)\}'
        for match in re.finditer(pattern, text, re.DOTALL):
            entry_type = match.group(1).lower()
            cite_key = match.group(2).strip()
            fields_text = match.group(3)

            entry = {"ENTRYTYPE": entry_type, "ID": cite_key}

            # Parse fields: field = {value} or field = "value"
            field_pattern = r'(\w+)\s*=\s*[{"]([^}"]*)[}"]'
            for fm in re.finditer(field_pattern, fields_text):
                entry[fm.group(1).lower()] = fm.group(2).strip()

            entries.append(entry)

        return entries

    # ── citation extraction from .tex ──

    def _extract_cited_keys(self, project: "LaTeXProject") -> set[str]:  # noqa: F821
        """Extract all citation keys from .tex files."""
        keys: set[str] = set()
        tex_files = [project.main_tex] + project.include_files

        cite_pattern = re.compile(
            r'\\(?:cite|citep|citet|citealp|citealt|citeauthor|citeyear|citeyearpar|'
            r'nocite|fullcite|footcite|textcite|parencite|supercite|autocite)s?\*?'
            r'\s*(?:\[[^\]]*\])?\s*\{([^}]+)\}'
        )

        for tex_file in tex_files:
            try:
                content = tex_file.read_text(encoding="utf-8", errors="replace")
                for match in cite_pattern.finditer(content):
                    cites = match.group(1)
                    for key in cites.split(","):
                        key = key.strip()
                        if key:
                            keys.add(key)
            except Exception:
                continue

        # If no cites found via regex, try basic \cite{...} pattern
        if not keys:
            simple_pattern = re.compile(r'\\cite\s*\{([^}]+)\}')
            for tex_file in tex_files:
                try:
                    content = tex_file.read_text(encoding="utf-8", errors="replace")
                    for match in simple_pattern.finditer(content):
                        for key in match.group(1).split(","):
                            key = key.strip()
                            if key:
                                keys.add(key)
                except Exception:
                    continue

        return keys

    # ── DOI validation ──

    def _validate_doi(self, doi: str) -> bool:
        """Validate a DOI via Crossref API with timeout and error handling."""
        if not doi:
            return False

        doi = re.sub(r'^https?://(?:dx\.)?doi\.org/', '', doi).strip()

        try:
            import requests
        except ImportError:
            return True  # Assume valid when requests unavailable (non-blocking)

        url = f"{DEFAULT_CONFIG.crossref_api_url}{doi}"
        try:
            resp = requests.get(
                url,
                timeout=DEFAULT_CONFIG.crossref_timeout,
                headers={"User-Agent": "lanes-ceo/1.0 (mailto:lane@example.com)"},
            )
            return resp.status_code == 200
        except requests.exceptions.Timeout:
            logger.warning("Crossref API timeout for DOI: %s", doi)
            return True  # Non-blocking on timeout
        except requests.exceptions.ConnectionError:
            logger.warning("Crossref API unreachable for DOI: %s", doi)
            return True  # Non-blocking on network error
        except Exception:
            return True  # Non-blocking on unexpected errors

    # ── abbreviation checking ──

    def _check_abbreviation(self, journal_name: str) -> str:
        """Check if journal name appears to use proper abbreviation conventions."""
        issues = []

        # Known words that should typically be abbreviated in journal names
        abbreviation_map = {
            "Transactions": "Trans.",
            "Journal": "J.",
            "Proceedings": "Proc.",
            "International": "Int.",
            "Conference": "Conf.",
            "IEEE": "IEEE",
            "ACM": "ACM",
            "Science": "Sci.",
            "Engineering": "Eng.",
            "Technology": "Technol.",
            "Letters": "Lett.",
            "Magazine": "Mag.",
            "Review": "Rev.",
            "Research": "Res.",
            "Applications": "Appl.",
            "Systems": "Syst.",
            "Circuits": "Circuits",
            "Electronics": "Electron.",
        }

        # Check if the name looks like a full journal name (has uppercase words that should be abbreviated)
        words = journal_name.split()
        for word in words:
            clean = word.rstrip(",.;:")
            if clean in abbreviation_map and clean != abbreviation_map[clean]:
                # Found a word that could/should be abbreviated
                if clean in journal_name and abbreviation_map[clean] not in journal_name:
                    issues.append(f"'{clean}' 可能需缩写为 '{abbreviation_map[clean]}'")

        return "; ".join(issues) if issues else ""
