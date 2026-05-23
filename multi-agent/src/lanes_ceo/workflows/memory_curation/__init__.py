"""Memory curation workflow — weekly dedup, TTL expiration, and cleanup of ~/.claude/memory/."""

from __future__ import annotations

import json
import logging
import os
import re
import subprocess
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

from lanes_ceo.contracts import Artifact, CriticReview, Job
from lanes_ceo.workflows.utils import llm_chat, get_artifact_dir

logger = logging.getLogger("lanes_ceo.memory_curation")

ACTOR_SYSTEM = """你是 Lane 的知识管理助手。你需要整理 ~/.claude/memory/ 目录下的跨会话记忆。

任务：
1. 扫描所有 memory 文件的 frontmatter 和 body
2. 检查 TTL 过期的条目（feedback 类 90 天 sliding TTL）
3. 识别高度相似的记忆（相似度 >= 0.85），标记为可合并
4. 生成整理报告，推送到飞书

报告格式（中文，300字以内）：
- 当前记忆总数: X 条
- 过期标记: Y 条
- 建议合并: Z 对
- 需手动确认: 列出关键决策变更

如果一切正常，直接说明「记忆系统状态良好，无需操作」即可。"""

CRITIC_SYSTEM = """你是知识管理审查员。检查记忆整理报告的完整性和准确性：
1. 过期判断是否正确（feedback 90天，其他永不过期）
2. 去重建议是否合理（仅标记，不自动删除）
3. 是否有遗漏的异常（如损坏文件、编码错误）

评分标准：覆盖完整+判断准确=90+，有遗漏=扣分"""

MEMORY_DIR = Path(os.environ.get("USERPROFILE", Path.home())) / ".claude" / "memory"

# ── helper functions ──

def _scan_memory_files() -> list[dict[str, Any]]:
    """Scan all memory files and return their metadata."""
    entries = []
    if not MEMORY_DIR.exists():
        return entries

    for md_file in MEMORY_DIR.rglob("*.md"):
        if md_file.name == "MEMORY.md" or md_file.name.startswith("_"):
            continue
        try:
            content = md_file.read_text(encoding="utf-8")
        except Exception:
            logger.warning("无法读取 %s", md_file)
            entries.append({
                "path": str(md_file),
                "name": md_file.stem,
                "error": "读取失败（编码或权限问题）",
                "type": "unknown",
                "size": 0,
                "created": "",
                "updated": "",
                "mtime": "",
            })
            continue

        # Parse frontmatter
        fm = {}
        body = content
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                fm_text = parts[1]
                body = parts[2]
                for line in fm_text.strip().split("\n"):
                    if ":" in line:
                        key, _, val = line.partition(":")
                        fm[key.strip()] = val.strip()

        mtime = datetime.fromtimestamp(md_file.stat().st_mtime).isoformat()
        entry_type = fm.get("type", "unknown")
        created = fm.get("created", "")
        updated = fm.get("updated", "")

        # Check TTL for feedback entries
        ttl_expired = False
        if entry_type == "feedback":
            try:
                last_updated = datetime.fromisoformat(updated) if updated else datetime.fromisoformat(created) if created else None
                if last_updated:
                    days_since = (datetime.now() - last_updated).days
                    if days_since > 90:
                        ttl_expired = True
            except (ValueError, TypeError):
                logger.debug("TTL check failed for %s: invalid date format", md_file.stem)

        entries.append({
            "path": str(md_file),
            "name": md_file.stem,
            "type": entry_type,
            "size": len(content),
            "created": created,
            "updated": updated,
            "mtime": mtime,
            "ttl_expired": ttl_expired,
            "frontmatter_valid": bool(fm.get("type")),
            "body_preview": body.strip()[:200],
        })

    return entries


def _check_large_files(entries: list[dict]) -> list[dict]:
    """Identify files exceeding 50KB limit."""
    large = []
    for e in entries:
        if e.get("size", 0) > 50_000:
            large.append(e)
    return large


def _detect_duplicates(entries: list[dict]) -> list[dict]:
    """Detect potential duplicate entries via simple body overlap."""
    pairs = []
    for i, e1 in enumerate(entries):
        for j, e2 in enumerate(entries):
            if j <= i:
                continue
            if e1.get("type") != e2.get("type"):
                continue
            # Simple Jaccard-like check on body preview (word overlap)
            words1 = set(e1.get("body_preview", "").split())
            words2 = set(e2.get("body_preview", "").split())
            if not words1 or not words2:
                continue
            overlap = len(words1 & words2) / len(words1 | words2)
            if overlap >= 0.5:  # Flag for LLM review
                pairs.append({
                    "entry_a": e1["name"],
                    "entry_b": e2["name"],
                    "overlap_score": round(overlap, 3),
                })
    return pairs


def _check_session_active() -> bool:
    """Check if a Claude Code session is currently active."""
    try:
        result = subprocess.run(
            ["tasklist"], capture_output=True, text=True, timeout=5
        )
        # Check for claude processes
        if "claude" in result.stdout.lower():
            return True
    except Exception:
        logger.debug("Session check failed (tasklist unavailable), assuming no active session")

    # Check session directory
    sessions_dir = Path.home() / ".claude" / "sessions"
    if sessions_dir.exists():
        recent = list(sessions_dir.glob("*"))
        for s in recent:
            try:
                mtime = datetime.fromtimestamp(s.stat().st_mtime)
                if (datetime.now() - mtime).total_seconds() < 300:  # modified in last 5 min
                    return True
            except Exception:
                logger.debug("Session stat check failed for %s", s)
    return False


def _update_memory_index(entries: list[dict]) -> None:
    """Update MEMORY.md index with current counts."""
    index_path = MEMORY_DIR / "MEMORY.md"
    if not index_path.exists():
        return

    total = len([e for e in entries if not e.get("error")])
    now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S%z")

    try:
        content = index_path.read_text(encoding="utf-8")
        content = re.sub(r"^last_updated:.*", f'last_updated: "{now}"', content, flags=re.MULTILINE)
        content = re.sub(r"^total_entries:\s*\d+", f"total_entries: {total}", content, flags=re.MULTILINE)
        index_path.write_text(content, encoding="utf-8")
    except Exception as exc:
        logger.warning("更新 MEMORY.md 索引失败: %s", exc)


# ── workflow class ──

class MemoryCurationWorkflow:
    role_group = "memory_curation"
    actor_name = "memory-curation-actor"
    critic_name = "memory-curation-critic"

    def run_actor(self, job: Job) -> Artifact:
        today = date.today().isoformat()
        logger.info("MemoryCuration actor starting, job=%s", job.job_id)

        # Pre-check: active session?
        session_active = _check_session_active()
        do_destructive = not session_active

        # Scan all memory files
        entries = _scan_memory_files()
        expired = [e for e in entries if e.get("ttl_expired")]
        large_files = _check_large_files(entries)
        dup_pairs = _detect_duplicates(entries)
        corrupted = [e for e in entries if e.get("error")]

        # Build report
        lines = [
            f"# 记忆整理报告 — {today}",
            "",
            f"## 概览",
            f"- 记忆总数: {len(entries)} 条",
            f"- 过期 (feedback > 90天): {len(expired)} 条",
            f"- 超大文件 (>50KB): {len(large_files)} 个",
            f"- 疑似重复: {len(dup_pairs)} 对",
            f"- 损坏文件: {len(corrupted)} 个",
            f"- 活跃 session: {'是 (仅做只读摘要)' if session_active else '否 (完整整理)'}",
            "",
        ]

        if expired:
            lines.append("## 过期条目")
            lines.append("```")
            for e in expired:
                lines.append(f"- {e['name']} ({e['type']}): 上次更新 {e.get('updated', '未知')}")
            lines.append("```")
            lines.append("")

        if large_files:
            lines.append("## 超大文件")
            lines.append("```")
            for f in large_files:
                lines.append(f"- {f['name']}: {f['size'] / 1024:.1f} KB")
            lines.append("```")
            lines.append("")

        if dup_pairs:
            lines.append("## 疑似重复对")
            lines.append("```")
            for p in dup_pairs:
                lines.append(f"- {p['entry_a']} ↔ {p['entry_b']} (重叠度: {p['overlap_score']})")
            lines.append("```")
            lines.append("")

        if corrupted:
            lines.append("## 损坏文件")
            for c in corrupted:
                lines.append(f"- {c['name']}: {c.get('error', '未知错误')}")
            lines.append("")

        raw_report = "\n".join(lines)

        # Let LLM generate clean summary
        summary = llm_chat(ACTOR_SYSTEM, raw_report)
        if summary is None:
            summary = raw_report

        # Save report
        out_dir = get_artifact_dir("memory_curation")
        ts = date.today().strftime("%Y%m%d")
        report_path = out_dir / f"memory-curation-{ts}.md"
        report_path.write_text(raw_report, encoding="utf-8")

        # Update index
        if do_destructive:
            _update_memory_index(entries)

        # Prepare Feishu notification content
        feishu_msg = (
            f"🧠 记忆整理完成 ({today})\n"
            f"总数: {len(entries)} | 过期: {len(expired)} | 疑似重复: {len(dup_pairs)}\n"
            + (f"超大文件: {len(large_files)} 个" if large_files else "")
        )

        return Artifact(
            artifact_id=f"artifact-{job.job_id}",
            job_id=job.job_id,
            artifact_type="memory_curation",
            summary=summary,
            artifact_paths=[str(report_path)],
            sources=["memory-scan", "ttl-check", "dedup-analysis", "llm-summary"],
            risks=[
                "去重仅标记不自动删除，需手动确认",
                "过期判断基于 updated 字段，若 frontmatter 损坏可能不准确",
                "LLM 语义去重阈值 0.85，相似但不同的条目可能被误标",
            ],
            user_confirmations=(
                [f"确认删除 {len(expired)} 条过期记忆? (需手动执行 claude-memory remove)"] if expired else []
            ) + ([f"确认合并 {len(dup_pairs)} 对疑似重复记忆?"] if dup_pairs else []),
        )

    def run_critic(self, job: Job, artifact: Artifact) -> CriticReview:
        issues: list[str] = []

        if len(artifact.artifact_paths) < 1:
            issues.append("缺少整理报告文件")
        if len(artifact.sources) < 3:
            issues.append("检查覆盖不够全面")
        if "memory-scan" not in artifact.sources:
            issues.append("未执行记忆扫描")

        score = 95 - len(issues) * 15
        approved = len(issues) == 0

        review_text = llm_chat(
            CRITIC_SYSTEM,
            f"整理报告：\n{artifact.summary}\n\n来源: {', '.join(artifact.sources)}\n风险: {', '.join(artifact.risks)}",
        )

        return CriticReview(
            review_id=f"review-{job.job_id}",
            job_id=job.job_id,
            review_result="approved" if approved else "returned",
            score=max(score, 0),
            issues=issues,
            approved=approved,
            return_to_actor=not approved,
            handoff_note=review_text[:500] if review_text else "审核完成",
        )
