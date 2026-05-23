"""Unit tests for UpdateCheckerWorkflow."""

from unittest.mock import MagicMock, patch

from lanes_ceo.contracts import Artifact, Job
from lanes_ceo.enums import JobStatus
from lanes_ceo.workflows.update_checker import (
    UpdateCheckerWorkflow,
    _check_claude_cli,
    _check_gh_cli,
    _check_pip_outdated,
)


def _make_job() -> Job:
    return Job(
        job_id="job-uc-1",
        request_id="req-uc-1",
        role_group="update_checker",
        actor="update-checker-actor",
        critic="update-checker-critic",
        status=JobStatus.RECEIVED,
        input={"message": "daily"},
        workspace="runtime/jobs/job-uc-1",
    )


# ── actor tests ──


def test_actor_produces_artifact() -> None:
    """Actor produces an update_check artifact even when CLI tools are missing."""
    wf = UpdateCheckerWorkflow()
    job = _make_job()
    with patch("lanes_ceo.workflows.update_checker.subprocess.run") as mock_run:
        # Make all subprocess calls return empty/error to exercise all paths
        mock_run.side_effect = FileNotFoundError("tool not found")
        artifact = wf.run_actor(job)

    assert artifact.artifact_type == "update_check"
    assert len(artifact.artifact_paths) >= 2
    assert len(artifact.summary) > 10


def test_actor_produces_rich_summary() -> None:
    """Actor summary should contain version/status information."""
    wf = UpdateCheckerWorkflow()
    job = _make_job()
    with patch("lanes_ceo.workflows.update_checker.subprocess.run") as mock_run:
        mock_run.side_effect = FileNotFoundError("tool not found")
        artifact = wf.run_actor(job)

    assert "Claude" in artifact.summary or "GitHub" in artifact.summary or "工具" in artifact.summary


# ── critic tests ──


def test_critic_approves_rich_content() -> None:
    wf = UpdateCheckerWorkflow()
    job = _make_job()
    artifact = Artifact(
        artifact_id="art-uc-1",
        job_id=job.job_id,
        artifact_type="update_check",
        summary=(
            "工具更新检查报告：Claude Code CLI 当前版本 v2.3.0 需要更新到 v2.4.0，"
            "GitHub CLI 已是最新版本，pip 包中 openai 和 python-docx 有可用更新，"
            "建议尽快更新 CLI 工具以获取最新功能和安全补丁。"
        ),
        artifact_paths=["/tmp/report.md", "/tmp/summary.md"],
        sources=["cli-scan", "pip", "npm", "git"],
        risks=["版本号仅做参考"],
        user_confirmations=[],
    )
    review = wf.run_critic(job, artifact)
    assert review.approved is True
    assert review.score >= 80


def test_critic_rejects_short_content() -> None:
    wf = UpdateCheckerWorkflow()
    job = _make_job()
    artifact = Artifact(
        artifact_id="art-uc-2",
        job_id=job.job_id,
        artifact_type="update_check",
        summary="short",
        artifact_paths=[],
        sources=["cli-scan"],
        risks=[],
        user_confirmations=[],
    )
    review = wf.run_critic(job, artifact)
    assert review.approved is False


def test_critic_rejects_missing_paths() -> None:
    wf = UpdateCheckerWorkflow()
    job = _make_job()
    artifact = Artifact(
        artifact_id="art-uc-3",
        job_id=job.job_id,
        artifact_type="update_check",
        summary="工具更新检查已完成，所有工具均为最新版本，无需任何更新操作。",
        artifact_paths=["/tmp/report.md"],  # only 1, critic wants >=2
        sources=["cli-scan", "pip", "npm"],
        risks=[],
        user_confirmations=[],
    )
    review = wf.run_critic(job, artifact)
    assert review.approved is False


def test_critic_rejects_few_sources() -> None:
    wf = UpdateCheckerWorkflow()
    job = _make_job()
    artifact = Artifact(
        artifact_id="art-uc-4",
        job_id=job.job_id,
        artifact_type="update_check",
        summary="本周工具扫描报告：Claude Code CLI最新版本已确认，pip包全部最新。",
        artifact_paths=["/tmp/report.md", "/tmp/summary.md"],
        sources=["cli-scan", "pip"],  # only 2, critic wants >=3
        risks=[],
        user_confirmations=[],
    )
    review = wf.run_critic(job, artifact)
    assert review.approved is False


# ── _check_claude_cli tests ──


def test_check_claude_cli_returns_version() -> None:
    with patch("lanes_ceo.workflows.update_checker.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(stdout="claude v2.3.0\n", stderr="", returncode=0)
        result = _check_claude_cli()
    assert result["tool"] == "Claude Code CLI"
    assert "v2.3.0" in result["current"]


def test_check_claude_cli_not_installed() -> None:
    with patch("lanes_ceo.workflows.update_checker.subprocess.run", side_effect=FileNotFoundError):
        result = _check_claude_cli()
    assert result["current"] == "未安装"


# ── _check_gh_cli tests ──


def test_check_gh_cli_returns_version() -> None:
    with patch("lanes_ceo.workflows.update_checker.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(
            stdout="gh version 2.63.0 (2025-03-25)\nhttps://github.com/cli/cli/releases/tag/v2.63.0\n",
            stderr="",
            returncode=0,
        )
        result = _check_gh_cli()
    assert result["tool"] == "GitHub CLI (gh)"
    assert "2.63.0" in result["current"]


def test_check_gh_cli_not_installed() -> None:
    with patch("lanes_ceo.workflows.update_checker.subprocess.run", side_effect=FileNotFoundError):
        result = _check_gh_cli()
    assert result["current"] == "未安装"


# ── _check_pip_outdated tests ──


def test_check_pip_outdated_with_updates() -> None:
    with patch("lanes_ceo.workflows.update_checker.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(
            stdout='[{"name": "openai", "version": "1.5.0", "latest_version": "1.6.0"}, '
            '{"name": "pip", "version": "23.0", "latest_version": "24.0"}, '
            '{"name": "requests", "version": "2.28.0", "latest_version": "2.31.0"}]',
            stderr="",
            returncode=0,
        )
        result = _check_pip_outdated()
    # openai and pip are in the relevant set; requests is not
    names = {p["name"] for p in result}
    assert "openai" in names
    assert "pip" in names
    assert "requests" not in names


def test_check_pip_outdated_empty() -> None:
    with patch("lanes_ceo.workflows.update_checker.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(stdout="[]", stderr="", returncode=0)
        result = _check_pip_outdated()
    assert result == []


def test_check_pip_outdated_not_installed() -> None:
    with patch("lanes_ceo.workflows.update_checker.subprocess.run", side_effect=FileNotFoundError):
        result = _check_pip_outdated()
    assert result == []


def test_check_pip_outdated_invalid_json() -> None:
    with patch("lanes_ceo.workflows.update_checker.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(stdout="not json", stderr="", returncode=0)
        result = _check_pip_outdated()
    assert result == []
