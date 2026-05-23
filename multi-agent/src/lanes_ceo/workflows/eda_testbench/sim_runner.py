"""Simulation runner: Makefile execution + log parsing + result extraction.

Runs cocotb+ModelSim simulation via make, parses the cocotb results.xml
and sim.log, and returns a structured SimResult.
"""

from __future__ import annotations

import logging
import os
import re
import subprocess
from pathlib import Path
from xml.etree import ElementTree

from .contracts import CoverageTargets, SimResult

logger = logging.getLogger("lanes_ceo.sim_runner")

# Regex patterns for log parsing
_RE_TEST_RESULT = re.compile(
    r"(test_\w+)\s+(passed|failed|error)", re.IGNORECASE
)
_RE_SIM_TIME = re.compile(r"simulation time[:=]\s*([0-9.]+)\s*(\w+)", re.IGNORECASE)
_RE_ERROR = re.compile(r"(Error|ERROR|Fatal|FATAL)[:\s]*(.*)", re.IGNORECASE)
_RE_WARNING = re.compile(r"(Warning|WARNING)[:\s]*(.*)", re.IGNORECASE)
_RE_LICENSE_FAIL = re.compile(r"(license|License).*(fail|denied|unavailable|not found|expired)", re.IGNORECASE)

_VCD_SIZE_WARN_THRESHOLD = 1_000_000_000  # 1 GB

DEFAULT_COCOTB_MIN_VERSION = "1.9.0"


def _parse_version(v: str) -> tuple[int, ...]:
    """Parse a version string into a comparable tuple."""
    return tuple(int(x) for x in re.findall(r"\d+", v))


def check_cocotb(min_version: str | None = None) -> tuple[bool, str]:
    """Check that cocotb is installed, importable, and meets minimum version.

    Args:
        min_version: Minimum required version string (e.g. "1.9.0").

    Returns:
        (available, version_string) tuple.
    """
    try:
        import cocotb
        ver = getattr(cocotb, "__version__", "unknown")
        if min_version and ver != "unknown":
            try:
                if _parse_version(ver) < _parse_version(min_version):
                    return False, f"cocotb {ver} < required {min_version}"
            except Exception:
                logger.debug("cocotb version check failed, proceeding anyway")
        return True, ver
    except ImportError:
        return False, "cocotb not installed"


def check_simulator(sim: str = "questa") -> tuple[bool, str]:
    """Check that the HDL simulator is available on PATH.

    Args:
        sim: Simulator name (questa, modelsim, etc.).

    Returns:
        (available, message) tuple.
    """
    vsim_cmd = "vsim" if sim in ("questa", "modelsim") else sim
    try:
        result = subprocess.run(
            [vsim_cmd, "-version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        line = (result.stdout + result.stderr).split("\n")[0].strip()
        return True, line
    except FileNotFoundError:
        return False, f"Simulator '{vsim_cmd}' not found on PATH"
    except Exception as exc:
        return False, f"Simulator check failed: {exc}"


def run_simulation(
    work_dir: str | Path,
    sim: str = "questa",
    timeout: int = 600,
    gui: bool = False,
    dut_file: str | None = None,
) -> SimResult:
    """Run ``make`` in the testbench workspace.

    Args:
        work_dir: Directory containing the generated Makefile and testbench.py.
        sim: HDL simulator to use (questa, modelsim, etc.).
        timeout: Maximum simulation wall-clock time in seconds.
        gui: If True, pass GUI=1 to make (opens ModelSim waveform window).
        dut_file: Optional path to Verilog DUT source for pre-flight check.

    Returns:
        SimResult with pass/fail status, test counts, and extracted errors.
    """
    work_dir = Path(work_dir)
    if not (work_dir / "Makefile").exists():
        return SimResult(
            success=False,
            return_code=-1,
            errors=["No Makefile found in workspace"],
        )

    if not (work_dir / "testbench.py").exists():
        return SimResult(
            success=False,
            return_code=-1,
            errors=["No testbench.py found in workspace"],
        )

    # Pre-flight: check DUT source exists (resolve relative to work_dir)
    if dut_file:
        dut_path = Path(dut_file)
        if not dut_path.is_absolute():
            dut_path = work_dir / dut_path
        if not dut_path.exists():
            return SimResult(
                success=False,
                return_code=-1,
                errors=[f"DUT source file not found: {dut_path}"],
            )

    env = {"SIM": sim}
    if gui:
        env["GUI"] = "1"

    cmd = ["make"]
    logger.info("Running simulation in %s (timeout=%ds)", work_dir, timeout)

    try:
        result = subprocess.run(
            cmd,
            cwd=str(work_dir),
            capture_output=True,
            text=True,
            timeout=timeout,
            env={**os.environ, **env},
        )
    except subprocess.TimeoutExpired:
        return SimResult(
            success=False,
            return_code=-1,
            errors=[f"Simulation timed out after {timeout}s"],
        )
    except Exception as exc:
        return SimResult(
            success=False,
            return_code=-1,
            errors=[f"Simulation subprocess error: {exc}"],
        )

    combined = result.stdout + result.stderr

    # Detect license failures
    if _RE_LICENSE_FAIL.search(combined):
        return SimResult(
            success=False,
            return_code=result.returncode,
            errors=["ModelSim license unavailable — check license server or LM_LICENSE_FILE"],
        )

    # Extract simulation time from log or XML
    sim_time_us = _extract_sim_time(combined)

    # Parse results from XML if available
    xml_path = work_dir / "results.xml"
    tests_passed, tests_failed, tests_total = 0, 0, 0
    if xml_path.exists():
        tests_passed, tests_failed, tests_total = _parse_results_xml(xml_path)
        if sim_time_us == 0.0:
            sim_time_us = _extract_xml_sim_time(xml_path)

    # Fallback: parse from stdout/stderr
    if tests_total == 0:
        tests_passed, tests_failed, tests_total = _parse_results_from_log(combined)

    # Extract warnings
    warnings = [m.group(2).strip() for m in _RE_WARNING.finditer(combined)]

    # Check VCD size
    vcd_files = list(work_dir.glob("*.vcd"))
    for vcd in vcd_files:
        if vcd.stat().st_size > _VCD_SIZE_WARN_THRESHOLD:
            warnings.append(f"VCD file {vcd.name} exceeds 1 GB ({vcd.stat().st_size / 1e9:.1f} GB)")

    return SimResult(
        success=result.returncode == 0 and tests_failed == 0,
        return_code=result.returncode,
        tests_passed=tests_passed,
        tests_failed=tests_failed,
        tests_total=tests_total,
        sim_time_us=sim_time_us,
        log_path=str(work_dir / "sim.log") if (work_dir / "sim.log").exists() else "",
        errors=_extract_errors(combined),
        warnings=warnings,
    )


def _extract_sim_time(combined: str) -> float:
    """Extract simulation time in microseconds from log output."""
    match = _RE_SIM_TIME.search(combined)
    if not match:
        return 0.0
    value = float(match.group(1))
    unit = match.group(2).lower()
    if unit == "s":
        value *= 1e6
    elif unit in ("ms", "m"):
        value *= 1000.0
    elif unit in ("ns", "n"):
        value /= 1000.0
    elif unit == "ps":
        value /= 1e6
    return value


def _extract_xml_sim_time(xml_path: Path) -> float:
    """Extract simulation time from results.xml testsuite time attribute."""
    try:
        tree = ElementTree.parse(str(xml_path))
        root = tree.getroot()
        time_attr = root.get("time", "")
        if time_attr:
            return float(time_attr) * 1e6  # XML time is in seconds, convert to us
    except Exception:
        logger.debug("XML sim time extraction failed, using 0.0 default")
    return 0.0


def _parse_results_xml(xml_path: Path) -> tuple[int, int, int]:
    """Parse cocotb results.xml for test pass/fail counts."""
    try:
        tree = ElementTree.parse(str(xml_path))
        root = tree.getroot()
        passed = failed = total = 0
        for testcase in root.iter("testcase"):
            total += 1
            failure = testcase.find("failure")
            error = testcase.find("error")
            if failure is not None or error is not None:
                failed += 1
            else:
                passed += 1
        return passed, failed, total
    except Exception as exc:
        logger.warning("Failed to parse results.xml: %s", exc)
        return 0, 0, 0


def _parse_results_from_log(output: str) -> tuple[int, int, int]:
    """Extract test pass/fail counts from simulation log output."""
    passed = failed = 0
    for match in _RE_TEST_RESULT.finditer(output):
        status = match.group(2).lower()
        if status == "passed":
            passed += 1
        elif status in ("failed", "error"):
            failed += 1
    total = passed + failed
    return passed, failed, total


def _extract_errors(output: str) -> list[str]:
    """Extract error lines from simulation output."""
    errors: list[str] = []
    for match in _RE_ERROR.finditer(output):
        msg = match.group(2).strip()
        if msg and msg not in errors:
            errors.append(msg)
    return errors[:20]  # Cap at 20 unique errors
