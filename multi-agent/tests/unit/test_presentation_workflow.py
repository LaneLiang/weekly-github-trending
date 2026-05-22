import tempfile
from pathlib import Path

from lanes_ceo.contracts import Artifact, Job
from lanes_ceo.enums import JobStatus
from lanes_ceo.workflows.presentation import (
    MAX_SLIDES,
    MIN_SLIDES,
    PRESENTATION_STRUCTURE,
    PresentationWorkflow,
    _write_pptx,
)


def test_presentation_actor_produces_artifact() -> None:
    wf = PresentationWorkflow()
    job = Job(
        job_id="job-pptx-1",
        request_id="req-pptx-1",
        role_group="presentation",
        actor="presentation-actor",
        critic="presentation-critic",
        status=JobStatus.RECEIVED,
        input={"message": "组会汇报"},
        workspace="runtime/jobs/test-pptx",
    )
    artifact = wf.run_actor(job)
    assert artifact.artifact_type == "presentation"
    assert len(artifact.artifact_paths) == 1
    assert artifact.artifact_paths[0].endswith(".pptx")
    assert "页" in artifact.summary


def test_presentation_actor_creates_pptx_file() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        workspace = Path(tmpdir) / "jobs" / "test-pptx2"
        workspace.mkdir(parents=True)
        wf = PresentationWorkflow()
        job = Job(
            job_id="job-pptx-2",
            request_id="req-pptx-2",
            role_group="presentation",
            actor="presentation-actor",
            critic="presentation-critic",
            status=JobStatus.RECEIVED,
            input={"message": "组会汇报"},
            workspace=str(workspace),
        )
        artifact = wf.run_actor(job)
        pptx_path = Path(artifact.artifact_paths[0])
        assert pptx_path.exists()
        assert pptx_path.suffix == ".pptx"
        assert pptx_path.stat().st_size > 0


def test_presentation_critic_approves_valid_artifact() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        workspace = Path(tmpdir) / "jobs" / "test-pptx3"
        workspace.mkdir(parents=True)
        pptx_path = workspace / "artifacts" / "slides.pptx"
        pptx_path.parent.mkdir(parents=True)
        _write_pptx(pptx_path, "test", "")

        wf = PresentationWorkflow()
        job = Job(
            job_id="job-pptx-3",
            request_id="req-pptx-3",
            role_group="presentation",
            actor="presentation-actor",
            critic="presentation-critic",
            status=JobStatus.WAITING_REVIEW,
            input={"message": "test"},
            workspace=str(workspace),
        )
        artifact = Artifact(
            artifact_id="art-pptx-1",
            job_id="job-pptx-3",
            artifact_type="presentation",
            summary="PPT 汇报 2026W21: 测试 包含背景 进展 实验 计划内容 (15 页)",
            artifact_paths=[str(pptx_path)],
            sources=["llm-generated"],
            risks=[],
            user_confirmations=["请确认内容"],
        )
        review = wf.run_critic(job, artifact)
        assert review.approved is True
        assert review.score >= 80


def test_presentation_critic_rejects_missing_file() -> None:
    wf = PresentationWorkflow()
    job = Job(
        job_id="job-pptx-4",
        request_id="req-pptx-4",
        role_group="presentation",
        actor="presentation-actor",
        critic="presentation-critic",
        status=JobStatus.WAITING_REVIEW,
        input={"message": "test"},
        workspace="runtime/test",
    )
    artifact = Artifact(
        artifact_id="art-pptx-2",
        job_id="job-pptx-4",
        artifact_type="presentation",
        summary="PPT",
        artifact_paths=["/nonexistent/path.pptx"],
        sources=[],
        risks=[],
        user_confirmations=[],
    )
    review = wf.run_critic(job, artifact)
    assert review.approved is False
    assert any("不存在" in i for i in review.issues)


def test_presentation_critic_flags_too_few_slides() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        pptx_path = Path(tmpdir) / "few.pptx"
        _write_pptx(pptx_path, "test", "")
        from pptx import Presentation
        # Verify min slide count check works
        prs = Presentation(str(pptx_path))
        slide_count = len(prs.slides)

        wf = PresentationWorkflow()
        job = Job(
            job_id="job-pptx-5",
            request_id="req-pptx-5",
            role_group="presentation",
            actor="presentation-actor",
            critic="presentation-critic",
            status=JobStatus.WAITING_REVIEW,
            input={"message": "test"},
            workspace=str(tmpdir),
        )
        # Artifact claiming too few pages
        artifact = Artifact(
            artifact_id="art-pptx-3",
            job_id="job-pptx-5",
            artifact_type="presentation",
            summary=f"PPT (5 页)",
            artifact_paths=[str(pptx_path)],
            sources=[],
            risks=[],
            user_confirmations=[],
        )
        review = wf.run_critic(job, artifact)
        if 5 < MIN_SLIDES:
            assert not review.approved
            assert any("不足" in i for i in review.issues)


def test_presentation_structure_has_ten_sections() -> None:
    assert len(PRESENTATION_STRUCTURE) == 10


def test_write_pptx_creates_valid_file() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "test.pptx"
        slide_count = _write_pptx(path, "测试主题", "")
        assert path.exists()
        assert path.stat().st_size > 0
        assert slide_count > 0
