import threading
import time
from datetime import datetime, timezone
from uuid import uuid4

from croniter import croniter

from lanes_ceo.contracts import TaskRequest
from lanes_ceo.enums import SourceChannel
from lanes_ceo.orchestrator import Orchestrator


class Scheduler:
    def __init__(
        self,
        orchestrator: Orchestrator,
        timezone_str: str = "Asia/Shanghai",
    ) -> None:
        self._orchestrator = orchestrator
        self._jobs: dict[str, dict] = {}
        self._lock = threading.Lock()
        self._running = False
        self._thread: threading.Thread | None = None
        self._tz = timezone_str

    def add_cron_job(
        self, job_id: str, cron_expr: str, role_group: str, message: str
    ) -> None:
        with self._lock:
            self._jobs[job_id] = {
                "cron": croniter(cron_expr, datetime.now()),
                "role_group": role_group,
                "message": message,
                "last_fire": None,
            }

    def remove_job(self, job_id: str) -> None:
        with self._lock:
            self._jobs.pop(job_id, None)

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)

    def _loop(self) -> None:
        while self._running:
            now = datetime.now()
            with self._lock:
                for job_id, cfg in list(self._jobs.items()):
                    next_fire = cfg["cron"].get_next(datetime)
                    if next_fire <= now:
                        self._fire(job_id, cfg)
            time.sleep(30)

    def _fire(self, job_id: str, cfg: dict) -> None:
        idempotency_key = f"{job_id}-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M')}"
        request = TaskRequest(
            request_id=f"sched-{uuid4().hex[:12]}",
            source_channel=SourceChannel.SCHEDULER,
            sender="scheduler",
            raw_message=cfg["message"],
            task_intent=cfg["role_group"],
            priority="normal",
            authorization_context={"scheduled_job_id": job_id},
            idempotency_key=idempotency_key,
        )
        self._orchestrator.handle(request, cfg["role_group"])
        cfg["last_fire"] = datetime.now(timezone.utc).isoformat()
