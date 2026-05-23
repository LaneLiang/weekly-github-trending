import json
import sqlite3
from pathlib import Path

from lanes_ceo.contracts import CriticReview, Job, NotificationEvent, ScoreRecord, TaskRequest
from lanes_ceo.enums import JobStatus, NotificationType, SourceChannel
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
                INSERT INTO task_requests VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                    request.idempotency_key,
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
            idempotency_key=row[8] if len(row) > 8 else None,
        )

    def has_idempotency_key(self, key: str) -> bool:
        if key is None:
            return False
        with sqlite3.connect(self.path) as conn:
            row = conn.execute(
                "SELECT 1 FROM task_requests WHERE idempotency_key = ? LIMIT 1",
                (key,),
            ).fetchone()
        return row is not None

    def save_job(self, job: Job) -> None:
        with sqlite3.connect(self.path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO jobs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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

    def save_notification(self, notification: NotificationEvent) -> None:
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

    def list_notifications(self, job_id: str) -> list[NotificationEvent]:
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

    def save_score_record(self, record: ScoreRecord) -> None:
        with sqlite3.connect(self.path) as conn:
            conn.execute(
                """
                INSERT INTO score_records VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.score_id,
                    record.job_id,
                    record.scored_role,
                    record.scorer_role,
                    record.score,
                    record.rating,
                    record.review_summary,
                    record.created_at,
                    record.month_bucket,
                ),
            )

    def list_score_records(self) -> list[ScoreRecord]:
        with sqlite3.connect(self.path) as conn:
            rows = conn.execute("SELECT * FROM score_records").fetchall()
        return [
            ScoreRecord(
                score_id=row[0],
                job_id=row[1],
                scored_role=row[2],
                scorer_role=row[3],
                score=row[4],
                rating=row[5],
                review_summary=row[6],
                created_at=row[7],
                month_bucket=row[8],
            )
            for row in rows
        ]
