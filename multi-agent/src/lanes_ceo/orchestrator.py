from uuid import uuid4

from lanes_ceo.contracts import Job, TaskRequest
from lanes_ceo.enums import JobStatus
from lanes_ceo.notifications.outbox import NotificationOutbox
from lanes_ceo.storage.sqlite_store import SQLiteStore
from lanes_ceo.subagent.manager import SubAgentManager
from lanes_ceo.workflows.registry import WorkflowRegistry


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

    def handle(self, request: TaskRequest, role_group: str) -> Job:
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
            input={"message": request.raw_message},
            workspace=f"runtime/jobs/{request.request_id}",
        )
        self.store.save_job(job)

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
            return self.store.get_job(job.job_id)
        self.store.update_job_status(job.job_id, JobStatus.APPROVED)
        approved_job = self.store.get_job(job.job_id)
        self.outbox.record_approved_job(approved_job)
        self.store.update_job_status(job.job_id, JobStatus.NOTIFIED)
        return self.store.get_job(job.job_id)
