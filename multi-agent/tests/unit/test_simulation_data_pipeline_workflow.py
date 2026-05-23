"""Unit tests for SimulationDataPipelineWorkflow."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from lanes_ceo.contracts import Artifact, Job
from lanes_ceo.enums import JobStatus
from lanes_ceo.workflows.simulation_data_pipeline import (
    SimulationDataPipelineWorkflow,
)


def _make_job() -> Job:
    return Job(
        job_id="job-sdp-1",
        request_id="req-sdp-1",
        role_group="simulation_data_pipeline",
        actor="sim-data-pipeline-actor",
        critic="sim-data-pipeline-critic",
        status=JobStatus.RECEIVED,
        input={"message": "/path/to/sim_data", "topology": "buck", "source": "/path/to/sim_data"},
        workspace="runtime/jobs/job-sdp-1",
    )


# ── shared mock setup helper ──

def _setup_pipeline_mocks(
    file_map: dict,
    *,
    raw_parser=None,
    mat_parser=None,
    vcd_parser=None,
    eff_ext=None,
    rip_ext=None,
    trans_ext=None,
    bode_ext=None,
    reg_ext=None,
    aggregator=None,
    plotter=None,
    exp_manager=None,
):
    """Build a dict of patch-target → return_value for the pipeline components.

    Returns a list of patch() context managers, ready for nesting.
    Each parser/extractor/aggregator/plotter has sensible defaults for a
    successful pipeline run, so callers only need to override what differs.
    """
    mock_dataframe = MagicMock()
    mock_dataframe.steady_state_reached = True

    if raw_parser is None:
        raw_parser = MagicMock()
        raw_parser.parse.return_value = mock_dataframe

    if mat_parser is None:
        mat_parser = MagicMock()
        mat_parser.parse.return_value = mock_dataframe

    if vcd_parser is None:
        vcd_parser = MagicMock()
        vcd_parser.parse.return_value = mock_dataframe

    if eff_ext is None:
        eff_ext = MagicMock()
        eff_ext.can_extract.return_value = True
        eff_ext.extract.return_value = 0.925

    if rip_ext is None:
        rip_ext = MagicMock()
        rip_ext.can_extract.return_value = True
        rip_ext.extract.return_value = (0.012, 0.045)

    if trans_ext is None:
        trans_ext = MagicMock()
        trans_ext.can_extract.return_value = True
        trans_ext.extract.return_value = {"rise_time": 1e-6}

    if bode_ext is None:
        bode_ext = MagicMock()
        bode_ext.can_extract.return_value = False

    if reg_ext is None:
        reg_ext = MagicMock()
        reg_ext.can_extract.return_value = False

    if aggregator is None:
        aggregator = MagicMock()
        aggregator.build.return_value = MagicMock()
        aggregator.build.return_value.__len__.return_value = 1
        mock_df = MagicMock()
        aggregator.build.return_value.to_dataframe.return_value = mock_df

    if plotter is None:
        plotter = MagicMock()
        plotter.prepare_plot_data.return_value = {"title": "Efficiency Plot"}
        plotter.generate_figure.return_value = None

    if exp_manager is None:
        manifest = MagicMock()
        exp_manager = MagicMock()
        exp_manager.create_manifest.return_value = manifest

    return [
        ("lanes_ceo.workflows.simulation_data_pipeline.parsers.spice_raw.SpiceRawParser", raw_parser),
        ("lanes_ceo.workflows.simulation_data_pipeline.parsers.matlab_mat.MatlabMatParser", mat_parser),
        ("lanes_ceo.workflows.simulation_data_pipeline.parsers.verilog_vcd.VCDParser", vcd_parser),
        ("lanes_ceo.workflows.simulation_data_pipeline.extractors.efficiency.EfficiencyExtractor", eff_ext),
        ("lanes_ceo.workflows.simulation_data_pipeline.extractors.ripple.RippleExtractor", rip_ext),
        ("lanes_ceo.workflows.simulation_data_pipeline.extractors.transient.TransientExtractor", trans_ext),
        ("lanes_ceo.workflows.simulation_data_pipeline.extractors.bode.BodeExtractor", bode_ext),
        ("lanes_ceo.workflows.simulation_data_pipeline.extractors.regulation.RegulationExtractor", reg_ext),
        ("lanes_ceo.workflows.simulation_data_pipeline.aggregators.scan.ParamScanAggregator", aggregator),
        ("lanes_ceo.workflows.simulation_data_pipeline.plotters.nature_figure_bridge.NatureFigureBridge", plotter),
        ("lanes_ceo.workflows.simulation_data_pipeline.experiment.manifest.ExperimentManager", exp_manager),
    ]


def _nest_patches(targets: list, inner_fn):
    """Recursively nest patch() context managers and call inner_fn inside."""
    if not targets:
        return inner_fn()
    target, return_value = targets[0]
    with patch(target, return_value=return_value):
        return _nest_patches(targets[1:], inner_fn)


# ── actor tests ──


def test_actor_missing_source() -> None:
    """Actor returns error artifact when no source path is provided."""
    wf = SimulationDataPipelineWorkflow()
    job = Job(
        job_id="job-sdp-err",
        request_id="req-sdp-err",
        role_group="simulation_data_pipeline",
        actor="sim-data-pipeline-actor",
        critic="sim-data-pipeline-critic",
        status=JobStatus.RECEIVED,
        input={"message": "", "source": "", "topology": "buck"},
        workspace="runtime/jobs/job-sdp-err",
    )

    with patch.object(wf, "_extract_source", return_value=""):
        artifact = wf.run_actor(job)
    assert artifact.artifact_type == "simulation_data_pipeline"
    assert "缺少数据源路径" in artifact.summary


def test_actor_source_not_exist() -> None:
    """Actor returns error artifact when source path does not exist."""
    wf = SimulationDataPipelineWorkflow()
    job = Job(
        job_id="job-sdp-err2",
        request_id="req-sdp-err2",
        role_group="simulation_data_pipeline",
        actor="sim-data-pipeline-actor",
        critic="sim-data-pipeline-critic",
        status=JobStatus.RECEIVED,
        input={"message": "/nonexistent/sim_data", "source": "/nonexistent/sim_data", "topology": "buck"},
        workspace="runtime/jobs/job-sdp-err2",
    )

    artifact = wf.run_actor(job)
    assert artifact.artifact_type == "simulation_data_pipeline"
    assert "数据源不存在" in artifact.summary


def test_actor_empty_directory() -> None:
    """Actor returns error when no simulation files found in directory."""
    wf = SimulationDataPipelineWorkflow()
    job = _make_job()

    with tempfile.TemporaryDirectory() as tmpdir:
        job.input["source"] = tmpdir
        job.input["message"] = tmpdir

        with patch.object(wf, "_scan_directory", return_value={"raw": [], "mat": [], "vcd": []}):
            artifact = wf.run_actor(job)

    assert "未发现仿真数据文件" in artifact.summary


def test_actor_valid_raw_files() -> None:
    """Actor processes .raw files successfully using the shared mock helper."""
    wf = SimulationDataPipelineWorkflow()
    job = _make_job()

    with tempfile.TemporaryDirectory() as tmpdir:
        sim_dir = Path(tmpdir) / "sim_data"
        sim_dir.mkdir()
        (sim_dir / "test.raw").write_text("raw data", encoding="utf-8")
        job.input["source"] = str(sim_dir)
        job.input["message"] = str(sim_dir)

        file_map = {"raw": [sim_dir / "test.raw"], "mat": [], "vcd": []}
        mock_targets = _setup_pipeline_mocks(file_map)

        with patch.object(wf, "_scan_directory", return_value=file_map):
            artifact = _nest_patches(mock_targets, lambda: wf.run_actor(job))

    assert artifact.artifact_type == "simulation_data_pipeline"
    assert "test.raw" in artifact.summary
    assert "0.925" in artifact.summary
    assert len(artifact.artifact_paths) >= 1


def test_actor_valid_mat_files() -> None:
    """Actor processes .mat files successfully using the shared mock helper."""
    wf = SimulationDataPipelineWorkflow()
    job = _make_job()

    with tempfile.TemporaryDirectory() as tmpdir:
        sim_dir = Path(tmpdir) / "sim_data"
        sim_dir.mkdir()
        (sim_dir / "sim1.mat").write_text("placeholder", encoding="utf-8")
        job.input["source"] = str(sim_dir)
        job.input["message"] = str(sim_dir)

        file_map = {"raw": [], "mat": [sim_dir / "sim1.mat"], "vcd": []}

        # All extractors return can_extract=False → only "parsed OK"
        mock_targets = _setup_pipeline_mocks(
            file_map,
            eff_ext=_make_extractor(can_extract=False),
            rip_ext=_make_extractor(can_extract=False),
            trans_ext=_make_extractor(can_extract=False),
        )

        with patch.object(wf, "_scan_directory", return_value=file_map):
            artifact = _nest_patches(mock_targets, lambda: wf.run_actor(job))

    assert artifact.artifact_type == "simulation_data_pipeline"
    assert "sim1.mat" in artifact.summary
    assert "parsed OK" in artifact.summary


def test_actor_mixed_file_types() -> None:
    """Actor processes mixed .raw and .mat files together using shared helper."""
    wf = SimulationDataPipelineWorkflow()
    job = _make_job()

    with tempfile.TemporaryDirectory() as tmpdir:
        sim_dir = Path(tmpdir) / "sim_data"
        sim_dir.mkdir()
        (sim_dir / "test.raw").write_text("raw", encoding="utf-8")
        (sim_dir / "data.mat").write_text("mat", encoding="utf-8")
        job.input["source"] = str(sim_dir)
        job.input["message"] = str(sim_dir)

        file_map = {
            "raw": [sim_dir / "test.raw"],
            "mat": [sim_dir / "data.mat"],
            "vcd": [],
        }
        mock_targets = _setup_pipeline_mocks(file_map)

        with patch.object(wf, "_scan_directory", return_value=file_map):
            artifact = _nest_patches(mock_targets, lambda: wf.run_actor(job))

    assert artifact.artifact_type == "simulation_data_pipeline"
    assert "处理完成" in artifact.summary
    assert "2 个文件" in artifact.summary


def test_actor_valid_vcd_files() -> None:
    """Actor processes .vcd files using VCDParser via the shared mock helper."""
    wf = SimulationDataPipelineWorkflow()
    job = _make_job()

    with tempfile.TemporaryDirectory() as tmpdir:
        sim_dir = Path(tmpdir) / "sim_data"
        sim_dir.mkdir()
        (sim_dir / "wave.vcd").write_text("$dumpvars ...", encoding="utf-8")
        job.input["source"] = str(sim_dir)
        job.input["message"] = str(sim_dir)

        file_map = {"raw": [], "mat": [], "vcd": [sim_dir / "wave.vcd"]}
        mock_targets = _setup_pipeline_mocks(file_map)

        with patch.object(wf, "_scan_directory", return_value=file_map):
            artifact = _nest_patches(mock_targets, lambda: wf.run_actor(job))

    assert artifact.artifact_type == "simulation_data_pipeline"
    assert "wave.vcd" in artifact.summary
    assert len(artifact.artifact_paths) >= 1


def test_actor_parser_error_handles_gracefully() -> None:
    """Actor continues processing after a parser error on one file."""
    wf = SimulationDataPipelineWorkflow()
    job = _make_job()

    with tempfile.TemporaryDirectory() as tmpdir:
        sim_dir = Path(tmpdir) / "sim_data"
        sim_dir.mkdir()
        (sim_dir / "bad.raw").write_text("corrupt", encoding="utf-8")
        (sim_dir / "good.raw").write_text("valid", encoding="utf-8")
        job.input["source"] = str(sim_dir)
        job.input["message"] = str(sim_dir)

        file_map = {
            "raw": [sim_dir / "bad.raw", sim_dir / "good.raw"],
            "mat": [],
            "vcd": [],
        }

        # First file errors, second succeeds
        raw_parser = MagicMock()
        raw_parser.parse.side_effect = [
            ValueError("Corrupt data"),
            MagicMock(steady_state_reached=True),
        ]

        mock_targets = _setup_pipeline_mocks(file_map, raw_parser=raw_parser)

        with patch.object(wf, "_scan_directory", return_value=file_map):
            artifact = _nest_patches(mock_targets, lambda: wf.run_actor(job))

    assert artifact.artifact_type == "simulation_data_pipeline"
    assert "错误" in artifact.summary
    assert "Corrupt data" in artifact.summary
    assert "good.raw" in artifact.summary
    assert len(artifact.risks) > 0


def test_actor_all_extractors_cant_extract() -> None:
    """Actor produces 'parsed OK' only when no extractor can extract metrics."""
    wf = SimulationDataPipelineWorkflow()
    job = _make_job()

    with tempfile.TemporaryDirectory() as tmpdir:
        sim_dir = Path(tmpdir) / "sim_data"
        sim_dir.mkdir()
        (sim_dir / "data.raw").write_text("raw data", encoding="utf-8")
        job.input["source"] = str(sim_dir)
        job.input["message"] = str(sim_dir)

        file_map = {"raw": [sim_dir / "data.raw"], "mat": [], "vcd": []}

        mock_targets = _setup_pipeline_mocks(
            file_map,
            eff_ext=_make_extractor(can_extract=False),
            rip_ext=_make_extractor(can_extract=False),
            trans_ext=_make_extractor(can_extract=False),
            bode_ext=_make_extractor(can_extract=False),
            reg_ext=_make_extractor(can_extract=False),
        )

        with patch.object(wf, "_scan_directory", return_value=file_map):
            artifact = _nest_patches(mock_targets, lambda: wf.run_actor(job))

    assert artifact.artifact_type == "simulation_data_pipeline"
    assert "data.raw" in artifact.summary
    assert "parsed OK" in artifact.summary
    # No efficiency in summary since extractor returned can_extract=False
    assert "0.925" not in artifact.summary


def test_actor_ripple_extract_returns_non_tuple() -> None:
    """Actor handles ripple_ext.extract returning a non-2-tuple without crashing."""
    wf = SimulationDataPipelineWorkflow()
    job = _make_job()

    with tempfile.TemporaryDirectory() as tmpdir:
        sim_dir = Path(tmpdir) / "sim_data"
        sim_dir.mkdir()
        (sim_dir / "data.raw").write_text("raw data", encoding="utf-8")
        job.input["source"] = str(sim_dir)
        job.input["message"] = str(sim_dir)

        file_map = {"raw": [sim_dir / "data.raw"], "mat": [], "vcd": []}

        rip_ext = MagicMock()
        rip_ext.can_extract.return_value = True
        # Return a single float instead of a 2-tuple — should NOT crash
        rip_ext.extract.return_value = 0.015

        mock_targets = _setup_pipeline_mocks(file_map, rip_ext=rip_ext)

        with patch.object(wf, "_scan_directory", return_value=file_map):
            artifact = _nest_patches(mock_targets, lambda: wf.run_actor(job))

    assert artifact.artifact_type == "simulation_data_pipeline"
    assert "data.raw" in artifact.summary
    assert "处理完成" in artifact.summary


# ── helper: make a can_extract=False extractor ──

def _make_extractor(can_extract: bool):
    ext = MagicMock()
    ext.can_extract.return_value = can_extract
    if can_extract:
        ext.extract.return_value = 0.9
    return ext


# ── _extract_source tests ──


def test_extract_source_finds_existing_path_in_message() -> None:
    """_extract_source returns resolved path when a part of the message exists."""
    with tempfile.TemporaryDirectory() as tmpdir:
        sim_dir = Path(tmpdir) / "my_sim_data"
        sim_dir.mkdir()
        message = f"process topology buck {sim_dir} some extra text"
        result = SimulationDataPipelineWorkflow._extract_source(message)
        assert result == str(sim_dir.resolve())


def test_extract_source_fallback_whole_message() -> None:
    """_extract_source falls back to treating the whole message as a path."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = SimulationDataPipelineWorkflow._extract_source(tmpdir)
        assert result == str(Path(tmpdir).resolve())


def test_extract_source_no_match_returns_empty() -> None:
    """_extract_source returns '' when no path in message exists."""
    result = SimulationDataPipelineWorkflow._extract_source("no path here at all")
    assert result == ""


# ── _scan_directory tests ──


def test_scan_directory_categorized() -> None:
    """_scan_directory categorizes files by type (.raw, .mat, .vcd)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        source = Path(tmpdir)
        (source / "sim1.raw").write_text("raw", encoding="utf-8")
        (source / "sim2.raw").write_text("raw", encoding="utf-8")
        (source / "data.mat").write_text("mat", encoding="utf-8")

        result = SimulationDataPipelineWorkflow._scan_directory(source)

    assert len(result["raw"]) == 2
    assert len(result["mat"]) == 1
    assert len(result["vcd"]) == 0


def test_scan_directory_empty() -> None:
    """_scan_directory returns empty lists for empty directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        source = Path(tmpdir)
        result = SimulationDataPipelineWorkflow._scan_directory(source)

    assert result["raw"] == []
    assert result["mat"] == []
    assert result["vcd"] == []


# ── critic tests ──


def test_critic_approves_complete_pipeline() -> None:
    """Critic approves a complete pipeline execution report."""
    wf = SimulationDataPipelineWorkflow()
    job = _make_job()

    artifact = Artifact(
        artifact_id="art-sdp-1",
        job_id=job.job_id,
        artifact_type="simulation_data_pipeline",
        summary=(
            "仿真数据管线执行报告\n"
            "数据源: /path/to/sim_data\n"
            "拓朴类型: buck\n\n"
            "[run-0001] test.raw: eta=0.9250\n"
            "[run-0002] data.mat: parsed OK\n\n"
            "处理完成: 2 个文件\n"
            "Run table: 2 rows → /tmp/run_table.csv"
        ),
        artifact_paths=["/tmp/output_run"],
        sources=["/path/to/sim_data"],
        risks=["图表须人工核验"],
        user_confirmations=["请核验提取的效率/纹波/瞬态指标是否合理"],
    )
    review = wf.run_critic(job, artifact)
    assert review.approved is True


def test_critic_rejects_short_or_malformed_summary() -> None:
    """Critic rejects when '处理完成' is not in summary without errors."""
    wf = SimulationDataPipelineWorkflow()
    job = _make_job()

    artifact = Artifact(
        artifact_id="art-sdp-3",
        job_id=job.job_id,
        artifact_type="simulation_data_pipeline",
        summary="仿真数据管线执行报告\n数据源: /path",
        artifact_paths=["/tmp/output"],
        sources=["/path/to/sim_data"],
        risks=[],
        user_confirmations=[],
    )
    review = wf.run_critic(job, artifact)
    assert review.approved is False


def test_critic_approves_with_errors_when_wancheng_present() -> None:
    """Critic approves when '处理完成' is present alongside errors."""
    wf = SimulationDataPipelineWorkflow()
    job = _make_job()

    artifact = Artifact(
        artifact_id="art-sdp-4",
        job_id=job.job_id,
        artifact_type="simulation_data_pipeline",
        summary=(
            "仿真数据管线执行报告\n"
            "[run-0001] good.raw: eta=0.90\n"
            "[run-0002] bad.raw: 错误 — Corrupt\n"
            "\n处理完成: 2 个文件\n"
            "错误: 1 个文件处理失败"
        ),
        artifact_paths=["/tmp/output"],
        sources=["/path/to/sim_data"],
        risks=["Corrupt data"],
        user_confirmations=[],
    )
    review = wf.run_critic(job, artifact)
    assert review.approved is True
