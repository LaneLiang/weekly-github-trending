"""Bode plot extractor: phase margin, gain margin, crossover frequency.

Analyzes AC simulation loop gain Bode data (magnitude + phase) to extract
stability metrics for DC-DC converter control loop design.
"""

from __future__ import annotations

import logging
from typing import Any

import numpy as np

from ..config import BODE_INTERP_POINTS, resolve_signal_name
from ..schemas import BodeMetrics, SimDataFrame
from . import BaseExtractor

logger = logging.getLogger("lanes_ceo.bode")


class BodeExtractor(BaseExtractor):
    """Extract phase margin, gain margin, and crossover frequency from AC data.

    Expects loop gain in dB and phase in degrees.
    """

    METRIC_NAME = "bode"

    def __init__(
        self,
        gain_signal: str = "loop_gain",
        phase_signal: str = "loop_phase",
        gain_is_db: bool = True,
        phase_is_deg: bool = True,
    ) -> None:
        self.gain_signal = gain_signal
        self.phase_signal = phase_signal
        self.gain_is_db = gain_is_db
        self.phase_is_deg = phase_is_deg

    def can_extract(self, dataframe: SimDataFrame) -> bool:
        """Bode extraction requires AC simulation with frequency axis."""
        if dataframe.frequency is None:
            return False
        gain = resolve_signal_name(list(dataframe.signals.keys()), self.gain_signal)
        return gain is not None

    def extract(self, dataframe: SimDataFrame, **kwargs: Any) -> BodeMetrics | None:
        """Extract Bode stability metrics.

        Returns:
            BodeMetrics with phase_margin_deg, gain_margin_db, crossover_freq, dc_gain_db, bandwidth_hz.
        """
        available = list(dataframe.signals.keys())
        gain_name = resolve_signal_name(available, self.gain_signal)
        phase_name = resolve_signal_name(available, self.phase_signal)

        if gain_name is None:
            logger.warning("No gain signal found for Bode extraction")
            return None

        freq = dataframe.frequency
        if freq is None or len(freq) < 2:
            return None

        gain = np.asarray(dataframe.signals[gain_name], dtype=np.float64).ravel()

        # Convert gain to dB if needed
        if not self.gain_is_db:
            # Assume linear gain magnitude
            gain_db = 20.0 * np.log10(np.abs(gain) + 1e-15)
        else:
            gain_db = gain

        phase_raw = None
        if phase_name is not None:
            phase_raw = np.asarray(dataframe.signals[phase_name], dtype=np.float64).ravel()
            if not self.phase_is_deg:
                phase_raw = phase_raw * 180.0 / np.pi

        # Interpolate to fine grid for accurate crossover detection
        freq_interp = np.logspace(
            np.log10(max(freq[0], 1e-6)),
            np.log10(freq[-1]),
            BODE_INTERP_POINTS,
        )
        gain_interp = np.interp(np.log(freq_interp), np.log(freq), gain_db)

        # Phase margin: phase at gain crossover (0 dB)
        crossover_freq: float | None = None
        phase_margin: float | None = None

        # Find 0 dB crossings
        sign_changes = np.diff(np.signbit(gain_interp))
        cross_indices = np.where(sign_changes)[0]

        if len(cross_indices) > 0:
            # Use the first 0 dB crossing (from left/top — highest gain first crossing)
            idx = cross_indices[0]
            # Linear interpolation for more accurate crossing
            if idx + 1 < len(gain_interp) and gain_interp[idx] * gain_interp[idx + 1] <= 0:
                g0, g1 = gain_interp[idx], gain_interp[idx + 1]
                f0, f1 = freq_interp[idx], freq_interp[idx + 1]
                crossover_freq = float(f0 + (f1 - f0) * abs(g0) / (abs(g0) + abs(g1)))
            else:
                crossover_freq = float(freq_interp[idx])

            # Phase at crossover
            if phase_raw is not None:
                phase_interp = np.interp(np.log(freq_interp), np.log(freq), phase_raw)
                phase_at_cross = float(np.interp(crossover_freq, freq_interp, phase_interp))
                # Phase margin = 180 + phase at crossover (for negative feedback)
                phase_margin = 180.0 + phase_at_cross
                # Normalize to [-180, 180]
                if phase_margin > 180:
                    phase_margin -= 360
                if phase_margin < -180:
                    phase_margin += 360
                phase_margin = float(phase_margin)

        # Gain margin: gain at phase crossover (-180 deg)
        gain_margin: float | None = None
        if phase_raw is not None:
            phase_interp = np.interp(np.log(freq_interp), np.log(freq), phase_raw)
            # Find -180 deg crossings on interpolated grid
            phase_for_cross = phase_interp + 180.0  # shift so we look for 0 crossings
            sign_changes_phase = np.diff(np.signbit(phase_for_cross))
            phase_cross_indices = np.where(sign_changes_phase)[0]
            if len(phase_cross_indices) > 0:
                idx = phase_cross_indices[0]
                # Gain at phase crossover (use interpolated gain)
                gain_at_phase_cross = gain_interp[idx]
                gain_margin = float(-gain_at_phase_cross)

        # DC gain (low-frequency asymptote)
        dc_idx = min(10, len(gain_db) - 1)
        dc_gain = float(np.mean(gain_db[:dc_idx]))

        # Bandwidth (-3 dB point)
        bw_hz: float | None = None
        bw_threshold = dc_gain - 3.0
        for i in range(len(gain_db)):
            if gain_db[i] <= bw_threshold:
                bw_hz = float(freq[i])
                break

        return BodeMetrics(
            phase_margin_deg=phase_margin,
            gain_margin_db=gain_margin,
            crossover_freq=crossover_freq,
            dc_gain_db=dc_gain,
            bandwidth_hz=bw_hz,
        )
