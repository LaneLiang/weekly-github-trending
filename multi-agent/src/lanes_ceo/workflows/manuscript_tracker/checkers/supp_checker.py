"""SuppChecker — validate supplementary material file integrity and cross-references."""

from __future__ import annotations

import logging
import re
from pathlib import Path

from lanes_ceo.workflows.manuscript_tracker.checkers.base import BaseChecker, CheckItem, CheckResult

logger = logging.getLogger("lanes_ceo.manuscript_tracker.supp")


class SuppChecker(BaseChecker):
    """Check supplementary material: file existence, format compliance, cross-references."""

    name = "supplementary"

    def check(self, project: "LaTeXProject", profile: "JournalProfile") -> CheckResult:  # noqa: F821
        items: list[CheckItem] = []

        supp_dir = project.supp_dir

        # 1. Supplementary directory presence
        if supp_dir is None:
            if profile.supplementary_required:
                return self._fail(
                    items=[CheckItem(
                        code="SUPP_MISSING_DIR",
                        description="期刊要求补充材料但未找到 supplementary/ 目录",
                        status="fail",
                        detail="未找到 supplementary, supp, si, 或 supporting_information 目录",
                        fix_suggestion="创建 supplementary/ 目录并放入补充材料文件",
                    )],
                    summary="缺少补充材料目录",
                )
            else:
                return self._skip("补充材料非必需且未找到对应目录")

        # 2. List supplementary files
        supp_files: list[Path] = []
        for f in supp_dir.iterdir():
            if f.is_file() and not f.name.startswith("."):
                supp_files.append(f)

        if not supp_files:
            if profile.supplementary_required:
                items.append(CheckItem(
                    code="SUPP_EMPTY",
                    description="补充材料目录为空",
                    status="fail",
                    detail=f"目录存在但是空的: {supp_dir}",
                    fix_suggestion="将补充图表、数据表、方法细节等放入 supplementary/ 目录",
                ))
            else:
                items.append(CheckItem(
                    code="SUPP_EMPTY",
                    description="补充材料目录为空",
                    status="warn",
                ))

        # 3. File format check
        allowed_extensions = profile.supplementary_extensions or []
        for f in supp_files:
            ext = f.suffix.lower()
            if ext == ".jpeg":
                ext = ".jpg"

            if allowed_extensions and ext not in allowed_extensions:
                items.append(CheckItem(
                    code="SUPP_FORMAT",
                    description=f"补充材料格式可能不被接受: {f.name} ({ext})",
                    status="warn",
                    detail=f"期刊接受格式: {allowed_extensions}",
                    fix_suggestion=f"检查期刊是否接受 {ext} 格式，或转换为允许的格式",
                ))

        # 4. Cross-reference check: compare refs in main.tex with actual supp files
        refs_in_tex = self._extract_supp_refs(project)
        supp_filenames = {f.name for f in supp_files}

        # Check for refs pointing to non-existent files
        for ref in refs_in_tex:
            if ref not in supp_filenames:
                # Try fuzzy match
                match = self._fuzzy_match(ref, supp_filenames)
                if match:
                    items.append(CheckItem(
                        code="SUPP_REF_MISMATCH",
                        description=f"补充材料引用文件名不匹配: '{ref}' (实际文件: '{match}')",
                        status="warn",
                        detail=f"TeX 中引用: '{ref}', 实际文件: '{match}'",
                        fix_suggestion=f"将 \\ref 中的文件名更新为 '{match}'",
                    ))
                else:
                    items.append(CheckItem(
                        code="SUPP_REF_MISSING",
                        description=f"补充材料引用指向不存在的文件: '{ref}'",
                        status="fail",
                        detail=f"TeX 中引用了 '{ref}' 但 supplementary/ 目录中没有该文件",
                        fix_suggestion=f"将 '{ref}' 存入 supplementary/ 目录，或修正引用",
                    ))

        # Check for files not referenced anywhere
        for fname in supp_filenames:
            if fname not in refs_in_tex and not self._fuzzy_match(fname, refs_in_tex):
                items.append(CheckItem(
                    code="SUPP_UNREFERENCED",
                    description=f"补充材料文件未被引用: {fname}",
                    status="warn",
                    detail="稿件正文中未引用此补充文件",
                    fix_suggestion="在正文中引用该文件，或从补充材料目录中移除",
                ))

        # 5. Summary
        fail_count = sum(1 for i in items if i.status == "fail")
        warn_count = sum(1 for i in items if i.status == "warn")

        if fail_count > 0:
            status = "fail"
        elif warn_count > 0:
            status = "warn"
        else:
            status = "pass"

        return CheckResult(
            checker_name=self.name,
            status=status,
            items=items,
            summary=f"补充材料检查: {len(supp_files)} 文件, {fail_count} 错误, {warn_count} 警告",
        )

    def _extract_supp_refs(self, project: "LaTeXProject") -> set[str]:  # noqa: F821
        """Extract references to supplementary files from main tex and includes."""
        refs: set[str] = set()

        tex_files = [project.main_tex] + project.include_files
        for tex_file in tex_files:
            try:
                content = tex_file.read_text(encoding="utf-8", errors="replace")

                # Match various patterns that reference supplementary files
                patterns = [
                    r'\\(?:href|url)\{([^}]*supplementary[^}]*)\}',  # \href{...supplementary...}
                    r'\\includegraphics\*?(?:\[.*?\])?\{([^}]*supp[^}]*)\}',  # \includegraphics{...supp...}
                    r'\{([^}]*(?:supplementary|supp)\/[^}]*)\}',  # {supplementary/file}
                    r'Supplementary\s+(?:Fig|Figure|Table|Note|Section|File|Video|Data)\s*[\dA-Za-z]+',
                ]

                for pattern in patterns:
                    for match in re.finditer(pattern, content, re.IGNORECASE):
                        matched = match.group(1) if match.lastindex else match.group(0)
                        # Extract just the filename
                        filename = Path(matched).name
                        if filename:
                            refs.add(filename)
            except Exception:
                continue

        return refs

    def _fuzzy_match(self, target: str, candidates: set[str]) -> str | None:
        """Fuzzy match a target filename against a set of candidate filenames."""
        target_lower = target.lower().replace("_", "").replace("-", "").replace(" ", "")

        for cand in candidates:
            cand_lower = cand.lower().replace("_", "").replace("-", "").replace(" ", "")
            if target_lower == cand_lower:
                return cand
            if target_lower in cand_lower or cand_lower in target_lower:
                return cand

        return None
