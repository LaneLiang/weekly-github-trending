"""Tests for evaluation metrics and experiment protocol."""

import pytest
import numpy as np
from dc_auto_tune.utils.types_ import CircuitParams
from dc_auto_tune.eval.metrics import ConverterMetrics, compute_metrics


class TestConverterMetrics:
    @pytest.fixture
    def params(self) -> CircuitParams:
        return CircuitParams(vin=12.0, vout_ref=5.0, L=100e-6, C=100e-6,
                             R_load=5.0, f_sw=100e3)

    def test_steady_state_perfect(self, params: CircuitParams):
        """Perfect steady state: Vo=5.0V, no ripple."""
        vo = np.full(100, 5.0)
        iL = np.full(100, 1.0)
        m = compute_metrics(vo, iL, params)
        assert m.vo_error_pct < 0.01
        assert m.vo_ripple_pct < 0.01

    def test_voltage_deviation(self, params: CircuitParams):
        """Vo=5.5V should give 10% error."""
        vo = np.full(100, 5.5)
        iL = np.full(100, 1.0)
        m = compute_metrics(vo, iL, params)
        assert 9.5 < m.vo_error_pct < 10.5

    def test_ripple_detection(self, params: CircuitParams):
        """Sinusoidal ripple: peak-to-peak 0.2V on 5V = 4%."""
        t = np.linspace(0, 1, 1000)
        vo = 5.0 + 0.1 * np.sin(2 * np.pi * 10 * t)  # 100mV amplitude
        iL = np.full(1000, 1.0)
        m = compute_metrics(vo, iL, params)
        assert 3.5 < m.vo_ripple_pct < 4.5  # p2p: 0.2V/5V = 4%

    def test_efficiency_calculation(self, params: CircuitParams):
        """Efficiency = Pout/Pin."""
        vo = np.full(100, 5.0)
        iL = np.full(100, 1.0)
        m = compute_metrics(vo, iL, params)
        assert 0 < m.efficiency_pct <= 100

    def test_startup_time(self, params: CircuitParams):
        """Startup: Vo rises from 0 to within 90% of Vref."""
        vo = np.concatenate([
            np.linspace(0, 4.5, 50),  # ramp up
            np.full(50, 5.0),          # steady
        ])
        iL = np.full(100, 1.0)
        m = compute_metrics(vo, iL, params)
        assert m.startup_time_ms > 0

    def test_overshoot_detection(self, params: CircuitParams):
        """Startup with overshoot."""
        vo = np.array([0.0, 2.0, 4.0, 5.5, 5.3, 5.1, 5.0, 5.0, 5.0, 5.0])
        iL = np.full(10, 1.0)
        m = compute_metrics(vo, iL, params)
        assert m.overshoot_pct > 5.0  # 0.5V/5V = 10%

    def test_undershoot_detection(self, params: CircuitParams):
        """Load transient with undershoot, measured from load step index."""
        vo = np.array([5.0, 5.0, 5.0, 4.5, 4.3, 4.6, 4.9, 5.0, 5.0, 5.0])
        iL = np.full(10, 1.0)
        m = compute_metrics(vo, iL, params, load_step_idx=2)
        assert m.undershoot_pct > 5.0  # (5.0-4.3)/5.0*100 = 14%

    def test_recovery_time(self, params: CircuitParams):
        """After settling, a load disturbance at load_step_idx causes a dip that recovers."""
        vo = np.array([0.0]*5 + [3.0, 4.0, 4.8, 5.0, 5.0]*2  # startup
                      + [5.0]*20  # steady
                      + [4.3, 4.4, 4.6, 4.8, 4.9, 5.0]  # disturbance + recovery
                      + [5.0]*10)
        iL = np.full(len(vo), 1.0)
        # Pass load_step_idx at the start of the dip
        m = compute_metrics(vo, iL, params, load_step_idx=35)
        assert m.recovery_time_ms > 0
