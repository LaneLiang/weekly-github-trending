from lanes_ceo.contracts import Artifact, CriticReview, Job


class GitHubTrendingWorkflow:
    role_group = "github_trending"
    actor_name = "github-actor"
    critic_name = "github-critic"

    def run_actor(self, job: Job) -> Artifact:
        return Artifact(
            artifact_id=f"artifact-{job.job_id}",
            job_id=job.job_id,
            artifact_type="github_trending",
            summary=f"github trending report for {job.input.get('message', 'weekly')}",
            artifact_paths=[],
            sources=["github-trending-api"],
            risks=["api rate limit"],
            user_confirmations=[],
        )

    def run_critic(self, job: Job, artifact: Artifact) -> CriticReview:
        has_sources = len(artifact.sources) > 0
        return CriticReview(
            review_id=f"review-{job.job_id}",
            job_id=job.job_id,
            review_result="approved" if has_sources else "rejected",
            score=90 if has_sources else 50,
            issues=[] if has_sources else ["no sources cited"],
            approved=has_sources,
            return_to_actor=not has_sources,
            handoff_note="ready" if has_sources else "add source references",
        )


class AINewsWorkflow:
    role_group = "ai_news"
    actor_name = "ai-news-actor"
    critic_name = "ai-news-critic"

    def run_actor(self, job: Job) -> Artifact:
        return Artifact(
            artifact_id=f"artifact-{job.job_id}",
            job_id=job.job_id,
            artifact_type="ai_news",
            summary=f"AI news briefing for {job.input.get('message', 'weekly')}",
            artifact_paths=[],
            sources=["arxiv", "huggingface", "twitter-ai"],
            risks=["source freshness"],
            user_confirmations=[],
        )

    def run_critic(self, job: Job, artifact: Artifact) -> CriticReview:
        has_sources = len(artifact.sources) > 0
        return CriticReview(
            review_id=f"review-{job.job_id}",
            job_id=job.job_id,
            review_result="approved" if has_sources else "rejected",
            score=88 if has_sources else 45,
            issues=[] if has_sources else ["no sources cited"],
            approved=has_sources,
            return_to_actor=not has_sources,
            handoff_note="ready" if has_sources else "add sources",
        )
