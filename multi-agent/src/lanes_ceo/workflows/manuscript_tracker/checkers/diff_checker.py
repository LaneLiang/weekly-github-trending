"""DiffChecker — generate diff between manuscript versions using latexdiff."""

from __future__ import annotations

import logging
import shutil
import subprocess
from pathlib import Path

from lanes_ceo.workflows.manuscript_tracker.checkers.base import BaseChecker, CheckItem, CheckResult
from lanes_ceo.workflows.manuscript_tracker.config import DEFAULT_CONFIG

logger = logging.getLogger("lanes_ceo.manuscript_tracker.diff")


class DiffChecker(BaseChecker):
    """Generate a diff between current manuscript and a baseline version.

    Baseline priority:
    1. CLI --baseline parameter (path to old .tex file)
    2. git HEAD~1 (last commit's version)
    3. Skip with warning if neither is available
    """

    name = "diff"

    def __init__(self, baseline: str | None = None):
        self._baseline = baseline

    def check(self, project: "LaTeXProject", profile: "JournalProfile") -> CheckResult:  # noqa: F821
        if shutil.which("latexdiff") is None:
            return self._skip("latexdiff not found in PATH")

        config = DEFAULT_CONFIG
        main_tex = project.main_tex
        project_dir = project.project_dir

        old_file = self._resolve_baseline(project)
        if old_file is None:
            return self._skip(
                "无法确定比较基线：未提供 --baseline 参数且无法从 git 获取上一版本"
            )

        out_file = project_dir / f"{main_tex.stem}.diff.tex"

        logger.info("Generating latexdiff: %s vs %s -> %s", old_file, main_tex.name, out_file.name)
        try:
            proc = subprocess.run(
                ["latexdiff", str(old_file), str(main_tex)],
                capture_output=True,
                text=True,
                timeout=config.diff_timeout_seconds,
                cwd=str(project_dir),
            )
        except subprocess.TimeoutExpired:
            return self._fail(
                items=[CheckItem(
                    code="DIFF_TIMEOUT",
                    description=f"latexdiff 超时 (>{config.diff_timeout_seconds}s)",
                    status="fail",
                    detail="文稿变化较大时 latexdiff 可能运行较慢",
                    fix_suggestion="如果文稿改动极大，考虑手动标注改动部分而非使用 latexdiff",
                )],
                summary=f"latexdiff 超时 (>{config.diff_timeout_seconds}s)",
            )
        except FileNotFoundError:
            return self._skip("latexdiff not found")

        if proc.returncode != 0:
            return self._fail(
                items=[CheckItem(
                    code="DIFF_ERROR",
                    description=f"latexdiff 执行失败 (返回码 {proc.returncode})",
                    status="fail",
                    detail=proc.stderr[:500] if proc.stderr else "No error output",
                    fix_suggestion="检查旧版本文件和当前文件编码是否一致（UTF-8）",
                )],
                summary=f"latexdiff 执行失败 (返回码 {proc.returncode})",
                fix_suggestions=[proc.stderr[:300] if proc.stderr else ""],
            )

        # Write diff output
        try:
            out_file.write_text(proc.stdout, encoding="utf-8")
        except Exception as exc:
            return self._fail(
                items=[CheckItem(
                    code="DIFF_WRITE_ERROR",
                    description=f"无法写入 .diff.tex 文件: {exc}",
                    status="fail",
                    detail=str(exc),
                    fix_suggestion="检查磁盘空间和写权限",
                )],
                summary=f"写入失败: {exc}",
            )

        # Count changes
        added = proc.stdout.count("\\DIFadd{")
        deleted = proc.stdout.count("\\DIFdel{")

        items = [
            CheckItem(
                code="DIFF_GENERATED",
                description=f"latexdiff 生成完成: {added} 处新增, {deleted} 处删除",
                status="pass",
                detail=f"Output: {out_file.name}",
                fix_suggestion="",
            ),
            CheckItem(
                code="DIFF_BASELINE",
                description=f"比较基线: {Path(old_file).name}",
                status="pass",
                detail=str(old_file),
            ),
        ]

        return CheckResult(
            checker_name=self.name,
            status="pass",
            items=items,
            summary=f"生成 diff: +{added}/-{deleted}",
        )

    def _resolve_baseline(self, project: "LaTeXProject") -> str | None:  # noqa: F821
        """Resolve baseline file for latexdiff using priority chain."""
        # Priority 1: CLI --baseline
        if self._baseline:
            candidate = Path(self._baseline)
            if candidate.is_absolute() and candidate.exists():
                logger.info("Using CLI baseline: %s", candidate)
                return str(candidate)
            # Try relative to project dir
            candidate = project.project_dir / self._baseline
            if candidate.exists():
                logger.info("Using CLI baseline (relative): %s", candidate)
                return str(candidate)
            logger.warning("CLI baseline '%s' not found, falling back", self._baseline)

        # Priority 2: git HEAD~1
        if shutil.which("git") is None:
            return None

        try:
            # Check if we're in a git repo and have at least one prior commit
            proc = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                capture_output=True, text=True, timeout=10,
                cwd=str(project.project_dir),
            )
            if proc.returncode != 0:
                return None

            # Try to get the file from HEAD~1
            main_tex_rel = project.main_tex.relative_to(project.project_dir)
            proc = subprocess.run(
                ["git", "show", f"HEAD~1:{main_tex_rel.as_posix()}"],
                capture_output=True, text=True, timeout=15,
                cwd=str(project.project_dir),
            )
            if proc.returncode != 0:
                logger.info("No prior commit found for %s", main_tex_rel)
                return None

            # Write old version to temp file
            old_path = project.project_dir / f"{project.main_tex.stem}.old.tex"
            old_path.write_text(proc.stdout, encoding="utf-8")
            logger.info("Using git HEAD~1 as baseline: %s", old_path)
            return str(old_path)
        except Exception as exc:
            logger.warning("Git baseline resolution failed: %s", exc)
            return None
