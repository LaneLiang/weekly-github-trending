"""QQ Bot integration bridge — wires the HTTP server, adapter, orchestrator, and sender together.

Follows the same pattern as FeishuBridge.
"""

from __future__ import annotations

import logging
import threading

from lanes_ceo.contracts import TaskRequest
from lanes_ceo.ingress.qqbot_server import QQBotServer
from lanes_ceo.ingress.hermes import HermesQQBotAdapter
from lanes_ceo.ingress.shared import (
    build_response,
    check_permission,
    handle_task_history,
    handle_unknown_intent,
    infer_intent,
    infer_role_group,
    is_history_query,
    split_long_message,
)
from lanes_ceo.ingress.qqbot_sender import QQBotSender, QQBotConfig

logger = logging.getLogger("lanes_ceo.qqbot")


QQ_MESSAGE_EVENT_TYPES = frozenset({
    "C2C_MESSAGE_CREATE",
    "GROUP_AT_MESSAGE_CREATE",
    "GUILD_MESSAGE_CREATE",
    "DIRECT_MESSAGE_CREATE",
    "MESSAGE_CREATE",
    "AT_MESSAGE_CREATE",
})


class QQBotBridge:
    """Connects QQ Bot webhook → orchestrator → QQ response sending.

    Usage in daemon.py:
        bridge = QQBotBridge(orchestrator, qqbot_config, host="0.0.0.0", port=8082)
        bridge.start()
        bridge.stop()
    """

    def __init__(
        self,
        orchestrator,
        qqbot_config: QQBotConfig,
        host: str = "127.0.0.1",
        port: int = 8082,
    ) -> None:
        self._orchestrator = orchestrator
        self._adapter = HermesQQBotAdapter()
        self._sender = QQBotSender(qqbot_config)
        self._server = QQBotServer(host=host, port=port, app_secret=qqbot_config.app_secret)
        self._server.set_callback(self._handle_event)

    def start(self) -> None:
        self._server.start()
        logger.info("QQ Bot bridge started (webhook on :%d)", self._server.port)

    def stop(self) -> None:
        self._server.stop()
        logger.info("QQ Bot bridge stopped")

    def send_response(self, openid: str, text: str) -> bool:
        """Send a text response back to a QQ user."""
        return self._sender.send_text(openid, text)

    # ── internal ──

    def _handle_event(self, event: dict) -> dict | None:
        """Called by QQBotServer for each incoming QQ Bot event."""
        opcode = event.get("op", -1)
        event_type = event.get("t", "")

        # Only handle message events (opcode 0, type MESSAGE_CREATE or similar)
        if opcode != 0:
            logger.debug("Ignoring non-dispatch QQ event: op=%s", opcode)
            return None

        if event_type not in QQ_MESSAGE_EVENT_TYPES:
            logger.debug("Ignoring non-message QQ event: type=%s", event_type)
            return None

        data = event.get("d", {})
        author = data.get("author", {})
        openid = author.get("id", "")
        message_id = data.get("id", "")
        content = data.get("content", "")

        if not content or not content.strip():
            self.send_response(openid, "收到空消息，请输入具体指令。")
            return None

        logger.info("QQ Bot message from openid=%s: %s", openid, content[:100])

        raw_event = {
            "event_id": message_id,
            "message_id": message_id,
            "sender_id": openid,
            "text": content.strip(),
            "intent": infer_intent(content.strip()),
            "chat_id": openid,
            "attachments": [],
        }
        try:
            task_request = self._adapter.receive(raw_event)
        except Exception as exc:
            logger.error("Adapter parse failed: %s", exc)
            self.send_response(openid, "消息解析失败，请稍后重试。")
            return None

        role_group = infer_role_group(content.strip())
        if role_group is None:
            handle_unknown_intent(openid, content.strip(), self.send_response)
            return None

        if role_group == "claude_task" and is_history_query(content.strip()):
            handle_task_history(openid, self.send_response)
            return None

        if role_group == "claude_task" and not check_permission(openid):
            logger.warning("Permission denied for sender=%s", openid)
            self.send_response(openid, "你没有权限执行此操作。")
            return None

        if role_group == "claude_task":
            self.send_response(openid, "任务已提交，正在执行中…\n预计需要1-3分钟，完成后会自动推送结果。")
            t = threading.Thread(
                target=self._run_and_respond,
                args=(openid, task_request, role_group),
                daemon=True,
            )
            t.start()
            return None

        self._run_and_respond(openid, task_request, role_group)
        return None

    def _run_and_respond(self, openid: str, task_request: TaskRequest, role_group: str) -> None:
        try:
            job, artifact = self._orchestrator.handle(task_request, role_group)
            response_text = build_response(role_group, job, artifact)
            self._send_long_message(openid, response_text)
        except Exception as exc:
            logger.error("Orchestrator failed: %s", exc)
            self.send_response(
                openid,
                f"处理请求时出错: {str(exc)[:200]}\n请稍后重试。",
            )

    def _send_long_message(self, openid: str, text: str) -> None:
        chunks = split_long_message(text, max_len=2000)
        for i, chunk in enumerate(chunks):
            prefix = f"({i+1}/{len(chunks)})\n" if len(chunks) > 1 else ""
            self.send_response(openid, f"{prefix}{chunk}")


