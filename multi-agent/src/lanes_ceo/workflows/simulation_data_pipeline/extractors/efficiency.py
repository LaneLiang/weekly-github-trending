"""Efficiency extractor: eta = P_out / P_in from steady-state waveform integration.

Accuracy target: < 0.5% error in steady-state efficiency calculation.
"""

from __future__ import annotations

import logging
from typing import Any

import numpy as np

from ..config import (
    DEFAULT_STEADY_STATE_FRACTION,
    EFFICIENCY_MAX_ERROR,
    STEADY_STATE_VOLTAGE_TOLERANCE,
    resolve_signal_name,
)
from ..schemas import SimDataFrame, SimMeta
from . import BaseExtractor

logger = logging.getLogger("lanes_ceo.efficiency")


class EfficiencyExtractor(BaseExtractor):
    """Extract power efficiency from transient simulation waveforms.

    Computes eta = mean(Vout * Iout) / mean(Vin * Iin) over the
    steady-state window of the simulation.
    """

    METRIC_NAME = "efficiency"

    def __init__(
        self,
        vin_signal: str = "vin",
        iin_signal: str = "iin",
        vout_signal: str = "vout",
        iout_signal: str = "iout",
        steady_state_window: tuple[float, float] | None = None,
        steady_state_fraction: float = DEFAULT_STEADY_STATE_FRACTION,
    ) -> None:
        self.vin_signal = vin_signal
        self.iin_signal = iin_signal
        self.vout_signal = vout_signal
        self.iout_signal = iout_signal
        self.steady_state_window = steady_state_window
        self.steady_state_fraction = steady_state_fraction

    def can_extract(self, dataframe: SimDataFrame) -> bool:
        """Efficiency extraction requires transient simulation with time axis."""
        if dataframe.time is None:
            return False
        # Need at least vin+in or vout+iout pair
        vin_found = resolve_signal_name(list(dataframe.signals.keys()), self.vin_signal)
        iin_found = resolve_signal_name(list(dataframe.signals.keys()), self.iin_signal)
        vout_found = resolve_signal_name(list(dataframe.signals.keys()), self.vout_signal)
        iout_found = resolve_signal_name(list(dataframe.signals.keys()), self.iout_signal)
        return (vin_found is not None and iin_found is not None) or (
            vout_found is not None and iout_found is not None
        )

    def extract(self, dataframe: SimDataFrame, **kwargs: Any) -> float | None:
        """Calculate efficiency from steady-state power integration.

        Returns:
            Efficiency value in [0, 1], or None if signals are missing.
        """
        available = list(dataframe.signals.keys())
        vin_name = resolve_signal_name(available, self.vin_signal)
        iin_name = resolve_signal_name(available, self.iin_signal)
        vout_name = resolve_signal_name(available, self.vout_signal)
        iout_name = resolve_signal_name(available, self.iout_signal)

        if vin_name is None or iin_name is None:
            logger.warning("Missing input voltage/current signals for efficiency")
            return None
        if vout_name is None or iout_name is None:
            logger.warning("Missing output voltage/current signals for efficiency")
            return None

        time = dataframe.time
        if time is None or len(time) < 2:
            return None

        vin = np.asarray(dataframe.signals[vin_name], dtype=np.float64).ravel()
        iin = np.asarray(dataframe.signals[iin_name], dtype=np.float64).ravel()
        vout = np.asarray(dataframe.signals[vout_name], dtype=np.float64).ravel()
        iout = np.asarray(dataframe.signals[iout_name], dtype=np.float64).ravel()

        # Determine steady-state window
        if self.steady_state_window is not None:
            t_start, t_end = self.steady_state_window
        else:
            t_start, t_end = self._auto_steady_state_window(time)

        # Mask to steady-state region
        mask = (time >= t_start) & (time <= t_end)
        if not np.any(mask):
            logger.warning("No samples in steady-state window [%g, %g]", t_start, t_end)
            return None

        time_ss = time[mask]
        vin_ss = vin[mask]
        iin_ss = iin[mask]
        vout_ss = vout[mask]
        iout_ss = iout[mask]

        # Integrate P_in and P_out over steady-state window using trapezoidal rule
        p_in = vin_ss * iin_ss
        p_out = vout_ss * iout_ss

        p_in_avg = np.trapz(p_in, time_ss) / (time_ss[-1] - time_ss[0])
        p_out_avg = np.trapz(p_out, time_ss) / (time_ss[-1] - time_ss[0])

        if p_in_avg <= 0:
            logger.warning("Average input power is zero or negative, cannot compute efficiency")
            return None

        eta = p_out_avg / p_in_avg

        # Clamp to physically meaningful range
        if eta < 0.0 or eta > 1.0:
            logger.warning(
                "Efficiency %f is out of [0, 1] range — check signal mappings or steady-state window",
                eta,
            )
            eta = float(np.clip(eta, 0.0, 1.0))

        return float(eta)

    @staticmethod
    def _auto_steady_state_window(
        time: np.ndarray, fraction: float = DEFAULT_STEADY_STATE_FRACTION
    ) -> tuple[float, float]:
        """Auto-detect steady-state as the final fraction of the simulation."""
        if len(time) < 2:
            return float(time[0]), float(time[0])
        # Use index-based window to work correctly with both
        # ascending and descending time axes.
        n = len(time)
        start_idx = max(0, int(n * (1.0 - fraction)))
        t0 = float(time[start_idx])
        t1 = float(time[-1])
        return (min(t0, t1), max(t0, t1))
