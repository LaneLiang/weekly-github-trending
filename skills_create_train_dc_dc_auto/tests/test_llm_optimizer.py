"""Tests for LLMMetaOptimizer — RED phase: tests must fail because the optimizer module doesn't exist yet."""

import pytest
from unittest.mock import Mock, patch
from dc_auto_tune.meta.optimizer import LLMMetaOptimizer
from dc_auto_tune.utils.types_ import MetaOptConfig, SACParams, RewardWeights
from dc_auto_tune.meta.hyperparam_space import HyperparamSpace


class TestLLMMetaOptimizer:
    @pytest.fixture
    def optimizer(self):
        config = MetaOptConfig(temperature=0.2)
        space = HyperparamSpace()
        return LLMMetaOptimizer(config, space)

    @pytest.fixture
    def mock_training_curve(self):
        return {
            "episode": 200,
            "recent_rewards": [0.5, 0.6, 0.55, 0.7, 0.65],
            "metrics": {
                "vo_ripple_pct": 1.2,
                "vo_error_pct": 0.8,
                "recovery_time_ms": 0.45,
                "overshoot_pct": 3.5,
                "undershoot_pct": 2.1,
            },
            "current_sac": SACParams(),
            "current_weights": RewardWeights(),
        }

    @patch("dc_auto_tune.meta.llm_client.LLMClient")
    def test_analyze_and_suggest_returns_valid_update(self, mock_llm, optimizer, mock_training_curve):
        mock_llm.return_value.chat.return_value = (
            '{"analysis": "ripple is the main bottleneck", '
            '"sac_updates": {"actor_lr": 0.0002}, '
            '"weight_updates": {"w_vr": 2.0}}'
        )
        result = optimizer.analyze_and_suggest(mock_training_curve)
        assert "analysis" in result
        assert "sac_updates" in result
        assert "weight_updates" in result

    @patch("dc_auto_tune.meta.llm_client.LLMClient")
    def test_suggestions_within_bounds(self, mock_llm, optimizer, mock_training_curve):
        """Suggested hyperparameters must stay within valid range even for out-of-bounds LLM output."""
        mock_llm.return_value.chat.return_value = (
            '{"analysis": "test", '
            '"sac_updates": {"actor_lr": 999.0, "gamma": 5.0}, '
            '"weight_updates": {"w_vr": -10.0}}'
        )
        result = optimizer.analyze_and_suggest(mock_training_curve)
        assert result["sac_updates"]["actor_lr"] <= HyperparamSpace.SAC_BOUNDS["actor_lr"][1]
        assert result["sac_updates"]["gamma"] <= HyperparamSpace.SAC_BOUNDS["gamma"][1]
        assert result["weight_updates"]["w_vr"] >= 0.0
