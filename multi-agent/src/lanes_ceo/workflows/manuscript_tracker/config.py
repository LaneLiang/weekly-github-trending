"""Default configuration for manuscript_tracker workflow.

External tool paths, timeout values, and thresholds.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ManuscriptTrackerConfig:
    """Centralized configuration for the manuscript tracker."""

    # ── file output ──
    report_filename: str = "compliance_report.json"
    checklist_filename: str = "submission_checklist.docx"

    # ── compile checker ──
    compile_timeout_seconds: int = 120
    compile_engine: str = "pdflatex"  # or xelatex, lualatex (v1 uses latexmk -pdf default)
    compile_cleanup: bool = True  # remove .aux, .log after success

    # ── figure checker ──
    figure_timeout_seconds: int = 30
    figure_dpi_min: int = 300
    figure_width_max_inches: float = 7.5

    # ── citation checker ──
    crossref_api_url: str = "https://api.crossref.org/works/"
    crossref_rate_limit: float = 1.0  # seconds between requests
    crossref_timeout: int = 15  # seconds per request

    # ── structure checker ──
    # IEEE double-column template may not have standalone abstract environment
    ieee_abstract_heuristic_words: int = 200

    # ── diff checker ──
    diff_timeout_seconds: int = 60

    # ── external tool paths (optional overrides) ──
    latexmk_path: str | None = None
    texcount_path: str | None = None
    pdfinfo_path: str | None = None
    latexdiff_path: str | None = None
    chktex_path: str | None = None

    # ── chktex ──
    chktex_rc_file: str | None = None  # custom .chktexrc path


# Singleton default configuration
DEFAULT_CONFIG = ManuscriptTrackerConfig()
