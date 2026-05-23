import time

from lanes_ceo.contracts import TaskRequest
from lanes_ceo.enums import JobStatus, SourceChannel
from lanes_ceo.orchestrator import DuplicateRequestError
from lanes_ceo.storage.sqlite_store import SQLiteStore


def test_idempotency_key_prevents_duplicate_requests(tmp_path) -> None:
    from lanes_ceo.notifications.outbox import NotificationOutbox
    from lanes_ceo.orchestrator import Orchestrator
    from lanes_ceo.workflows.registry import WorkflowRegistry

    store = SQLiteStore(tmp_path / "lanes.sqlite3")
    store.initialize()
    orchestrator = Orchestrator(store, WorkflowRegistry(), NotificationOutbox(store))

    request = TaskRequest(
        request_id="req-idem-1",
        source_channel=SourceChannel.SCHEDULER,
        sender="scheduler",
        raw_message="daily briefing",
        task_intent="fake",
        priority="normal",
        idempotency_key="daily-briefing-20260522-0900",
    )

    job1, _ = orchestrator.handle(request, "fake")
    assert job1.status is JobStatus.NOTIFIED

    duplicate = TaskRequest(
        request_id="req-idem-2",
        source_channel=SourceChannel.SCHEDULER,
        sender="scheduler",
        raw_message="daily briefing",
        task_intent="fake",
        priority="normal",
        idempotency_key="daily-briefing-20260522-0900",
    )

    try:
        orchestrator.handle(duplicate, "fake")
        assert False, "expected DuplicateRequestError"
    except DuplicateRequestError:
        pass


def test_requests_without_idempotency_key_are_not_deduped(tmp_path) -> None:
    from lanes_ceo.notifications.outbox import NotificationOutbox
    from lanes_ceo.orchestrator import Orchestrator
    from lanes_ceo.workflows.registry import WorkflowRegistry

    store = SQLiteStore(tmp_path / "lanes.sqlite3")
    store.initialize()
    orchestrator = Orchestrator(store, WorkflowRegistry(), NotificationOutbox(store))

    req1 = TaskRequest(
        request_id="req-no-key-1",
        source_channel=SourceChannel.CLI,
        sender="lane",
        raw_message="hello",
        task_intent="fake",
        priority="normal",
    )

    req2 = TaskRequest(
        request_id="req-no-key-2",
        source_channel=SourceChannel.CLI,
        sender="lane",
        raw_message="hello",
        task_intent="fake",
        priority="normal",
    )

    job1, _ = orchestrator.handle(req1, "fake")
    job2, _ = orchestrator.handle(req2, "fake")

    assert job1.job_id != job2.job_id
    assert job1.status is JobStatus.NOTIFIED
    assert job2.status is JobStatus.NOTIFIED
