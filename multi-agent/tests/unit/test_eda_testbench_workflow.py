"""Unit tests for EDATestbenchWorkflow."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from lanes_ceo.contracts import Artifact, Job
from lanes_ceo.enums import JobStatus
from lanes_ceo.workflows.eda_testbench import (
    EDATestbenchWorkflow,
    _build_summary,
    load_workflow_config,
)


def _make_job() -> Job:
    return Job(
        job_id="job-et-1",
        request_id="req-et-1",
        role_group="eda_testbench",
        actor="eda-testbench-actor",
        critic="eda-testbench-critic",
        status=JobStatus.RECEIVED,
        input={
            "message": "/path/to/dut_spec.yaml",
            "yaml_path": "/path/to/dut_spec.yaml",
            "dut_file": "/path/to/dut.v",
            "output_dir": "runtime/jobs/job-et-1",
        },
        workspace="runtime/jobs/job-et-1",
    )


# ── helpers: build mock objects for _build_summary and actor ──


def _make_mock_spec():
    """Return a mock DUTSpec with enough attributes for _build_summary."""
    from lanes_ceo.workflows.eda_testbench.contracts import (
        ClockConfig,
        CoverageConfig,
        CoverageTargets,
        DUTSpec,
        ResetConfig,
        SimConfig,
    )
    return DUTSpec(
        module_name="buck_converter",
        top_entity="buck_converter",
        clock=ClockConfig(signal="clk", period_ns=10.0),
        reset=ResetConfig(signal="rst_n", active_low=True),
        sim=SimConfig(time_us=500.0, vcd_dump=True),
        coverage=CoverageConfig(
            enabled=True,
            targets=CoverageTargets(line=90.0, toggle=80.0, branch=85.0, fsm=80.0),
        ),
    )


def _make_mock_sim_result(success=True):
    """Return a mock SimResult."""
    from lanes_ceo.workflows.eda_testbench.contracts import SimResult
    return SimResult(
        success=success,
        return_code=0 if success else 1,
        tests_passed=10 if success else 8,
        tests_failed=0 if success else 2,
        tests_total=10,
        sim_time_us=500.0,
        log_path="/tmp/sim.log",
        errors=[] if success else ["Test test_output failed"],
        warnings=[],
    )


def _make_mock_coverage(passed=True):
    """Return a mock CoverageReport."""
    from lanes_ceo.workflows.eda_testbench.contracts import CoverageReport
    return CoverageReport(
        line=95.5,
        toggle=85.0,
        branch=90.0,
        fsm=82.0,
        total=88.0,
        raw_report="<coverage>...</coverage>",
        passed=passed,
    )


# ── load_workflow_config tests ──


def test_load_workflow_config_file_missing_returns_defaults() -> None:
    """load_workflow_config returns defaults when config file doesn't exist."""
    result = load_workflow_config(Path("/nonexistent/eda_testbench.yaml"))
    assert result["simulator"]["name"] == "questa"
    assert result["cocotb"]["min_version"] == "1.9.0"
    assert result["coverage"]["enabled"] is True
    assert result["simulation"]["default_timeout"] == 600


def test_load_workflow_config_merges_user_config() -> None:
    """load_workflow_config merges user YAML over defaults."""
    with tempfile.TemporaryDirectory() as tmpdir:
        import yaml
        config_path = Path(tmpdir) / "eda_testbench.yaml"
        config_path.write_text(
            yaml.safe_dump({"simulator": {"name": "vcs", "gui": True}}),
            encoding="utf-8",
        )
        result = load_workflow_config(config_path)
    assert result["simulator"]["name"] == "vcs"
    assert result["simulator"]["gui"] is True
    # Defaults still present
    assert result["cocotb"]["min_version"] == "1.9.0"


# ── _build_summary tests ──


def test_build_summary_produces_correct_sections() -> None:
    """_build_summary includes all required sections in the report."""
    spec = _make_mock_spec()
    sim_result = _make_mock_sim_result(success=True)
    cov_report = _make_mock_coverage(passed=True)
    errors: list[str] = []
    warnings: list[str] = []

    lines = _build_summary(spec, sim_result, cov_report, errors, warnings)
    text = "\n".join(lines)

    assert "buck_converter" in text
    assert "## Simulation Result" in text
    assert "**Status**: PASS" in text
    assert "## Coverage Results" in text
    assert "**Coverage Status**: PASS" in text


def test_build_summary_with_errors() -> None:
    """_build_summary includes errors section when errors exist."""
    spec = _make_mock_spec()
    sim_result = _make_mock_sim_result(success=False)
    cov_report = None
    errors = ["Compilation failed", "Simulation aborted"]
    warnings: list[str] = []

    lines = _build_summary(spec, sim_result, cov_report, errors, warnings)
    text = "\n".join(lines)

    assert "## Errors" in text
    assert "Compilation failed" in text
    assert "**Status**: FAIL" in text


def test_build_summary_with_warnings() -> None:
    """_build_summary includes warnings section when warnings exist."""
    spec = _make_mock_spec()
    sim_result = _make_mock_sim_result(success=True)
    cov_report = None
    errors: list[str] = []
    warnings = ["VCD file large", "License warning"]

    lines = _build_summary(spec, sim_result, cov_report, errors, warnings)
    text = "\n".join(lines)

    assert "## Warnings" in text
    assert "VCD file large" in text


# ── actor tests ──


def test_actor_cocotb_missing() -> None:
    """Actor returns error artifact when cocotb is not installed."""
    wf = EDATestbenchWorkflow()
    job = _make_job()

    with patch("lanes_ceo.workflows.eda_testbench.check_cocotb",
               return_value=(False, "not found")):
        with patch("lanes_ceo.workflows.eda_testbench.load_workflow_config") as mock_cfg:
            mock_cfg.return_value = {
                "simulator": {"name": "questa", "gui": False},
                "cocotb": {"min_version": "1.9.0"},
                "coverage": {"enabled": True},
                "simulation": {"default_timeout": 600},
            }
            artifact = wf.run_actor(job)

    assert artifact.artifact_type == "eda_testbench"
    assert "cocotb" in artifact.summary.lower() and "未安装" in artifact.summary


def test_actor_missing_yaml_spec() -> None:
    """Actor returns error artifact when YAML spec file not found."""
    wf = EDATestbenchWorkflow()
    job = _make_job()
    job.input["yaml_path"] = "/nonexistent/dut.yaml"

    with patch("lanes_ceo.workflows.eda_testbench.check_cocotb",
               return_value=(True, "1.9.0")):
        with patch("lanes_ceo.workflows.eda_testbench.load_workflow_config") as mock_cfg:
            mock_cfg.return_value = {
                "simulator": {"name": "questa", "gui": False},
                "cocotb": {"min_version": "1.9.0"},
                "coverage": {"enabled": True},
                "simulation": {"default_timeout": 600},
            }
            artifact = wf.run_actor(job)

    assert "未找到" in artifact.summary


def test_actor_full_pipeline_success() -> None:
    """Actor produces complete artifact when all pipeline stages succeed."""
    wf = EDATestbenchWorkflow()
    job = _make_job()

    mock_spec = _make_mock_spec()

    with patch("lanes_ceo.workflows.eda_testbench.check_cocotb",
               return_value=(True, "1.9.0")):
        with patch("lanes_ceo.workflows.eda_testbench.check_simulator",
                   return_value=(True, "questa ready")):
            with tempfile.TemporaryDirectory() as tmpdir:
                yaml_path = Path(tmpdir) / "dut.yaml"
                yaml_path.write_text("module_name: buck_converter", encoding="utf-8")
                job.input["yaml_path"] = str(yaml_path)
                job.input["output_dir"] = tmpdir

                with patch("lanes_ceo.workflows.eda_testbench.generate_all") as mock_gen:
                    mock_gen.return_value = (
                        mock_spec,
                        Path(tmpdir) / "test_buck_converter.py",
                        Path(tmpdir) / "Makefile",
                    )
                    with patch("lanes_ceo.workflows.eda_testbench.run_simulation") as mock_sim:
                        mock_sim.return_value = _make_mock_sim_result(success=True)
                        with patch("lanes_ceo.workflows.eda_testbench.try_merge_coverage",
                                   return_value=Path(tmpdir) / "merged.ucdb"):
                            with patch("lanes_ceo.workflows.eda_testbench.extract_coverage") as mock_cov:
                                mock_cov.return_value = _make_mock_coverage(passed=True)
                                with patch("lanes_ceo.workflows.eda_testbench.generate_all_reports") as mock_rpt:
                                    mock_rpt.return_value = (
                                        Path(tmpdir) / "report.md",
                                        Path(tmpdir) / "report.json",
                                    )
                                    with patch("lanes_ceo.workflows.eda_testbench.load_workflow_config") as mock_cfg:
                                        mock_cfg.return_value = {
                                            "simulator": {"name": "questa", "gui": False},
                                            "cocotb": {"min_version": "1.9.0"},
                                            "coverage": {"enabled": True},
                                            "simulation": {"default_timeout": 600},
                                        }
                                        artifact = wf.run_actor(job)

    assert artifact.artifact_type == "eda_testbench"
    assert "## Simulation Result" in artifact.summary
    assert "PASS" in artifact.summary
    assert len(artifact.artifact_paths) >= 2


def test_actor_simulation_failure() -> None:
    """Actor reports simulation failure with risks populated.

    Note: extract_coverage is NOT mocked here because try_merge_coverage
    returns None (merge failed), so the coverage extraction block is
    never entered — extract_coverage is never called.
    """
    wf = EDATestbenchWorkflow()
    job = _make_job()

    mock_spec = _make_mock_spec()

    with patch("lanes_ceo.workflows.eda_testbench.check_cocotb",
               return_value=(True, "1.9.0")):
        with patch("lanes_ceo.workflows.eda_testbench.check_simulator",
                   return_value=(True, "questa ready")):
            with tempfile.TemporaryDirectory() as tmpdir:
                yaml_path = Path(tmpdir) / "dut.yaml"
                yaml_path.write_text("module_name: buck_converter", encoding="utf-8")
                job.input["yaml_path"] = str(yaml_path)
                job.input["output_dir"] = tmpdir

                with patch("lanes_ceo.workflows.eda_testbench.generate_all") as mock_gen:
                    mock_gen.return_value = (
                        mock_spec,
                        Path(tmpdir) / "tb.py",
                        Path(tmpdir) / "Makefile",
                    )
                    with patch("lanes_ceo.workflows.eda_testbench.run_simulation") as mock_sim:
                        mock_sim.return_value = _make_mock_sim_result(success=False)
                        # try_merge_coverage returns None — coverage extraction is skipped
                        with patch("lanes_ceo.workflows.eda_testbench.try_merge_coverage",
                                   return_value=None):
                            with patch("lanes_ceo.workflows.eda_testbench.generate_all_reports") as mock_rpt:
                                mock_rpt.return_value = (
                                    Path(tmpdir) / "report.md",
                                    Path(tmpdir) / "report.json",
                                )
                                with patch("lanes_ceo.workflows.eda_testbench.load_workflow_config") as mock_cfg:
                                    mock_cfg.return_value = {
                                        "simulator": {"name": "questa", "gui": False},
                                        "cocotb": {"min_version": "1.9.0"},
                                        "coverage": {"enabled": True},
                                        "simulation": {"default_timeout": 600},
                                    }
                                    artifact = wf.run_actor(job)

    assert "FAIL" in artifact.summary
    assert len(artifact.risks) > 0
    assert any("simulation failed" in r for r in artifact.risks)


def test_actor_coverage_below_threshold() -> None:
    """Actor reports coverage FAIL in summary and risks when below threshold."""
    wf = EDATestbenchWorkflow()
    job = _make_job()

    mock_spec = _make_mock_spec()

    with patch("lanes_ceo.workflows.eda_testbench.check_cocotb",
               return_value=(True, "1.9.0")):
        with patch("lanes_ceo.workflows.eda_testbench.check_simulator",
                   return_value=(True, "questa ready")):
            with tempfile.TemporaryDirectory() as tmpdir:
                yaml_path = Path(tmpdir) / "dut.yaml"
                yaml_path.write_text("module_name: buck_converter", encoding="utf-8")
                job.input["yaml_path"] = str(yaml_path)
                job.input["output_dir"] = tmpdir

                with patch("lanes_ceo.workflows.eda_testbench.generate_all") as mock_gen:
                    mock_gen.return_value = (
                        mock_spec,
                        Path(tmpdir) / "tb.py",
                        Path(tmpdir) / "Makefile",
                    )
                    with patch("lanes_ceo.workflows.eda_testbench.run_simulation") as mock_sim:
                        mock_sim.return_value = _make_mock_sim_result(success=True)
                        with patch("lanes_ceo.workflows.eda_testbench.try_merge_coverage",
                                   return_value=Path(tmpdir) / "merged.ucdb"):
                            with patch("lanes_ceo.workflows.eda_testbench.extract_coverage") as mock_cov:
                                mock_cov.return_value = _make_mock_coverage(passed=False)
                                with patch("lanes_ceo.workflows.eda_testbench.generate_all_reports") as mock_rpt:
                                    mock_rpt.return_value = (
                                        Path(tmpdir) / "report.md",
                                        Path(tmpdir) / "report.json",
                                    )
                                    with patch("lanes_ceo.workflows.eda_testbench.load_workflow_config") as mock_cfg:
                                        mock_cfg.return_value = {
                                            "simulator": {"name": "questa", "gui": False},
                                            "cocotb": {"min_version": "1.9.0"},
                                            "coverage": {"enabled": True},
                                            "simulation": {"default_timeout": 600},
                                        }
                                        artifact = wf.run_actor(job)

    assert "Coverage Status**: FAIL" in artifact.summary
    assert any("coverage below threshold" in r for r in artifact.risks)


def test_actor_generation_error() -> None:
    """Actor returns error artifact when testbench generation fails."""
    wf = EDATestbenchWorkflow()
    job = _make_job()

    with patch("lanes_ceo.workflows.eda_testbench.check_cocotb",
               return_value=(True, "1.9.0")):
        with patch("lanes_ceo.workflows.eda_testbench.check_simulator",
                   return_value=(True, "questa ready")):
            with tempfile.TemporaryDirectory() as tmpdir:
                yaml_path = Path(tmpdir) / "dut.yaml"
                yaml_path.write_text("module_name: bad_module", encoding="utf-8")
                job.input["yaml_path"] = str(yaml_path)

                with patch("lanes_ceo.workflows.eda_testbench.generate_all",
                           side_effect=ValueError("Invalid port definition")):
                    with patch("lanes_ceo.workflows.eda_testbench.load_workflow_config") as mock_cfg:
                        mock_cfg.return_value = {
                            "simulator": {"name": "questa", "gui": False},
                            "cocotb": {"min_version": "1.9.0"},
                            "coverage": {"enabled": True},
                            "simulation": {"default_timeout": 600},
                        }
                        artifact = wf.run_actor(job)

    assert "生成失败" in artifact.summary
    assert "Invalid port definition" in artifact.summary


def test_actor_coverage_merge_fails_pipeline_continues() -> None:
    """Actor continues pipeline with cov_report=None when coverage merge fails."""
    wf = EDATestbenchWorkflow()
    job = _make_job()

    mock_spec = _make_mock_spec()

    with patch("lanes_ceo.workflows.eda_testbench.check_cocotb",
               return_value=(True, "1.9.0")):
        with patch("lanes_ceo.workflows.eda_testbench.check_simulator",
                   return_value=(True, "questa ready")):
            with tempfile.TemporaryDirectory() as tmpdir:
                yaml_path = Path(tmpdir) / "dut.yaml"
                yaml_path.write_text("module_name: buck_converter", encoding="utf-8")
                job.input["yaml_path"] = str(yaml_path)
                job.input["output_dir"] = tmpdir

                with patch("lanes_ceo.workflows.eda_testbench.generate_all") as mock_gen:
                    mock_gen.return_value = (
                        mock_spec,
                        Path(tmpdir) / "tb.py",
                        Path(tmpdir) / "Makefile",
                    )
                    with patch("lanes_ceo.workflows.eda_testbench.run_simulation") as mock_sim:
                        mock_sim.return_value = _make_mock_sim_result(success=True)
                        # Coverage merge returns None — pipeline continues, no coverage in summary
                        with patch("lanes_ceo.workflows.eda_testbench.try_merge_coverage",
                                   return_value=None):
                            with patch("lanes_ceo.workflows.eda_testbench.generate_all_reports") as mock_rpt:
                                mock_rpt.return_value = (
                                    Path(tmpdir) / "report.md",
                                    Path(tmpdir) / "report.json",
                                )
                                with patch("lanes_ceo.workflows.eda_testbench.load_workflow_config") as mock_cfg:
                                    mock_cfg.return_value = {
                                        "simulator": {"name": "questa", "gui": False},
                                        "cocotb": {"min_version": "1.9.0"},
                                        "coverage": {"enabled": True},
                                        "simulation": {"default_timeout": 600},
                                    }
                                    artifact = wf.run_actor(job)

    assert "PASS" in artifact.summary
    # Coverage section is absent because cov_report is None
    assert "Coverage Results" not in artifact.summary
    assert len(artifact.artifact_paths) >= 2


# ── _build_summary edge case tests ──


def test_build_summary_with_none_cov_fields() -> None:
    """_build_summary generates 'N/A' lines when cov_report fields are None."""
    spec = _make_mock_spec()
    sim_result = _make_mock_sim_result(success=True)

    # Build a CoverageReport with all fields as None but passed=True
    from lanes_ceo.workflows.eda_testbench.contracts import CoverageReport
    cov_report = CoverageReport(
        line=None,
        toggle=None,
        branch=None,
        fsm=None,
        total=None,
        raw_report="",
        passed=True,
    )
    errors: list[str] = []
    warnings: list[str] = []

    lines = _build_summary(spec, sim_result, cov_report, errors, warnings)
    text = "\n".join(lines)

    assert "N/A" in text
    assert "## Coverage Results" in text
    assert "**Coverage Status**: PASS" in text


# ── critic tests ──


def test_critic_approves_complete_report() -> None:
    """Critic approves a fully complete EDA testbench report."""
    wf = EDATestbenchWorkflow()
    job = _make_job()

    artifact = Artifact(
        artifact_id="art-et-1",
        job_id=job.job_id,
        artifact_type="eda_testbench",
        summary=(
            "# EDA Testbench Report: buck_converter\n\n"
            "- **DUT**: buck_converter\n"
            "- **Clock**: clk @ 10.0 ns\n\n"
            "## Simulation Result\n"
            "- **Status**: PASS\n"
            "- **Tests**: 10/10 passed\n\n"
            "## Coverage Results\n\n"
            "- **Line**: 95.5% (target 90%)\n"
            "- **Toggle**: 85.0% (target 80%)\n"
            "**Coverage Status**: PASS\n"
        ),
        artifact_paths=[
            "/tmp/test_buck_converter.py",
            "/tmp/Makefile",
            "/tmp/report.md",
            "/tmp/report.json",
        ],
        sources=["/path/to/dut.yaml"],
        risks=[],
        user_confirmations=[],
    )
    review = wf.run_critic(job, artifact)
    assert review.approved is True
    assert review.score >= 80


def test_critic_rejects_missing_testbench_py() -> None:
    """Critic rejects when no testbench .py file is in artifact_paths."""
    wf = EDATestbenchWorkflow()
    job = _make_job()

    artifact = Artifact(
        artifact_id="art-et-2",
        job_id=job.job_id,
        artifact_type="eda_testbench",
        summary="## Simulation Result\n- **Status**: PASS\n- **Tests**: 10/10 passed",
        artifact_paths=["/tmp/Makefile", "/tmp/report.md", "/tmp/report.json"],
        sources=["/path/to/dut.yaml"],
        risks=[],
        user_confirmations=[],
    )
    review = wf.run_critic(job, artifact)
    assert review.approved is False


def test_critic_rejects_missing_makefile() -> None:
    """Critic rejects when no Makefile is in artifact_paths."""
    wf = EDATestbenchWorkflow()
    job = _make_job()

    artifact = Artifact(
        artifact_id="art-et-3",
        job_id=job.job_id,
        artifact_type="eda_testbench",
        summary="## Simulation Result\n- **Status**: PASS\n- **Tests**: 10/10 passed",
        artifact_paths=["/tmp/test_buck_converter.py", "/tmp/report.md", "/tmp/report.json"],
        sources=["/path/to/dut.yaml"],
        risks=[],
        user_confirmations=[],
    )
    review = wf.run_critic(job, artifact)
    assert review.approved is False


def test_critic_rejects_missing_report_md() -> None:
    """Critic rejects when report.md is missing from artifact_paths."""
    wf = EDATestbenchWorkflow()
    job = _make_job()

    artifact = Artifact(
        artifact_id="art-et-4",
        job_id=job.job_id,
        artifact_type="eda_testbench",
        summary="## Simulation Result\n- **Status**: PASS\n- **Tests**: 10/10 passed",
        artifact_paths=[
            "/tmp/test_buck_converter.py",
            "/tmp/Makefile",
            "/tmp/report.json",
        ],
        sources=["/path/to/dut.yaml"],
        risks=[],
        user_confirmations=[],
    )
    review = wf.run_critic(job, artifact)
    assert review.approved is False


def test_critic_rejects_simulation_fail() -> None:
    """Critic rejects when simulation status is FAIL."""
    wf = EDATestbenchWorkflow()
    job = _make_job()

    artifact = Artifact(
        artifact_id="art-et-5",
        job_id=job.job_id,
        artifact_type="eda_testbench",
        summary="## Simulation Result\n- **Status**: FAIL\n- **Tests**: 8/10 passed",
        artifact_paths=[
            "/tmp/test_buck_converter.py",
            "/tmp/Makefile",
            "/tmp/report.md",
            "/tmp/report.json",
        ],
        sources=["/path/to/dut.yaml"],
        risks=["simulation failed (2/10 tests failed)"],
        user_confirmations=[],
    )
    review = wf.run_critic(job, artifact)
    assert review.approved is False
