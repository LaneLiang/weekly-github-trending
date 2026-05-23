"""Hyperparameter search space with bounds for SAC parameters and reward weights."""

from dc_auto_tune.utils.types_ import SACParams, RewardWeights


class HyperparamSpace:
    """Defines valid ranges for SAC hyperparameters and reward weights.

    Provides validation/clamping helpers and a prompt-context generator
    consumed by the LLM meta-optimizer.
    """

    SAC_BOUNDS: dict[str, tuple[float, float] | tuple[int, int]] = {
        "actor_lr": (1e-5, 1e-2),
        "critic_lr": (1e-5, 1e-2),
        "alpha_lr": (1e-5, 1e-2),
        "gamma": (0.8, 0.999),
        "tau": (0.001, 0.05),
        "batch_size": (64, 512),
        "buffer_size": (10000, 1000000),
        "initial_alpha": (0.01, 1.0),
    }

    SAC_INT_PARAMS: set[str] = {"batch_size", "buffer_size"}

    WEIGHT_BOUNDS: dict[str, tuple[float, float]] = {
        "w_ev": (0.0, 5.0),
        "w_vr": (0.0, 5.0),
        "w_eff": (0.0, 5.0),
        "w_os": (0.0, 5.0),
        "w_us": (0.0, 5.0),
        "w_tr": (0.0, 5.0),
        "w_ts": (0.0, 5.0),
    }

    @classmethod
    def validate_and_clamp_sac(cls, updates: dict) -> dict:
        """Clamp each SAC parameter to its allowed range.

        Args:
            updates: Dict mapping SAC parameter names to proposed values.

        Returns:
            Dict with every value clamped to [lo, hi] for its key.
            Integer-typed parameters are rounded to int.
        """
        clamped: dict = {}
        for k, v in updates.items():
            if k in cls.SAC_BOUNDS:
                lo, hi = cls.SAC_BOUNDS[k]
                v = max(lo, min(hi, v))
                if k in cls.SAC_INT_PARAMS:
                    v = int(round(v))
                clamped[k] = v
        return clamped

    @classmethod
    def validate_and_clamp_weights(cls, updates: dict) -> dict:
        """Clamp each reward weight to its allowed range.

        Args:
            updates: Dict mapping weight names to proposed values.

        Returns:
            Dict with every value clamped to [lo, hi] for its key.
        """
        clamped: dict = {}
        for k, v in updates.items():
            if k in cls.WEIGHT_BOUNDS:
                lo, hi = cls.WEIGHT_BOUNDS[k]
                clamped[k] = max(lo, min(hi, v))
        return clamped

    @classmethod
    def generate_prompt_context(cls) -> str:
        """Build a human-readable summary of all search-space bounds for the LLM prompt."""
        sac_desc = "\n".join(
            f"  {k}: [{lo}, {hi}]" for k, (lo, hi) in cls.SAC_BOUNDS.items()
        )
        weight_desc = "\n".join(
            f"  {k}: [{lo}, {hi}]" for k, (lo, hi) in cls.WEIGHT_BOUNDS.items()
        )
        return f"""SAC Hyperparameters (with valid ranges):
{sac_desc}

Reward Weights (with valid ranges):
{weight_desc}"""
