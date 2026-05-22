from lanes_ceo.contracts import Job
from lanes_ceo.enums import JobStatus
from lanes_ceo.workflows.briefings import AINewsWorkflow, GitHubTrendingWorkflow


def _make_job(role_group: str) -> Job:
    return Job(
        job_id=f"job-{role_group}",
        request_id="req-1",
        role_group=role_group,
        actor=f"{role_group}-actor",
        critic=f"{role_group}-critic",
        status=JobStatus.RECEIVED,
        input={"message": "weekly"},
        workspace="runtime/jobs/test",
    )


def test_github_trending_actor_produces_artifact() -> None:
    wf = GitHubTrendingWorkflow()
    job = _make_job("github_trending")
    artifact = wf.run_actor(job)
    assert artifact.artifact_type == "github_trending"
    assert len(artifact.sources) > 0


def test_github_trending_critic_approves_with_sources() -> None:
    wf = GitHubTrendingWorkflow()
    job = _make_job("github_trending")
    artifact = wf.run_actor(job)
    review = wf.run_critic(job, artifact)
    assert review.approved is True
    assert review.score >= 80


def test_ai_news_actor_produces_artifact() -> None:
    wf = AINewsWorkflow()
    job = _make_job("ai_news")
    artifact = wf.run_actor(job)
    assert artifact.artifact_type == "ai_news"
    assert len(artifact.sources) >= 3


def test_ai_news_critic_approves_with_sources() -> None:
    wf = AINewsWorkflow()
    job = _make_job("ai_news")
    artifact = wf.run_actor(job)
    review = wf.run_critic(job, artifact)
    assert review.approved is True
