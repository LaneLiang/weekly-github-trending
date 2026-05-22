from lanes_ceo.contracts import Job
from lanes_ceo.enums import JobStatus
from lanes_ceo.workflows.daily_loop import DailyReportWorkflow, ReflectionWorkflow


def _make_job(role_group: str) -> Job:
    return Job(
        job_id=f"job-{role_group}",
        request_id="req-1",
        role_group=role_group,
        actor=f"{role_group}-actor",
        critic=f"{role_group}-critic",
        status=JobStatus.RECEIVED,
        input={"message": "今日工作"},
        workspace="runtime/jobs/test",
    )


def test_daily_report_actor_requests_user_confirmation() -> None:
    wf = DailyReportWorkflow()
    job = _make_job("daily_report")
    artifact = wf.run_actor(job)
    assert artifact.artifact_type == "daily_report"
    assert len(artifact.user_confirmations) > 0


def test_daily_report_critic_approves() -> None:
    wf = DailyReportWorkflow()
    job = _make_job("daily_report")
    artifact = wf.run_actor(job)
    review = wf.run_critic(job, artifact)
    assert review.approved is True


def test_reflection_actor_requests_user_confirmation() -> None:
    wf = ReflectionWorkflow()
    job = _make_job("reflection")
    artifact = wf.run_actor(job)
    assert artifact.artifact_type == "reflection"
    assert len(artifact.user_confirmations) > 0


def test_reflection_critic_approves_with_confirmations() -> None:
    wf = ReflectionWorkflow()
    job = _make_job("reflection")
    artifact = wf.run_actor(job)
    review = wf.run_critic(job, artifact)
    assert review.approved is True
