"""Domain randomization for device aging and operating-condition variation."""

import copy
import numpy as np
from dc_auto_tune.utils.types_ import CircuitParams, PerturbationConfig


class DomainRandomizer:
    """Randomly samples circuit parameters at episode start to simulate aging,
    manufacturing variation, and operating-condition drift.

    Perturbation ranges (relative to nominal):
        - ESR: [1.0x, max_esr_ratio]     (aging increases ESR)
        - L:   [min_L_ratio, 1.0x]        (core loss degrades inductance)
        - C:   [min_C_ratio, 1.0x]        (electrolyte dry-out)
        - Vin: nominal * [1 - vin_ripple, 1 + vin_ripple]
        - R_load: nominal * [1 - load_spread, 1 + load_spread]
    """

    def __init__(
        self,
        config: PerturbationConfig | None = None,
        seed: int | None = None,
    ):
        self.config = config or PerturbationConfig()
        self._rng = np.random.RandomState(seed)

    def sample(self, base: CircuitParams) -> CircuitParams:
        """Return a perturbed copy of *base* with randomised component values."""
        p = copy.deepcopy(base)
        cfg = self.config

        p.esr_c = base.esr_c * self._rng.uniform(1.0, cfg.max_esr_ratio)
        p.L = base.L * self._rng.uniform(cfg.min_L_ratio, 1.0)
        p.C = base.C * self._rng.uniform(cfg.min_C_ratio, 1.0)
        p.vin = base.vin * self._rng.uniform(1 - cfg.vin_ripple, 1 + cfg.vin_ripple)
        p.R_load = base.R_load * self._rng.uniform(
            1 - cfg.load_spread, 1 + cfg.load_spread
        )

        return p
