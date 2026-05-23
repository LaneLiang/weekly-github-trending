"""Tests for MultiObjectiveReward — sliding-window online reward computation."""

import pytest
from dc_auto_tune.env.rewards import MultiObjectiveReward
from dc_auto_tune.utils.types_ import RewardWeights


class TestMultiObjectiveReward:
    @pytest.fixture
    def rfn(self):
        return MultiObjectiveReward(vout_ref=5.0)

    @pytest.fixture
    def steady_info(self):
        return {"vo": 5.0, "t": 0.001, "iL": 1.0, "p_in": 12.0, "p_out": 5.0}

    def test_reset_clears_buffers(self, rfn, steady_info):
        rfn.compute(steady_info)
        assert len(rfn._vo_buf) == 1
        rfn.reset()
        assert len(rfn._vo_buf) == 0
        assert rfn._first_t is None

    def test_compute_returns_float(self, rfn, steady_info):
        r = rfn.compute(steady_info)
        assert isinstance(r, float)

    def test_voltage_error_perfect_tracking(self, rfn):
        """r_ev should be near 1.0 when Vo == Vref."""
        for _ in range(20):
            rfn.compute({"vo": 5.0, "t": 0.001, "iL": 1.0, "p_in": 12.0, "p_out": 5.0})
        r = rfn.compute({"vo": 5.0, "t": 0.001, "iL": 1.0, "p_in": 12.0, "p_out": 5.0})
        # r_ev should dominate and be close to 1.0 (with default weights)
        assert r > 0.0

    def test_voltage_error_penalizes_deviation(self, rfn):
        """Deviation from Vref should reduce reward."""
        for _ in range(20):
            rfn.compute({"vo": 5.0, "t": 0.001, "iL": 1.0, "p_in": 12.0, "p_out": 5.0})
        r_good = rfn.compute({"vo": 5.0, "t": 0.001, "iL": 1.0, "p_in": 12.0, "p_out": 5.0})

        rfn.reset()
        for _ in range(20):
            rfn.compute({"vo": 4.5, "t": 0.001, "iL": 1.0, "p_in": 10.0, "p_out": 4.0})
        r_bad = rfn.compute({"vo": 4.5, "t": 0.001, "iL": 1.0, "p_in": 10.0, "p_out": 4.0})

        assert r_good > r_bad, f"r_good={r_good}, r_bad={r_bad}"

    def test_ripple_penalty_increases_with_variation(self, rfn):
        """Higher Vo variation should produce more negative ripple penalty."""
        # Low ripple
        rfn.reset()
        for i in range(30):
            vo = 5.0 + 0.01 * (i % 3 - 1)  # tiny variation
            rfn.compute({"vo": vo, "t": 0.001 * i, "iL": 1.0, "p_in": 12.0, "p_out": 5.0})
        metrics_low = rfn.get_current_metrics()

        # High ripple
        rfn.reset()
        for i in range(30):
            vo = 5.0 + 0.2 * (i % 3 - 1)  # large variation
            rfn.compute({"vo": vo, "t": 0.001 * i, "iL": 1.0, "p_in": 12.0, "p_out": 5.0})
        metrics_high = rfn.get_current_metrics()

        assert metrics_high["vo_ripple_pct"] > metrics_low["vo_ripple_pct"]

    def test_efficiency_below_50_percent_negative(self, rfn):
        """Efficiency term should be negative when P_out < 0.5 * P_in."""
        rfn.reset()
        for _ in range(20):
            rfn.compute({"vo": 5.0, "t": 0.001, "iL": 1.0, "p_in": 12.0, "p_out": 3.0})
        metrics = rfn.get_current_metrics()
        # eff = 3/12 = 25%, mapped via 2*(eff - 0.5) = -0.5 → negative
        assert metrics["efficiency_pct"] < 50

    def test_startup_detection(self, rfn):
        """After sustained Vo >= 0.9 * Vref for 10+ steps, startup should be done."""
        rfn.reset()
        # Below threshold
        for i in range(5):
            rfn.compute({"vo": 2.0, "t": i * 1e-6, "iL": 0.5, "p_in": 5.0, "p_out": 1.0})
        assert not rfn._startup_done
        # Above 0.9 * Vref sustained for 10 steps
        for i in range(15):
            rfn.compute({"vo": 4.8, "t": (5 + i) * 1e-6, "iL": 1.0, "p_in": 12.0, "p_out": 5.0})
        assert rfn._startup_done

    def test_overshoot_penalty(self, rfn):
        """Vo > 1.05 * Vref should produce negative overshoot penalty."""
        rfn.reset()
        for _ in range(10):
            rfn.compute({"vo": 5.0, "t": 0.001, "iL": 1.0, "p_in": 12.0, "p_out": 5.0})
        r_normal = rfn.compute({"vo": 5.0, "t": 0.001, "iL": 1.0, "p_in": 12.0, "p_out": 5.0})

        rfn.reset()
        for _ in range(10):
            rfn.compute({"vo": 5.0, "t": 0.001, "iL": 1.0, "p_in": 12.0, "p_out": 5.0})
        r_overshoot = rfn.compute({"vo": 5.5, "t": 0.001, "iL": 1.0, "p_in": 13.0, "p_out": 6.0})

        assert r_overshoot < r_normal, f"r_overshoot={r_overshoot}, r_normal={r_normal}"

    def test_update_weights_changes_reward(self, rfn):
        """Changing weights should alter reward for the same state."""
        for _ in range(20):
            rfn.compute({"vo": 5.0, "t": 0.001, "iL": 1.0, "p_in": 12.0, "p_out": 5.0})
        r1 = rfn.compute({"vo": 5.0, "t": 0.001, "iL": 1.0, "p_in": 12.0, "p_out": 5.0})

        new_weights = RewardWeights(w_ev=5.0, w_vr=0.0, w_eff=0.0, w_os=0.0, w_us=0.0, w_tr=0.0, w_ts=0.0)
        rfn.update_weights(new_weights)
        r2 = rfn.compute({"vo": 5.0, "t": 0.001, "iL": 1.0, "p_in": 12.0, "p_out": 5.0})

        assert r1 != r2

    def test_get_current_metrics_returns_all_keys(self, rfn):
        """get_current_metrics should return all 7 expected metric keys."""
        for i in range(20):
            rfn.compute({"vo": 5.0, "t": i * 1e-6, "iL": 1.0, "p_in": 12.0, "p_out": 5.0})
        m = rfn.get_current_metrics()
        expected_keys = {"vo_error_pct", "vo_ripple_pct", "efficiency_pct",
                         "overshoot_pct", "undershoot_pct",
                         "startup_time_ms", "recovery_time_ms"}
        assert set(m.keys()) == expected_keys

    def test_window_too_small_returns_zeros(self, rfn):
        """Metrics should be 0 when buffer has fewer than 10 samples."""
        m = rfn.get_current_metrics()
        assert m["vo_error_pct"] == 0
        assert m["vo_ripple_pct"] == 0
        assert m["efficiency_pct"] == 0

    def test_transient_detection(self, rfn):
        """Transient state should be entered when Vo deviates from ±2% band."""
        rfn.reset()
        # Steady state first
        for i in range(30):
            rfn.compute({"vo": 5.0, "t": i * 1e-6, "iL": 1.0, "p_in": 12.0, "p_out": 5.0})
        assert not rfn._in_transient
        # Large deviation triggers transient
        rfn.compute({"vo": 4.5, "t": 30e-6, "iL": 0.8, "p_in": 10.0, "p_out": 4.0})
        assert rfn._in_transient
        # Recovery: sustained in-band for 20 steps
        for i in range(25):
            rfn.compute({"vo": 5.0, "t": (31 + i) * 1e-6, "iL": 1.0, "p_in": 12.0, "p_out": 5.0})
        assert not rfn._in_transient
