from lanes_ceo.contracts import Job
from lanes_ceo.enums import JobStatus
from lanes_ceo.workflows.fake import FakeWorkflow


def test_fake_workflow_returns_approved_review_by_default() -> None:
    job = Job(
        job_id="job-1",
        request_id="req-1",
        role_group="fake",
        actor="fake-actor",
        critic="fake-critic",
        status=JobStatus.RECEIVED,
        input={"message": "hello"},
        workspace="runtime/jobs/job-1",
    )

    artifact = FakeWorkflow().run_actor(job)
    review = FakeWorkflow().run_critic(job, artifact)

    assert artifact.summary == "fake actor processed hello"
    assert review.approved is True
    assert review.score == 95
