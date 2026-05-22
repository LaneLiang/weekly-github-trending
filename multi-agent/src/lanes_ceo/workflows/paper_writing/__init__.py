from lanes_ceo.contracts import Artifact, CriticReview, Job
from lanes_ceo.workflows.utils import llm_chat


DRAFT_SYSTEM = (
    "你是一名博士研究生，需要按照Nature/Science水准撰写论文草稿。"
    "要求：逻辑清晰、论证严密、图表题注规范、公式编号完整。"
    "输出完整的论文小节，800字以内。"
)


class PaperWritingWorkflow:
    role_group = "paper_writing"
    actor_name = "paper-writing-actor"
    critic_name = "paper-writing-critic"
    exempt_from_elimination = True

    def run_actor(self, job: Job) -> Artifact:
        section = job.input.get("message", "draft section")

        draft = llm_chat(DRAFT_SYSTEM, f"撰写以下论文小节：{section}")
        summary = draft if draft else (
            f"论文草稿: {section}\n"
            f"输出路径: drafts/current/, figures/, references.bib\n"
            f"（待 LLM 配置后自动生成论文草稿）"
        )

        return Artifact(
            artifact_id=f"artifact-{job.job_id}",
            job_id=job.job_id,
            artifact_type="paper_draft",
            summary=summary,
            artifact_paths=["drafts/current/", "figures/", "references.bib"],
            sources=["literature-review", "experiment-data"],
            risks=["factual accuracy requires author verification", "figure placement may need adjustment"],
            user_confirmations=["请确认技术内容准确性", "图表数据和格式是否需要调整"],
        )

    def run_critic(self, job: Job, artifact: Artifact) -> CriticReview:
        issues = _check_draft_quality(artifact)
        score = 92 - len(issues) * 12
        approved = len(issues) == 0
        return CriticReview(
            review_id=f"review-{job.job_id}",
            job_id=job.job_id,
            review_result="approved" if approved else "returned",
            score=max(score, 0),
            issues=issues,
            approved=approved,
            return_to_actor=not approved,
            handoff_note="论文草稿审核通过" if approved else "请修改后重新提交",
        )


def _check_draft_quality(artifact: Artifact) -> list[str]:
    issues = []
    if artifact.artifact_type != "paper_draft":
        issues.append("产物类型错误")
    if len(artifact.user_confirmations) < 2:
        issues.append("缺少作者确认检查点")
    if len(artifact.artifact_paths) < 2:
        issues.append("缺少预期输出路径")
    if len(artifact.summary) < 150:
        issues.append("草稿内容过短（<150字），不够完整")
    has_structure = any(
        kw in artifact.summary
        for kw in ["引言", "方法", "结果", "结论", "introduction", "method", "result", "conclusion"]
    )
    if not has_structure:
        issues.append("缺少论文基本结构（引言/方法/结果/结论）")
    return issues
