"""Multi-objective reward function with online sliding-window metrics.

Each step, compute() is called with the environment's info dict.
A sliding window (deque) accumulates recent vo, iL, t, p_in, p_out values
to compute stable rolling metrics rather than per-step deltas.

The reward is a weighted sum of 7 terms:
  r_ev — voltage error (gaussian)
  r_vr — voltage ripple (peak-to-peak over window)
  r_eff — efficiency (P_out / P_in, window average)
  r_os — overshoot penalty (above +5% band)
  r_us — undershoot penalty (below -5% band)
  r_tr — transient recovery penalty (after disturbance event)
  r_ts — startup time penalty (decays with time)
"""

import math
from collections import deque

from dc_auto_tune.utils.types_ import RewardWeights


class MultiObjectiveReward:
    """Multi-objective reward with LLM-adjustable weights and online windowing."""

    def __init__(self, vout_ref: float, weights: RewardWeights | None = None,
                 window_size: int = 100):
        self.vout_ref = vout_ref
        self.weights = weights or RewardWeights()
        self.window_size = window_size
        self._vo_buf: deque[float] = deque(maxlen=window_size)
        self._il_buf: deque[float] = deque(maxlen=window_size)
        self._p_in_buf: deque[float] = deque(maxlen=window_size)
        self._p_out_buf: deque[float] = deque(maxlen=window_size)
        self._t_buf: deque[float] = deque(maxlen=window_size)
        self._first_t: float | None = None
        self._startup_done: bool = False
        self._in_transient: bool = False
        self._transient_start_t: float = 0.0
        self._last_vo_deviation_t: float = 0.0

    def update_weights(self, weights: RewardWeights):
        self.weights = weights

    def reset(self):
        """Clear sliding window and transient state. Call at start of each episode."""
        self._vo_buf.clear()
        self._il_buf.clear()
        self._p_in_buf.clear()
        self._p_out_buf.clear()
        self._t_buf.clear()
        self._first_t = None
        self._startup_done = False
        self._in_transient = False
        self._transient_start_t = 0.0
        self._last_vo_deviation_t = 0.0

    def compute(self, info: dict) -> float:
        """Compute multi-objective reward from a single step's info dict."""
        vo = info["vo"]
        t = info.get("t", 0.0)
        iL = info.get("iL", 0.0)
        p_in = info.get("p_in", 0.0)
        p_out = info.get("p_out", 0.0)

        # Track first timestamp for startup timing
        if self._first_t is None:
            self._first_t = t

        # Update sliding windows
        self._vo_buf.append(vo)
        self._il_buf.append(iL)
        self._p_in_buf.append(p_in)
        self._p_out_buf.append(p_out)
        self._t_buf.append(t)

        w = self.weights

        # 1. Voltage error — gaussian, peaks at perfect tracking
        error_pct = abs(self.vout_ref - vo) / self.vout_ref
        r_ev = math.exp(-10 * error_pct ** 2)

        # 2. Voltage ripple — peak-to-peak over window
        r_vr = self._compute_ripple()

        # 3. Efficiency — window average P_out / P_in
        r_eff = self._compute_efficiency()

        # 4. Overshoot — penalty above +5% band
        overshoot = max(0, vo - self.vout_ref * 1.05) / self.vout_ref
        r_os = -overshoot * 10

        # 5. Undershoot — penalty below -5% band (after startup)
        if self._startup_done:
            undershoot = max(0, self.vout_ref * 0.95 - vo) / self.vout_ref
            r_us = -undershoot * 10
        else:
            # During startup, undershoot is expected (Vo starts at 0)
            # Only penalize if Vo was already near target and then dropped
            r_us = 0.0
            if (len(self._vo_buf) >= 10 and
                max(list(self._vo_buf)[-10:]) > self.vout_ref * 0.8 and
                vo < self.vout_ref * 0.8):
                r_us = -(self.vout_ref * 0.8 - vo) / self.vout_ref * 5

        # 6. Startup time — decays as time progresses
        r_ts = self._compute_startup(vo, t)

        # 7. Transient recovery — penalty when recovering from disturbance
        r_tr = self._compute_transient(vo, t)

        reward = (
            w.w_ev * r_ev
            + w.w_vr * r_vr
            + w.w_eff * r_eff
            + w.w_os * r_os
            + w.w_us * r_us
            + w.w_tr * r_tr
            + w.w_ts * r_ts
        )
        return float(reward)

    def get_current_metrics(self) -> dict:
        """Return current sliding-window metric snapshot for LLM observation."""
        n = len(self._vo_buf)
        if n < 10:
            return {"vo_error_pct": 0, "vo_ripple_pct": 0, "efficiency_pct": 0,
                    "overshoot_pct": 0, "undershoot_pct": 0,
                    "startup_time_ms": 0, "recovery_time_ms": 0}

        vos = list(self._vo_buf)
        vref = self.vout_ref

        vo_mean = sum(vos) / n
        vo_error_pct = abs(vref - vo_mean) / vref * 100
        vo_ripple_pct = (max(vos) - min(vos)) / vref * 100

        p_in_sum = sum(self._p_in_buf)
        p_out_sum = sum(self._p_out_buf)
        efficiency_pct = (p_out_sum / max(p_in_sum, 1e-9)) * 100

        overshoot_pct = max(0, max(vos) - vref) / vref * 100
        undershoot_pct = max(0, vref - min(vos)) / vref * 100

        startup_ms = 0.0
        if self._first_t is not None and self._startup_done:
            startup_ms = 0.0  # startup completed, no active penalty
        elif self._first_t is not None:
            startup_ms = (self._t_buf[-1] - self._first_t) * 1000 if self._t_buf else 0

        recovery_ms = 0.0
        if self._in_transient and self._transient_start_t > 0:
            recovery_ms = max(0, (t := self._t_buf[-1] if self._t_buf else 0) - self._transient_start_t) * 1000

        return {
            "vo_error_pct": round(vo_error_pct, 3),
            "vo_ripple_pct": round(vo_ripple_pct, 3),
            "efficiency_pct": round(efficiency_pct, 1),
            "overshoot_pct": round(overshoot_pct, 3),
            "undershoot_pct": round(undershoot_pct, 3),
            "startup_time_ms": round(startup_ms, 2),
            "recovery_time_ms": round(recovery_ms, 2),
        }

    # ---- internal compute helpers ----

    def _compute_ripple(self) -> float:
        """Peak-to-peak ripple from sliding window. Returns negative penalty."""
        if len(self._vo_buf) < 10:
            return 0.0
        vos = list(self._vo_buf)
        ripple_pct = (max(vos) - min(vos)) / self.vout_ref
        return -ripple_pct

    def _compute_efficiency(self) -> float:
        """Window-average efficiency. Returns positive reward scaled to [-1, 1]."""
        if len(self._p_in_buf) < 10:
            return 0.0
        p_in_sum = sum(self._p_in_buf)
        if p_in_sum < 1e-9:
            return 0.0
        eff = sum(self._p_out_buf) / p_in_sum
        # Map [0, 1] → [-1, 1] with sigmoid-like shape centered at 0.85
        return 2 * (eff - 0.5)

    def _compute_startup(self, vo: float, t: float) -> float:
        """Startup time penalty. Strong negative early, zero once Vo reaches 90% Vref."""
        if self._startup_done:
            return 0.0
        if vo >= self.vout_ref * 0.9:
            # Check sustained: Vo stays above 0.85 for 10+ steps
            if len(self._vo_buf) >= 10:
                if all(v >= self.vout_ref * 0.85 for v in list(self._vo_buf)[-10:]):
                    self._startup_done = True
                    return 0.0
        # Before startup done: exponential decay penalty
        if self._first_t is not None:
            elapsed = t - self._first_t
            return -math.exp(-elapsed * 50)  # faster decay than before (was 100 in hardcoded)
        return -1.0

    def _compute_transient(self, vo: float, t: float) -> float:
        """Transient recovery penalty. Active when Vo deviates from steady-state band."""
        in_band = abs(vo - self.vout_ref) / self.vout_ref < 0.02

        if not in_band and not self._in_transient:
            self._in_transient = True
            self._transient_start_t = t
            self._last_vo_deviation_t = t

        if in_band and self._in_transient:
            # Check sustained return: stay in band for 20+ steps
            if len(self._vo_buf) >= 20:
                recent = list(self._vo_buf)[-20:]
                if all(abs(v - self.vout_ref) / self.vout_ref < 0.02 for v in recent):
                    self._in_transient = False
                    return 0.0
            # Still recovering
            duration = t - self._transient_start_t
            return -math.exp(-duration * 200) * 0.5

        if self._in_transient:
            duration = t - self._transient_start_t
            return -math.exp(-duration * 200) * 0.5

        return 0.0
