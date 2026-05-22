from datetime import date

from lanes_ceo.contracts import Artifact, CriticReview, Job

REPORT_MIN_SECTIONS = 3
REFLECTION_MIN_WORDS = 80

DAILY_REPORT_SYSTEM = (
    "你是一名博士研究生，需要写一份今日工作总结。要求简洁、具体、数据化，"
    "避免空话套话。包含：已完成工作、遇到的问题、明日计划。总计300字以内。"
)

REFLECTION_SYSTEM = (
    "你是一名博士研究生，需要进行每日反思复盘。要求深入、诚实、有洞察力。"
    "包含：今天最大的收获、做得不好的地方、明天如何改进。总计200字以内。"
)


class DailyReportWorkflow:
    role_group = "daily_report"
    actor_name = "daily-report-actor"
    critic_name = "daily-report-critic"

    def run_actor(self, job: Job) -> Artifact:
        message = job.input.get("message", "今日工作总结")
        today = date.today().isoformat()

        content = _llm_chat(DAILY_REPORT_SYSTEM, f"今天日期：{today}\n主题：{message}")
        report = content if content else f"今日工作总结（{today}）：{message}\n（待 LLM 配置后自动生成详细内容）"

        return Artifact(
            artifact_id=f"artifact-{job.job_id}",
            job_id=job.job_id,
            artifact_type="daily_report",
            summary=report,
            artifact_paths=[],
            sources=["user-conversation", "llm-generated"],
            risks=["incomplete coverage"],
            user_confirmations=["请确认今日工作内容是否完整"],
        )

    def run_critic(self, job: Job, artifact: Artifact) -> CriticReview:
        issues = _check_report_quality(artifact.summary)
        score = _score_report(len(issues))
        approved = len(issues) == 0
        return CriticReview(
            review_id=f"review-{job.job_id}",
            job_id=job.job_id,
            review_result="approved" if approved else "returned",
            score=score,
            issues=issues,
            approved=approved,
            return_to_actor=not approved,
            handoff_note="日报审核通过" if approved else "请补充完善后再提交",
        )


class ReflectionWorkflow:
    role_group = "reflection"
    actor_name = "reflection-actor"
    critic_name = "reflection-critic"

    def run_actor(self, job: Job) -> Artifact:
        message = job.input.get("message", "今日反思")
        today = date.today().isoformat()

        content = _llm_chat(REFLECTION_SYSTEM, f"今天日期：{today}\n主题：{message}")
        reflection = content if content else f"今日反思（{today}）：{message}\n（待 LLM 配置后自动生成详细内容）"

        return Artifact(
            artifact_id=f"artifact-{job.job_id}",
            job_id=job.job_id,
            artifact_type="reflection",
            summary=reflection,
            artifact_paths=[],
            sources=["user-conversation", "llm-generated"],
            risks=["shallow analysis"],
            user_confirmations=["反思内容是否需要调整方向"],
        )

    def run_critic(self, job: Job, artifact: Artifact) -> CriticReview:
        issues = _check_reflection_quality(artifact.summary)
        score = _score_report(len(issues)) + 5
        approved = len(issues) == 0
        return CriticReview(
            review_id=f"review-{job.job_id}",
            job_id=job.job_id,
            review_result="approved" if approved else "returned",
            score=min(score, 100),
            issues=issues,
            approved=approved,
            return_to_actor=not approved,
            handoff_note="反思总结审核通过" if approved else "反思不够深入，请重新思考",
        )


def _llm_chat(system_prompt: str, user_prompt: str) -> str | None:
    try:
        from lanes_ceo.config import Config
        from lanes_ceo.llm import LLMClient

        cfg = Config.from_env()
        llm = LLMClient(cfg)
        response = llm.chat(system_prompt, user_prompt)
        if response.startswith("[LLM") or response.startswith("[LLM error"):
            return None
        return response
    except Exception:
        return None


def _check_report_quality(text: str) -> list[str]:
    issues: list[str] = []
    if len(text) < 60:
        issues.append("日报内容过短（<60字）")
    empty_phrases = ["有待加强", "进一步研究", "继续努力", "积极推进", "总体良好"]
    found = [p for p in empty_phrases if p in text]
    if found:
        issues.append(f"包含空话表述: {', '.join(found)}")
    if "完成" not in text and "做了" not in text and "进行" not in text:
        issues.append("缺少具体工作描述")
    return issues


def _check_reflection_quality(text: str) -> list[str]:
    issues: list[str] = []
    if len(text) < REFLECTION_MIN_WORDS:
        issues.append(f"反思内容过短（<{REFLECTION_MIN_WORDS}字）")
    empty_phrases = ["进一步研究", "继续努力", "有待加强"]
    found = [p for p in empty_phrases if p in text]
    if found:
        issues.append(f"包含空话表述: {', '.join(found)}")
    return issues


def _score_report(issue_count: int) -> int:
    base = 85
    return max(base - issue_count * 15, 0)
