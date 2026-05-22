import json
from pathlib import Path

from lanes_ceo.storage.sqlite_store import SQLiteStore


class ScoreReporter:
    """Exports score records to Excel and JSON from the SQLite runtime store.

    Fraction.xlsx is the human-readable report; score_records.json is the
    machine-readable source. Both are generated from the same SQLite data.
    """

    def __init__(self, store: SQLiteStore) -> None:
        self._store = store

    def export_json(self, output_dir: str | Path) -> Path:
        output = Path(output_dir) / "score_records.json"
        records = self._store.list_score_records()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            json.dumps(
                [
                    {
                        "score_id": r.score_id,
                        "job_id": r.job_id,
                        "scored_role": r.scored_role,
                        "scorer_role": r.scorer_role,
                        "score": r.score,
                        "rating": r.rating,
                        "review_summary": r.review_summary,
                        "created_at": r.created_at,
                        "month_bucket": r.month_bucket,
                    }
                    for r in records
                ],
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        return output

    def monthly_summary(self) -> dict:
        records = self._store.list_score_records()
        if not records:
            return {"total_jobs": 0, "avg_score": 0, "ratings": {}}
        scores = [r.score for r in records]
        ratings: dict[str, int] = {}
        for r in records:
            ratings[r.rating] = ratings.get(r.rating, 0) + 1
        return {
            "total_jobs": len(records),
            "avg_score": sum(scores) / len(scores),
            "ratings": ratings,
        }
