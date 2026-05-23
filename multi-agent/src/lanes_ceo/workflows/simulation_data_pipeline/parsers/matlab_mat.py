"""MATLAB .mat file parser.

Supports v5, v7 (via scipy.io.loadmat) and v7.3 (via h5py).
Automatically flattens struct and cell arrays into the unified SimDataFrame schema.
"""

from __future__ import annotations

import logging
import struct
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

from ..schemas import SimDataFrame, SimMeta
from .base import BaseParser, RawParseError

logger = logging.getLogger("lanes_ceo.matlab_mat")

# ── h5py availability ──

_H5PY_AVAILABLE: bool = False
try:
    import h5py

    _H5PY_AVAILABLE = True
except ImportError:
    logger.warning("h5py not installed — MATLAB v7.3 .mat files will not be parseable")


class MatlabMatParser(BaseParser):
    """Parser for MATLAB .mat files, v5/v7/v7.3.

    Extracts time-series data from Simulink Scope, To Workspace blocks,
    or manually saved workspace variables.
    """

    SUPPORTED_EXTENSIONS: set[str] = {".mat"}
    PARSER_NAME: str = "matlab_mat"

    def parse(self, path: Path, **kwargs: Any) -> SimDataFrame:
        """Parse a .mat file into a SimDataFrame.

        Args:
            path: Path to the .mat file.
            **kwargs:
                signal_name_map: Dict mapping .mat variable names to canonical signal names.
                time_var: Name of the time variable (default: auto-detect).
        """
        if not path.exists():
            raise RawParseError(f"File not found: {path}", path=str(path))

        version = self._detect_version(path)
        if version == 3 and not _H5PY_AVAILABLE:
            raise RawParseError(
                "MATLAB v7.3 .mat file requires h5py. Install with: pip install h5py",
                path=str(path),
            )

        if version == 3:
            return self._parse_v73(path, **kwargs)
        else:
            return self._parse_v5_v7(path, **kwargs)

    def _parse_v5_v7(self, path: Path, **kwargs: Any) -> SimDataFrame:
        """Parse v5/v7 .mat files using scipy.io.loadmat."""
        import scipy.io as sio

        mat_data = sio.loadmat(str(path), struct_as_record=False, squeeze_me=True)

        signals: dict[str, np.ndarray] = {}
        time_axis: np.ndarray | None = None
        signal_names: list[str] = []

        # Filter out MATLAB internal keys (starting with __)
        var_names = [k for k in mat_data.keys() if not k.startswith("__")]

        for vname in var_names:
            value = mat_data[vname]

            # Handle Simulink time series structs
            if hasattr(value, "dtype") and value.dtype.names:
                # It's a structured array (e.g., Simulink timeseries)
                value = self._flatten_struct(value)

            # Skip non-numeric or non-array values
            if not isinstance(value, np.ndarray):
                # Try to convert scalars
                try:
                    value = np.atleast_1d(np.float64(value))
                except (ValueError, TypeError):
                    continue

            if value.size == 0:
                continue

            # Detect time variable by name
            sanitized = self._sanitize_signal_name(vname)
            if sanitized.lower() in ("time", "t", "tout"):
                time_axis = np.atleast_1d(value.ravel()).astype(np.float64)
            else:
                signals[sanitized] = np.atleast_1d(value.ravel()).astype(np.float64)
                signal_names.append(sanitized)

        meta = SimMeta(
            tool="matlab",
            sim_type=".mat",
            timestamp=datetime.now(timezone.utc).replace(tzinfo=None),
            signal_names=signal_names,
        )

        return SimDataFrame(signals=signals, time=time_axis, meta=meta)

    def _parse_v73(self, path: Path, **kwargs: Any) -> SimDataFrame:
        """Parse v7.3 .mat files using h5py."""
        import h5py

        signals: dict[str, np.ndarray] = {}
        time_axis: np.ndarray | None = None
        signal_names: list[str] = []

        with h5py.File(str(path), "r") as f:
            for key in f.keys():
                if key.startswith("#refs#") or key.startswith("_"):
                    continue

                dataset: Any = f[key]

                try:
                    # Handle HDF5 references (links to other datasets)
                    if isinstance(dataset, h5py.Group):
                        data = self._extract_h5_group(dataset)
                    else:
                        data = np.array(dataset[:], dtype=np.float64)

                    if data is None or data.size == 0:
                        continue

                    sanitized = self._sanitize_signal_name(key)
                    data_flat = data.ravel() if data.ndim > 1 else data

                    if sanitized.lower() in ("time", "t", "tout"):
                        time_axis = data_flat.astype(np.float64)
                    else:
                        signals[sanitized] = data_flat.astype(np.float64)
                        signal_names.append(sanitized)

                except Exception as exc:
                    logger.debug("Skipping h5 key %s: %s", key, exc)
                    continue

        meta = SimMeta(
            tool="matlab",
            sim_type=".mat",
            timestamp=datetime.now(timezone.utc).replace(tzinfo=None),
            signal_names=signal_names,
        )

        return SimDataFrame(signals=signals, time=time_axis, meta=meta)

    # ── helpers ──

    @staticmethod
    def _detect_version(path: Path) -> int:
        """Detect .mat file version from magic bytes.

        Returns:
            1: v4 or earlier
            2: v5/v7
            3: v7.3 (HDF5 based)
        """
        with open(path, "rb") as fh:
            magic = fh.read(8)
        # v7.3 files start with HDF5 magic
        if magic[:4] == b"\x89HDF":
            return 3
        # v5/v7 start with specific MATLAB header
        if len(magic) >= 4:
            # MATLAB level 5 format has a 128-byte header starting with text
            header_text = magic[:4]
            if header_text.startswith(b"MATL"):
                return 2
        return 1

    @staticmethod
    def _flatten_struct(arr: np.ndarray) -> np.ndarray:
        """Flatten a numpy structured array into a simple 1D or 2D array."""
        if arr.dtype.names is None:
            return arr

        # Take the first field as the primary data
        first_field = arr.dtype.names[0]
        return arr[first_field]

    @staticmethod
    def _extract_h5_group(group: "h5py.Group", depth: int = 0) -> np.ndarray | None:
        """Recursively extract data from an HDF5 group, handling references and nested groups."""
        if depth > 4:
            return None
        # Try common Simulink timeseries patterns
        for key in ("values", "data"):
            if key in group:
                ds = group[key]
                if isinstance(ds, h5py.Dataset):
                    return np.array(ds[:], dtype=np.float64)
        # Handle HDF5 object references (#refs#)
        if "#refs#" in group:
            try:
                refs = group["#refs#"]
                if isinstance(refs, h5py.Dataset) and refs.dtype.kind == "O":
                    deref = refs[0]
                    if isinstance(deref, h5py.Group):
                        return MatlabMatParser._extract_h5_group(deref, depth + 1)
            except Exception:
                pass
        # Traverse sub-groups and datasets
        for subkey in group.keys():
            if subkey.startswith("#"):
                continue
            ds = group[subkey]
            if isinstance(ds, h5py.Dataset):
                try:
                    return np.array(ds[:], dtype=np.float64)
                except Exception:
                    pass
            elif isinstance(ds, h5py.Group):
                result = MatlabMatParser._extract_h5_group(ds, depth + 1)
                if result is not None:
                    return result
        return None

    @staticmethod
    def _sanitize_signal_name(name: str) -> str:
        """Replace spaces with underscores; preserve UTF-8."""
        return name.strip().replace(" ", "_").replace("/", "_")
