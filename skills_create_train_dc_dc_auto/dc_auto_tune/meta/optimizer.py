"""LLM-driven meta-optimizer for SAC hyperparameter and reward-weight tuning."""

import json

from dc_auto_tune.utils.types_ import MetaOptConfig
from dc_auto_tune.meta.hyperparam_space import HyperparamSpace
from dc_auto_tune.meta.llm_client import LLMClient
from dc_auto_tune.meta import llm_client as _llm_client_mod

SYSTEM_PROMPT = """You are an expert in reinforcement learning training optimization for power electronics control.
Your task is to analyze the training progress of a SAC agent controlling a DC-DC buck converter,
and suggest adjustments to SAC hyperparameters and reward function weights to accelerate convergence.

The agent is being trained to meet multiple objectives: voltage ripple, voltage accuracy, efficiency,
load transient recovery time, overshoot, undershoot, and startup time.

Respond with a JSON object containing:
{{
  "analysis": "brief analysis of current bottlenecks (1-2 sentences)",
  "sac_updates": {{ "parameter_name": new_value, ... }},
  "weight_updates": {{ "w_xx": new_weight, ... }}
}}

Only adjust parameters that need changing. Keep adjustments within the provided bounds.
When metrics are improving, make small adjustments. When stuck, make larger changes.
Prioritize the worst-performing metric.
{hyperparam_context}"""


class LLMMetaOptimizer:
    """Periodically queries an LLM to suggest hyperparameter / reward-weight
    adjustments based on training progress.

    Suggested values are clamped to the defined ``HyperparamSpace`` bounds and
    magnitude-limited to prevent destabilising jumps.
    """

    def __init__(
        self,
        config: MetaOptConfig,
        space: HyperparamSpace,
        api_key: str | None = None,
    ):
        self.config = config
        self.space = space
        self._api_key = api_key
        self._client: LLMClient | None = None  # type: ignore[valid-type]

    @property
    def client(self):
        """Lazily resolve LLMClient so that ``@patch`` on the module-level class
        is picked up when the test fixture creates this optimizer before the
        patcher is active."""
        if self._client is None:
            self._client = _llm_client_mod.LLMClient(self.config, self._api_key)
        return self._client

    def analyze_and_suggest(self, training_state: dict) -> dict:
        """Analyze the current training state and return suggested adjustments.

        Args:
            training_state: Dict with keys ``episode``, ``recent_rewards``,
                ``metrics``, ``current_sac``, ``current_weights``.

        Returns:
            Dict with keys ``analysis``, ``sac_updates``, ``weight_updates``.
        """
        system = SYSTEM_PROMPT.format(
            hyperparam_context=self.space.generate_prompt_context()
        )
        user = self._build_prompt(training_state)
        raw = self.client.chat(system, user)
        result = json.loads(raw)

        if "sac_updates" in result:
            result["sac_updates"] = self.space.validate_and_clamp_sac(
                self._apply_magnitude_limit(result["sac_updates"], training_state)
            )
        if "weight_updates" in result:
            result["weight_updates"] = self.space.validate_and_clamp_weights(
                result["weight_updates"]
            )
        return result

    def _build_prompt(self, state: dict) -> str:
        """Build the user-message text describing current training state."""
        metrics = state.get("metrics", {})
        rewards = state.get("recent_rewards", [])
        return f"""Training progress report:
Episode: {state['episode']}
Recent episode rewards: {rewards[-5:]}
Current metrics:
  - Voltage ripple: {metrics.get('vo_ripple_pct', 'N/A')}%
  - Voltage error: {metrics.get('vo_error_pct', 'N/A')}%
  - Recovery time: {metrics.get('recovery_time_ms', 'N/A')}ms
  - Overshoot: {metrics.get('overshoot_pct', 'N/A')}%
  - Undershoot: {metrics.get('undershoot_pct', 'N/A')}%

Current SAC hyperparameters:
{self._dict_to_str(state.get('current_sac', {}))}

Current reward weights:
{self._dict_to_str(state.get('current_weights', {}))}

Please analyze the training progress and suggest adjustments."""

    def _apply_magnitude_limit(self, updates: dict, state: dict) -> dict:
        """Cap each suggested change so no parameter jumps more than
        ``max_suggestion_magnitude`` fraction from its current value."""
        current = state.get("current_sac", {})
        limit = self.config.max_suggestion_magnitude
        limited: dict = {}
        for k, new_val in updates.items():
            if hasattr(current, k):
                old_val = getattr(current, k)
                max_change = (
                    abs(old_val) * limit if abs(old_val) > 1e-9 else 1e-4
                )
                limited[k] = max(
                    old_val - max_change, min(old_val + max_change, new_val)
                )
            else:
                limited[k] = new_val
        return limited

    @staticmethod
    def _dict_to_str(d) -> str:
        """Render a dict or dataclass as one key-value pair per line."""
        if hasattr(d, "__dataclass_fields__"):
            return "\n".join(
                f"  {k}: {v}" for k, v in d.__dict__.items()
            )
        return "\n".join(f"  {k}: {v}" for k, v in d.items())
