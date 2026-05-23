"""ClaudeTaskWorkflow — trigger words → claude -p prompts, loaded from YAML.

Config lives at config/claude_tasks.yaml. Edit that file to add/change tasks
without touching code. The workflow loads and caches it at first use.
"""

from __future__ import annotations

import logging
import subprocess
import threading
from pathlib import Path

from lanes_ceo.contracts import Artifact, CriticReview, Job

logger = logging.getLogger("lanes_ceo.claude_task")

PROJECT_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_CONFIG = PROJECT_ROOT / "config" / "claude_tasks.yaml"

# thread-local storage for async results
_pending_results: dict[str, dict] = {}
_results_lock = threading.Lock()


# ── config loading ──

def load_task_map(config_path: Path | None = None) -> dict:
    """Load the task map from YAML. Falls back to built-in defaults if missing."""
    path = config_path or DEFAULT_CONFIG
    try:
        import yaml

        with open(path, "r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        tasks = data.get("tasks", {}) if isinstance(data, dict) else {}
        if tasks:
            logger.info("Loaded %d tasks from %s", len(tasks), path)
            return tasks
    except FileNotFoundError:
        logger.warning("Task config not found at %s, using defaults", path)
    except Exception as exc:
        logger.error("Failed to load task config: %s", exc)

    return _DEFAULT_TASKS


def get_allowed_users(config_path: Path | None = None) -> list[str]:
    """Return the allowed_users whitelist from the config."""
    path = config_path or DEFAULT_CONFIG
    try:
        import yaml

        with open(path, "r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        return data.get("allowed_users", []) if isinstance(data, dict) else []
    except Exception:
        return []


# ── built-in fallback ──

_DEFAULT_TASKS: dict[str, dict] = {
    "测试": {
        "prompt": (
            "运行 pytest 测试套件，报告：1) 多少通过多少失败 "
            "2) 失败测试的根因分析 3) 修复建议。"
            "用中文回复，控制在500字以内。"
        ),
        "description": "运行测试套件并分析失败原因",
        "timeout": 300,
    },
    "跑测试": {
        "prompt": (
            "运行 pytest 测试套件，报告：1) 多少通过多少失败 "
            "2) 失败测试的根因分析 3) 修复建议。"
            "用中文回复，控制在500字以内。"
        ),
        "description": "运行测试套件并分析失败原因",
        "timeout": 300,
    },
    "最近提交": {
        "prompt": "查看最近5条 git log，用中文简要总结每条提交做了什么。",
        "description": "查看最近 git 提交记录",
        "timeout": 60,
    },
    "提交": {
        "prompt": "查看最近5条 git log，用中文简要总结每条提交做了什么。",
        "description": "查看最近 git 提交记录",
        "timeout": 60,
    },
    "项目状态": {
        "prompt": (
            "运行 git status 和 git diff --stat，用中文总结："
            "有哪些未提交的修改，当前分支是什么。"
        ),
        "description": "查看项目当前状态",
        "timeout": 60,
    },
    "状态": {
        "prompt": (
            "运行 git status 和 git diff --stat，用中文总结："
            "有哪些未提交的修改，当前分支是什么。"
        ),
        "description": "查看项目当前状态",
        "timeout": 60,
    },
}

# module-level cache
_task_map: dict | None = None


def _get_task_map() -> dict:
    global _task_map
    if _task_map is None:
        _task_map = load_task_map()
    return _task_map


# ── workflow ──

class ClaudeTaskWorkflow:
    role_group = "claude_task"
    actor_name = "claude-task-actor"
    critic_name = "claude-task-critic"

    def run_actor(self, job: Job) -> Artifact:
        message = job.input.get("message", "")
        task_map = _get_task_map()
        task = _match_task(message, task_map)
        if task is None:
            return Artifact(
                artifact_id=f"artifact-{job.job_id}",
                job_id=job.job_id,
                artifact_type="claude_task",
                summary=f"未匹配到已知任务。可用的触发词：{'、'.join(task_map.keys())}",
                artifact_paths=[],
                sources=[],
                risks=[],
                user_confirmations=[],
            )

        logger.info("Running claude task: %s → %s", task["trigger"], task["description"])
        output = _run_claude(task["prompt"], timeout=task["timeout"])

        summary = f"【{task['description']}】\n\n{output}"
        artifact = Artifact(
            artifact_id=f"artifact-{job.job_id}",
            job_id=job.job_id,
            artifact_type="claude_task",
            summary=summary,
            artifact_paths=[],
            sources=["claude-cli"],
            risks=[],
            user_confirmations=[],
        )

        # Store result for async delivery and history
        _store_result(job.job_id, summary, task["description"])

        return artifact

    def run_critic(self, job: Job, artifact: Artifact) -> CriticReview:
        issues: list[str] = []
        if "未匹配到已知任务" in artifact.summary:
            issues.append("未匹配到已知任务触发词")
        elif len(artifact.summary) < 20:
            issues.append("claude 输出过短")
        elif "Error" in artifact.summary or "错误" in artifact.summary:
            issues.append("claude 输出中可能包含错误")

        approved = len(issues) == 0
        return CriticReview(
            review_id=f"review-{job.job_id}",
            job_id=job.job_id,
            review_result="approved" if approved else "returned",
            score=85 if approved else 60,
            issues=issues,
            approved=approved,
            return_to_actor=not approved,
            handoff_note="claude_task 完成" if approved else "任务执行有问题，请检查",
        )


# ── async result storage ──

def _store_result(job_id: str, summary: str, description: str) -> None:
    with _results_lock:
        _pending_results[job_id] = {"summary": summary, "description": description}
        # Keep only last 20
        if len(_pending_results) > 20:
            oldest = sorted(_pending_results.keys())[0]
            del _pending_results[oldest]


def pop_result(job_id: str) -> dict | None:
    with _results_lock:
        return _pending_results.pop(job_id, None)


def get_recent_results(limit: int = 5) -> list[dict]:
    with _results_lock:
        items = sorted(_pending_results.items(), key=lambda x: x[0], reverse=True)
        return [v for _, v in items[:limit]]


# ── helpers ──

def _match_task(message: str, task_map: dict) -> dict | None:
    """Find the longest matching trigger word in the message.

    Sorted by length descending so 「跑测试」 matches before 「测试」."""
    triggers = sorted(task_map.keys(), key=len, reverse=True)
    for trigger in triggers:
        if trigger in message:
            cfg = task_map[trigger]
            return {"trigger": trigger, **cfg}
    return None


def _run_claude(prompt: str, timeout: int = 120) -> str:
    """Run claude -p in a subprocess and return stdout."""
    try:
        result = subprocess.run(
            ["claude", "-p", prompt],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(PROJECT_ROOT),
        )
        output = result.stdout.strip()
        if not output and result.stderr.strip():
            output = f"[stderr]\n{result.stderr.strip()[:2000]}"
        if not output:
            output = "(claude 无输出)"
        return output[:4000]
    except subprocess.TimeoutExpired:
        return f"任务超时（>{timeout}s），claude 进程已终止。"
    except FileNotFoundError:
        return "未找到 claude CLI，请确认已安装并在 PATH 中。"
    except Exception as exc:
        return f"执行异常: {exc}"


def list_trigger_words() -> list[str]:
    return list(_get_task_map().keys())
