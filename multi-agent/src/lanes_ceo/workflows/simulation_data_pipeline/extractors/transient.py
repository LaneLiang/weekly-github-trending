"""Transient response extractor: overshoot, undershoot, recovery time.

Analyzes load-step transient response from Vout waveforms.
"""

from __future__ import annotations

import logging
from typing import Any

import numpy as np

from ..config import (
    TRANSIENT_OVERSHOOT_WINDOW_FRACTION,
    TRANSIENT_SETTLING_BAND_PCT,
    resolve_signal_name,
)
from ..schemas import SimDataFrame, TransientMetrics
from . import BaseExtractor

logger = logging.getLogger("lanes_ceo.transient")


class TransientExtractor(BaseExtractor):
    """Extract load transient response metrics from Vout waveforms.

    Detects load step transitions, computes overshoot/undershoot
    percentages and recovery time.
    """

    METRIC_NAME = "transient"

    def __init__(
        self,
        vout_signal: str = "vout",
        iout_signal: str = "iout",
        steady_state_vout: float | None = None,
        settling_band_pct: float = TRANSIENT_SETTLING_BAND_PCT,
    ) -> None:
        self.vout_signal = vout_signal
        self.iout_signal = iout_signal
        self.steady_state_vout = steady_state_vout
        self.settling_band_pct = settling_band_pct

    def can_extract(self, dataframe: SimDataFrame) -> bool:
        """Transient extraction requires Vout signal with time axis."""
        if dataframe.time is None:
            return False
        vout = resolve_signal_name(list(dataframe.signals.keys()), self.vout_signal)
        return vout is not None

    def extract(self, dataframe: SimDataFrame, **kwargs: Any) -> TransientMetrics | None:
        """Extract transient response metrics.

        Returns:
            TransientMetrics with overshoot_pct, undershoot_pct, recovery_time, settling_time.
        """
        available = list(dataframe.signals.keys())
        vout_name = resolve_signal_name(available, self.vout_signal)
        if vout_name is None:
            return None

        time = dataframe.time
        if time is None:
            return None

        vout = np.asarray(dataframe.signals[vout_name], dtype=np.float64).ravel()

        # Detect load step from Iout changes
        step_indices = self._detect_load_steps(dataframe, available)
        if not step_indices:
            # Fallback: treat as single transient pulse
            return self._single_transient(time, vout)

        # Analyze each step
        metrics_list = []
        for idx in step_indices:
            metrics = self._analyze_step(time, vout, idx)
            if metrics:
                metrics_list.append(metrics)

        if not metrics_list:
            return None

        # Return worst-case metrics across all steps
        result = TransientMetrics(
            settling_band_pct=self.settling_band_pct,
        )

        overshoots = [m.overshoot_pct for m in metrics_list if m.overshoot_pct is not None]
        undershoots = [m.undershoot_pct for m in metrics_list if m.undershoot_pct is not None]
        recovery_times = [m.recovery_time for m in metrics_list if m.recovery_time is not None]
        settling_times = [m.settling_time for m in metrics_list if m.settling_time is not None]

        if overshoots:
            result.overshoot_pct = max(overshoots)
        if undershoots:
            result.undershoot_pct = max(undershoots)
        if recovery_times:
            result.recovery_time = max(recovery_times)
        if settling_times:
            result.settling_time = max(settling_times)

        return result

    def _detect_load_steps(
        self, dataframe: SimDataFrame, available: list[str]
    ) -> list[int]:
        """Detect indices where load current changes significantly."""
        iout_name = resolve_signal_name(available, self.iout_signal)
        if iout_name is None:
            return []

        iout = np.asarray(dataframe.signals[iout_name], dtype=np.float64).ravel()
        if len(iout) < 5:
            return []

        # Use gradient to find step changes
        di = np.abs(np.gradient(iout))
        threshold = 0.1 * (np.max(iout) - np.min(iout) + 1e-12)
        if threshold < 1e-9:
            return []

        # Find local maxima in |di/dt| — these are step boundaries
        step_indices: list[int] = []
        for i in range(1, len(di) - 1):
            if di[i] > threshold and di[i] >= di[i - 1] and di[i] >= di[i + 1]:
                step_indices.append(i)

        # De-duplicate close indices (within 10 samples)
        if step_indices:
            deduped: list[int] = [step_indices[0]]
            for idx in step_indices[1:]:
                if idx - deduped[-1] > 10:
                    deduped.append(idx)
            step_indices = deduped

        return step_indices

    def _analyze_step(
        self, time: np.ndarray, vout: np.ndarray, step_idx: int
    ) -> TransientMetrics | None:
        """Analyze transient response around a single load step."""
        n = len(vout)
        # Window around the step
        window_size = max(10, n // 10)
        start_idx = max(0, step_idx - window_size // 4)
        end_idx = min(n, step_idx + window_size)

        if end_idx - start_idx < 10:
            return None

        vout_window = vout[start_idx:end_idx]
        time_window = time[start_idx:end_idx]

        # Determine baseline (pre-step) and target (post-step)
        pre_step_vout = np.mean(vout_window[:window_size // 4])

        # Post-step plateau value
        plateau_start = min(len(vout_window) - 1, step_idx - start_idx + window_size // 2)
        post_step_vout = np.mean(vout_window[plateau_start:])

        if abs(post_step_vout - pre_step_vout) < 1e-9:
            return None  # No detectable change

        vout_step = post_step_vout - pre_step_vout

        # Overshoot / undershoot
        if vout_step > 0:
            # Positive step: look for overshoot (above final value)
            peak = np.max(vout_window[plateau_start:])
            overshoot = peak - post_step_vout
            undershoot = 0.0
        else:
            # Negative step: look for undershoot (below final value)
            peak = np.min(vout_window[plateau_start:])
            overshoot = 0.0
            undershoot = post_step_vout - peak

        # Settling band
        band = abs(post_step_vout) * self.settling_band_pct / 100.0
        if band < 1e-9:
            band = abs(vout_step) * 0.01

        # Recovery time: time until Vout stays within band of final value
        recovery_time = self._find_settling_time(
            time_window, vout_window, post_step_vout, band
        )

        return TransientMetrics(
            overshoot_pct=float(overshoot / abs(post_step_vout) * 100) if post_step_vout else None,
            undershoot_pct=float(undershoot / abs(post_step_vout) * 100) if post_step_vout else None,
            recovery_time=recovery_time,
            settling_time=recovery_time,
            settling_band_pct=self.settling_band_pct,
        )

    def _single_transient(self, time: np.ndarray, vout: np.ndarray) -> TransientMetrics | None:
        """Analyze single transient pulse (fallback when no load step detected)."""
        vout_mean = np.mean(vout)
        vout_max = np.max(vout)
        vout_min = np.min(vout)

        overshoot_abs = vout_max - vout_mean
        undershoot_abs = vout_mean - vout_min

        return TransientMetrics(
            overshoot_pct=float(overshoot_abs / abs(vout_mean) * 100) if vout_mean else None,
            undershoot_pct=float(undershoot_abs / abs(vout_mean) * 100) if vout_mean else None,
            recovery_time=None,
            settling_time=None,
            settling_band_pct=self.settling_band_pct,
        )

    @staticmethod
    def _find_setting_time(
        time: np.ndarray, vout: np.ndarray, target: float, band: float
    ) -> float | None:
        """Find the time when the signal permanently enters the settling band."""
        within_band = np.abs(vout - target) <= band

        # Search backwards: find the last time it left the band
        settled = False
        settle_idx = 0
        for i in range(len(within_band) - 1, -1, -1):
            if not within_band[i] and settled:
                # We found the settling point: first index after this where it stays in band
                for j in range(i + 1, len(within_band)):
                    if within_band[j]:
                        settle_idx = j
                        break
                break
            if within_band[i]:
                settled = True

        if settle_idx > 0 and settle_idx < len(time):
            return float(time[settle_idx])

        return None
