"""Testbench generator: YAML spec → Jinja2 → cocotb testbench + Makefile.

Parses a DUT YAML specification, validates it against the DUTSpec pydantic
model, and renders both the cocotb Python testbench and the simulation
Makefile via Jinja2 templates.
"""

from __future__ import annotations

import logging
import subprocess
from pathlib import Path
from typing import Any

import yaml

from .contracts import (
    ClockConfig,
    CoverageConfig,
    CoverageTargets,
    DUTSpec,
    PortDirection,
    PortSpec,
    ResetConfig,
    SimConfig,
)

logger = logging.getLogger("lanes_ceo.tb_generator")

_TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"


def parse_spec(yaml_path: str | Path) -> DUTSpec:
    """Parse a YAML DUT specification into a DUTSpec model.

    Args:
        yaml_path: Path to the YAML spec file.

    Returns:
        Validated DUTSpec instance.

    Raises:
        FileNotFoundError: If the YAML file doesn't exist.
        ValueError: If the YAML is malformed or missing required fields.
    """
    yaml_path = Path(yaml_path)
    if not yaml_path.exists():
        raise FileNotFoundError(f"DUT spec not found: {yaml_path}")

    with open(yaml_path, "r", encoding="utf-8") as fh:
        raw = yaml.safe_load(fh)

    if not isinstance(raw, dict):
        raise ValueError("YAML spec must be a mapping at top level")

    return _build_spec(raw, yaml_path)


def _build_spec(raw: dict, source_path: Path) -> DUTSpec:
    """Convert raw YAML dict to DUTSpec, normalizing port lists."""
    # Parse ports
    ports: list[PortSpec] = []
    port_map = raw.get("ports", {})
    for direction in ("input", "output", "inout"):
        for p in port_map.get(direction, []):
            ports.append(
                PortSpec(
                    name=p["name"],
                    direction=PortDirection(direction),
                    width=p.get("width", 1),
                )
            )

    # Parse clock
    clock_raw = raw.get("clock", {})
    clock = ClockConfig(
        signal=clock_raw.get("signal", "clk"),
        period_ns=clock_raw.get("period_ns", 10.0),
    )

    # Parse reset
    reset_raw = raw.get("reset", {})
    reset = ResetConfig(
        signal=reset_raw.get("signal", "rst_n"),
        active_low=reset_raw.get("active_low", True),
        duration_ns=reset_raw.get("duration_ns", 100.0),
    )

    # Parse sim
    sim_raw = raw.get("sim", {})
    sim = SimConfig(
        time_us=sim_raw.get("time_us", 500.0),
        vcd_dump=sim_raw.get("vcd_dump", True),
    )

    # Parse coverage
    cov_raw = raw.get("coverage", {})
    targets_raw = cov_raw.get("targets", {})
    coverage = CoverageConfig(
        enabled=cov_raw.get("enabled", True),
        targets=CoverageTargets(
            line=targets_raw.get("line", 90.0),
            toggle=targets_raw.get("toggle", 80.0),
            branch=targets_raw.get("branch", 85.0),
            fsm=targets_raw.get("fsm", 80.0),
        ),
    )

    return DUTSpec(
        module_name=raw["module_name"],
        top_entity=raw.get("top_entity", raw["module_name"]),
        dut_file=raw.get("dut_file", ""),
        clock=clock,
        reset=reset,
        ports=ports,
        parameters=raw.get("parameters", {}),
        sim=sim,
        coverage=coverage,
    )


def generate_testbench(spec: DUTSpec, output_dir: str | Path) -> Path:
    """Generate cocotb testbench Python file from DUTSpec.

    Args:
        spec: Parsed DUT specification.
        output_dir: Directory to write the testbench file.

    Returns:
        Path to the generated testbench.py.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    template_path = _TEMPLATE_DIR / "testbench.py.j2"
    output_path = output_dir / "testbench.py"

    _render_jinja2(template_path, spec, output_path)
    logger.info("Generated testbench: %s", output_path)
    return output_path


def generate_makefile(spec: DUTSpec, output_dir: str | Path) -> Path:
    """Generate cocotb Makefile from DUTSpec.

    Args:
        spec: Parsed DUT specification.
        output_dir: Directory to write the Makefile.

    Returns:
        Path to the generated Makefile.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    template_path = _TEMPLATE_DIR / "Makefile.j2"
    output_path = output_dir / "Makefile"

    # Build template context with extra derived values
    context = spec.model_dump()
    context["tb_module_name"] = "testbench"  # cocotb module name

    _render_jinja2(template_path, context, output_path)
    logger.info("Generated Makefile: %s", output_path)
    return output_path


def _render_jinja2(
    template_path: Path,
    context: dict[str, Any] | DUTSpec,
    output_path: Path,
) -> None:
    """Render a Jinja2 template to a file."""
    from jinja2 import Environment, FileSystemLoader

    env = Environment(
        loader=FileSystemLoader(str(template_path.parent)),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template(template_path.name)

    if hasattr(context, "model_dump"):
        context = context.model_dump()
        # Expand nested models for template access
        context.setdefault("clock", {})
        context.setdefault("reset", {})
        context.setdefault("sim", {})
        context.setdefault("coverage", {})

    # Add port groups for template convenience
    if "ports" in context:
        context["input_ports"] = [p for p in context["ports"] if p.get("direction") == "input"]
        context["output_ports"] = [p for p in context["ports"] if p.get("direction") == "output"]
        context["inout_ports"] = [p for p in context["ports"] if p.get("direction") == "inout"]

    rendered = template.render(**context)
    output_path.write_text(rendered, encoding="utf-8")


def run_verible_check(verilog_path: str | Path) -> tuple[bool, str]:
    """Run Verible syntax check on a Verilog/SystemVerilog file.

    Args:
        verilog_path: Path to the Verilog source file.

    Returns:
        (passed, message) tuple. passed=False means syntax errors found.
        If Verible is not installed, returns (True, warning_message).
    """
    verilog_path = Path(verilog_path)
    if not verilog_path.exists():
        return False, f"File not found: {verilog_path}"

    try:
        result = subprocess.run(
            ["verible-verilog-syntax", str(verilog_path)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            return True, "Syntax check passed"
        return False, result.stderr.strip() or result.stdout.strip()
    except FileNotFoundError:
        logger.warning("Verible not installed — skipping syntax check")
        return True, "[warning] Verible not found, syntax check skipped"
    except subprocess.TimeoutExpired:
        logger.warning("Verible check timed out after 30s on %s", verilog_path)
        return False, "Verible check timed out after 30s"
    except Exception as exc:
        logger.error("Verible check failed: %s", exc)
        return False, f"Verible check error: {exc}"


def generate_all(
    yaml_path: str | Path,
    output_dir: str | Path,
    verilog_source: str | Path | None = None,
) -> tuple[DUTSpec, Path, Path]:
    """Run full testbench generation: parse → render → verify.

    Args:
        yaml_path: Path to the YAML DUT spec.
        output_dir: Output directory for generated files.
        verilog_source: Optional path to Verilog/SystemVerilog source for syntax check.

    Returns:
        (spec, testbench_path, makefile_path) tuple.
    """
    spec = parse_spec(yaml_path)

    if not spec.ports:
        logger.warning("DUT spec has no ports defined — generated testbench will be empty")

    tb_path = generate_testbench(spec, output_dir)
    mk_path = generate_makefile(spec, output_dir)

    # Verible check on DUT source if provided
    if verilog_source:
        passed, msg = run_verible_check(verilog_source)
        if not passed:
            logger.warning("Verible check failed on %s: %s", verilog_source, msg)

    return spec, tb_path, mk_path
