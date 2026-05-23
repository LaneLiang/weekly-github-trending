"""Unit tests for LiteratureSurveyWorkflow."""

import json
import sys
import tempfile
import urllib.error
from datetime import datetime, timedelta
from io import BytesIO
from pathlib import Path
from unittest.mock import MagicMock, patch

from lanes_ceo.contracts import Artifact, Job
from lanes_ceo.enums import JobStatus
from lanes_ceo.workflows.literature_survey import (
    LiteratureSurveyWorkflow,
    _build_matrix,
    _check_recent_execution,
    _dedup_and_rank,
    _download_pdf,
    _gap_analysis,
    _generate_bibtex,
    _generate_review_draft,
    _get_idempotency_key,
    _mark_execution,
    _normalize_title,
    _parse_nl_message,
    _search_arxiv,
    _search_ieee,
    _search_scholar,
    _summarize_batch,
    _try_carsi_download,
)


def _make_job() -> Job:
    return Job(
        job_id="job-ls-1",
        request_id="req-ls-1",
        role_group="literature_survey",
        actor="literature-survey-actor",
        critic="literature-survey-critic",
        status=JobStatus.RECEIVED,
        input={"message": "DC-DC 变换器 效率优化 TPE 2020年后 至少20篇"},
        workspace="runtime/jobs/job-ls-1",
    )


# ── _parse_nl_message tests ──


def test_parse_nl_message_chinese_input() -> None:
    """_parse_nl_message translates Chinese keywords to English."""
    with patch("lanes_ceo.workflows.literature_survey.llm_chat",
               return_value="DC-DC converter efficiency optimization"):
        result = _parse_nl_message("DC-DC 变换器 效率优化 TPE 2020年后 至少20篇")

    assert result["query_cn"] == "DC-DC 变换器 效率优化 TPE 2020年后 至少20篇"
    assert len(result["keywords_en"]) > 0
    assert "converter" in result["query_en"].lower() or "dcdc" in result["query_en"].lower() or "dc-dc" in result["query_en"].lower()


def test_parse_nl_message_english_input() -> None:
    """_parse_nl_message extracts keywords directly from English input."""
    result = _parse_nl_message("reinforcement learning, buck converter, efficiency")

    assert len(result["keywords_en"]) > 0
    assert "reinforcement" in [k.lower() for k in result["keywords_en"]]


def test_parse_nl_message_year_constraint() -> None:
    """_parse_nl_message extracts year_from from '2020年后' pattern."""
    result = _parse_nl_message("DC-DC converter 2020年后")

    assert result["year_from"] == 2020


def test_parse_nl_message_journal_names() -> None:
    """_parse_nl_message extracts journal abbreviations."""
    result = _parse_nl_message("TPE JSSC Nature 论文")

    assert "TPE" in result["journals"]
    assert "JSSC" in result["journals"]
    assert "Nature" in result["journals"]


def test_parse_nl_message_review_trigger() -> None:
    """_parse_nl_message sets generate_review_draft when '写综述' is present."""
    with patch("lanes_ceo.workflows.literature_survey.llm_chat",
               return_value="DC-DC converter review"):
        result = _parse_nl_message("写综述 DC-DC converter efficiency")

    assert result["generate_review_draft"] is True


def test_parse_nl_message_paper_count() -> None:
    """_parse_nl_message extracts '至少N篇' paper count."""
    with patch("lanes_ceo.workflows.literature_survey.llm_chat",
               return_value="buck converter efficiency"):
        result = _parse_nl_message("至少 30 篇 buck converter")

    assert result["max_papers"] == 30


# ── _search_arxiv tests ──


def test_search_arxiv_success() -> None:
    """_search_arxiv returns parsed paper dicts from valid XML response."""
    arxiv_xml = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom" xmlns:arxiv="http://arxiv.org/schemas/atom">
  <entry>
    <title>Efficient DC-DC Converter Design Using RL</title>
    <summary>We present a novel approach for DC-DC converter efficiency optimization.</summary>
    <id>http://arxiv.org/abs/2401.00001</id>
    <published>2024-01-15T00:00:00Z</published>
    <author><name>Smith J</name></author>
    <author><name>Jones K</name></author>
  </entry>
</feed>"""
    mock_resp = MagicMock()
    mock_resp.read.return_value = arxiv_xml.encode("utf-8")
    mock_resp.__enter__ = MagicMock(return_value=mock_resp)
    mock_resp.__exit__ = MagicMock(return_value=False)

    with patch("urllib.request.urlopen", return_value=mock_resp):
        papers = _search_arxiv(["dc", "dc", "converter", "efficiency"], max_results=5)

    assert len(papers) == 1
    assert "DC-DC Converter" in papers[0]["title"]
    assert papers[0]["source"] == "arxiv"
    assert papers[0]["year"] == 2024
    assert "Smith" in papers[0]["authors"]
    assert "pdf" in papers[0]["pdf_url"]


def test_search_arxiv_empty_keywords() -> None:
    """_search_arxiv returns empty list when keywords list is empty."""
    papers = _search_arxiv([], max_results=5)
    assert papers == []


def test_search_arxiv_network_error() -> None:
    """_search_arxiv returns empty list on network failure."""
    with patch("urllib.request.urlopen", side_effect=OSError("Network error")):
        papers = _search_arxiv(["test"], max_results=5)
    assert papers == []


# ── _download_pdf tests ──


def test_download_pdf_arxiv_success() -> None:
    """_download_pdf downloads from arXiv and writes PDF bytes to disk."""
    with tempfile.TemporaryDirectory() as tmpdir:
        out_dir = Path(tmpdir) / "pdfs"
        out_dir.mkdir()
        paper = {
            "title": "A Test Paper on Converters",
            "authors": "Smith J, Jones K",
            "year": 2024,
            "source": "arxiv",
            "pdf_url": "http://arxiv.org/pdf/2401.00001",
        }
        mock_resp = MagicMock()
        mock_resp.read.return_value = b"%PDF-1.4 fake content"
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)

        with patch("urllib.request.urlopen", return_value=mock_resp):
            result = _download_pdf(paper, out_dir, retries=1)

        assert result is not None
        assert result.endswith(".pdf")
        assert Path(result).exists()


def test_download_pdf_file_exists_returns_cached() -> None:
    """_download_pdf returns cached path when file already exists."""
    with tempfile.TemporaryDirectory() as tmpdir:
        out_dir = Path(tmpdir) / "pdfs"
        out_dir.mkdir()
        paper = {
            "title": "A Test Paper on Converters",
            "authors": "Smith J",
            "year": 2024,
            "source": "arxiv",
            "pdf_url": "http://arxiv.org/pdf/2401.00001",
        }
        # _download_pdf takes the last word of the first author's name:
        # "Smith J".split()[-1] = "J"
        expected_filename = out_dir / "J_2024_A-Test-Paper-on-Converters.pdf"
        expected_filename.write_text("cached content", encoding="utf-8")

        result = _download_pdf(paper, out_dir, retries=1)
        assert result == str(expected_filename)


# ── _summarize_batch tests ──


def test_summarize_batch_json_in_code_fence() -> None:
    """_summarize_batch parses JSON from markdown code fence."""
    papers = [{
        "title": "Test Paper",
        "authors": "Smith J",
        "year": 2024,
        "journal": "TPE",
        "doi": "10.1234/test",
        "abstract": "Test abstract content.",
    }]
    json_response = '```json\n[{"index": 1, "summary_cn": "测试摘要", "method_tags": ["RL"], "contribution_tags": ["高效"], "limitation_tags": ["局限"], "relevance_score": 8}]\n```'
    with patch("lanes_ceo.workflows.literature_survey.llm_chat", return_value=json_response):
        result = _summarize_batch(papers, batch_size=5)

    assert result[0]["llm_summary"] == "测试摘要"
    assert "RL" in result[0]["method_tags"]
    assert result[0]["llm_relevance"] == 8


def test_summarize_batch_bracket_matching_fallback() -> None:
    """_summarize_batch uses bracket-matching fallback when no code fence exists."""
    papers = [{
        "title": "Test Paper 2",
        "authors": "Jones K",
        "year": 2023,
        "journal": "TIE",
        "doi": "10.1234/test2",
        "abstract": "Another test.",
    }]
    json_response = 'Plain text before [{"index": 1, "summary_cn": "fallback摘要", "method_tags": ["PID"], "contribution_tags": ["c1"], "limitation_tags": ["l1"], "relevance_score": 7}] more text after'
    with patch("lanes_ceo.workflows.literature_survey.llm_chat", return_value=json_response):
        result = _summarize_batch(papers, batch_size=5)

    assert result[0]["llm_summary"] == "fallback摘要"
    assert result[0]["llm_relevance"] == 7


def test_summarize_batch_llm_unavailable() -> None:
    """_summarize_batch sets fallback values when llm_chat returns None."""
    papers = [{
        "title": "Test Paper",
        "authors": "X",
        "year": 2024,
        "journal": "J",
        "doi": "",
        "abstract": "test",
    }]
    with patch("lanes_ceo.workflows.literature_survey.llm_chat", return_value=None):
        result = _summarize_batch(papers, batch_size=5)

    assert result[0]["llm_summary"] == "[LLM不可用]"
    assert result[0]["method_tags"] == []


def test_summarize_batch_invalid_json_graceful() -> None:
    """_summarize_batch handles malformed JSON without crashing."""
    papers = [{
        "title": "Test Paper",
        "authors": "X",
        "year": 2024,
        "journal": "J",
        "doi": "",
        "abstract": "test",
    }]
    # Response with balanced brackets so bracket matching extracts text, but json.loads fails
    with patch("lanes_ceo.workflows.literature_survey.llm_chat", return_value="[not valid json]"):
        result = _summarize_batch(papers, batch_size=5)

    # Should not crash; fallback values set via except handler
    assert "llm_summary" in result[0]
    assert result[0]["llm_summary"] == "[LLM解析失败]"


# ── _build_matrix tests ──


def test_build_matrix_creates_csv_and_json() -> None:
    """_build_matrix writes CSV with BOM and JSON with session metadata."""
    papers = [
        {
            "title": "Test Paper One",
            "authors": "Smith J",
            "year": 2024,
            "journal": "TPE",
            "doi": "10.1/test",
            "abstract": "Test abstract.",
            "citation_count": 10,
            "source": "ieee",
            "pdf_path": "/tmp/p1.pdf",
            "llm_summary": "summary text",
            "method_tags": ["RL"],
            "contribution_tags": ["高效"],
            "limitation_tags": ["局限A"],
            "relevance_score": 8.5,
        },
    ]
    query_info = {"query_cn": "测试查询", "query_en": "test query"}

    with tempfile.TemporaryDirectory() as tmpdir:
        out_dir = Path(tmpdir)
        csv_path, json_path = _build_matrix(papers, "session-001", query_info, out_dir)

        assert csv_path.exists()
        assert json_path.exists()

        # Check CSV content
        csv_text = csv_path.read_text(encoding="utf-8-sig")
        assert "Test Paper One" in csv_text
        assert "Smith J" in csv_text
        assert "RL" in csv_text

        # Check JSON content
        json_data = json.loads(json_path.read_text(encoding="utf-8"))
        assert json_data["session_id"] == "session-001"
        assert json_data["total_found"] == 1
        assert json_data["total_downloaded"] == 1
        assert json_data["papers"][0]["title"] == "Test Paper One"


# ── _generate_bibtex tests ──


def test_generate_bibtex_creates_valid_entries() -> None:
    """_generate_bibtex writes proper BibTeX with sanitized author names."""
    papers = [
        {
            "title": "Efficient Converter Design",
            "authors": "Smith J, Jones K",
            "year": 2024,
            "journal": "IEEE Trans. Power Electron.",
            "doi": "10.1109/TPE.2024.123",
        },
        {
            "title": "Deep Learning for Power Electronics",
            "authors": "Wang L",
            "year": 2023,
            "journal": "arXiv preprint",
            "doi": "",
        },
    ]
    with tempfile.TemporaryDirectory() as tmpdir:
        out_dir = Path(tmpdir)
        bib_path = _generate_bibtex(papers, out_dir)

        assert bib_path.exists()
        bib_text = bib_path.read_text(encoding="utf-8")

        # First paper: article type, key includes sanitized author
        assert "@article{" in bib_text
        assert "ref1_Smith_2024" in bib_text or "ref1_J_" in bib_text
        assert "Efficient Converter Design" in bib_text
        assert "IEEE Trans. Power Electron." in bib_text

        # Second paper: misc type (preprint), no doi field
        # Author "Wang L" → last_name via .split()[-1] = "L"
        assert "@misc{" in bib_text
        assert "ref2_L_2023" in bib_text
        assert "Wang L" in bib_text


def test_generate_bibtex_handles_empty_authors() -> None:
    """_generate_bibtex uses 'anon' when authors field is empty."""
    papers = [{"title": "Untitled Work", "authors": "", "year": 2025, "journal": "Unknown"}]
    with tempfile.TemporaryDirectory() as tmpdir:
        bib_path = _generate_bibtex(papers, Path(tmpdir))
        bib_text = bib_path.read_text(encoding="utf-8")
        assert "_anon_" in bib_text


def test_normalize_title_strips_punctuation() -> None:
    """_normalize_title removes punctuation and lowercases."""
    result = _normalize_title("A Very Important Paper: A Study!")
    assert ":" not in result
    assert "!" not in result
    assert result == "averyimportantpaperastudy"


def test_normalize_title_handles_special_chars() -> None:
    """_normalize_title handles special characters (hyphens, colons)."""
    result = _normalize_title("DC-DC Converter: Efficiency & Optimization")
    assert "--" not in result
    assert "&" not in result
    assert ":" not in result


# ── _dedup_and_rank tests ──


def test_dedup_and_rank_removes_duplicates() -> None:
    """_dedup_and_rank deduplicates papers by normalized title."""
    papers = [
        {"title": "A Study on DC-DC Converters", "authors": "A", "year": 2024, "source": "ieee", "citation_count": 10},
        {"title": "A Study on DCDC Converters!", "authors": "B", "year": 2023, "source": "arxiv", "citation_count": 5},
    ]
    keywords = ["dc", "dc", "converter"]
    result = _dedup_and_rank(papers, keywords, [])
    assert len(result) == 1


def test_dedup_and_rank_ranks_by_relevance() -> None:
    """_dedup_and_rank sorts by relevance_score descending."""
    papers = [
        {"title": "Memory Management in Operating Systems", "authors": "X", "year": 2020, "source": "ieee", "citation_count": 5},
        {"title": "DC-DC Buck Converter Efficiency Optimization", "authors": "Y", "year": 2025, "source": "ieee", "citation_count": 10},
    ]
    keywords = ["buck", "converter", "efficiency"]
    result = _dedup_and_rank(papers, keywords, [])
    assert len(result) == 2
    assert "Buck" in result[0]["title"]


def test_dedup_and_rank_short_title_removed() -> None:
    """_dedup_and_rank removes papers with very short normalized titles."""
    papers = [
        {"title": "A", "authors": "X", "year": 2024, "source": "ieee", "citation_count": 1},
        {"title": "A Real Paper About Something Important", "authors": "Y", "year": 2024, "source": "ieee", "citation_count": 1},
    ]
    result = _dedup_and_rank(papers, [], [])
    assert len(result) == 1
    assert "Real" in result[0]["title"]


# ── _get_idempotency_key tests ──


def test_get_idempotency_key_consistent() -> None:
    """_get_idempotency_key returns consistent hash for same input."""
    key1 = _get_idempotency_key("DC-DC converter efficiency")
    key2 = _get_idempotency_key("DC-DC converter efficiency")
    assert key1 == key2
    assert len(key1) == 16


def test_get_idempotency_key_different_input() -> None:
    """_get_idempotency_key returns different hashes for different inputs."""
    key1 = _get_idempotency_key("DC-DC converter")
    key2 = _get_idempotency_key("buck converter")
    assert key1 != key2


# ── _check_recent_execution tests ──


def test_check_recent_execution_no_marker() -> None:
    """_check_recent_execution returns False when no marker file exists."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch("lanes_ceo.workflows.literature_survey.PROJECT_OUTPUT_BASE", Path(tmpdir)):
            result = _check_recent_execution("abc123")
    assert result is False


def test_check_recent_execution_within_window() -> None:
    """_check_recent_execution returns True when marker is within time window."""
    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        marker_dir = base / "literature_survey" / ".idempotency"
        marker_dir.mkdir(parents=True, exist_ok=True)
        marker_file = marker_dir / "abc123.json"
        marker_file.write_text(json.dumps({"timestamp": datetime.now().isoformat()}))

        with patch("lanes_ceo.workflows.literature_survey.PROJECT_OUTPUT_BASE", base):
            result = _check_recent_execution("abc123", window_minutes=60)

    assert result is True


def test_check_recent_execution_expired_window() -> None:
    """_check_recent_execution returns False when marker is outside window."""
    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        marker_dir = base / "literature_survey" / ".idempotency"
        marker_dir.mkdir(parents=True, exist_ok=True)
        marker_file = marker_dir / "abc123.json"
        old_time = (datetime.now() - timedelta(hours=2)).isoformat()
        marker_file.write_text(json.dumps({"timestamp": old_time}))

        with patch("lanes_ceo.workflows.literature_survey.PROJECT_OUTPUT_BASE", base):
            result = _check_recent_execution("abc123", window_minutes=30)

    assert result is False


# ── actor tests ──


def test_actor_no_api_key_produces_stub() -> None:
    """Actor produces artifact even without LLM API key (uses stub summaries)."""
    wf = LiteratureSurveyWorkflow()
    job = _make_job()

    with patch("lanes_ceo.workflows.literature_survey.os.environ", {}):
        with patch("lanes_ceo.workflows.literature_survey._load_config") as mock_cfg:
            mock_cfg.return_value = {
                "search_sources": {
                    "arxiv": {"priority": 3, "enabled": True, "max_results": 5},
                    "ieee": {"priority": 1, "enabled": False, "max_results": 5},
                    "scholar": {"priority": 2, "enabled": False, "max_results": 5},
                },
                "pipeline": {
                    "default_max_papers": 5,
                    "llm_batch_size": 5,
                    "download_retries": 1,
                    "download_timeout_seconds": 10,
                    "idempotency_window_minutes": 30,
                },
            }
            with patch("lanes_ceo.workflows.literature_survey.llm_chat",
                       return_value="DC-DC converter efficiency optimization buck"):
                with patch("lanes_ceo.workflows.literature_survey._check_recent_execution", return_value=False):
                    with patch("lanes_ceo.workflows.literature_survey._search_arxiv") as mock_arxiv:
                        mock_arxiv.return_value = [
                            {
                                "title": "Efficient DC-DC Converter Design Using RL",
                                "authors": "Smith J",
                                "year": 2024,
                                "abstract": "We present a novel approach...",
                                "source": "arxiv",
                                "doi": "10.1234/abcd",
                                "journal": "arXiv preprint",
                                "pdf_url": "http://arxiv.org/pdf/2401.00001",
                            }
                        ]
                        # Also patch _search_ieee and _search_scholar even though
                        # config disables them — resilience against future config changes
                        with patch("lanes_ceo.workflows.literature_survey._search_ieee", return_value=[]):
                            with patch("lanes_ceo.workflows.literature_survey._search_scholar", return_value=[]):
                                with patch("lanes_ceo.workflows.literature_survey.get_artifact_dir") as mock_dir:
                                    with tempfile.TemporaryDirectory() as tmpdir:
                                        mock_dir.return_value = Path(tmpdir)
                                        artifact = wf.run_actor(job)

    assert artifact.artifact_type == "literature_survey"
    assert len(artifact.summary) > 50


def test_actor_empty_message_handles_gracefully() -> None:
    """Actor handles empty input message without crashing."""
    wf = LiteratureSurveyWorkflow()
    job = Job(
        job_id="job-ls-empty",
        request_id="req-ls-empty",
        role_group="literature_survey",
        actor="literature-survey-actor",
        critic="literature-survey-critic",
        status=JobStatus.RECEIVED,
        input={"message": ""},
        workspace="runtime/jobs/job-ls-empty",
    )

    with patch("lanes_ceo.workflows.literature_survey.os.environ", {}):
        with patch("lanes_ceo.workflows.literature_survey._load_config") as mock_cfg:
            mock_cfg.return_value = {
                "search_sources": {
                    "arxiv": {"priority": 3, "enabled": False, "max_results": 5},
                    "ieee": {"priority": 1, "enabled": False, "max_results": 5},
                    "scholar": {"priority": 2, "enabled": False, "max_results": 5},
                },
                "pipeline": {
                    "default_max_papers": 5,
                    "llm_batch_size": 5,
                    "download_retries": 1,
                    "download_timeout_seconds": 10,
                    "idempotency_window_minutes": 30,
                },
            }
            with patch("lanes_ceo.workflows.literature_survey._check_recent_execution", return_value=False):
                with patch("lanes_ceo.workflows.literature_survey.get_artifact_dir") as mock_dir:
                    with tempfile.TemporaryDirectory() as tmpdir:
                        mock_dir.return_value = Path(tmpdir)
                        artifact = wf.run_actor(job)

    assert artifact.artifact_type == "literature_survey"
    # Should not crash — even with empty message it should produce some artifact
    assert artifact is not None


def test_actor_idempotency_cache_hit() -> None:
    """Actor returns cached artifact when _check_recent_execution returns True
    and a recent session directory with session_summary.md is found."""
    wf = LiteratureSurveyWorkflow()
    job = _make_job()

    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        # Simulate a previous session directory with a summary file
        prev_session = base / "abc123456789"
        prev_session.mkdir(parents=True)
        summary_path = prev_session / "session_summary.md"
        summary_path.write_text("# 之前调研结果\n内容提要...", encoding="utf-8")

        with patch("lanes_ceo.workflows.literature_survey.llm_chat",
                   return_value="DC-DC converter efficiency optimization"):
            with patch("lanes_ceo.workflows.literature_survey._check_recent_execution", return_value=True):
                with patch("lanes_ceo.workflows.literature_survey.get_artifact_dir") as mock_dir:
                    mock_dir.return_value = base
                    artifact = wf.run_actor(job)

    assert artifact.artifact_type == "literature_survey"
    assert "idempotency_cache" in artifact.sources
    assert "复用最近调研结果" in artifact.summary or "重复查询" in artifact.summary


# ── critic tests ──


def test_critic_approves_complete_survey() -> None:
    """Critic approves a well-formed literature survey report."""
    import tempfile

    wf = LiteratureSurveyWorkflow()
    job = _make_job()

    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        # Create a pretend CSV matrix
        csv_path = base / "literature_matrix.csv"
        csv_path.write_text(
            "title,authors,year\n"
            "Paper One,Smith J,2024\n"
            "Paper Two,Jones K,2023\n"
            "Paper Three,Brown L,2025\n"
            "Paper Four,White M,2024\n",
            encoding="utf-8",
        )
        # Create a gap analysis
        gap_path = base / "gap_analysis.md"
        gap_path.write_text(
            "# Gap Analysis\n\n"
            "## 已覆盖方向\n"
            "- Direction A\n"
            "- Direction B\n\n"
            "## 研究空白\n"
            "### Gap 1: Something missing\n"
            "### Gap 2: Another gap\n"
            "### Gap 3: Third gap\n",
            encoding="utf-8",
        )
        # Create a references.bib
        bib_path = base / "references.bib"
        bib_path.write_text(
            "@article{ref1_smith_2024,\n"
            "  title = Paper One,\n"
            "  author = Smith J,\n"
            "  year = 2024,\n"
            "}\n\n"
            "@article{ref2_jones_2023,\n"
            "  title = Paper Two,\n"
            "  author = Jones K,\n"
            "  year = 2023,\n"
            "}\n",
            encoding="utf-8",
        )

        with patch("lanes_ceo.workflows.literature_survey.llm_chat",
                   return_value="审查通过，报告质量良好"):
            artifact = Artifact(
                artifact_id="art-ls-1",
                job_id=job.job_id,
                artifact_type="literature_survey",
                summary=(
                    "# 文献调研报告 — 2026-05-23\n"
                    "**查询**: DC-DC 变换器 效率优化\n"
                    "**英文关键词**: DC-DC converter efficiency optimization\n\n"
                    "## 统计\n"
                    "- 各源命中: arxiv: 5\n"
                    "- 去重后: 4 篇\n"
                    "- 全文下载成功: 2 篇\n"
                    "## 关键发现\n"
                    "- 主要方法: RL, PID, MPC\n"
                ),
                artifact_paths=[
                    str(base / "session_summary.md"),
                    str(csv_path),
                    str(base / "literature_matrix.json"),
                    str(gap_path),
                    str(bib_path),
                ],
                sources=["ieee", "arxiv", "scholar", "llm-summarization", "llm-gap-analysis"],
                risks=["IEEE API 可能受认证限制"],
                user_confirmations=[],
            )
            # Make sure summary and gap file exist
            (base / "session_summary.md").write_text("summary", encoding="utf-8")
            (base / "literature_matrix.json").write_text("{}", encoding="utf-8")

            review = wf.run_critic(job, artifact)

    assert review.approved is True
    assert review.score >= 70


def test_critic_rejects_short_summary() -> None:
    """Critic rejects survey with summary shorter than 100 characters."""
    wf = LiteratureSurveyWorkflow()
    job = _make_job()

    with patch("lanes_ceo.workflows.literature_survey.llm_chat",
               return_value="内容不足"):
        artifact = Artifact(
            artifact_id="art-ls-2",
            job_id=job.job_id,
            artifact_type="literature_survey",
            summary="short",
            artifact_paths=["/tmp/summary.md", "/tmp/matrix.csv", "/tmp/gap.md"],
            sources=["ieee", "arxiv", "scholar"],
            risks=[],
            user_confirmations=[],
        )
        review = wf.run_critic(job, artifact)

    assert review.approved is False


def test_critic_rejects_missing_sources() -> None:
    """Critic rejects survey with fewer than 3 sources."""
    wf = LiteratureSurveyWorkflow()
    job = _make_job()

    with patch("lanes_ceo.workflows.literature_survey.llm_chat",
               return_value="来源不足"):
        artifact = Artifact(
            artifact_id="art-ls-3",
            job_id=job.job_id,
            artifact_type="literature_survey",
            summary=(
                "# 文献调研报告 — 2026-05-23\n"
                "**查询**: Test query\n"
                "## 统计\n"
                "- 去重后: 5 篇\n"
                "- 全文下载成功: 0 篇"
            ),
            artifact_paths=["/tmp/summary.md", "/tmp/matrix.csv", "/tmp/gap.md"],
            sources=["ieee", "arxiv"],
            risks=[],
            user_confirmations=[],
        )
        review = wf.run_critic(job, artifact)

    assert review.approved is False


def test_critic_rejects_empty_csv() -> None:
    """Critic rejects survey when CSV matrix is empty."""
    import tempfile

    wf = LiteratureSurveyWorkflow()
    job = _make_job()

    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        csv_path = base / "matrix.csv"
        csv_path.write_text("title,authors,year\n", encoding="utf-8")

        with patch("lanes_ceo.workflows.literature_survey.llm_chat",
                   return_value="CSV内容不足"):
            artifact = Artifact(
                artifact_id="art-ls-4",
                job_id=job.job_id,
                artifact_type="literature_survey",
                summary=(
                    "# 文献调研报告 — 2026-05-23\n"
                    "**查询**: Test query\n"
                    "## 统计\n"
                    "- 去重后: 2 篇\n"
                    "- 全文下载成功: 0 篇"
                ),
                artifact_paths=[str(csv_path)],
                sources=["ieee", "arxiv", "scholar"],
                risks=[],
                user_confirmations=[],
            )
            review = wf.run_critic(job, artifact)

    assert review.approved is False


# ── _search_ieee tests ──


def test_search_ieee_empty_keywords() -> None:
    """_search_ieee returns empty list when keywords list is empty."""
    papers = _search_ieee([], max_results=10)
    assert papers == []


def test_search_ieee_success() -> None:
    """_search_ieee returns paper dicts from a valid JSON response."""
    ieee_response = {
        "articles": [
            {
                "title": "Efficient DC-DC Converter Via Reinforcement Learning",
                "authors": {"authors": [
                    {"preferred_name": "John", "last_name": "Smith"},
                    {"preferred_name": "Jane", "last_name": "Doe"},
                ]},
                "publication_year": 2024,
                "abstract": "A novel RL-based approach for DC-DC efficiency.",
                "doi": "10.1109/TPE.2024.123456",
                "publication_title": "IEEE Trans. Power Electron.",
                "citing_paper_count": 15,
                "article_number": "9876543",
            },
        ],
    }
    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps(ieee_response).encode("utf-8")
    mock_resp.__enter__ = MagicMock(return_value=mock_resp)
    mock_resp.__exit__ = MagicMock(return_value=False)

    with patch("urllib.request.urlopen", return_value=mock_resp):
        with patch("time.sleep", return_value=None):
            papers = _search_ieee(["dc", "dc", "converter", "efficiency"], max_results=10)

    assert len(papers) == 1
    assert papers[0]["source"] == "ieee"
    assert "DC-DC Converter" in papers[0]["title"]
    assert papers[0]["year"] == 2024
    assert "John Smith" in papers[0]["authors"]
    assert papers[0]["doi"] == "10.1109/TPE.2024.123456"
    assert papers[0]["journal"] == "IEEE Trans. Power Electron."
    assert papers[0]["citation_count"] == 15
    assert "9876543" in papers[0]["pdf_url"]


def test_search_ieee_success_with_year_filter() -> None:
    """_search_ieee includes year_from in request params when provided."""
    ieee_response = {"articles": []}
    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps(ieee_response).encode("utf-8")
    mock_resp.__enter__ = MagicMock(return_value=mock_resp)
    mock_resp.__exit__ = MagicMock(return_value=False)

    with patch("urllib.request.urlopen", return_value=mock_resp) as mock_urlopen:
        with patch("time.sleep", return_value=None):
            _search_ieee(["buck", "converter"], max_results=10, year_from=2020)

    # Verify year_from was included in the request body
    call_args = mock_urlopen.call_args[0][0]
    sent_data = json.loads(call_args.data.decode("utf-8"))
    assert sent_data["start_year"] == "2020"


def test_search_ieee_http_429_retry_succeeds() -> None:
    """_search_ieee retries on HTTP 429 and recovers on the second retry."""
    ieee_response = {"articles": [
        {"title": "Recovered Paper", "authors": {"authors": [
            {"preferred_name": "A", "last_name": "B"}
        ]}, "publication_year": 2023, "abstract": "x",
         "doi": "", "publication_title": "", "citing_paper_count": 0, "article_number": ""}
    ]}
    success_resp = MagicMock()
    success_resp.read.return_value = json.dumps(ieee_response).encode("utf-8")
    success_resp.__enter__ = MagicMock(return_value=success_resp)
    success_resp.__exit__ = MagicMock(return_value=False)

    http_429 = urllib.error.HTTPError(
        "https://ieeexplore.ieee.org/rest/search", 429,
        "Too Many Requests", {}, BytesIO(b"")
    )

    # Side effect: first call + retry 0 both 429, retry 1 succeeds
    side_effects = [http_429, http_429, success_resp]

    with patch("urllib.request.urlopen", side_effect=side_effects):
        with patch("time.sleep", return_value=None):
            papers = _search_ieee(["test"], max_results=5)

    assert len(papers) == 1
    assert papers[0]["title"] == "Recovered Paper"
    assert papers[0]["year"] == 2023


def test_search_ieee_http_429_all_retries_exhausted() -> None:
    """_search_ieee gives up after 3 failed retries on HTTP 429."""
    http_429 = urllib.error.HTTPError(
        "https://ieeexplore.ieee.org/rest/search", 429,
        "Too Many Requests", {}, BytesIO(b"")
    )
    # First call + 3 retries all raise 429
    side_effects = [http_429, http_429, http_429, http_429]

    with patch("urllib.request.urlopen", side_effect=side_effects):
        with patch("time.sleep", return_value=None):
            papers = _search_ieee(["test"], max_results=5)

    assert papers == []


def test_search_ieee_other_http_error() -> None:
    """_search_ieee logs warning and returns [] on non-429 HTTP errors."""
    http_500 = urllib.error.HTTPError(
        "https://ieeexplore.ieee.org/rest/search", 500,
        "Internal Server Error", {}, BytesIO(b"")
    )

    with patch("urllib.request.urlopen", side_effect=http_500):
        papers = _search_ieee(["test"], max_results=5)

    assert papers == []


def test_search_ieee_generic_exception() -> None:
    """_search_ieee returns [] on generic exception (e.g., network timeout)."""
    with patch("urllib.request.urlopen", side_effect=OSError("Connection refused")):
        papers = _search_ieee(["test"], max_results=5)

    assert papers == []


# ── _search_scholar tests ──


def test_search_scholar_scholarly_success() -> None:
    """_search_scholar returns papers via scholarly library when available."""
    mock_paper = {
        "bib": {
            "title": "Efficient DC-DC Converter Design",
            "author": "Smith J",
            "pub_year": 2024,
            "journal": "IEEE Trans. Power Electron.",
            "abstract": "A test paper abstract about converters.",
            "eprint_url": "http://example.com/pdf",
            "doi": "10.1109/TPE.2024.1",
        },
        "num_citations": 42,
    }

    # Build mock scholarly module
    mock_scholarly = MagicMock()
    mock_scholarly.search_pubs.return_value = [mock_paper]
    mock_scholarly_mod = MagicMock()
    mock_scholarly_mod.scholarly = mock_scholarly
    mock_pg_instance = MagicMock()
    mock_pg_instance.FreeProxies.return_value = True
    mock_scholarly_mod.ProxyGenerator = MagicMock(return_value=mock_pg_instance)

    with patch.dict(sys.modules, {"scholarly": mock_scholarly_mod}):
        papers = _search_scholar(["dc", "dc", "converter"], max_results=5)

    assert len(papers) == 1
    assert papers[0]["title"] == "Efficient DC-DC Converter Design"
    assert papers[0]["source"] == "scholar"
    assert papers[0]["citation_count"] == 42
    assert papers[0]["year"] == 2024
    assert papers[0]["doi"] == "10.1109/TPE.2024.1"


def test_search_scholar_subprocess_fallback() -> None:
    """_search_scholar uses subprocess fallback when scholarly import fails."""
    papers_json = json.dumps([
        {
            "title": "Fallback Paper via Subprocess",
            "authors": "Jones K",
            "year": "2023",
            "source": "scholar",
        },
    ])
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = papers_json
    mock_result.stderr = ""

    scholarly_saved = sys.modules.pop("scholarly", None)
    try:
        with patch("subprocess.run", return_value=mock_result):
            papers = _search_scholar(["test"], max_results=5)
    finally:
        if scholarly_saved is not None:
            sys.modules["scholarly"] = scholarly_saved

    assert len(papers) == 1
    assert papers[0]["title"] == "Fallback Paper via Subprocess"


def test_search_scholar_all_approaches_fail() -> None:
    """_search_scholar returns [] when both scholarly and subprocess fail."""
    scholarly_saved = sys.modules.pop("scholarly", None)
    try:
        with patch("subprocess.run", side_effect=FileNotFoundError("python not found")):
            papers = _search_scholar(["test"], max_results=5)
    finally:
        if scholarly_saved is not None:
            sys.modules["scholarly"] = scholarly_saved

    assert papers == []


# ── _gap_analysis tests ──


def test_gap_analysis_writes_file_with_llm_response() -> None:
    """_gap_analysis calls llm_chat and writes result to gap_analysis.md."""
    papers = [{
        "title": "Test Paper on Buck Converters",
        "authors": "Smith J",
        "year": 2024,
        "journal": "TPE",
        "doi": "10.1/test",
        "abstract": "Test.",
        "method_tags": ["RL"],
        "contribution_tags": ["High efficiency"],
        "limitation_tags": ["Narrow input range"],
    }]
    query_info = {"query_cn": "buck converter efficiency"}
    llm_output = "## 已覆盖方向\n- RL-based control\n\n## 研究空白\n### Gap 1: ..."

    with tempfile.TemporaryDirectory() as tmpdir:
        out_dir = Path(tmpdir)
        with patch("lanes_ceo.workflows.literature_survey.llm_chat", return_value=llm_output):
            with patch("lanes_ceo.workflows.literature_survey._load_config", return_value={}):
                result_path = _gap_analysis(papers, query_info, out_dir)

        assert result_path.exists()
        assert result_path.name == "gap_analysis.md"
        content = result_path.read_text(encoding="utf-8")
        assert "RL-based control" in content
        assert "Gap 1" in content


def test_gap_analysis_llm_unavailable_writes_fallback() -> None:
    """_gap_analysis writes '[LLM不可用]' fallback when llm_chat returns None."""
    papers = [{
        "title": "Test Paper", "authors": "X", "year": 2024,
        "journal": "J", "doi": "", "abstract": "",
        "method_tags": [], "contribution_tags": [], "limitation_tags": [],
    }]
    query_info = {"query_cn": "test query"}

    with tempfile.TemporaryDirectory() as tmpdir:
        out_dir = Path(tmpdir)
        with patch("lanes_ceo.workflows.literature_survey.llm_chat", return_value=None):
            with patch("lanes_ceo.workflows.literature_survey._load_config", return_value={}):
                result_path = _gap_analysis(papers, query_info, out_dir)

        assert result_path.exists()
        content = result_path.read_text(encoding="utf-8")
        assert "LLM不可用" in content


def test_gap_analysis_truncates_papers_to_20() -> None:
    """_gap_analysis only includes first 20 papers in the prompt."""
    papers = []
    for i in range(25):
        papers.append({
            "title": f"Paper {i+1}",
            "authors": "Author",
            "year": 2020 + (i % 5),
            "journal": "J",
            "doi": "",
            "abstract": "",
            "method_tags": [],
            "contribution_tags": [],
            "limitation_tags": [],
        })

    with tempfile.TemporaryDirectory() as tmpdir:
        out_dir = Path(tmpdir)
        with patch("lanes_ceo.workflows.literature_survey.llm_chat") as mock_llm:
            mock_llm.return_value = "## analysis"
            with patch("lanes_ceo.workflows.literature_survey._load_config", return_value={}):
                _gap_analysis(papers, {"query_cn": "test"}, out_dir)

        # Verify prompt only includes papers[:20]
        prompt_arg = mock_llm.call_args[0][1]
        assert "Paper 1" in prompt_arg
        assert "Paper 20" in prompt_arg
        assert "Paper 21" not in prompt_arg


# ── _generate_review_draft tests ──


def test_generate_review_draft_writes_file_with_llm_response() -> None:
    """_generate_review_draft reads gap content, calls llm_chat, writes review."""
    papers = [{
        "title": "A Review Paper",
        "authors": "Smith J",
        "year": 2024,
        "journal": "TPE",
        "doi": "",
        "abstract": "",
    }]
    query_info = {"query_cn": "DC-DC converter review"}
    llm_output = "# 综述草稿\n\n## 引言\nThis is a review draft."

    with tempfile.TemporaryDirectory() as tmpdir:
        out_dir = Path(tmpdir)
        gap_path = out_dir / "gap_analysis.md"
        gap_path.write_text("## 缺口分析内容\nGap content here.", encoding="utf-8")

        with patch("lanes_ceo.workflows.literature_survey.llm_chat", return_value=llm_output):
            with patch("lanes_ceo.workflows.literature_survey._load_config", return_value={}):
                result_path = _generate_review_draft(papers, gap_path, query_info, out_dir)

        assert result_path.exists()
        assert result_path.name == "review_draft.md"
        content = result_path.read_text(encoding="utf-8")
        assert "综述草稿" in content
        assert "引言" in content


def test_generate_review_draft_missing_gap_file() -> None:
    """_generate_review_draft uses empty gap_content when gap_path does not exist."""
    papers = [{
        "title": "Test Paper", "authors": "A", "year": 2024,
        "journal": "J", "doi": "", "abstract": "",
    }]
    query_info = {"query_cn": "test"}
    llm_output = "# Review\nContent."

    with tempfile.TemporaryDirectory() as tmpdir:
        out_dir = Path(tmpdir)
        non_existent_gap = out_dir / "does_not_exist.md"

        with patch("lanes_ceo.workflows.literature_survey.llm_chat", return_value=llm_output):
            with patch("lanes_ceo.workflows.literature_survey._load_config", return_value={}):
                result_path = _generate_review_draft(
                    papers, non_existent_gap, query_info, out_dir
                )

        assert result_path.exists()
        content = result_path.read_text(encoding="utf-8")
        assert "Review" in content


def test_generate_review_draft_llm_unavailable_writes_fallback() -> None:
    """_generate_review_draft writes '[LLM不可用]' fallback when llm_chat returns None."""
    papers = [{
        "title": "Paper", "authors": "A", "year": 2024,
        "journal": "J", "doi": "", "abstract": "",
    }]
    query_info = {"query_cn": "test"}

    with tempfile.TemporaryDirectory() as tmpdir:
        out_dir = Path(tmpdir)
        gap_path = out_dir / "gap_analysis.md"
        gap_path.write_text("Some gap content.", encoding="utf-8")

        with patch("lanes_ceo.workflows.literature_survey.llm_chat", return_value=None):
            with patch("lanes_ceo.workflows.literature_survey._load_config", return_value={}):
                result_path = _generate_review_draft(
                    papers, gap_path, query_info, out_dir
                )

        assert result_path.exists()
        content = result_path.read_text(encoding="utf-8")
        assert "LLM不可用" in content


# ── _mark_execution tests ──


def test_mark_execution_creates_idempotency_file() -> None:
    """_mark_execution creates a JSON marker file with timestamp."""
    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        with patch("lanes_ceo.workflows.literature_survey.PROJECT_OUTPUT_BASE", base):
            _mark_execution("test-key-001")

        marker_file = (
            base / "literature_survey" / ".idempotency" / "test-key-001.json"
        )
        assert marker_file.exists()
        data = json.loads(marker_file.read_text())
        assert "timestamp" in data
        # Verify it is a valid ISO format datetime
        parsed = datetime.fromisoformat(data["timestamp"])
        assert isinstance(parsed, datetime)


def test_mark_execution_overwrites_existing_marker() -> None:
    """_mark_execution overwrites an existing marker file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        marker_dir = base / "literature_survey" / ".idempotency"
        marker_dir.mkdir(parents=True, exist_ok=True)
        marker_file = marker_dir / "test-key-002.json"
        old_time = "2020-01-01T00:00:00"
        marker_file.write_text(json.dumps({"timestamp": old_time}))

        with patch("lanes_ceo.workflows.literature_survey.PROJECT_OUTPUT_BASE", base):
            _mark_execution("test-key-002")

        data = json.loads(marker_file.read_text())
        assert data["timestamp"] != old_time


# ── _try_carsi_download tests ──


def test_try_carsi_download_pdf_success() -> None:
    """_try_carsi_download returns file path when response contains PDF bytes."""
    with tempfile.TemporaryDirectory() as tmpdir:
        out_dir = Path(tmpdir)
        doi = "10.1109/TPE.2024.123456/test"

        mock_resp = MagicMock()
        mock_resp.read.return_value = b"%PDF-1.4 fake pdf content"
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)

        with patch("urllib.request.urlopen", return_value=mock_resp):
            result = _try_carsi_download(doi, out_dir, "user", "password")

        assert result is not None
        assert result.endswith(".pdf")
        saved = Path(result).read_bytes()
        assert saved == b"%PDF-1.4 fake pdf content"


def test_try_carsi_download_html_redirect_returns_none() -> None:
    """_try_carsi_download returns None when response is HTML (not a PDF)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        out_dir = Path(tmpdir)
        doi = "10.1109/TEST.2024/paper"

        mock_resp = MagicMock()
        mock_resp.read.return_value = b"<!DOCTYPE html><html><body>Login page</body></html>"
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)

        with patch("urllib.request.urlopen", return_value=mock_resp):
            result = _try_carsi_download(doi, out_dir, "user", "pass")

        assert result is None


def test_try_carsi_download_exception_returns_none() -> None:
    """_try_carsi_download returns None when URL fetch raises an exception."""
    with tempfile.TemporaryDirectory() as tmpdir:
        out_dir = Path(tmpdir)

        with patch("urllib.request.urlopen", side_effect=OSError("Connection error")):
            result = _try_carsi_download(
                "10.1234/doi", out_dir, "user", "pass"
            )

        assert result is None
