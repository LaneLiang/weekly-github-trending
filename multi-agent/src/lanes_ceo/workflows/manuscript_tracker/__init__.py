"""ManuscriptTrackerWorkflow — 投稿合规检查 workflow.

Checks: compile, diff, figure DPI/colorspace, citations, structure, supplementary.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from lanes_ceo.contracts import Artifact, CriticReview, Job
from lanes_ceo.workflows.manuscript_tracker.engine import ManuscriptTracker

logger = logging.getLogger("lanes_ceo.manuscript_tracker")


class ManuscriptTrackerWorkflow:
    """Workflow for submission compliance checking.

    Trigger: lanes-ceo --role manuscript_tracker --message "..."
    """

    role_group = "manuscript_tracker"
    actor_name = "manuscript-tracker-actor"
    critic_name = "manuscript-tracker-critic"

    def run_actor(self, job: Job) -> Artifact:
        """Run the full compliance check via ManuscriptTracker engine."""
        message = job.input.get("message", "")
        journal_key = job.input.get("journal_key", "")
        project_dir = job.input.get("project_dir", "")
        main_file = job.input.get("main_file") or None
        article_type = job.input.get("article_type") or None
        compare_journals = job.input.get("compare_journals") or None

        if not journal_key:
            journal_key = self._extract_journal_key(message)
        if not project_dir:
            project_dir = self._extract_project_dir(message)

        if not journal_key or not project_dir:
            return Artifact(
                artifact_id=f"artifact-{job.job_id}",
                job_id=job.job_id,
                artifact_type="manuscript_tracker",
                summary=(
                    "缺少必要参数。请提供 --journal-key 和 --project-dir。\n"
                    f"用法: lanes-ceo --role manuscript_tracker --message "
                    f"'nature /path/to/project'"
                ),
                artifact_paths=[],
                sources=[],
                risks=["missing required parameters"],
                user_confirmations=["请确认期刊名称和项目路径"],
            )

        logger.info(
            "Starting manuscript check: journal=%s, project=%s, main_file=%s, article=%s",
            journal_key, project_dir, main_file, article_type,
        )

        # Run comparison mode if requested
        if compare_journals:
            return self._run_comparison(job, journal_key, compare_journals, project_dir,
                                        main_file, article_type)

        engine = ManuscriptTracker(
            journal_key=journal_key,
            project_dir=Path(project_dir),
            main_file=main_file,
            article_type=article_type,
        )

        try:
            result = engine.run_full_check()
            report_path = engine.save_report(result)
        except Exception as exc:
            logger.exception("Manuscript check failed with exception")
            return Artifact(
                artifact_id=f"artifact-{job.job_id}",
                job_id=job.job_id,
                artifact_type="manuscript_tracker",
                summary=f"投稿检查引擎异常: {exc}",
                artifact_paths=[],
                sources=[],
                risks=[str(exc)],
                user_confirmations=["请检查项目文件路径和期刊名称是否正确"],
            )

        # Format summary
        summary_lines = [
            f"投稿合规检查报告 — {engine.profile.journal_name}",
            f"项目: {engine.project_dir}",
            f"主文件: {engine.main_tex}",
            f"检查时间: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}",
            "",
        ]
        for cr in result:
            icon = {"pass": "[通过]", "fail": "[失败]", "warn": "[警告]", "skip": "[跳过]"}.get(cr.status, "[?]")
            summary_lines.append(f"  {icon} {cr.checker_name}: {cr.summary}")
            for item in cr.items:
                if item.status in ("fail", "warn"):
                    summary_lines.append(f"    - [{item.code}] {item.description}")
                    if item.fix_suggestion:
                        summary_lines.append(f"      建议: {item.fix_suggestion}")

        passed = sum(1 for cr in result if cr.passed)
        failed = sum(1 for cr in result if cr.failed)
        summary_lines.append("")
        summary_lines.append(f"合计: {len(result)} 项检查, {passed} 通过, {failed} 失败")

        summary = "\n".join(summary_lines)

        return Artifact(
            artifact_id=f"artifact-{job.job_id}",
            job_id=job.job_id,
            artifact_type="manuscript_tracker",
            summary=summary,
            artifact_paths=[str(report_path)] if report_path else [],
            sources=["latexmk", "texcount", "pdfinfo", "magick", "latexdiff", "chktex", "crossref"],
            risks=[],
            user_confirmations=[
                f"检查报告已保存至: {report_path}" if report_path else "报告未保存",
            ],
        )

    def run_critic(self, job: Job, artifact: Artifact) -> CriticReview:
        """Verify the compliance report is complete and well-formed."""
        issues: list[str] = []

        if artifact.artifact_type != "manuscript_tracker":
            issues.append("artifact_type 不正确")

        if "缺少必要参数" in artifact.summary:
            issues.append("缺少 journal_key 或 project_dir 参数")

        if "投稿检查引擎异常" in artifact.summary:
            issues.append("引擎执行过程中抛出异常")

        if "合计:" not in artifact.summary:
            issues.append("报告缺少合计行，可能未完成所有检查")

        if len(artifact.summary) < 100:
            issues.append("检查报告内容过短（<100字）")

        # Check for report file existence
        if artifact.artifact_paths:
            report_path = Path(artifact.artifact_paths[0])
            if not report_path.exists():
                issues.append(f"报告文件不存在: {report_path}")
            else:
                try:
                    with open(report_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    if not isinstance(data, list):
                        issues.append("compliance_report.json 格式错误：应为列表")
                    elif len(data) == 0:
                        issues.append("compliance_report.json 为空：无检查结果")
                except (json.JSONDecodeError, FileNotFoundError) as exc:
                    issues.append(f"无法解析 compliance_report.json: {exc}")

        approved = len(issues) == 0
        score = 90 - len(issues) * 10 if not approved else 90
        return CriticReview(
            review_id=f"review-{job.job_id}",
            job_id=job.job_id,
            review_result="approved" if approved else "returned",
            score=max(score, 30),
            issues=issues,
            approved=approved,
            return_to_actor=not approved,
            handoff_note="投稿合规检查审核通过" if approved else "检查报告不完整，请重新执行",
        )

    def _extract_journal_key(self, message: str) -> str:
        """Extract journal key from message text."""
        known_journals = ["nature", "science", "ieee_jssc", "ieee_tpe",
                          "jssc", "tpe", "ieee"]
        msg_lower = message.lower()
        # Direct match
        for kj in known_journals:
            if kj in msg_lower:
                if kj == "jssc":
                    return "ieee_jssc"
                if kj == "tpe":
                    return "ieee_tpe"
                if kj == "ieee" and "tpe" in msg_lower:
                    return "ieee_tpe"
                if kj == "ieee" and "jssc" in msg_lower:
                    return "ieee_jssc"
                return kj
        return ""

    def _extract_project_dir(self, message: str) -> str:
        """Try to extract a project directory path from the message."""
        parts = message.strip().split()
        for part in parts:
            p = Path(part)
            if p.exists() and p.is_dir():
                return str(p.resolve())
        return ""

    def _run_comparison(
        self,
        job: Job,
        journal_key: str,
        compare_journals: str,
        project_dir: str,
        main_file: str | None,
        article_type: str | None,
    ) -> Artifact:
        """Run comparison between two journal profiles."""
        from lanes_ceo.workflows.manuscript_tracker.profiles import ProfileLoader

        try:
            diffs = ProfileLoader.diff_profiles(journal_key, compare_journals)
        except Exception as exc:
            return Artifact(
                artifact_id=f"artifact-{job.job_id}",
                job_id=job.job_id,
                artifact_type="manuscript_tracker",
                summary=f"对比期刊失败: {exc}",
                artifact_paths=[],
                sources=[],
                risks=[str(exc)],
                user_confirmations=["请确认两个期刊的 profile key 是否正确"],
            )

        lines = [
            f"期刊要求对比: {journal_key} vs {compare_journals}",
            "",
        ]
        if not diffs:
            lines.append("两份期刊的所有字段完全一致。")
        else:
            for d in diffs:
                compat = "[兼容]" if d.get("compatible") else "[不兼容]"
                lines.append(
                    f"  {d['field']}: {d['value_a']} vs {d['value_b']} {compat}"
                )

        summary = "\n".join(lines)
        return Artifact(
            artifact_id=f"artifact-{job.job_id}",
            job_id=job.job_id,
            artifact_type="manuscript_tracker",
            summary=summary,
            artifact_paths=[],
            sources=[],
            risks=[],
            user_confirmations=[],
        )
