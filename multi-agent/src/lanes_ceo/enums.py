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
