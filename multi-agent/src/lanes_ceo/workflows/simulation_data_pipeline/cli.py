"""CLI entry point for the simulation data pipeline.

Provides the ``lanes-data`` command with subcommands:
    lanes-data run-all --source <dir>
    lanes-data parse --source <file>
    lanes-data extract --source <file>
    lanes-data plot --source <dir>
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Any

import click

from .config import KNOWN_EXTENSIONS
from .schemas import MetricsDict, RunTable

logger = logging.getLogger("lanes_ceo.cli")


def _configure_logging(verbose: bool) -> None:
    """Set up logging for CLI usage."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        stream=sys.stderr,
    )


def _check_dependencies() -> list[str]:
    """Pre-flight check for required Python packages. Returns list of missing packages."""
    missing: list[str] = []
    required = {
        "numpy": "numpy",
        "scipy": "scipy",
        "pydantic": "pydantic",
        "yaml": "pyyaml",
        "click": "click",
        "pandas": "pandas",
    }
    for import_name, pip_name in required.items():
        try:
            __import__(import_name)
        except ImportError:
            missing.append(pip_name)

    if missing:
        click.echo(f"Missing dependencies. Install with: pip install {' '.join(missing)}", err=True)

    return missing


def _scan_directory(source: Path) -> dict[str, list[Path]]:
    """Scan a directory for simulation files, grouped by type.

    Returns:
        Dict mapping file type (raw, mat, vcd) to list of paths.
    """
    files: dict[str, list[Path]] = {"raw": [], "mat": [], "vcd": [], "skipped": []}

    for item in sorted(source.rglob("*")):
        if not item.is_file():
            continue
        suffix = item.suffix.lower()
        if suffix in {".raw", ".sw0", ".ac0", ".dc0", ".tr0"}:
            files["raw"].append(item)
        elif suffix == ".mat":
            files["mat"].append(item)
        elif suffix == ".vcd":
            files["vcd"].append(item)
        elif suffix in KNOWN_EXTENSIONS:
            files["skipped"].append(item)
        # Ignore other files silently

    return files


@click.group(name="lanes-data")
def main() -> None:
    """Lanes Data Pipeline — automated simulation data processing for DC-DC designs."""
    pass


@main.command(name="run-all")
@click.option("--source", "-s", type=click.Path(exists=True, file_okay=True, dir_okay=True),
              required=True, help="Path to simulation results directory or single file.")
@click.option("--output", "-o", type=click.Path(), default="./output",
              help="Output directory for metrics, figures, and manifest.")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging.")
@click.option("--steady-state-window", type=(float, float), default=None,
              help="Manual steady-state window as (start, end) in seconds.")
@click.option("--topology", type=click.Choice(["buck", "boost", "buck-boost"]),
              default="buck", help="DC-DC converter topology.")
def run_all(
    source: str,
    output: str,
    verbose: bool,
    steady_state_window: tuple[float, float] | None,
    topology: str,
) -> None:
    """Run the full pipeline: parse -> extract -> aggregate -> plot -> manifest."""
    _configure_logging(verbose)
    _check_dependencies()

    source_path = Path(source)
    output_path = Path(output)
    output_path.mkdir(parents=True, exist_ok=True)

    click.echo(f"Source: {source_path}")
    click.echo(f"Output: {output_path}")

    # Scan for files
    if source_path.is_dir():
        file_map = _scan_directory(source_path)
        total_files = sum(len(v) for v in file_map.values())
        if total_files == 0:
            click.echo(f"No simulation files found in {source_path}")
            return
        click.echo(
            f"Found {len(file_map['raw'])} SPICE raw, "
            f"{len(file_map['mat'])} MATLAB, "
            f"{len(file_map['vcd'])} VCD files "
            f"({len(file_map['skipped'])} skipped)"
        )
    else:
        # Single file mode
        suffix = source_path.suffix.lower()
        if suffix in {".raw", ".sw0", ".ac0", ".dc0", ".tr0"}:
            file_map = {"raw": [source_path], "mat": [], "vcd": [], "skipped": []}
        elif suffix == ".mat":
            file_map = {"raw": [], "mat": [source_path], "vcd": [], "skipped": []}
        elif suffix == ".vcd":
            file_map = {"raw": [], "mat": [], "vcd": [source_path], "skipped": []}
        else:
            click.echo(f"Unsupported file type: {source_path.suffix}", err=True)
            return

    # Initialize pipeline components
    from .parsers.spice_raw import SpiceRawParser
    from .parsers.matlab_mat import MatlabMatParser
    from .parsers.verilog_vcd import VCDParser
    from .extractors.efficiency import EfficiencyExtractor
    from .extractors.ripple import RippleExtractor
    from .extractors.transient import TransientExtractor
    from .extractors.bode import BodeExtractor
    from .extractors.regulation import RegulationExtractor
    from .aggregators.scan import ParamScanAggregator
    from .plotters.nature_figure_bridge import NatureFigureBridge
    from .experiment.manifest import ExperimentManager

    raw_parser = SpiceRawParser()
    mat_parser = MatlabMatParser()
    vcd_parser = VCDParser()

    eff_ext = EfficiencyExtractor(steady_state_window=steady_state_window)
    rip_ext = RippleExtractor(steady_state_window=steady_state_window)
    trans_ext = TransientExtractor()
    bode_ext = BodeExtractor()
    reg_ext = RegulationExtractor()

    aggregator = ParamScanAggregator()
    plotter = NatureFigureBridge()
    exp_manager = ExperimentManager(output_base=output_path)

    figures_dir = output_path / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)

    # Process each file
    run_counter = 0
    for file_type, paths in [("raw", file_map["raw"]), ("mat", file_map["mat"]), ("vcd", file_map["vcd"])]:
        if file_type == "skipped":
            for p in paths:
                click.echo(f"  Skipped: {p.name}")
            continue

        for filepath in paths:
            run_counter += 1
            run_id = f"run-{run_counter:04d}"
            click.echo(f"\n[{run_id}] Processing: {filepath.name}")

            try:
                # Parse
                if file_type == "raw":
                    dataframe = raw_parser.parse(filepath)
                elif file_type == "mat":
                    dataframe = mat_parser.parse(filepath)
                else:
                    dataframe = vcd_parser.parse(filepath)

                click.echo(f"  Parsed: {dataframe.n_signals} signals, "
                          f"steady_state_reached={dataframe.steady_state_reached}")

                # Extract metrics
                metrics = MetricsDict()
                if eff_ext.can_extract(dataframe):
                    metrics.efficiency = eff_ext.extract(dataframe)

                if rip_ext.can_extract(dataframe):
                    rms, pkpk = rip_ext.extract(dataframe)
                    metrics.ripple_rms = rms
                    metrics.ripple_pkpk = pkpk

                if trans_ext.can_extract(dataframe):
                    metrics.transient = trans_ext.extract(dataframe)

                if bode_ext.can_extract(dataframe):
                    metrics.bode = bode_ext.extract(dataframe)

                if reg_ext.can_extract(dataframe):
                    reg = reg_ext.extract(dataframe)
                    if reg:
                        metrics.regulation = reg
                        metrics.load_regulation = reg.load_regulation_pct
                        metrics.line_regulation = reg.line_regulation_pct

                metrics.steady_state_reached = dataframe.steady_state_reached

                click.echo(f"  Metrics: efficiency={metrics.efficiency}, "
                          f"ripple_rms={metrics.ripple_rms}")

                # Aggregate
                aggregator.add_run(
                    run_id=run_id,
                    parameters={"source": str(filepath), "topology": topology},
                    metrics=metrics,
                    source_path=str(filepath),
                )

                # Generate plots
                fig_paths = []
                try:
                    # Efficiency curve (if applicable)
                    if metrics.efficiency is not None:
                        out_fig = figures_dir / f"{run_id}_efficiency.svg"
                        plot_data = plotter.prepare_plot_data("efficiency", dataframe, metrics)
                        plot_data["title"] = f"Efficiency — {filepath.stem}"
                        plotter.generate_figure("efficiency", plot_data, out_fig)
                        fig_paths.append(str(out_fig))
                except Exception as exc:
                    logger.warning("Plot generation skipped: %s", exc)

                # Create manifest
                manifest = exp_manager.create_manifest(
                    dataframe=dataframe,
                    metrics=metrics,
                    figures=fig_paths,
                    input_files=[str(filepath)],
                    parameters={"topology": topology},
                )
                exp_manager.save_manifest(manifest)
                click.echo(f"  Manifest: {manifest.experiment_id}")

            except Exception as exc:
                click.echo(f"  ERROR: {exc}", err=True)
                logger.exception("Failed to process %s", filepath)
                continue

    # Final summary
    run_table = aggregator.build()
    click.echo(f"\n{'='*60}")
    click.echo(f"Pipeline complete. Processed {run_counter} file(s).")
    click.echo(f"Output directory: {output_path.resolve()}")
    if len(run_table) > 0:
        click.echo(f"Run table: {len(run_table)} rows")
        # Save run table
        table_path = output_path / "run_table.csv"
        run_table.to_dataframe().to_csv(table_path, index=False)
        click.echo(f"Run table saved: {table_path}")
    click.echo(f"{'='*60}")


def _get_parser_for_path(path: Path):
    """Return the appropriate parser for a given simulation file path."""
    suffix = path.suffix.lower()
    if suffix in {".raw", ".sw0", ".ac0", ".dc0", ".tr0"}:
        from .parsers.spice_raw import SpiceRawParser
        return SpiceRawParser()
    elif suffix == ".mat":
        from .parsers.simulink_scope import SimulinkScopeParser
        return SimulinkScopeParser()
    elif suffix == ".vcd":
        from .parsers.verilog_vcd import VCDParser
        return VCDParser()
    return None


@main.command(name="parse")
@click.option("--source", "-s", type=click.Path(exists=True), required=True,
              help="Path to a single simulation file.")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output.")
def parse_cmd(source: str, verbose: bool) -> None:
    """Parse a single simulation file and print summary."""
    _configure_logging(verbose)

    path = Path(source)
    parser = _get_parser_for_path(path)
    if parser is None:
        click.echo(f"Unsupported file type: {path.suffix}", err=True)
        return

    df = parser.parse(path)
    click.echo(f"Tool: {df.meta.tool}")
    click.echo(f"Type: {df.meta.sim_type}")
    click.echo(f"Signals ({df.n_signals}): {', '.join(df.meta.signal_names)}")
    click.echo(f"Time points: {len(df.time) if df.time is not None else 'N/A'}")
    click.echo(f"Freq points: {len(df.frequency) if df.frequency is not None else 'N/A'}")


@main.command(name="extract")
@click.option("--source", "-s", type=click.Path(exists=True), required=True,
              help="Path to a single simulation file.")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output.")
def extract_cmd(source: str, verbose: bool) -> None:
    """Parse a file and extract all applicable metrics."""
    _configure_logging(verbose)

    path = Path(source)
    parser = _get_parser_for_path(path)
    if parser is None:
        click.echo(f"Unsupported file type: {path.suffix}", err=True)
        return

    df = parser.parse(path)

    from .extractors.efficiency import EfficiencyExtractor
    from .extractors.ripple import RippleExtractor
    from .extractors.transient import TransientExtractor
    from .extractors.bode import BodeExtractor
    from .extractors.regulation import RegulationExtractor

    eff_ext = EfficiencyExtractor()
    rip_ext = RippleExtractor()
    trans_ext = TransientExtractor()
    bode_ext = BodeExtractor()
    reg_ext = RegulationExtractor()

    click.echo(f"\nMetrics for: {path.name}")
    click.echo(f"{'='*50}")

    if eff_ext.can_extract(df):
        eta = eff_ext.extract(df)
        if eta is not None:
            click.echo(f"Efficiency:        {eta:.4f} ({eta*100:.2f}%)")
        else:
            click.echo("Efficiency: N/A")

    if rip_ext.can_extract(df):
        rms, pkpk = rip_ext.extract(df)
        click.echo(f"Ripple RMS:        {rms:.6f} V" if rms is not None else "Ripple RMS: N/A")
        click.echo(f"Ripple Pk-Pk:      {pkpk:.6f} V" if pkpk is not None else "Ripple Pk-Pk: N/A")

    if trans_ext.can_extract(df):
        tr = trans_ext.extract(df)
        if tr:
            click.echo(f"Overshoot:         {tr.overshoot_pct:.2f}%" if tr.overshoot_pct is not None else "Overshoot: N/A")
            click.echo(f"Undershoot:        {tr.undershoot_pct:.2f}%" if tr.undershoot_pct is not None else "Undershoot: N/A")
            click.echo(f"Recovery Time:     {tr.recovery_time:.6e} s" if tr.recovery_time is not None else "Recovery Time: N/A")

    if bode_ext.can_extract(df):
        bd = bode_ext.extract(df)
        if bd:
            click.echo(f"Phase Margin:      {bd.phase_margin_deg:.2f} deg" if bd.phase_margin_deg is not None else "Phase Margin: N/A")
            click.echo(f"Gain Margin:       {bd.gain_margin_db:.2f} dB" if bd.gain_margin_db is not None else "Gain Margin: N/A")
            click.echo(f"Crossover Freq:    {bd.crossover_freq:.2f} Hz" if bd.crossover_freq is not None else "Crossover Freq: N/A")

    if reg_ext.can_extract(df):
        reg = reg_ext.extract(df)
        if reg:
            click.echo(f"Load Regulation:   {reg.load_regulation_pct:.4f}%" if reg.load_regulation_pct is not None else "Load Regulation: N/A")
            click.echo(f"Line Regulation:   {reg.line_regulation_pct:.4f}%" if reg.line_regulation_pct is not None else "Line Regulation: N/A")


@main.command(name="plot")
@click.option("--source", "-s", type=click.Path(exists=True), required=True,
              help="Path to a simulation file.")
@click.option("--template", "-t", type=click.Choice(
    ["efficiency", "bode", "transient", "load_regulation", "ripple", "line_regulation"]
), default="efficiency", help="Plot template to use.")
@click.option("--output", "-o", type=click.Path(), default="./output",
              help="Output directory for figures.")
def plot_cmd(source: str, template: str, output: str) -> None:
    """Generate a plot from a simulation file using a named template."""
    path = Path(source)
    parser = _get_parser_for_path(path)
    if parser is None:
        click.echo(f"Unsupported file type: {path.suffix}", err=True)
        return

    from .plotters.nature_figure_bridge import NatureFigureBridge

    df = parser.parse(path)

    plotter = NatureFigureBridge()
    output_path = Path(output) / f"{path.stem}_{template}.svg"

    data = plotter.prepare_plot_data(template, df)
    data["title"] = f"{template.title()} — {path.stem}"
    result_path = plotter.generate_figure(template, data, output_path)
    click.echo(f"Figure saved: {result_path}")


if __name__ == "__main__":
    main()
