import tempfile
from pathlib import Path
from unittest.mock import patch

from lanes_ceo.contracts import Job
from lanes_ceo.enums import JobStatus
from lanes_ceo.workflows.weekly_report import (
    WEEKLY_REPORT_SECTIONS,
    WeeklyReportWorkflow,
    _write_docx,
    detect_empty_phrases,
    llm_response_has_all_sections,
)


def test_weekly_report_actor_produces_artifact() -> None:
    wf = WeeklyReportWorkflow()
    job = Job(
        job_id="job-wr-1",
        request_id="req-wr-1",
        role_group="weekly_report",
        actor="weekly-report-actor",
        critic="weekly-report-critic",
        status=JobStatus.RECEIVED,
        input={"message": "测试周报"},
        workspace="runtime/jobs/test-wr",
    )
    artifact = wf.run_actor(job)
    assert artifact.artifact_type == "weekly_report"
    assert len(artifact.artifact_paths) == 1
    assert artifact.artifact_paths[0].endswith(".docx")


def test_weekly_report_actor_creates_docx_file() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        workspace = Path(tmpdir) / "jobs" / "test-wr2"
        workspace.mkdir(parents=True)
        wf = WeeklyReportWorkflow()
        job = Job(
            job_id="job-wr-2",
            request_id="req-wr-2",
            role_group="weekly_report",
            actor="weekly-report-actor",
            critic="weekly-report-critic",
            status=JobStatus.RECEIVED,
            input={"message": "测试周报"},
            workspace=str(workspace),
        )
        artifact = wf.run_actor(job)
        docx_path = Path(artifact.artifact_paths[0])
        assert docx_path.exists()
        assert docx_path.suffix == ".docx"
        assert docx_path.stat().st_size > 0


def test_weekly_report_critic_approves_valid_artifact() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        workspace = Path(tmpdir) / "jobs" / "test-wr3"
        workspace.mkdir(parents=True)
        docx_path = workspace / "artifacts" / "report.docx"
        docx_path.parent.mkdir(parents=True)
        _write_docx(docx_path, "2026W21", "test")

        wf = WeeklyReportWorkflow()
        job = Job(
            job_id="job-wr-3",
            request_id="req-wr-3",
            role_group="weekly_report",
            actor="weekly-report-actor",
            critic="weekly-report-critic",
            status=JobStatus.WAITING_REVIEW,
            input={"message": "test"},
            workspace=str(workspace),
        )
        from lanes_ceo.contracts import Artifact
        artifact = Artifact(
            artifact_id="art-wr-1",
            job_id="job-wr-3",
            artifact_type="weekly_report",
            summary="周报 2026W21: 测试 包含研究背景 实验 计划 亮点",
            artifact_paths=[str(docx_path)],
            sources=["llm-generated"],
            risks=[],
            user_confirmations=["请核验数据"],
        )
        review = wf.run_critic(job, artifact)
        assert review.approved is True
        assert review.score >= 80


def test_weekly_report_critic_rejects_missing_file() -> None:
    wf = WeeklyReportWorkflow()
    job = Job(
        job_id="job-wr-4",
        request_id="req-wr-4",
        role_group="weekly_report",
        actor="weekly-report-actor",
        critic="weekly-report-critic",
        status=JobStatus.WAITING_REVIEW,
        input={"message": "test"},
        workspace="runtime/test",
    )
    from lanes_ceo.contracts import Artifact
    artifact = Artifact(
        artifact_id="art-wr-2",
        job_id="job-wr-4",
        artifact_type="weekly_report",
        summary="周报",
        artifact_paths=["/nonexistent/path.docx"],
        sources=[],
        risks=[],
        user_confirmations=[],
    )
    review = wf.run_critic(job, artifact)
    assert review.approved is False
    assert any("不存在" in i for i in review.issues)


def test_section_count_is_eight() -> None:
    assert len(WEEKLY_REPORT_SECTIONS) == 8


def test_llm_response_has_all_sections() -> None:
    assert llm_response_has_all_sections("any") is True


def test_detect_empty_phrases() -> None:
    text = "本周工作总体良好，需要进一步研究，积极推进项目"
    flags = detect_empty_phrases(text)
    assert "总体良好" in flags
    assert "进一步研究" in flags
    assert "积极推进" in flags


def test_clean_text_no_empty_phrases() -> None:
    text = "完成了3组对照实验，发现方案A在信噪比指标上优于方案B 15%"
    flags = detect_empty_phrases(text)
    assert len(flags) == 0


def test_write_docx_creates_valid_file() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "test.docx"
        _write_docx(path, "2026W21", "测试主题")
        assert path.exists()
        assert path.stat().st_size > 0
