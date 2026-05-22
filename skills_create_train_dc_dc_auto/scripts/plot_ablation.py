#!/usr/bin/env python3
"""Generate ablation comparison charts from results.json."""

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))


def load_results(path: str = "logs/ablation/results.json") -> dict:
    with open(path) as f:
        return json.load(f)


def smooth(data: list[float], window: int = 10) -> np.ndarray:
    arr = np.array(data)
    if len(arr) < window:
        return arr
    kernel = np.ones(window) / window
    return np.convolve(arr, kernel, mode="valid")


def plot_convergence(results: dict, out_path: str = "logs/ablation/convergence.png"):
    """Generate reward-vs-episode convergence plot."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed; skipping plot generation")
        return

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    colors = {"random": "#e74c3c", "bayesopt": "#3498db", "llm": "#2ecc71"}
    labels = {"random": "Random Search", "bayesopt": "Bayesian Opt (GP-EI)", "llm": "LLM Meta-Optimizer (Ours)"}

    # Left: raw + smoothed
    for name in ["random", "bayesopt", "llm"]:
        if name not in results:
            continue
        rewards = results[name]["rewards"]
        smoothed = smooth(rewards, window=15)
        ax1.plot(rewards, alpha=0.15, color=colors[name])
        ax1.plot(range(len(smoothed)), smoothed, color=colors[name],
                 linewidth=2, label=labels[name])

    ax1.set_xlabel("Episode")
    ax1.set_ylabel("Avg Reward / Episode")
    ax1.set_title("Convergence Comparison (200 episodes)")
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Right: final performance bar chart
    names = ["random", "bayesopt", "llm"]
    final_means = []
    final_stds = []
    for name in names:
        last20 = results[name]["rewards"][-20:]
        final_means.append(np.mean(last20))
        final_stds.append(np.std(last20))

    bars = ax2.bar([labels[n] for n in names], final_means,
                   yerr=final_stds, color=[colors[n] for n in names],
                   capsize=5, edgecolor="black", linewidth=0.5)
    ax2.set_ylabel("Final Reward (last 20 ep)")
    ax2.set_title("Final Performance Comparison")
    ax2.grid(True, alpha=0.3, axis="y")

    # Annotate values
    for bar, val in zip(bars, final_means):
        ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.002,
                 f"{val:.4f}", ha="center", va="bottom", fontsize=10)

    plt.tight_layout()
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    print(f"Convergence plot saved to {out_path}")
    plt.close()


def main():
    results_path = "logs/ablation/results.json"
    if not Path(results_path).exists():
        print(f"Results file not found: {results_path}")
        print("Run scripts/run_ablation.py first.")
        sys.exit(1)

    results = load_results(results_path)

    # Print summary table
    print("=== Ablation Results Summary ===")
    print(f"{'Strategy':<15} {'Final Reward':>14} {'± Std':>10} {'Time':>10} {'LLM Calls':>10}")
    print("-" * 62)
    for name in ["random", "bayesopt", "llm"]:
        if name not in results:
            continue
        r = results[name]
        last20 = r["rewards"][-20:]
        print(f"{name:<15} {np.mean(last20):>14.4f} {np.std(last20):>10.4f} "
              f"{r['elapsed_s']:>8.0f}s {r['llm_calls']:>10}")

    # Best strategy
    best = max(results, key=lambda n: np.mean(results[n]["rewards"][-20:]))
    print(f"\nBest strategy: {best}")

    # Generate plots
    plot_convergence(results)


if __name__ == "__main__":
    main()
