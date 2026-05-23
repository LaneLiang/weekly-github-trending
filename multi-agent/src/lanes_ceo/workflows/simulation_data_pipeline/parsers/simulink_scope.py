"""Simulink Scope data parser.

Extracts structured time-series data from Simulink Scope block saves.
Scope data is typically stored in .mat files with a top-level ``ScopeData``
struct or ``tout``/``yout``/``simout`` To Workspace variables.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

from ..schemas import SimDataFrame, SimMeta
from .base import BaseParser, RawParseError

logger = logging.getLogger("lanes_ceo.simulink_scope")

_H5PY_AVAILABLE: bool = False
try:
    import h5py
    _H5PY_AVAILABLE = True
except ImportError:
    pass


class SimulinkScopeParser(BaseParser):
    """Parser for Simulink Scope block data stored in .mat files.

    Auto-detects ScopeData, tout/yout, and simout structures.
    Falls back to :class:`MatlabMatParser` for generic .mat files.
    """

    SUPPORTED_EXTENSIONS: set[str] = {".mat"}
    PARSER_NAME: str = "simulink_scope"

    _SCOPE_KEYS = {"ScopeData", "ScopeData1", "ScopeData2"}
    _TIME_KEYS = {"tout", "simTime", "time", "t"}
    _SIGNAL_KEYS = {"yout", "simout", "ScopeData", "ScopeData1", "ScopeData2"}

    def parse(self, path: Path, **kwargs: Any) -> SimDataFrame:
        if not path.exists():
            raise RawParseError(f"File not found: {path}", path=str(path))

        version = self._detect_version(path)

        if version == 3:
            if not _H5PY_AVAILABLE:
                raise RawParseError(
                    "MATLAB v7.3 file requires h5py. Install with: pip install h5py",
                    path=str(path),
                )
            return self._parse_scope_v73(path, **kwargs)
        else:
            return self._parse_scope_v5_v7(path, **kwargs)

    # ── v5 / v7 ──

    def _parse_scope_v5_v7(self, path: Path, **kwargs: Any) -> SimDataFrame:
        import scipy.io as sio

        mat = sio.loadmat(str(path), struct_as_record=False, squeeze_me=True)
        var_names = [k for k in mat if not k.startswith("__")]

        # Look for ScopeData struct
        for scope_key in self._SCOPE_KEYS:
            if scope_key in mat:
                return self._unwrap_scope_struct(mat[scope_key], scope_key)

        # Look for tout + yout
        tout = None
        for tk in self._TIME_KEYS:
            if tk in mat:
                tout = np.atleast_1d(mat[tk]).ravel().astype(np.float64)
                break

        yout = None
        for sk in ("yout", "simout"):
            if sk in mat:
                raw = mat[sk]
                if hasattr(raw, "dtype") and raw.dtype.names:
                    raw = raw[raw.dtype.names[0]]
                yout = np.atleast_1d(raw).ravel().astype(np.float64)
                break

        if tout is not None and yout is not None:
            meta = SimMeta(
                tool="simulink",
                sim_type=".scope",
                timestamp=datetime.now(timezone.utc).replace(tzinfo=None),
                signal_names=["yout"],
            )
            return SimDataFrame(signals={"yout": yout}, time=tout, meta=meta)

        # Fallback: delegate to generic MATLAB parser
        from .matlab_mat import MatlabMatParser
        logger.info("No ScopeData found in %s, falling back to generic MATLAB parser", path.name)
        return MatlabMatParser().parse(path, **kwargs)

    # ── v7.3 ──

    def _parse_scope_v73(self, path: Path, **kwargs: Any) -> SimDataFrame:
        import h5py

        with h5py.File(str(path), "r") as f:
            keys = set(f.keys())

            for scope_key in self._SCOPE_KEYS:
                if scope_key in keys:
                    return self._unwrap_scope_h5(f, scope_key)

            # tout + yout
            tout = None
            for tk in self._TIME_KEYS:
                if tk in keys:
                    ds = f[tk]
                    try:
                        tout = np.array(ds[:], dtype=np.float64).ravel()
                    except Exception:
                        pass
                    break

            yout = None
            for sk in ("yout", "simout"):
                if sk in keys:
                    ds = f[sk]
                    try:
                        data = np.array(ds[:], dtype=np.float64)
                        if data.ndim > 1:
                            data = data.ravel()
                        yout = data
                    except Exception:
                        pass
                    break

            if tout is not None and yout is not None:
                meta = SimMeta(
                    tool="simulink",
                    sim_type=".scope",
                    timestamp=datetime.now(timezone.utc).replace(tzinfo=None),
                    signal_names=["yout"],
                )
                return SimDataFrame(signals={"yout": yout}, time=tout, meta=meta)

        # Fallback
        from .matlab_mat import MatlabMatParser
        logger.info("No ScopeData found in %s, falling back to generic MATLAB parser", path.name)
        return MatlabMatParser().parse(path, **kwargs)

    # ── ScopeData unwrapping ──

    def _unwrap_scope_struct(self, scope_obj: Any, label: str) -> SimDataFrame:
        """Unwrap a Simulink ScopeData struct (v5/v7)."""
        times: np.ndarray | None = None
        signals: dict[str, np.ndarray] = {}
        sig_names: list[str] = []

        if hasattr(scope_obj, "dtype") and scope_obj.dtype.names:
            fields = scope_obj.dtype.names
            if "time" in fields:
                times = np.atleast_1d(scope_obj["time"].item()).ravel().astype(np.float64)

            if "signals" in fields:
                sigs = scope_obj["signals"].item()
                if hasattr(sigs, "dtype") and sigs.dtype.names:
                    if "values" in sigs.dtype.names:
                        vals = sigs["values"].item()
                        vals = np.atleast_1d(vals).ravel().astype(np.float64)
                        sig_name = sigs["label"].item() if "label" in sigs.dtype.names and sigs["label"].item() else f"{label}_sig1"
                        sig_name = str(sig_name).strip().replace(" ", "_")
                        signals[sig_name] = vals
                        sig_names.append(sig_name)

        if times is None:
            raise RawParseError("ScopeData struct missing 'time' field")

        meta = SimMeta(
            tool="simulink",
            sim_type=".scope",
            timestamp=datetime.now(timezone.utc).replace(tzinfo=None),
            signal_names=sig_names,
        )
        return SimDataFrame(signals=signals, time=times, meta=meta)

    def _unwrap_scope_h5(self, f: "h5py.File", scope_key: str) -> SimDataFrame:
        """Unwrap a Simulink ScopeData group (v7.3 HDF5)."""
        group = f[scope_key]
        times: np.ndarray | None = None
        signals: dict[str, np.ndarray] = {}
        sig_names: list[str] = []

        if "time" in group:
            times = np.array(group["time"][:], dtype=np.float64).ravel()

        if "signals" in group:
            sig_group = group["signals"]
            for sig_key in sig_group:
                if sig_key.startswith("#"):
                    continue
                sg = sig_group[sig_key]
                if isinstance(sg, h5py.Group):
                    for field in ("values", "data"):
                        if field in sg:
                            vals = np.array(sg[field][:], dtype=np.float64).ravel()
                            label = sig_key.replace("values", "").replace("data", "")
                            label = label.strip("_") or f"{scope_key}_{sig_key}"
                            signals[label] = vals
                            sig_names.append(label)
                            break

        if times is None:
            raise RawParseError(f"ScopeData group '{scope_key}' missing 'time' dataset")

        meta = SimMeta(
            tool="simulink",
            sim_type=".scope",
            timestamp=datetime.now(timezone.utc).replace(tzinfo=None),
            signal_names=sig_names,
        )
        return SimDataFrame(signals=signals, time=times, meta=meta)

    # ── helpers ──

    @staticmethod
    def _detect_version(path: Path) -> int:
        with open(path, "rb") as fh:
            magic = fh.read(8)
        if magic[:4] == b"\x89HDF":
            return 3
        if magic[:4] == b"MATL":
            return 2
        return 1
