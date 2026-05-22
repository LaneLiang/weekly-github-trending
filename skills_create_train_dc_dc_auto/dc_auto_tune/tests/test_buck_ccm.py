"""Unit tests for BuckCCMEnv — RED phase.

These tests MUST fail because BuckCCMEnv is not implemented yet.
"""

import pytest
import torch

from dc_auto_tune.env.buck_ccm import BuckCCMEnv


class TestBuckCCMEnv:
    """Test suite for the Buck CCM gymnasium environment."""

    def test_reset_returns_valid_state(self, default_circuit):
        """reset() should return a (7,) float tensor with plausible initial values."""
        env = BuckCCMEnv(default_circuit)
        obs = env.reset()
        assert obs.shape == (7,)
        assert obs[0].item() == pytest.approx(0.0, abs=0.5)
        assert obs[1].item() == pytest.approx(0.0, abs=0.1)

    def test_steady_state_converges(self, default_circuit):
        """CCM Buck: d=0.416 should give Vo ~ 5 V at Vin = 12 V."""
        env = BuckCCMEnv(default_circuit)
        env.reset()
        d = default_circuit.vout_ref / default_circuit.vin
        for _ in range(2000):
            obs, _, term, trunc, _ = env.step(d)
        vo = obs[0].item()
        assert 4.8 < vo < 5.2, f"Expected Vo ~ 5 V, got {vo}"

    def test_action_clamped(self, default_circuit):
        """Actions outside [0, 1] should be safely clamped, not crash."""
        env = BuckCCMEnv(default_circuit)
        env.reset()
        # Out-of-range duties should be clamped, not raise
        obs, _, _, _, _ = env.step(1.5)
        obs2, _, _, _, _ = env.step(-0.5)

    def test_duty_zero_gives_decay(self, default_circuit):
        """d = 0 should discharge the output; voltage must remain non-negative."""
        env = BuckCCMEnv(default_circuit)
        env.reset()
        for _ in range(500):
            env.step(0.5)
        obs, _, _, _, _ = env.step(0.0)
        assert obs[0].item() >= 0
