"""Bridge: simulation pipeline -> paper_research workflow.

Formats simulation results (figures + metrics) for consumption by the
paper_research actor/critic in the LANEs_CEO system.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from ..schemas import Manifest, MetricsDict, RunTable

logger = logging.getLogger("lanes_ceo.paper_research_bridge")


class PaperResearchBridge:
    """Bridge between simulation pipeline outputs and paper_research workflow.

    Formats metrics and figure paths into the schema expected by the
    paper_research actor for automated literature comparison and figure
    inclusion in manuscripts.
    """

    def build_context(
        self,
        manifest: Manifest | None = None,
        run_table: RunTable | None = None,
        figures_dir: str | Path | None = None,
    ) -> dict[str, Any]:
        """Build a context dict ready for paper_research consumption.

        Args:
            manifest: Experiment manifest with metrics and file paths.
            run_table: Multi-run comparison table.
            figures_dir: Directory containing generated figures.

        Returns:
            Dict with keys: metrics, figures, run_comparison, metadata.
        """
        ctx: dict[str, Any] = {
            "metrics": {},
            "figures": [],
            "run_comparison": None,
            "metadata": {
                "pipeline_version": "0.1.0",
                "generated_by": "simulation_data_pipeline",
            },
        }

        if manifest:
            ctx["metrics"] = manifest.metrics
            ctx["figures"] = manifest.outputs.get("figures", [])
            ctx["metadata"]["experiment_id"] = manifest.experiment_id
            ctx["metadata"]["parameters"] = manifest.parameters

        if run_table and len(run_table) > 0:
            ctx["run_comparison"] = run_table.to_dataframe().to_dict(orient="records")

        if figures_dir:
            fig_path = Path(figures_dir)
            if fig_path.exists():
                extra_figs = sorted(fig_path.glob("*.svg")) + sorted(fig_path.glob("*.pdf"))
                for f in extra_figs:
                    if str(f) not in ctx["figures"]:
                        ctx["figures"].append(str(f))

        return ctx

    def export_metrics_json(
        self,
        metrics: MetricsDict,
        output_path: str | Path,
    ) -> None:
        """Export metrics as a JSON file for paper_research ingestion.

        Args:
            metrics: MetricsDict to export.
            output_path: Path to write metrics.json.
        """
        data = metrics.summary
        with open(output_path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, ensure_ascii=False, default=str)
        logger.info("Metrics exported to %s", output_path)
