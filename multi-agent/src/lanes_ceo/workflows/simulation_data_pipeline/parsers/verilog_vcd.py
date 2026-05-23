"""Verilog VCD (Value Change Dump) waveform parser.

Uses pyvcd for standard IEEE 1364 VCD parsing.
Extracts digital signal transitions for analog-digital co-verification.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import numpy as np

from ..schemas import SimDataFrame, SimMeta
from .base import BaseParser, RawParseError

logger = logging.getLogger("lanes_ceo.verilog_vcd")

# ── pyvcd availability ──

_PYVCD_AVAILABLE: bool = False
try:
    from vcd import VCD  # type: ignore[import-untyped]
    from vcd.reader import Token, tokenize  # type: ignore[import-untyped]

    _PYVCD_AVAILABLE = True
except ImportError:
    logger.warning("pyvcd not installed — VCD parsing disabled. Install with: pip install pyvcd")


class VCDParser(BaseParser):
    """Parser for Verilog Value Change Dump (VCD) files.

    Extracts digital logic signals into time-value pairs suitable for
    co-plotting with analog simulation results.
    """

    SUPPORTED_EXTENSIONS: set[str] = {".vcd"}
    PARSER_NAME: str = "verilog_vcd"

    def parse(self, path: Path, **kwargs: Any) -> SimDataFrame:
        """Parse a VCD file into a SimDataFrame.

        Args:
            path: Path to the .vcd file.
            **kwargs:
                signal_filter: Optional list of signal name prefixes to include.

        Returns:
            SimDataFrame with digital signal values as float arrays.
        """
        if not path.exists():
            raise RawParseError(f"File not found: {path}", path=str(path))

        if not _PYVCD_AVAILABLE:
            raise RawParseError(
                "pyvcd is required to parse VCD files. Install with: pip install pyvcd",
                path=str(path),
            )

        return self._parse_vcd(path, **kwargs)

    # Maximum VCD file size before warning (100MB). Larger files may use
    # excessive memory since pyvcd reads the entire file eagerly.
    _MAX_VCD_SIZE = 100 * 1024 * 1024

    def _parse_vcd(self, path: Path, **kwargs: Any) -> SimDataFrame:
        """Parse VCD using pyvcd and convert to SimDataFrame."""
        file_size = path.stat().st_size
        if file_size > self._MAX_VCD_SIZE:
            logger.warning(
                "VCD file %s is %.1f MB (>100MB threshold) — may exhaust memory. "
                "Consider pre-filtering signals with $dumpvars or splitting the file.",
                path.name, file_size / (1024 * 1024),
            )

        signal_filter = kwargs.get("signal_filter", [])

        with open(path, "r") as fh:
            vcd_reader = VCD(fh)

        # Collect all signal references
        signal_refs: dict[str, str] = {}  # code -> name
        for child in vcd_reader.references:
            if hasattr(child, "name") and hasattr(child, "code"):
                signal_refs[child.code] = child.name

        # Time-value data: {time: {code: value}}
        time_data: dict[int, dict[str, str]] = {}
        current_time = 0

        for tv_element in vcd_reader:
            if hasattr(tv_element, "time"):
                current_time = tv_element.time
                if current_time not in time_data:
                    time_data[current_time] = {}
            elif hasattr(tv_element, "code") and hasattr(tv_element, "value"):
                time_data.setdefault(current_time, {})[tv_element.code] = tv_element.value

        if not time_data:
            raise RawParseError("No time-value data found in VCD file", path=str(path))

        # Build uniform time axis
        time_ticks = sorted(time_data.keys())
        t_array = np.array(time_ticks, dtype=np.float64)

        # Filter signals
        codes = list(signal_refs.keys())
        if signal_filter:
            codes = [c for c in codes if any(
                signal_refs.get(c, "").startswith(prefix) for prefix in signal_filter
            )]

        # Build signal arrays (forward-fill for digital signals)
        signals: dict[str, np.ndarray] = {}
        for code in codes:
            name = self._sanitize_signal_name(signal_refs.get(code, code))
            values = np.zeros(len(time_ticks), dtype=np.float64)

            last_val = ""
            for idx, t in enumerate(time_ticks):
                if code in time_data[t]:
                    last_val = time_data[t][code]
                # Convert digital value to float
                if last_val:
                    try:
                        # Binary: '1' → 1.0, '0' → 0.0, 'x'/'z' → NaN
                        if last_val in ("1", "b1"):
                            values[idx] = 1.0
                        elif last_val in ("0", "b0"):
                            values[idx] = 0.0
                        elif last_val.lower() in ("x", "z"):
                            values[idx] = float("nan")
                        else:
                            # Multi-bit bus value, try to convert as integer
                            bin_str = last_val.lstrip("b")
                            try:
                                values[idx] = float(int(bin_str, 2))
                            except ValueError:
                                values[idx] = float("nan")
                    except (ValueError, AttributeError):
                        values[idx] = float("nan")
                else:
                    values[idx] = float("nan")

            signals[name] = values

        meta = SimMeta(
            tool="verilog",
            sim_type=".vcd",
            signal_names=list(signals.keys()),
        )

        return SimDataFrame(signals=signals, time=t_array, meta=meta)

    @staticmethod
    def _sanitize_signal_name(name: str) -> str:
        """Clean signal names for internal use."""
        return name.strip().replace(" ", "_").replace(".", "_").replace("[", "_").replace("]", "")
