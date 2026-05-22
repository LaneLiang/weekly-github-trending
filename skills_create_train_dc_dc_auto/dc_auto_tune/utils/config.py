"""Configuration loading utilities."""

import os
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


def _load_env_file(path: str | Path = ".env") -> None:
    """Load key-value pairs from a .env file into os.environ (no override)."""
    path = Path(path)
    if not path.exists():
        return
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            key, val = key.strip(), val.strip().strip("\"'")
            if key not in os.environ:
                os.environ[key] = val


def load_config(path: str | Path) -> Config:
    """Load configuration from a YAML file.

    Args:
        path: Path to the YAML configuration file.

    Returns:
        A Config instance populated from the file.

    Raises:
        FileNotFoundError: If the config file does not exist.
    """
    _load_env_file()

    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    with open(path, "r") as f:
        raw = yaml.safe_load(f)

    meta_raw = raw.get("meta", {})
    # Resolve API key: explicit config > DEEPSEEK_API_KEY > OPENAI_API_KEY > ANTHROPIC_API_KEY
    if not meta_raw.get("llm_api_key"):
        for env_var in ("DEEPSEEK_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY"):
            key = os.environ.get(env_var, "")
            if key:
                meta_raw["llm_api_key"] = key
                break

    return Config(
        circuit=CircuitParams(**raw.get("circuit", {})),
        sac=SACParams(**raw.get("sac", {})),
        reward_weights=RewardWeights(**raw.get("reward_weights", {})),
        meta=MetaOptConfig(**meta_raw),
        train=TrainConfig(**raw.get("train", {})),
    )
