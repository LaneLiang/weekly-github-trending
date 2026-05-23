import logging
import time
from uuid import uuid4

from lanes_ceo.contracts import Artifact, Job, TaskRequest
from lanes_ceo.enums import JobStatus
from lanes_ceo.notifications.outbox import NotificationOutbox
from lanes_ceo.storage.sqlite_store import SQLiteStore
from lanes_ceo.subagent.manager import SubAgentManager
from lanes_ceo.workflows.registry import WorkflowRegistry

logger = logging.getLogger("lanes_ceo.orchestrator")

MAX_RETRIES = 3
BASE_BACKOFF = 2.0  # seconds, exponential: 2, 4, 8


class DuplicateRequestError(ValueError):
    """Raised when a request with the same idempotency key has already been processed."""


class Orchestrator:
    def __init__(
        self,
        store: SQLiteStore,
        registry: WorkflowRegistry,
        outbox: NotificationOutbox,
    ) -> None:
        self.store = store
        self.registry = registry
        self.outbox = outbox
        self.subagents = SubAgentManager(registry)

    def handle(self, request: TaskRequest, role_group: str) -> tuple[Job, Artifact | None]:
        if request.idempotency_key and self.store.has_idempotency_key(
            request.idempotency_key
        ):
            raise DuplicateRequestError(
                f"Duplicate idempotency key: {request.idempotency_key}"
            )
        workflow = self.registry.get(role_group)
        self.store.save_request(request)
        job = Job(
            job_id=f"job-{uuid4().hex}",
            request_id=request.request_id,
            role_group=role_group,
            actor=workflow.actor_name,
            critic=workflow.critic_name,
            status=JobStatus.RECEIVED,
            input={"message": request.raw_message, "sender": request.sender},
            workspace=f"runtime/jobs/{request.request_id}",
        )
        self.store.save_job(job)

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                return self._execute_job(job, request, role_group)
            except Exception as exc:
                job.retry_count = attempt
                job.failure_reason = str(exc)[:200]
                self.store.save_job(job)

                if attempt < MAX_RETRIES:
                    backoff = BASE_BACKOFF ** attempt
                    logger.warning(
                        "Job %s attempt %d/%d failed: %s — retrying in %.1fs",
                        job.job_id, attempt, MAX_RETRIES, exc, backoff,
                    )
                    time.sleep(backoff)
                else:
                    logger.error(
                        "Job %s failed after %d attempts: %s",
                        job.job_id, MAX_RETRIES, exc,
                    )
                    self.store.update_job_status(job.job_id, JobStatus.FAILED)
                    return self.store.get_job(job.job_id), None

        # Unreachable
        self.store.update_job_status(job.job_id, JobStatus.FAILED)
        return self.store.get_job(job.job_id), None

    def _execute_job(self, job: Job, request: TaskRequest, role_group: str) -> tuple[Job, Artifact | None]:
        """Execute a single attempt of actor → critic → notification."""
        # Spawn actor sub-agent and execute
        self.store.update_job_status(job.job_id, JobStatus.RUNNING_ACTOR)
        actor = self.subagents.spawn(role_group, "actor")
        artifact = actor.run(job, {})

        # Spawn critic sub-agent and execute
        self.store.update_job_status(job.job_id, JobStatus.WAITING_REVIEW)
        critic = self.subagents.spawn(role_group, "critic")
        review = critic.run(job, {"artifact": artifact})

        self.store.save_review(review)
        if not review.approved:
            self.store.update_job_status(job.job_id, JobStatus.RETURNED_TO_ACTOR)
            return self.store.get_job(job.job_id), artifact
        self.store.update_job_status(job.job_id, JobStatus.APPROVED)
        approved_job = self.store.get_job(job.job_id)
        self.outbox.record_approved_job(
            approved_job, target_channel=request.source_channel.value
        )
        self.store.update_job_status(job.job_id, JobStatus.NOTIFIED)
        return self.store.get_job(job.job_id), artifact
