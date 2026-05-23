"""Default parameters, thresholds, and signal-name mappings for the pipeline."""

from __future__ import annotations

from pathlib import Path
from typing import Any

# ── Steady-state Detection ──

DEFAULT_STEADY_STATE_FRACTION: float = 0.2
"""Fraction of the final portion of a transient waveform to treat as steady-state."""

STEADY_STATE_VOLTAGE_TOLERANCE: float = 0.005
"""Max relative voltage change in steady-state window to consider it settled (0.5%)."""

# ── Ripple ──

RIPPLE_AC_COUPLING_FC: float = 0.1
"""Cutoff fraction for AC-coupling (relative to fsw). E.g., 0.1 * fsw."""

# ── Transient ──

TRANSIENT_SETTLING_BAND_PCT: float = 1.0
"""Default settling band as percentage of final value."""

TRANSIENT_OVERSHOOT_WINDOW_FRACTION: float = 0.3
"""Window fraction after load step to search for overshoot peak."""

# ── Bode / AC ──

BODE_INTERP_POINTS: int = 10000
"""Number of interpolation points for smooth Bode analysis."""

# ── Regulation ──

REGULATION_DEFAULT_VOUT_TARGET: float = 3.3
"""Default target Vout in volts, used for calculating regulation percentages."""

# ── Efficiency ──

EFFICIENCY_MAX_ERROR: float = 0.005
"""Maximum acceptable error in efficiency calculation (0.5%)."""

# ── File Format Extensions ──

SUPPORTED_RAW_EXTENSIONS: set[str] = {".raw", ".sw0", ".ac0", ".dc0", ".tr0"}
SUPPORTED_MAT_EXTENSIONS: set[str] = {".mat"}
SUPPORTED_VCD_EXTENSIONS: set[str] = {".vcd"}
KNOWN_EXTENSIONS: set[str] = (
    SUPPORTED_RAW_EXTENSIONS | SUPPORTED_MAT_EXTENSIONS | SUPPORTED_VCD_EXTENSIONS
)

# ── Large-file Handling ──

LARGE_FILE_THRESHOLD_BYTES: int = 500 * 1024 * 1024
"""Files larger than this trigger chunked reading (500 MB)."""

MEMMAP_THRESHOLD_BYTES: int = 100 * 1024 * 1024
"""Minimum file size to consider memory-mapping (100 MB)."""

MAX_RUNS_PER_PAGE: int = 100
"""Maximum runs to load into memory per page for RunTable."""

# ── Signal Name Mappings ──

# Canonical signal names mapped from common vendor-specific names
SIGNAL_NAME_ALIASES: dict[str, list[str]] = {
    "vin": ["vin", "v_in", "vdd", "vddc", "input_voltage", "vsource"],
    "vout": ["vout", "v_out", "output_voltage", "vload", "v(out)"],
    "iin": ["iin", "i_in", "i(vsource)", "input_current", "isource"],
    "iout": ["iout", "i_out", "i(rload)", "output_current", "iload", "i_load", "i(load)"],
    "il": ["il", "i_l", "i(l)", "inductor_current", "i(l1)"],
    "sw": ["sw", "vsw", "v_sw", "switch_node", "v(lx)", "v(sw)"],
    "gate_hs": ["gate_hs", "v_gate_hs", "vg_hs", "v(gh)"],
    "gate_ls": ["gate_ls", "v_gate_ls", "vg_ls", "v(gl)"],
    "loop_gain": ["loop_gain", "loopgain", "vdb(out)", "gain_db", "vdb(loop)"],
    "loop_phase": ["loop_phase", "phase", "vp(out)", "phase_deg", "vp(loop)"],
}

# Build a reverse map for canonical lookup
SIGNAL_CANONICAL_MAP: dict[str, str] = {}
for _canonical, _aliases in SIGNAL_NAME_ALIASES.items():
    for _alias in _aliases:
        SIGNAL_CANONICAL_MAP[_alias.lower()] = _canonical


def get_canonical_name(signal_name: str) -> str:
    """Map a vendor-specific signal name to its canonical form."""
    return SIGNAL_CANONICAL_MAP.get(signal_name.lower().strip(), signal_name)


# ── Plot Templates ──

# Matplotlib style defaults for DC-DC plots
PLOT_STYLE_DEFAULTS: dict[str, Any] = {
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.format": "svg",
    "font.family": "sans-serif",
    "font.size": 10,
    "axes.labelsize": 11,
    "axes.titlesize": 12,
    "legend.fontsize": 9,
    "lines.linewidth": 1.5,
    "figure.figsize": (6, 4),
}

# Color palette for multi-run efficiency comparisons
EFFICIENCY_COLORS: list[str] = [
    "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728",
    "#9467bd", "#8c564b", "#e377c2", "#7f7f7f",
    "#bcbd22", "#17becf",
]


def resolve_signal_name(available_signals: list[str], target_canonical: str) -> str | None:
    """Find the best-matching signal name from available signals.

    Args:
        available_signals: List of signal names present in the simulation data.
        target_canonical: Canonical signal name (e.g., 'vout', 'iin').

    Returns:
        Best-matching signal name, or None if no match found.
    """
    aliases = SIGNAL_NAME_ALIASES.get(target_canonical, [target_canonical])
    available_lower = {s.lower(): s for s in available_signals}
    for alias in aliases:
        if alias.lower() in available_lower:
            return available_lower[alias.lower()]
    return None
