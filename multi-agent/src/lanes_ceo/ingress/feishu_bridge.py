"""Feishu integration bridge — wires the HTTP server, adapter, orchestrator, and sender together.

This is the "main entry point" for the Feishu communication channel.
"""

from __future__ import annotations

import logging
from threading import Thread
from typing import Callable

from lanes_ceo.ingress.feishu_server import FeishuServer
from lanes_ceo.ingress.hermes import HermesFeishuAdapter
from lanes_ceo.notifications.feishu_sender import FeishuSender, FeishuConfig

logger = logging.getLogger("lanes_ceo.feishu")


class FeishuBridge:
    """Connects Feishu webhook → orchestrator → Feishu response sending.

    Usage in daemon.py:
        bridge = FeishuBridge(config, orchestrator, feishu_config)
        bridge.start()
        # ... scheduler runs ...
        bridge.stop()
    """

    def __init__(
        self,
        orchestrator,
        feishu_config: FeishuConfig,
        host: str = "127.0.0.1",
        port: int = 8080,
    ) -> None:
        self._orchestrator = orchestrator
        self._adapter = HermesFeishuAdapter()
        self._sender = FeishuSender(feishu_config)
        self._server = FeishuServer(host=host, port=port)
        self._server.set_callback(self._handle_event)

    def start(self) -> None:
        self._server.start()
        logger.info("Feishu bridge started (webhook on :%d)", self._server.port)

    def stop(self) -> None:
        self._server.stop()
        logger.info("Feishu bridge stopped")

    def send_response(self, chat_id: str, text: str) -> bool:
        """Send a text response back to a Feishu chat."""
        return self._sender.send_text(chat_id, text)

    def send_card(self, chat_id: str, title: str, content: str) -> bool:
        """Send a rich card to a Feishu chat."""
        return self._sender.send_card(chat_id, title, content)

    # ── internal ──

    def _handle_event(self, event: dict) -> dict | None:
        """Called by FeishuServer for each incoming Feishu event."""
        event_type = event.get("header", {}).get("event_type", "")

        # Only handle message events for now
        if event_type != "im.message.receive_v1":
            logger.debug("Ignoring non-message event: %s", event_type)
            return None

        event_body = event.get("event", {})
        message = event_body.get("message", {})
        chat_id = message.get("chat_id", "")
        message_id = event_body.get("sender", {}).get("id", "")
        message_type = message.get("message_type", "text")

        # Extract text content
        text = ""
        if message_type == "text":
            text = json_parse_text(message.get("content", "{}"))
        elif message_type == "post":
            text = json_parse_post(message.get("content", "{}"))

        if not text.strip():
            self.send_response(chat_id, "收到空消息，请输入具体指令。")
            return None

        logger.info("Feishu message from chat=%s: %s", chat_id, text[:100])

        # Parse into TaskRequest via Hermes adapter
        raw_event = {
            "event_id": event.get("header", {}).get("event_id", ""),
            "message_id": message_id,
            "sender_id": event_body.get("sender", {}).get("sender_id", {}).get("user_id", "unknown"),
            "text": text,
            "intent": _infer_intent(text),
            "chat_id": chat_id,
            "attachments": [],
        }
        task_request = self._adapter.receive(raw_event)

        # Route to orchestrator
        role_group = _infer_role_group(text)
        try:
            job = self._orchestrator.handle(task_request, role_group)
            status = job.status.value
            self.send_response(
                chat_id,
                f"任务已提交 | 角色组: {role_group}\n"
                f"状态: {status}\n"
                f"Job ID: {job.job_id}",
            )
        except Exception as exc:
            logger.error("Orchestrator failed: %s", exc)
            self.send_response(
                chat_id,
                f"处理请求时出错: {str(exc)[:200]}\n请稍后重试。",
            )

        return None


def _infer_intent(text: str) -> str:
    """Naive intent classifier based on keywords."""
    kw_map = {
        "周报": "weekly_report",
        "日报": "daily_report",
        "总结": "daily_report",
        "PPT": "presentation",
        "汇报": "presentation",
        "论文": "paper_writing",
        "文献": "paper_research",
        "邮件": "mail_digest",
        "反思": "reflection",
        "GitHub": "github_trending",
        "AI新闻": "ai_news",
        "新闻": "ai_news",
    }
    for kw, intent in kw_map.items():
        if kw in text:
            return intent
    return "daily_report"


def _infer_role_group(text: str) -> str:
    """Map natural language trigger words to role_group."""
    kw_map = {
        "周报": "weekly_report",
        "周总结": "weekly_report",
        "PPT": "presentation",
        "汇报": "presentation",
        "日报": "daily_report",
        "总结": "daily_report",
        "反思": "reflection",
        "论文": "paper_writing",
        "写论文": "paper_writing",
        "文献": "paper_research",
        "调研": "paper_research",
        "邮件": "mail_digest",
        "收件箱": "mail_digest",
        "GitHub": "github_trending",
        "hot": "github_trending",
        "新闻": "ai_news",
        "AI新闻": "ai_news",
    }
    for kw, role in kw_map.items():
        if kw in text:
            return role
    return "daily_report"


def json_parse_text(content_str: str) -> str:
    import json
    try:
        return json.loads(content_str).get("text", "")
    except Exception:
        return content_str


def json_parse_post(content_str: str) -> str:
    import json
    try:
        data = json.loads(content_str)
        parts = []
        for block in data.get("content", []):
            for elem in block:
                if isinstance(elem, dict) and "text" in elem:
                    parts.append(elem["text"])
        return " ".join(parts)
    except Exception:
        return ""
