"""Bridge: simulation pipeline -> weekly_report workflow.

Formats simulation results for the weekly_report actor in the
LANEs_CEO system. Provides run table summaries and figure paths
for inclusion in the weekly report Word document.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from ..schemas import Manifest, RunTable

logger = logging.getLogger("lanes_ceo.weekly_report_bridge")


class WeeklyReportBridge:
    """Bridge between simulation pipeline outputs and weekly_report workflow.

    Provides structured data (run summaries, key metrics, figure references)
    formatted to plug into the weekly report's 8-section structure.
    """

    def build_summary(
        self,
        run_table: RunTable | None = None,
        manifests: list[Manifest] | None = None,
        figures_dir: str | Path | None = None,
    ) -> dict[str, Any]:
        """Build a weekly report summary dict.

        Args:
            run_table: Multi-run comparison table.
            manifests: List of experiment manifests.
            figures_dir: Directory containing generated figures.

        Returns:
            Dict with keys:
                - key_metrics: dict of highlight metrics (efficiency, phase_margin, etc.)
                - run_count: total number of simulation runs
                - parameter_space: dict of parameter ranges scanned
                - figures: list of figure paths for report inclusion
                - experiment_ids: list of experiment IDs
        """
        summary: dict[str, Any] = {
            "key_metrics": {},
            "run_count": 0,
            "parameter_space": {},
            "figures": [],
            "experiment_ids": [],
        }

        # Collect from manifests
        if manifests:
            summary["experiment_ids"] = [m.experiment_id for m in manifests]

            # Collect key metrics
            for m in manifests:
                for metric_name in ("efficiency", "phase_margin", "ripple_rms",
                                    "load_regulation", "line_regulation"):
                    if metric_name in m.metrics:
                        summary["key_metrics"].setdefault(metric_name, []).append(
                            m.metrics[metric_name]
                        )

                # Collect figures
                for fig in m.outputs.get("figures", []):
                    if fig not in summary["figures"]:
                        summary["figures"].append(fig)

                # Collect parameter ranges
                for param, value in m.parameters.items():
                    if param not in summary["parameter_space"]:
                        summary["parameter_space"][param] = []
                    summary["parameter_space"][param].append(value)

        # From run table
        if run_table and len(run_table) > 0:
            df = run_table.to_dataframe()
            summary["run_count"] = len(df)

            # Collect parameter ranges from dataframe columns
            for col in df.columns:
                if col not in ("run_id", "source_path", "efficiency", "steady_state_reached"):
                    try:
                        vals = df[col].dropna().unique().tolist()
                        if len(vals) > 1 and len(vals) < 50:
                            # Likely a sweep parameter, not a metric
                            if col not in summary["parameter_space"]:
                                summary["parameter_space"][col] = vals
                    except Exception:
                        pass

        # Supplement from figures directory
        if figures_dir:
            fig_path = Path(figures_dir)
            if fig_path.exists():
                for f in sorted(fig_path.glob("*.svg")):
                    if str(f) not in summary["figures"]:
                        summary["figures"].append(str(f))

        return summary
