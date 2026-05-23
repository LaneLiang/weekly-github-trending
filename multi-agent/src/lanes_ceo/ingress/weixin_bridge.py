"""Weixin integration bridge — wires the HTTP server, adapter, orchestrator, and sender together.

Follows the same pattern as FeishuBridge.
"""

from __future__ import annotations

import logging
import threading

from lanes_ceo.contracts import TaskRequest
from lanes_ceo.ingress.weixin_server import WeixinServer
from lanes_ceo.ingress.hermes import HermesWeixinAdapter
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
from lanes_ceo.ingress.weixin_sender import WeixinSender, WeixinConfig

logger = logging.getLogger("lanes_ceo.weixin")


class WeixinBridge:
    """Connects WeChat webhook → orchestrator → WeChat response sending.

    Usage in daemon.py:
        bridge = WeixinBridge(orchestrator, weixin_config, host="0.0.0.0", port=8081)
        bridge.start()
        bridge.stop()
    """

    def __init__(
        self,
        orchestrator,
        weixin_config: WeixinConfig,
        host: str = "127.0.0.1",
        port: int = 8081,
    ) -> None:
        self._orchestrator = orchestrator
        self._adapter = HermesWeixinAdapter()
        self._sender = WeixinSender(weixin_config)
        self._server = WeixinServer(host=host, port=port, token=weixin_config.token)
        self._server.set_callback(self._handle_event)

    def start(self) -> None:
        self._server.start()
        logger.info("Weixin bridge started (webhook on :%d)", self._server.port)

    def stop(self) -> None:
        self._server.stop()
        logger.info("Weixin bridge stopped")

    def send_response(self, openid: str, text: str) -> bool:
        """Send a text response back to a WeChat user."""
        return self._sender.send_text(openid, text)

    # ── internal ──

    def _handle_event(self, event: dict) -> dict | None:
        """Called by WeixinServer for each incoming WeChat event."""
        msg_type = event.get("MsgType", "")
        if msg_type != "text":
            logger.debug("Ignoring non-text Weixin event: %s", msg_type)
            return None

        text = event.get("Content", "").strip()
        openid = event.get("FromUserName", "")
        message_id = event.get("MsgId", "")

        if not text:
            self.send_response(openid, "收到空消息，请输入具体指令。")
            return None

        logger.info("Weixin message from openid=%s: %s", openid, text[:100])

        raw_event = {
            "event_id": message_id,
            "message_id": message_id,
            "sender_id": openid,
            "text": text,
            "intent": infer_intent(text),
            "chat_id": openid,
            "attachments": [],
        }
        try:
            task_request = self._adapter.receive(raw_event)
        except Exception as exc:
            logger.error("Adapter parse failed: %s", exc)
            self.send_response(openid, "消息解析失败，请稍后重试。")
            return None

        role_group = infer_role_group(text)
        if role_group is None:
            handle_unknown_intent(openid, text, self.send_response)
            return None

        if role_group == "claude_task" and is_history_query(text):
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
        chunks = split_long_message(text, max_len=500)  # WeChat limit is lower
        for i, chunk in enumerate(chunks):
            prefix = f"({i+1}/{len(chunks)})\n" if len(chunks) > 1 else ""
            self.send_response(openid, f"{prefix}{chunk}")


