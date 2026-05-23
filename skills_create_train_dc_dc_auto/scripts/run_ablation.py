#!/usr/bin/env python3
"""Run expanded ablation study with multiple trials and event-triggered mode.

Strategies:
  1. random      — Random search meta-optimization (fixed interval)
  2. bayesopt    — Bayesian Optimization with GP-EI (fixed interval)
  3. llm_fixed   — LLM meta-optimizer, fixed 50-ep interval (ours)
  4. llm_event   — LLM meta-optimizer, plateau event-triggered (ours, new)

Usage:
  python scripts/run_ablation.py --episodes 500 --trials 5
"""

import argparse
import json
import sys
import time
from collections import deque
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import torch

from dc_auto_tune.utils.config import load_config
from dc_auto_tune.env.buck_ccm import BuckCCMEnv
from dc_auto_tune.env.rewards import MultiObjectiveReward
from dc_auto_tune.rl.sac_agent import SACAgent
from dc_auto_tune.rl.replay_buffer import ReplayBuffer
from dc_auto_tune.eval.metrics import compute_metrics, check_tier
from dc_auto_tune.meta.hyperparam_space import HyperparamSpace
from dc_auto_tune.meta.plateau_detector import PlateauDetector
from dc_auto_tune.meta.ablation import (
    RandomSearchOptimizer,
    BayesOptOptimizer,
    LLMOptimizerWrapper,
)


def set_seed(seed: int):
    torch.manual_seed(seed)
    np.random.seed(seed)


def train_one_trial(
    name: str,
    suggest_fn,
    circuit_config,
    reward_fn_base,
    sac_config,
    train_config,
    meta_config,
    episodes: int,
    seed: int,
    use_event_trigger: bool = False,
) -> dict:
    """Train one trial of a meta-optimization strategy.

    Returns per-episode rewards, final metrics, timing, and intervention log.
    """
    set_seed(seed)
    env = BuckCCMEnv(circuit_config)
    reward_fn = MultiObjectiveReward(circuit_config.vout_ref, reward_fn_base.weights)
    agent = SACAgent(obs_dim=8, action_dim=1, params=sac_config)
    buffer = ReplayBuffer(sac_config.buffer_size, obs_dim=8, action_dim=1)

    rewards = []
    vo_readings = []
    llm_calls = 0
    intervention_eps = []
    t0 = time.time()

    # Event-triggered plateau detector
    if use_event_trigger:
        detector = PlateauDetector(
            window=meta_config.plateau_window,
            patience=meta_config.plateau_patience,
            improvement_threshold=meta_config.plateau_improvement_threshold,
            min_interval=meta_config.plateau_min_interval,
            max_interval=meta_config.plateau_max_interval,
        )
    else:
        detector = None

    reward_window = deque(maxlen=20)
    vo_error = 0.0
    vo_ripple = 0.0

    for ep in range(1, episodes + 1):
        obs = env.reset()
        reward_fn.reset()
        ep_reward = 0.0
        ep_vo = []

        for step in range(train_config.steps_per_episode):
            action = agent.select_action(obs, evaluate=False)
            next_obs, _, _, _, info = env.step(action)
            r = reward_fn.compute(info)
            buffer.push(obs, torch.tensor([action]), r, next_obs, False)
            obs = next_obs
            ep_reward += r
            ep_vo.append(info["vo"])

            if buffer.size >= sac_config.batch_size:
                batch = buffer.sample(sac_config.batch_size)
                if batch is not None:
                    agent.update(batch)

        avg_r = ep_reward / (step + 1)
        rewards.append(avg_r)
        reward_window.append(avg_r)
        vo_readings.extend(ep_vo[-100:])

        # Compute running metrics
        if len(ep_vo) >= 10:
            vo_error = abs(circuit_config.vout_ref - np.mean(ep_vo[-100:]))
            vo_error = vo_error / circuit_config.vout_ref * 100
            vo_ripple = float(np.std(ep_vo[-100:]) / circuit_config.vout_ref * 100)

        # Intervention decision
        should_intervene = False
        if use_event_trigger and detector is not None:
            window_avg = float(np.mean(reward_window)) if reward_window else avg_r
            should_intervene = detector.update(ep, window_avg)
        else:
            should_intervene = (ep % meta_config.intervention_interval == 0)

        if should_intervene:
            state = {
                "episode": ep,
                "recent_rewards": list(reward_window),
                "metrics": reward_fn.get_current_metrics(),
                "current_sac": agent.params,
                "current_weights": reward_fn.weights,
            }
            suggestion = suggest_fn(state)
            if "sac_updates" in suggestion:
                agent.update_hyperparams(**suggestion["sac_updates"])
            if "weight_updates" in suggestion:
                from dc_auto_tune.utils.types_ import RewardWeights
                new_w = RewardWeights(**{
                    **reward_fn.weights.__dict__,
                    **suggestion["weight_updates"],
                })
                reward_fn.update_weights(new_w)
            llm_calls += 1
            intervention_eps.append(ep)

        if ep % 10 == 0 or ep == 1:
            m = reward_fn.get_current_metrics()
            print(f"  [{name}][seed={seed}] ep {ep:4d}/{episodes} | "
                  f"avg_r={avg_r:+.4f} | verr={m.get('vo_error_pct',vo_error):.1f}% "
                  f"rip={m.get('vo_ripple_pct',vo_ripple):.1f}% "
                  f"eff={m.get('efficiency_pct',0):.0f}% | "
                  f"calls={llm_calls} | t={time.time()-t0:.0f}s")

    # ---- Final 7-metric evaluation on trained policy ----
    eval_metrics = _evaluate_policy(agent, circuit_config, n_steps=1000)

    elapsed = time.time() - t0
    final_vo = vo_readings[-100:] if vo_readings else []
    final_vo_mean = float(np.mean(final_vo)) if final_vo else 0
    final_vo_std = float(np.std(final_vo)) if len(final_vo) >= 10 else 0

    # Check P0/P1/P2 tier pass
    p0_pass, p0_detail = check_tier(eval_metrics, "P0")
    p1_pass, p1_detail = check_tier(eval_metrics, "P1")
    p2_pass, p2_detail = check_tier(eval_metrics, "P2")

    return {
        "rewards": rewards,
        "llm_calls": llm_calls,
        "intervention_eps": intervention_eps,
        "elapsed_s": elapsed,
        # Legacy simple metrics
        "final_vo_error_pct": vo_error,
        "final_vo_ripple_pct": vo_ripple,
        "final_vo_mean": final_vo_mean,
        "final_vo_std": final_vo_std,
        # Full 7-metric evaluation
        "eval_metrics": eval_metrics,
        "p0_pass": p0_pass,
        "p0_detail": p0_detail,
        "p1_pass": p1_pass,
        "p1_detail": p1_detail,
        "p2_pass": p2_pass,
        "p2_detail": p2_detail,
    }


def _evaluate_policy(
    agent: SACAgent,
    circuit: "CircuitParams",
    n_steps: int = 1000,
) -> dict:
    """Run a full evaluation rollout with startup + load-step transient.

    First half: startup from zero initial conditions at nominal load.
    Midpoint: load step (R_load halved → 2× load current).
    Second half: recovery under heavy load.
    """
    from copy import deepcopy
    from dc_auto_tune.utils.types_ import CircuitParams
    env = BuckCCMEnv(circuit)
    obs = env.reset()
    vo_history = []
    il_history = []
    p_in_history = []
    p_out_history = []
    load_step_idx: int | None = None

    half = n_steps // 2
    nominal_rload = circuit.R_load

    for i in range(n_steps):
        action = agent.select_action(obs, evaluate=True)
        obs, _, done, _, info = env.step(action)
        vo_history.append(info["vo"])
        il_history.append(info.get("iL", 0.0))
        p_in_history.append(info.get("p_in", 0.0))
        p_out_history.append(info.get("p_out", 0.0))
        if done:
            break
        if i == half:
            load_step_idx = len(vo_history)  # next sample will be post-step
            env.p.R_load = nominal_rload * 0.5  # 2× load current

    dt = env.T_sw  # one env.step() = one switching cycle
    m = compute_metrics(
        np.array(vo_history),
        np.array(il_history),
        circuit,
        dt=dt,
        p_in_history=np.array(p_in_history),
        p_out_history=np.array(p_out_history),
        load_step_idx=load_step_idx,
    )
    return m.to_dict()


def aggregate_trials(trials: list[dict]) -> dict:
    """Compute mean ± std across multiple trials."""
    all_rewards = [t["rewards"] for t in trials]
    min_len = min(len(r) for r in all_rewards)
    rewards_matrix = np.array([r[:min_len] for r in all_rewards])

    final_last20 = [np.mean(t["rewards"][-20:]) for t in trials]
    times = [t["elapsed_s"] for t in trials]
    calls = [t["llm_calls"] for t in trials]
    vo_errors = [t["final_vo_error_pct"] for t in trials]
    vo_ripples = [t["final_vo_ripple_pct"] for t in trials]

    # Aggregate full 7-metric evaluation
    eval_keys = ["vo_error_pct", "vo_ripple_pct", "efficiency_pct",
                 "overshoot_pct", "undershoot_pct", "recovery_time_ms", "startup_time_ms"]
    eval_agg = {}
    for key in eval_keys:
        vals = [t.get("eval_metrics", {}).get(key, 0) for t in trials]
        eval_agg[f"eval_{key}_mean"] = float(np.mean(vals)) if vals else 0
        eval_agg[f"eval_{key}_std"] = float(np.std(vals)) if len(vals) > 1 else 0

    # P0/P1/P2 pass rates
    p0_rate = sum(1 for t in trials if t.get("p0_pass", False)) / len(trials)
    p1_rate = sum(1 for t in trials if t.get("p1_pass", False)) / len(trials)
    p2_rate = sum(1 for t in trials if t.get("p2_pass", False)) / len(trials)

    return {
        "reward_mean": rewards_matrix.mean(axis=0).tolist(),
        "reward_std": rewards_matrix.std(axis=0).tolist(),
        "final_reward_mean": float(np.mean(final_last20)),
        "final_reward_std": float(np.std(final_last20)),
        "elapsed_s_mean": float(np.mean(times)),
        "elapsed_s_std": float(np.std(times)),
        "llm_calls_mean": float(np.mean(calls)),
        "llm_calls_std": float(np.std(calls)),
        "vo_error_mean": float(np.mean(vo_errors)),
        "vo_error_std": float(np.std(vo_errors)),
        "vo_ripple_mean": float(np.mean(vo_ripples)),
        "vo_ripple_std": float(np.std(vo_ripples)),
        "n_trials": len(trials),
        "per_trial": trials,
        # Full 7-metric aggregate
        **eval_agg,
        "p0_pass_rate": p0_rate,
        "p1_pass_rate": p1_rate,
        "p2_pass_rate": p2_rate,
    }


def main():
    parser = argparse.ArgumentParser(description="Run expanded ablation study")
    parser.add_argument("--episodes", type=int, default=500,
                        help="Episodes per trial (default: 500)")
    parser.add_argument("--trials", type=int, default=5,
                        help="Trials per strategy (default: 5)")
    parser.add_argument("--steps", type=int, default=200,
                        help="Steps per episode (default: 200)")
    parser.add_argument("--strategies", type=str, default="all",
                        help="Comma-separated: random,bayesopt,llm_fixed,llm_event or 'all'")
    parser.add_argument("--interval", type=int, default=None,
                        help="LLM intervention interval in episodes (default: 50)")
    parser.add_argument("--output", type=str, default=None,
                        help="Output JSON path (default: logs/ablation/results_expanded.json)")
    args = parser.parse_args()

    config = load_config("dc_auto_tune/configs/default.yaml")
    config.train.n_episodes = args.episodes
    config.train.steps_per_episode = args.steps
    config.train.warmup_steps = 500
    config.meta.intervention_interval = args.interval if args.interval is not None else 50

    print(f"=== Expanded Ablation Study ===")
    print(f"Episodes: {args.episodes}, Steps/ep: {args.steps}, Trials: {args.trials}")
    print(f"Total: {args.episodes * args.steps} steps per trial")
    print(f"LLM: {config.meta.llm_model}")
    print()

    space = HyperparamSpace()

    # Define strategies
    all_strategies = {
        "random": {
            "suggest_fn": RandomSearchOptimizer(space).suggest,
            "use_event_trigger": False,
            "label": "Random Search",
        },
        "bayesopt": {
            "suggest_fn": BayesOptOptimizer(space).suggest,
            "use_event_trigger": False,
            "label": "Bayesian Opt (GP-EI)",
        },
        "llm_fixed": {
            "suggest_fn": LLMOptimizerWrapper(config.meta, space).suggest,
            "use_event_trigger": False,
            "label": "LLM Fixed-Interval (Ours)",
        },
        "llm_event": {
            "suggest_fn": LLMOptimizerWrapper(config.meta, space).suggest,
            "use_event_trigger": True,
            "label": "LLM Event-Triggered (Ours)",
        },
    }

    # Filter strategies
    if args.strategies == "all":
        strategy_names = list(all_strategies.keys())
    else:
        strategy_names = [s.strip() for s in args.strategies.split(",")]

    all_results = {}
    out_dir = Path("logs/ablation")
    out_dir.mkdir(parents=True, exist_ok=True)

    for name in strategy_names:
        strat = all_strategies[name]
        print(f"{'='*60}")
        print(f"Strategy: {strat['label']} ({args.trials} trials × {args.episodes} ep)")
        print(f"Event-triggered: {strat['use_event_trigger']}")
        print(f"{'='*60}")

        trials = []
        for trial_idx in range(args.trials):
            seed = 42 + trial_idx * 100 + hash(name) % 1000
            print(f"\n--- Trial {trial_idx+1}/{args.trials} (seed={seed}) ---")
            result = train_one_trial(
                name=name,
                suggest_fn=strat["suggest_fn"],
                circuit_config=config.circuit,
                reward_fn_base=MultiObjectiveReward(config.circuit.vout_ref, config.reward_weights),
                sac_config=config.sac,
                train_config=config.train,
                meta_config=config.meta,
                episodes=args.episodes,
                seed=seed,
                use_event_trigger=strat["use_event_trigger"],
            )
            trials.append(result)
            print(f"  Trial {trial_idx+1} done: {result['elapsed_s']:.0f}s, "
                  f"{result['llm_calls']} LLM calls")

        aggregated = aggregate_trials(trials)
        aggregated["label"] = strat["label"]
        aggregated["use_event_trigger"] = strat["use_event_trigger"]
        all_results[name] = aggregated

        print(f"\n  Aggregate: final_reward={aggregated['final_reward_mean']:+.4f}±"
              f"{aggregated['final_reward_std']:.4f} | "
              f"vo_err={aggregated['vo_error_mean']:.2f}±{aggregated['vo_error_std']:.2f}% | "
              f"time={aggregated['elapsed_s_mean']:.0f}±{aggregated['elapsed_s_std']:.0f}s")

    # Save aggregated results
    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
    else:
        out_path = out_dir / "results_expanded.json"
    with open(out_path, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\nResults saved to {out_path}")

    # Print summary table
    print(f"\n{'='*120}")
    print(f"FINAL SUMMARY ({args.episodes}ep × {args.trials} trials) — Full Multi-Objective Evaluation")
    print(f"{'='*120}")
    header = (f"{'Strategy':<25} {'Reward':>12} {'VoErr%':>8} {'Rip%':>8} "
              f"{'Eff%':>8} {'Ov%':>8} {'Uv%':>8} {'Recovms':>8} {'Startms':>10} "
              f"{'P0%':>6} {'Time(s)':>8} {'Calls':>6}")
    print(header)
    print("-" * 120)
    for name in strategy_names:
        r = all_results[name]
        print(f"{r['label']:<25} "
              f"{r['final_reward_mean']:>+6.3f}±{r['final_reward_std']:.2f} "
              f"{r.get('eval_vo_error_pct_mean', 0):>6.2f}±{r.get('eval_vo_error_pct_std', 0):.2f} "
              f"{r.get('eval_vo_ripple_pct_mean', 0):>6.2f}±{r.get('eval_vo_ripple_pct_std', 0):.2f} "
              f"{r.get('eval_efficiency_pct_mean', 0):>6.1f}±{r.get('eval_efficiency_pct_std', 0):.1f} "
              f"{r.get('eval_overshoot_pct_mean', 0):>6.2f}±{r.get('eval_overshoot_pct_std', 0):.2f} "
              f"{r.get('eval_undershoot_pct_mean', 0):>6.2f}±{r.get('eval_undershoot_pct_std', 0):.2f} "
              f"{r.get('eval_recovery_time_ms_mean', 0):>6.2f}±{r.get('eval_recovery_time_ms_std', 0):.2f} "
              f"{r.get('eval_startup_time_ms_mean', 0):>8.2f}±{r.get('eval_startup_time_ms_std', 0):.2f} "
              f"{r.get('p0_pass_rate', 0)*100:>5.0f}% "
              f"{r['elapsed_s_mean']:>6.0f}±{r['elapsed_s_std']:.0f} "
              f"{r['llm_calls_mean']:>4.0f}±{r['llm_calls_std']:.0f}")


if __name__ == "__main__":
    main()
