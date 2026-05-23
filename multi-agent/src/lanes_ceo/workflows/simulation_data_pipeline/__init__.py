"""SimulationDataPipelineWorkflow — 仿真数据管线 workflow.

Parses SPICE .raw / MATLAB .mat / Verilog .vcd → extracts DC-DC metrics
(efficiency, ripple, transient, Bode, regulation) → aggregates →
generates Nature-style figures → creates experiment manifest.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from lanes_ceo.contracts import Artifact, CriticReview, Job

logger = logging.getLogger("lanes_ceo.simulation_data_pipeline")


class SimulationDataPipelineWorkflow:
    """Workflow for automated simulation data processing.

    Trigger: lanes-ceo --role simulation_data_pipeline --message "<source_dir>"
    """

    role_group = "simulation_data_pipeline"
    actor_name = "sim-data-pipeline-actor"
    critic_name = "sim-data-pipeline-critic"

    def run_actor(self, job: Job) -> Artifact:
        """Run the full simulation data pipeline: parse → extract → aggregate → plot → manifest."""
        message = job.input.get("message", "")
        source = job.input.get("source", self._extract_source(message))
        topology = job.input.get("topology", "buck")

        if not source:
            return Artifact(
                artifact_id=f"artifact-{job.job_id}",
                job_id=job.job_id,
                artifact_type="simulation_data_pipeline",
                summary=(
                    "缺少数据源路径。请提供仿真数据文件或目录路径。\n"
                    "用法: lanes-ceo --role simulation_data_pipeline "
                    "--message '/path/to/sim_results'"
                ),
                artifact_paths=[],
                sources=[],
                risks=["missing source path"],
                user_confirmations=["请提供仿真数据源路径"],
            )

        source_path = Path(source)
        if not source_path.exists():
            return Artifact(
                artifact_id=f"artifact-{job.job_id}",
                job_id=job.job_id,
                artifact_type="simulation_data_pipeline",
                summary=f"数据源不存在: {source}",
                artifact_paths=[],
                sources=[],
                risks=["source path does not exist"],
                user_confirmations=["请确认仿真数据路径是否正确"],
            )

        from lanes_ceo.workflows.utils import get_artifact_dir

        artifact_dir = get_artifact_dir("simulation_data_pipeline")
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
        output_path = artifact_dir / f"run-{ts}"
        output_path.mkdir(parents=True, exist_ok=True)

        # Scan and classify files
        file_map = self._scan_directory(source_path)
        total_files = sum(len(v) for v in file_map.values())
        if total_files == 0:
            return Artifact(
                artifact_id=f"artifact-{job.job_id}",
                job_id=job.job_id,
                artifact_type="simulation_data_pipeline",
                summary=f"在 {source} 中未发现仿真数据文件（.raw/.mat/.vcd）",
                artifact_paths=[],
                sources=[],
                risks=["no simulation files found"],
                user_confirmations=["请确认目录是否包含仿真结果文件"],
            )

        logger.info(
            "Pipeline start: source=%s, files=%d (raw=%d, mat=%d, vcd=%d)",
            source, total_files,
            len(file_map["raw"]), len(file_map["mat"]), len(file_map["vcd"]),
        )

        # Initialize components
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
        from .schemas import MetricsDict

        raw_parser = SpiceRawParser()
        mat_parser = MatlabMatParser()
        vcd_parser = VCDParser()
        eff_ext = EfficiencyExtractor()
        rip_ext = RippleExtractor()
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
        summary_lines = [
            f"仿真数据管线执行报告",
            f"数据源: {source_path}",
            f"处理时间: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}",
            f"拓朴类型: {topology}",
            "",
        ]
        errors: list[str] = []

        for file_type, paths in [
            ("raw", file_map["raw"]),
            ("mat", file_map["mat"]),
            ("vcd", file_map["vcd"]),
        ]:
            for filepath in paths:
                run_counter += 1
                run_id = f"run-{run_counter:04d}"
                try:
                    if file_type == "raw":
                        dataframe = raw_parser.parse(filepath)
                    elif file_type == "mat":
                        dataframe = mat_parser.parse(filepath)
                    else:
                        dataframe = vcd_parser.parse(filepath)

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

                    aggregator.add_run(
                        run_id=run_id,
                        parameters={"source": str(filepath), "topology": topology},
                        metrics=metrics,
                        source_path=str(filepath),
                    )

                    # Generate key plots
                    fig_paths: list[str] = []
                    try:
                        if metrics.efficiency is not None:
                            ef_path = figures_dir / f"{run_id}_efficiency.svg"
                            plot_data = plotter.prepare_plot_data("efficiency", dataframe, metrics)
                            plot_data["title"] = f"Efficiency — {filepath.stem}"
                            plotter.generate_figure("efficiency", plot_data, ef_path)
                            fig_paths.append(str(ef_path))
                    except Exception as pe:
                        logger.warning("Plot generation failed for %s: %s", filepath.name, pe)

                    manifest = exp_manager.create_manifest(
                        dataframe=dataframe,
                        metrics=metrics,
                        figures=fig_paths,
                        input_files=[str(filepath)],
                        parameters={"topology": topology},
                    )
                    exp_manager.save_manifest(manifest)

                    if metrics.efficiency is not None:
                        summary_lines.append(
                            f"[{run_id}] {filepath.name}: η={metrics.efficiency:.4f}"
                        )
                    else:
                        summary_lines.append(
                            f"[{run_id}] {filepath.name}: parsed OK"
                        )

                except Exception as exc:
                    msg = f"[{run_id}] {filepath.name}: 错误 — {exc}"
                    summary_lines.append(msg)
                    errors.append(msg)
                    logger.exception("Pipeline step failed for %s", filepath)
                    continue

        # Build run table
        run_table = aggregator.build()
        table_path = output_path / "run_table.csv"
        if len(run_table) > 0:
            run_table.to_dataframe().to_csv(table_path, index=False)

        summary_lines.append("")
        summary_lines.append(f"处理完成: {run_counter} 个文件")
        if len(run_table) > 0:
            summary_lines.append(f"Run table: {len(run_table)} rows → {table_path}")
        if errors:
            summary_lines.append(f"错误: {len(errors)} 个文件处理失败")

        return Artifact(
            artifact_id=f"artifact-{job.job_id}",
            job_id=job.job_id,
            artifact_type="simulation_data_pipeline",
            summary="\n".join(summary_lines),
            artifact_paths=[str(output_path)] if output_path else [],
            sources=[str(source_path)],
            risks=errors if errors else [
                "数值提取精度依赖稳态检测算法",
                "图表须人工核验",
            ],
            user_confirmations=[
                "请核验提取的效率/纹波/瞬态指标是否合理",
                "请确认生成的图表是否符合论文要求",
            ],
        )

    def run_critic(self, job: Job, artifact: Artifact) -> CriticReview:
        """Verify the pipeline output is complete and well-formed."""
        issues: list[str] = []

        if "缺少数据源路径" in artifact.summary:
            issues.append("缺少 source 路径参数")
        if "数据源不存在" in artifact.summary:
            issues.append("数据源路径不存在")
        if "未发现仿真数据文件" in artifact.summary:
            issues.append("未找到可解析的仿真文件")
        if "处理完成" not in artifact.summary and "错误" not in artifact.summary:
            issues.append("管线未正常完成")

        error_lines = [l for l in artifact.summary.split("\n") if "错误" in l]
        if len(error_lines) == 0 and "处理完成" not in artifact.summary:
            issues.append("管线报告格式异常")

        approved = len(issues) == 0
        score = 90 - len(issues) * 10 if not approved else 90
        return CriticReview(
            review_id=f"review-{job.job_id}",
            job_id=job.job_id,
            review_result="approved" if approved else "returned",
            score=max(score, 30),
            issues=issues,
            approved=approved,
            return_to_actor=not approved,
            handoff_note="管线执行报告审核通过" if approved else "管线报告不完整",
        )

    @staticmethod
    def _extract_source(message: str) -> str:
        """Extract source path from message text."""
        parts = message.strip().split()
        for part in parts:
            p = Path(part)
            if p.exists():
                return str(p.resolve())
        # Fallback: use the whole message as a path
        msg_path = Path(message.strip())
        if msg_path.exists():
            return str(msg_path.resolve())
        return ""

    @staticmethod
    def _scan_directory(source: Path) -> dict[str, list[Path]]:
        """Scan a directory for simulation files grouped by type."""
        from .cli import _scan_directory as _scan
        return _scan(source)
