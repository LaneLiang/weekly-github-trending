from lanes_ceo.contracts import Job
from lanes_ceo.enums import JobStatus
from lanes_ceo.workflows.paper_research import PaperResearchWorkflow
from lanes_ceo.workflows.paper_writing import PaperWritingWorkflow


def _make_job(role_group: str, message: str = "test topic") -> Job:
    return Job(
        job_id=f"job-{role_group}",
        request_id="req-1",
        role_group=role_group,
        actor=f"{role_group}-actor",
        critic=f"{role_group}-critic",
        status=JobStatus.RECEIVED,
        input={"message": message},
        workspace="runtime/jobs/test",
    )


class TestPaperResearchWorkflow:
    def test_actor_produces_research_artifact(self) -> None:
        wf = PaperResearchWorkflow()
        job = _make_job("paper_research", "transformer architectures")
        artifact = wf.run_actor(job)
        assert artifact.artifact_type == "paper_research"
        assert "transformer" in artifact.summary
        assert len(artifact.sources) >= 2
        assert len(artifact.artifact_paths) >= 2
        assert len(artifact.user_confirmations) >= 1

    def test_critic_approves_complete_artifact(self) -> None:
        wf = PaperResearchWorkflow()
        job = _make_job("paper_research")
        artifact = wf.run_actor(job)
        review = wf.run_critic(job, artifact)
        assert review.approved is True
        assert review.score >= 85

    def test_critic_rejects_insufficient_sources(self) -> None:
        wf = PaperResearchWorkflow()
        job = _make_job("paper_research")
        artifact = wf.run_actor(job)
        artifact.sources = []
        review = wf.run_critic(job, artifact)
        assert review.approved is False
        assert review.return_to_actor is True


class TestPaperWritingWorkflow:
    def test_writing_is_exempt_from_elimination(self) -> None:
        wf = PaperWritingWorkflow()
        assert wf.exempt_from_elimination is True

    def test_actor_produces_draft_artifact(self) -> None:
        wf = PaperWritingWorkflow()
        job = _make_job("paper_writing", "methods section")
        artifact = wf.run_actor(job)
        assert artifact.artifact_type == "paper_draft"
        assert len(artifact.user_confirmations) >= 2
        assert "references.bib" in artifact.artifact_paths

    def test_critic_approves_valid_draft(self) -> None:
        wf = PaperWritingWorkflow()
        job = _make_job("paper_writing")
        artifact = wf.run_actor(job)
        review = wf.run_critic(job, artifact)
        assert review.approved is True
        assert review.score >= 90

    def test_critic_rejects_missing_checkpoints(self) -> None:
        wf = PaperWritingWorkflow()
        job = _make_job("paper_writing")
        artifact = wf.run_actor(job)
        artifact.user_confirmations = []
        review = wf.run_critic(job, artifact)
        assert review.approved is False
