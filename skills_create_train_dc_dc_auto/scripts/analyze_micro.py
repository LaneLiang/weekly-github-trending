#!/usr/bin/env python3
"""Analyze micro-validation results with full 7-metric P0/P1/P2 tier checks."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dc_auto_tune.eval.metrics import (
    check_tier, tier_pass_rate, compute_hypervolume,
    compute_c_metric, compute_psr
)

TIER_NAMES = ["P0", "P1", "P2"]
METRIC_KEYS = ["vo_error_pct", "vo_ripple_pct", "efficiency_pct",
               "overshoot_pct", "undershoot_pct", "recovery_time_ms", "startup_time_ms"]


def load_results(path: str) -> dict:
    with open(path) as f:
        return json.load(f)


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "logs/ablation/micro_v4_final.json"
    data = load_results(path)

    print("=" * 100)
    print("MICRO-VALIDATION ANALYSIS — Full 7-Metric Multi-Objective Evaluation")
    print("=" * 100)

    # Collect per-strategy eval metrics for HV/C-metric
    all_eval_metrics: dict[str, list[dict]] = {}

    for strategy_name, result in data.items():
        label = result.get("label", strategy_name)
        n_trials = result.get("n_trials", 0)
        print(f"\n{'─' * 80}")
        print(f"  {label} ({n_trials} trials)")
        print(f"{'─' * 80}")

        # Basic stats
        print(f"  Final reward:    {result.get('final_reward_mean', 0):+.4f} ± "
              f"{result.get('final_reward_std', 0):.4f}")
        print(f"  Wall time:       {result.get('elapsed_s_mean', 0):.0f} ± "
              f"{result.get('elapsed_s_std', 0):.0f}s")
        print(f"  LLM calls:       {result.get('llm_calls_mean', 0):.0f} ± "
              f"{result.get('llm_calls_std', 0):.0f}")

        # 7-metric evaluation
        print(f"\n  {'Metric':<22} {'Mean':>8} {'± Std':>8}  {'P0':>6}  {'P1':>6}  {'P2':>6}")
        print(f"  {'─'*22} {'─'*8} {'─'*8}  {'─'*6}  {'─'*6}  {'─'*6}")

        eval_metrics_list = []
        per_trial = result.get("per_trial", [])
        for key in METRIC_KEYS:
            eval_key = f"eval_{key}"
            mean = result.get(f"{eval_key}_mean", 0)
            std = result.get(f"{eval_key}_std", 0)

            # Check per-tier status from per-trial eval data
            p0_ok = sum(1 for t in per_trial
                       if t.get("eval_metrics", {}).get(key, 999) <
                       (999 if "efficiency" not in key else 0))  # simplified
            print(f"  {key:<22} {mean:>8.2f} {std:>8.2f}", end="")

            # Simplified tier check using mean
            for tier in TIER_NAMES:
                from dc_auto_tune.eval.metrics import TIER_SPECS
                spec = TIER_SPECS.get(tier, {})
                if key in spec:
                    limit, direction = spec[key]
                    if direction == "lt":
                        ok = mean < limit
                    else:
                        ok = mean > limit
                    print(f"  {'✓' if ok else '✗':>6}", end="")
                else:
                    print(f"  {'—':>6}", end="")
            print()

        # Per-trial eval metrics
        for t in per_trial:
            em = t.get("eval_metrics", {})
            if em:
                eval_metrics_list.append(em)

        all_eval_metrics[strategy_name] = eval_metrics_list

        # P0/P1/P2 pass rates from the result
        p0 = result.get("p0_pass_rate", 0)
        p1 = result.get("p1_pass_rate", 0)
        p2 = result.get("p2_pass_rate", 0)
        print(f"\n  Tier pass rates: P0={p0*100:.0f}%  P1={p1*100:.0f}%  P2={p2*100:.0f}%")

    # Cross-strategy comparisons
    print(f"\n{'=' * 100}")
    print("CROSS-STRATEGY COMPARISON (Multi-Objective)")
    print(f"{'=' * 100}")

    # Hypervolume per strategy
    print(f"\n  {'Strategy':<30} {'Hypervolume':>12}")
    print(f"  {'─'*30} {'─'*12}")
    for name, result in data.items():
        per_trial = result.get("per_trial", [])
        eval_list = [t.get("eval_metrics", {}) for t in per_trial if t.get("eval_metrics")]
        hv = compute_hypervolume(eval_list)
        print(f"  {result.get('label', name):<30} {hv:>12.4f}")

    # C-metric: compare LLM strategies vs Random Search
    if "random" in all_eval_metrics:
        random_metrics = all_eval_metrics["random"]
        print(f"\n  C-metric (coverage of Random Search):")
        for name, metrics_list in all_eval_metrics.items():
            if name == "random" or not metrics_list:
                continue
            c_val = compute_c_metric(metrics_list, random_metrics)
            label = data.get(name, {}).get("label", name)
            print(f"    C({label}, Random) = {c_val:.3f}")


if __name__ == "__main__":
    main()
