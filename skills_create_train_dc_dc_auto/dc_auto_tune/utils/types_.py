"""Shared dataclass type definitions for dc_auto_tune."""

from dataclasses import dataclass, field


@dataclass
class CircuitParams:
    """Buck converter circuit parameters."""

    vin: float = 12.0
    vout_ref: float = 5.0
    L: float = 100e-6
    C: float = 100e-6
    R_load: float = 5.0
    f_sw: float = 100e3
    rds_on: float = 0.05
    esr_c: float = 0.01


@dataclass
class SACParams:
    """SAC agent hyperparameters."""

    actor_lr: float = 3e-4
    critic_lr: float = 3e-4
    alpha_lr: float = 3e-4
    gamma: float = 0.99
    tau: float = 0.005
    batch_size: int = 256
    buffer_size: int = 100_000
    hidden_dim: int = 256
    n_hidden: int = 2
    initial_alpha: float = 0.2


@dataclass
class RewardWeights:
    """Multi-objective reward function weights."""

    w_vr: float = 1.0   # voltage regulation
    w_ev: float = 1.0   # error voltage
    w_eff: float = 0.5  # efficiency
    w_tr: float = 0.8   # transient response
    w_os: float = 0.8   # overshoot
    w_us: float = 0.8   # undershoot
    w_pm: float = 0.3   # phase margin
    w_ts: float = 0.5   # settling time


@dataclass
class MetaOptConfig:
    """LLM meta-optimizer configuration."""

    llm_provider: str = "openai"  # "openai" also covers DeepSeek (compatible API)
    llm_model: str = "deepseek-chat"
    llm_base_url: str = "https://api.deepseek.com"
    llm_api_key: str = ""  # populated from env at load time
    intervention_interval: int = 50
    temperature: float = 0.2
    max_suggestion_magnitude: float = 0.5


@dataclass
class TrainConfig:
    """Training loop configuration."""

    n_episodes: int = 1000
    steps_per_episode: int = 500
    warmup_steps: int = 5000
    update_every: int = 1
    random_seed: int = 42


@dataclass
class Config:
    """Top-level configuration aggregating all sub-configs."""

    circuit: CircuitParams = field(default_factory=CircuitParams)
    sac: SACParams = field(default_factory=SACParams)
    reward_weights: RewardWeights = field(default_factory=RewardWeights)
    meta: MetaOptConfig = field(default_factory=MetaOptConfig)
    train: TrainConfig = field(default_factory=TrainConfig)
