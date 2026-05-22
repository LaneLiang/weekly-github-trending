"""Tests for ablation study meta-optimizer comparison."""

import pytest
from dc_auto_tune.utils.types_ import SACParams, RewardWeights
from dc_auto_tune.meta.hyperparam_space import HyperparamSpace
from dc_auto_tune.meta.ablation import (
    RandomSearchOptimizer,
    BayesOptOptimizer,
    _sac_params_to_vec,
    _weights_to_vec,
    _vec_to_sac_updates,
    _vec_to_weight_updates,
    _SimpleGP,
)


class TestRandomSearchOptimizer:
    def test_suggest_returns_valid_structure(self):
        opt = RandomSearchOptimizer(HyperparamSpace())
        state = {
            "episode": 10,
            "recent_rewards": [-0.5, -0.4, -0.3],
            "metrics": {},
            "current_sac": SACParams(),
            "current_weights": RewardWeights(),
        }
        result = opt.suggest(state)
        assert "analysis" in result
        assert "sac_updates" in result
        assert "weight_updates" in result
        assert isinstance(result["sac_updates"], dict)
        assert isinstance(result["weight_updates"], dict)

    def test_suggest_stays_within_bounds(self):
        opt = RandomSearchOptimizer(HyperparamSpace(), noise_scale=0.5)
        state = {
            "current_sac": SACParams(),
            "current_weights": RewardWeights(),
        }
        for _ in range(20):
            result = opt.suggest(state)
            sac = result["sac_updates"]
            for k, v in sac.items():
                lo, hi = HyperparamSpace.SAC_BOUNDS.get(k, (0, float("inf")))
                assert lo <= v <= hi, f"{k}={v} out of bounds [{lo}, {hi}]"
            weights = result["weight_updates"]
            for k, v in weights.items():
                lo, hi = HyperparamSpace.WEIGHT_BOUNDS.get(k, (0, float("inf")))
                assert lo <= v <= hi, f"{k}={v} out of bounds [{lo}, {hi}]"


class TestBayesOptOptimizer:
    def test_suggest_returns_valid_structure(self):
        opt = BayesOptOptimizer(HyperparamSpace())
        state = {
            "episode": 10,
            "recent_rewards": [-0.5, -0.4, -0.3],
            "current_sac": SACParams(),
            "current_weights": RewardWeights(),
        }
        result = opt.suggest(state)
        assert "analysis" in result
        assert "sac_updates" in result
        assert "weight_updates" in result

    def test_random_phase_then_gp_phase(self):
        opt = BayesOptOptimizer(HyperparamSpace(), n_random=3)
        state = {
            "recent_rewards": [-0.5],
            "current_sac": SACParams(),
            "current_weights": RewardWeights(),
        }
        # First 3 calls should be random exploration
        for i in range(3):
            result = opt.suggest(state)
            assert "random exploration" in result["analysis"].lower()
        # 4th call should switch to GP
        result = opt.suggest(state)
        assert "ei" in result["analysis"].lower()

    def test_stays_within_bounds(self):
        opt = BayesOptOptimizer(HyperparamSpace(), n_random=1)
        state = {
            "recent_rewards": [-0.5],
            "current_sac": SACParams(),
            "current_weights": RewardWeights(),
        }
        for _ in range(20):
            # Force random phase to test bounds
            opt.call_count = 0
            result = opt.suggest(state)
            for k, v in result["sac_updates"].items():
                lo, hi = HyperparamSpace.SAC_BOUNDS.get(k, (0, float("inf")))
                assert lo <= v <= hi, f"{k}={v} out of bounds"
            for k, v in result["weight_updates"].items():
                lo, hi = HyperparamSpace.WEIGHT_BOUNDS.get(k, (0, float("inf")))
                assert lo <= v <= hi, f"{k}={v} out of bounds"


class TestVectorConversion:
    def test_sac_roundtrip(self):
        orig = SACParams()
        vec = _sac_params_to_vec(orig)
        updates = _vec_to_sac_updates(vec, orig)
        for f in SACParams.__dataclass_fields__:
            assert f in updates
            # Normalised values should decode back close to original
            assert abs(updates[f] - getattr(orig, f)) < 1e-6 * max(abs(getattr(orig, f)), 1.0)

    def test_weight_roundtrip(self):
        orig = RewardWeights()
        vec = _weights_to_vec(orig)
        updates = _vec_to_weight_updates(vec, orig)
        for f in RewardWeights.__dataclass_fields__:
            assert f in updates


class TestSimpleGP:
    def test_fit_predict(self):
        gp = _SimpleGP(length_scale=1.0, noise=1e-6)
        import numpy as np
        X = np.array([[0.0], [1.0], [2.0]])
        y = np.array([0.0, 1.0, 0.0])
        gp.fit(X, y)
        mu, sigma2 = gp.predict(np.array([[0.5], [1.5]]))
        assert mu.shape == (2,)
        assert sigma2.shape == (2,)
        assert all(s > 0 for s in sigma2)

    def test_predict_at_training_points(self):
        gp = _SimpleGP(length_scale=1.0, noise=1e-8)
        import numpy as np
        X = np.array([[0.0], [1.0]])
        y = np.array([0.5, -0.5])
        gp.fit(X, y)
        mu, sigma2 = gp.predict(X)
        assert abs(mu[0] - 0.5) < 1e-4
        assert abs(mu[1] - (-0.5)) < 1e-4
