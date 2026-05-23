"""Update checker workflow — daily scan for outdated tools, skills, MCPs, and CLIs."""

from __future__ import annotations

import json
import logging
import subprocess
from datetime import date
from pathlib import Path
from typing import Any

from lanes_ceo.contracts import Artifact, CriticReview, Job
from lanes_ceo.workflows.utils import llm_chat, get_artifact_dir

logger = logging.getLogger("lanes_ceo.update_checker")

ACTOR_SYSTEM = """你是 Lane 的 DevOps 助手。以下是今日自动扫描的工具/Skill/MCP/CLI 更新状态报告。

你需要用中文整理一份简洁的更新建议（300字以内），按优先级排列：
1. 【紧急】安全漏洞或破坏性更新
2. 【建议】有重要新功能或性能提升的更新
3. 【可选】小幅改进或边缘工具

如果一切最新，直接说「全部工具已是最新版本，无需更新」即可。"""

CRITIC_SYSTEM = """你是 DevOps 审查员。检查这份更新报告的完整性和准确性：
1. 是否覆盖了所有需要检查的工具类别
2. 更新建议是否合理
3. 是否有遗漏的重要更新

评分标准：覆盖完整+建议合理=90+，有遗漏=扣分"""


# ── check targets ──

def _check_claude_cli() -> dict[str, Any]:
    """Check Claude Code CLI version."""
    try:
        result = subprocess.run(
            ["claude", "--version"], capture_output=True, text=True, timeout=15
        )
        current = result.stdout.strip() or result.stderr.strip()
    except FileNotFoundError:
        current = "未安装"
    except subprocess.TimeoutExpired:
        current = "检查超时"
    except Exception as exc:
        current = f"检查失败: {exc}"

    return {"tool": "Claude Code CLI", "current": current, "latest": "需手动确认", "source": "cli"}


def _check_pip_outdated() -> list[dict[str, str]]:
    """Check outdated pip packages for LANEs_CEO and key tools."""
    packages = []
    try:
        # Check LANEs_CEO dependencies
        result = subprocess.run(
            ["pip", "list", "--outdated", "--format", "json"],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode == 0 and result.stdout.strip():
            all_outdated = json.loads(result.stdout)
            # Filter to relevant packages
            relevant = {
                "croniter", "python-docx", "python-pptx", "openai",
                "python-dotenv", "lark-oapi", "lxml", "pyyaml",
                "setuptools", "pip", "wheel",
            }
            for pkg in all_outdated:
                if pkg.get("name", "").lower() in relevant:
                    packages.append({
                        "name": pkg["name"],
                        "current": pkg.get("version", "?"),
                        "latest": pkg.get("latest_version", "?"),
                    })
    except FileNotFoundError:
        logger.debug("pip not installed, skipping outdated check")
    except (json.JSONDecodeError, subprocess.TimeoutExpired, Exception):
        logger.warning("pip outdated check failed, skipping")
    return packages


def _check_gh_cli() -> dict[str, Any]:
    """Check GitHub CLI version."""
    try:
        result = subprocess.run(
            ["gh", "--version"], capture_output=True, text=True, timeout=10
        )
        lines = result.stdout.strip().split("\n")
        # First line is like "gh version 2.63.0 (2025-03-25)"
        current = lines[0].strip() if lines else "unknown"
    except FileNotFoundError:
        current = "未安装"
    except Exception as exc:
        current = f"检查失败: {exc}"
    return {"tool": "GitHub CLI (gh)", "current": current, "source": "cli"}


def _check_git_repos() -> list[dict[str, str]]:
    """Check local git repos for unpulled changes."""
    repo_paths = [
        Path("G:/blog/claude_code_useage/multi-agent"),
        Path.home() / ".claude",
    ]
    repos = []
    for path in repo_paths:
        if not (path / ".git").exists():
            continue
        try:
            result = subprocess.run(
                ["git", "-C", str(path), "remote", "update"], capture_output=True, timeout=15,
            )
            result2 = subprocess.run(
                ["git", "-C", str(path), "status", "--porcelain", "-b"],
                capture_output=True, text=True, timeout=10,
            )
            status = result2.stdout.strip()[:200]
            repos.append({"repo": str(path), "status": status or "clean"})
        except Exception as exc:
            repos.append({"repo": str(path), "status": f"检查失败: {exc}"})
    return repos


def _check_mcp_servers() -> list[dict[str, str]]:
    """Check configured MCP servers (read from settings)."""
    servers = []
    settings_paths = [
        Path.home() / ".claude" / "settings.json",
        Path.home() / ".claude" / "settings.local.json",
    ]
    for sp in settings_paths:
        if not sp.exists():
            continue
        try:
            data = json.loads(sp.read_text(encoding="utf-8"))
            mcp_servers = data.get("mcpServers", {})
            for name, cfg in mcp_servers.items():
                servers.append({
                    "name": name,
                    "type": cfg.get("type", "stdio"),
                    "command": cfg.get("command", "?")[:80],
                })
        except Exception as exc:
            logger.debug("Failed to read MCP settings from %s: %s", sp, exc)
    return servers


def _check_npm_outdated() -> list[dict[str, str]]:
    """Check outdated global npm packages (often used by MCP servers)."""
    packages = []
    try:
        result = subprocess.run(
            ["npm", "list", "-g", "--depth=0", "--json"],
            capture_output=True, text=True, timeout=20,
        )
        if result.returncode == 0 and result.stdout.strip():
            data = json.loads(result.stdout)
            deps = data.get("dependencies", {})
            for name, info in deps.items():
                current = info.get("version", "?")
                # Try to get latest
                try:
                    latest_result = subprocess.run(
                        ["npm", "view", name, "version"],
                        capture_output=True, text=True, timeout=10,
                    )
                    latest = latest_result.stdout.strip() if latest_result.returncode == 0 else "?"
                except Exception:
                    latest = "?"
                if latest != "?" and current != latest:
                    packages.append({"name": name, "current": current, "latest": latest})
    except FileNotFoundError:
        logger.debug("npm not installed, skipping outdated check")
    except Exception:
        logger.warning("npm outdated check failed, skipping")
    return packages


# ── workflow ──

class UpdateCheckerWorkflow:
    role_group = "update_checker"
    actor_name = "update-checker-actor"
    critic_name = "update-checker-critic"

    def run_actor(self, job: Job) -> Artifact:
        today = date.today().isoformat()
        logger.info("UpdateChecker actor starting, job=%s", job.job_id)

        # Run all checks
        claude = _check_claude_cli()
        gh = _check_gh_cli()
        pip_old = _check_pip_outdated()
        npm_old = _check_npm_outdated()
        mcp_list = _check_mcp_servers()
        git_repos = _check_git_repos()

        # Build check report
        report_lines = [
            f"# 工具更新检查报告 — {today}",
            "",
            "## 1. CLI 工具",
            f"- Claude Code: {claude['current']}",
            f"- GitHub CLI: {gh['current']}",
            "",
            "## 2. Python 包 (LANEs_CEO 相关)",
        ]
        if pip_old:
            for pkg in pip_old:
                report_lines.append(f"- **{pkg['name']}**: {pkg['current']} → {pkg['latest']} [需更新]")
        else:
            report_lines.append("- 全部最新 ✓")
        report_lines.append("")
        report_lines.append("## 3. 全局 npm 包 (MCP 服务器相关)")
        if npm_old:
            for pkg in npm_old:
                report_lines.append(f"- **{pkg['name']}**: {pkg['current']} → {pkg['latest']} [需更新]")
        else:
            report_lines.append("- 全部最新或无更新 ✓")
        report_lines.append("")
        report_lines.append("## 4. MCP 服务器配置")
        if mcp_list:
            for srv in mcp_list:
                report_lines.append(f"- {srv['name']} ({srv['type']}): `{srv['command']}`")
            report_lines.append("  - ⚠ MCP 服务器更新需手动检查各自仓库")
        else:
            report_lines.append("- 未配置 MCP 服务器")
        report_lines.append("")
        report_lines.append("## 5. 本地仓库状态")
        for repo in git_repos:
            report_lines.append(f"- {repo['repo']}: {repo['status']}")
        report_lines.append("")
        report_lines.append("## 6. Skills 更新")
        report_lines.append("- Skills 随 Claude Code CLI 更新，检查 CLI 版本即可")
        report_lines.append("- 自定义 Skills 路径: `~/.claude/skills/`")

        raw_report = "\n".join(report_lines)

        # Let LLM summarize
        update_summary = llm_chat(ACTOR_SYSTEM, raw_report)
        if update_summary is None:
            update_summary = raw_report

        # Save report
        out_dir = get_artifact_dir("update_check")
        ts = date.today().strftime("%Y%m%d")
        report_path = out_dir / f"update-check-{ts}.md"
        report_path.write_text(raw_report, encoding="utf-8")
        summary_path = out_dir / f"update-summary-{ts}.md"
        summary_path.write_text(update_summary, encoding="utf-8")

        # Determine if action needed
        needs_action = bool(pip_old or npm_old)

        return Artifact(
            artifact_id=f"artifact-{job.job_id}",
            job_id=job.job_id,
            artifact_type="update_check",
            summary=update_summary,
            artifact_paths=[str(report_path), str(summary_path)],
            sources=["cli-scan", "pip", "npm", "git", "llm-analysis"],
            risks=["版本号仅做参考，实际更新前请检查 changelog", "某些工具可能被间接依赖约束无法升级"],
            user_confirmations=(
                ["请确认是否需要立即执行更新操作"] if needs_action else []
            ),
        )

    def run_critic(self, job: Job, artifact: Artifact) -> CriticReview:
        issues: list[str] = []

        if len(artifact.artifact_paths) < 2:
            issues.append("缺少完整报告文件")
        if len(artifact.sources) < 3:
            issues.append("检查覆盖不够全面")
        if len(artifact.summary) < 60:
            issues.append("更新摘要过短")

        score = 95 - len(issues) * 15
        approved = len(issues) == 0

        # Double-check with LLM critic
        review_text = llm_chat(
            CRITIC_SYSTEM,
            f"更新报告摘要：\n{artifact.summary}\n\n原始扫描结果：\n来源: {', '.join(artifact.sources)}",
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
