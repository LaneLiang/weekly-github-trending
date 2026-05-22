"""Tests for SACAgent (RED phase — these tests MUST fail)."""

import torch
import pytest
from dc_auto_tune.rl.sac_agent import SACAgent
from dc_auto_tune.utils.types_ import SACParams


class TestSACAgent:
    @pytest.fixture
    def agent(self):
        return SACAgent(obs_dim=7, action_dim=1, params=SACParams())

    def test_select_action_returns_valid_range(self, agent):
        obs = torch.randn(7)
        action = agent.select_action(obs, evaluate=False)
        assert 0.0 <= action <= 1.0

    def test_select_action_deterministic_in_eval_mode(self, agent):
        obs = torch.randn(7)
        a1 = agent.select_action(obs, evaluate=True)
        a2 = agent.select_action(obs, evaluate=True)
        assert a1 == pytest.approx(a2)

    def test_update_does_not_crash(self, agent):
        batch = (
            torch.randn(32, 7), torch.rand(32, 1),
            torch.randn(32, 1), torch.randn(32, 7),
            torch.zeros(32, 1)
        )
        info = agent.update(batch)
        assert "critic_loss" in info
        assert "actor_loss" in info
        assert "alpha_loss" in info
