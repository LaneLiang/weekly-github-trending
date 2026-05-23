"""HSpice / Spectre .raw file parser.

Uses spicelib as the primary parsing path, with an ASCII fallback
for Spectre ASCII .raw files that spicelib cannot handle.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

import numpy as np

from ..config import LARGE_FILE_THRESHOLD_BYTES, MEMMAP_THRESHOLD_BYTES
from ..schemas import SimDataFrame, SimMeta
from .base import BaseParser, RawParseError, UnsupportedSPICEVariant

logger = logging.getLogger("lanes_ceo.spice_raw")


# ── spicelib availability ──

_SPICELIB_AVAILABLE: bool = False
try:
    import spicelib  # type: ignore[import-untyped]

    _SPICELIB_AVAILABLE = True
except ImportError:
    logger.warning("spicelib not installed — SPICE .raw parsing will use ASCII fallback only")


class SpiceRawParser(BaseParser):
    """Parser for HSpice and Spectre .raw simulation output files.

    Primary path: spicelib (supports binary HSpice .raw and common ASCII variants).
    Fallback path: ASCII text parsing for Spectre ASCII .raw files.
    """

    SUPPORTED_EXTENSIONS: set[str] = {".raw", ".sw0", ".ac0", ".dc0", ".tr0"}
    PARSER_NAME: str = "spice_raw"

    def parse(self, path: Path, **kwargs: Any) -> SimDataFrame:
        """Parse a SPICE .raw file into a SimDataFrame.

        Args:
            path: Path to the .raw file.
            **kwargs:
                force_ascii_fallback: If True, skip spicelib and use ASCII parsing.
                steady_state_window: Optional (start, end) tuple for manual steady-state.

        Returns:
            SimDataFrame with parsed signals.
        """
        path_str = str(path)
        if not path.exists():
            raise RawParseError(f"File not found: {path_str}", path=path_str)

        # Check for truly empty files
        if path.stat().st_size == 0:
            raise RawParseError("File is empty (0 bytes)", path=path_str)

        force_ascii = kwargs.get("force_ascii_fallback", False)

        # Primary path: spicelib
        if _SPICELIB_AVAILABLE and not force_ascii:
            try:
                return self._parse_with_spicelib(path, **kwargs)
            except Exception as exc:
                logger.warning(
                    "spicelib parse failed for %s (%s), falling back to ASCII parser",
                    path_str,
                    exc,
                )
                # Fall through to ASCII fallback

        # ASCII fallback path
        return self._parse_ascii(path, **kwargs)

    def _parse_with_spicelib(self, path: Path, **kwargs: Any) -> SimDataFrame:
        """Primary parsing path using spicelib."""
        import spicelib  # type: ignore[import-untyped]

        file_size = path.stat().st_size
        use_memmap = file_size > MEMMAP_THRESHOLD_BYTES

        # spicelib loads the raw file into a dict-like structure
        reader = spicelib.read_raw(str(path))
        if reader is None:
            raise RawParseError("spicelib returned None", path=str(path))

        signals: dict[str, np.ndarray] = {}
        signal_units: dict[str, str] = {}

        # Extract variables (signals)
        if hasattr(reader, "variables"):
            for var in reader.variables:
                name = self._sanitize_signal_name(var.name if hasattr(var, "name") else str(var))
                data = var.data if hasattr(var, "data") else np.array([])
                if isinstance(data, list):
                    data = np.array(data, dtype=np.float64)
                elif not isinstance(data, np.ndarray):
                    data = np.array(data, dtype=np.float64)
                signals[name] = data
                if hasattr(var, "unit") and var.unit:
                    signal_units[name] = var.unit

        # Extract time/frequency/sweep axis
        time_axis = None
        freq_axis = None
        sweep_axis = None

        if hasattr(reader, "time") and reader.time is not None:
            time_axis = np.array(reader.time, dtype=np.float64)
        elif hasattr(reader, "axis") and reader.axis is not None:
            # Some sims put time under .axis
            time_axis = np.array(reader.axis, dtype=np.float64)

        if hasattr(reader, "frequency") and reader.frequency is not None:
            freq_axis = np.array(reader.frequency, dtype=np.float64)

        # Detect simulation type from flags or filename
        sim_type = self._detect_sim_type(reader, path)
        if hasattr(reader, "flags"):
            for flag_name in ("dc", "tran", "ac", "op"):
                if getattr(reader.flags, flag_name, False):
                    sim_type = f".{flag_name}"
                    break

        # Extract parameters from title/header
        meta = self._extract_meta(reader, path, sim_type)
        meta.signal_names = list(signals.keys())
        meta.units = signal_units

        return SimDataFrame(
            signals=signals,
            time=time_axis,
            frequency=freq_axis,
            sweep_variable=sweep_axis,
            meta=meta,
        )

    def _parse_ascii(self, path: Path, **kwargs: Any) -> SimDataFrame:
        """ASCII fallback parser for Spectre and other text-based .raw files.

        Handles the common SPICE ASCII raw format:
            Title: <title>
            Date: <date>
            Plotname: <name>
            Flags: <flags>
            No. Variables: <n>
            No. Points: <m>
            Variables:
                0 <name> <type>
                1 <name> <type>
            Values:
            0   <val0> <val1> ...
            1   <val0> <val1> ...
        """
        file_size = path.stat().st_size
        is_large = file_size > LARGE_FILE_THRESHOLD_BYTES

        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            if is_large:
                return self._parse_ascii_chunked(fh, path, **kwargs)
            content = fh.read()

        lines = content.splitlines()
        if not lines:
            raise RawParseError("ASCII .raw file is empty", path=str(path))

        variables: list[tuple[int, str, str]] = []  # (index, name, type)
        sim_type = ".tran"
        n_points = 0
        title = ""
        date_str = ""
        plotname = ""
        flags_str = ""
        in_header = True
        in_variables = False
        data_start_line = 0

        for i, line in enumerate(lines):
            stripped = line.strip()
            if not stripped:
                continue

            if stripped.startswith("Title:"):
                title = stripped[len("Title:"):].strip()
            elif stripped.startswith("Date:"):
                date_str = stripped[len("Date:"):].strip()
            elif stripped.startswith("Plotname:"):
                plotname = stripped[len("Plotname:"):].strip()
            elif stripped.startswith("Flags:"):
                flags_str = stripped[len("Flags:"):].strip()
                sim_type = self._flags_to_sim_type(flags_str)
            elif stripped.startswith("No. Variables:"):
                n_vars = int(stripped.split(":")[1].strip())
                in_variables = True
            elif stripped.startswith("No. Points:"):
                n_points = int(stripped.split(":")[1].strip())
            elif stripped == "Variables:":
                in_variables = True
                continue
            elif stripped == "Values:":
                in_header = False
                in_variables = False
                data_start_line = i + 1
                break
            elif in_variables:
                parts = stripped.split()
                if len(parts) >= 3:
                    idx = int(parts[0])
                    name = parts[1]
                    vtype = parts[2]
                    variables.append((idx, self._sanitize_signal_name(name), vtype))

        if not variables:
            raise RawParseError("No variables found in ASCII .raw header", path=str(path))

        # Parse data section
        data_lines = lines[data_start_line:]
        n_var = len(variables)
        data_matrix = np.zeros((n_points, n_var), dtype=np.float64)

        row = 0
        for line in data_lines:
            stripped = line.strip()
            if not stripped or stripped == "Values:":
                continue
            # Remove leading row index
            parts = stripped.split()
            if len(parts) >= 2:
                # First token may be row index
                try:
                    int(parts[0])
                    values = parts[1:]
                except ValueError:
                    values = parts

                if row < n_points:
                    for col, val in enumerate(values[:n_var]):
                        try:
                            data_matrix[row, col] = float(val)
                        except (ValueError, IndexError):
                            pass
                    row += 1

        # Truncate to actual rows read
        data_matrix = data_matrix[:row, :]

        # Build signals dict
        signals: dict[str, np.ndarray] = {}
        signal_names: list[str] = []
        for idx, name, vtype in variables:
            if idx < data_matrix.shape[1]:
                signals[name] = data_matrix[:, idx]
                signal_names.append(name)

        # Identify time/freq/sweep axis — first column by convention
        time_axis = None
        freq_axis = None
        if variables and variables[0][2].lower() in ("time", "frequency", "freq"):
            if "freq" in variables[0][2].lower():
                freq_axis = signals.get(variables[0][1])
            else:
                time_axis = signals.get(variables[0][1])

        meta = SimMeta(
            tool="spectre" if "spectre" in plotname.lower() else "hspice",
            sim_type=sim_type,
            signal_names=signal_names,
            comments=[title, plotname],
        )

        return SimDataFrame(
            signals=signals,
            time=time_axis,
            frequency=freq_axis,
            meta=meta,
        )

    def _parse_ascii_chunked(self, fh: Any, path: Path, **kwargs: Any) -> SimDataFrame:
        """Chunked ASCII parser for large files (>500MB). Uses memmap internally."""
        # For large files, we read the header first, then stream the data
        header_lines: list[str] = []
        for line in fh:
            header_lines.append(line.rstrip())
            if line.strip() == "Values:":
                break

        # Parse header
        variables: list[tuple[int, str, str]] = []
        sim_type = ".tran"
        n_points = 0
        in_variables = False

        for line in header_lines:
            stripped = line.strip()
            if stripped.startswith("Flags:"):
                sim_type = self._flags_to_sim_type(stripped[len("Flags:"):].strip())
            elif stripped.startswith("No. Variables:"):
                in_variables = True
            elif stripped.startswith("No. Points:"):
                n_points = int(stripped.split(":")[1].strip())
            elif in_variables and stripped and not stripped.startswith("No."):
                parts = stripped.split()
                if len(parts) >= 3:
                    try:
                        idx = int(parts[0])
                        name = parts[1]
                        vtype = parts[2]
                        variables.append((idx, self._sanitize_signal_name(name), vtype))
                    except ValueError:
                        pass

        n_var = len(variables)
        if n_var == 0 or n_points == 0:
            raise RawParseError("Could not parse ASCII header for chunked file", path=str(path))

        # Stream data rows into numpy array
        data = np.zeros((n_points, n_var), dtype=np.float64)
        row = 0
        for line in fh:
            stripped = line.strip()
            if not stripped:
                continue
            parts = stripped.split()
            if len(parts) >= 2:
                try:
                    int(parts[0])
                    values = parts[1:]
                except ValueError:
                    values = parts
                if row < n_points:
                    for col, val in enumerate(values[:n_var]):
                        try:
                            data[row, col] = float(val)
                        except (ValueError, IndexError):
                            pass
                    row += 1

        data = data[:row, :]

        signals: dict[str, np.ndarray] = {}
        signal_names: list[str] = []
        for idx, name, vtype in variables:
            if idx < data.shape[1]:
                signals[name] = data[:, idx]
                signal_names.append(name)

        time_axis = None
        if variables and variables[0][2].lower() in ("time",):
            time_axis = signals.get(variables[0][1])

        meta = SimMeta(
            tool="hspice",
            sim_type=sim_type,
            signal_names=signal_names,
        )

        return SimDataFrame(
            signals=signals,
            time=time_axis,
            meta=meta,
        )

    # ── helpers ──

    @staticmethod
    def _sanitize_signal_name(name: str) -> str:
        """Replace spaces with underscores; preserve UTF-8 characters."""
        return name.strip().replace(" ", "_")

    @staticmethod
    def _detect_sim_type(reader: Any, path: Path) -> str:
        """Detect simulation type from spicelib reader or filename conventions."""
        fname = path.stem.lower()
        if any(kw in fname for kw in ("tran", "transient")):
            return ".tran"
        if any(kw in fname for kw in ("dc", "sweep")):
            return ".dc"
        if any(kw in fname for kw in ("ac", "bode", "loop", "stb")):
            return ".ac"
        if any(kw in fname for kw in ("op", "operating", "dcop")):
            return ".op"
        # Check the reader object for clues
        if hasattr(reader, "flags"):
            flags = reader.flags
            for flag_name in ("dc", "tran", "ac", "op"):
                if getattr(flags, flag_name, None):
                    return f".{flag_name}"
        return ".tran"  # Default assumption

    @staticmethod
    def _flags_to_sim_type(flags_str: str) -> str:
        """Convert SPICE ASCII flags string to sim type."""
        flags_lower = flags_str.lower()
        if "dc" in flags_lower:
            return ".dc"
        if "ac" in flags_lower:
            return ".ac"
        if "tran" in flags_lower or "transient" in flags_lower:
            return ".tran"
        if "op" in flags_lower:
            return ".op"
        return ".tran"

    @staticmethod
    def _extract_meta(reader: Any, path: Path, sim_type: str) -> SimMeta:
        """Extract metadata from spicelib reader object."""
        tool = "unknown"
        if hasattr(reader, "title"):
            title = str(reader.title).lower() if reader.title else ""
            if "hspice" in title:
                tool = "hspice"
            elif "spectre" in title:
                tool = "spectre"

        comments = []
        if hasattr(reader, "title") and reader.title:
            comments.append(str(reader.title))
        if hasattr(reader, "date") and reader.date:
            comments.append(str(reader.date))

        return SimMeta(
            tool=tool,
            sim_type=sim_type,
            comments=comments,
        )
