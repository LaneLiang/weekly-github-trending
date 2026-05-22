from lanes_ceo.contracts import CriticReview, Job, TaskRequest
from lanes_ceo.enums import JobStatus, SourceChannel
from lanes_ceo.storage.sqlite_store import SQLiteStore


def test_store_round_trips_request_job_and_review(tmp_path) -> None:
    store = SQLiteStore(tmp_path / "lanes.sqlite3")
    store.initialize()
    request = TaskRequest(
        request_id="req-1",
        source_channel=SourceChannel.CLI,
        sender="lane",
        raw_message="run fake workflow",
        task_intent="fake",
        priority="normal",
    )
    job = Job(
        job_id="job-1",
        request_id=request.request_id,
        role_group="fake",
        actor="fake-actor",
        critic="fake-critic",
        status=JobStatus.RECEIVED,
        input={"message": request.raw_message},
        workspace="runtime/jobs/job-1",
    )
    review = CriticReview(
        review_id="review-1",
        job_id=job.job_id,
        review_result="approved",
        score=95,
        issues=[],
        approved=True,
        return_to_actor=False,
        handoff_note="ok",
    )

    store.save_request(request)
    store.save_job(job)
    store.save_review(review)
    store.update_job_status(job.job_id, JobStatus.APPROVED)

    assert store.get_request("req-1").sender == "lane"
    assert store.get_job("job-1").status is JobStatus.APPROVED
    assert store.get_review("review-1").approved is True
