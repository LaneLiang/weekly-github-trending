import argparse
from pathlib import Path
from uuid import uuid4

from lanes_ceo.contracts import TaskRequest
from lanes_ceo.enums import SourceChannel
from lanes_ceo.notifications.outbox import NotificationOutbox
from lanes_ceo.orchestrator import Orchestrator
from lanes_ceo.storage.sqlite_store import SQLiteStore
from lanes_ceo.workflows.registry import WorkflowRegistry


def run_local_request(message: str, role_group: str, db_path: str | Path):
    store = SQLiteStore(db_path)
    store.initialize()
    request = TaskRequest(
        request_id=f"request-{uuid4().hex}",
        source_channel=SourceChannel.CLI,
        sender="lane",
        raw_message=message,
        task_intent=role_group,
        priority="normal",
    )
    orchestrator = Orchestrator(store, WorkflowRegistry(), NotificationOutbox(store))
    return orchestrator.handle(request, role_group)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("message")
    parser.add_argument("--role-group", default="fake")
    parser.add_argument("--db", default="runtime/lanes_ceo.sqlite3")
    args = parser.parse_args()
    job = run_local_request(args.message, args.role_group, args.db)
    print(f"{job.job_id} {job.status.value}")


if __name__ == "__main__":
    main()
