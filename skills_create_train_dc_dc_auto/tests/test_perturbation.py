"""Tests for domain randomization perturbation injector."""

import pytest
from dc_auto_tune.utils.types_ import CircuitParams, PerturbationConfig
from dc_auto_tune.env.perturbation import DomainRandomizer


class TestDomainRandomizer:
    @pytest.fixture
    def base_params(self) -> CircuitParams:
        return CircuitParams(
            vin=12.0, vout_ref=5.0, L=100e-6, C=100e-6,
            R_load=5.0, f_sw=100e3, esr_c=0.01, rds_on=0.05,
        )

    def test_sample_returns_same_type(self, base_params: CircuitParams):
        rand = DomainRandomizer()
        result = rand.sample(base_params)
        assert isinstance(result, CircuitParams)

    def test_sample_within_bounds(self, base_params: CircuitParams):
        rand = DomainRandomizer(seed=42)
        for _ in range(100):
            p = rand.sample(base_params)
            assert 1.0 * base_params.esr_c <= p.esr_c <= 2.5 * base_params.esr_c
            assert 0.8 * base_params.L <= p.L <= 1.0 * base_params.L
            assert 0.7 * base_params.C <= p.C <= 1.0 * base_params.C
            assert 0.9 * base_params.vin <= p.vin <= 1.1 * base_params.vin
            assert 0.5 * base_params.R_load <= p.R_load <= 1.5 * base_params.R_load

    def test_deterministic_with_seed(self, base_params: CircuitParams):
        r1 = DomainRandomizer(seed=42)
        r2 = DomainRandomizer(seed=42)
        for _ in range(10):
            p1 = r1.sample(base_params)
            p2 = r2.sample(base_params)
            assert p1.L == p2.L
            assert p1.C == p2.C
            assert p1.vin == p2.vin

    def test_variation_is_applied(self, base_params: CircuitParams):
        rand = DomainRandomizer(seed=123)
        any_different = False
        for _ in range(20):
            p = rand.sample(base_params)
            if abs(p.L - base_params.L) > 1e-9:
                any_different = True
                break
        assert any_different, "Randomizer should produce varied parameters"

    def test_base_is_not_mutated(self, base_params: CircuitParams):
        rand = DomainRandomizer(seed=0)
        orig_L = base_params.L
        orig_C = base_params.C
        rand.sample(base_params)
        assert base_params.L == orig_L
        assert base_params.C == orig_C
