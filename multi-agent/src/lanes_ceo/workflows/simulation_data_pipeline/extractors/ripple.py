"""Ripple extractor: output voltage ripple RMS and peak-to-peak.

Operates on the steady-state portion of transient waveforms.
AC-couples the signal by subtracting the DC mean before computing ripple.
"""

from __future__ import annotations

import logging
from typing import Any

import numpy as np
from scipy import signal as scipy_signal

from ..config import (
    DEFAULT_STEADY_STATE_FRACTION,
    RIPPLE_AC_COUPLING_FC,
    resolve_signal_name,
)
from ..schemas import SimDataFrame
from . import BaseExtractor

logger = logging.getLogger("lanes_ceo.ripple")


class RippleExtractor(BaseExtractor):
    """Extract output voltage ripple (RMS and peak-to-peak) from transient data.

    Applies AC-coupling to remove the DC component, then computes
    ripple statistics over the steady-state window.
    """

    METRIC_NAME = "ripple"

    def __init__(
        self,
        vout_signal: str = "vout",
        steady_state_window: tuple[float, float] | None = None,
        steady_state_fraction: float = DEFAULT_STEADY_STATE_FRACTION,
        ac_coupling_fc: float | None = None,
        fsw: float | None = None,
    ) -> None:
        self.vout_signal = vout_signal
        self.steady_state_window = steady_state_window
        self.steady_state_fraction = steady_state_fraction
        self.ac_coupling_fc = ac_coupling_fc
        self.fsw = fsw

    def can_extract(self, dataframe: SimDataFrame) -> bool:
        """Ripple extraction requires transient Vout signal with time axis."""
        if dataframe.time is None:
            return False
        vout = resolve_signal_name(list(dataframe.signals.keys()), self.vout_signal)
        return vout is not None

    def extract(
        self, dataframe: SimDataFrame, **kwargs: Any
    ) -> tuple[float | None, float | None]:
        """Extract ripple RMS and peak-to-peak voltage.

        Returns:
            (ripple_rms, ripple_pkpk) tuple, each in volts.
        """
        available = list(dataframe.signals.keys())
        vout_name = resolve_signal_name(available, self.vout_signal)
        if vout_name is None:
            return None, None

        time = dataframe.time
        if time is None or len(time) < 2:
            return None, None

        vout = np.asarray(dataframe.signals[vout_name], dtype=np.float64).ravel()

        # Determine steady-state window (index-based, works with any time direction)
        if self.steady_state_window is not None:
            t_start, t_end = self.steady_state_window
        else:
            n = len(time)
            start_idx = max(0, int(n * (1.0 - self.steady_state_fraction)))
            t0 = float(time[start_idx])
            t1 = float(time[-1])
            t_start, t_end = min(t0, t1), max(t0, t1)

        mask = (time >= t_start) & (time <= t_end)
        if not np.any(mask):
            return None, None

        time_ss = time[mask]
        vout_ss = vout[mask]

        # AC-couple: subtract DC mean
        vout_ac = vout_ss - np.mean(vout_ss)

        # Optional high-pass filtering for AC coupling
        if self.ac_coupling_fc is not None and self.fsw is not None:
            time_diffs = np.diff(time_ss)
            if np.std(time_diffs) / (np.mean(time_diffs) + 1e-15) > 0.1:
                logger.warning(
                    "Non-uniform time steps detected (std/mean=%.3f); "
                    "HP filter may be inaccurate. Consider resampling.",
                    np.std(time_diffs) / np.mean(time_diffs),
                )
            try:
                fs = 1.0 / np.mean(time_diffs)
                vout_ac = self._high_pass_filter(vout_ss, self.ac_coupling_fc, fs)
            except Exception:
                pass

        # RMS ripple
        ripple_rms = float(np.sqrt(np.mean(vout_ac**2)))

        # Peak-to-peak ripple
        ripple_pkpk = float(np.max(vout_ac) - np.min(vout_ac))

        return ripple_rms, ripple_pkpk

    @staticmethod
    def _high_pass_filter(
        signal_data: np.ndarray, cutoff: float, fs: float, order: int = 2
    ) -> np.ndarray:
        """Apply a Butterworth high-pass filter for AC coupling."""
        nyq = 0.5 * fs
        normal_cutoff = cutoff / nyq
        if normal_cutoff >= 1.0:
            normal_cutoff = 0.9  # Clamp to stable range
        if normal_cutoff <= 0.0:
            return signal_data - np.mean(signal_data)

        b, a = scipy_signal.butter(order, normal_cutoff, btype="high", analog=False)
        return scipy_signal.filtfilt(b, a, signal_data)
