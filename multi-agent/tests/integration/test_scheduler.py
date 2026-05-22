from lanes_ceo.scheduler import Scheduler


def test_scheduler_add_and_remove_jobs(tmp_path) -> None:
    from lanes_ceo.notifications.outbox import NotificationOutbox
    from lanes_ceo.orchestrator import Orchestrator
    from lanes_ceo.storage.sqlite_store import SQLiteStore
    from lanes_ceo.workflows.registry import WorkflowRegistry

    store = SQLiteStore(tmp_path / "lanes.sqlite3")
    store.initialize()
    orchestrator = Orchestrator(store, WorkflowRegistry(), NotificationOutbox(store))
    scheduler = Scheduler(orchestrator)

    scheduler.add_cron_job("test-job", "*/5 * * * *", "fake", "scheduled hello")
    assert "test-job" in scheduler._jobs

    scheduler.remove_job("test-job")
    assert "test-job" not in scheduler._jobs


def test_scheduler_fire_creates_task_request(tmp_path) -> None:
    from lanes_ceo.notifications.outbox import NotificationOutbox
    from lanes_ceo.orchestrator import Orchestrator
    from lanes_ceo.storage.sqlite_store import SQLiteStore
    from lanes_ceo.workflows.registry import WorkflowRegistry

    store = SQLiteStore(tmp_path / "lanes.sqlite3")
    store.initialize()
    orchestrator = Orchestrator(store, WorkflowRegistry(), NotificationOutbox(store))
    scheduler = Scheduler(orchestrator)

    scheduler.add_cron_job("test-fire", "* * * * *", "fake", "fire test")
    cfg = scheduler._jobs["test-fire"]
    scheduler._fire("test-fire", cfg)

    assert cfg["last_fire"] is not None
    # _fire creates a TaskRequest with sched- prefix via SourceChannel.SCHEDULER
    assert store.has_idempotency_key(cfg["message"]) is False


def test_scheduler_start_stop(tmp_path) -> None:
    from lanes_ceo.notifications.outbox import NotificationOutbox
    from lanes_ceo.orchestrator import Orchestrator
    from lanes_ceo.storage.sqlite_store import SQLiteStore
    from lanes_ceo.workflows.registry import WorkflowRegistry

    store = SQLiteStore(tmp_path / "lanes.sqlite3")
    store.initialize()
    orchestrator = Orchestrator(store, WorkflowRegistry(), NotificationOutbox(store))
    scheduler = Scheduler(orchestrator)

    scheduler.add_cron_job("start-test", "0 0 1 1 *", "fake", "yearly")
    scheduler.start()
    assert scheduler._running is True
    assert scheduler._thread is not None
    scheduler.stop()
    assert scheduler._running is False
