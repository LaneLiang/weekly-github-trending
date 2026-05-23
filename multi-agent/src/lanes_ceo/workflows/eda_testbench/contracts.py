"""Data contracts for the EDA testbench workflow.

Defines the pydantic models used throughout the eda_testbench pipeline:
YAML spec → tb_generator → sim_runner → coverage → report.
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class PortDirection(str, Enum):
    INPUT = "input"
    OUTPUT = "output"
    INOUT = "inout"


class PortSpec(BaseModel):
    """A single DUT port definition."""

    name: str
    direction: PortDirection
    width: int = 1


class ClockConfig(BaseModel):
    """Clock signal configuration."""

    signal: str = "clk"
    period_ns: float = 10.0


class ResetConfig(BaseModel):
    """Reset signal configuration."""

    signal: str = "rst_n"
    active_low: bool = True
    duration_ns: float = 100.0


class SimConfig(BaseModel):
    """Simulation parameters."""

    time_us: float = 500.0
    vcd_dump: bool = True


class CoverageTargets(BaseModel):
    """Per-metric coverage thresholds."""

    line: float = 90.0
    toggle: float = 80.0
    branch: float = 85.0
    fsm: float = 80.0


class CoverageConfig(BaseModel):
    """Coverage collection configuration."""

    enabled: bool = True
    targets: CoverageTargets = Field(default_factory=CoverageTargets)


class DUTSpec(BaseModel):
    """Complete DUT specification parsed from YAML."""

    module_name: str
    top_entity: str = ""
    dut_file: str = ""
    clock: ClockConfig = Field(default_factory=ClockConfig)
    reset: ResetConfig = Field(default_factory=ResetConfig)
    ports: list[PortSpec] = Field(default_factory=list)
    parameters: dict[str, Any] = Field(default_factory=dict)
    sim: SimConfig = Field(default_factory=SimConfig)
    coverage: CoverageConfig = Field(default_factory=CoverageConfig)

    def model_post_init(self, __context: Any) -> None:
        if not self.top_entity:
            self.top_entity = self.module_name

    @property
    def input_ports(self) -> list[PortSpec]:
        return [p for p in self.ports if p.direction == PortDirection.INPUT]

    @property
    def output_ports(self) -> list[PortSpec]:
        return [p for p in self.ports if p.direction == PortDirection.OUTPUT]

    @property
    def inout_ports(self) -> list[PortSpec]:
        return [p for p in self.ports if p.direction == PortDirection.INOUT]


class SimResult(BaseModel):
    """Simulation run result."""

    success: bool
    return_code: int
    tests_passed: int = 0
    tests_failed: int = 0
    tests_total: int = 0
    sim_time_us: float = 0.0
    log_path: str = ""
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class CoverageReport(BaseModel):
    """Coverage data extracted from UCDB/XML report."""

    line: float | None = None
    toggle: float | None = None
    branch: float | None = None
    fsm: float | None = None
    total: float | None = None
    raw_report: str = ""
    passed: bool = False
