from lanes_ceo.contracts import Artifact, CriticReview, Job


class DailyReportWorkflow:
    role_group = "daily_report"
    actor_name = "daily-report-actor"
    critic_name = "daily-report-critic"

    def run_actor(self, job: Job) -> Artifact:
        return Artifact(
            artifact_id=f"artifact-{job.job_id}",
            job_id=job.job_id,
            artifact_type="daily_report",
            summary=f"daily report: {job.input.get('message', '今日总结')}",
            artifact_paths=[],
            sources=["user-conversation"],
            risks=["incomplete coverage"],
            user_confirmations=["请确认今日工作内容是否完整"],
        )

    def run_critic(self, job: Job, artifact: Artifact) -> CriticReview:
        return CriticReview(
            review_id=f"review-{job.job_id}",
            job_id=job.job_id,
            review_result="approved",
            score=85,
            issues=[],
            approved=True,
            return_to_actor=False,
            handoff_note="daily report ready for review",
        )


class ReflectionWorkflow:
    role_group = "reflection"
    actor_name = "reflection-actor"
    critic_name = "reflection-critic"

    def run_actor(self, job: Job) -> Artifact:
        return Artifact(
            artifact_id=f"artifact-{job.job_id}",
            job_id=job.job_id,
            artifact_type="reflection",
            summary=f"reflection: {job.input.get('message', '今日反思')}",
            artifact_paths=[],
            sources=["user-conversation"],
            risks=["shallow analysis"],
            user_confirmations=["反思内容是否需要调整方向"],
        )

    def run_critic(self, job: Job, artifact: Artifact) -> CriticReview:
        has_confirmations = len(artifact.user_confirmations) > 0
        return CriticReview(
            review_id=f"review-{job.job_id}",
            job_id=job.job_id,
            review_result="approved" if has_confirmations else "rejected",
            score=82 if has_confirmations else 55,
            issues=[] if has_confirmations else ["no user confirmations requested"],
            approved=has_confirmations,
            return_to_actor=not has_confirmations,
            handoff_note="reflection ready",
        )
