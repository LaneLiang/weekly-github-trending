import os
from datetime import date
from pathlib import Path

from lanes_ceo.contracts import Artifact, CriticReview, Job

WEEKLY_REPORT_SECTIONS = [
    "本周已完成工作",
    "科研进度复盘",
    "实验数据/仿真结果（含图表）",
    "工作亮点",
    "现存问题",
    "失败案例及原因分析",
    "下周详细工作计划",
    "需要团队及导师协助解决的问题",
]

EMPTY_PHRASE_FLAGS = [
    "有待加强", "进一步研究", "继续努力", "积极推进",
    "认真完成", "努力改进", "高度重视", "持续关注",
    "总体良好", "基本完成", "大致符合",
]

SECTION_HEADING_LEVEL = 1


class WeeklyReportWorkflow:
    role_group = "weekly_report"
    actor_name = "weekly-report-actor"
    critic_name = "weekly-report-critic"

    def run_actor(self, job: Job) -> Artifact:
        message = job.input.get("message", "生成本周周报")
        today = date.today()
        week_label = f"{today.year}W{today.isocalendar()[1]}"

        from lanes_ceo.workflows.utils import llm_chat

        prompt = _build_weekly_report_prompt(message)
        llm_response = llm_chat(
            "你是一名博士研究生，需按毕业论文格式撰写周报。输出严格分8个章节，内容详实。",
            prompt,
        ) or ""

        artifact_dir = Path(job.workspace) / "artifacts"
        artifact_dir.mkdir(parents=True, exist_ok=True)
        docx_path = artifact_dir / f"weekly-report-{week_label}.docx"

        _write_docx(docx_path, week_label, message, llm_response)

        return Artifact(
            artifact_id=f"artifact-{job.job_id}",
            job_id=job.job_id,
            artifact_type="weekly_report",
            summary=f"周报 {week_label}: {message}",
            artifact_paths=[str(docx_path)],
            sources=["llm-generated", "user-input"],
            risks=["LLM 内容需人工核实", "图表需手动补充"],
            user_confirmations=[
                "请核验所有实验数据和图表",
                "请确认下周计划是否可执行",
            ],
        )

    def run_critic(self, job: Job, artifact: Artifact) -> CriticReview:
        issues: list[str] = []
        score = 90

        # Check file exists
        if artifact.artifact_paths:
            path = Path(artifact.artifact_paths[0])
            if not path.exists():
                issues.append("生成的 docx 文件不存在")
                score -= 30

        # Check sections coverage
        if not llm_response_has_all_sections(artifact.summary):
            issues.append("部分周报板块缺失")

        # Check for empty phrases
        empty_count = len(detect_empty_phrases(artifact.summary))
        if empty_count > 2:
            issues.append(f"检测到 {empty_count} 处空话/套话表述")
            score -= empty_count * 5

        approved = len(issues) == 0
        return CriticReview(
            review_id=f"review-{job.job_id}",
            job_id=job.job_id,
            review_result="approved" if approved else "returned",
            score=max(score, 0),
            issues=issues,
            approved=approved,
            return_to_actor=not approved,
            handoff_note="周报质量合格" if approved else "请修正后重新提交",
        )


def _build_weekly_report_prompt(message: str) -> str:
    sections_text = "\n".join(
        f"{i + 1}. {s}" for i, s in enumerate(WEEKLY_REPORT_SECTIONS)
    )
    return (
        f"请根据以下主题生成一份完整的周报，严格按以下8个章节撰写，每章内容充实（100-200字）：\n\n"
        f"{sections_text}\n\n"
        f"主题：{message}\n\n"
        f"格式要求：使用正式学术语言，图表需附题注（如：图1-1 xxx），公式需编号（如：(1-1)）。"
    )


def _write_docx(
    path: Path,
    week_label: str,
    message: str,
    llm_response: str,
) -> None:
    from docx import Document
    from docx.shared import Pt

    doc = Document()
    doc.add_heading(f"周报 — {week_label}", level=0)
    doc.add_paragraph(f"主题：{message}")

    if llm_response and not llm_response.startswith("[LLM"):
        sections = llm_response.split("\n\n")
        for section_text in sections:
            stripped = section_text.strip()
            if not stripped:
                continue
            # Try to detect section header
            lines = stripped.split("\n", 1)
            heading_text = lines[0].lstrip("0123456789. )（）")
            doc.add_heading(heading_text, level=1)
            if len(lines) > 1:
                doc.add_paragraph(lines[1])
    else:
        for i, section in enumerate(WEEKLY_REPORT_SECTIONS):
            doc.add_heading(
                f"{i + 1}. {section}",
                level=SECTION_HEADING_LEVEL,
            )
            doc.add_paragraph("（待 LLM 填充 — 请在 .env 中配置 LANES_CEO_LLM_API_KEY）")

    doc.save(str(path))


def llm_response_has_all_sections(summary: str) -> bool:
    # Stub: in production this would parse LLM output
    return True


def detect_empty_phrases(text: str) -> list[str]:
    return [p for p in EMPTY_PHRASE_FLAGS if p in text]
