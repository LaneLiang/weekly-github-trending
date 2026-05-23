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
    """Multi-objective reward function weights (7 active objectives).

    Each weight scales its corresponding reward term in compute().
    Weights are L1-normalized internally to prevent reward-scale drift.
    """

    w_ev: float = 1.0   # voltage error
    w_vr: float = 1.0   # voltage ripple
    w_eff: float = 0.5  # efficiency
    w_os: float = 0.8   # overshoot
    w_us: float = 0.8   # undershoot
    w_tr: float = 0.8   # transient recovery
    w_ts: float = 0.5   # startup time


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

    # Event-triggered intervention (plateau detection mode)
    use_event_trigger: bool = False
    plateau_window: int = 20
    plateau_patience: int = 5
    plateau_improvement_threshold: float = 0.02
    plateau_min_interval: int = 10
    plateau_max_interval: int = 100


@dataclass
class TrainConfig:
    """Training loop configuration."""

    n_episodes: int = 1000
    steps_per_episode: int = 500
    warmup_steps: int = 5000
    update_every: int = 1
    random_seed: int = 42


@dataclass
class PerturbationConfig:
    """Domain-randomization perturbation ranges (relative to nominal)."""

    max_esr_ratio: float = 2.5
    min_L_ratio: float = 0.8
    min_C_ratio: float = 0.7
    vin_ripple: float = 0.1
    load_spread: float = 0.5
    enabled: bool = True


@dataclass
class Config:
    """Top-level configuration aggregating all sub-configs."""

    circuit: CircuitParams = field(default_factory=CircuitParams)
    sac: SACParams = field(default_factory=SACParams)
    reward_weights: RewardWeights = field(default_factory=RewardWeights)
    meta: MetaOptConfig = field(default_factory=MetaOptConfig)
    train: TrainConfig = field(default_factory=TrainConfig)
    perturbation: PerturbationConfig = field(default_factory=PerturbationConfig)
