"""ManuscriptTracker — main orchestrator for submission compliance checking."""

from __future__ import annotations

import json
import logging
import re
import shutil
import subprocess
import traceback
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from lanes_ceo.workflows.manuscript_tracker.checkers import (
    BaseChecker,
    CheckResult,
    CitationChecker,
    CompileChecker,
    DiffChecker,
    FigureChecker,
    StructureChecker,
    SuppChecker,
)
from lanes_ceo.workflows.manuscript_tracker.checkers.base import CheckItem
from lanes_ceo.workflows.manuscript_tracker.config import DEFAULT_CONFIG
from lanes_ceo.workflows.manuscript_tracker.profiles import JournalProfile, ProfileLoader

logger = logging.getLogger("lanes_ceo.manuscript_tracker.engine")


@dataclass
class LaTeXProject:
    """Represents a parsed LaTeX manuscript project."""

    project_dir: Path
    main_tex: Path
    article_type: str | None = None

    # Discovered files
    _includes: list[Path] = field(default_factory=list)
    _bib_files: list[Path] = field(default_factory=list)
    _figure_files: list[Path] = field(default_factory=list)
    _supp_dir: Path | None = None

    @property
    def include_files(self) -> list[Path]:
        return self._includes

    @property
    def bib_files(self) -> list[Path]:
        return self._bib_files

    @property
    def figure_files(self) -> list[Path]:
        return self._figure_files

    @property
    def supp_dir(self) -> Path | None:
        return self._supp_dir

    def add_include(self, path: Path) -> None:
        if path not in self._includes:
            self._includes.append(path)

    def add_bib(self, path: Path) -> None:
        if path not in self._bib_files:
            self._bib_files.append(path)

    def add_figure(self, path: Path) -> None:
        if path not in self._figure_files:
            self._figure_files.append(path)

    def discover_supp_dir(self) -> None:
        """Discover supplementary material directory."""
        for name in ("supplementary", "supp", "si", "supporting_information"):
            candidate = self.project_dir / name
            if candidate.is_dir():
                self._supp_dir = candidate
                break


class ManuscriptTracker:
    """Main engine for manuscript submission compliance checking.

    Orchestrates all checkers, handles error isolation, generates reports.
    """

    def __init__(
        self,
        journal_key: str,
        project_dir: Path,
        main_file: str | None = None,
        article_type: str | None = None,
        baseline: str | None = None,
    ):
        self.journal_key = journal_key
        self.project_dir = Path(project_dir).resolve()
        self._main_file_arg = main_file
        self._article_type_arg = article_type
        self._baseline_arg = baseline

        # Unified forward-slash paths for cross-platform consistency
        self._normalized_dir = self.project_dir.as_posix()

        # Load profile
        self.profile: JournalProfile = ProfileLoader.load(journal_key)

        # Discover project structure
        self.project: LaTeXProject = self._init_project()

        # Determine article type
        self.article_type = article_type or self.profile.default_type
        if self.article_type not in self.profile.article_types:
            logger.warning(
                "Article type '%s' not found in profile; falling back to '%s'",
                self.article_type, self.profile.default_type,
            )
            self.article_type = self.profile.default_type

        # Tool availability cache
        self._tool_cache: dict[str, bool | None] = {}

    # ── project discovery ──

    def _init_project(self) -> LaTeXProject:
        """Initialize LaTeXProject: discover main tex, includes, bib, figures, supp."""
        main_tex = self._discover_main_tex()
        project = LaTeXProject(
            project_dir=self.project_dir,
            main_tex=main_tex,
            article_type=self._article_type_arg,
        )

        # Recursively resolve includes
        self._resolve_includes(project.main_tex, project)

        # Discover bib files
        for f in self.project_dir.iterdir():
            if f.suffix.lower() == ".bib":
                project.add_bib(f)

        # Discover figure files (excluding build artifacts)
        _excluded_dirs = {"build", "out", "dist", "__pycache__", ".git", "node_modules"}
        for ext in (".pdf", ".eps", ".png", ".jpg", ".jpeg", ".tiff", ".tif"):
            for f in self.project_dir.rglob(f"*{ext}"):
                if any(excl in f.parts for excl in _excluded_dirs):
                    continue
                project.add_figure(f)

        # Discover supplementary
        project.discover_supp_dir()

        return project

    def _discover_main_tex(self) -> Path:
        """Discover the main .tex file.

        Priority: CLI --main-file > main.tex > single .tex > error.
        """
        # Priority 1: CLI argument
        if self._main_file_arg:
            candidate = self.project_dir / self._main_file_arg
            if candidate.exists():
                logger.info("Using CLI-specified main file: %s", candidate)
                return candidate
            logger.warning("CLI main-file %s not found; falling back to auto-detect", candidate)

        # Priority 2: main.tex
        main_path = self.project_dir / "main.tex"
        if main_path.exists():
            logger.info("Found main.tex")
            return main_path

        # Priority 3: Single .tex file in directory
        tex_files = list(self.project_dir.glob("*.tex"))
        if len(tex_files) == 1:
            logger.info("Single .tex file found: %s", tex_files[0])
            return tex_files[0]

        # Priority 4: No .tex file found
        if not tex_files:
            raise FileNotFoundError(
                f"No .tex file found in {self.project_dir}. "
                f"Please specify --main-file."
            )

        # Multiple .tex files, ambiguous
        raise FileNotFoundError(
            f"Multiple .tex files found in {self.project_dir}: "
            f"{[f.name for f in tex_files]}. "
            f"Please specify --main-file."
        )

    def _resolve_includes(self, tex_file: Path, project: LaTeXProject,
                          visited: set[Path] | None = None) -> None:
        """Recursively resolve \\input and \\include directives."""
        if visited is None:
            visited = set()

        resolved = tex_file.resolve()
        if resolved in visited:
            return
        visited.add(resolved)

        if not tex_file.exists():
            logger.warning("Include file not found: %s", tex_file)
            return

        try:
            content = tex_file.read_text(encoding="utf-8", errors="replace")
        except Exception as exc:
            logger.warning("Cannot read %s: %s", tex_file, exc)
            return

        # Match \input{...} and \include{...}
        pattern = r'\\(?:input|include)\{([^}]+)\}'
        for match in re.finditer(pattern, content):
            included_name = match.group(1).strip()

            # Remove .tex extension if present (some users add it)
            if not included_name.endswith(".tex"):
                included_name += ".tex"

            # Resolve relative to the current tex file's directory
            candidate = (tex_file.parent / included_name).resolve()

            # Try a few alternatives
            if not candidate.exists():
                candidate = (self.project_dir / included_name).resolve()
            if not candidate.exists():
                alt_name = match.group(1).strip()
                if not alt_name.endswith(".tex"):
                    # Try without adding .tex (for \include)
                    candidate = (tex_file.parent / alt_name).resolve()
                    if not candidate.exists():
                        candidate = (self.project_dir / alt_name).resolve()

            if candidate.exists():
                project.add_include(candidate)
                self._resolve_includes(candidate, project, visited)
            else:
                logger.warning(
                    "Could not resolve \\input{%s} from %s",
                    match.group(1), tex_file.name,
                )

    # ── tool detection ──

    def _precheck_tools(self) -> dict[str, bool]:
        """Check which external tools are available."""
        if self._tool_cache:
            return dict(self._tool_cache)

        tools = {
            "latexmk": "latexmk",
            "texcount": "texcount",
            "pdfinfo": "pdfinfo",
            "latexdiff": "latexdiff",
            "magick": "magick",  # ImageMagick v7
            "convert": "convert",  # ImageMagick v6 fallback
            "chktex": "chktex",
        }

        for key, cmd in tools.items():
            # For ImageMagick, try both magick (v7) and convert (v6)
            if key == "magick":
                found = shutil.which("magick") is not None
                if not found:
                    found = shutil.which("convert") is not None
                    if found:
                        tools["magick_cmd"] = "convert"
                    else:
                        tools["magick_cmd"] = None
                else:
                    tools["magick_cmd"] = "magick"
            elif key == "convert":
                # Handled as fallback for magick, skip standalone check
                continue
            else:
                found = shutil.which(cmd) is not None
            self._tool_cache[key] = found

        return dict(self._tool_cache)

    # ── full check ──

    def run_full_check(self) -> list[CheckResult]:
        """Run all checkers sequentially with error isolation.

        Each checker is run in a try/except; failures are captured
        as CheckResult with status='fail' + traceback, and execution
        continues to the next checker.

        Returns:
            List of CheckResult objects, one per checker.
        """
        tools = self._precheck_tools()
        logger.info("Tool availability: %s", {k: v for k, v in tools.items() if v})

        checkers: list[BaseChecker] = [
            CompileChecker(),
            DiffChecker(baseline=self._baseline_arg),
            FigureChecker(),
            CitationChecker(),
            StructureChecker(),
            SuppChecker(),
        ]

        results: list[CheckResult] = []
        for checker in checkers:
            try:
                logger.info("Running checker: %s", checker.name)
                result = checker.check(self.project, self.profile)
                results.append(result)
                self._print_result(result)
            except Exception as exc:
                logger.exception("Checker '%s' raised exception", checker.name)
                fail_result = CheckResult(
                    checker_name=checker.name,
                    status="fail",
                    items=[CheckItem(
                        code=f"{checker.name.upper()}_EXCEPTION",
                        description=f"{checker.name} 检查异常",
                        status="fail",
                        detail=str(exc),
                        fix_suggestion="请检查项目文件完整性，或联系开发者",
                    )],
                    summary=f"检查异常: {exc}",
                    fix_suggestions=[traceback.format_exc()],
                )
                results.append(fail_result)
                self._print_result(fail_result)

        return results

    def save_report(self, results: list[CheckResult],
                    output_dir: Path | None = None) -> Path | None:
        """Save compliance report as JSON and generate checklist DOCX.

        Returns:
            Path to the JSON report file.
        """
        output_dir = output_dir or self.project_dir

        # Build report data
        report = {
            "journal": self.profile.journal_name,
            "journal_key": self.journal_key,
            "article_type": self.article_type,
            "project_dir": str(self.project_dir),
            "main_tex": str(self.project.main_tex.name),
            "check_time": datetime.now(timezone.utc).isoformat(),
            "schema_version": "1.0",
            "results": [],
        }

        for cr in results:
            report["results"].append({
                "checker_name": cr.checker_name,
                "status": cr.status,
                "summary": cr.summary,
                "fix_suggestions": cr.fix_suggestions,
                "items": [
                    {
                        "code": item.code,
                        "description": item.description,
                        "status": item.status,
                        "detail": item.detail,
                        "fix_suggestion": item.fix_suggestion,
                    }
                    for item in cr.items
                ],
            })

        json_path = output_dir / DEFAULT_CONFIG.report_filename
        try:
            json_path.write_text(
                json.dumps(report, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            logger.info("Report saved to %s", json_path)
        except Exception as exc:
            logger.error("Failed to save report: %s", exc)
            return None

        # Generate checklist DOCX
        try:
            from lanes_ceo.workflows.manuscript_tracker.generators.checklist_docx import (
                ChecklistGenerator,
            )
            docx_gen = ChecklistGenerator()
            docx_gen.generate(
                results=results,
                profile=self.profile,
                project=self.project,
                output_dir=output_dir,
            )
        except Exception as exc:
            logger.warning("Checklist DOCX generation failed: %s", exc)

        return json_path

    def _print_result(self, result: CheckResult) -> None:
        """Print a single checker result with colored terminal output."""
        # ANSI color codes
        GREEN = "\033[92m"
        RED = "\033[91m"
        YELLOW = "\033[93m"
        CYAN = "\033[96m"
        RESET = "\033[0m"
        BOLD = "\033[1m"

        icon_color = {
            "pass": f"{GREEN}[PASS]{RESET}",
            "fail": f"{RED}[FAIL]{RESET}",
            "warn": f"{YELLOW}[WARN]{RESET}",
            "skip": f"{CYAN}[SKIP]{RESET}",
        }
        icon = icon_color.get(result.status, f"[{result.status.upper()}]")

        print(f"\n{BOLD}{icon} {result.checker_name}{RESET}  {result.summary}")
        for item in result.items:
            item_icon = icon_color.get(item.status, f"[{item.status.upper()}]")
            prefix = f"  {item_icon} [{item.code}] {item.description}"
            if item.detail:
                prefix += f"  ({item.detail})"
            print(prefix)
            if item.fix_suggestion:
                print(f"       建议: {item.fix_suggestion}")


# ── convenience function ──

def create_tracker(
    journal_key: str,
    project_dir: str | Path,
    main_file: str | None = None,
    article_type: str | None = None,
    baseline: str | None = None,
) -> ManuscriptTracker:
    """Factory function to create a ManuscriptTracker instance."""
    return ManuscriptTracker(
        journal_key=journal_key,
        project_dir=Path(project_dir),
        main_file=main_file,
        article_type=article_type,
        baseline=baseline,
    )
