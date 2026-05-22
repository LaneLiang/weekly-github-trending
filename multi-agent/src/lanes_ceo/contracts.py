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
