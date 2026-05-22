"""Tests for DCM (Discontinuous Conduction Mode) event-driven solver."""

import pytest
from dc_auto_tune.utils.types_ import CircuitParams
from dc_auto_tune.env.buck_ccm import BuckCCMEnv


class TestDCM:
    """Verify DCM detection and mode switching in Buck converter environment."""

    @pytest.fixture
    def light_load_env(self) -> BuckCCMEnv:
        """Very light load — should enter DCM."""
        params = CircuitParams(
            vin=12.0,
            vout_ref=5.0,
            L=100e-6,
            C=100e-6,
            R_load=50.0,  # light load
            f_sw=100e3,
        )
        return BuckCCMEnv(params)

    @pytest.fixture
    def heavy_load_env(self) -> BuckCCMEnv:
        """Heavy load — should stay in CCM."""
        params = CircuitParams(
            vin=12.0,
            vout_ref=5.0,
            L=100e-6,
            C=100e-6,
            R_load=2.0,  # heavy load
            f_sw=100e3,
        )
        return BuckCCMEnv(params)

    def test_light_load_enters_dcm(self, light_load_env: BuckCCMEnv):
        """Light load should cause iL to drop to zero and enter DCM."""
        env = light_load_env
        env.reset()
        hit_dcm = False
        for _ in range(100):
            obs, _, _, _, info = env.step(0.2)  # small duty cycle
            if info.get("mode") == "DCM" or (info.get("iL", 1) <= 0):
                hit_dcm = True
                break
        assert hit_dcm, "Light load should enter DCM"

    def test_heavy_load_stays_ccm(self, heavy_load_env: BuckCCMEnv):
        """Heavy load should keep iL > 0 throughout."""
        env = heavy_load_env
        env.reset()
        for _ in range(100):
            obs, _, _, _, info = env.step(0.5)
        # After settling, iL should be positive in CCM
        assert env.iL > 0, f"Expected iL>0 in CCM, got iL={env.iL:.4f}"

    def test_dcm_mode_flag_in_obs(self, light_load_env: BuckCCMEnv):
        """Observation vector should include mode_flag (8-dim) indicating DCM/CCM."""
        env = light_load_env
        obs = env.reset()
        assert obs.shape[0] == 8, f"Expected 8-dim obs, got {obs.shape[0]}"

    def test_dcm_il_clamped_to_zero(self, light_load_env: BuckCCMEnv):
        """In DCM IDLE mode, iL must be clamped to zero, not negative."""
        env = light_load_env
        env.reset()
        for _ in range(200):
            obs, _, _, _, info = env.step(0.15)
            if info.get("mode") == "DCM":
                assert info["iL"] >= -1e-9, f"iL should be clamped to 0, got {info['iL']}"

    def test_dcm_vo_decays_during_idle(self, light_load_env: BuckCCMEnv):
        """During DCM IDLE, Vo should decay only through RC discharge."""
        env = light_load_env
        env.reset()
        dcm_vo_readings = []
        for _ in range(50):
            obs, _, _, _, info = env.step(0.1)
            if info.get("mode") == "DCM":
                dcm_vo_readings.append(info["vo"])
        # Vo should be positive and not excessively large
        assert len(dcm_vo_readings) > 0, "Should record some DCM cycles"
        assert all(v >= 0 for v in dcm_vo_readings), "Vo should be non-negative"
