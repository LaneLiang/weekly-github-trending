from lanes_ceo.contracts import Artifact, Job
from lanes_ceo.enums import JobStatus
from lanes_ceo.workflows.briefings import AINewsWorkflow, GitHubTrendingWorkflow


def _make_job(role_group: str) -> Job:
    return Job(
        job_id=f"job-{role_group}",
        request_id="req-1",
        role_group=role_group,
        actor=f"{role_group}-actor",
        critic=f"{role_group}-critic",
        status=JobStatus.RECEIVED,
        input={"message": "weekly"},
        workspace="runtime/jobs/test",
    )


def test_github_trending_actor_produces_artifact() -> None:
    wf = GitHubTrendingWorkflow()
    job = _make_job("github_trending")
    artifact = wf.run_actor(job)
    assert artifact.artifact_type == "github_trending"


def test_github_trending_critic_approves_rich_content() -> None:
    wf = GitHubTrendingWorkflow()
    job = _make_job("github_trending")
    artifact = Artifact(
        artifact_id="art-gh",
        job_id=job.job_id,
        artifact_type="github_trending",
        summary="本周GitHub热门项目：1) transformers升级到v5版本，支持多模态训练，这是深度学习框架的重大更新 2) langchain发布v1.0正式版 3) pytorch-lightning引入新的分布式策略",
        artifact_paths=[],
        sources=["https://github.com/huggingface/transformers", "https://github.com/langchain-ai/langchain"],
        risks=[],
        user_confirmations=[],
    )
    review = wf.run_critic(job, artifact)
    assert review.approved is True
    assert review.score >= 80


def test_github_trending_critic_rejects_short_content() -> None:
    wf = GitHubTrendingWorkflow()
    job = _make_job("github_trending")
    artifact = Artifact(
        artifact_id="art-gh2",
        job_id=job.job_id,
        artifact_type="github_trending",
        summary="short",
        artifact_paths=[],
        sources=[],
        risks=[],
        user_confirmations=[],
    )
    review = wf.run_critic(job, artifact)
    assert review.approved is False


def test_ai_news_actor_produces_artifact() -> None:
    wf = AINewsWorkflow()
    job = _make_job("ai_news")
    artifact = wf.run_actor(job)
    assert artifact.artifact_type == "ai_news"


def test_ai_news_critic_approves_rich_content() -> None:
    wf = AINewsWorkflow()
    job = _make_job("ai_news")
    artifact = Artifact(
        artifact_id="art-ai",
        job_id=job.job_id,
        artifact_type="ai_news",
        summary="本周AI重要新闻：1) OpenAI发布GPT-5预览版，在推理和代码生成上有显著提升 2) Meta开源Llama-4系列模型 3) DeepMind发表AlphaFold-3论文，扩展蛋白质结构预测到更多生物分子 4) Anthropic发布Claude Opus 4.7",
        artifact_paths=[],
        sources=["arxiv", "huggingface", "twitter-ai"],
        risks=[],
        user_confirmations=[],
    )
    review = wf.run_critic(job, artifact)
    assert review.approved is True


def test_ai_news_critic_rejects_short_content() -> None:
    wf = AINewsWorkflow()
    job = _make_job("ai_news")
    artifact = Artifact(
        artifact_id="art-ai2",
        job_id=job.job_id,
        artifact_type="ai_news",
        summary="AI news brief",
        artifact_paths=[],
        sources=[],
        risks=[],
        user_confirmations=[],
    )
    review = wf.run_critic(job, artifact)
    assert review.approved is False
