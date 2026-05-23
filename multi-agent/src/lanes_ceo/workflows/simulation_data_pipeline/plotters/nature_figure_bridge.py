"""Nature-figure integration bridge.

Provides a unified interface for generating publication-quality figures.
When nature-figure is available, delegates to it. Otherwise falls back
to bare matplotlib with a [fallback: matplotlib] label.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import numpy as np

from ..config import resolve_signal_name

logger = logging.getLogger("lanes_ceo.nature_figure_bridge")

_NATURE_FIGURE_AVAILABLE: bool = False
try:
    # Attempt to import nature-figure
    import importlib

    nature_figure_spec = importlib.util.find_spec("nature_figure")
    if nature_figure_spec is not None:
        _NATURE_FIGURE_AVAILABLE = True
except Exception:
    logger.debug("nature-figure not available, using matplotlib fallback")

_FALLBACK_LABEL = "[fallback: matplotlib]"


class NatureFigureBridge:
    """Bridge between simulation pipeline and nature-figure plotting.

    This class normalizes MetricsDict data into the schema that
    nature-figure expects, and handles the fallback path gracefully.
    """

    def __init__(self) -> None:
        self.use_fallback = not _NATURE_FIGURE_AVAILABLE
        if self.use_fallback:
            logger.info("nature-figure not available — using matplotlib fallback")

    def generate_figure(
        self,
        template_name: str,
        data: dict[str, Any],
        output_path: str | Path,
        metadata: dict[str, Any] | None = None,
    ) -> Path:
        """Generate a figure using the specified template.

        Args:
            template_name: Name of the DC-DC template:
                efficiency, bode, transient, load_regulation, ripple, line_regulation.
            data: Data dict matching the template's expected schema.
            output_path: File path for the output figure.
            metadata: Optional dict of figure metadata (author, version, etc.).

        Returns:
            Path to the generated figure file.
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if not self.use_fallback:
            try:
                return self._generate_with_nature_figure(
                    template_name, data, output_path, metadata
                )
            except Exception as exc:
                logger.warning(
                    "nature-figure generation failed (%s), falling back to matplotlib", exc
                )
                self.use_fallback = True

        # Fallback: matplotlib
        return self._generate_with_matplotlib(template_name, data, output_path)

    def _generate_with_nature_figure(
        self,
        template_name: str,
        data: dict[str, Any],
        output_path: Path,
        metadata: dict[str, Any] | None,
    ) -> Path:
        """Generate figure using the nature-figure package.

        Attempts direct import and invocation of nature-figure's generate().
        If nature-figure is installed but lacks the expected API, raises
        ImportError so the caller falls back to matplotlib.
        """
        try:
            import nature_figure
        except ImportError:
            raise ImportError("nature-figure not importable at call time")

        if not hasattr(nature_figure, "generate"):
            raise ImportError("nature-figure installed but missing 'generate' entry point")

        # Normalize data to nature-figure schema
        fig_data: dict[str, Any] = {
            "type": template_name,
            "output": str(output_path),
            "metadata": metadata or {},
            "series": [],
        }

        # Convert pipeline data keys to nature-figure series format
        for key, value in data.items():
            if key in ("title", "xlabel", "ylabel"):
                fig_data[key] = value
            elif hasattr(value, "tolist"):
                fig_data["series"].append({"label": key, "values": value.tolist()})
            elif isinstance(value, dict):
                fig_data.setdefault("params", {}).update(value)

        nature_figure.generate(**fig_data)
        return output_path

    def _generate_with_matplotlib(
        self,
        template_name: str,
        data: dict[str, Any],
        output_path: Path,
    ) -> Path:
        """Generate figure using bare matplotlib with fallback label."""
        from .templates import get_template

        template_func = get_template(template_name)

        # Determine output format from extension
        fmt = output_path.suffix.lstrip(".").lower()
        if fmt not in ("svg", "pdf", "png", "tiff", "tif", "jpg", "jpeg"):
            fmt = "svg"
            output_path = output_path.with_suffix(".svg")

        # Call the template function with data kwargs
        try:
            fig, axes = template_func(save_path=None, **data)
        except Exception as exc:
            logger.error("Matplotlib template %s failed: %s", template_name, exc)
            raise

        # Add fallback watermark subtitle
        if template_func.__doc__ and _FALLBACK_LABEL not in (data.get("title", "") or ""):
            # Add fallback annotation to the figure
            fig.text(
                0.5, 0.01, _FALLBACK_LABEL,
                ha="center", fontsize=6, color="gray", alpha=0.5,
            )

        fig.savefig(str(output_path), dpi=300, bbox_inches="tight")

        # Close figure to free memory
        import matplotlib.pyplot as plt
        plt.close(fig)

        return output_path

    def prepare_plot_data(
        self,
        template_name: str,
        dataframe: Any,
        metrics: Any | None = None,
    ) -> dict[str, Any]:
        """Map SimDataFrame + MetricsDict to template keyword arguments.

        Resolves canonical signal names to vendor-specific names present
        in the dataframe, then packs them as the kwargs each template expects.
        """
        signals: dict[str, Any] = getattr(dataframe, "signals", {}) or {}
        available = list(signals.keys())
        data: dict[str, Any] = {}

        if template_name == "efficiency":
            i_load_name = resolve_signal_name(available, "iout") or resolve_signal_name(available, "iload")
            if i_load_name:
                data["load_currents"] = [np.asarray(signals[i_load_name]).ravel()]
                # Efficiency must come from metrics (single value) or computed
                if metrics is not None and getattr(metrics, "efficiency", None) is not None:
                    data["efficiencies"] = [np.full_like(data["load_currents"][0], metrics.efficiency)]
            data.setdefault("title", "Efficiency Curve")

        elif template_name == "bode":
            freq_name = resolve_signal_name(available, "freq")
            gain_name = resolve_signal_name(available, "loop_gain") or resolve_signal_name(available, "gain")
            phase_name = resolve_signal_name(available, "loop_phase") or resolve_signal_name(available, "phase")
            if freq_name and gain_name and phase_name:
                data["frequency"] = np.asarray(signals[freq_name]).ravel()
                data["gain_db"] = np.asarray(signals[gain_name]).ravel()
                data["phase_deg"] = np.asarray(signals[phase_name]).ravel()
            if metrics is not None:
                bd = getattr(metrics, "bode", None)
                if bd is not None:
                    data["phase_margin"] = getattr(bd, "phase_margin_deg", None)
                    data["gain_margin_db"] = getattr(bd, "gain_margin_db", None)
                    data["crossover_freq"] = getattr(bd, "crossover_freq", None)
            data.setdefault("title", "Loop Gain Bode Plot")

        elif template_name in ("transient", "transient_waveform"):
            time_name = resolve_signal_name(available, "time")
            vout_name = resolve_signal_name(available, "vout")
            il_name = resolve_signal_name(available, "il")
            if time_name:
                data["time"] = np.asarray(signals[time_name]).ravel()
            if vout_name:
                data["vout"] = np.asarray(signals[vout_name]).ravel()
            if il_name:
                data["il"] = np.asarray(signals[il_name]).ravel()
            if metrics is not None:
                tr = getattr(metrics, "transient", None)
                if tr is not None:
                    data["overshoot_pct"] = getattr(tr, "overshoot_pct", None)
                    data["undershoot_pct"] = getattr(tr, "undershoot_pct", None)
                    data["recovery_time"] = getattr(tr, "recovery_time", None)
            data.setdefault("title", "Load Transient Response")

        elif template_name == "ripple":
            # plot_ripple_comparison expects {run_labels, ripple_rms, ripple_pkpk}
            label = getattr(dataframe, "meta", None)
            label_str = getattr(label, "tool", "unknown") if label else "run1"
            data["run_labels"] = [label_str]
            if metrics is not None:
                rms = getattr(metrics, "ripple_rms", None)
                pkpk = getattr(metrics, "ripple_pkpk", None)
                if rms is not None and pkpk is not None:
                    data["ripple_rms"] = [rms]
                    data["ripple_pkpk"] = [pkpk]
            # Fallback: compute from waveform if metrics unavailable
            if "ripple_rms" not in data:
                vout_name = resolve_signal_name(available, "vout")
                if vout_name:
                    vout = np.asarray(signals[vout_name]).ravel()
                    data["ripple_rms"] = [float(np.std(vout))]
                    data["ripple_pkpk"] = [float(np.ptp(vout))]
            data.setdefault("title", "Output Voltage Ripple Comparison")

        elif template_name == "load_regulation":
            i_load_name = resolve_signal_name(available, "iout") or resolve_signal_name(available, "iload")
            vout_name = resolve_signal_name(available, "vout")
            if i_load_name:
                data["load_currents"] = [np.asarray(signals[i_load_name]).ravel()]
            if vout_name:
                data["vout_values"] = [np.asarray(signals[vout_name]).ravel()]
            data.setdefault("title", "Load Regulation")

        elif template_name == "line_regulation":
            vin_name = resolve_signal_name(available, "vin")
            vout_name = resolve_signal_name(available, "vout")
            if vin_name:
                data["vin_values"] = [np.asarray(signals[vin_name]).ravel()]
            if vout_name:
                data["vout_values"] = [np.asarray(signals[vout_name]).ravel()]
            data.setdefault("title", "Line Regulation")

        logger.debug("Prepared plot data for %s: %d keys", template_name, len(data))
        return data

    def batch_generate(
        self,
        template_configs: list[dict[str, Any]],
        output_dir: str | Path,
    ) -> list[Path]:
        """Generate multiple figures from a list of configs.

        Args:
            template_configs: List of dicts with keys:
                template_name, data, filename
            output_dir: Directory for output files.

        Returns:
            List of generated file paths.
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        paths = []
        for cfg in template_configs:
            filename = cfg.get("filename", f"{cfg['template_name']}.svg")
            path = self.generate_figure(
                template_name=cfg["template_name"],
                data=cfg["data"],
                output_path=output_dir / filename,
                metadata=cfg.get("metadata"),
            )
            paths.append(path)

        return paths
