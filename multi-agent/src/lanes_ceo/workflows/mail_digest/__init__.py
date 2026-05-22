from lanes_ceo.contracts import Artifact, CriticReview, Job

# Paper-related email keywords that should be preserved as unread
PAPER_KEYWORDS = [
    "accept",
    "reject",
    "decision",
    "review",
    "revision",
    "minor revision",
    "major revision",
    "manuscript",
    "submission",
    "editor",
]


class MailDigestWorkflow:
    role_group = "mail_digest"
    actor_name = "mail-digest-actor"
    critic_name = "mail-digest-critic"

    def run_actor(self, job: Job) -> Artifact:
        return Artifact(
            artifact_id=f"artifact-{job.job_id}",
            job_id=job.job_id,
            artifact_type="mail_digest",
            summary=f"email digest for {job.input.get('message', 'today')}",
            artifact_paths=[],
            sources=["mail-inbox"],
            risks=[
                "sensitive email content exposure",
                "paper decision emails require unread preservation",
            ],
            user_confirmations=[
                "论文相关邮件是否已正确标记为未读",
                "是否有需要额外关注的紧急邮件",
            ],
        )

    def run_critic(self, job: Job, artifact: Artifact) -> CriticReview:
        issues = []
        if "mail-inbox" not in artifact.sources:
            issues.append("email source not verified")
        if not artifact.user_confirmations:
            issues.append("no paper email confirmation check")
        return CriticReview(
            review_id=f"review-{job.job_id}",
            job_id=job.job_id,
            review_result="approved" if not issues else "rejected",
            score=80 if not issues else 55,
            issues=issues,
            approved=not issues,
            return_to_actor=bool(issues),
            handoff_note="digest ready" if not issues else "re-run with proper checks",
        )

    @staticmethod
    def should_keep_unread(subject: str) -> bool:
        return any(kw.lower() in subject.lower() for kw in PAPER_KEYWORDS)
