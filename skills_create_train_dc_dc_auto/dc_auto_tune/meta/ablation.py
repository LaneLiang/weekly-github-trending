"""Ablation study: compare LLM vs Random Search vs Bayesian Optimization meta-optimizers."""

import math
import numpy as np
from typing import Callable
from dataclasses import fields

from dc_auto_tune.utils.types_ import SACParams, RewardWeights, MetaOptConfig
from dc_auto_tune.meta.hyperparam_space import HyperparamSpace
from dc_auto_tune.meta.optimizer import LLMMetaOptimizer


def _sac_params_to_vec(params: SACParams) -> np.ndarray:
    """Flatten a SACParams into a normalised vector."""
    bounds = HyperparamSpace.SAC_BOUNDS
    vec = []
    for f in fields(params):
        lo, hi = bounds.get(f.name, (getattr(params, f.name) * 0.5,
                                     getattr(params, f.name) * 2.0))
        val = getattr(params, f.name)
        mid = (lo + hi) / 2.0
        half = (hi - lo) / 2.0
        vec.append((val - mid) / max(half, 1e-9))
    return np.array(vec, dtype=np.float64)


def _weights_to_vec(weights: RewardWeights) -> np.ndarray:
    """Flatten RewardWeights into a normalised vector."""
    bounds = HyperparamSpace.WEIGHT_BOUNDS
    vec = []
    for f in fields(weights):
        lo, hi = bounds.get(f.name, (0.1, 5.0))
        val = getattr(weights, f.name)
        mid = (lo + hi) / 2.0
        half = (hi - lo) / 2.0
        vec.append((val - mid) / max(half, 1e-9))
    return np.array(vec, dtype=np.float64)


def _vec_to_sac_updates(vec: np.ndarray, base: SACParams) -> dict:
    """Convert normalised vector back to SAC parameter dict."""
    bounds = HyperparamSpace.SAC_BOUNDS
    result = {}
    for i, f in enumerate(fields(base)):
        if i >= len(vec):
            break
        lo, hi = bounds.get(f.name, (getattr(base, f.name) * 0.5,
                                     getattr(base, f.name) * 2.0))
        mid = (lo + hi) / 2.0
        half = (hi - lo) / 2.0
        result[f.name] = float(np.clip(vec[i] * half + mid, lo, hi))
    return result


def _vec_to_weight_updates(vec: np.ndarray, base: RewardWeights,
                            offset: int = 0) -> dict:
    """Convert normalised vector back to weight dict."""
    bounds = HyperparamSpace.WEIGHT_BOUNDS
    result = {}
    for i, f in enumerate(fields(base)):
        idx = offset + i
        if idx >= len(vec):
            break
        lo, hi = bounds.get(f.name, (0.1, 5.0))
        mid = (lo + hi) / 2.0
        half = (hi - lo) / 2.0
        result[f.name] = float(np.clip(vec[idx] * half + mid, lo, hi))
    return result


class _SimpleGP:
    """Minimal Gaussian Process regressor with RBF kernel."""

    def __init__(self, length_scale: float = 1.0, noise: float = 1e-3):
        self.length_scale = length_scale
        self.noise = noise
        self.X: np.ndarray | None = None
        self.y: np.ndarray | None = None
        self.K_inv: np.ndarray | None = None

    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        self.X = X.copy()
        self.y = y.copy().reshape(-1, 1)
        K = self._kernel(X, X) + self.noise * np.eye(len(X))
        self.K_inv = np.linalg.inv(K)

    def predict(self, X: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        K_s = self._kernel(self.X, X)
        K_ss = self._kernel(X, X)
        mu = K_s.T @ self.K_inv @ self.y
        sigma2 = K_ss - K_s.T @ self.K_inv @ K_s
        return mu.flatten(), np.maximum(sigma2.diagonal(), 1e-9)

    def _kernel(self, X1: np.ndarray, X2: np.ndarray) -> np.ndarray:
        dist2 = (
            np.sum(X1**2, axis=1).reshape(-1, 1)
            + np.sum(X2**2, axis=1).reshape(1, -1)
            - 2 * X1 @ X2.T
        )
        return np.exp(-0.5 * dist2 / self.length_scale**2)


class RandomSearchOptimizer:
    """Baseline: randomly perturb hyperparameters within bounds."""

    def __init__(self, space: HyperparamSpace, noise_scale: float = 0.1):
        self.space = space
        self.noise_scale = noise_scale
        self._rng = np.random.RandomState(42)

    def suggest(self, training_state: dict) -> dict:
        sac = training_state["current_sac"]
        weights = training_state["current_weights"]
        sac_updates = {}
        for f in fields(sac):
            val = getattr(sac, f.name)
            noise = self._rng.normal(0, self.noise_scale * max(abs(val), 1e-6))
            sac_updates[f.name] = val + noise
        weight_updates = {}
        for f in fields(weights):
            val = getattr(weights, f.name)
            noise = self._rng.normal(0, self.noise_scale * max(abs(val), 1e-6))
            weight_updates[f.name] = val + noise
        sac_updates = self.space.validate_and_clamp_sac(sac_updates)
        weight_updates = self.space.validate_and_clamp_weights(weight_updates)
        return {
            "analysis": f"Random perturbation (noise_scale={self.noise_scale})",
            "sac_updates": sac_updates,
            "weight_updates": weight_updates,
        }


class BayesOptOptimizer:
    """Bayesian optimization meta-optimizer using GP surrogate + Expected Improvement.

    Maintains a history of (hyperparam_vector, avg_reward) pairs, fits a GP,
    and proposes the point that maximises expected improvement.
    """

    def __init__(self, space: HyperparamSpace, n_random: int = 5):
        self.space = space
        self.n_random = n_random
        self.gp = _SimpleGP(length_scale=0.5)
        self.X: list[np.ndarray] = []
        self.y: list[float] = []
        self.call_count = 0
        self._rng = np.random.RandomState(99)

    def suggest(self, training_state: dict) -> dict:
        sac = training_state["current_sac"]
        weights = training_state["current_weights"]
        current_vec = np.concatenate([_sac_params_to_vec(sac), _weights_to_vec(weights)])
        reward = float(np.mean(training_state.get("recent_rewards", [0])))

        self.X.append(current_vec)
        self.y.append(reward)
        self.call_count += 1

        sac_updates: dict = {}
        weight_updates: dict = {}

        n_sac = len(list(fields(sac)))
        if self.call_count <= self.n_random:
            # Initial random exploration
            candidate = current_vec + self._rng.normal(0, 0.3, size=len(current_vec))
            sac_updates = _vec_to_sac_updates(candidate, sac)
            weight_updates = _vec_to_weight_updates(candidate, weights, offset=n_sac)
            analysis = f"BayesOpt random exploration ({self.call_count}/{self.n_random})"
        else:
            try:
                self.gp.fit(np.array(self.X), np.array(self.y))
                best_y = max(self.y)
                # Random sampling to optimize EI
                candidates = current_vec + self._rng.normal(
                    0, 0.5, size=(500, len(current_vec))
                )
                mu, sigma = self.gp.predict(candidates)
                sigma = np.sqrt(np.maximum(sigma, 0))
                improvement = mu - best_y
                Z = np.where(sigma > 1e-9, improvement / sigma, 0)
                ei = improvement * _norm_cdf(Z) + sigma * _norm_pdf(Z)
                best_idx = int(np.argmax(ei))
                candidate = candidates[best_idx]
                sac_updates = _vec_to_sac_updates(candidate, sac)
                weight_updates = _vec_to_weight_updates(candidate, weights, offset=n_sac)
                analysis = f"BayesOpt EI (best_y={best_y:.3f}, n_obs={len(self.X)})"
            except np.linalg.LinAlgError:
                analysis = "BayesOpt GP singular matrix, falling back to random"
                candidate = current_vec + self._rng.normal(0, 0.3, size=len(current_vec))
                sac_updates = _vec_to_sac_updates(candidate, sac)
                weight_updates = _vec_to_weight_updates(candidate, weights, offset=n_sac)

        sac_updates = self.space.validate_and_clamp_sac(sac_updates)
        weight_updates = self.space.validate_and_clamp_weights(weight_updates)
        return {
            "analysis": analysis,
            "sac_updates": sac_updates,
            "weight_updates": weight_updates,
        }


def _norm_cdf(x: np.ndarray) -> np.ndarray:
    return 0.5 * (1.0 + np.vectorize(math.erf)(x / math.sqrt(2)))


def _norm_pdf(x: np.ndarray) -> np.ndarray:
    return np.exp(-0.5 * x**2) / math.sqrt(2 * math.pi)


class LLMOptimizerWrapper:
    """Thin wrapper around LLMMetaOptimizer for uniform interface."""

    def __init__(self, meta_config: MetaOptConfig, space: HyperparamSpace):
        self.opt = LLMMetaOptimizer(meta_config, space)

    def suggest(self, training_state: dict) -> dict:
        return self.opt.analyze_and_suggest(training_state)


def run_ablation(
    meta_config: MetaOptConfig,
    train_config: "TrainConfig",
    circuit_config: "CircuitParams",
    sac_config: SACParams,
    weight_config: RewardWeights,
    n_trials: int = 3,
    episodes_per_trial: int = 100,
) -> dict:
    """Run all three strategies and return comparison results.

    Returns:
        Dict mapping strategy name to list of per-episode rewards.
    """
    from dc_auto_tune.env.buck_ccm import BuckCCMEnv
    from dc_auto_tune.env.rewards import MultiObjectiveReward
    from dc_auto_tune.rl.sac_agent import SACAgent
    from dc_auto_tune.rl.replay_buffer import ReplayBuffer
    import torch

    space = HyperparamSpace()
    strategies: dict[str, Callable] = {
        "random": RandomSearchOptimizer(space).suggest,
        "bayesopt": BayesOptOptimizer(space).suggest,
        "llm": LLMOptimizerWrapper(meta_config, space).suggest,
    }

    results: dict[str, list] = {name: [] for name in strategies}

    for name, suggest_fn in strategies.items():
        for trial in range(n_trials):
            env = BuckCCMEnv(circuit_config)
            reward_fn = MultiObjectiveReward(circuit_config.vout_ref, weight_config)
            agent = SACAgent(obs_dim=8, action_dim=1, params=sac_config)
            buffer = ReplayBuffer(sac_config.buffer_size, obs_dim=8, action_dim=1)

            trial_rewards = []
            for ep in range(1, episodes_per_trial + 1):
                obs = env.reset()
                ep_reward = 0.0
                for step in range(train_config.steps_per_episode):
                    action = agent.select_action(obs, evaluate=False)
                    next_obs, r, _, _, info = env.step(action)
                    buffer.push(obs, torch.tensor([action]), r, next_obs, False)
                    obs = next_obs
                    ep_reward += r
                    if buffer.size >= sac_config.batch_size:
                        batch = buffer.sample(sac_config.batch_size)
                        if batch is not None:
                            agent.update(batch)

                avg_r = ep_reward / (step + 1)
                trial_rewards.append(avg_r)

                if ep % meta_config.intervention_interval == 0:
                    state = {
                        "episode": ep,
                        "recent_rewards": trial_rewards[-20:],
                        "metrics": {},
                        "current_sac": agent.params,
                        "current_weights": reward_fn.weights,
                    }
                    suggestion = suggest_fn(state)
                    if "sac_updates" in suggestion:
                        agent.update_hyperparams(**suggestion["sac_updates"])
                    if "weight_updates" in suggestion:
                        new_w = RewardWeights(**{
                            **reward_fn.weights.__dict__,
                            **suggestion["weight_updates"],
                        })
                        reward_fn.update_weights(new_w)

            results[name].extend(trial_rewards)

    return results
