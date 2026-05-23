"""Pydantic models for the simulation data pipeline.

Defines the core data structures that flow through the pipeline:
SimMeta, SimDataFrame, MetricsDict, RunTable, and Manifest.
"""

from __future__ import annotations

import hashlib
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
from pydantic import BaseModel, ConfigDict, Field


# ── Simulation Metadata ──


class SimMeta(BaseModel):
    """Metadata about a simulation run, extracted from the raw file header."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    tool: str = ""
    """Simulation tool name: hspice, spectre, matlab, modelsim, etc."""

    sim_type: str = ""
    """Simulation type: .tran, .dc, .ac, .op, etc."""

    timestamp: datetime | None = None
    """Simulation timestamp extracted from the file, if available."""

    sweep_variables: dict[str, list[float]] = Field(default_factory=dict)
    """Sweep variable names -> list of sweep values."""

    parameters: dict[str, float] = Field(default_factory=dict)
    """Design parameters: vin, vout, fsw, l, c, etc."""

    signal_names: list[str] = Field(default_factory=list)
    """Ordered list of signal names as they appear in the file."""

    units: dict[str, str] = Field(default_factory=dict)
    """Signal name -> unit string mapping (V, A, W, s, etc.)."""

    comments: list[str] = Field(default_factory=list)
    """Any comment lines or notes from the simulation header."""


class SimDataFrame(BaseModel):
    """Unified container for simulation waveform data.

    This is the central data structure produced by all parsers.
    Downstream extractors consume this format regardless of source.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    signals: dict[str, np.ndarray]
    """Signal name -> 1D or 2D numpy array of values."""

    time: np.ndarray | None = None
    """Time axis for transient simulations. None for DC/AC sweeps."""

    frequency: np.ndarray | None = None
    """Frequency axis for AC simulations. None for transient/DC."""

    sweep_variable: np.ndarray | None = None
    """Primary sweep variable axis for DC sweeps. None for transient."""

    sweeps: dict[str, np.ndarray] = Field(default_factory=dict)
    """Additional sweep variable axes for nested sweeps."""

    meta: SimMeta = Field(default_factory=SimMeta)
    """Simulation metadata extracted from the file header."""

    steady_state_reached: bool = True
    """Whether the simulation reached steady-state in the saved window."""

    steady_state_window: tuple[float, float] | None = None
    """(start_time, end_time) of the manually-specified or auto-detected steady-state window."""

    irregular_sampling: bool = False
    """True if the time/frequency axis has non-uniform sampling intervals."""

    @property
    def input_hash(self) -> str:
        """SHA-256 of the concatenated signal data (deterministic ID for dedup)."""
        hasher = hashlib.sha256()
        for name in sorted(self.signals.keys()):
            hasher.update(name.encode())
            hasher.update(self.signals[name].tobytes())
        if self.time is not None:
            hasher.update(self.time.tobytes())
        return hasher.hexdigest()

    @property
    def n_signals(self) -> int:
        """Number of signals in this dataframe."""
        return len(self.signals)

    @property
    def shape(self) -> dict[str, tuple[int, ...]]:
        """Shape of each signal array."""
        return {name: arr.shape for name, arr in self.signals.items()}


# ── Metrics ──


class TransientMetrics(BaseModel):
    """Load transient response metrics."""

    overshoot_pct: float | None = None
    """Peak overshoot as percentage of final steady-state value."""

    undershoot_pct: float | None = None
    """Peak undershoot as percentage of final steady-state value."""

    recovery_time: float | None = None
    """Time to settle within ±1% of final value, in seconds."""

    settling_time: float | None = None
    """Time to settle within a specified band, in seconds."""

    settling_band_pct: float = 1.0
    """Settling band as percentage (default 1%)."""


class BodeMetrics(BaseModel):
    """Loop gain Bode plot metrics from AC simulation."""

    phase_margin_deg: float | None = None
    """Phase margin in degrees at the 0 dB crossover frequency."""

    gain_margin_db: float | None = None
    """Gain margin in dB at the -180 degree phase crossover."""

    crossover_freq: float | None = None
    """0 dB crossover frequency in Hz."""

    dc_gain_db: float | None = None
    """DC (low-frequency) loop gain in dB."""

    bandwidth_hz: float | None = None
    """-3 dB bandwidth of the closed-loop system in Hz."""


class RegulationMetrics(BaseModel):
    """Load and line regulation metrics from DC sweep."""

    load_regulation_pct: float | None = None
    """Load regulation: delta_Vout / delta_Iload * 100%, from DC sweep."""

    load_regulation_absolute: float | None = None
    """Absolute voltage change per unit load change (V/A or mV/A)."""

    line_regulation_pct: float | None = None
    """Line regulation: delta_Vout / delta_Vin * 100%, from DC sweep."""

    line_regulation_absolute: float | None = None
    """Absolute output voltage change per unit input change (V/V or mV/V)."""


class MetricsDict(BaseModel):
    """Aggregated metrics container for a single simulation run.

    Each metric group is optional — only the fields relevant to the
    simulation type are populated.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    efficiency: float | None = None
    """Power efficiency: P_out / P_in, dimensionless [0, 1]."""

    ripple_rms: float | None = None
    """Output voltage ripple RMS value, in volts."""

    ripple_pkpk: float | None = None
    """Output voltage ripple peak-to-peak value, in volts."""

    transient: TransientMetrics | None = None
    """Load transient response metrics."""

    bode: BodeMetrics | None = None
    """AC loop gain metrics."""

    load_regulation: float | None = None
    """Load regulation percentage (convenience alias for RegulationMetrics.load_regulation_pct)."""

    line_regulation: float | None = None
    """Line regulation percentage (convenience alias for RegulationMetrics.line_regulation_pct)."""

    regulation: RegulationMetrics | None = None
    """Full regulation metrics (load + line)."""

    steady_state_reached: bool = True
    """Whether the simulation reached steady-state."""

    @property
    def summary(self) -> dict[str, Any]:
        """Flattened dict of all non-None metrics for serialization."""
        result: dict[str, Any] = {}
        if self.efficiency is not None:
            result["efficiency"] = self.efficiency
        if self.ripple_rms is not None:
            result["ripple_rms"] = self.ripple_rms
        if self.ripple_pkpk is not None:
            result["ripple_pkpk"] = self.ripple_pkpk
        if self.transient is not None:
            result["transient"] = self.transient.model_dump(exclude_none=True)
        if self.bode is not None:
            result["bode"] = self.bode.model_dump(exclude_none=True)
        if self.regulation is not None:
            result["regulation"] = self.regulation.model_dump(exclude_none=True)
        result["steady_state_reached"] = self.steady_state_reached
        return result


# ── Run Table ──


class RunTable:
    """Aggregated table of metrics from multiple simulation runs.

    Wraps a pandas DataFrame for parameter scan / corner analysis results.
    """

    def __init__(self, df: Any = None) -> None:
        import pandas as pd

        self._df: pd.DataFrame = df if df is not None else pd.DataFrame()

    @property
    def df(self) -> "pd.DataFrame":
        return self._df

    def add_run(
        self,
        run_id: str,
        parameters: dict[str, Any],
        metrics: MetricsDict,
        source_path: str = "",
    ) -> None:
        """Append a single run's parameters and metrics as a row."""
        row: dict[str, Any] = {"run_id": run_id, "source_path": source_path}
        row.update(parameters)
        row.update(metrics.summary)
        import pandas as pd

        self._df = pd.concat(
            [self._df, pd.DataFrame([row])], ignore_index=True
        )

    def add_runs(self, rows: list[dict[str, Any]]) -> None:
        """Append multiple rows at once."""
        import pandas as pd

        new_df = pd.DataFrame(rows)
        self._df = pd.concat([self._df, new_df], ignore_index=True)

    def query(self, **kwargs: Any) -> "RunTable":
        """Filter runs by column value. Returns a new RunTable."""
        mask = True
        import pandas as pd

        for col, val in kwargs.items():
            if col in self._df.columns:
                mask = mask & (self._df[col] == val)
        return RunTable(self._df[mask].copy())

    def sort_by(self, column: str, ascending: bool = True) -> "RunTable":
        """Return sorted RunTable."""
        return RunTable(self._df.sort_values(column, ascending=ascending).copy())

    def to_dataframe(self) -> "pd.DataFrame":
        return self._df.copy()

    def __len__(self) -> int:
        return len(self._df)

    def __repr__(self) -> str:
        return f"RunTable(n_runs={len(self._df)})"


# ── Manifest ──


class ManifestInputFile(BaseModel):
    """Record of a single input file used in the simulation."""

    path: str
    sha256: str


class ManifestOutputEntry(BaseModel):
    """Record of a generated output file."""

    path: str
    kind: str  # "figure", "data", "manifest"


class Manifest(BaseModel):
    """Experiment manifest recording simulation inputs, metrics, and outputs.

    Schema version: 1.0. Stored as YAML alongside experiment data.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    schema_version: str = "1.0"
    """Manifest schema version for forward compatibility."""

    experiment_id: str = Field(default_factory=lambda: f"exp-{uuid.uuid4().hex[:12]}")
    """Unique experiment identifier."""

    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc)
        .astimezone()
        .strftime("%Y-%m-%dT%H:%M:%S%z")
    )
    """ISO 8601 timestamp at manifest creation."""

    simulation: dict[str, Any] = Field(default_factory=dict)
    """Simulation tool info: {tool, type, input_files: [{path, sha256}]}."""

    parameters: dict[str, Any] = Field(default_factory=dict)
    """Design parameters: vin, vout, fsw, corner, etc."""

    metrics: dict[str, Any] = Field(default_factory=dict)
    """Flattened metrics dict from MetricsDict.summary."""

    outputs: dict[str, list[str]] = Field(default_factory=dict)
    """Output file paths grouped by type: {figures: [...], data: [...]}."""

    pipeline_version: str = "0.1.0"
    """Version of the simulation_data_pipeline package."""

    input_hash: str = ""
    """SHA-256 hash of the input waveform data for reproducibility."""

    def to_yaml(self, path: Path) -> None:
        """Write manifest as YAML file."""
        import yaml

        with open(path, "w", encoding="utf-8") as fh:
            yaml.dump(self.model_dump(exclude_none=True), fh, allow_unicode=True, sort_keys=False)

    @classmethod
    def from_yaml(cls, path: Path) -> "Manifest":
        """Load manifest from YAML file."""
        import yaml

        with open(path, "r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        return cls(**data)


# ── Constants ──

MANIFEST_SCHEMA_VERSION = "1.0"
PIPE_VERSION: str = "0.1.0"
