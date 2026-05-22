"""Configuration loading utilities."""

import yaml
from pathlib import Path
from dc_auto_tune.utils.types_ import (
    Config,
    CircuitParams,
    SACParams,
    RewardWeights,
    MetaOptConfig,
    TrainConfig,
)


def load_config(path: str | Path) -> Config:
    """Load configuration from a YAML file.

    Args:
        path: Path to the YAML configuration file.

    Returns:
        A Config instance populated from the file.

    Raises:
        FileNotFoundError: If the config file does not exist.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    with open(path, "r") as f:
        raw = yaml.safe_load(f)
    return Config(
        circuit=CircuitParams(**raw.get("circuit", {})),
        sac=SACParams(**raw.get("sac", {})),
        reward_weights=RewardWeights(**raw.get("reward_weights", {})),
        meta=MetaOptConfig(**raw.get("meta", {})),
        train=TrainConfig(**raw.get("train", {})),
    )
