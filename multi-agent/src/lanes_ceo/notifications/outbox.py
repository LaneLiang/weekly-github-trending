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
