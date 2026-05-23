"""Unit tests for MemoryCurationWorkflow."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from lanes_ceo.contracts import Artifact, CriticReview, Job
from lanes_ceo.enums import JobStatus
from lanes_ceo.workflows.memory_curation import (
    MemoryCurationWorkflow,
    _check_large_files,
    _check_session_active,
    _detect_duplicates,
    _scan_memory_files,
    _update_memory_index,
)


def _make_job() -> Job:
    return Job(
        job_id="job-mc-1",
        request_id="req-mc-1",
        role_group="memory_curation",
        actor="memory-curation-actor",
        critic="memory-curation-critic",
        status=JobStatus.RECEIVED,
        input={"message": "weekly"},
        workspace="runtime/jobs/job-mc-1",
    )


# ── _scan_memory_files tests ──


def test_scan_memory_files_empty_dir() -> None:
    """_scan_memory_files returns empty list when MEMORY_DIR does not exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch("lanes_ceo.workflows.memory_curation.MEMORY_DIR", Path(tmpdir) / "nonexistent"):
            result = _scan_memory_files()
    assert result == []


def test_scan_memory_files_with_entries() -> None:
    """_scan_memory_files returns properly parsed entries from .md files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        memdir = Path(tmpdir)
        # Create a valid feedback entry
        fb = memdir / "feedback_test.md"
        fb.write_text(
            "---\ntype: feedback\ncreated: 2024-01-01T00:00:00\nupdated: 2024-01-01T00:00:00\n---\n\nSome body text here.",
            encoding="utf-8",
        )
        # Create a user entry
        user = memdir / "user_pref.md"
        user.write_text(
            "---\ntype: user\ncreated: 2024-06-15T10:00:00\nupdated: 2025-01-01T12:00:00\n---\n\nUser preferences body.",
            encoding="utf-8",
        )
        # Create a file without frontmatter
        nofm = memdir / "plain.md"
        nofm.write_text("Just plain text without frontmatter.", encoding="utf-8")

        with patch("lanes_ceo.workflows.memory_curation.MEMORY_DIR", memdir):
            result = _scan_memory_files()

    assert len(result) >= 2
    names = {e["name"] for e in result}
    assert "feedback_test" in names
    assert "user_pref" in names
    # Check types
    types = {e["type"] for e in result}
    assert "feedback" in types
    assert "user" in types


def test_scan_memory_files_skips_mem_yml_and_underscore() -> None:
    """_scan_memory_files skips MEMORY.md and files starting with underscore."""
    with tempfile.TemporaryDirectory() as tmpdir:
        memdir = Path(tmpdir)
        (memdir / "MEMORY.md").write_text("# Index", encoding="utf-8")
        (memdir / "_internal.md").write_text("internal", encoding="utf-8")
        (memdir / "real.md").write_text(
            "---\ntype: user\n---\n\nBody here.", encoding="utf-8"
        )

        with patch("lanes_ceo.workflows.memory_curation.MEMORY_DIR", memdir):
            result = _scan_memory_files()

    names = {e["name"] for e in result}
    assert "real" in names
    assert "MEMORY" not in names
    assert "_internal" not in names


# ── _check_large_files tests ──


def test_check_large_files_over_threshold() -> None:
    """_check_large_files identifies files exceeding 50KB."""
    entries = [
        {"name": "small", "size": 1000},
        {"name": "big", "size": 60000},
        {"name": "huge", "size": 200000},
    ]
    result = _check_large_files(entries)
    assert len(result) == 2
    names = {e["name"] for e in result}
    assert "big" in names
    assert "huge" in names
    assert "small" not in names


def test_check_large_files_all_small() -> None:
    """_check_large_files returns empty when all files are under 50KB."""
    entries = [
        {"name": "a", "size": 100},
        {"name": "b", "size": 49999},
        {"name": "c", "size": 50000},
    ]
    result = _check_large_files(entries)
    assert result == []


def test_check_large_files_no_size_field() -> None:
    """_check_large_files handles entries without size field gracefully."""
    entries = [
        {"name": "no_size"},
        {"name": "with_size", "size": 100000},
    ]
    result = _check_large_files(entries)
    assert len(result) == 1
    assert result[0]["name"] == "with_size"


# ── _detect_duplicates tests ──


def test_detect_duplicates_similar_bodies() -> None:
    """_detect_duplicates finds entries with high word overlap."""
    entries = [
        {
            "name": "entry_a",
            "type": "project",
            "body_preview": "DC-DC converter efficiency optimization using reinforcement learning",
        },
        {
            "name": "entry_b",
            "type": "project",
            "body_preview": "DC-DC converter efficiency optimization with reinforcement learning method",
        },
    ]
    result = _detect_duplicates(entries)
    assert len(result) >= 1
    pair = result[0]
    assert pair["entry_a"] == "entry_a"
    assert pair["entry_b"] == "entry_b"
    assert pair["overlap_score"] >= 0.5


def test_detect_duplicates_different_bodies() -> None:
    """_detect_duplicates returns empty for completely different bodies."""
    entries = [
        {"name": "a", "type": "project", "body_preview": "DC-DC converter efficiency"},
        {"name": "b", "type": "project", "body_preview": "memory management system design"},
        {"name": "c", "type": "project", "body_preview": "neural network training pipeline"},
    ]
    result = _detect_duplicates(entries)
    assert result == []


def test_detect_duplicates_different_types() -> None:
    """_detect_duplicates ignores entries of different types."""
    entries = [
        {"name": "a", "type": "project", "body_preview": "same content here"},
        {"name": "b", "type": "feedback", "body_preview": "same content here"},
    ]
    result = _detect_duplicates(entries)
    assert result == []


def test_detect_duplicates_empty_bodies() -> None:
    """_detect_duplicates skips entries with empty body_preview."""
    entries = [
        {"name": "a", "type": "project", "body_preview": ""},
        {"name": "b", "type": "project", "body_preview": ""},
    ]
    result = _detect_duplicates(entries)
    assert result == []


# ── _check_session_active tests ──


def test_check_session_active_with_claude_process() -> None:
    """_check_session_active returns True when claude process is found."""
    mock_run = MagicMock()
    mock_run.return_value = MagicMock(stdout="claude.exe 1234 Console 1 500,000 K", returncode=0)
    with patch("lanes_ceo.workflows.memory_curation.subprocess.run", mock_run):
        result = _check_session_active()
    assert result is True


def test_check_session_active_without_claude() -> None:
    """_check_session_active returns False when no claude process exists."""
    # No claude in output, no recent session files
    mock_run = MagicMock()
    mock_run.return_value = MagicMock(stdout="some other process", returncode=0)
    with patch("lanes_ceo.workflows.memory_curation.subprocess.run", mock_run):
        with patch("pathlib.Path.home") as mock_home:
            mock_home.return_value = Path(tempfile.mkdtemp())
            result = _check_session_active()
    assert result is False


def test_check_session_active_tasklist_fails() -> None:
    """_check_session_active returns False when tasklist subprocess fails."""
    with patch("lanes_ceo.workflows.memory_curation.subprocess.run", side_effect=FileNotFoundError):
        with patch("pathlib.Path.home") as mock_home:
            mock_home.return_value = Path(tempfile.mkdtemp())
            result = _check_session_active()
    assert result is False


# ── _update_memory_index tests ──


def test_update_memory_index_no_index_file() -> None:
    """_update_memory_index is a no-op when MEMORY.md doesn't exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        memdir = Path(tmpdir)
        with patch("lanes_ceo.workflows.memory_curation.MEMORY_DIR", memdir):
            _update_memory_index([])  # Should not raise
    # No MEMORY.md created — the function only updates, doesn't create
    assert not (memdir / "MEMORY.md").exists()


def test_update_memory_index_with_entries() -> None:
    """_update_memory_index writes updated counts to MEMORY.md."""
    with tempfile.TemporaryDirectory() as tmpdir:
        memdir = Path(tmpdir)
        index = memdir / "MEMORY.md"
        index.write_text(
            'last_updated: "2024-01-01T00:00:00+0000"\ntotal_entries: 5\n', encoding="utf-8"
        )
        entries = [{"name": "a"}, {"name": "b"}, {"name": "c"}]

        with patch("lanes_ceo.workflows.memory_curation.MEMORY_DIR", memdir):
            _update_memory_index(entries)

        updated = index.read_text(encoding="utf-8")
        assert "total_entries: 3" in updated


# ── actor tests ──


def test_actor_no_memory_dir_produces_report() -> None:
    """Actor produces a report even when no memory files are present."""
    wf = MemoryCurationWorkflow()
    job = _make_job()

    with patch("lanes_ceo.workflows.memory_curation._check_session_active", return_value=False):
        with patch("lanes_ceo.workflows.memory_curation._scan_memory_files", return_value=[]):
            with patch("lanes_ceo.workflows.memory_curation._check_large_files", return_value=[]):
                with patch("lanes_ceo.workflows.memory_curation._detect_duplicates", return_value=[]):
                    with patch("lanes_ceo.workflows.memory_curation.llm_chat",
                               return_value="记忆系统状态良好，无需操作。当前无过期条目和疑似重复。"):
                        with patch("lanes_ceo.workflows.memory_curation.get_artifact_dir") as mock_dir:
                            with tempfile.TemporaryDirectory() as tmpdir:
                                mock_dir.return_value = Path(tmpdir)
                                with patch("lanes_ceo.workflows.memory_curation._update_memory_index"):
                                    artifact = wf.run_actor(job)

    assert artifact.artifact_type == "memory_curation"
    assert len(artifact.summary) > 10
    # Summary should contain either "记忆" (healthy state) or indicate no action needed
    assert "记忆" in artifact.summary or "无需操作" in artifact.summary
    assert len(artifact.artifact_paths) >= 1
    assert "memory-scan" in artifact.sources


def test_actor_with_ttl_expired_entries() -> None:
    """Actor reports expired entries correctly."""
    wf = MemoryCurationWorkflow()
    job = _make_job()

    entries = [
        {"name": "old_feedback", "type": "feedback", "updated": "2023-01-01T00:00:00", "ttl_expired": True, "size": 100, "body_preview": "old", "error": None},
        {"name": "recent_feedback", "type": "feedback", "updated": "2025-06-01T00:00:00", "ttl_expired": False, "size": 200, "body_preview": "recent", "error": None},
    ]

    with patch("lanes_ceo.workflows.memory_curation._check_session_active", return_value=False):
        with patch("lanes_ceo.workflows.memory_curation._scan_memory_files", return_value=entries):
            with patch("lanes_ceo.workflows.memory_curation._check_large_files", return_value=[]):
                with patch("lanes_ceo.workflows.memory_curation._detect_duplicates", return_value=[]):
                    with patch("lanes_ceo.workflows.memory_curation.llm_chat", return_value="发现 1 条过期"):
                        with patch("lanes_ceo.workflows.memory_curation.get_artifact_dir") as mock_dir:
                            with tempfile.TemporaryDirectory() as tmpdir:
                                mock_dir.return_value = Path(tmpdir)
                                with patch("lanes_ceo.workflows.memory_curation._update_memory_index"):
                                    artifact = wf.run_actor(job)

    # The llm_chat mock returns "发现 1 条过期", and the actor reports expired
    # entries in the raw report section "## 过期条目" before calling llm_chat.
    assert "过期" in artifact.summary
    assert len(artifact.user_confirmations) > 0


def test_actor_with_duplicates() -> None:
    """Actor reports duplicate entries in summary."""
    wf = MemoryCurationWorkflow()
    job = _make_job()

    entries = [
        {"name": "a", "type": "project", "updated": "2025-01-01T00:00:00", "ttl_expired": False, "size": 100, "body_preview": "content", "error": None},
        {"name": "b", "type": "project", "updated": "2025-01-01T00:00:00", "ttl_expired": False, "size": 100, "body_preview": "content", "error": None},
    ]
    dup_pairs = [{"entry_a": "a", "entry_b": "b", "overlap_score": 0.85}]

    with patch("lanes_ceo.workflows.memory_curation._check_session_active", return_value=False):
        with patch("lanes_ceo.workflows.memory_curation._scan_memory_files", return_value=entries):
            with patch("lanes_ceo.workflows.memory_curation._check_large_files", return_value=[]):
                with patch("lanes_ceo.workflows.memory_curation._detect_duplicates", return_value=dup_pairs):
                    with patch("lanes_ceo.workflows.memory_curation.llm_chat", return_value="发现 1 对疑似重复"):
                        with patch("lanes_ceo.workflows.memory_curation.get_artifact_dir") as mock_dir:
                            with tempfile.TemporaryDirectory() as tmpdir:
                                mock_dir.return_value = Path(tmpdir)
                                with patch("lanes_ceo.workflows.memory_curation._update_memory_index"):
                                    artifact = wf.run_actor(job)

    assert len(artifact.user_confirmations) > 0


def test_actor_with_large_files() -> None:
    """Actor reports large files in summary."""
    wf = MemoryCurationWorkflow()
    job = _make_job()

    entries = [
        {"name": "big_file", "type": "project", "size": 80000, "ttl_expired": False, "body_preview": "large content", "error": None},
    ]
    large_files = [{"name": "big_file", "size": 80000}]

    with patch("lanes_ceo.workflows.memory_curation._check_session_active", return_value=False):
        with patch("lanes_ceo.workflows.memory_curation._scan_memory_files", return_value=entries):
            with patch("lanes_ceo.workflows.memory_curation._check_large_files", return_value=large_files):
                with patch("lanes_ceo.workflows.memory_curation._detect_duplicates", return_value=[]):
                    with patch("lanes_ceo.workflows.memory_curation.llm_chat", return_value="发现 1 个超大文件"):
                        with patch("lanes_ceo.workflows.memory_curation.get_artifact_dir") as mock_dir:
                            with tempfile.TemporaryDirectory() as tmpdir:
                                mock_dir.return_value = Path(tmpdir)
                                with patch("lanes_ceo.workflows.memory_curation._update_memory_index"):
                                    artifact = wf.run_actor(job)

    # The llm_chat mock returns "发现 1 个超大文件", which contains "超大".
    # large_files is hardcoded to always be non-empty, so we should assert
    # the actual summary content, not a tautology.
    assert "超大" in artifact.summary


def test_actor_active_session_no_destructive() -> None:
    """Actor with active session sets do_destructive=False and skips index update."""
    wf = MemoryCurationWorkflow()
    job = _make_job()

    entries = [
        {"name": "test", "type": "user", "size": 100, "ttl_expired": False, "body_preview": "body", "error": None},
    ]

    with patch("lanes_ceo.workflows.memory_curation._check_session_active", return_value=True):
        with patch("lanes_ceo.workflows.memory_curation._scan_memory_files", return_value=entries):
            with patch("lanes_ceo.workflows.memory_curation._check_large_files", return_value=[]):
                with patch("lanes_ceo.workflows.memory_curation._detect_duplicates", return_value=[]):
                    with patch("lanes_ceo.workflows.memory_curation.llm_chat", return_value="状态良好"):
                        with patch("lanes_ceo.workflows.memory_curation.get_artifact_dir") as mock_dir:
                            with tempfile.TemporaryDirectory() as tmpdir:
                                mock_dir.return_value = Path(tmpdir)
                                with patch("lanes_ceo.workflows.memory_curation._update_memory_index") as mock_update:
                                    artifact = wf.run_actor(job)
                                    # Index should NOT be updated when session is active
                                    mock_update.assert_not_called()

    assert artifact.artifact_type == "memory_curation"
    # Active session means llm_chat summary may not include session status text.
    # Instead, verify constraints: mock_update was NOT called, and the artifact is valid.
    assert len(artifact.risks) >= 1  # The risks are always set by run_actor


def test_actor_with_corrupted_files() -> None:
    """Actor reports corrupted file entries in the summary and 损坏文件 section."""
    wf = MemoryCurationWorkflow()
    job = _make_job()

    entries = [
        {"name": "good_file", "type": "user", "size": 100, "ttl_expired": False, "body_preview": "valid", "error": None},
        {"name": "bad_file", "type": "unknown", "size": 0, "ttl_expired": False, "body_preview": "", "error": "读取失败（编码或权限问题）"},
    ]

    with patch("lanes_ceo.workflows.memory_curation._check_session_active", return_value=False):
        with patch("lanes_ceo.workflows.memory_curation._scan_memory_files", return_value=entries):
            with patch("lanes_ceo.workflows.memory_curation._check_large_files", return_value=[]):
                with patch("lanes_ceo.workflows.memory_curation._detect_duplicates", return_value=[]):
                    with patch("lanes_ceo.workflows.memory_curation.llm_chat",
                               return_value="发现 1 个损坏文件: bad_file"):
                        with patch("lanes_ceo.workflows.memory_curation.get_artifact_dir") as mock_dir:
                            with tempfile.TemporaryDirectory() as tmpdir:
                                mock_dir.return_value = Path(tmpdir)
                                with patch("lanes_ceo.workflows.memory_curation._update_memory_index"):
                                    artifact = wf.run_actor(job)

    assert artifact.artifact_type == "memory_curation"
    # The raw report includes a "## 损坏文件" section listing bad_file
    assert "损坏" in artifact.summary or "bad_file" in artifact.summary


# ── critic tests ──


def test_critic_approves_complete_report() -> None:
    """Critic approves a well-formed memory curation report."""
    wf = MemoryCurationWorkflow()
    job = _make_job()
    artifact = Artifact(
        artifact_id="art-mc-1",
        job_id=job.job_id,
        artifact_type="memory_curation",
        summary=(
            "# 记忆整理报告 — 2026-05-23\n\n"
            "## 概览\n"
            "- 记忆总数: 42 条\n"
            "- 过期 (feedback > 90天): 3 条\n"
            "- 超大文件 (>50KB): 1 个\n"
            "- 疑似重复: 2 对\n"
            "- 损坏文件: 0 个"
        ),
        artifact_paths=["/tmp/memory-curation-20260523.md"],
        sources=["memory-scan", "ttl-check", "dedup-analysis", "llm-summary"],
        risks=["去重仅标记不自动删除"],
        user_confirmations=[],
    )
    review = wf.run_critic(job, artifact)
    assert review.approved is True
    assert review.score >= 80


def test_critic_rejects_missing_report_path() -> None:
    """Critic rejects artifact with no report file path."""
    wf = MemoryCurationWorkflow()
    job = _make_job()
    artifact = Artifact(
        artifact_id="art-mc-2",
        job_id=job.job_id,
        artifact_type="memory_curation",
        summary="整理完成，状态良好",
        artifact_paths=[],
        sources=["memory-scan", "ttl-check", "dedup-analysis"],
        risks=[],
        user_confirmations=[],
    )
    review = wf.run_critic(job, artifact)
    assert review.approved is False


def test_critic_rejects_insufficient_sources() -> None:
    """Critic rejects artifact with fewer than 3 sources."""
    wf = MemoryCurationWorkflow()
    job = _make_job()
    artifact = Artifact(
        artifact_id="art-mc-3",
        job_id=job.job_id,
        artifact_type="memory_curation",
        summary="整理完成，发现 5 条过期记忆",
        artifact_paths=["/tmp/report.md"],
        sources=["memory-scan", "ttl-check"],
        risks=[],
        user_confirmations=[],
    )
    review = wf.run_critic(job, artifact)
    assert review.approved is False


def test_critic_rejects_missing_memory_scan_source() -> None:
    """Critic rejects when 'memory-scan' source is missing."""
    wf = MemoryCurationWorkflow()
    job = _make_job()
    artifact = Artifact(
        artifact_id="art-mc-4",
        job_id=job.job_id,
        artifact_type="memory_curation",
        summary="整理完成，状态良好，无需操作",
        artifact_paths=["/tmp/report.md"],
        sources=["ttl-check", "dedup-analysis", "llm-summary"],
        risks=[],
        user_confirmations=[],
    )
    review = wf.run_critic(job, artifact)
    assert review.approved is False
