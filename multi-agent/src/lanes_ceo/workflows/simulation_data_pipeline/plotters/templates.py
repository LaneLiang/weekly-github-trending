"""DC-DC plot templates (6 templates).

Provides matplotlib-based plotting functions for common DC-DC converter
figure types. All templates return (fig, ax) so callers can further
customize before saving.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import numpy as np

from ..config import EFFICIENCY_COLORS, PLOT_STYLE_DEFAULTS

logger = logging.getLogger("lanes_ceo.plotters")

_mpl_initialized: bool = False


def _ensure_mpl() -> None:
    """Lazily apply default matplotlib style on first use."""
    global _mpl_initialized
    if _mpl_initialized:
        return
    try:
        import matplotlib.pyplot as plt
        plt.rcParams.update(PLOT_STYLE_DEFAULTS)
        _mpl_initialized = True
    except ImportError:
        _mpl_initialized = True  # Don't retry on every call
        logger.warning("matplotlib not installed — plotting disabled")


# ── Template 1: Efficiency Curve Comparison ──


def plot_efficiency_comparison(
    load_currents: list[np.ndarray] | None = None,
    efficiencies: list[np.ndarray] | None = None,
    labels: list[str] | None = None,
    xlabel: str = "Load Current (A)",
    ylabel: str = "Efficiency",
    title: str = "DC-DC Converter Efficiency Comparison",
    save_path: str | Path | None = None,
    **kwargs: Any,
) -> tuple[Any, Any]:
    """Plot efficiency curves for multiple runs/designs on the same axes.

    Args:
        load_currents: List of 1D arrays of load currents for each run.
        efficiencies: List of 1D arrays of efficiency values (0-1 or 0-100%).
        labels: Legend labels for each curve.
        xlabel: X-axis label.
        ylabel: Y-axis label.
        title: Plot title.
        save_path: Optional path to save the figure.
        **kwargs: Additional matplotlib parameters.

    Returns:
        (fig, ax) matplotlib objects.
    """
    _ensure_mpl()
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots()

    if load_currents and efficiencies:
        for i, (i_load, eta) in enumerate(zip(load_currents, efficiencies)):
            label = labels[i] if labels and i < len(labels) else f"Run {i + 1}"
            color = EFFICIENCY_COLORS[i % len(EFFICIENCY_COLORS)]
            # Convert to percentage if values are in [0, 1]
            eta_pct = np.asarray(eta) * 100.0 if np.max(eta) <= 1.0 else np.asarray(eta)
            ax.plot(i_load, eta_pct, "o-", color=color, label=label, markersize=4)

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.legend(loc="best")
    ax.grid(True, alpha=0.3)

    if save_path:
        fig.savefig(str(save_path), bbox_inches="tight")

    return fig, ax


# ── Template 2: Bode Plot (Gain + Phase) ──


def plot_bode(
    frequency: np.ndarray | None = None,
    gain_db: np.ndarray | None = None,
    phase_deg: np.ndarray | None = None,
    phase_margin: float | None = None,
    gain_margin_db: float | None = None,
    crossover_freq: float | None = None,
    title: str = "DC-DC Converter Loop Gain Bode Plot",
    save_path: str | Path | None = None,
    **kwargs: Any,
) -> tuple[Any, tuple[Any, Any]]:
    """Plot loop gain Bode diagram (gain in dB, phase in degrees).

    Args:
        frequency: Frequency axis in Hz.
        gain_db: Loop gain magnitude in dB.
        phase_deg: Loop phase in degrees.
        phase_margin: Annotated phase margin (degrees).
        gain_margin_db: Annotated gain margin (dB).
        crossover_freq: Annotated 0 dB crossover frequency (Hz).
        title: Plot title.
        save_path: Optional path to save the figure.
        **kwargs: Additional matplotlib parameters.

    Returns:
        (fig, (ax_gain, ax_phase)) matplotlib objects.
    """
    _ensure_mpl()
    import matplotlib.pyplot as plt

    fig, (ax_gain, ax_phase) = plt.subplots(2, 1, sharex=True, figsize=(6, 6))

    if frequency is not None and gain_db is not None:
        ax_gain.semilogx(frequency, gain_db, "b-")
        ax_gain.axhline(y=0, color="k", linestyle="--", alpha=0.3)
        ax_gain.set_ylabel("Gain (dB)")
        ax_gain.grid(True, alpha=0.3)

        # Annotate crossover and gain margin
        if crossover_freq is not None:
            ax_gain.axvline(x=crossover_freq, color="r", linestyle="--", alpha=0.5)
            ax_gain.annotate(
                f"f_c = {crossover_freq:.1f} Hz",
                xy=(crossover_freq, 0),
                xytext=(crossover_freq * 2, -10),
                arrowprops=dict(arrowstyle="->", color="gray"),
                fontsize=8,
            )

    if frequency is not None and phase_deg is not None:
        ax_phase.semilogx(frequency, phase_deg, "b-")
        ax_phase.axhline(y=-180, color="k", linestyle="--", alpha=0.3)
        ax_phase.set_xlabel("Frequency (Hz)")
        ax_phase.set_ylabel("Phase (deg)")
        ax_phase.grid(True, alpha=0.3)

        # Annotate phase margin
        if phase_margin is not None and crossover_freq is not None:
            phase_at_cross = -180.0 + phase_margin
            ax_phase.annotate(
                f"PM = {phase_margin:.1f} deg",
                xy=(crossover_freq, phase_at_cross),
                xytext=(crossover_freq * 2, phase_at_cross + 30),
                arrowprops=dict(arrowstyle="->", color="gray"),
                fontsize=8,
            )

    ax_gain.set_title(title)

    if save_path:
        fig.savefig(str(save_path), bbox_inches="tight")

    return fig, (ax_gain, ax_phase)


# ── Template 3: Transient Waveform ──


def plot_transient_waveform(
    time: np.ndarray | None = None,
    vout: np.ndarray | None = None,
    iout: np.ndarray | None = None,
    overshoot_pct: float | None = None,
    undershoot_pct: float | None = None,
    recovery_time: float | None = None,
    title: str = "Load Transient Response",
    save_path: str | Path | None = None,
    **kwargs: Any,
) -> tuple[Any, tuple[Any, Any]]:
    """Plot load transient response: Vout and Iout vs time.

    Args:
        time: Time axis.
        vout: Output voltage waveform.
        iout: Load current waveform.
        overshoot_pct: Overshoot percentage for annotation.
        undershoot_pct: Undershoot percentage for annotation.
        recovery_time: Recovery time for annotation.
        title: Plot title.
        save_path: Optional save path.
        **kwargs: Additional matplotlib parameters.

    Returns:
        (fig, (ax_vout, ax_iout)) matplotlib objects.
    """
    _ensure_mpl()
    import matplotlib.pyplot as plt

    fig, (ax_vout, ax_iout) = plt.subplots(2, 1, sharex=True, figsize=(6, 6))

    if time is not None and vout is not None:
        ax_vout.plot(time, vout, "b-")
        ax_vout.set_ylabel("Vout (V)")
        ax_vout.grid(True, alpha=0.3)
        # Annotation text box
        info_lines: list[str] = []
        if overshoot_pct is not None:
            info_lines.append(f"Overshoot: {overshoot_pct:.2f}%")
        if undershoot_pct is not None:
            info_lines.append(f"Undershoot: {undershoot_pct:.2f}%")
        if recovery_time is not None:
            info_lines.append(f"Recovery: {recovery_time:.2e} s")
        if info_lines:
            ax_vout.text(
                0.98, 0.95, "\n".join(info_lines),
                transform=ax_vout.transAxes, va="top", ha="right",
                bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5),
                fontsize=8,
            )

    if time is not None and iout is not None:
        ax_iout.plot(time, iout, "r-")
        ax_iout.set_xlabel("Time (s)")
        ax_iout.set_ylabel("Iout (A)")
        ax_iout.grid(True, alpha=0.3)

    ax_vout.set_title(title)

    if save_path:
        fig.savefig(str(save_path), bbox_inches="tight")

    return fig, (ax_vout, ax_iout)


# ── Template 4: Load Regulation Bar Chart ──


def plot_load_regulation(
    load_points: list[str] | None = None,
    vout_values: list[float] | None = None,
    regulation_pct: float | None = None,
    title: str = "Load Regulation",
    save_path: str | Path | None = None,
    **kwargs: Any,
) -> tuple[Any, Any]:
    """Plot load regulation as a bar chart of Vout vs load.

    Args:
        load_points: Labels for each load condition.
        vout_values: Vout at each load condition.
        regulation_pct: Overall load regulation percentage for annotation.
        title: Plot title.
        save_path: Optional save path.
        **kwargs: Additional matplotlib parameters.

    Returns:
        (fig, ax) matplotlib objects.
    """
    _ensure_mpl()
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots()

    if load_points and vout_values:
        x = np.arange(len(load_points))
        bars = ax.bar(x, vout_values, color=EFFICIENCY_COLORS[: len(vout_values)])
        ax.set_xticks(x)
        ax.set_xticklabels(load_points)
        ax.set_ylabel("Vout (V)")
        ax.set_xlabel("Load Condition")

        if regulation_pct is not None:
            ax.text(
                0.98, 0.95, f"Load Regulation: {regulation_pct:.3f}%",
                transform=ax.transAxes, va="top", ha="right",
                bbox=dict(boxstyle="round", facecolor="lightblue", alpha=0.5),
                fontsize=9,
            )

    ax.set_title(title)
    ax.grid(True, alpha=0.3, axis="y")

    if save_path:
        fig.savefig(str(save_path), bbox_inches="tight")

    return fig, ax


# ── Template 5: Ripple Comparison ──


def plot_ripple_comparison(
    run_labels: list[str] | None = None,
    ripple_rms: list[float] | None = None,
    ripple_pkpk: list[float] | None = None,
    title: str = "Output Voltage Ripple Comparison",
    save_path: str | Path | None = None,
    **kwargs: Any,
) -> tuple[Any, Any]:
    """Plot ripple comparison as a grouped bar chart.

    Args:
        run_labels: Labels for each run.
        ripple_rms: RMS ripple values.
        ripple_pkpk: Peak-to-peak ripple values.
        title: Plot title.
        save_path: Optional save path.
        **kwargs: Additional matplotlib parameters.

    Returns:
        (fig, ax) matplotlib objects.
    """
    _ensure_mpl()
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots()

    if run_labels and ripple_rms and ripple_pkpk:
        x = np.arange(len(run_labels))
        width = 0.35
        ax.bar(x - width / 2, ripple_rms, width, label="RMS Ripple", color=EFFICIENCY_COLORS[0])
        ax.bar(x + width / 2, ripple_pkpk, width, label="Pk-Pk Ripple", color=EFFICIENCY_COLORS[1])
        ax.set_xticks(x)
        ax.set_xticklabels(run_labels)
        ax.legend()

    ax.set_ylabel("Ripple Voltage (V)")
    ax.set_xlabel("Run")
    ax.set_title(title)
    ax.grid(True, alpha=0.3, axis="y")

    if save_path:
        fig.savefig(str(save_path), bbox_inches="tight")

    return fig, ax


# ── Template 6: Line Regulation ──


def plot_line_regulation(
    vin_values: np.ndarray | None = None,
    vout_values: np.ndarray | None = None,
    regulation_pct: float | None = None,
    title: str = "Line Regulation",
    save_path: str | Path | None = None,
    **kwargs: Any,
) -> tuple[Any, Any]:
    """Plot line regulation: Vout vs Vin.

    Args:
        vin_values: Input voltage sweep values.
        vout_values: Output voltage corresponding to each Vin.
        regulation_pct: Overall line regulation percentage for annotation.
        title: Plot title.
        save_path: Optional save path.
        **kwargs: Additional matplotlib parameters.

    Returns:
        (fig, ax) matplotlib objects.
    """
    _ensure_mpl()
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots()

    if vin_values is not None and vout_values is not None:
        ax.plot(vin_values, vout_values, "o-", color=EFFICIENCY_COLORS[0])
        ax.set_xlabel("Input Voltage (V)")
        ax.set_ylabel("Output Voltage (V)")

        if regulation_pct is not None:
            ax.text(
                0.98, 0.95, f"Line Regulation: {regulation_pct:.3f}%",
                transform=ax.transAxes, va="top", ha="right",
                bbox=dict(boxstyle="round", facecolor="lightblue", alpha=0.5),
                fontsize=9,
            )

    ax.set_title(title)
    ax.grid(True, alpha=0.3)

    if save_path:
        fig.savefig(str(save_path), bbox_inches="tight")

    return fig, ax


# ── Template Registry ──

TEMPLATE_REGISTRY: dict[str, Any] = {
    "efficiency": plot_efficiency_comparison,
    "bode": plot_bode,
    "transient": plot_transient_waveform,
    "load_regulation": plot_load_regulation,
    "ripple": plot_ripple_comparison,
    "line_regulation": plot_line_regulation,
}


def get_template(name: str) -> Any:
    """Look up a plot template function by name."""
    if name not in TEMPLATE_REGISTRY:
        raise KeyError(f"Unknown plot template: {name}. Available: {list(TEMPLATE_REGISTRY.keys())}")
    return TEMPLATE_REGISTRY[name]
