from lanes_ceo.contracts import CriticReview, TaskRequest
from lanes_ceo.enums import JobStatus, SourceChannel
from lanes_ceo.notifications.outbox import NotificationOutbox
from lanes_ceo.orchestrator import Orchestrator
from lanes_ceo.storage.sqlite_store import SQLiteStore
from lanes_ceo.workflows.fake import FakeWorkflow
from lanes_ceo.workflows.registry import WorkflowRegistry


class RejectingWorkflow(FakeWorkflow):
    def run_critic(self, job, artifact):
        return CriticReview(
            review_id=f"review-{job.job_id}",
            job_id=job.job_id,
            review_result="rejected",
            score=62,
            issues=["missing evidence"],
            approved=False,
            return_to_actor=True,
            handoff_note="revise",
        )


def make_request() -> TaskRequest:
    return TaskRequest(
        request_id="req-1",
        source_channel=SourceChannel.CLI,
        sender="lane",
        raw_message="hello",
        task_intent="fake",
        priority="normal",
    )


def test_approved_job_is_notified(tmp_path) -> None:
    store = SQLiteStore(tmp_path / "lanes.sqlite3")
    store.initialize()
    orchestrator = Orchestrator(store, WorkflowRegistry(), NotificationOutbox(store))

    job = orchestrator.handle(make_request(), "fake")

    assert store.get_job(job.job_id).status is JobStatus.NOTIFIED
    assert store.list_notifications(job.job_id)[0].payload["status"] == "approved"


def test_rejected_job_returns_to_actor_without_notification(tmp_path) -> None:
    store = SQLiteStore(tmp_path / "lanes.sqlite3")
    store.initialize()
    registry = WorkflowRegistry()
    registry._workflows["fake"] = RejectingWorkflow()
    orchestrator = Orchestrator(store, registry, NotificationOutbox(store))

    job = orchestrator.handle(make_request(), "fake")

    assert store.get_job(job.job_id).status is JobStatus.RETURNED_TO_ACTOR
    assert store.list_notifications(job.job_id) == []
