from lanes_ceo.contracts import Artifact, CriticReview, Job


class FakeWorkflow:
    role_group = "fake"
    actor_name = "fake-actor"
    critic_name = "fake-critic"

    def run_actor(self, job: Job) -> Artifact:
        message = str(job.input["message"])
        return Artifact(
            artifact_id=f"artifact-{job.job_id}",
            job_id=job.job_id,
            artifact_type="summary",
            summary=f"fake actor processed {message}",
            artifact_paths=[],
            sources=["fake"],
            risks=[],
            user_confirmations=[],
        )

    def run_critic(self, job: Job, artifact: Artifact) -> CriticReview:
        return CriticReview(
            review_id=f"review-{job.job_id}",
            job_id=job.job_id,
            review_result="approved",
            score=95,
            issues=[],
            approved=True,
            return_to_actor=False,
            handoff_note=f"approved {artifact.artifact_id}",
        )
