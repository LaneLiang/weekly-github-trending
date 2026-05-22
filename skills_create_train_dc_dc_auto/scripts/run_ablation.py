#!/usr/bin/env python3
"""Run ablation study: LLM vs Random Search vs Bayesian Optimization.

Generates convergence curves and saves results to logs/ablation/.
"""

import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import torch

from dc_auto_tune.utils.config import load_config
from dc_auto_tune.utils.types_ import MetaOptConfig
from dc_auto_tune.env.buck_ccm import BuckCCMEnv
from dc_auto_tune.env.rewards import MultiObjectiveReward
from dc_auto_tune.rl.sac_agent import SACAgent
from dc_auto_tune.rl.replay_buffer import ReplayBuffer
from dc_auto_tune.meta.hyperparam_space import HyperparamSpace
from dc_auto_tune.meta.ablation import (
    RandomSearchOptimizer,
    BayesOptOptimizer,
    LLMOptimizerWrapper,
)


def train_one_strategy(
    name: str,
    suggest_fn,
    circuit_config,
    reward_fn_base,
    sac_config,
    train_config,
    meta_config,
    episodes: int,
) -> dict:
    """Train with one meta-optimization strategy and return per-episode rewards."""
    env = BuckCCMEnv(circuit_config)
    reward_fn = MultiObjectiveReward(circuit_config.vout_ref, reward_fn_base.weights)
    agent = SACAgent(obs_dim=8, action_dim=1, params=sac_config)
    buffer = ReplayBuffer(sac_config.buffer_size, obs_dim=8, action_dim=1)

    rewards = []
    metrics_history = []
    llm_calls = 0
    t0 = time.time()

    for ep in range(1, episodes + 1):
        obs = env.reset()
        ep_reward = 0.0
        vo_readings = []

        for step in range(train_config.steps_per_episode):
            action = agent.select_action(obs, evaluate=False)
            next_obs, r, _, _, info = env.step(action)
            buffer.push(obs, torch.tensor([action]), r, next_obs, False)
            obs = next_obs
            ep_reward += r
            vo_readings.append(info["vo"])

            if buffer.size >= sac_config.batch_size:
                batch = buffer.sample(sac_config.batch_size)
                if batch is not None:
                    agent.update(batch)

        avg_r = ep_reward / (step + 1)
        rewards.append(avg_r)

        # Compute metrics
        vo = np.mean(vo_readings[-100:]) if vo_readings else 0
        vo_error = abs(circuit_config.vout_ref - vo) / circuit_config.vout_ref * 100
        vo_ripple = float(np.std(vo_readings[-100:]) / circuit_config.vout_ref * 100) if len(vo_readings) >= 10 else 0

        # LLM intervention
        if ep % meta_config.intervention_interval == 0:
            state = {
                "episode": ep,
                "recent_rewards": rewards[-20:],
                "metrics": {
                    "vo_ripple_pct": vo_ripple,
                    "vo_error_pct": vo_error,
                    "recovery_time_ms": 0,
                    "overshoot_pct": 0,
                    "undershoot_pct": 0,
                },
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

        if ep % 20 == 0 or ep == 1:
            print(f"  [{name}] ep {ep:4d}/{episodes} | avg_r={avg_r:+.4f} | vo_err={vo_error:.1f}% | "
                  f"ripple={vo_ripple:.2f}% | time={time.time()-t0:.0f}s")

    elapsed = time.time() - t0
    print(f"  [{name}] DONE in {elapsed:.0f}s ({elapsed/episodes:.1f}s/ep), {llm_calls} LLM calls")

    return {
        "rewards": rewards,
        "llm_calls": llm_calls,
        "elapsed_s": elapsed,
        "final_vo_error_pct": vo_error,
        "final_vo_ripple_pct": vo_ripple,
    }


def main():
    config = load_config("dc_auto_tune/configs/default.yaml")

    # Shortened training for ablation study
    config.train.n_episodes = 200
    config.train.steps_per_episode = 200
    config.train.warmup_steps = 500
    config.meta.intervention_interval = 50

    episodes = config.train.n_episodes
    print(f"=== Ablation Study: {episodes} episodes, {config.train.steps_per_episode} steps/ep ===")
    print(f"LLM: {config.meta.llm_model} @ {config.meta.llm_base_url}")
    print()

    space = HyperparamSpace()
    strategies = {
        "random": RandomSearchOptimizer(space).suggest,
        "bayesopt": BayesOptOptimizer(space).suggest,
        "llm": LLMOptimizerWrapper(config.meta, space).suggest,
    }

    all_results = {}

    for name, suggest_fn in strategies.items():
        print(f"--- Running {name} ---")
        result = train_one_strategy(
            name=name,
            suggest_fn=suggest_fn,
            circuit_config=config.circuit,
            reward_fn_base=MultiObjectiveReward(config.circuit.vout_ref, config.reward_weights),
            sac_config=config.sac,
            train_config=config.train,
            meta_config=config.meta,
            episodes=episodes,
        )
        all_results[name] = result
        print()

    # Save results
    out_dir = Path("logs/ablation")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "results.json"
    with open(out_path, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"Results saved to {out_path}")

    # Quick comparison
    print()
    print("=== Summary ===")
    for name, r in all_results.items():
        final_rewards = r["rewards"][-20:]
        print(f"  {name:12s}: final_avg_r={np.mean(final_rewards):+.4f} | "
              f"vo_err={r['final_vo_error_pct']:.1f}% | "
              f"time={r['elapsed_s']:.0f}s | "
              f"llm_calls={r['llm_calls']}")


if __name__ == "__main__":
    main()
