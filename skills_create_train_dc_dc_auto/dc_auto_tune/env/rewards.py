"""Multi-objective reward function for DC-DC converter tuning."""

from dc_auto_tune.utils.types_ import RewardWeights
import math


class MultiObjectiveReward:
    """Multi-objective reward with LLM-adjustable weights.

    r = sum(w_i * r_i) - sum(lambda_j * penalty_j)
    """

    def __init__(self, vout_ref: float, weights: RewardWeights | None = None):
        self.vout_ref = vout_ref
        self.weights = weights or RewardWeights()
        self._prev_vo: float | None = None

    def update_weights(self, weights: RewardWeights):
        self.weights = weights

    def compute(self, info: dict, prev_info: dict | None = None) -> float:
        vo = info["vo"]
        error_pct = abs(self.vout_ref - vo) / self.vout_ref

        # Voltage accuracy: gaussian-shaped, peaks at perfect tracking
        r_ev = math.exp(-10 * error_pct**2)

        # Voltage ripple: penalty for consecutive vo delta
        # Use prev_info if provided, otherwise fall back to stored _prev_vo
        r_vr = 0.0
        prev_vo = None
        if prev_info is not None:
            prev_vo = prev_info.get("vo")
        elif self._prev_vo is not None:
            prev_vo = self._prev_vo

        if prev_vo is not None:
            ripple = abs(vo - prev_vo) / self.vout_ref
            r_vr = -ripple
        self._prev_vo = vo

        # Efficiency proxy: minimize conduction loss proxy
        iL = info.get("iL", 0)
        d = info.get("d", 0)
        cond_loss_proxy = iL**2 * d / max(vo * iL, 1e-6)
        r_eff = -cond_loss_proxy * 0.1

        # Overshoot penalty (only when vo > vout_ref * 1.05)
        overshoot = max(0, vo - self.vout_ref * 1.05) / self.vout_ref
        r_os = -overshoot * 10

        # Undershoot penalty (only when vo < vout_ref * 0.95)
        undershoot = max(0, self.vout_ref * 0.95 - vo) / self.vout_ref
        r_us = -undershoot * 10

        # Startup time penalty: negative early on, decays with time
        t = info.get("t", 0)
        r_ts = -math.exp(-t * 100)

        w = self.weights
        reward = (
            w.w_ev * r_ev
            + w.w_vr * r_vr
            + w.w_eff * r_eff
            + w.w_os * r_os
            + w.w_us * r_us
            + w.w_ts * r_ts
        )
        return float(reward)
