"""Integration tests for the full Orchestrator pipeline with UpdateCheckerWorkflow.

These tests exercise the real Orchestrator.handle() → actor → critic → notification
flow using UpdateCheckerWorkflow, with all external calls (subprocess, LLM, filesystem)
mocked so the tests are fast and deterministic.
"""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from lanes_ceo.contracts import CriticReview, TaskRequest
from lanes_ceo.enums import JobStatus, SourceChannel
from lanes_ceo.notifications.outbox import NotificationOutbox
from lanes_ceo.orchestrator import DuplicateRequestError, Orchestrator
from lanes_ceo.storage.sqlite_store import SQLiteStore
from lanes_ceo.workflows.registry import WorkflowRegistry
from lanes_ceo.workflows.update_checker import UpdateCheckerWorkflow

# ---------------------------------------------------------------------------
# Shared test helpers
# ---------------------------------------------------------------------------

# Must be >= 60 characters — UpdateCheckerWorkflow critic rejects summaries < 60 chars.
LLM_CHAT_RETURN = (
    "所有工具已是最新版本，无需更新。"
    "本次检查覆盖了Claude Code CLI、GitHub CLI、pip包、npm包、"
    "MCP服务器配置以及本地Git仓库状态，"
    "未发现任何需要关注的安全漏洞或重要功能更新。"
)


def _make_fake_subprocess_run():
    """Return a fake ``subprocess.run`` side-effect function.

    Handles every subprocess call made by UpdateCheckerWorkflow's check helpers:
    _check_claude_cli, _check_gh_cli, _check_pip_outdated, _check_npm_outdated,
    and _check_git_repos.
    """

    def fake_run(args, **kwargs):
        result = MagicMock()
        result.returncode = 0
        result.stderr = ""
        cmd_str = " ".join(args) if isinstance(args, list) else str(args)

        if "gh" in cmd_str and "--version" in cmd_str:
            result.stdout = "gh version 2.63.0 (2025-03-25)"
        elif "--version" in cmd_str:
            result.stdout = "1.0.0"
        elif "npm" in cmd_str and "view" in cmd_str and "version" in cmd_str:
            result.stdout = "1.0.0"
        elif "npm" in cmd_str and "list" in cmd_str:
            result.stdout = '{"dependencies": {}}'
        elif "pip" in cmd_str and "list" in cmd_str:
            result.stdout = "[]"
        elif "git" in cmd_str and "remote" in cmd_str and "update" in cmd_str:
            result.stdout = ""
        elif "git" in cmd_str and "status" in cmd_str:
            result.stdout = "## main...origin/main"
        else:
            result.stdout = ""
        return result

    return fake_run


_USE_DEFAULT = object()


@contextmanager
def _mock_update_checker_env(tmp_path: Path, llm_chat_return=_USE_DEFAULT):
    """Context manager that mocks all external dependencies of UpdateCheckerWorkflow.

    Parameters:
        tmp_path: Temp directory to use as the artifact directory.
        llm_chat_return: Value returned by llm_chat(). Defaults to LLM_CHAT_RETURN.
            Pass None explicitly to simulate LLM unavailable.
    """
    if llm_chat_return is _USE_DEFAULT:
        llm_chat_return = LLM_CHAT_RETURN
    with patch("subprocess.run", side_effect=_make_fake_subprocess_run()):
        with patch(
            "lanes_ceo.workflows.update_checker.llm_chat",
            return_value=llm_chat_return,
        ):
            with patch(
                "lanes_ceo.workflows.update_checker.get_artifact_dir",
                return_value=Path(tmp_path),
            ):
                with patch(
                    "lanes_ceo.workflows.update_checker._check_mcp_servers",
                    return_value=[],
                ):
                    yield


# ---------------------------------------------------------------------------
# Test 1 — Full pipeline with UpdateCheckerWorkflow (success)
# ---------------------------------------------------------------------------


def test_full_pipeline_update_checker_success(tmp_path: Path) -> None:
    """A complete handle() call with UpdateCheckerWorkflow should reach NOTIFIED."""
    store = SQLiteStore(tmp_path / "lanes.sqlite3")
    store.initialize()
    orchestrator = Orchestrator(store, WorkflowRegistry(), NotificationOutbox(store))

    request = TaskRequest(
        request_id="req-int-1",
        source_channel=SourceChannel.CLI,
        sender="lane",
        raw_message="check for outdated tools",
        task_intent="update_checker",
        priority="normal",
    )

    with _mock_update_checker_env(tmp_path):
        job, artifact = orchestrator.handle(request, "update_checker")

    assert job.status is JobStatus.NOTIFIED
    assert artifact is not None
    assert artifact.artifact_type == "update_check"
    assert len(artifact.artifact_paths) == 2
    assert len(artifact.sources) == 5

    notifications = store.list_notifications(job.job_id)
    assert len(notifications) >= 1
    assert notifications[0].payload["status"] == "approved"


# ---------------------------------------------------------------------------
# Test 2 — Critic rejection returns job to actor
# ---------------------------------------------------------------------------


class _RejectingUpdateCheckerWorkflow(UpdateCheckerWorkflow):
    """A variant whose critic always rejects."""

    def run_critic(self, job, artifact):
        return CriticReview(
            review_id=f"review-{job.job_id}",
            job_id=job.job_id,
            review_result="rejected",
            score=50,
            issues=["summary too short", "missing paths"],
            approved=False,
            return_to_actor=True,
            handoff_note="redo the check",
        )


def test_critic_rejection_returns_to_actor(tmp_path: Path) -> None:
    """When the critic rejects, the job should be RETURNED_TO_ACTOR with no notification."""
    store = SQLiteStore(tmp_path / "lanes.sqlite3")
    store.initialize()

    registry = WorkflowRegistry()
    registry.register("update_checker", _RejectingUpdateCheckerWorkflow())

    orchestrator = Orchestrator(store, registry, NotificationOutbox(store))

    request = TaskRequest(
        request_id="req-reject-1",
        source_channel=SourceChannel.CLI,
        sender="lane",
        raw_message="check tools",
        task_intent="update_checker",
        priority="normal",
    )

    with _mock_update_checker_env(tmp_path):
        job, artifact = orchestrator.handle(request, "update_checker")

    assert job.status is JobStatus.RETURNED_TO_ACTOR
    assert artifact is not None
    assert store.list_notifications(job.job_id) == []


# ---------------------------------------------------------------------------
# Test 3 — Retry exhaustion when the actor always raises
# ---------------------------------------------------------------------------


class _AlwaysFailingWorkflow:
    """Minimal workflow whose run_actor always raises (used for retry-exhaustion testing).

    The critic is never reached because the actor always fails.
    """

    role_group = "failing"
    actor_name = "failing-actor"
    critic_name = "failing-critic"

    def run_actor(self, job):
        raise RuntimeError("simulated failure")

    def run_critic(self, job, artifact):
        raise NotImplementedError("critic should never be reached — actor always fails")


def test_orchestrator_retry_exhausted(tmp_path: Path) -> None:
    """After MAX_RETRIES (3) failures the job should be FAILED with the last error."""
    store = SQLiteStore(tmp_path / "lanes.sqlite3")
    store.initialize()

    registry = WorkflowRegistry()
    registry.register("failing", _AlwaysFailingWorkflow())

    orchestrator = Orchestrator(store, registry, NotificationOutbox(store))

    request = TaskRequest(
        request_id="req-fail-1",
        source_channel=SourceChannel.CLI,
        sender="lane",
        raw_message="test",
        task_intent="failing",
        priority="normal",
    )

    with patch("time.sleep", return_value=None):
        job, artifact = orchestrator.handle(request, "failing")

    assert job.status is JobStatus.FAILED
    assert artifact is None
    assert job.retry_count == 3
    assert "simulated failure" in (job.failure_reason or "")


# ---------------------------------------------------------------------------
# Test 4 — Idempotency key prevents duplicate (with UpdateCheckerWorkflow)
# ---------------------------------------------------------------------------


def test_idempotency_key_prevents_duplicate_update_checker(tmp_path: Path) -> None:
    """A second request with the same idempotency key must raise DuplicateRequestError."""
    store = SQLiteStore(tmp_path / "lanes.sqlite3")
    store.initialize()
    orchestrator = Orchestrator(store, WorkflowRegistry(), NotificationOutbox(store))

    request = TaskRequest(
        request_id="req-idem-uc-1",
        source_channel=SourceChannel.SCHEDULER,
        sender="scheduler",
        raw_message="daily update check",
        task_intent="update_checker",
        priority="normal",
        idempotency_key="update-check-20260523-0700",
    )

    with _mock_update_checker_env(tmp_path):
        job1, _ = orchestrator.handle(request, "update_checker")

    assert job1.status is JobStatus.NOTIFIED

    duplicate = TaskRequest(
        request_id="req-idem-uc-2",
        source_channel=SourceChannel.SCHEDULER,
        sender="scheduler",
        raw_message="daily update check",
        task_intent="update_checker",
        priority="normal",
        idempotency_key="update-check-20260523-0700",
    )

    with pytest.raises(DuplicateRequestError):
        orchestrator.handle(duplicate, "update_checker")


# ---------------------------------------------------------------------------
# Test 5 — Scheduler-generated idempotency key is persisted
# ---------------------------------------------------------------------------


def test_full_pipeline_scheduler_with_idempotency_key(tmp_path: Path) -> None:
    """A scheduler-triggered request persists its idempotency key."""
    store = SQLiteStore(tmp_path / "lanes.sqlite3")
    store.initialize()
    orchestrator = Orchestrator(store, WorkflowRegistry(), NotificationOutbox(store))

    idem_key = "update_checker-2026-05-23-07"
    request = TaskRequest(
        request_id="req-sched-1",
        source_channel=SourceChannel.SCHEDULER,
        sender="scheduler",
        raw_message="scheduled update check",
        task_intent="update_checker",
        priority="normal",
        idempotency_key=idem_key,
    )

    with _mock_update_checker_env(tmp_path):
        job, artifact = orchestrator.handle(request, "update_checker")

    assert job.status is JobStatus.NOTIFIED
    assert artifact is not None
    assert store.has_idempotency_key(idem_key) is True


# ---------------------------------------------------------------------------
# Test 6 — llm_chat returns None (LLM unavailable fallback)
# ---------------------------------------------------------------------------


def test_full_pipeline_llm_unavailable_fallback(tmp_path: Path) -> None:
    """When llm_chat returns None, the pipeline succeeds using raw_report as summary."""
    store = SQLiteStore(tmp_path / "lanes.sqlite3")
    store.initialize()
    orchestrator = Orchestrator(store, WorkflowRegistry(), NotificationOutbox(store))

    request = TaskRequest(
        request_id="req-llm-none-1",
        source_channel=SourceChannel.CLI,
        sender="lane",
        raw_message="check tools",
        task_intent="update_checker",
        priority="normal",
    )

    # Use _mock_update_checker_env with llm_chat_return explicitly set to None
    # to simulate the LLM API being unavailable.
    with _mock_update_checker_env(tmp_path, llm_chat_return=None):
        job, artifact = orchestrator.handle(request, "update_checker")

    assert job.status is JobStatus.NOTIFIED
    assert artifact is not None
    assert "工具更新检查报告" in artifact.summary
    assert len(artifact.summary) >= 60


# ---------------------------------------------------------------------------
# Test 7 — Tool not installed (FileNotFoundError) handled gracefully
# ---------------------------------------------------------------------------


def test_full_pipeline_tool_not_installed_graceful(tmp_path: Path) -> None:
    """Pipeline handles missing tools (FileNotFoundError) gracefully."""
    store = SQLiteStore(tmp_path / "lanes.sqlite3")
    store.initialize()
    orchestrator = Orchestrator(store, WorkflowRegistry(), NotificationOutbox(store))

    request = TaskRequest(
        request_id="req-missing-tool-1",
        source_channel=SourceChannel.CLI,
        sender="lane",
        raw_message="check tools",
        task_intent="update_checker",
        priority="normal",
    )

    def fake_run_with_missing(args, **kwargs):
        cmd_str = " ".join(args) if isinstance(args, list) else str(args)
        if "claude" in cmd_str and "--version" in cmd_str:
            raise FileNotFoundError("claude not found")
        return _make_fake_subprocess_run()(args, **kwargs)

    with patch("subprocess.run", side_effect=fake_run_with_missing):
        with patch(
            "lanes_ceo.workflows.update_checker.llm_chat",
            return_value=LLM_CHAT_RETURN,
        ):
            with patch(
                "lanes_ceo.workflows.update_checker.get_artifact_dir",
                return_value=Path(tmp_path),
            ):
                with patch(
                    "lanes_ceo.workflows.update_checker._check_mcp_servers",
                    return_value=[],
                ):
                    job, artifact = orchestrator.handle(request, "update_checker")

    assert job.status is JobStatus.NOTIFIED
    # "未安装" appears in the raw report (not the LLM-generated summary).
    raw_report_path = Path(artifact.artifact_paths[0])
    assert raw_report_path.exists()
    assert "未安装" in raw_report_path.read_text(encoding="utf-8")
