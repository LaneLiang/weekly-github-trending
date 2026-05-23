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
    def __init__(
        self,
        store: SQLiteStore,
        feishu_sender: FeishuSender | None = None,
        default_chat_id: str = "",
    ) -> None:
        self.store = store
        self._feishu_sender = feishu_sender
        self._default_chat_id = default_chat_id
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
        if self._feishu_sender:
            # Priority: job-specific chat_id > default_chat_id > none
            chat_id = self._chat_id_cache.get(job.job_id, "") or self._default_chat_id
            if chat_id:
                self._send_job_notification(chat_id, job)

    def set_chat_id(self, job_id: str, chat_id: str) -> None:
        """Associate a chat_id with a job for response delivery."""
        self._chat_id_cache[job_id] = chat_id

    def set_default_chat_id(self, chat_id: str) -> None:
        """Set the fallback chat_id for scheduler-triggered jobs."""
        self._default_chat_id = chat_id

    def set_feishu_sender(self, sender: FeishuSender) -> None:
        """Wire in the Feishu sender after construction."""
        self._feishu_sender = sender

    def _send_job_notification(self, chat_id: str, job: Job) -> None:
        """Send a rich notification about a completed job to a chat."""
        role_labels = {
            "weekly_report": "周报", "presentation": "PPT汇报",
            "daily_report": "日报", "reflection": "反思",
            "paper_research": "文献调研", "paper_writing": "论文草稿",
            "mail_digest": "邮件摘要", "github_trending": "GitHub热点",
            "ai_news": "AI新闻", "update_checker": "工具更新检查",
        }
        label = role_labels.get(job.role_group, job.role_group)
        text = f"【{label}】已完成\nJob ID: {job.job_id}\n状态: 已审核通过"
        self._feishu_sender.send_text(chat_id, text)
