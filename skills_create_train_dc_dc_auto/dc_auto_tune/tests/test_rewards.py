"""Unit tests for MultiObjectiveReward — RED phase.

These tests MUST fail because MultiObjectiveReward is not implemented yet.
"""

import pytest

from dc_auto_tune.env.rewards import MultiObjectiveReward
from dc_auto_tune.utils.types_ import RewardWeights


class TestMultiObjectiveReward:
    """Test suite for the multi-objective reward function."""

    @pytest.fixture
    def reward(self):
        """Create a default MultiObjectiveReward with vout_ref=5.0."""
        return MultiObjectiveReward(vout_ref=5.0)

    def test_perfect_tracking_gives_high_reward(self, reward):
        """Perfect tracking (vo == vout_ref) should yield a positive reward."""
        info = {"vo": 5.0, "iL": 1.0, "d": 0.417, "t": 0.01}
        r = reward.compute(info)
        assert r > 0, f"Expected positive reward, got {r}"

    def test_large_error_gives_negative_reward(self, reward):
        """Large voltage deviation should yield a negative reward."""
        info = {"vo": 2.0, "iL": 0.5, "d": 0.2, "t": 0.01}
        r = reward.compute(info)
        assert r < 0, f"Expected negative reward, got {r}"

    def test_ripple_increases_with_low_capacitance(self, reward):
        """Higher voltage ripple should yield lower reward."""
        history = [
            {"vo": 5.0, "iL": 1.0, "d": 0.417, "t": 0.0},
            {"vo": 5.05, "iL": 1.1, "d": 0.417, "t": 0.01},
        ]
        r1 = reward.compute(history[0], history[-1])
        history2 = [
            {"vo": 5.0, "iL": 1.0, "d": 0.417, "t": 0.0},
            {"vo": 5.15, "iL": 1.2, "d": 0.417, "t": 0.01},
        ]
        r2 = reward.compute(history2[0], history2[-1])
        assert r1 > r2, f"Higher ripple should yield lower reward: {r1} vs {r2}"

    def test_weight_update_changes_reward(self, reward):
        """Updating reward weights should change the computed reward value."""
        info = {"vo": 4.9, "iL": 1.0, "d": 0.417, "t": 0.01}
        r1 = reward.compute(info)
        reward.update_weights(RewardWeights(w_ev=10.0, w_vr=0.1))
        r2 = reward.compute(info)
        assert r1 != r2, f"Weight update should change reward: {r1} vs {r2}"
