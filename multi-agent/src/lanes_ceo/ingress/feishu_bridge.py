"""Feishu integration bridge — wires the HTTP server, adapter, orchestrator, and sender together.

This is the "main entry point" for the Feishu communication channel.
"""

from __future__ import annotations

import logging
import threading

from lanes_ceo.contracts import TaskRequest
from lanes_ceo.ingress.feishu_server import FeishuServer
from lanes_ceo.ingress.hermes import HermesFeishuAdapter
from lanes_ceo.ingress.shared import (
    HELP_FOOTER,
    HELP_TEXT,
    build_response,
    check_permission,
    general_chat,
    handle_task_history,
    handle_unknown_intent,
    infer_intent,
    infer_role_group,
    is_history_query,
    json_parse_post,
    json_parse_text,
    split_long_message,
    truncate,
)
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
        sender_id = event_body.get("sender", {}).get("sender_id", {}).get("user_id", "unknown")

        # Extract text content
        text = ""
        if message_type == "text":
            text = json_parse_text(message.get("content", "{}"))
        elif message_type == "post":
            text = json_parse_post(message.get("content", "{}"))

        if not text.strip():
            self.send_response(chat_id, "收到空消息，请输入具体指令。")
            return None

        logger.info("Feishu message from chat=%s sender=%s: %s", chat_id, sender_id, text[:100])

        # Parse into TaskRequest via Hermes adapter
        raw_event = {
            "event_id": event.get("header", {}).get("event_id", ""),
            "message_id": message_id,
            "sender_id": sender_id,
            "text": text,
            "intent": infer_intent(text),
            "chat_id": chat_id,
            "attachments": [],
        }
        try:
            task_request = self._adapter.receive(raw_event)
        except Exception as exc:
            logger.error("Adapter parse failed: %s", exc)
            self.send_response(chat_id, "消息解析失败，请稍后重试。")
            return None

        # Route to orchestrator, or handle unknown intent
        role_group = infer_role_group(text)
        if role_group is None:
            handle_unknown_intent(chat_id, text, self.send_response)
            return None

        # Task history — handled directly, no orchestrator needed
        if role_group == "claude_task" and is_history_query(text):
            handle_task_history(chat_id, self.send_response)
            return None

        # Permission check for claude_task
        if role_group == "claude_task" and not check_permission(sender_id):
            logger.warning("Permission denied for sender=%s", sender_id)
            self.send_response(chat_id, "你没有权限执行此操作。")
            return None

        # Async execution for claude_task: ack now, send result later
        if role_group == "claude_task":
            self.send_response(chat_id, "任务已提交，正在执行中…\n预计需要1-3分钟，完成后会自动推送结果。")
            t = threading.Thread(
                target=self._run_and_respond,
                args=(chat_id, task_request, role_group),
                daemon=True,
            )
            t.start()
            return None

        # Sync execution for all other roles
        self._run_and_respond(chat_id, task_request, role_group)
        return None

    def _run_and_respond(self, chat_id: str, task_request: TaskRequest, role_group: str) -> None:
        """Run orchestrator and send result, with long output splitting."""
        try:
            job, artifact = self._orchestrator.handle(task_request, role_group)
            response_text = build_response(role_group, job, artifact)
            self._send_long_message(chat_id, response_text)
        except Exception as exc:
            logger.error("Orchestrator failed: %s", exc)
            self.send_response(
                chat_id,
                f"处理请求时出错: {str(exc)[:200]}\n请稍后重试。",
            )

    def _send_long_message(self, chat_id: str, text: str) -> None:
        """Send a message, splitting into chunks if it exceeds Feishu's limit."""
        chunks = split_long_message(text, max_len=3500)
        for i, chunk in enumerate(chunks):
            prefix = f"({i+1}/{len(chunks)})\n" if len(chunks) > 1 else ""
            self.send_response(chat_id, f"{prefix}{chunk}")


