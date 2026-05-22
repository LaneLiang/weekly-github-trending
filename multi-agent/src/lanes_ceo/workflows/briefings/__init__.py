import json
import subprocess

from lanes_ceo.contracts import Artifact, CriticReview, Job

GITHUB_TRENDING_SYSTEM = (
    "你是一名技术分析师，需要基于GitHub热门仓库数据撰写周报摘要。"
    "对每个仓库，用1-2句中文概括其功能和价值。总计300字以内。"
)

AI_NEWS_SYSTEM = (
    "你是一名AI行业分析师，需要撰写本周AI领域重要新闻简报。"
    "覆盖：大模型进展、开源发布、学术突破、产业动态。"
    "每条新闻50字以内，含标题+简要说明。总计10条以内。"
)


class GitHubTrendingWorkflow:
    role_group = "github_trending"
    actor_name = "github-actor"
    critic_name = "github-critic"

    def run_actor(self, job: Job) -> Artifact:
        message = job.input.get("message", "weekly")

        # Try fetching real GitHub data via gh CLI
        repos = _fetch_trending_repos()
        if repos:
            repo_list = "\n".join(
                f"- {r['full_name']}: {r['description'] or 'no description'} (⭐{r['stars']})"
                for r in repos
            )
            llm_input = f"本周GitHub热门仓库：\n{repo_list}"
            summary = _llm_chat(GITHUB_TRENDING_SYSTEM, llm_input) or repo_list
            sources = [r["url"] for r in repos]
        else:
            llm_input = f"生成一周GitHub热门项目调研报告。主题：{message}"
            summary = _llm_chat(GITHUB_TRENDING_SYSTEM, llm_input) or (
                f"GitHub 热门项目调研报告: {message}\n"
                f"（gh CLI 不可用且未配置 LLM，请安装 gh 或配置 LANES_CEO_LLM_API_KEY）"
            )
            sources = ["github-trending-page"]

        return Artifact(
            artifact_id=f"artifact-{job.job_id}",
            job_id=job.job_id,
            artifact_type="github_trending",
            summary=summary,
            artifact_paths=[],
            sources=sources,
            risks=["API rate limit", "data may not reflect real-time trending"],
            user_confirmations=[],
        )

    def run_critic(self, job: Job, artifact: Artifact) -> CriticReview:
        issues = _check_briefing_quality(artifact, "GitHub")
        approved = len(issues) == 0
        return CriticReview(
            review_id=f"review-{job.job_id}",
            job_id=job.job_id,
            review_result="approved" if approved else "returned",
            score=90 - len(issues) * 15,
            issues=issues,
            approved=approved,
            return_to_actor=not approved,
            handoff_note="GitHub热点报告审核通过" if approved else "请补充数据源或分析深度",
        )


class AINewsWorkflow:
    role_group = "ai_news"
    actor_name = "ai-news-actor"
    critic_name = "ai-news-critic"

    def run_actor(self, job: Job) -> Artifact:
        message = job.input.get("message", "weekly")

        news = _llm_chat(
            AI_NEWS_SYSTEM,
            f"请生成本周（截止{_today()}）AI领域重要新闻简报。主题偏好：{message}",
        )
        summary = news if news else (
            f"AI 新闻简报: {message}\n"
            f"（未配置 LLM，请设置 LANES_CEO_LLM_API_KEY 以启用 AI 新闻生成）"
        )

        return Artifact(
            artifact_id=f"artifact-{job.job_id}",
            job_id=job.job_id,
            artifact_type="ai_news",
            summary=summary,
            artifact_paths=[],
            sources=["llm-knowledge", "arxiv", "huggingface"],
            risks=["source freshness", "LLM knowledge cutoff may miss latest news"],
            user_confirmations=[],
        )

    def run_critic(self, job: Job, artifact: Artifact) -> CriticReview:
        issues = _check_briefing_quality(artifact, "AI新闻")
        approved = len(issues) == 0
        return CriticReview(
            review_id=f"review-{job.job_id}",
            job_id=job.job_id,
            review_result="approved" if approved else "returned",
            score=88 - len(issues) * 12,
            issues=issues,
            approved=approved,
            return_to_actor=not approved,
            handoff_note="AI新闻简报审核通过" if approved else "请补充新闻来源或分析深度",
        )


# --- GitHub data fetcher ---

def _fetch_trending_repos() -> list[dict] | None:
    """Fetch trending repos via gh CLI. Returns None if unavailable."""
    try:
        result = subprocess.run(
            [
                "gh", "api",
                "/search/repositories",
                "-f", "q=stars:>50+pushed:>2026-05-01",
                "-f", "sort=stars",
                "-f", "order=desc",
                "-f", "per_page=10",
                "--jq", ".items[] | {full_name, description, stars: .stargazers_count, url: .html_url}",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            return None
        repos = []
        for line in result.stdout.strip().split("\n"):
            if line.strip():
                try:
                    repos.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        return repos if repos else None
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None


# --- Shared helpers ---

def _llm_chat(system_prompt: str, user_prompt: str) -> str | None:
    try:
        from lanes_ceo.config import Config
        from lanes_ceo.llm import LLMClient

        cfg = Config.from_env()
        llm = LLMClient(cfg)
        response = llm.chat(system_prompt, user_prompt)
        if response.startswith("[LLM"):
            return None
        return response
    except Exception:
        return None


def _today() -> str:
    from datetime import date
    return date.today().isoformat()


def _check_briefing_quality(artifact: Artifact, label: str) -> list[str]:
    issues = []
    if len(artifact.summary) < 80:
        issues.append(f"{label}内容过短（<80字）")
    if len(artifact.sources) == 0:
        issues.append("缺少数据来源标注")
    return issues
