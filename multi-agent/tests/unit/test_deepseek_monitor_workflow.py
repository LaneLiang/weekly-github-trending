"""Unit tests for DeepSeekMonitorWorkflow."""

import json
import urllib.error
from unittest.mock import MagicMock, patch

from lanes_ceo.contracts import Artifact, Job
from lanes_ceo.enums import JobStatus
from lanes_ceo.workflows.deepseek_monitor import (
    DeepSeekMonitorWorkflow,
    _fetch_balance,
)


def _make_job() -> Job:
    return Job(
        job_id="job-dsm-1",
        request_id="req-dsm-1",
        role_group="deepseek_monitor",
        actor="deepseek-monitor-actor",
        critic="deepseek-monitor-critic",
        status=JobStatus.RECEIVED,
        input={"message": "daily"},
        workspace="runtime/jobs/job-dsm-1",
    )


# ── actor tests ──


def test_actor_no_api_key() -> None:
    """Actor returns warning artifact when API key is not configured."""
    wf = DeepSeekMonitorWorkflow()
    job = _make_job()

    with patch("lanes_ceo.workflows.deepseek_monitor.Config.from_env") as mock_cfg:
        mock_cfg.return_value = MagicMock(deepseek_api_key="", deepseek_balance_threshold=10.0)
        artifact = wf.run_actor(job)

    assert artifact.artifact_type == "deepseek_monitor"
    assert "API key 未配置" in artifact.summary


def test_actor_with_balance() -> None:
    """Actor produces a balance report when API is available."""
    wf = DeepSeekMonitorWorkflow()
    job = _make_job()

    with patch("lanes_ceo.workflows.deepseek_monitor.Config.from_env") as mock_cfg:
        mock_cfg.return_value = MagicMock(deepseek_api_key="sk-test-key", deepseek_balance_threshold=10.0)
        with patch("lanes_ceo.workflows.deepseek_monitor._fetch_balance") as mock_fetch:
            mock_fetch.return_value = {
                "balance": 25.50,
                "is_available": True,
                "raw": '{"balance": 25.50}',
                "error": None,
            }
            artifact = wf.run_actor(job)

    assert artifact.artifact_type == "deepseek_monitor"
    assert "当前余额" in artifact.summary
    assert "25.50" in artifact.summary
    assert len(artifact.artifact_paths) >= 1


def test_actor_below_threshold() -> None:
    """Actor produces an alert when balance is below threshold."""
    wf = DeepSeekMonitorWorkflow()
    job = _make_job()

    with patch("lanes_ceo.workflows.deepseek_monitor.Config.from_env") as mock_cfg:
        mock_cfg.return_value = MagicMock(deepseek_api_key="sk-test-key", deepseek_balance_threshold=50.0)
        with patch("lanes_ceo.workflows.deepseek_monitor._fetch_balance") as mock_fetch:
            mock_fetch.return_value = {
                "balance": 3.20,
                "is_available": True,
                "raw": '{"balance": 3.20}',
                "error": None,
            }
            artifact = wf.run_actor(job)

    assert "低于阈值" in artifact.summary
    assert len(artifact.risks) > 0
    assert len(artifact.user_confirmations) > 0


def test_actor_fetch_error() -> None:
    """Actor returns error artifact when API call fails."""
    wf = DeepSeekMonitorWorkflow()
    job = _make_job()

    with patch("lanes_ceo.workflows.deepseek_monitor.Config.from_env") as mock_cfg:
        mock_cfg.return_value = MagicMock(deepseek_api_key="sk-test-key", deepseek_balance_threshold=10.0)
        with patch("lanes_ceo.workflows.deepseek_monitor._fetch_balance") as mock_fetch:
            mock_fetch.return_value = {
                "balance": None,
                "is_available": False,
                "raw": "",
                "error": "Connection timeout",
            }
            artifact = wf.run_actor(job)

    assert "检查失败" in artifact.summary


def test_actor_unparseable_balance() -> None:
    """Actor returns warning when balance data can't be parsed."""
    wf = DeepSeekMonitorWorkflow()
    job = _make_job()

    with patch("lanes_ceo.workflows.deepseek_monitor.Config.from_env") as mock_cfg:
        mock_cfg.return_value = MagicMock(deepseek_api_key="sk-test-key", deepseek_balance_threshold=10.0)
        with patch("lanes_ceo.workflows.deepseek_monitor._fetch_balance") as mock_fetch:
            mock_fetch.return_value = {
                "balance": None,
                "is_available": True,
                "raw": '{"unexpected_format": true}',
                "error": None,
            }
            artifact = wf.run_actor(job)

    assert "无法解析" in artifact.summary


# ── _fetch_balance tests ──


def test_fetch_balance_success() -> None:
    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps({
        "balance": 100.50,
        "is_available": True,
    }).encode("utf-8")
    mock_response.__enter__.return_value = mock_response

    with patch("urllib.request.urlopen", return_value=mock_response) as mock_urlopen:
        with patch("urllib.request.Request") as mock_req:
            mock_req.return_value = MagicMock()
            result = _fetch_balance("sk-test-key")

    assert result["balance"] == 100.50
    assert result["is_available"] is True
    assert result["error"] is None


def test_fetch_balance_data_field() -> None:
    """Test parsing with balance inside data dict."""
    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps({
        "data": {"balance": 42.00},
        "is_available": "true",
    }).encode("utf-8")
    mock_response.__enter__.return_value = mock_response

    with patch("urllib.request.urlopen", return_value=mock_response):
        with patch("urllib.request.Request") as mock_req:
            mock_req.return_value = MagicMock()
            result = _fetch_balance("sk-test-key")

    assert result["balance"] == 42.00
    assert result["is_available"] is True


def test_fetch_balance_total_balance_field() -> None:
    """Test parsing with total_balance field."""
    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps({
        "total_balance": 88.88,
        "is_available": True,
    }).encode("utf-8")
    mock_response.__enter__.return_value = mock_response

    with patch("urllib.request.urlopen", return_value=mock_response):
        with patch("urllib.request.Request") as mock_req:
            mock_req.return_value = MagicMock()
            result = _fetch_balance("sk-test-key")

    assert result["balance"] == 88.88


def test_fetch_balance_http_error() -> None:
    with patch("urllib.request.Request") as mock_req:
        mock_req.return_value = MagicMock()
        with patch("urllib.request.urlopen", side_effect=urllib.error.HTTPError(
            "https://api.deepseek.com/user/balance", 401, "Unauthorized",
            {}, None,
        )):
            result = _fetch_balance("bad-key")

    assert result["balance"] is None
    assert result["is_available"] is False
    assert "HTTP 401" in result["error"]


def test_fetch_balance_generic_error() -> None:
    with patch("urllib.request.Request") as mock_req:
        mock_req.return_value = MagicMock()
        with patch("urllib.request.urlopen", side_effect=Exception("Network unreachable")):
            result = _fetch_balance("sk-test-key")

    assert result["balance"] is None
    assert result["error"] == "Network unreachable"


# ── critic tests ──


def test_critic_approves_valid_balance_report() -> None:
    wf = DeepSeekMonitorWorkflow()
    job = _make_job()
    artifact = Artifact(
        artifact_id="art-dsm-1",
        job_id=job.job_id,
        artifact_type="deepseek_monitor",
        summary=(
            "# DeepSeek 余额报告 — 2026-05-23\n\n"
            "- **当前余额**: ¥25.50\n"
            "- **告警阈值**: ¥10.00\n"
            "- **API 可用**: 是\n"
            "- **状态**: 正常"
        ),
        artifact_paths=["/tmp/deepseek-balance-20260523.md"],
        sources=["deepseek-api"],
        risks=[],
        user_confirmations=[],
    )
    review = wf.run_critic(job, artifact)
    assert review.approved is True


def test_critic_approves_no_api_key() -> None:
    """Critic accepts artifact when API key is intentionally absent."""
    wf = DeepSeekMonitorWorkflow()
    job = _make_job()
    artifact = Artifact(
        artifact_id="art-dsm-2",
        job_id=job.job_id,
        artifact_type="deepseek_monitor",
        summary="DeepSeek API key 未配置，跳过余额检查。\n请在 .env 中设置 LANES_CEO_DEEPSEEK_API_KEY。",
        artifact_paths=[],
        sources=[],
        risks=[],
        user_confirmations=[],
    )
    review = wf.run_critic(job, artifact)
    assert review.approved is True


def test_critic_flags_api_failure() -> None:
    wf = DeepSeekMonitorWorkflow()
    job = _make_job()
    artifact = Artifact(
        artifact_id="art-dsm-3",
        job_id=job.job_id,
        artifact_type="deepseek_monitor",
        summary="# DeepSeek 余额检查失败 — 2026-05-23\n\n错误: Connection timeout",
        artifact_paths=[],
        sources=["deepseek-api"],
        risks=[],
        user_confirmations=[],
    )
    review = wf.run_critic(job, artifact)
    assert review.approved is False


def test_critic_flags_unparseable_response() -> None:
    wf = DeepSeekMonitorWorkflow()
    job = _make_job()
    artifact = Artifact(
        artifact_id="art-dsm-4",
        job_id=job.job_id,
        artifact_type="deepseek_monitor",
        summary="# DeepSeek 余额查询 — 2026-05-23\n\n余额数据无法解析",
        artifact_paths=[],
        sources=["deepseek-api"],
        risks=[],
        user_confirmations=[],
    )
    review = wf.run_critic(job, artifact)
    assert review.approved is False


def test_critic_flags_missing_file_for_balance_report() -> None:
    """Critic should flag when balance report exists but has no saved file."""
    wf = DeepSeekMonitorWorkflow()
    job = _make_job()
    artifact = Artifact(
        artifact_id="art-dsm-5",
        job_id=job.job_id,
        artifact_type="deepseek_monitor",
        summary="- **当前余额**: ¥25.50\n- **API 可用**: 是\n- **状态**: 正常",
        artifact_paths=[],  # missing file
        sources=["deepseek-api"],
        risks=[],
        user_confirmations=[],
    )
    review = wf.run_critic(job, artifact)
    assert review.approved is False


def test_critic_flags_threshold_mismatch() -> None:
    """Critic should flag when '低于阈值' is in summary but risks is empty."""
    wf = DeepSeekMonitorWorkflow()
    job = _make_job()
    artifact = Artifact(
        artifact_id="art-dsm-6",
        job_id=job.job_id,
        artifact_type="deepseek_monitor",
        summary="- **当前余额**: ¥3.20\n- **低于阈值**\n- **API 可用**: 是",
        artifact_paths=["/tmp/balance.md"],
        sources=["deepseek-api"],
        risks=[],  # should have risk entries
        user_confirmations=[],
    )
    review = wf.run_critic(job, artifact)
    assert review.approved is False
