"""Metric extractors for simulation data pipeline."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..schemas import SimDataFrame, MetricsDict


class BaseExtractor:
    """Abstract base for metric extractors.

    Each extractor takes a SimDataFrame and populates a specific metric group.
    """

    METRIC_NAME: str = "base"

    def can_extract(self, dataframe: SimDataFrame) -> bool:
        """Check if this extractor is applicable to the given simulation type."""
        raise NotImplementedError

    def extract(self, dataframe: SimDataFrame, **kwargs: Any) -> Any:
        """Extract metrics from the dataframe. Returns extracted value(s)."""
        raise NotImplementedError
