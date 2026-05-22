from lanes_ceo.contracts import Artifact, CriticReview, Job
from lanes_ceo.workflows.utils import llm_chat


class PaperResearchWorkflow:
    role_group = "paper_research"
    actor_name = "paper-research-actor"
    critic_name = "paper-research-critic"

    def run_actor(self, job: Job) -> Artifact:
        topic = job.input.get("message", "research topic")

        research_plan = llm_chat(
            "你是一名博士研究生，需要为指定课题做文献调研。输出：1) 推荐检索关键词 "
            "2) 该领域前5篇重要论文（含标题+期刊+年份）3) 研究缺口分析。"
            "使用学术语言。总计500字以内。",
            f"调研课题：{topic}",
        )
        summary = research_plan if research_plan else (
            f"文献调研: {topic}\n"
            f"检索源: arxiv, semantic-scholar, google-scholar\n"
            f"（待 LLM 配置后自动生成检索策略和文献分析）"
        )

        return Artifact(
            artifact_id=f"artifact-{job.job_id}",
            job_id=job.job_id,
            artifact_type="paper_research",
            summary=summary,
            artifact_paths=["papers/downloaded/", "papers/notes/"],
            sources=["arxiv", "scholar", "semantic-scholar"],
            risks=["download failures on paywalled papers", "citation format inconsistency"],
            user_confirmations=["请确认检索关键词是否准确", "下载的论文是否需要补充"],
        )

    def run_critic(self, job: Job, artifact: Artifact) -> CriticReview:
        issues = _check_research_quality(artifact)
        score = 90 - len(issues) * 15
        approved = len(issues) == 0
        return CriticReview(
            review_id=f"review-{job.job_id}",
            job_id=job.job_id,
            review_result="approved" if approved else "returned",
            score=max(score, 0),
            issues=issues,
            approved=approved,
            return_to_actor=not approved,
            handoff_note="文献调研完成" if approved else "请补充检索范围和文献分析",
        )


def _check_research_quality(artifact: Artifact) -> list[str]:
    issues = []
    if len(artifact.sources) < 2:
        issues.append("检索源覆盖不足（需≥2个来源）")
    if len(artifact.artifact_paths) < 2:
        issues.append("缺少下载或笔记目录")
    if len(artifact.summary) < 100:
        issues.append("调研内容过短（<100字）")
    return issues
