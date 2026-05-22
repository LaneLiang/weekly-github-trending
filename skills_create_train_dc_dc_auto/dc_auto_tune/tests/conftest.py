"""Shared pytest fixtures for dc_auto_tune tests."""

import pytest
import torch
import numpy as np

from dc_auto_tune.utils.types_ import CircuitParams


@pytest.fixture
def default_circuit():
    """Return a default Buck converter CircuitParams for testing."""
    return CircuitParams(
        vin=12.0,
        vout_ref=5.0,
        L=100e-6,
        C=100e-6,
        R_load=5.0,
        f_sw=100e3,
        rds_on=0.05,
        esr_c=0.01,
    )


@pytest.fixture(autouse=True)
def seed():
    """Fix random seeds for reproducibility across all tests."""
    torch.manual_seed(42)
    np.random.seed(42)
