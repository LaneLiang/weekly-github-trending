"""LANEs_CEO daemon — runs scheduler and Feishu webhook server concurrently."""

import logging
import signal
import sys
import time
from pathlib import Path

from lanes_ceo.config import Config
from lanes_ceo.notifications.outbox import NotificationOutbox
from lanes_ceo.notifications.feishu_sender import FeishuConfig
from lanes_ceo.orchestrator import Orchestrator
from lanes_ceo.ingress.feishu_bridge import FeishuBridge
from lanes_ceo.scheduler import Scheduler
from lanes_ceo.storage.sqlite_store import SQLiteStore
from lanes_ceo.workflows.registry import WorkflowRegistry

logger = logging.getLogger("lanes_ceo")


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
    outbox = NotificationOutbox(store)
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


def run_daemon() -> None:
    config = Config.from_env()
    setup_logging(config)

    logger.info("LANEs_CEO V1 starting with config: db=%s tz=%s",
                config.db_path, config.timezone)

    orchestrator = build_orchestrator(config)
    scheduler = configure_scheduler(orchestrator, config)
    feishu_bridge = _build_feishu_bridge(orchestrator, config)

    stop_event = False

    def handle_signal(signum, frame):
        nonlocal stop_event
        logger.info("Received signal %s, shutting down...", signum)
        stop_event = True

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    scheduler.start()
    logger.info(
        "Scheduler started with %d cron jobs, timezone=%s",
        len(scheduler._jobs), config.timezone,
    )

    if feishu_bridge:
        feishu_bridge.start()
        orchestrator.outbox.set_feishu_sender(feishu_bridge._sender)
        logger.info("Feishu bridge started on :%d", feishu_bridge._server.port)

    try:
        while not stop_event:
            time.sleep(1)
    finally:
        scheduler.stop()
        if feishu_bridge:
            feishu_bridge.stop()
        logger.info("LANEs_CEO V1 stopped")


if __name__ == "__main__":
    run_daemon()
