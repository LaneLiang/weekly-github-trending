"""7-metric evaluation for DC-DC converter controller performance."""

from dataclasses import dataclass
import numpy as np
from dc_auto_tune.utils.types_ import CircuitParams


@dataclass
class ConverterMetrics:
    """Quantitative evaluation of all 7 converter performance metrics."""

    vo_error_pct: float = 0.0
    vo_ripple_pct: float = 0.0
    efficiency_pct: float = 0.0
    recovery_time_ms: float = 0.0
    overshoot_pct: float = 0.0
    undershoot_pct: float = 0.0
    startup_time_ms: float = 0.0

    def to_dict(self) -> dict:
        return {
            "vo_error_pct": self.vo_error_pct,
            "vo_ripple_pct": self.vo_ripple_pct,
            "efficiency_pct": self.efficiency_pct,
            "recovery_time_ms": self.recovery_time_ms,
            "overshoot_pct": self.overshoot_pct,
            "undershoot_pct": self.undershoot_pct,
            "startup_time_ms": self.startup_time_ms,
        }

    def all_within(self, targets: dict) -> bool:
        """Check if all metrics are within target thresholds."""
        for key, limit in targets.items():
            if getattr(self, key, 0) > limit:
                return False
        return True


def compute_metrics(
    vo_history: np.ndarray,
    iL_history: np.ndarray,
    params: CircuitParams,
    dt: float | None = None,
) -> ConverterMetrics:
    """Compute all 7 metrics from voltage and current histories.

    Args:
        vo_history: Output voltage time series [V].
        iL_history: Inductor current time series [A].
        params: Nominal circuit parameters.
        dt: Time step in seconds (auto-computed if None).

    Returns:
        ConverterMetrics with all 7 fields populated.
    """
    vo = np.asarray(vo_history, dtype=np.float64)
    iL = np.asarray(iL_history, dtype=np.float64)

    if dt is None:
        dt = 1.0 / (params.f_sw * 50) if params.f_sw > 0 else 1e-6

    if len(vo) < 10:
        return ConverterMetrics()

    vref = params.vout_ref

    # 1. Voltage error (steady-state mean of last 20% samples)
    steady_region = vo[-max(1, len(vo) // 5):]
    vo_error_pct = float(abs(np.mean(steady_region) - vref) / vref * 100)

    # 2. Voltage ripple (peak-to-peak in steady region)
    vo_ripple_pct = float((np.max(steady_region) - np.min(steady_region)) / vref * 100)

    # 3. Efficiency (Pout/Pin proxy)
    i_out = np.mean(steady_region) / max(params.R_load, 1e-6)
    p_out = np.mean(steady_region) * i_out
    p_in = params.vin * np.mean(iL[-max(1, len(iL) // 5):])
    efficiency_pct = float(min(p_out / max(p_in, 1e-9) * 100, 100.0))

    # 4. Startup time (Vo reaches 90% of Vref and stays within ±10%)
    startup_idx = _find_settling_index(vo, vref, target_pct=0.9, band_pct=0.1)
    startup_time_ms = float(startup_idx * dt * 1000)

    # 5-6. Overshoot and undershoot
    overshoot_pct = float(max(0.0, (np.max(vo) - vref) / vref * 100))
    undershoot_pct = float(max(0.0, (vref - np.min(vo[startup_idx:])) / vref * 100)
                           if startup_idx < len(vo) else 0.0)

    # 7. Recovery time (time to return within ±2% band after worst disturbance)
    recovery_idx = _find_recovery_index(vo, vref, band_pct=0.02)
    recovery_time_ms = float(max(0, recovery_idx - startup_idx) * dt * 1000)

    return ConverterMetrics(
        vo_error_pct=vo_error_pct,
        vo_ripple_pct=vo_ripple_pct,
        efficiency_pct=efficiency_pct,
        recovery_time_ms=recovery_time_ms,
        overshoot_pct=overshoot_pct,
        undershoot_pct=undershoot_pct,
        startup_time_ms=startup_time_ms,
    )


def _find_settling_index(
    vo: np.ndarray, vref: float,
    target_pct: float = 0.9, band_pct: float = 0.1,
) -> int:
    """Find first index where Vo reaches target_pct * Vref and stays in band."""
    target = target_pct * vref
    lo = (1 - band_pct) * vref
    hi = (1 + band_pct) * vref

    for i in range(len(vo)):
        if vo[i] >= target:
            # Check if it stays within band for the rest
            if np.all((vo[i:] >= lo) & (vo[i:] <= hi)):
                return i
    return len(vo) - 1


def _find_recovery_index(
    vo: np.ndarray, vref: float, band_pct: float = 0.02,
) -> int:
    """Find index where Vo returns to within band_pct of Vref after the last
    significant disturbance (beyond 2× the band)."""
    lo = (1 - band_pct) * vref
    hi = (1 + band_pct) * vref
    threshold = band_pct * vref * 2  # significant deviation

    # Find the last region where Vo deviates significantly
    deviations = np.abs(vo - vref)
    # Scan backwards to find the last significant disturbance
    last_disturbance = len(vo) - 1
    for i in range(len(vo) - 1, -1, -1):
        if deviations[i] > threshold:
            last_disturbance = i
            break

    for i in range(last_disturbance, len(vo)):
        if lo <= vo[i] <= hi:
            return i
    return len(vo) - 1
