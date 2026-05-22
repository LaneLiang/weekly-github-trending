"""Experiment protocol framework for batch-running evaluation matrices."""

import copy
import json
import time
from dataclasses import dataclass, field
from pathlib import Path

from dc_auto_tune.utils.types_ import Config
from dc_auto_tune.eval.metrics import compute_metrics


@dataclass
class ExperimentResult:
    name: str
    config_override: dict
    metrics: dict = field(default_factory=dict)
    rewards: list = field(default_factory=list)
    elapsed_s: float = 0.0
    llm_calls: int = 0


class ExperimentProtocol:
    """Define and execute experiment matrices.

    Usage::

        protocol = ExperimentProtocol(base_config)
        protocol.add_experiment("baseline", {})
        protocol.add_experiment("no_perturbation", {"perturbation": {"enabled": False}})
        results = protocol.run_all()
    """

    def __init__(self, base_config: Config):
        self.base_config = base_config
        self.experiments: list[tuple[str, dict]] = []

    def add_experiment(self, name: str, config_override: dict) -> None:
        self.experiments.append((name, config_override))

    def run_all(
        self,
        episodes: int = 200,
        steps_per_episode: int = 200,
    ) -> list[ExperimentResult]:
        """Run all registered experiments and return results."""
        from dc_auto_tune.train.trainer import Trainer

        results: list[ExperimentResult] = []
        for name, override in self.experiments:
            config = self._apply_override(override)
            config.train.n_episodes = episodes
            config.train.steps_per_episode = steps_per_episode

            print(f"\n=== Experiment: {name} ===")
            t0 = time.time()
            trainer = Trainer(config)
            trainer.train()
            elapsed = time.time() - t0

            result = ExperimentResult(
                name=name,
                config_override=override,
                elapsed_s=elapsed,
                llm_calls=trainer.llm_call_count,
            )
            results.append(result)
            print(f"  Done in {elapsed:.0f}s, {trainer.llm_call_count} LLM calls")

        return results

    def _apply_override(self, override: dict) -> Config:
        """Deep-merge override dict into a copy of base_config."""
        config = copy.deepcopy(self.base_config)
        for section, values in override.items():
            if hasattr(config, section):
                target = getattr(config, section)
                if isinstance(values, dict):
                    for k, v in values.items():
                        if hasattr(target, k):
                            setattr(target, k, v)
            else:
                setattr(config, section, values)
        return config

    def summary_table(self, results: list[ExperimentResult]) -> str:
        """Generate a LaTeX-formatted summary table."""
        header = "Experiment & VoErr\\% & Ripple\\% & Eff\\% & Recov\\,ms & Over\\% & Under\\% & Start\\,ms \\\\"
        lines = [header, "\\midrule"]
        for r in results:
            m = r.metrics
            row = (
                f"{r.name} & {m.get('vo_error_pct',0):.1f} & "
                f"{m.get('vo_ripple_pct',0):.1f} & {m.get('efficiency_pct',0):.1f} & "
                f"{m.get('recovery_time_ms',0):.1f} & {m.get('overshoot_pct',0):.1f} & "
                f"{m.get('undershoot_pct',0):.1f} & {m.get('startup_time_ms',0):.1f} \\\\"
            )
            lines.append(row)
        return "\n".join(lines)
