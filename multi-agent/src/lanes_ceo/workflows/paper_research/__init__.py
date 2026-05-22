from lanes_ceo.contracts import Artifact, CriticReview, Job


class PaperResearchWorkflow:
    role_group = "paper_research"
    actor_name = "paper-research-actor"
    critic_name = "paper-research-critic"

    def run_actor(self, job: Job) -> Artifact:
        topic = job.input.get("message", "research topic")
        return Artifact(
            artifact_id=f"artifact-{job.job_id}",
            job_id=job.job_id,
            artifact_type="paper_research",
            summary=f"literature research for: {topic}",
            artifact_paths=[
                "papers/downloaded/",
                "papers/notes/",
            ],
            sources=["arxiv", "scholar", "semantic-scholar"],
            risks=[
                "download failures on paywalled papers",
                "citation format inconsistency",
            ],
            user_confirmations=[
                "请确认检索关键词是否准确",
                "下载的论文是否需要补充",
            ],
        )

    def run_critic(self, job: Job, artifact: Artifact) -> CriticReview:
        has_sources = len(artifact.sources) >= 2
        has_paths = len(artifact.artifact_paths) >= 2
        issues = []
        if not has_sources:
            issues.append("insufficient source coverage")
        if not has_paths:
            issues.append("missing download or notes directory")
        return CriticReview(
            review_id=f"review-{job.job_id}",
            job_id=job.job_id,
            review_result="approved" if not issues else "rejected",
            score=90 if not issues else 55,
            issues=issues,
            approved=not issues,
            return_to_actor=bool(issues),
            handoff_note="research complete" if not issues else "expand sources and outputs",
        )
