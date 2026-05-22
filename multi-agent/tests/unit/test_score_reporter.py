from datetime import datetime, timezone

from lanes_ceo.contracts import ScoreRecord
from lanes_ceo.reporting.score_reporter import ScoreReporter
from lanes_ceo.storage.sqlite_store import SQLiteStore


def test_score_reporter_exports_json(tmp_path) -> None:
    store = SQLiteStore(tmp_path / "lanes.sqlite3")
    store.initialize()
    now = datetime.now(timezone.utc).isoformat()
    store.save_score_record(
        ScoreRecord(
            score_id="score-1",
            job_id="job-1",
            scored_role="github-actor",
            scorer_role="github-critic",
            score=90,
            rating="A",
            review_summary="good coverage",
            created_at=now,
            month_bucket="2026-05",
        )
    )
    store.save_score_record(
        ScoreRecord(
            score_id="score-2",
            job_id="job-2",
            scored_role="ai-news-actor",
            scorer_role="ai-news-critic",
            score=88,
            rating="A",
            review_summary="solid",
            created_at=now,
            month_bucket="2026-05",
        )
    )

    reporter = ScoreReporter(store)
    out = reporter.export_json(tmp_path)

    assert out.exists()
    assert out.name == "score_records.json"


def test_score_reporter_monthly_summary(tmp_path) -> None:
    store = SQLiteStore(tmp_path / "lanes.sqlite3")
    store.initialize()
    now = datetime.now(timezone.utc).isoformat()
    store.save_score_record(
        ScoreRecord(
            score_id="score-3",
            job_id="job-3",
            scored_role="github-actor",
            scorer_role="github-critic",
            score=100,
            rating="S",
            review_summary="perfect",
            created_at=now,
            month_bucket="2026-05",
        )
    )
    store.save_score_record(
        ScoreRecord(
            score_id="score-4",
            job_id="job-4",
            scored_role="ai-news-actor",
            scorer_role="ai-news-critic",
            score=80,
            rating="B",
            review_summary="ok",
            created_at=now,
            month_bucket="2026-05",
        )
    )

    reporter = ScoreReporter(store)
    summary = reporter.monthly_summary()

    assert summary["total_jobs"] == 2
    assert summary["avg_score"] == 90.0
    assert summary["ratings"] == {"S": 1, "B": 1}


def test_empty_summary(tmp_path) -> None:
    store = SQLiteStore(tmp_path / "lanes.sqlite3")
    store.initialize()
    reporter = ScoreReporter(store)
    summary = reporter.monthly_summary()
    assert summary["total_jobs"] == 0
    assert summary["avg_score"] == 0
