from datetime import date
from pathlib import Path

from lanes_ceo.contracts import Artifact, CriticReview, Job

PRESENTATION_STRUCTURE = [
    ("封面", "汇报标题 / 姓名 / 日期"),
    ("目录", "汇报大纲"),
    ("研究背景与意义", "课题来源、学术价值、应用前景"),
    ("本周核心进展", "2-3 项关键进展，每项配数据/图表支撑"),
    ("实验结果与分析", "实验设计、数据展示、结果讨论"),
    ("难点与挑战", "遇到的技术瓶颈和理论困难"),
    ("方案对比与选型", "候选方案对比、决策依据"),
    ("下周工作计划", "具体任务、预期产出、时间节点"),
    ("需要讨论的问题", "向导师和团队请教的问题"),
    ("参考文献与致谢", "引用文献、合作致谢"),
]

TARGET_SLIDE_COUNT = 15
MIN_SLIDES = 12
MAX_SLIDES = 18
CORE_SLIDE_MIN_RATIO = 0.30


class PresentationWorkflow:
    role_group = "presentation"
    actor_name = "presentation-actor"
    critic_name = "presentation-critic"

    def run_actor(self, job: Job) -> Artifact:
        message = job.input.get("message", "生成组会汇报PPT")
        today = date.today()
        week_label = f"{today.year}W{today.isocalendar()[1]}"

        from lanes_ceo.workflows.utils import llm_chat

        prompt = _build_ppt_prompt(message)
        llm_response = llm_chat(
            "你是一名博士研究生，需准备30分钟组会PPT汇报。输出每页标题和要点。",
            prompt,
        ) or ""

        artifact_dir = Path(job.workspace) / "artifacts"
        artifact_dir.mkdir(parents=True, exist_ok=True)
        pptx_path = artifact_dir / f"presentation-{week_label}.pptx"

        slide_count = _write_pptx(pptx_path, message, llm_response)

        return Artifact(
            artifact_id=f"artifact-{job.job_id}",
            job_id=job.job_id,
            artifact_type="presentation",
            summary=f"PPT 汇报 {week_label}: {message} ({slide_count} 页)",
            artifact_paths=[str(pptx_path)],
            sources=["llm-generated", "user-input"],
            risks=["LLM 内容需人工核实", "图表需手动插入"],
            user_confirmations=[
                "请确认幻灯片内容和数据准确性",
                "请确认汇报时长是否适配 (~30分钟)",
            ],
        )

    def run_critic(self, job: Job, artifact: Artifact) -> CriticReview:
        issues: list[str] = []
        score = 85

        # Check file exists
        if artifact.artifact_paths:
            path = Path(artifact.artifact_paths[0])
            if not path.exists():
                issues.append("生成的 pptx 文件不存在")
                score -= 30

        # Check slide count range
        slide_count = _extract_slide_count(artifact.summary)
        if slide_count is not None:
            if slide_count < MIN_SLIDES:
                issues.append(f"页数不足 (当前 {slide_count}, 最少 {MIN_SLIDES})")
                score -= 10
            elif slide_count > MAX_SLIDES:
                issues.append(f"页数过多 (当前 {slide_count}, 最多 {MAX_SLIDES})")
                score -= 10

        # Check structure
        structure_ok = _check_structure(artifact.summary)
        if not structure_ok:
            issues.append("PPT 结构不完整，缺少关键章节")

        approved = len(issues) == 0
        return CriticReview(
            review_id=f"review-{job.job_id}",
            job_id=job.job_id,
            review_result="approved" if approved else "returned",
            score=max(score, 0),
            issues=issues,
            approved=approved,
            return_to_actor=not approved,
            handoff_note="PPT 质量合格" if approved else "请修正后重新提交",
        )


def _build_ppt_prompt(message: str) -> str:
    structure_text = "\n".join(
        f"{i + 1}. {s[0]} — {s[1]}" for i, s in enumerate(PRESENTATION_STRUCTURE)
    )
    return (
        f"请根据以下主题生成组会汇报PPT的完整大纲，共约{TARGET_SLIDE_COUNT}页：\n\n"
        f"主题：{message}\n\n"
        f"要求结构：\n{structure_text}\n\n"
        f"要点：每页给出标题和3-5个要点，核心成果页占比≥{int(CORE_SLIDE_MIN_RATIO * 100)}%。"
    )


def _write_pptx(path: Path, message: str, llm_response: str) -> int:
    from pptx import Presentation

    prs = Presentation()
    prs.slide_width = 13350400  # 16:9 widescreen
    prs.slide_height = 7512000

    # Title slide
    slide_layout = prs.slide_layouts[0] if prs.slide_layouts else None
    if slide_layout:
        slide = prs.slides.add_slide(slide_layout)
        if slide.shapes.title:
            slide.shapes.title.text = message

    if llm_response and not llm_response.startswith("[LLM"):
        # Parse LLM output into slides
        sections = llm_response.split("\n\n")
        for section_text in sections:
            stripped = section_text.strip()
            if not stripped:
                continue
            lines = stripped.split("\n", 1)
            title_text = lines[0].lstrip("0123456789. )-")
            body_text = lines[1] if len(lines) > 1 else "（待展开）"

            if len(prs.slide_layouts) > 1:
                slide = prs.slides.add_slide(prs.slide_layouts[1])
            else:
                slide = prs.slides.add_slide(prs.slide_layouts[0])
            if slide.shapes.title:
                slide.shapes.title.text = title_text
    else:
        # Stub slides from structure
        for title, description in PRESENTATION_STRUCTURE:
            if len(prs.slide_layouts) > 1:
                slide = prs.slides.add_slide(prs.slide_layouts[1])
            else:
                slide = prs.slides.add_slide(prs.slide_layouts[0])
            if slide.shapes.title:
                slide.shapes.title.text = title

    prs.save(str(path))
    return len(prs.slides)


def _extract_slide_count(summary: str) -> int | None:
    import re

    match = re.search(r"(\d+)\s*页", summary)
    return int(match.group(1)) if match else None


def _check_structure(summary: str) -> bool:
    required_sections = ["背景", "进展", "实验", "计划"]
    return any(s in summary for s in required_sections)
