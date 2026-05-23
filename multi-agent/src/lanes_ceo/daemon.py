"""LANEs_CEO daemon — runs scheduler, ingress bridges, and health server concurrently."""

import json
import logging
import signal
import sys
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from threading import Thread

from lanes_ceo.config import Config
from lanes_ceo.notifications.outbox import NotificationOutbox
from lanes_ceo.notifications.feishu_sender import FeishuConfig
from lanes_ceo.orchestrator import Orchestrator
from lanes_ceo.ingress.feishu_bridge import FeishuBridge
from lanes_ceo.ingress.weixin_bridge import WeixinBridge
from lanes_ceo.ingress.weixin_sender import WeixinConfig
from lanes_ceo.ingress.qqbot_bridge import QQBotBridge
from lanes_ceo.ingress.qqbot_sender import QQBotConfig
from lanes_ceo.scheduler import Scheduler
from lanes_ceo.storage.sqlite_store import SQLiteStore
from lanes_ceo.workflows.registry import WorkflowRegistry

logger = logging.getLogger("lanes_ceo")

# Module-level clock for uptime tracking
_start_time: float | None = None


def _uptime_seconds() -> float:
    """Return seconds since daemon started, or 0 if not started."""
    if _start_time is None:
        return 0.0
    return time.time() - _start_time


def setup_logging(config: Config) -> None:
    config.ensure_dirs()
    logging.basicConfig(
        level=getattr(logging, config.log_level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(config.log_file, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )


def build_orchestrator(config: Config) -> Orchestrator:
    store = SQLiteStore(config.db_path)
    store.initialize()
    registry = WorkflowRegistry()
    outbox = NotificationOutbox(
        store,
        default_chat_id=config.feishu_notification_chat_id,
    )
    return Orchestrator(store, registry, outbox)


def configure_scheduler(orchestrator: Orchestrator, config: Config) -> Scheduler:
    sched = Scheduler(orchestrator, timezone_str=config.timezone)
    sched.add_cron_job(
        "github-trending-weekly",
        "0 9 * * 1",
        "github_trending",
        "本周 GitHub 热门项目调研",
    )
    sched.add_cron_job(
        "ai-news-weekly",
        "0 10 * * 1",
        "ai_news",
        "本周 AI 领域重要新闻",
    )
    sched.add_cron_job(
        "daily-report",
        "0 22 * * *",
        "daily_report",
        "今日工作总结",
    )
    sched.add_cron_job(
        "daily-reflection",
        "30 22 * * *",
        "reflection",
        "今日反思与改进",
    )
    sched.add_cron_job(
        "weekly-report",
        "0 21 * * 5",
        "weekly_report",
        "生成当周科研周报",
    )
    sched.add_cron_job(
        "presentation-prep",
        "0 20 * * 0",
        "presentation",
        "生成下周组会汇报PPT",
    )
    sched.add_cron_job(
        "literature-weekly-scan",
        "7 8 * * 1",
        "paper_research",
        "检索过去一周内arXiv和IEEE Xplore上RL+Power Electronics+LLM的最新论文"
        "（关键词：LLM meta-optimizer RL, dynamic reward shaping power converter,"
        " CCM DCM unified modeling, domain randomization aging-aware DC-DC）",
    )
    sched.add_cron_job(
        "daily-update-check",
        "0 7 * * *",
        "update_checker",
        "扫描检查所有工具、Skills、MCP服务器、CLI是否有可用更新",
    )
    sched.add_cron_job(
        "weekly-memory-curation",
        "7 2 * * 0",
        "memory_curation",
        "扫描 ~/.claude/memory/ 目录，去重、过期标记、生成整理报告",
    )
    sched.add_cron_job(
        "daily-deepseek-balance",
        "0 8 * * *",
        "deepseek_monitor",
        "检查 DeepSeek API 余额，低于阈值时告警",
    )
    return sched


def _build_feishu_bridge(orchestrator: Orchestrator, config: Config) -> FeishuBridge | None:
    """Create FeishuBridge if Feishu is enabled and configured."""
    if not config.feishu_enabled:
        logger.info("Feishu not enabled (LANES_CEO_FEISHU_ENABLED not set)")
        return None

    if not config.feishu_app_id or not config.feishu_app_secret:
        logger.warning(
            "Feishu enabled but app_id/app_secret not configured — "
            "set LANES_CEO_FEISHU_APP_ID and LANES_CEO_FEISHU_APP_SECRET"
        )
        return None

    feishu_host = config.feishu_webhook_host or "127.0.0.1"
    feishu_port = config.feishu_webhook_port or 8080

    feishu_cfg = FeishuConfig(
        app_id=config.feishu_app_id,
        app_secret=config.feishu_app_secret,
    )
    bridge = FeishuBridge(
        orchestrator,
        feishu_cfg,
        host=feishu_host,
        port=feishu_port,
    )
    logger.info("Feishu bridge configured: %s:%d", feishu_host, feishu_port)
    return bridge


def _build_weixin_bridge(orchestrator: Orchestrator, config: Config) -> WeixinBridge | None:
    """Create WeixinBridge if Weixin is enabled and configured."""
    if not config.weixin_enabled:
        logger.info("Weixin not enabled (LANES_CEO_WEIXIN_ENABLED not set)")
        return None

    if not config.weixin_app_id or not config.weixin_app_secret:
        logger.warning(
            "Weixin enabled but app_id/app_secret not configured — "
            "set LANES_CEO_WEIXIN_APP_ID and LANES_CEO_WEIXIN_APP_SECRET"
        )
        return None

    weixin_host = config.weixin_webhook_host or "127.0.0.1"
    weixin_port = config.weixin_webhook_port or 8081

    weixin_cfg = WeixinConfig(
        app_id=config.weixin_app_id,
        app_secret=config.weixin_app_secret,
        token=config.weixin_token,
    )
    bridge = WeixinBridge(
        orchestrator,
        weixin_cfg,
        host=weixin_host,
        port=weixin_port,
    )
    logger.info("Weixin bridge configured: %s:%d", weixin_host, weixin_port)
    return bridge


def _build_qq_bridge(orchestrator: Orchestrator, config: Config) -> QQBotBridge | None:
    """Create QQBotBridge if QQ is enabled and configured."""
    if not config.qq_enabled:
        logger.info("QQ not enabled (LANES_CEO_QQ_ENABLED not set)")
        return None

    if not config.qqbot_app_id or not config.qqbot_app_secret:
        logger.warning(
            "QQ enabled but app_id/app_secret not configured — "
            "set LANES_CEO_QQBOT_APP_ID and LANES_CEO_QQBOT_APP_SECRET"
        )
        return None

    qq_host = config.qqbot_webhook_host or "127.0.0.1"
    qq_port = config.qqbot_webhook_port or 8082

    qq_cfg = QQBotConfig(
        app_id=config.qqbot_app_id,
        app_secret=config.qqbot_app_secret,
    )
    bridge = QQBotBridge(
        orchestrator,
        qq_cfg,
        host=qq_host,
        port=qq_port,
    )
    logger.info("QQ Bot bridge configured: %s:%d", qq_host, qq_port)
    return bridge


# ── health check server ──

class _HealthHandler(BaseHTTPRequestHandler):
    """Lightweight health check endpoint for runtime observation."""

    def do_GET(self) -> None:
        routes = {
            "/health": self._serve_health,
            "/health/jobs": self._serve_health_jobs,
        }
        handler = routes.get(self.path, self._serve_not_found)
        handler()

    def _serve_health(self) -> None:
        daemon = getattr(self.server, "daemon_state", {})
        bridges = {
            "feishu": daemon.get("feishu_running", False),
            "weixin": daemon.get("weixin_running", False),
            "qq": daemon.get("qq_running", False),
        }
        payload = {
            "status": "ok",
            "uptime_seconds": round(_uptime_seconds(), 1),
            "bridges": bridges,
            "scheduler": daemon.get("scheduler_running", False),
            "scheduler_jobs": daemon.get("scheduler_job_count", 0),
        }
        self._send_json(200, payload)

    def _serve_health_jobs(self) -> None:
        daemon = getattr(self.server, "daemon_state", {})
        store = daemon.get("store")
        if store:
            try:
                records = store.list_score_records()
                recent = records[:20]
                total = len(recent)
                passed = sum(1 for r in recent if r.score >= 80)
                payload = {
                    "recent_24h_total": total,
                    "recent_24h_passed": passed,
                    "recent_24h_failed": total - passed,
                }
            except Exception:
                payload = {"error": "unavailable"}
        else:
            payload = {"error": "store not available"}
        self._send_json(200, payload)

    def _serve_not_found(self) -> None:
        self._send_json(404, {"error": "not found"})

    def _send_json(self, status: int, data: dict) -> None:
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        pass  # suppress health check noise


def _build_health_server(config: Config, daemon_state: dict) -> HTTPServer | None:
    """Create health check HTTP server if health_port is configured."""
    if not config.health_port:
        return None

    server = HTTPServer(("127.0.0.1", config.health_port), _HealthHandler)
    server.daemon_state = daemon_state  # type: ignore[attr-defined]
    thread = Thread(target=server.serve_forever, daemon=True, name="health-server")
    thread.start()
    logger.info("Health server started on :%d", config.health_port)
    return server


# ── main daemon loop ──

def run_daemon() -> None:
    global _start_time

    config = Config.from_env()
    setup_logging(config)

    logger.info("LANEs_CEO V1 starting with config: db=%s tz=%s",
                config.db_path, config.timezone)

    orchestrator = build_orchestrator(config)
    scheduler = configure_scheduler(orchestrator, config)
    feishu_bridge = _build_feishu_bridge(orchestrator, config)
    weixin_bridge = _build_weixin_bridge(orchestrator, config)
    qq_bridge = _build_qq_bridge(orchestrator, config)

    stop_event = False

    def handle_signal(signum, frame):
        nonlocal stop_event
        logger.info("Received signal %s, shutting down...", signum)
        stop_event = True

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    scheduler.start()
    _start_time = time.time()
    logger.info(
        "Scheduler started with %d cron jobs, timezone=%s",
        len(scheduler._jobs), config.timezone,
    )

    if feishu_bridge:
        feishu_bridge.start()
        orchestrator.outbox.set_feishu_sender(feishu_bridge._sender)
        logger.info("Feishu bridge started on :%d", feishu_bridge._server.port)

    if weixin_bridge:
        weixin_bridge.start()
        logger.info("Weixin bridge started on :%d", weixin_bridge._server.port)

    if qq_bridge:
        qq_bridge.start()
        logger.info("QQ Bot bridge started on :%d", qq_bridge._server.port)

    bridges_started = sum(1 for b in [feishu_bridge, weixin_bridge, qq_bridge] if b)
    logger.info("Ingress: %d bridge(s) running", bridges_started)

    # Health check server
    daemon_state = {
        "feishu_running": feishu_bridge is not None and feishu_bridge._server.is_running,
        "weixin_running": weixin_bridge is not None and weixin_bridge._server.is_running,
        "qq_running": qq_bridge is not None and qq_bridge._server.is_running,
        "scheduler_running": True,
        "scheduler_job_count": len(scheduler._jobs),
        "store": orchestrator.store,
    }
    health_server = _build_health_server(config, daemon_state)

    _last_heartbeat = time.time()
    _heartbeat_interval = 3600  # heartbeat every hour

    try:
        while not stop_event:
            time.sleep(1)

            # Hourly heartbeat log
            if time.time() - _last_heartbeat >= _heartbeat_interval:
                _last_heartbeat = time.time()
                uptime_h = _uptime_seconds() / 3600
                logger.info(
                    "HEARTBEAT: uptime=%.1fh bridges=%d scheduler_jobs=%d",
                    uptime_h, bridges_started, len(scheduler._jobs),
                )
    finally:
        scheduler.stop()
        if health_server:
            health_server.shutdown()
        if feishu_bridge:
            feishu_bridge.stop()
        if weixin_bridge:
            weixin_bridge.stop()
        if qq_bridge:
            qq_bridge.stop()
        logger.info("LANEs_CEO V1 stopped (uptime %.1fh)", _uptime_seconds() / 3600)


if __name__ == "__main__":
    run_daemon()
