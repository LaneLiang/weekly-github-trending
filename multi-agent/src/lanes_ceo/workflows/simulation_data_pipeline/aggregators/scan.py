"""Parameter scan aggregator: merge multiple run results into a RunTable."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from ..config import MAX_RUNS_PER_PAGE
from ..schemas import MetricsDict, RunTable

logger = logging.getLogger("lanes_ceo.scan")


class ParamScanAggregator:
    """Aggregate metrics from multiple simulation runs into a queryable RunTable.

    Supports parameter sweep analysis, corner analysis (TT/FF/SS/etc.),
    and Monte Carlo result collection.
    """

    def __init__(self, page_size: int = MAX_RUNS_PER_PAGE) -> None:
        self.page_size = page_size
        self._runs: list[dict[str, Any]] = []
        self._table: RunTable = RunTable()

    def add_run(
        self,
        run_id: str,
        parameters: dict[str, Any],
        metrics: MetricsDict,
        source_path: str = "",
    ) -> None:
        """Add a single run's results to the aggregator."""
        row: dict[str, Any] = {"run_id": run_id, "source_path": source_path}
        row.update(parameters)
        row.update(metrics.summary)
        self._runs.append(row)
        self._table.add_run(run_id, parameters, metrics, source_path)

    def add_batch(self, entries: list[dict[str, Any]]) -> None:
        """Add multiple runs at once. Each entry is a dict with run_id, parameters, metrics."""
        for entry in entries:
            metrics = entry.pop("metrics", MetricsDict())
            run_id = entry.pop("run_id", f"run-{len(self._runs)}")
            params = entry.pop("parameters", {})
            source = entry.pop("source_path", "")
            params.update(entry)  # Remaining keys become parameters
            self.add_run(run_id, params, metrics, source)

    def build(self) -> RunTable:
        """Return the accumulated RunTable."""
        return self._table

    def query(self, **kwargs: Any) -> RunTable:
        """Filter runs by parameter/metric values."""
        return self._table.query(**kwargs)

    def sort_by(self, column: str, ascending: bool = True) -> RunTable:
        """Sort runs by a column value."""
        return self._table.sort_by(column, ascending)

    def to_dataframe(self) -> "pd.DataFrame":
        """Export the full run table as a pandas DataFrame."""
        return self._table.to_dataframe()

    def get_pages(self) -> list[dict[str, Any]]:
        """Yield pages of runs for memory-efficient processing."""
        for i in range(0, len(self._runs), self.page_size):
            yield {
                "page": i // self.page_size + 1,
                "total_pages": (len(self._runs) + self.page_size - 1) // self.page_size,
                "runs": self._runs[i : i + self.page_size],
            }

    def n_runs(self) -> int:
        return len(self._runs)

    def __len__(self) -> int:
        return len(self._runs)

    def __repr__(self) -> str:
        return f"ParamScanAggregator(n_runs={len(self._runs)})"
