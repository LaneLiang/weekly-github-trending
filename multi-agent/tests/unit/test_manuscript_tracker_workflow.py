"""Unit tests for ManuscriptTrackerWorkflow."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal
from unittest.mock import MagicMock, patch

from lanes_ceo.contracts import Artifact, Job
from lanes_ceo.enums import JobStatus
from lanes_ceo.workflows.manuscript_tracker import ManuscriptTrackerWorkflow


def _make_job() -> Job:
    return Job(
        job_id="job-mt-1",
        request_id="req-mt-1",
        role_group="manuscript_tracker",
        actor="manuscript-tracker-actor",
        critic="manuscript-tracker-critic",
        status=JobStatus.RECEIVED,
        input={
            "message": "nature /some/project",
            "journal_key": "nature",
            "project_dir": "/some/project",
        },
        workspace="runtime/jobs/job-mt-1",
    )


# ── helper: build mock CheckResult / CheckItem ──


@dataclass
class _MockCheckItem:
    code: str
    description: str
    status: Literal["pass", "fail", "warn", "skip"]
    detail: str = ""
    fix_suggestion: str = ""


@dataclass
class _MockCheckResult:
    checker_name: str
    status: Literal["pass", "fail", "warn", "skip"]
    items: list = field(default_factory=list)
    summary: str = ""

    @property
    def passed(self) -> bool:
        return self.status == "pass"

    @property
    def failed(self) -> bool:
        return self.status == "fail"


# ── _extract_journal_key tests ──


def test_extract_journal_key_nature() -> None:
    """_extract_journal_key returns 'nature' for message containing 'nature'."""
    wf = ManuscriptTrackerWorkflow()
    result = wf._extract_journal_key("nature /path/to/project")
    assert result == "nature"


def test_extract_journal_key_ieee_jssc() -> None:
    """_extract_journal_key returns 'ieee_jssc' for 'jssc'."""
    wf = ManuscriptTrackerWorkflow()
    result = wf._extract_journal_key("ieee jssc paper check")
    assert result == "ieee_jssc"


def test_extract_journal_key_ieee_tpe() -> None:
    """_extract_journal_key returns 'ieee_tpe' for 'tpe'."""
    wf = ManuscriptTrackerWorkflow()
    result = wf._extract_journal_key("tpe paper submission")
    assert result == "ieee_tpe"


def test_extract_journal_key_ieee_tpe_from_ieee_tpe_combo() -> None:
    """_extract_journal_key returns 'ieee_tpe' for 'ieee' + 'tpe' in message."""
    wf = ManuscriptTrackerWorkflow()
    result = wf._extract_journal_key("submit to ieee tpe")
    assert result == "ieee_tpe"


def test_extract_journal_key_science() -> None:
    """_extract_journal_key returns 'science' for message containing 'science'."""
    wf = ManuscriptTrackerWorkflow()
    result = wf._extract_journal_key("science manuscript check")
    assert result == "science"


def test_extract_journal_key_no_known_journal() -> None:
    """_extract_journal_key returns empty string for unrecognized journal names."""
    wf = ManuscriptTrackerWorkflow()
    result = wf._extract_journal_key("submit to some random journal")
    assert result == ""


def test_extract_journal_key_ieee_generic() -> None:
    """_extract_journal_key returns 'ieee' for bare 'ieee' without tpe/jssc."""
    wf = ManuscriptTrackerWorkflow()
    result = wf._extract_journal_key("ieee submission check")
    assert result == "ieee"


# ── _extract_project_dir tests ──


def test_extract_project_dir_existing() -> None:
    """_extract_project_dir returns resolved path when directory exists."""
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        wf = ManuscriptTrackerWorkflow()
        result = wf._extract_project_dir(f"nature {tmpdir}")
        assert result == str(Path(tmpdir).resolve())


def test_extract_project_dir_nonexistent() -> None:
    """_extract_project_dir returns empty string when no existing directory."""
    wf = ManuscriptTrackerWorkflow()
    result = wf._extract_project_dir("nature /nonexistent/path/12345")
    assert result == ""


# ── actor tests ──


def test_actor_missing_params() -> None:
    """Actor returns error artifact when journal_key and project_dir are missing."""
    wf = ManuscriptTrackerWorkflow()
    job = Job(
        job_id="job-mt-err",
        request_id="req-mt-err",
        role_group="manuscript_tracker",
        actor="manuscript-tracker-actor",
        critic="manuscript-tracker-critic",
        status=JobStatus.RECEIVED,
        input={"message": "hello world", "journal_key": "", "project_dir": ""},
        workspace="runtime/jobs/job-mt-err",
    )

    with patch.object(wf, "_extract_journal_key", return_value=""):
        with patch.object(wf, "_extract_project_dir", return_value=""):
            artifact = wf.run_actor(job)

    assert artifact.artifact_type == "manuscript_tracker"
    assert "缺少必要参数" in artifact.summary


def test_actor_missing_journal_key_only() -> None:
    """Actor returns error when only journal_key is missing."""
    wf = ManuscriptTrackerWorkflow()
    job = Job(
        job_id="job-mt-err2",
        request_id="req-mt-err2",
        role_group="manuscript_tracker",
        actor="manuscript-tracker-actor",
        critic="manuscript-tracker-critic",
        status=JobStatus.RECEIVED,
        input={"message": "/some/project", "journal_key": "", "project_dir": "/some/project"},
        workspace="runtime/jobs/job-mt-err2",
    )

    with patch.object(wf, "_extract_journal_key", return_value=""):
        artifact = wf.run_actor(job)

    assert "缺少必要参数" in artifact.summary


def test_actor_valid_params_engine_success() -> None:
    """Actor produces report when ManuscriptTracker completes successfully."""
    import tempfile

    wf = ManuscriptTrackerWorkflow()
    job = _make_job()

    mock_check_results = [
        _MockCheckResult(checker_name="编译检查", status="pass", summary="OK", items=[
            _MockCheckItem(code="COMPILE_001", description="LaTeX 编译通过", status="pass"),
        ]),
        _MockCheckResult(checker_name="图片检查", status="pass", summary="OK", items=[
            _MockCheckItem(code="FIGURE_001", description="DPI >= 300", status="pass"),
        ]),
    ]

    mock_engine = MagicMock()
    mock_engine.profile.journal_name = "Nature"
    mock_engine.project_dir = Path("/some/project")
    mock_engine.main_tex = Path("/some/project/main.tex")
    mock_engine.run_full_check.return_value = mock_check_results

    with tempfile.TemporaryDirectory() as tmpdir:
        report_path = Path(tmpdir) / "compliance_report.json"
        report_path.write_text('[{"checker_name": "编译检查", "status": "pass"}]', encoding="utf-8")
        mock_engine.save_report.return_value = report_path

        with patch(
            "lanes_ceo.workflows.manuscript_tracker.ManuscriptTracker",
            return_value=mock_engine,
        ):
            artifact = wf.run_actor(job)

    assert artifact.artifact_type == "manuscript_tracker"
    assert "合计:" in artifact.summary
    assert "Nature" in artifact.summary
    assert len(artifact.artifact_paths) >= 1


def test_actor_engine_raises_exception() -> None:
    """Actor returns error artifact when ManuscriptTracker engine.run_full_check raises."""
    wf = ManuscriptTrackerWorkflow()
    job = _make_job()

    mock_engine = MagicMock()
    mock_engine.profile.journal_name = "Nature"
    mock_engine.project_dir = Path("/some/project")
    mock_engine.main_tex = Path("/some/project/main.tex")
    mock_engine.run_full_check.side_effect = RuntimeError("引擎初始化失败")

    with patch(
        "lanes_ceo.workflows.manuscript_tracker.ManuscriptTracker",
        return_value=mock_engine,
    ):
        artifact = wf.run_actor(job)

    assert "引擎异常" in artifact.summary
    assert "引擎初始化失败" in artifact.summary


def test_actor_compare_mode() -> None:
    """Actor enters comparison mode when compare_journals is set in input."""
    wf = ManuscriptTrackerWorkflow()
    job = _make_job()
    job.input["compare_journals"] = "science"

    mock_diffs = [
        {"field": "word_count_max", "value_a": 6000, "value_b": 5000, "compatible": False},
    ]

    with patch(
        "lanes_ceo.workflows.manuscript_tracker.profiles.ProfileLoader.diff_profiles",
        return_value=mock_diffs,
    ):
        artifact = wf.run_actor(job)

    assert artifact.artifact_type == "manuscript_tracker"
    assert "nature" in artifact.summary.lower()
    assert "science" in artifact.summary.lower()


def test_actor_compare_mode_exception() -> None:
    """Actor returns error artifact when ProfileLoader.diff_profiles raises."""
    wf = ManuscriptTrackerWorkflow()
    job = _make_job()
    job.input["compare_journals"] = "invalid_journal"

    with patch(
        "lanes_ceo.workflows.manuscript_tracker.profiles.ProfileLoader.diff_profiles",
        side_effect=KeyError("Unknown journal profile: invalid_journal"),
    ):
        artifact = wf.run_actor(job)

    assert artifact.artifact_type == "manuscript_tracker"
    assert "对比期刊失败" in artifact.summary
    assert "invalid_journal" in artifact.summary
    assert len(artifact.risks) > 0


# ── critic tests ──


def test_critic_approves_well_formed_report() -> None:
    """Critic approves a complete manuscript tracker report."""
    import tempfile

    wf = ManuscriptTrackerWorkflow()
    job = _make_job()

    with tempfile.TemporaryDirectory() as tmpdir:
        report_path = Path(tmpdir) / "compliance_report.json"
        report_path.write_text(
            '[{"checker_name": "编译检查", "status": "pass", "items": [], "summary": "OK"}]',
            encoding="utf-8",
        )

        artifact = Artifact(
            artifact_id="art-mt-1",
            job_id=job.job_id,
            artifact_type="manuscript_tracker",
            summary=(
                "投稿合规检查报告 — Nature\n"
                "项目: /some/project\n"
                "主文件: main.tex\n"
                "  [通过] 编译检查: OK\n"
                "  [通过] 图片检查: OK\n"
                "合计: 2 项检查, 2 通过, 0 失败"
            ),
            artifact_paths=[str(report_path)],
            sources=["latexmk", "texcount", "pdfinfo"],
            risks=[],
            user_confirmations=[],
        )
        review = wf.run_critic(job, artifact)

    assert review.approved is True
    assert review.score >= 80


def test_critic_rejects_missing_heji_line() -> None:
    """Critic rejects report without '合计:' summary line."""
    import tempfile

    wf = ManuscriptTrackerWorkflow()
    job = _make_job()

    with tempfile.TemporaryDirectory() as tmpdir:
        report_path = Path(tmpdir) / "compliance_report.json"
        report_path.write_text(
            '[{"checker_name": "编译检查", "status": "pass", "items": [], "summary": "OK"}]',
            encoding="utf-8",
        )

        artifact = Artifact(
            artifact_id="art-mt-2",
            job_id=job.job_id,
            artifact_type="manuscript_tracker",
            summary="投稿合规检查报告 — Nature\n  [通过] 编译检查: OK",
            artifact_paths=[str(report_path)],
            sources=["latexmk"],
            risks=[],
            user_confirmations=[],
        )
        review = wf.run_critic(job, artifact)

    assert review.approved is False


def test_critic_rejects_short_summary() -> None:
    """Critic rejects report with summary shorter than 100 characters."""
    wf = ManuscriptTrackerWorkflow()
    job = _make_job()

    artifact = Artifact(
        artifact_id="art-mt-3",
        job_id=job.job_id,
        artifact_type="manuscript_tracker",
        summary="short",
        artifact_paths=[],
        sources=[],
        risks=[],
        user_confirmations=[],
    )
    review = wf.run_critic(job, artifact)
    assert review.approved is False


def test_critic_rejects_engine_exception() -> None:
    """Critic rejects artifact when engine threw an exception."""
    wf = ManuscriptTrackerWorkflow()
    job = _make_job()

    artifact = Artifact(
        artifact_id="art-mt-4",
        job_id=job.job_id,
        artifact_type="manuscript_tracker",
        summary="投稿检查引擎异常: RuntimeError('引擎初始化失败')",
        artifact_paths=[],
        sources=[],
        risks=["RuntimeError('引擎初始化失败')"],
        user_confirmations=[],
    )
    review = wf.run_critic(job, artifact)
    assert review.approved is False


def test_critic_rejects_wrong_artifact_type() -> None:
    """Critic rejects when artifact_type is not 'manuscript_tracker'."""
    wf = ManuscriptTrackerWorkflow()
    job = _make_job()

    artifact = Artifact(
        artifact_id="art-mt-5",
        job_id=job.job_id,
        artifact_type="other_type",
        summary="投稿合规检查报告 — Nature\n合计: 5 项检查, 5 通过, 0 失败",
        artifact_paths=["/tmp/report.json"],
        sources=["latexmk"],
        risks=[],
        user_confirmations=[],
    )
    review = wf.run_critic(job, artifact)
    assert review.approved is False
