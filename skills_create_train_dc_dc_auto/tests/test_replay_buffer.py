"""Tests for ReplayBuffer (RED phase — these tests MUST fail)."""

import torch
from dc_auto_tune.rl.replay_buffer import ReplayBuffer


class TestReplayBuffer:
    def test_push_and_sample(self):
        buf = ReplayBuffer(capacity=100, obs_dim=7, action_dim=1)
        obs = torch.randn(7)
        action = torch.tensor([0.5])
        reward = 0.1
        next_obs = torch.randn(7)
        done = False
        buf.push(obs, action, reward, next_obs, done)
        assert len(buf) == 1

    def test_sample_returns_correct_shapes(self):
        buf = ReplayBuffer(capacity=100, obs_dim=7, action_dim=1)
        for _ in range(50):
            buf.push(torch.randn(7), torch.tensor([0.3]), 0.0, torch.randn(7), False)
        obs, acts, rews, next_obs, dones = buf.sample(32)
        assert obs.shape == (32, 7)
        assert acts.shape == (32, 1)
        assert rews.shape == (32, 1)
        assert next_obs.shape == (32, 7)
        assert dones.shape == (32, 1)

    def test_cannot_sample_before_filled(self):
        buf = ReplayBuffer(capacity=100, obs_dim=7, action_dim=1)
        buf.push(torch.randn(7), torch.tensor([0.5]), 0.0, torch.randn(7), False)
        result = buf.sample(32)
        assert result is None
