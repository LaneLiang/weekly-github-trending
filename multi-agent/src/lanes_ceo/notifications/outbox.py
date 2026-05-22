"""NotificationOutbox — records job outcomes and dispatches to notification channels."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from lanes_ceo.contracts import Job, NotificationEvent
from lanes_ceo.enums import NotificationType, SourceChannel
from lanes_ceo.storage.sqlite_store import SQLiteStore

if TYPE_CHECKING:
    from lanes_ceo.notifications.feishu_sender import FeishuSender

logger = logging.getLogger("lanes_ceo.outbox")


class NotificationOutbox:
    def __init__(self, store: SQLiteStore, feishu_sender: FeishuSender | None = None) -> None:
        self.store = store
        self._feishu_sender = feishu_sender
        self._chat_id_cache: dict[str, str] = {}  # job_id → chat_id

    def record_approved_job(self, job: Job, target_channel: str = "") -> None:
        """Record a completed job and attempt to send notification."""
        channel = target_channel or "cli"

        # Persist to store
        self.store.save_notification(
            NotificationEvent(
                notification_id=f"notification-{job.job_id}",
                job_id=job.job_id,
                target_channel=SourceChannel(channel) if channel in SourceChannel.__members__.values() else SourceChannel.CLI,
                target_recipient=job.input.get("sender", "lane"),
                message_type=NotificationType.JOB_COMPLETED,
                payload={
                    "status": "approved",
                    "job_id": job.job_id,
                    "role_group": job.role_group,
                },
                receipt_required=False,
                retry_policy="default",
            )
        )

        # Attempt real delivery via Feishu
        if channel == "feishu" and self._feishu_sender:
            chat_id = self._chat_id_cache.get(job.job_id, "")
            if chat_id:
                self._feishu_sender.send_text(
                    chat_id,
                    f"任务完成 | {job.role_group}\nJob ID: {job.job_id}",
                )

    def set_chat_id(self, job_id: str, chat_id: str) -> None:
        """Associate a chat_id with a job for response delivery."""
        self._chat_id_cache[job_id] = chat_id

    def set_feishu_sender(self, sender: FeishuSender) -> None:
        """Wire in the Feishu sender after construction."""
        self._feishu_sender = sender
