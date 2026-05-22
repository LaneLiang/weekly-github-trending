"""LANEs_CEO daemon entry point — runs scheduler and watches for tasks."""

import logging
import signal
import sys
import time
from pathlib import Path

from lanes_ceo.config import Config
from lanes_ceo.notifications.outbox import NotificationOutbox
from lanes_ceo.orchestrator import Orchestrator
from lanes_ceo.scheduler import Scheduler
from lanes_ceo.storage.sqlite_store import SQLiteStore
from lanes_ceo.workflows.registry import WorkflowRegistry


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
    # V1 default schedules — all times in Asia/Shanghai
    sched.add_cron_job(
        "github-trending-weekly",
        "0 9 * * 1",  # Monday 9am
        "github_trending",
        "本周 GitHub 热门项目调研",
    )
    sched.add_cron_job(
        "ai-news-weekly",
        "0 10 * * 1",  # Monday 10am
        "ai_news",
        "本周 AI 领域重要新闻",
    )
    sched.add_cron_job(
        "daily-report",
        "0 22 * * *",  # Every day 10pm
        "daily_report",
        "今日工作总结",
    )
    sched.add_cron_job(
        "daily-reflection",
        "30 22 * * *",  # Every day 10:30pm
        "reflection",
        "今日反思与改进",
    )
    sched.add_cron_job(
        "weekly-report",
        "0 21 * * 5",  # Friday 9pm (buffer before 24:00 deadline)
        "weekly_report",
        "生成当周科研周报",
    )
    sched.add_cron_job(
        "presentation-prep",
        "0 20 * * 0",  # Sunday 8pm (prepare for next week's meeting)
        "presentation",
        "生成下周组会汇报PPT",
    )
    sched.add_cron_job(
        "literature-weekly-scan",
        "7 8 * * 1",  # Monday 8:07am (offset from github-trending to avoid API burst)
        "paper_research",
        "检索过去一周内arXiv和IEEE Xplore上RL+Power Electronics+LLM的最新论文（关键词：LLM meta-optimizer RL, dynamic reward shaping power converter, CCM DCM unified modeling, domain randomization aging-aware DC-DC）",
    )
    return sched


def run_daemon() -> None:
    config = Config.from_env()
    setup_logging(config)
    logger = logging.getLogger("lanes_ceo")

    logger.info("LANEs_CEO V1 starting with config: db=%s tz=%s",
                config.db_path, config.timezone)

    orchestrator = build_orchestrator(config)
    scheduler = configure_scheduler(orchestrator, config)

    stop_event = False

    def handle_signal(signum, frame):
        nonlocal stop_event
        logger.info("Received signal %s, shutting down...", signum)
        stop_event = True

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    scheduler.start()
    logger.info(
        "Scheduler started with %d jobs, timezone=%s",
        len(scheduler._jobs), config.timezone,
    )

    try:
        while not stop_event:
            time.sleep(1)
    finally:
        scheduler.stop()
        logger.info("LANEs_CEO V1 stopped")


if __name__ == "__main__":
    run_daemon()
