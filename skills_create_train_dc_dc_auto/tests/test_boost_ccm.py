"""Tests for Boost converter CCM environment."""

import pytest
from dc_auto_tune.utils.types_ import CircuitParams
from dc_auto_tune.env.boost_ccm import BoostCCMEnv


class TestBoostCCMEnv:
    """Verify Boost converter CCM ODE simulation."""

    @pytest.fixture
    def boost_env(self) -> BoostCCMEnv:
        params = CircuitParams(
            vin=12.0,
            vout_ref=24.0,
            L=200e-6,
            C=100e-6,
            R_load=24.0,
            f_sw=100e3,
        )
        return BoostCCMEnv(params)

    def test_steady_state_converges(self, boost_env: BoostCCMEnv):
        """Boost CCM: Vo = Vin/(1-d), d=0.5 -> Vo ~= 24V at Vin=12V."""
        env = boost_env
        env.reset()
        for _ in range(3000):
            obs, _, _, _, _ = env.step(0.5)
        vo = obs[0].item()
        assert 21 < vo < 27, f"Expected Vo near 24V, got {vo:.2f}V"

    def test_vo_below_vin_is_not_boost(self, boost_env: BoostCCMEnv):
        """If d is too low, Boost output may be near Vin in startup transient."""
        env = boost_env
        env.reset()
        # Very low d means almost no boosting, but steady state still > Vin
        for _ in range(3000):
            obs, _, _, _, _ = env.step(0.3)
        vo = obs[0].item()
        # d=0.3 -> Vo_ideal = 12/(1-0.3) = 17.1V
        assert 15 < vo < 20, f"Expected Vo near 17V (d=0.3), got {vo:.2f}V"

    def test_observation_shape(self, boost_env: BoostCCMEnv):
        """Boost observation should be 8-dim (including mode_flag)."""
        env = boost_env
        obs = env.reset()
        assert obs.shape[0] == 8

    def test_reset_clears_state(self, boost_env: BoostCCMEnv):
        """After running and resetting, state should be at zero."""
        env = boost_env
        env.reset()
        for _ in range(500):
            obs, _, _, _, _ = env.step(0.5)
        assert env.vo > 0.1
        env.reset()
        assert env.vo == 0.0
        assert env.iL == 0.0

    def test_action_clamped(self, boost_env: BoostCCMEnv):
        """Actions outside [0,1] should be clamped."""
        env = boost_env
        env.reset()
        # Should not crash with out-of-range actions
        obs, _, _, _, info = env.step(-0.2)
        assert 0 <= info["d"] <= 1
        obs, _, _, _, info = env.step(1.5)
        assert 0 <= info["d"] <= 1
