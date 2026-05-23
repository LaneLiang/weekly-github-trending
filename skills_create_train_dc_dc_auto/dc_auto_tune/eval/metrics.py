"""Multi-objective evaluation metrics for DC-DC converter controller performance.

Includes: per-trial 7-metric computation, tiered P0/P1/P2 pass-rate checking,
hypervolume (HV), C-metric (coverage), and Preference Satisfaction Rate (PSR).
"""

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
    p_in_history: np.ndarray | None = None,
    p_out_history: np.ndarray | None = None,
    load_step_idx: int | None = None,
) -> ConverterMetrics:
    """Compute all 7 metrics from voltage and current histories.

    Args:
        vo_history: Output voltage time series [V].
        iL_history: Inductor current time series [A].
        params: Nominal circuit parameters.
        dt: Time step in seconds between consecutive samples.
        p_in_history: Optional input power per step [W] from env info.
        p_out_history: Optional output power per step [W] from env info.
        load_step_idx: Index where load step occurs (for recovery time).

    Returns:
        ConverterMetrics with all 7 fields populated.
    """
    vo = np.asarray(vo_history, dtype=np.float64)
    iL = np.asarray(iL_history, dtype=np.float64)

    if dt is None:
        dt = 1.0 / params.f_sw if params.f_sw > 0 else 1e-6

    if len(vo) < 10:
        return ConverterMetrics()

    vref = params.vout_ref

    # 1. Voltage error (steady-state mean of last 20% samples)
    steady_region = vo[-max(1, len(vo) // 5):]
    vo_error_pct = float(abs(np.mean(steady_region) - vref) / vref * 100)

    # 2. Voltage ripple (peak-to-peak in steady region)
    vo_ripple_pct = float((np.max(steady_region) - np.min(steady_region)) / vref * 100)

    # 3. Efficiency (Pout/Pin). Prefer env-provided power when available.
    if p_in_history is not None and p_out_history is not None and len(p_in_history) > 0:
        # Use last 20% for steady-state efficiency
        n_steady = max(1, len(p_in_history) // 5)
        p_in_avg = float(np.mean(p_in_history[-n_steady:]))
        p_out_avg = float(np.mean(p_out_history[-n_steady:]))
        efficiency_pct = float(min(p_out_avg / max(p_in_avg, 1e-9) * 100, 100.0))
    else:
        # Fallback: approximate using duty cycle Vout/Vin for buck topology
        vout_avg = float(np.mean(steady_region))
        i_out = vout_avg / max(params.R_load, 1e-6)
        p_out = vout_avg * i_out
        iL_avg = float(np.mean(iL[-max(1, len(iL) // 5):]))
        duty_approx = vout_avg / max(params.vin, 1e-6)
        p_in = params.vin * iL_avg * min(duty_approx, 1.0)
        efficiency_pct = float(min(p_out / max(p_in, 1e-9) * 100, 100.0))

    # 4. Startup time (Vo reaches 90% of Vref and stays within ±10%)
    startup_idx = _find_settling_index(vo, vref, target_pct=0.9, band_pct=0.1)
    startup_time_ms = float(startup_idx * dt * 1000)

    # 5. Overshoot: max above Vref after startup (not initial ramp)
    overshoot_pct = float(max(0.0, (np.max(vo[startup_idx:]) - vref) / vref * 100))

    # 6. Undershoot: max below Vref after load step, or in steady region
    if load_step_idx is not None and load_step_idx < len(vo):
        undershoot_pct = float(max(0.0, (vref - np.min(vo[load_step_idx:])) / vref * 100))
    else:
        undershoot_pct = float(max(0.0, (vref - np.min(vo[-max(1, len(vo)//5):])) / vref * 100))

    # 7. Recovery time: time to return within ±2% band after load step
    if load_step_idx is not None and load_step_idx < len(vo):
        recovery_idx = _find_recovery_index(vo, vref, band_pct=0.02, start_idx=load_step_idx)
        recovery_time_ms = float(max(0, recovery_idx - load_step_idx) * dt * 1000)
    else:
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
    start_idx: int | None = None,
) -> int:
    """Find index where Vo returns to within band_pct of Vref after a disturbance.

    If start_idx is provided, measures recovery from that index (e.g. load step).
    Otherwise scans backwards to find the last significant disturbance.
    """
    lo = (1 - band_pct) * vref
    hi = (1 + band_pct) * vref
    threshold = band_pct * vref * 2  # significant deviation

    if start_idx is not None:
        disturbance_idx = start_idx
    else:
        deviations = np.abs(vo - vref)
        disturbance_idx = len(vo) - 1
        for i in range(len(vo) - 1, -1, -1):
            if deviations[i] > threshold:
                disturbance_idx = i
                break

    for i in range(disturbance_idx, len(vo)):
        if lo <= vo[i] <= hi:
            return i
    return len(vo) - 1


# ---- Multi-objective evaluation: tiered specs, HV, C-metric, PSR ----


# P0/P1/P2 tier definitions from SPECS.md
# Each tier maps metric_name -> (limit, direction)
# direction: "lt" = lower is better, "gt" = higher is better
TIER_SPECS: dict[str, dict[str, tuple[float, str]]] = {
    "P0": {
        "vo_error_pct": (0.5, "lt"),
        "vo_ripple_pct": (2.0, "lt"),
        "overshoot_pct": (5.0, "lt"),
        "undershoot_pct": (5.0, "lt"),
        "recovery_time_ms": (0.5, "lt"),
        "startup_time_ms": (10.0, "lt"),
        "efficiency_pct": (88.0, "gt"),
    },
    "P1": {
        "vo_error_pct": (0.2, "lt"),
        "vo_ripple_pct": (1.0, "lt"),
        "overshoot_pct": (2.0, "lt"),
        "undershoot_pct": (2.0, "lt"),
        "recovery_time_ms": (0.2, "lt"),
        "startup_time_ms": (5.0, "lt"),
        "efficiency_pct": (92.0, "gt"),
    },
    "P2": {
        "vo_error_pct": (0.1, "lt"),
        "vo_ripple_pct": (0.5, "lt"),
        "overshoot_pct": (1.0, "lt"),
        "undershoot_pct": (1.0, "lt"),
        "recovery_time_ms": (0.1, "lt"),
        "startup_time_ms": (3.0, "lt"),
        "efficiency_pct": (95.0, "gt"),
    },
}

# Metrics where lower is better (for HV normalization direction)
_LOWER_BETTER = {"vo_error_pct", "vo_ripple_pct", "overshoot_pct",
                 "undershoot_pct", "recovery_time_ms", "startup_time_ms"}
_HIGHER_BETTER = {"efficiency_pct"}

# Reference point for Hypervolume (slightly worse than P0)
HV_REFERENCE: dict[str, float] = {
    "vo_error_pct": 1.0,
    "vo_ripple_pct": 5.0,
    "overshoot_pct": 10.0,
    "undershoot_pct": 10.0,
    "recovery_time_ms": 2.0,
    "startup_time_ms": 20.0,
    "efficiency_pct": 80.0,
}


def check_tier(metrics: dict, tier: str = "P0") -> tuple[bool, dict[str, bool]]:
    """Check whether a metrics dict passes a given tier.

    Returns (all_pass, per_metric_results).
    """
    spec = TIER_SPECS[tier]
    results: dict[str, bool] = {}
    for key, (limit, direction) in spec.items():
        val = metrics.get(key, float("inf") if direction == "lt" else 0)
        if direction == "lt":
            results[key] = val < limit
        else:
            results[key] = val > limit
    all_pass = all(results.values())
    return all_pass, results


def tier_pass_rate(list_of_metrics: list[dict], tier: str = "P0") -> dict:
    """Compute tier pass rate across multiple trials.

    Returns dict with per-metric pass rates and overall pass rate.
    """
    n = len(list_of_metrics)
    if n == 0:
        return {"overall": 0.0}
    spec = TIER_SPECS[tier]
    counts = {k: 0 for k in spec}
    all_pass_count = 0
    for m in list_of_metrics:
        passed, per = check_tier(m, tier)
        if passed:
            all_pass_count += 1
        for k in spec:
            if per.get(k, False):
                counts[k] += 1
    return {
        "overall": all_pass_count / n,
        **{k: v / n for k, v in counts.items()},
        "n_trials": n,
    }


def _normalize_metrics(metrics: dict) -> np.ndarray:
    """Normalize metrics to [0, 1] where 1 = best (at reference point), 0 = perfect.

    For lower-better metrics: 1 at reference, 0 at 0.
    For higher-better metrics: 1 at reference, 0 at 1.0 (100%).
    """
    vec = []
    for key in sorted(_LOWER_BETTER | _HIGHER_BETTER):
        val = metrics.get(key, HV_REFERENCE.get(key, 1.0))
        ref = HV_REFERENCE.get(key, 1.0)
        if key in _LOWER_BETTER:
            # Normalize: clipped to [0, ref], then 1 - val/ref so better = higher
            norm = 1.0 - min(max(val, 0.0), ref) / max(ref, 1e-9)
        else:
            # Higher is better: normalize to [0, 1], 1 = 100%
            norm = min(max(val, 0.0), 100.0) / 100.0
        vec.append(max(norm, 0.0))
    return np.array(vec, dtype=np.float64)


def compute_hypervolume(metrics_list: list[dict]) -> float:
    """Compute Hypervolume of a Pareto-approximation set relative to HV_REFERENCE.

    Uses a simple Monte Carlo estimator (10k samples) since dimensionality is
    moderate (7 objectives).

    Args:
        metrics_list: List of metric dicts (one per trial/front point).

    Returns:
        Hypervolume as fraction of total reference volume [0, 1].
    """
    if not metrics_list:
        return 0.0

    points = np.array([_normalize_metrics(m) for m in metrics_list])
    n_obj = points.shape[1]
    n_samples = 10000

    # Find reference point (all zeros after normalization for lower-better flipped)
    # Actually after normalization, 0 = worst, 1 = best.
    # HV = volume of space dominated by the front AND bounded by reference.
    # Reference is at all-zeros. We count samples that are dominated by any point.
    samples = np.random.random((n_samples, n_obj))
    dominated = np.zeros(n_samples, dtype=bool)
    for p in points:
        dominated |= np.all(samples <= p, axis=1)
    return float(np.mean(dominated))


def compute_c_metric(set_a: list[dict], set_b: list[dict]) -> float:
    """Coverage metric C(A, B): fraction of B points dominated by at least one A point.

    C(A, B) = 1 means every point in B is dominated by some point in A.
    C(A, B) = 0 means no B point is dominated by A.

    Args:
        set_a: List of metric dicts for strategy A.
        set_b: List of metric dicts for strategy B.

    Returns:
        C(A, B) in [0, 1].
    """
    if not set_a or not set_b:
        return 0.0
    pts_a = np.array([_normalize_metrics(m) for m in set_a])
    pts_b = np.array([_normalize_metrics(m) for m in set_b])
    dominated_count = 0
    for b in pts_b:
        if np.any(np.all(b <= pts_a, axis=1)):
            dominated_count += 1
    return dominated_count / len(pts_b)


def compute_psr(
    metrics_list: list[dict],
    preference: str,
    weights: dict[str, float] | None = None,
) -> float:
    """Preference Satisfaction Rate: how well the front aligns with user preference.

    Computes weighted score for each point using preference weights, then
    measures the ratio of weighted score for the best point vs an equally
    weighted baseline.

    Args:
        metrics_list: List of metric dicts.
        preference: Semantic label (e.g. "efficiency", "transient", "ripple", "balanced").
        weights: Optional explicit weight mapping. If None, uses preference label.

    Returns:
        PSR score in [0, 1] where higher = better alignment.
    """
    if not metrics_list:
        return 0.0

    preference_weights = weights or _preference_to_weights(preference)
    if not preference_weights:
        return 0.5

    points = np.array([_normalize_metrics(m) for m in metrics_list])
    metric_order = sorted(_LOWER_BETTER | _HIGHER_BETTER)

    # Weighted score for each point
    w = np.array([preference_weights.get(k, 0.0) for k in metric_order])
    w = w / max(np.sum(w), 1e-9)

    weighted_scores = points @ w

    # Equal-weight baseline
    uniform_w = np.ones(len(metric_order)) / len(metric_order)
    uniform_scores = points @ uniform_w

    # PSR = (max weighted - max uniform) / max uniform, clipped
    best_weighted = np.max(weighted_scores)
    best_uniform = np.max(uniform_scores)
    if best_uniform < 1e-9:
        return 0.5
    psr = (best_weighted - best_uniform) / best_uniform
    return float(np.clip(psr, -1.0, 1.0))


def _preference_to_weights(preference: str) -> dict[str, float]:
    """Map semantic preference to metric weight vector."""
    mapping = {
        "efficiency": {"efficiency_pct": 3.0, "vo_error_pct": 0.5, "vo_ripple_pct": 0.3,
                       "overshoot_pct": 0.3, "undershoot_pct": 0.3,
                       "recovery_time_ms": 0.3, "startup_time_ms": 0.3},
        "transient": {"recovery_time_ms": 2.0, "overshoot_pct": 2.0, "undershoot_pct": 2.0,
                      "vo_error_pct": 0.5, "vo_ripple_pct": 0.3, "efficiency_pct": 0.3,
                      "startup_time_ms": 0.5},
        "ripple": {"vo_ripple_pct": 3.0, "vo_error_pct": 1.0, "efficiency_pct": 0.5,
                   "overshoot_pct": 0.3, "undershoot_pct": 0.3,
                   "recovery_time_ms": 0.3, "startup_time_ms": 0.3},
        "balanced": {"vo_error_pct": 1.0, "vo_ripple_pct": 1.0, "efficiency_pct": 1.0,
                     "overshoot_pct": 1.0, "undershoot_pct": 1.0,
                     "recovery_time_ms": 1.0, "startup_time_ms": 1.0},
    }
    return mapping.get(preference, mapping["balanced"])
