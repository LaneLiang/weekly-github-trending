"""Coverage extraction: UCDB → structured coverage data.

Invokes ModelSim/Questa ``vcover report`` to extract coverage metrics
from the merged UCDB file, and parses the text output into a CoverageReport.
"""

from __future__ import annotations

import logging
import re
import subprocess
from pathlib import Path

from .contracts import CoverageReport, CoverageTargets

logger = logging.getLogger("lanes_ceo.coverage")

# Regex patterns for vcover report -text output
_RE_LINE_COV = re.compile(r"Line Coverage[:\s]+([0-9.]+)\s*%")
_RE_TOGGLE_COV = re.compile(r"Toggle Coverage[:\s]+([0-9.]+)\s*%")
_RE_BRANCH_COV = re.compile(r"Branch Coverage[:\s]+([0-9.]+)\s*%")
_RE_FSM_COV = re.compile(r"FSM Coverage[:\s]+([0-9.]+)\s*%")
_RE_TOTAL_COV = re.compile(r"Total Coverage[:\s]+([0-9.]+)\s*%")

# Alternative patterns for HTML/text report parsing
_RE_LINE_PCT = re.compile(r"(?:Line|Statement)\s*(?:Coverage|coverage).*?([0-9.]+)\s*%", re.IGNORECASE)
_RE_TOGGLE_PCT = re.compile(r"Toggle\s*(?:Coverage|coverage).*?([0-9.]+)\s*%", re.IGNORECASE)
_RE_BRANCH_PCT = re.compile(r"Branch\s*(?:Coverage|coverage).*?([0-9.]+)\s*%", re.IGNORECASE)
_RE_FSM_PCT = re.compile(r"FSM\s*(?:Coverage|coverage).*?([0-9.]+)\s*%", re.IGNORECASE)
_RE_TOTAL_PCT = re.compile(r"(?:Total|Overall)\s*(?:Coverage|coverage).*?([0-9.]+)\s*%", re.IGNORECASE)


def extract_coverage(
    work_dir: str | Path,
    ucdb_file: str = "merged.ucdb",
    targets: CoverageTargets | None = None,
) -> CoverageReport:
    """Run vcover report and parse coverage metrics.

    Args:
        work_dir: Directory containing the UCDB file.
        ucdb_file: Name of the UCDB file (default: merged.ucdb).
        targets: Coverage threshold targets for pass/fail decision.

    Returns:
        CoverageReport with extracted metrics and pass/fail status.
    """
    work_dir = Path(work_dir)
    ucdb_path = work_dir / ucdb_file

    if not ucdb_path.exists():
        # Try finding any .ucdb file
        ucdb_files = list(work_dir.glob("*.ucdb"))
        if ucdb_files:
            ucdb_path = ucdb_files[0]
            logger.info("Using UCDB: %s", ucdb_path.name)
        else:
            logger.warning("No UCDB file found in %s", work_dir)
            return CoverageReport(raw_report="No UCDB file found")

    targets = targets or CoverageTargets()

    try:
        result = subprocess.run(
            ["vcover", "report", "-details", "-text", str(ucdb_path)],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(work_dir),
        )
    except FileNotFoundError:
        logger.warning("vcover not found — coverage data unavailable")
        return CoverageReport(raw_report="vcover not available on PATH")
    except subprocess.TimeoutExpired:
        return CoverageReport(raw_report="Coverage extraction timed out")
    except Exception as exc:
        logger.error("vcover failed: %s", exc)
        return CoverageReport(raw_report=f"vcover error: {exc}")

    raw_output = result.stdout or result.stderr
    return _parse_coverage_text(raw_output, targets)


def _parse_coverage_text(text: str, targets: CoverageTargets) -> CoverageReport:
    """Parse vcover text report output into a CoverageReport."""
    # Try primary patterns first, then fallback patterns
    line: float | None = _extract_pct(text, _RE_LINE_COV, _RE_LINE_PCT)
    toggle: float | None = _extract_pct(text, _RE_TOGGLE_COV, _RE_TOGGLE_PCT)
    branch: float | None = _extract_pct(text, _RE_BRANCH_COV, _RE_BRANCH_PCT)
    fsm: float | None = _extract_pct(text, _RE_FSM_COV, _RE_FSM_PCT)
    total: float | None = _extract_pct(text, _RE_TOTAL_COV, _RE_TOTAL_PCT)

    # Determine pass/fail against targets
    checks = []
    if line is not None:
        checks.append(line >= targets.line)
    if toggle is not None:
        checks.append(toggle >= targets.toggle)
    if branch is not None:
        checks.append(branch >= targets.branch)
    if fsm is not None:
        checks.append(fsm >= targets.fsm)

    passed = all(checks) if checks else False

    return CoverageReport(
        line=line,
        toggle=toggle,
        branch=branch,
        fsm=fsm,
        total=total,
        raw_report=text[:5000],
        passed=passed,
    )


def _extract_pct(text: str, primary: re.Pattern, fallback: re.Pattern) -> float | None:
    """Extract a coverage percentage using primary then fallback pattern."""
    for pattern in (primary, fallback):
        match = pattern.search(text)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                continue
    return None


def try_merge_coverage(
    work_dir: str | Path,
    ucdb_files: str = "*.ucdb",
    output: str = "merged.ucdb",
) -> Path | None:
    """Merge multiple UCDB files into one using vcover merge.

    Args:
        work_dir: Directory containing UCDB files.
        ucdb_files: Glob pattern for input UCDB files.
        output: Output filename for merged UCDB.

    Returns:
        Path to merged UCDB, or None if merge failed.
    """
    work_dir = Path(work_dir)
    ucdb_list = sorted(work_dir.glob(ucdb_files))
    if len(ucdb_list) < 2:
        if ucdb_list:
            return ucdb_list[0]
        return None

    output_path = work_dir / output
    cmd = ["vcover", "merge", str(output_path)] + [str(u) for u in ucdb_list]
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=120, cwd=str(work_dir)
        )
        if result.returncode != 0:
            logger.warning(
                "UCDB merge failed (rc=%d): %s", result.returncode,
                (result.stderr or result.stdout).strip()[:200],
            )
            return ucdb_list[0]
        if output_path.exists():
            logger.info("Merged %d UCDB files → %s", len(ucdb_list), output_path)
            return output_path
    except Exception as exc:
        logger.warning("UCDB merge failed: %s", exc)

    # Fallback: return the first file
    return ucdb_list[0]
