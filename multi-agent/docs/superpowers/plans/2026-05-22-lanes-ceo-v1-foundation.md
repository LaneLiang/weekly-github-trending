# LANEs_CEO V1 Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first runnable `LANEs_CEO` foundation slice that persists task requests and jobs, enforces the actor/critic review gate, and exposes a local CLI entrypoint for later Hermes ingress integration.

**Architecture:** Implement a Python package with dependency-light domain contracts, a SQLite runtime store, a workflow registry, an orchestrator, and a CLI ingress adapter. Keep messaging gateways, browser automation, Excel reporting, and real role workflows outside this first slice so later plans can attach them through contracts already covered by tests.

**Tech Stack:** Python 3.11+, `pytest`, standard-library `dataclasses` and `enum`, standard-library `sqlite3`, `argparse`, JSON serialization.

---

## File Map

| Path | Responsibility |
| --- | --- |
| `pyproject.toml` | Package metadata, editable install and pytest configuration |
| `.gitignore` | Ignore runtime database, artifacts and local secrets |
| `src/lanes_ceo/enums.py` | Job status, source channel and notification type enums |
| `src/lanes_ceo/contracts.py` | Dataclass contracts defined by the requirements spec |
| `src/lanes_ceo/storage/schema.py` | SQLite DDL for foundation tables |
| `src/lanes_ceo/storage/sqlite_store.py` | Persistence API for foundation requests, jobs, reviews and notifications |
| `src/lanes_ceo/workflows/base.py` | Actor, critic and workflow protocols |
| `src/lanes_ceo/workflows/fake.py` | Deterministic fake workflow used by local CLI and tests |
| `src/lanes_ceo/workflows/registry.py` | Workflow lookup by role group |
| `src/lanes_ceo/notifications/outbox.py` | Persist notifications after approved jobs |
| `src/lanes_ceo/orchestrator.py` | Actor/critic review flow and job state transitions |
| `src/lanes_ceo/ingress/cli.py` | Local CLI adapter that creates a `TaskRequest` |
| `tests/unit/` | Contract and store tests |
| `tests/integration/` | Review-gate and CLI flow tests |

## Task 1: Scaffold the Python Package

**Files:**
- Create: `pyproject.toml`
- Create: `.gitignore`
- Create: `src/lanes_ceo/__init__.py`
- Create: `src/lanes_ceo/storage/__init__.py`
- Create: `src/lanes_ceo/workflows/__init__.py`
- Create: `src/lanes_ceo/notifications/__init__.py`
- Create: `src/lanes_ceo/ingress/__init__.py`
- Create: `tests/unit/test_package_smoke.py`

- [ ] **Step 1: Write the failing smoke test**

```python
# tests/unit/test_package_smoke.py
from lanes_ceo import APP_NAME


def test_package_exports_app_name() -> None:
    assert APP_NAME == "LANEs_CEO"
```

- [ ] **Step 2: Run the smoke test and confirm the import fails**

Run:

```powershell
python -m pytest tests/unit/test_package_smoke.py -q
```

Expected: fail with an import error because `lanes_ceo` is not packaged yet.

- [ ] **Step 3: Add the package configuration**

```toml
# pyproject.toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "lanes-ceo"
version = "0.1.0"
requires-python = ">=3.11"

[project.optional-dependencies]
dev = ["pytest>=8"]

[project.scripts]
lanes-ceo = "lanes_ceo.ingress.cli:main"

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
```

```gitignore
# .gitignore
__pycache__/
.pytest_cache/
*.pyc
runtime/
secret.local.*
```

```python
# src/lanes_ceo/__init__.py
APP_NAME = "LANEs_CEO"
```

Create empty `__init__.py` files under `storage`, `workflows`, `notifications`, and `ingress`.

- [ ] **Step 4: Install the package in editable development mode**

Run:

```powershell
python -m pip install -e ".[dev]"
```

Expected: the `lanes-ceo` package and `pytest` development dependency install successfully.

- [ ] **Step 5: Run the smoke test and confirm it passes**

Run:

```powershell
python -m pytest tests/unit/test_package_smoke.py -q
```

Expected: `1 passed`.

- [ ] **Step 6: Commit the package scaffold**

```powershell
git add pyproject.toml .gitignore src tests/unit/test_package_smoke.py
git commit -m "chore: scaffold lanes ceo package"
```

## Task 2: Define Foundation Contracts and Enums

**Files:**
- Create: `src/lanes_ceo/enums.py`
- Create: `src/lanes_ceo/contracts.py`
- Create: `tests/unit/test_contracts.py`

- [ ] **Step 1: Write contract tests**

```python
# tests/unit/test_contracts.py
from lanes_ceo.contracts import Artifact, CriticReview, NotificationEvent, TaskRequest
from lanes_ceo.enums import JobStatus, NotificationType, SourceChannel


def test_task_request_keeps_ingress_context() -> None:
    request = TaskRequest(
        request_id="req-1",
        source_channel=SourceChannel.FEISHU,
        sender="lane",
        raw_message="summarize this",
        task_intent="briefing",
        priority="normal",
        attachments=["doc://draft"],
        authorization_context={"trusted_sender": True},
    )

    assert request.source_channel is SourceChannel.FEISHU
    assert request.authorization_context["trusted_sender"] is True


def test_review_and_notification_contracts_capture_gate_result() -> None:
    artifact = Artifact(
        artifact_id="art-1",
        job_id="job-1",
        artifact_type="summary",
        summary="draft result",
        artifact_paths=[],
        sources=["fake"],
        risks=[],
        user_confirmations=[],
    )
    review = CriticReview(
        review_id="review-1",
        job_id="job-1",
        review_result="approved",
        score=96,
        issues=[],
        approved=True,
        return_to_actor=False,
        handoff_note="ready",
    )
    notification = NotificationEvent(
        notification_id="note-1",
        job_id="job-1",
        target_channel=SourceChannel.FEISHU,
        target_recipient="secretary-group",
        message_type=NotificationType.JOB_COMPLETED,
        payload={"artifact_id": artifact.artifact_id},
        receipt_required=False,
        retry_policy="default",
    )

    assert review.score == 96
    assert notification.message_type is NotificationType.JOB_COMPLETED
    assert JobStatus.APPROVED.value == "approved"
```

- [ ] **Step 2: Run the contract tests and confirm they fail**

Run:

```powershell
python -m pytest tests/unit/test_contracts.py -q
```

Expected: fail because contracts and enums do not exist.

- [ ] **Step 3: Implement enum values**

```python
# src/lanes_ceo/enums.py
from enum import StrEnum


class SourceChannel(StrEnum):
    FEISHU = "feishu"
    WEIXIN = "weixin"
    QQ = "qq"
    SCHEDULER = "scheduler"
    CLI = "cli"


class JobStatus(StrEnum):
    RECEIVED = "received"
    RUNNING_ACTOR = "running_actor"
    WAITING_REVIEW = "waiting_review"
    RETURNED_TO_ACTOR = "returned_to_actor"
    WAITING_USER = "waiting_user"
    APPROVED = "approved"
    NOTIFIED = "notified"
    FAILED = "failed"


class NotificationType(StrEnum):
    JOB_RECEIVED = "job_received"
    JOB_STARTED = "job_started"
    JOB_COMPLETED = "job_completed"
    JOB_FAILED = "job_failed"
    WAITING_USER = "waiting_user"
```

- [ ] **Step 4: Implement dataclass contracts**

```python
# src/lanes_ceo/contracts.py
from dataclasses import dataclass, field
from typing import Any

from lanes_ceo.enums import JobStatus, NotificationType, SourceChannel


@dataclass(slots=True)
class TaskRequest:
    request_id: str
    source_channel: SourceChannel
    sender: str
    raw_message: str
    task_intent: str
    priority: str
    attachments: list[str] = field(default_factory=list)
    authorization_context: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class Job:
    job_id: str
    request_id: str
    role_group: str
    actor: str
    critic: str
    status: JobStatus
    input: dict[str, Any]
    workspace: str
    artifact_paths: list[str] = field(default_factory=list)
    retry_count: int = 0
    timeout_seconds: int = 300
    failure_reason: str | None = None


@dataclass(slots=True)
class Artifact:
    artifact_id: str
    job_id: str
    artifact_type: str
    summary: str
    artifact_paths: list[str]
    sources: list[str]
    risks: list[str]
    user_confirmations: list[str]


@dataclass(slots=True)
class CriticReview:
    review_id: str
    job_id: str
    review_result: str
    score: int
    issues: list[str]
    approved: bool
    return_to_actor: bool
    handoff_note: str


@dataclass(slots=True)
class ScoreRecord:
    score_id: str
    job_id: str
    scored_role: str
    scorer_role: str
    score: int
    rating: str
    review_summary: str
    created_at: str
    month_bucket: str


@dataclass(slots=True)
class NotificationEvent:
    notification_id: str
    job_id: str
    target_channel: SourceChannel
    target_recipient: str
    message_type: NotificationType
    payload: dict[str, Any]
    receipt_required: bool
    retry_policy: str
```

- [ ] **Step 5: Run the contract tests and confirm they pass**

Run:

```powershell
python -m pytest tests/unit/test_contracts.py -q
```

Expected: `2 passed`.

- [ ] **Step 6: Commit the contracts**

```powershell
git add src/lanes_ceo/enums.py src/lanes_ceo/contracts.py tests/unit/test_contracts.py
git commit -m "feat: define lanes ceo contracts"
```

## Task 3: Persist Foundation Records in SQLite

**Files:**
- Create: `src/lanes_ceo/storage/schema.py`
- Create: `src/lanes_ceo/storage/sqlite_store.py`
- Create: `tests/unit/test_sqlite_store.py`

- [ ] **Step 1: Write the store test**

```python
# tests/unit/test_sqlite_store.py
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
```

- [ ] **Step 2: Run the store test and confirm it fails**

Run:

```powershell
python -m pytest tests/unit/test_sqlite_store.py -q
```

Expected: fail because the SQLite store does not exist.

- [ ] **Step 3: Add the schema**

```python
# src/lanes_ceo/storage/schema.py
FOUNDATION_SCHEMA = """
CREATE TABLE IF NOT EXISTS task_requests (
    request_id TEXT PRIMARY KEY,
    source_channel TEXT NOT NULL,
    sender TEXT NOT NULL,
    raw_message TEXT NOT NULL,
    task_intent TEXT NOT NULL,
    priority TEXT NOT NULL,
    attachments_json TEXT NOT NULL,
    authorization_context_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS jobs (
    job_id TEXT PRIMARY KEY,
    request_id TEXT NOT NULL,
    role_group TEXT NOT NULL,
    actor TEXT NOT NULL,
    critic TEXT NOT NULL,
    status TEXT NOT NULL,
    input_json TEXT NOT NULL,
    workspace TEXT NOT NULL,
    artifact_paths_json TEXT NOT NULL,
    retry_count INTEGER NOT NULL,
    timeout_seconds INTEGER NOT NULL,
    failure_reason TEXT
);

CREATE TABLE IF NOT EXISTS critic_reviews (
    review_id TEXT PRIMARY KEY,
    job_id TEXT NOT NULL,
    review_result TEXT NOT NULL,
    score INTEGER NOT NULL,
    issues_json TEXT NOT NULL,
    approved INTEGER NOT NULL,
    return_to_actor INTEGER NOT NULL,
    handoff_note TEXT NOT NULL
);
"""
```

- [ ] **Step 4: Add the store implementation**

```python
# src/lanes_ceo/storage/sqlite_store.py
import json
import sqlite3
from pathlib import Path

from lanes_ceo.contracts import CriticReview, Job, TaskRequest
from lanes_ceo.enums import JobStatus, SourceChannel
from lanes_ceo.storage.schema import FOUNDATION_SCHEMA


class SQLiteStore:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def initialize(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.path) as conn:
            conn.executescript(FOUNDATION_SCHEMA)

    def save_request(self, request: TaskRequest) -> None:
        with sqlite3.connect(self.path) as conn:
            conn.execute(
                """
                INSERT INTO task_requests VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    request.request_id,
                    request.source_channel.value,
                    request.sender,
                    request.raw_message,
                    request.task_intent,
                    request.priority,
                    json.dumps(request.attachments),
                    json.dumps(request.authorization_context),
                ),
            )

    def get_request(self, request_id: str) -> TaskRequest:
        with sqlite3.connect(self.path) as conn:
            row = conn.execute(
                "SELECT * FROM task_requests WHERE request_id = ?",
                (request_id,),
            ).fetchone()
        if row is None:
            raise KeyError(request_id)
        return TaskRequest(
            request_id=row[0],
            source_channel=SourceChannel(row[1]),
            sender=row[2],
            raw_message=row[3],
            task_intent=row[4],
            priority=row[5],
            attachments=json.loads(row[6]),
            authorization_context=json.loads(row[7]),
        )

    def save_job(self, job: Job) -> None:
        with sqlite3.connect(self.path) as conn:
            conn.execute(
                """
                INSERT INTO jobs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    job.job_id,
                    job.request_id,
                    job.role_group,
                    job.actor,
                    job.critic,
                    job.status.value,
                    json.dumps(job.input),
                    job.workspace,
                    json.dumps(job.artifact_paths),
                    job.retry_count,
                    job.timeout_seconds,
                    job.failure_reason,
                ),
            )

    def update_job_status(self, job_id: str, status: JobStatus) -> None:
        with sqlite3.connect(self.path) as conn:
            conn.execute("UPDATE jobs SET status = ? WHERE job_id = ?", (status.value, job_id))

    def get_job(self, job_id: str) -> Job:
        with sqlite3.connect(self.path) as conn:
            row = conn.execute("SELECT * FROM jobs WHERE job_id = ?", (job_id,)).fetchone()
        if row is None:
            raise KeyError(job_id)
        return Job(
            job_id=row[0],
            request_id=row[1],
            role_group=row[2],
            actor=row[3],
            critic=row[4],
            status=JobStatus(row[5]),
            input=json.loads(row[6]),
            workspace=row[7],
            artifact_paths=json.loads(row[8]),
            retry_count=row[9],
            timeout_seconds=row[10],
            failure_reason=row[11],
        )

    def save_review(self, review: CriticReview) -> None:
        with sqlite3.connect(self.path) as conn:
            conn.execute(
                """
                INSERT INTO critic_reviews VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    review.review_id,
                    review.job_id,
                    review.review_result,
                    review.score,
                    json.dumps(review.issues),
                    int(review.approved),
                    int(review.return_to_actor),
                    review.handoff_note,
                ),
            )

    def get_review(self, review_id: str) -> CriticReview:
        with sqlite3.connect(self.path) as conn:
            row = conn.execute(
                "SELECT * FROM critic_reviews WHERE review_id = ?",
                (review_id,),
            ).fetchone()
        if row is None:
            raise KeyError(review_id)
        return CriticReview(
            review_id=row[0],
            job_id=row[1],
            review_result=row[2],
            score=row[3],
            issues=json.loads(row[4]),
            approved=bool(row[5]),
            return_to_actor=bool(row[6]),
            handoff_note=row[7],
        )
```

- [ ] **Step 5: Run the store test and confirm it passes**

Run:

```powershell
python -m pytest tests/unit/test_sqlite_store.py -q
```

Expected: `1 passed`.

- [ ] **Step 6: Commit the SQLite foundation**

```powershell
git add src/lanes_ceo/storage tests/unit/test_sqlite_store.py
git commit -m "feat: persist foundation records"
```

## Task 4: Add Workflow Protocols and a Fake Review Gate

**Files:**
- Create: `src/lanes_ceo/workflows/base.py`
- Create: `src/lanes_ceo/workflows/fake.py`
- Create: `src/lanes_ceo/workflows/registry.py`
- Create: `tests/unit/test_fake_workflow.py`

- [ ] **Step 1: Write fake workflow tests**

```python
# tests/unit/test_fake_workflow.py
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
```

- [ ] **Step 2: Run the workflow test and confirm it fails**

Run:

```powershell
python -m pytest tests/unit/test_fake_workflow.py -q
```

Expected: fail because workflow code does not exist.

- [ ] **Step 3: Add workflow protocols**

```python
# src/lanes_ceo/workflows/base.py
from typing import Protocol

from lanes_ceo.contracts import Artifact, CriticReview, Job


class Workflow(Protocol):
    role_group: str
    actor_name: str
    critic_name: str

    def run_actor(self, job: Job) -> Artifact: ...

    def run_critic(self, job: Job, artifact: Artifact) -> CriticReview: ...
```

- [ ] **Step 4: Add the fake workflow and registry**

```python
# src/lanes_ceo/workflows/fake.py
from lanes_ceo.contracts import Artifact, CriticReview, Job


class FakeWorkflow:
    role_group = "fake"
    actor_name = "fake-actor"
    critic_name = "fake-critic"

    def run_actor(self, job: Job) -> Artifact:
        message = str(job.input["message"])
        return Artifact(
            artifact_id=f"artifact-{job.job_id}",
            job_id=job.job_id,
            artifact_type="summary",
            summary=f"fake actor processed {message}",
            artifact_paths=[],
            sources=["fake"],
            risks=[],
            user_confirmations=[],
        )

    def run_critic(self, job: Job, artifact: Artifact) -> CriticReview:
        return CriticReview(
            review_id=f"review-{job.job_id}",
            job_id=job.job_id,
            review_result="approved",
            score=95,
            issues=[],
            approved=True,
            return_to_actor=False,
            handoff_note=f"approved {artifact.artifact_id}",
        )
```

```python
# src/lanes_ceo/workflows/registry.py
from lanes_ceo.workflows.base import Workflow
from lanes_ceo.workflows.fake import FakeWorkflow


class WorkflowRegistry:
    def __init__(self) -> None:
        fake = FakeWorkflow()
        self._workflows: dict[str, Workflow] = {fake.role_group: fake}

    def get(self, role_group: str) -> Workflow:
        try:
            return self._workflows[role_group]
        except KeyError as exc:
            raise KeyError(f"unknown role group: {role_group}") from exc
```

- [ ] **Step 5: Run the workflow test and confirm it passes**

Run:

```powershell
python -m pytest tests/unit/test_fake_workflow.py -q
```

Expected: `1 passed`.

- [ ] **Step 6: Commit the workflow gate pieces**

```powershell
git add src/lanes_ceo/workflows tests/unit/test_fake_workflow.py
git commit -m "feat: add workflow registry and fake workflow"
```

## Task 5: Enforce the Orchestrator Approval Gate

**Files:**
- Modify: `src/lanes_ceo/storage/schema.py`
- Modify: `src/lanes_ceo/storage/sqlite_store.py`
- Create: `src/lanes_ceo/notifications/outbox.py`
- Create: `src/lanes_ceo/orchestrator.py`
- Create: `tests/integration/test_orchestrator_gate.py`

- [ ] **Step 1: Write the gate integration tests**

```python
# tests/integration/test_orchestrator_gate.py
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
```

- [ ] **Step 2: Run the gate tests and confirm they fail**

Run:

```powershell
python -m pytest tests/integration/test_orchestrator_gate.py -q
```

Expected: fail because notification persistence and orchestrator do not exist.

- [ ] **Step 3: Extend the SQLite schema for notifications**

Append to `FOUNDATION_SCHEMA`:

```python
CREATE TABLE IF NOT EXISTS notification_events (
    notification_id TEXT PRIMARY KEY,
    job_id TEXT NOT NULL,
    target_channel TEXT NOT NULL,
    target_recipient TEXT NOT NULL,
    message_type TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    receipt_required INTEGER NOT NULL,
    retry_policy TEXT NOT NULL
);
```

- [ ] **Step 4: Extend the store with notification methods**

Add to `SQLiteStore`:

```python
    def save_notification(self, notification) -> None:
        with sqlite3.connect(self.path) as conn:
            conn.execute(
                """
                INSERT INTO notification_events VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    notification.notification_id,
                    notification.job_id,
                    notification.target_channel.value,
                    notification.target_recipient,
                    notification.message_type.value,
                    json.dumps(notification.payload),
                    int(notification.receipt_required),
                    notification.retry_policy,
                ),
            )

    def list_notifications(self, job_id: str) -> list:
        from lanes_ceo.contracts import NotificationEvent
        from lanes_ceo.enums import NotificationType

        with sqlite3.connect(self.path) as conn:
            rows = conn.execute(
                "SELECT * FROM notification_events WHERE job_id = ?",
                (job_id,),
            ).fetchall()
        return [
            NotificationEvent(
                notification_id=row[0],
                job_id=row[1],
                target_channel=SourceChannel(row[2]),
                target_recipient=row[3],
                message_type=NotificationType(row[4]),
                payload=json.loads(row[5]),
                receipt_required=bool(row[6]),
                retry_policy=row[7],
            )
            for row in rows
        ]
```

- [ ] **Step 5: Add the notification outbox**

```python
# src/lanes_ceo/notifications/outbox.py
from lanes_ceo.contracts import Job, NotificationEvent
from lanes_ceo.enums import NotificationType, SourceChannel
from lanes_ceo.storage.sqlite_store import SQLiteStore


class NotificationOutbox:
    def __init__(self, store: SQLiteStore) -> None:
        self.store = store

    def record_approved_job(self, job: Job) -> None:
        self.store.save_notification(
            NotificationEvent(
                notification_id=f"notification-{job.job_id}",
                job_id=job.job_id,
                target_channel=SourceChannel.FEISHU,
                target_recipient="lane",
                message_type=NotificationType.JOB_COMPLETED,
                payload={"status": "approved", "job_id": job.job_id},
                receipt_required=False,
                retry_policy="default",
            )
        )
```

- [ ] **Step 6: Add the orchestrator**

```python
# src/lanes_ceo/orchestrator.py
from uuid import uuid4

from lanes_ceo.contracts import Job, TaskRequest
from lanes_ceo.enums import JobStatus
from lanes_ceo.notifications.outbox import NotificationOutbox
from lanes_ceo.storage.sqlite_store import SQLiteStore
from lanes_ceo.workflows.registry import WorkflowRegistry


class Orchestrator:
    def __init__(
        self,
        store: SQLiteStore,
        registry: WorkflowRegistry,
        outbox: NotificationOutbox,
    ) -> None:
        self.store = store
        self.registry = registry
        self.outbox = outbox

    def handle(self, request: TaskRequest, role_group: str) -> Job:
        workflow = self.registry.get(role_group)
        self.store.save_request(request)
        job = Job(
            job_id=f"job-{uuid4().hex}",
            request_id=request.request_id,
            role_group=role_group,
            actor=workflow.actor_name,
            critic=workflow.critic_name,
            status=JobStatus.RECEIVED,
            input={"message": request.raw_message},
            workspace=f"runtime/jobs/{request.request_id}",
        )
        self.store.save_job(job)
        self.store.update_job_status(job.job_id, JobStatus.RUNNING_ACTOR)
        artifact = workflow.run_actor(job)
        self.store.update_job_status(job.job_id, JobStatus.WAITING_REVIEW)
        review = workflow.run_critic(job, artifact)
        self.store.save_review(review)
        if not review.approved:
            self.store.update_job_status(job.job_id, JobStatus.RETURNED_TO_ACTOR)
            return self.store.get_job(job.job_id)
        self.store.update_job_status(job.job_id, JobStatus.APPROVED)
        approved_job = self.store.get_job(job.job_id)
        self.outbox.record_approved_job(approved_job)
        self.store.update_job_status(job.job_id, JobStatus.NOTIFIED)
        return self.store.get_job(job.job_id)
```

- [ ] **Step 7: Run the gate tests and confirm they pass**

Run:

```powershell
python -m pytest tests/integration/test_orchestrator_gate.py -q
```

Expected: `2 passed`.

- [ ] **Step 8: Commit the approval gate**

```powershell
git add src/lanes_ceo/storage src/lanes_ceo/notifications src/lanes_ceo/orchestrator.py tests/integration/test_orchestrator_gate.py
git commit -m "feat: enforce actor critic approval gate"
```

## Task 6: Add a Local CLI Ingress Path

**Files:**
- Create: `src/lanes_ceo/ingress/cli.py`
- Create: `tests/integration/test_cli_ingress.py`

- [ ] **Step 1: Write the CLI integration test**

```python
# tests/integration/test_cli_ingress.py
from lanes_ceo.ingress.cli import run_local_request


def test_local_cli_request_completes_fake_workflow(tmp_path) -> None:
    job = run_local_request(
        message="hello from cli",
        role_group="fake",
        db_path=tmp_path / "lanes.sqlite3",
    )

    assert job.role_group == "fake"
    assert job.status.value == "notified"
```

- [ ] **Step 2: Run the CLI test and confirm it fails**

Run:

```powershell
python -m pytest tests/integration/test_cli_ingress.py -q
```

Expected: fail because CLI ingress does not exist.

- [ ] **Step 3: Implement the CLI ingress**

```python
# src/lanes_ceo/ingress/cli.py
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
```

- [ ] **Step 4: Run the CLI test and confirm it passes**

Run:

```powershell
python -m pytest tests/integration/test_cli_ingress.py -q
```

Expected: `1 passed`.

- [ ] **Step 5: Run the full foundation suite**

Run:

```powershell
python -m pytest -q
```

Expected: all foundation tests pass.

- [ ] **Step 6: Run a local manual CLI smoke check**

Run:

```powershell
python -m lanes_ceo.ingress.cli "foundation smoke"
```

Expected: output includes a generated job ID and `notified`.

- [ ] **Step 7: Commit the local ingress path**

```powershell
git add src/lanes_ceo/ingress/cli.py tests/integration/test_cli_ingress.py
git commit -m "feat: add local ingress smoke path"
```

## Foundation Exit Criteria

This plan is complete when:

1. `python -m pytest -q` passes for the foundation suite.
2. `python -m lanes_ceo.ingress.cli "foundation smoke"` prints a generated job ID and `notified`.
3. The SQLite store contains a persisted task request, job, critic review and notification for the smoke request.
4. A rejecting critic path leaves the job in `returned_to_actor` and does not create a formal completion notification.

The next implementation plan should start from the tested `TaskRequest` and `Orchestrator` interfaces and add Hermes Feishu, Weixin and QQ ingress adapters plus scheduled task idempotency.
