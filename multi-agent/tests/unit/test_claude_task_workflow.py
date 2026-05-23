"""Unit tests for ClaudeTaskWorkflow."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from lanes_ceo.contracts import Job
from lanes_ceo.enums import JobStatus
from lanes_ceo.workflows.claude_task import (
    ClaudeTaskWorkflow,
    _match_task,
    get_recent_results,
    list_trigger_words,
    load_task_map,
    get_allowed_users,
    pop_result,
    _store_result,
)


def _make_job(message: str) -> Job:
    return Job(
        job_id="job-ct-1",
        request_id="req-ct-1",
        role_group="claude_task",
        actor="claude-task-actor",
        critic="claude-task-critic",
        status=JobStatus.RECEIVED,
        input={"message": message},
        workspace="runtime/jobs/job-ct-1",
    )


# ── actor tests ──


def test_actor_matches_known_task() -> None:
    wf = ClaudeTaskWorkflow()
    with patch(
        "lanes_ceo.workflows.claude_task._run_claude",
        return_value="74 passed, 0 failed",
    ):
        artifact = wf.run_actor(_make_job("跑测试"))
    assert artifact.artifact_type == "claude_task"
    assert "74 passed" in artifact.summary
    assert "运行测试" in artifact.summary


def test_actor_returns_help_for_unknown_trigger() -> None:
    wf = ClaudeTaskWorkflow()
    artifact = wf.run_actor(_make_job("不存在的任务xyz"))
    assert "未匹配到已知任务" in artifact.summary


def test_actor_does_not_call_claude_for_unknown() -> None:
    wf = ClaudeTaskWorkflow()
    artifact = wf.run_actor(_make_job("今天天气怎么样"))
    assert "未匹配到已知任务" in artifact.summary
    assert "测试" in artifact.summary  # includes available trigger words


# ── critic tests ──


def test_critic_approves_valid_output() -> None:
    wf = ClaudeTaskWorkflow()
    job = _make_job("测试")
    from lanes_ceo.contracts import Artifact

    artifact = Artifact(
        artifact_id="art-1",
        job_id=job.job_id,
        artifact_type="claude_task",
        summary="【运行测试套件并分析失败原因】\n\n74 passed, 0 failed",
        artifact_paths=[],
        sources=["claude-cli"],
        risks=[],
        user_confirmations=[],
    )
    review = wf.run_critic(job, artifact)
    assert review.approved is True
    assert review.score >= 80


def test_critic_flags_unknown_trigger() -> None:
    wf = ClaudeTaskWorkflow()
    job = _make_job("xyz")
    from lanes_ceo.contracts import Artifact

    artifact = Artifact(
        artifact_id="art-2",
        job_id=job.job_id,
        artifact_type="claude_task",
        summary="未匹配到已知任务。可用的触发词：测试、跑测试",
        artifact_paths=[],
        sources=[],
        risks=[],
        user_confirmations=[],
    )
    review = wf.run_critic(job, artifact)
    assert review.approved is False
    assert any("未匹配到已知任务" in i for i in review.issues)


def test_critic_flags_short_output() -> None:
    wf = ClaudeTaskWorkflow()
    job = _make_job("测试")
    from lanes_ceo.contracts import Artifact

    artifact = Artifact(
        artifact_id="art-3",
        job_id=job.job_id,
        artifact_type="claude_task",
        summary="hi",
        artifact_paths=[],
        sources=[],
        risks=[],
        user_confirmations=[],
    )
    review = wf.run_critic(job, artifact)
    assert review.approved is False


# ── task matching ──


def test_match_task_finds_trigger() -> None:
    task_map = load_task_map()
    result = _match_task("请帮我跑测试", task_map)
    assert result is not None
    assert result["trigger"] == "跑测试"


def test_match_task_returns_none_for_no_match() -> None:
    task_map = load_task_map()
    result = _match_task("今天吃什么", task_map)
    assert result is None


def test_match_task_longest_wins() -> None:
    """Longer triggers should match before shorter substrings."""
    task_map = {"测试": {"prompt": "p1", "description": "d1", "timeout": 1},
                "跑测试": {"prompt": "p2", "description": "d2", "timeout": 2}}
    result = _match_task("跑测试和测试一起", task_map)
    assert result["trigger"] == "跑测试"  # longest match wins


# ── config loading ──


def test_load_task_map_returns_dict() -> None:
    tasks = load_task_map()
    assert isinstance(tasks, dict)
    assert len(tasks) >= 2
    for cfg in tasks.values():
        assert "prompt" in cfg
        assert "description" in cfg
        assert "timeout" in cfg


def test_load_task_map_has_expected_triggers() -> None:
    tasks = load_task_map()
    triggers = list(tasks.keys())
    assert "测试" in triggers
    assert "提交" in triggers
    assert "项目状态" in triggers


def test_list_trigger_words() -> None:
    triggers = list_trigger_words()
    assert len(triggers) >= 2
    assert "测试" in triggers


def test_default_fallback_on_missing_file() -> None:
    tasks = load_task_map(Path("/nonexistent/path.yaml"))
    assert len(tasks) >= 2
    assert "测试" in tasks


# ── permission check ──


def test_allowed_users_defaults_to_empty() -> None:
    allowed = get_allowed_users()
    assert allowed == []


def test_allowed_users_from_nonexistent_file() -> None:
    allowed = get_allowed_users(Path("/nonexistent/path.yaml"))
    assert allowed == []


# ── result storage and history ──


def test_store_and_pop_result() -> None:
    _store_result("job-1", "summary text", "test task")
    result = pop_result("job-1")
    assert result is not None
    assert result["summary"] == "summary text"
    assert result["description"] == "test task"


def test_pop_nonexistent_returns_none() -> None:
    assert pop_result("nonexistent-id") is None


def test_get_recent_results_empty() -> None:
    results = get_recent_results(5)
    # May have results from other tests; just check it's a list
    assert isinstance(results, list)


def test_get_recent_results_returns_list_of_dicts() -> None:
    _store_result("job-a", "summary a", "desc a")
    _store_result("job-b", "summary b", "desc b")
    results = get_recent_results(3)
    assert isinstance(results, list)
    # Each result should have expected keys
    for r in results:
        assert "summary" in r
        assert "description" in r
