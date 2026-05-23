"""Report generation: Markdown + JSON output from EDA testbench results.

Produces a human-readable Markdown verification report and a structured
report.json file consumable by the simulation_data_pipeline (P0-3).
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from .contracts import CoverageReport, DUTSpec, SimResult

logger = logging.getLogger("lanes_ceo.eda_report")


def generate_markdown_report(
    spec: DUTSpec,
    sim_result: SimResult,
    coverage: CoverageReport | None,
    output_path: str | Path,
    tb_path: str | None = None,
) -> Path:
    """Write a Markdown verification report.

    Args:
        spec: DUT specification.
        sim_result: Simulation results.
        coverage: Coverage data (may be None if disabled).
        output_path: Path for the output .md file.
        tb_path: Optional path to the generated testbench for reference.

    Returns:
        Path to the written report.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    lines = _build_report_lines(spec, sim_result, coverage, tb_path)
    output_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Markdown report: %s", output_path)
    return output_path


def _build_report_lines(
    spec: DUTSpec,
    sim_result: SimResult,
    coverage: CoverageReport | None,
    tb_path: str | None = None,
) -> list[str]:
    """Build report content as list of lines."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    status_icon = "PASS" if sim_result.success else "FAIL"

    lines = [
        f"# EDA Verification Report: {spec.module_name}",
        "",
        f"**Generated**: {now}",
        f"**Status**: {status_icon}",
        "",
        "---",
        "",
        "## DUT Specification",
        "",
        f"| Property | Value |",
        f"|----------|-------|",
        f"| Module | `{spec.module_name}` |",
        f"| Top Entity | `{spec.top_entity}` |",
        f"| Clock | `{spec.clock.signal}` @ {spec.clock.period_ns} ns |",
        f"| Reset | `{spec.reset.signal}` (active {'low' if spec.reset.active_low else 'high'}, {spec.reset.duration_ns} ns) |",
        f"| Input Ports | {len(spec.input_ports)} |",
        f"| Output Ports | {len(spec.output_ports)} |",
        f"| Inout Ports | {len(spec.inout_ports)} |",
        f"| Sim Time | {spec.sim.time_us} us |",
        f"| VCD Dump | {'yes' if spec.sim.vcd_dump else 'no'} |",
        "",
    ]

    # Port tables
    if spec.input_ports:
        lines.append("### Input Ports")
        lines.append("")
        lines.append("| Name | Width |")
        lines.append("|------|-------|")
        for p in spec.input_ports:
            lines.append(f"| `{p.name}` | {p.width} |")
        lines.append("")

    if spec.output_ports:
        lines.append("### Output Ports")
        lines.append("")
        lines.append("| Name | Width |")
        lines.append("|------|-------|")
        for p in spec.output_ports:
            lines.append(f"| `{p.name}` | {p.width} |")
        lines.append("")

    # Simulation results
    lines.extend([
        "---",
        "",
        "## Simulation Results",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Return Code | {sim_result.return_code} |",
        f"| Tests Passed | {sim_result.tests_passed} |",
        f"| Tests Failed | {sim_result.tests_failed} |",
        f"| Tests Total | {sim_result.tests_total} |",
        f"| Log | `{Path(sim_result.log_path).name}` |" if sim_result.log_path else "| Log | N/A |",
        "",
    ])

    if sim_result.errors:
        lines.append("### Errors")
        lines.append("")
        for e in sim_result.errors:
            lines.append(f"- {e}")
        lines.append("")

    if sim_result.warnings:
        lines.append("### Warnings")
        lines.append("")
        for w in sim_result.warnings:
            lines.append(f"- {w}")
        lines.append("")

    # Coverage
    if coverage is not None:
        lines.extend([
            "---",
            "",
            "## Coverage Results",
            "",
            f"| Metric | Value | Target | Status |",
            f"|--------|-------|--------|--------|",
        ])
        lines.append(_coverage_row("Line", coverage.line, spec.coverage.targets.line))
        lines.append(_coverage_row("Toggle", coverage.toggle, spec.coverage.targets.toggle))
        lines.append(_coverage_row("Branch", coverage.branch, spec.coverage.targets.branch))
        lines.append(_coverage_row("FSM", coverage.fsm, spec.coverage.targets.fsm))
        if coverage.total is not None:
            lines.append(f"| **Total** | **{coverage.total:.1f}%** | — | — |")
        lines.append("")
        lines.append(f"**Coverage Status**: {'PASS' if coverage.passed else 'FAIL'}")

    # Generated files
    if tb_path:
        lines.extend([
            "",
            "---",
            "",
            "## Generated Files",
            "",
            f"- Testbench: `{tb_path}`",
        ])

    return lines


def _coverage_row(label: str, value: float | None, target: float) -> str:
    """Format a coverage table row with pass/fail indicator."""
    if value is None:
        return f"| {label} | N/A | {target:.0f}% | N/A |"
    status = "PASS" if value >= target else "FAIL"
    return f"| {label} | {value:.1f}% | {target:.0f}% | {status} |"


def generate_json_report(
    spec: DUTSpec,
    sim_result: SimResult,
    coverage: CoverageReport | None,
    output_path: str | Path,
    tb_path: str | None = None,
) -> Path:
    """Write a structured report.json consumable by simulation_data_pipeline (P0-3).

    The JSON schema matches what the P0-3 experiment manifest expects,
    so eda_testbench results can flow seamlessly into the data pipeline.

    Args:
        spec: DUT specification.
        sim_result: Simulation results.
        coverage: Coverage data.
        output_path: Path for report.json.
        tb_path: Optional testbench file path for reference.

    Returns:
        Path to the written JSON file.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    ts = datetime.now(timezone.utc)
    report = {
        "experiment_id": f"eda-{spec.module_name}-{ts.strftime('%Y%m%d%H%M%S')}",
        "timestamp": ts.isoformat(),
        "dut": {
            "module_name": spec.module_name,
            "top_entity": spec.top_entity,
            "clock_period_ns": spec.clock.period_ns,
            "sim_time_us": spec.sim.time_us,
        },
        "simulation": {
            "success": sim_result.success,
            "return_code": sim_result.return_code,
            "tests_passed": sim_result.tests_passed,
            "tests_failed": sim_result.tests_failed,
            "tests_total": sim_result.tests_total,
            "errors": sim_result.errors,
            "warnings": sim_result.warnings,
        },
        "files": {
            "testbench": tb_path or "",
            "log": sim_result.log_path,
        },
    }

    if coverage is not None:
        report["coverage"] = {
            "line": coverage.line,
            "toggle": coverage.toggle,
            "branch": coverage.branch,
            "fsm": coverage.fsm,
            "total": coverage.total,
            "passed": coverage.passed,
        }

    output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info("JSON report: %s", output_path)
    return output_path


def generate_all_reports(
    spec: DUTSpec,
    sim_result: SimResult,
    coverage: CoverageReport | None,
    output_dir: str | Path,
    tb_path: str | None = None,
) -> tuple[Path, Path]:
    """Generate both Markdown and JSON reports.

    Returns:
        (md_path, json_path) tuple.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    md_path = generate_markdown_report(
        spec, sim_result, coverage, output_dir / "report.md", tb_path
    )
    json_path = generate_json_report(
        spec, sim_result, coverage, output_dir / "report.json", tb_path
    )
    return md_path, json_path
