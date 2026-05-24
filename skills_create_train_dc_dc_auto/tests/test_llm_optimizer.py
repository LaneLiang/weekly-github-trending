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
    def test_suggestions_within_bounds(self, mock_llm, optimizer):
        """Suggested hyperparameters must stay within valid range even for out-of-bounds LLM output."""
        # Use vo_error < 0.5 (P0 PASS) so SAC freeze gate does not clear sac_updates
        state = {
            "episode": 200,
            "recent_rewards": [0.7, 0.75, 0.72, 0.78, 0.8],
            "metrics": {
                "vo_error_pct": 0.3,
                "vo_ripple_pct": 1.2,
                "efficiency_pct": 90.0,
                "overshoot_pct": 3.5,
                "undershoot_pct": 2.1,
                "recovery_time_ms": 0.45,
                "startup_time_ms": 8.0,
            },
            "current_sac": SACParams(),
            "current_weights": RewardWeights(),
        }
        mock_llm.return_value.chat.return_value = (
            '{"analysis": "test", '
            '"sac_updates": {"actor_lr": 999.0, "gamma": 5.0}, '
            '"weight_updates": {"w_vr": -10.0}}'
        )
        result = optimizer.analyze_and_suggest(state)
        assert result["sac_updates"]["actor_lr"] <= HyperparamSpace.SAC_BOUNDS["actor_lr"][1]
        assert result["sac_updates"]["gamma"] <= HyperparamSpace.SAC_BOUNDS["gamma"][1]
        assert result["weight_updates"]["w_vr"] >= 0.0

    # ---- P0 gate tests (Reviewer Fix 4) ----

    @patch("dc_auto_tune.meta.llm_client.LLMClient")
    def test_vo_error_fail_prevents_w_ev_decrease(self, mock_llm, optimizer):
        """When vo_error P0 FAIL (>=0.5%), LLM-suggested w_ev decrease is blocked."""
        current_weights = RewardWeights(w_ev=1.0)
        state = {
            "episode": 200,
            "recent_rewards": [0.5, 0.6, 0.55, 0.7, 0.65],
            "metrics": {
                "vo_error_pct": 0.8,
                "vo_ripple_pct": 1.2,
                "efficiency_pct": 85.0,
                "overshoot_pct": 3.5,
                "undershoot_pct": 2.1,
                "recovery_time_ms": 0.45,
                "startup_time_ms": 8.0,
            },
            "current_sac": SACParams(),
            "current_weights": current_weights,
        }
        # LLM tries to decrease w_ev from 1.0 to 0.5 (reward hacking)
        mock_llm.return_value.chat.return_value = (
            '{"analysis": "decrease w_ev to boost other metrics", '
            '"weight_updates": {"w_ev": 0.5, "w_vr": 2.0}}'
        )
        result = optimizer.analyze_and_suggest(state)
        # P0 gate forces w_ev to min(old * 1.2, bound_max) = min(1.2, 5.0) = 1.2
        assert "weight_updates" in result
        assert result["weight_updates"]["w_ev"] >= 1.0  # must increase, not just stay flat

    @patch("dc_auto_tune.meta.llm_client.LLMClient")
    def test_vo_error_pass_allows_w_ev_adjustment(self, mock_llm, optimizer):
        """When vo_error P0 PASS (<0.5%), w_ev can be freely adjusted (up or down)."""
        current_weights = RewardWeights(w_ev=1.0)
        state = {
            "episode": 200,
            "recent_rewards": [0.7, 0.75, 0.72, 0.78, 0.8],
            "metrics": {
                "vo_error_pct": 0.3,
                "vo_ripple_pct": 1.2,
                "efficiency_pct": 90.0,
                "overshoot_pct": 3.5,
                "undershoot_pct": 2.1,
                "recovery_time_ms": 0.45,
                "startup_time_ms": 8.0,
            },
            "current_sac": SACParams(),
            "current_weights": current_weights,
        }
        # LLM suggests decreasing w_ev — allowed since P0 is PASS
        mock_llm.return_value.chat.return_value = (
            '{"analysis": "vo_error is good, shift focus", '
            '"weight_updates": {"w_ev": 0.6, "w_vr": 3.0}}'
        )
        result = optimizer.analyze_and_suggest(state)
        # vo_error PASS: the suggested decrease should be respected
        assert "weight_updates" in result
        assert result["weight_updates"]["w_ev"] < 1.0

    def test_vo_error_missing_triggers_critical_warning(self, optimizer):
        """When vo_error_pct is missing from metrics, critical_warning fires
        (assume worst case)."""
        state = {
            "episode": 100,
            "recent_rewards": [0.5, 0.55],
            "metrics": {
                "vo_ripple_pct": 1.2,
                # vo_error_pct intentionally absent
            },
            "current_sac": SACParams(),
            "current_weights": RewardWeights(),
        }
        prompt = optimizer._build_prompt(state)
        assert "CRITICAL" in prompt
        assert "NOT AVAILABLE" in prompt
        assert "P0 FAIL" in prompt

    @patch("dc_auto_tune.meta.llm_client.LLMClient")
    def test_vo_error_none_prevents_w_ev_decrease(self, mock_llm, optimizer):
        """Code-level gate: when vo_error_pct is None (missing data),
        treat as worst case and force w_ev increase."""
        current_weights = RewardWeights(w_ev=1.0)
        state = {
            "episode": 50,
            "recent_rewards": [0.3, 0.35, 0.4],
            "metrics": {
                "vo_ripple_pct": 2.0,
                "efficiency_pct": 90.0,
                # vo_error_pct intentionally absent
            },
            "current_sac": SACParams(),
            "current_weights": current_weights,
        }
        mock_llm.return_value.chat.return_value = (
            '{"analysis": "try to reduce w_ev", '
            '"weight_updates": {"w_ev": 0.3, "w_vr": 2.0}}'
        )
        result = optimizer.analyze_and_suggest(state)
        assert "weight_updates" in result
        assert result["weight_updates"]["w_ev"] >= 1.0  # forced increase

    @patch("dc_auto_tune.meta.llm_client.LLMClient")
    def test_vo_error_fail_freezes_other_weights(self, mock_llm, optimizer):
        """When vo_error P0 FAIL, non-w_ev weights cannot increase (freeze gate)."""
        current_weights = RewardWeights(w_ev=1.0, w_vr=1.0, w_eff=0.5,
                                        w_os=0.8, w_us=0.8, w_tr=0.8, w_ts=0.5)
        state = {
            "episode": 200,
            "recent_rewards": [0.5, 0.6, 0.55, 0.7, 0.65],
            "metrics": {
                "vo_error_pct": 0.8,
                "vo_ripple_pct": 1.2,
                "efficiency_pct": 85.0,
                "overshoot_pct": 3.5,
                "undershoot_pct": 2.1,
                "recovery_time_ms": 0.45,
                "startup_time_ms": 8.0,
            },
            "current_sac": SACParams(),
            "current_weights": current_weights,
        }
        # LLM tries to massively increase w_vr (reward hacking via dilution)
        mock_llm.return_value.chat.return_value = (
            '{"analysis": "boost vr to inflate reward", '
            '"weight_updates": {"w_ev": 1.5, "w_vr": 5.0, "w_eff": 0.5, '
            '"w_os": 0.8, "w_us": 0.8, "w_tr": 0.8, "w_ts": 0.5}}'
        )
        result = optimizer.analyze_and_suggest(state)
        assert "weight_updates" in result
        # w_ev may increase (forced by existing P0 gate)
        assert result["weight_updates"]["w_ev"] >= 1.0
        # w_vr should be clamped to current value (1.0), NOT increased to 5.0
        assert result["weight_updates"]["w_vr"] == 1.0

    @patch("dc_auto_tune.meta.llm_client.LLMClient")
    def test_vo_error_pass_allows_other_weight_increase(self, mock_llm, optimizer):
        """When vo_error P0 PASS, non-w_ev weights can increase freely."""
        current_weights = RewardWeights(w_ev=1.0, w_vr=1.0, w_eff=0.5,
                                        w_os=0.8, w_us=0.8, w_tr=0.8, w_ts=0.5)
        state = {
            "episode": 200,
            "recent_rewards": [0.7, 0.75, 0.72, 0.78, 0.8],
            "metrics": {
                "vo_error_pct": 0.3,
                "vo_ripple_pct": 1.2,
                "efficiency_pct": 90.0,
                "overshoot_pct": 3.5,
                "undershoot_pct": 2.1,
                "recovery_time_ms": 0.45,
                "startup_time_ms": 8.0,
            },
            "current_sac": SACParams(),
            "current_weights": current_weights,
        }
        # LLM increases w_vr — allowed since vo_error P0 PASS
        mock_llm.return_value.chat.return_value = (
            '{"analysis": "vo_error is good, boost vr", '
            '"weight_updates": {"w_vr": 5.0}}'
        )
        result = optimizer.analyze_and_suggest(state)
        assert "weight_updates" in result
        # w_vr should be allowed to increase to 5.0
        assert result["weight_updates"]["w_vr"] == 5.0

    @patch("dc_auto_tune.meta.llm_client.LLMClient")
    def test_vo_error_fail_allows_other_weight_decrease(self, mock_llm, optimizer):
        """When vo_error P0 FAIL, non-w_ev weights CAN still decrease (only increases blocked)."""
        current_weights = RewardWeights(w_ev=1.0, w_vr=1.0, w_eff=0.5,
                                        w_os=0.8, w_us=0.8, w_tr=0.8, w_ts=0.5)
        state = {
            "episode": 200,
            "recent_rewards": [0.5, 0.6, 0.55, 0.7, 0.65],
            "metrics": {
                "vo_error_pct": 0.8,
                "vo_ripple_pct": 1.2,
                "efficiency_pct": 85.0,
                "overshoot_pct": 3.5,
                "undershoot_pct": 2.1,
                "recovery_time_ms": 0.45,
                "startup_time_ms": 8.0,
            },
            "current_sac": SACParams(),
            "current_weights": current_weights,
        }
        # LLM tries to decrease w_tr — allowed even during P0 FAIL
        mock_llm.return_value.chat.return_value = (
            '{"analysis": "reduce transient weight", '
            '"weight_updates": {"w_ev": 1.5, "w_tr": 0.3}}'
        )
        result = optimizer.analyze_and_suggest(state)
        assert "weight_updates" in result
        assert result["weight_updates"]["w_tr"] == 0.3  # decrease allowed

    @patch("dc_auto_tune.meta.llm_client.LLMClient")
    def test_vo_error_at_exact_boundary_freezes_weights(self, mock_llm, optimizer):
        """vo_error == 0.5 (exact P0 boundary) triggers freeze gate."""
        current_weights = RewardWeights(w_ev=1.0, w_vr=1.0, w_eff=0.5,
                                        w_os=0.8, w_us=0.8, w_tr=0.8, w_ts=0.5)
        state = {
            "episode": 200,
            "recent_rewards": [0.5, 0.6, 0.55, 0.7, 0.65],
            "metrics": {
                "vo_error_pct": 0.5,  # exact boundary
                "vo_ripple_pct": 1.2,
                "efficiency_pct": 85.0,
                "overshoot_pct": 3.5,
                "undershoot_pct": 2.1,
                "recovery_time_ms": 0.45,
                "startup_time_ms": 8.0,
            },
            "current_sac": SACParams(),
            "current_weights": current_weights,
        }
        mock_llm.return_value.chat.return_value = (
            '{"analysis": "test boundary", '
            '"weight_updates": {"w_ev": 0.8, "w_vr": 3.0}}'
        )
        result = optimizer.analyze_and_suggest(state)
        assert "weight_updates" in result
        # w_ev: LLM tried 0.8 (< old * 0.95 = 0.95), gate forces increase
        assert result["weight_updates"]["w_ev"] >= 1.0
        # w_vr: freeze gate clamps to current (1.0)
        assert result["weight_updates"]["w_vr"] == 1.0

    # ---- SAC freeze gate tests (Reviewer Fix 5) ----

    @patch("dc_auto_tune.meta.llm_client.LLMClient")
    def test_vo_error_fail_freezes_sac_params(self, mock_llm, optimizer):
        """When vo_error P0 FAIL (0.8%), LLM-suggested sac_updates are cleared
        to prevent destabilizing learning dynamics before primary objective is met."""
        current_weights = RewardWeights(w_ev=1.0)
        state = {
            "episode": 200,
            "recent_rewards": [0.5, 0.6, 0.55, 0.7, 0.65],
            "metrics": {
                "vo_error_pct": 0.8,
                "vo_ripple_pct": 1.2,
                "efficiency_pct": 85.0,
                "overshoot_pct": 3.5,
                "undershoot_pct": 2.1,
                "recovery_time_ms": 0.45,
                "startup_time_ms": 8.0,
            },
            "current_sac": SACParams(),
            "current_weights": current_weights,
        }
        # LLM tries to change SAC hyperparameters (actor_lr, initial_alpha)
        mock_llm.return_value.chat.return_value = (
            '{"analysis": "adjust SAC params to improve exploration", '
            '"sac_updates": {"actor_lr": 0.0005, "initial_alpha": 0.1}}'
        )
        result = optimizer.analyze_and_suggest(state)
        # SAC freeze gate clears sac_updates when vo_error P0 FAIL
        assert result["sac_updates"] == {}

    @patch("dc_auto_tune.meta.llm_client.LLMClient")
    def test_vo_error_pass_allows_sac_updates(self, mock_llm, optimizer):
        """When vo_error P0 PASS (0.3%), LLM-suggested sac_updates are allowed through."""
        current_weights = RewardWeights(w_ev=1.0)
        state = {
            "episode": 200,
            "recent_rewards": [0.7, 0.75, 0.72, 0.78, 0.8],
            "metrics": {
                "vo_error_pct": 0.3,
                "vo_ripple_pct": 1.2,
                "efficiency_pct": 90.0,
                "overshoot_pct": 3.5,
                "undershoot_pct": 2.1,
                "recovery_time_ms": 0.45,
                "startup_time_ms": 8.0,
            },
            "current_sac": SACParams(),
            "current_weights": current_weights,
        }
        # LLM suggests SAC hyperparameter changes — allowed since vo_error P0 PASS
        mock_llm.return_value.chat.return_value = (
            '{"analysis": "tune SAC params now that vo_error is good", '
            '"sac_updates": {"actor_lr": 0.0005, "initial_alpha": 0.1}}'
        )
        result = optimizer.analyze_and_suggest(state)
        # SAC updates preserved when vo_error P0 PASS
        # (magnitude limiter clamps actor_lr: 0.0003 -> 0.0005 becomes 0.00045)
        assert "sac_updates" in result
        assert result["sac_updates"]["actor_lr"] == pytest.approx(0.00045)
        assert result["sac_updates"]["initial_alpha"] == 0.1
