"""EDATestbenchWorkflow — YAML spec → cocotb testbench → ModelSim simulation.

Generates a cocotb testbench from a YAML DUT specification, runs ModelSim/Questa
simulation, collects coverage data, and produces a verification report.

Trigger: ``lanes-ceo --role eda_testbench --message "<yaml_path>"``
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import yaml

from lanes_ceo.contracts import Artifact, CriticReview, Job

from .contracts import CoverageReport, DUTSpec, SimResult
from .tb_generator import generate_all
from .sim_runner import check_cocotb, check_simulator, run_simulation
from .coverage import extract_coverage, try_merge_coverage
from .report import generate_all_reports

logger = logging.getLogger("lanes_ceo.eda_testbench")

_CONFIG_PATH = Path(__file__).resolve().parents[4] / "config" / "eda_testbench.yaml"

_DEFAULT_CONFIG: dict[str, Any] = {
    "simulator": {"name": "questa", "gui": False},
    "cocotb": {"min_version": "1.9.0"},
    # Coverage targets here are workflow-level defaults;
    # per-DUT targets in the YAML spec take precedence.
    "coverage": {
        "enabled": True,
        "targets": {"line": 90.0, "toggle": 80.0, "branch": 85.0, "fsm": 80.0},
    },
    # These are simulation fallback defaults; the DUT YAML spec's sim
    # section (time_us, vcd_dump) takes precedence for actual runs.
    "simulation": {"default_timeout": 600, "default_time_us": 500, "vcd_dump": True},
}


def load_workflow_config(config_path: Path | None = None) -> dict[str, Any]:
    """Load eda_testbench configuration from YAML file.

    Returns a merged dict of user config over defaults. Config file is
    optional — if missing, built-in defaults are used.
    """
    path = config_path or _CONFIG_PATH
    try:
        with open(path, "r", encoding="utf-8") as fh:
            user = yaml.safe_load(fh) or {}
    except FileNotFoundError:
        logger.debug("Config file not found at %s, using defaults", path)
        return dict(_DEFAULT_CONFIG)
    except Exception as exc:
        logger.warning("Failed to load config %s: %s", path, exc)
        return dict(_DEFAULT_CONFIG)

    # Shallow merge: user keys override defaults
    merged = dict(_DEFAULT_CONFIG)
    for key in user:
        if key in merged and isinstance(user[key], dict):
            merged[key] = {**merged.get(key, {}), **user[key]}
    return merged


class EDATestbenchWorkflow:
    """EDA testbench workflow: spec → generate → simulate → coverage → report."""

    role_group = "eda_testbench"
    actor_name = "eda-testbench-actor"
    critic_name = "eda-testbench-critic"

    def run_actor(self, job: Job) -> Artifact:
        """Execute the full EDA testbench pipeline.

        Expects job.input to contain:
            yaml_path: Path to YAML DUT spec
            dut_file: Optional path to Verilog/SystemVerilog DUT file
            output_dir: Optional output directory (default: job workspace)
            sim_timeout: Optional simulation timeout in seconds (default from config)
        """
        cfg = load_workflow_config()
        message = job.input.get("message", "")
        yaml_path = job.input.get("yaml_path", message)
        dut_file = job.input.get("dut_file", "")
        output_dir = Path(job.input.get("output_dir", job.workspace))
        sim_timeout = int(job.input.get(
            "sim_timeout",
            cfg.get("simulation", {}).get("default_timeout", 600),
        ))
        sim_name = cfg.get("simulator", {}).get("name", "questa")

        errors: list[str] = []
        warnings: list[str] = []
        sources: list[str] = []
        artifact_paths: list[str] = []

        # 1. Pre-flight: check cocotb and simulator
        cocotb_min_ver = cfg.get("cocotb", {}).get("min_version", "1.9.0")
        cocotb_ok, cocotb_ver = check_cocotb(min_version=cocotb_min_ver)
        if not cocotb_ok:
            return Artifact(
                artifact_id=f"artifact-{job.job_id}",
                job_id=job.job_id,
                artifact_type="eda_testbench",
                summary="cocotb 未安装或不可导入。请运行: pip install cocotb",
                artifact_paths=[],
                sources=[],
                risks=["cocotb missing"],
                user_confirmations=[],
            )

        sim_ok, sim_msg = check_simulator(sim_name)
        if not sim_ok:
            warnings.append(f"Simulator check: {sim_msg}")

        # 2. Validate YAML spec
        if not yaml_path or not Path(yaml_path).exists():
            return Artifact(
                artifact_id=f"artifact-{job.job_id}",
                job_id=job.job_id,
                artifact_type="eda_testbench",
                summary=f"YAML spec 未找到: {yaml_path or '(未指定)'}",
                artifact_paths=[],
                sources=[],
                risks=["missing yaml spec"],
                user_confirmations=[],
            )

        # 3. Generate testbench + Makefile
        try:
            spec, tb_path, mk_path = generate_all(
                yaml_path=yaml_path,
                output_dir=output_dir,
                verilog_source=dut_file if dut_file else None,
            )
            artifact_paths.extend([str(tb_path), str(mk_path)])
            sources.append(str(yaml_path))
            if dut_file:
                sources.append(dut_file)
        except Exception as exc:
            logger.exception("Testbench generation failed")
            return Artifact(
                artifact_id=f"artifact-{job.job_id}",
                job_id=job.job_id,
                artifact_type="eda_testbench",
                summary=f"Testbench 生成失败: {exc}",
                artifact_paths=[],
                sources=[],
                risks=["generation failed"],
                user_confirmations=[],
            )

        # 4. Run simulation
        sim_result = run_simulation(
            work_dir=output_dir,
            sim=sim_name,
            timeout=sim_timeout,
            dut_file=dut_file if dut_file else None,
        )
        if sim_result.log_path:
            artifact_paths.append(sim_result.log_path)
        errors.extend(sim_result.errors)
        warnings.extend(sim_result.warnings)

        # 5. Coverage extraction (if enabled)
        cov_report = None
        if spec.coverage.enabled:
            try:
                merged = try_merge_coverage(output_dir)
                if merged is not None:
                    cov_report = extract_coverage(
                        work_dir=output_dir,
                        ucdb_file=merged.name,
                        targets=spec.coverage.targets,
                    )
                    logger.info(
                        "Coverage: line=%.1f toggle=%.1f branch=%.1f fsm=%.1f passed=%s",
                        cov_report.line or -1,
                        cov_report.toggle or -1,
                        cov_report.branch or -1,
                        cov_report.fsm or -1,
                        cov_report.passed,
                    )
            except Exception as exc:
                logger.warning("Coverage extraction failed: %s", exc)
                warnings.append(f"Coverage extraction error: {exc}")

        # 6. Generate reports
        md_path, json_path = generate_all_reports(
            spec=spec,
            sim_result=sim_result,
            coverage=cov_report,
            output_dir=output_dir,
            tb_path=str(tb_path),
        )
        artifact_paths.extend([str(md_path), str(json_path)])

        # 7. Build result summary
        lines = _build_summary(spec, sim_result, cov_report, errors, warnings)

        risks: list[str] = []
        if not sim_result.success:
            risks.append(
                f"simulation failed ({sim_result.tests_failed}/{sim_result.tests_total} tests failed)"
            )
        if not sim_ok:
            risks.append("simulator not verified")
        if cov_report is not None and not cov_report.passed:
            risks.append("coverage below threshold")

        return Artifact(
            artifact_id=f"artifact-{job.job_id}",
            job_id=job.job_id,
            artifact_type="eda_testbench",
            summary="\n".join(lines),
            artifact_paths=artifact_paths,
            sources=sources,
            risks=risks,
            user_confirmations=[],
        )

    def run_critic(self, job: Job, artifact: Artifact) -> CriticReview:
        """Review the EDA testbench artifact.

        Checks: generation completeness, simulation results, coverage
        thresholds, and report existence.
        """
        issues: list[str] = []
        summary = artifact.summary

        # Check generation success
        if "生成失败" in summary:
            issues.append("Testbench generation failed — no files produced")

        # Check required files exist
        tb_files = [p for p in artifact.artifact_paths if p.endswith(".py")]
        if not tb_files:
            issues.append("No testbench Python file generated")

        mk_files = [p for p in artifact.artifact_paths if p.endswith("Makefile")]
        if not mk_files:
            issues.append("No Makefile generated")

        # Check simulation results
        if "## Simulation Result" not in summary:
            issues.append("No simulation result section in artifact")
        elif "**Status**: FAIL" in summary:
            issues.append("Simulation failed — check errors section")

        # Check reports exist
        md_files = [p for p in artifact.artifact_paths if p.endswith("report.md")]
        json_files = [p for p in artifact.artifact_paths if p.endswith("report.json")]
        if not md_files:
            issues.append("Missing report.md")
        if not json_files:
            issues.append("Missing report.json (required for P0-3 pipeline)")

        # Check coverage if present in summary
        if "## Coverage Results" in summary:
            if "**Coverage Status**: FAIL" in summary:
                issues.append("Coverage fails to meet target thresholds")
        elif "coverage" not in summary.lower():
            pass  # Coverage disabled is OK

        # Pre-flight checks
        if "cocotb 未安装" in summary:
            issues.append("cocotb not installed — cannot run simulation")

        score = max(0, 100 - len(issues) * 15)
        approved = len(issues) == 0

        return CriticReview(
            review_id=f"review-{job.job_id}",
            job_id=job.job_id,
            review_result="approved" if approved else "returned",
            score=score,
            issues=issues,
            approved=approved,
            return_to_actor=not approved,
            handoff_note="EDA testbench 验证通过" if approved else f"发现 {len(issues)} 个问题，请修正",
        )


def _build_summary(
    spec: "DUTSpec",
    sim_result: "SimResult",
    cov_report: "CoverageReport | None",
    errors: list[str],
    warnings: list[str],
) -> list[str]:
    """Build the artifact summary in Markdown format."""
    lines = [
        f"# EDA Testbench Report: {spec.module_name}",
        "",
        f"- **DUT**: {spec.top_entity}",
        f"- **Clock**: {spec.clock.signal} @ {spec.clock.period_ns} ns",
        f"- **Reset**: {spec.reset.signal} (active {'low' if spec.reset.active_low else 'high'})",
        f"- **Ports**: {len(spec.input_ports)} in, {len(spec.output_ports)} out, {len(spec.inout_ports)} inout",
        f"- **Sim time**: {spec.sim.time_us} us, VCD={'yes' if spec.sim.vcd_dump else 'no'}",
        "",
        "## Simulation Result",
        f"- **Status**: {'PASS' if sim_result.success else 'FAIL'}",
        f"- **Tests**: {sim_result.tests_passed}/{sim_result.tests_total} passed",
        "",
    ]

    if errors:
        lines.append("## Errors")
        for e in errors[:10]:
            lines.append(f"- {e}")
        lines.append("")

    if warnings:
        lines.append("## Warnings")
        for w in warnings[:10]:
            lines.append(f"- {w}")
        lines.append("")

    if cov_report is not None:
        lines.extend([
            "## Coverage Results",
            "",
            f"- **Line**: {cov_report.line:.1f}% (target {spec.coverage.targets.line:.0f}%)" if cov_report.line is not None else "- **Line**: N/A",
            f"- **Toggle**: {cov_report.toggle:.1f}% (target {spec.coverage.targets.toggle:.0f}%)" if cov_report.toggle is not None else "- **Toggle**: N/A",
            f"- **Branch**: {cov_report.branch:.1f}% (target {spec.coverage.targets.branch:.0f}%)" if cov_report.branch is not None else "- **Branch**: N/A",
            f"- **FSM**: {cov_report.fsm:.1f}% (target {spec.coverage.targets.fsm:.0f}%)" if cov_report.fsm is not None else "- **FSM**: N/A",
            "",
            f"**Coverage Status**: {'PASS' if cov_report.passed else 'FAIL'}",
            "",
        ])

    return lines
