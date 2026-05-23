"""Regulation extractor: load regulation and line regulation.

Analyzes DC sweep simulations to compute:
- Load regulation: delta_Vout / delta_Iload (mV/A or %)
- Line regulation: delta_Vout / delta_Vin (mV/V or %)
"""

from __future__ import annotations

import logging
from typing import Any

import numpy as np

from ..config import REGULATION_DEFAULT_VOUT_TARGET, resolve_signal_name
from ..schemas import RegulationMetrics, SimDataFrame
from . import BaseExtractor

logger = logging.getLogger("lanes_ceo.regulation")


class RegulationExtractor(BaseExtractor):
    """Extract load and line regulation from DC sweep simulation data.

    Supports both explicit sweep variables and implicit load/line sweeps.
    """

    METRIC_NAME = "regulation"

    def __init__(
        self,
        vout_signal: str = "vout",
        iout_signal: str = "iout",
        vin_signal: str = "vin",
        vout_target: float = REGULATION_DEFAULT_VOUT_TARGET,
    ) -> None:
        self.vout_signal = vout_signal
        self.iout_signal = iout_signal
        self.vin_signal = vin_signal
        self.vout_target = vout_target

    def can_extract(self, dataframe: SimDataFrame) -> bool:
        """Regulation requires a DC sweep."""
        vout = resolve_signal_name(list(dataframe.signals.keys()), self.vout_signal)
        return vout is not None

    def extract(self, dataframe: SimDataFrame, **kwargs: Any) -> RegulationMetrics | None:
        """Extract load and line regulation metrics.

        Returns:
            RegulationMetrics with load_regulation_pct, line_regulation_pct, etc.
        """
        available = list(dataframe.signals.keys())
        vout_name = resolve_signal_name(available, self.vout_signal)
        if vout_name is None:
            return None

        vout = np.asarray(dataframe.signals[vout_name], dtype=np.float64).ravel()
        if len(vout) < 2:
            return None

        result = RegulationMetrics()

        # Try to identify sweep variable for load regulation
        iout_name = resolve_signal_name(available, self.iout_signal)
        if iout_name is not None:
            iout = np.asarray(dataframe.signals[iout_name], dtype=np.float64).ravel()
            load_reg = self._compute_load_regulation(iout, vout)
            result.load_regulation_pct = load_reg["pct"]
            result.load_regulation_absolute = load_reg["absolute"]

        # Try to identify sweep variable for line regulation
        vin_name = resolve_signal_name(available, self.vin_signal)
        if vin_name is not None:
            vin = np.asarray(dataframe.signals[vin_name], dtype=np.float64).ravel()
            # Check if Vin actually varies (is a sweep variable)
            if np.std(vin) > 1e-9 * (np.mean(vin) + 1.0):
                line_reg = self._compute_line_regulation(vin, vout)
                result.line_regulation_pct = line_reg["pct"]
                result.line_regulation_absolute = line_reg["absolute"]

        # If we have a DC sweep variable (from sweeps or primary sweep), use it
        if dataframe.sweep_variable is not None:
            sweep = dataframe.sweep_variable
            # Heuristic: check if sweep range matches typical load/line ranges
            sweep_range = np.max(sweep) - np.min(sweep)
            if sweep_range > 0.01:
                # Could be either load or line sweep — compute both possibilities
                self._extract_from_sweep(sweep, vout, result)

        return result

    def _compute_load_regulation(
        self, iout: np.ndarray, vout: np.ndarray
    ) -> dict[str, float | None]:
        """Compute load regulation from Iout sweep data.

        Load regulation = (Vout_max - Vout_min) / (Iout_max - Iout_min)
        """
        iout_span = np.max(iout) - np.min(iout)
        if iout_span < 1e-12:
            return {"pct": None, "absolute": None}

        vout_span = np.max(vout) - np.min(vout)
        # Absolute: V/A (or mV/A)
        absolute = vout_span / iout_span

        # Percentage of nominal Vout
        vout_nom = self.vout_target if self.vout_target else np.mean(vout)
        if abs(vout_nom) < 1e-12:
            return {"pct": None, "absolute": float(absolute)}

        pct = (vout_span / abs(vout_nom)) * 100.0
        return {"pct": float(pct), "absolute": float(absolute)}

    def _compute_line_regulation(
        self, vin: np.ndarray, vout: np.ndarray
    ) -> dict[str, float | None]:
        """Compute line regulation from Vin sweep data.

        Line regulation = (Vout_max - Vout_min) / (Vin_max - Vin_min)
        """
        vin_span = np.max(vin) - np.min(vin)
        if vin_span < 1e-12:
            return {"pct": None, "absolute": None}

        vout_span = np.max(vout) - np.min(vout)
        # Absolute: V/V
        absolute = vout_span / vin_span

        # Percentage: (delta_Vout / Vout_nom) / (delta_Vin / Vin_nom) * 100
        vout_nom = self.vout_target if self.vout_target else np.mean(vout)
        if abs(vout_nom) < 1e-12:
            return {"pct": None, "absolute": float(absolute)}

        pct = (vout_span / abs(vout_nom)) * 100.0
        return {"pct": float(pct), "absolute": float(absolute)}

    def _extract_from_sweep(
        self, sweep: np.ndarray, vout: np.ndarray, result: RegulationMetrics
    ) -> None:
        """Extract regulation from a generic sweep variable when type is unknown."""
        sweep_span = np.max(sweep) - np.min(sweep)
        if sweep_span < 1e-12:
            return

        vout_span = np.max(vout) - np.min(vout)
        if result.load_regulation_pct is None:
            absolute = vout_span / sweep_span
            vout_nom = self.vout_target if self.vout_target else np.mean(vout)
            pct = (vout_span / abs(vout_nom)) * 100.0 if abs(vout_nom) > 1e-12 else None
            result.load_regulation_pct = float(pct) if pct is not None else None
            result.load_regulation_absolute = float(absolute)
