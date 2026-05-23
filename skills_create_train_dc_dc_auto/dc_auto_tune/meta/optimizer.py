"""LLM-driven meta-optimizer for SAC hyperparameter and reward-weight tuning."""

import json

from dc_auto_tune.utils.types_ import MetaOptConfig
from dc_auto_tune.meta.hyperparam_space import HyperparamSpace
from dc_auto_tune.meta.llm_client import LLMClient
from dc_auto_tune.meta import llm_client as _llm_client_mod

SYSTEM_PROMPT = """You are an expert in reinforcement learning training optimization for power electronics control.
Your task is to analyze the training progress of a SAC agent controlling a DC-DC buck converter,
and suggest adjustments to SAC hyperparameters and reward function weights to accelerate convergence.

CRITICAL — P0 Gate Constraint (Lexicographic Priority):

The 7 objectives have a strict lexicographic priority order. This means:

  1. PRIMARY GATE: vo_error (voltage regulation accuracy) is the PRIMARY gate metric.
     If vo_error > 0.5% (P0 FAIL), ALL other objectives MUST yield.
     You MUST NOT decrease w_ev (voltage error weight) when vo_error P0 has not been met.
     Decreasing w_ev to boost other reward components while vo_error degrades past 0.5%
     is REWARD HACKING and is strictly forbidden.

  2. PRIORITY ORDER: First, pass vo_error P0 (error < 0.5%).
     Then, pass all other P0 thresholds (ripple < 2%, eff > 88%, overshoot < 5%,
     undershoot < 5%, recovery < 500us, startup < 10ms).
     Only after ALL P0 gates are passed may you optimize P1 targets.

  3. WEIGHT ADJUSTMENT RULES:
     - If vo_error P0 FAIL: INCREASE w_ev aggressively. Do not decrease w_ev for any reason.
     - If vo_error P0 PASS but other P0 metrics FAIL: adjust weights to fix the worst
       failing P0 metric while keeping vo_error < 0.5%. Never let a weight decrease
       on the failing metric.
     - If ALL P0 metrics PASS: you may freely tune weights toward user preferences
       and P1 targets.

  4. SAFETY CHECK: Before suggesting any weight_updates, verify that decreasing any
     weight will not cause its corresponding metric to degrade past P0. If a metric
     is already near the P0 boundary, do NOT decrease its weight.

The agent optimizes 7 objectives simultaneously:
  1. w_ev  — voltage error (deviation from Vref)
  2. w_vr  — voltage ripple (peak-to-peak over window)
  3. w_eff — efficiency (P_out / P_in)
  4. w_os  — overshoot penalty (above +5% band)
  5. w_us  — undershoot penalty (below -5% band)
  6. w_tr  — transient recovery penalty (after disturbance)
  7. w_ts  — startup time penalty (decays with time)

Target tiers (must reach P0 for functional controller):
  P0: error<0.5%, ripple<2%, eff>88%, overshoot<5%, undershoot<5%, recovery<500us, startup<10ms
  P1: error<0.2%, ripple<1%, eff>92%, overshoot<2%, undershoot<2%, recovery<200us, startup<5ms

{preference_section}

Respond with a JSON object containing:
{{
  "analysis": "brief analysis of current bottlenecks (1-2 sentences)",
  "sac_updates": {{ "parameter_name": new_value, ... }},
  "weight_updates": {{ "w_xx": new_weight, ... }}
}}

Only adjust parameters that need changing. Keep adjustments within the provided bounds.
When metrics are improving, make small adjustments. When stuck, make larger changes.
ALWAYS prioritize P0 gate failures first — fix vo_error before any other metric.
If a user preference is specified, bias weight adjustments toward the preferred
objective ONLY after all P0 gates (especially vo_error) are satisfied.
{hyperparam_context}"""


PREFERENCE_MAP: dict[str, str] = {
    "efficiency": (
        "USER PREFERENCE: Prioritize efficiency above all else.\n"
        "IMPORTANT: If P0 vo_error is not met (<0.5%), first bring vo_error under "
        "control by increasing w_ev before optimizing efficiency.\n"
        "Increase w_eff significantly and reduce w_vr, w_tr.\n"
        "Accept slightly higher ripple and slower recovery if efficiency improves "
        "ONLY IF vo_error stays < 0.5%."
    ),
    "transient": (
        "USER PREFERENCE: Prioritize transient response (fast recovery, low overshoot).\n"
        "IMPORTANT: If P0 vo_error is not met (<0.5%), first bring vo_error under "
        "control by increasing w_ev before optimizing transient response.\n"
        "Increase w_tr, w_os, w_us significantly.\n"
        "Accept slightly lower efficiency if transient performance improves "
        "ONLY IF vo_error stays < 0.5%."
    ),
    "ripple": (
        "USER PREFERENCE: Prioritize low output voltage ripple.\n"
        "IMPORTANT: If P0 vo_error is not met (<0.5%), first bring vo_error under "
        "control by increasing w_ev before optimizing ripple.\n"
        "Increase w_vr significantly and w_ev moderately.\n"
        "Accept slightly slower startup and lower efficiency if ripple decreases "
        "ONLY IF vo_error stays < 0.5%."
    ),
    "startup": (
        "USER PREFERENCE: Prioritize fast startup time.\n"
        "IMPORTANT: If P0 vo_error is not met (<0.5%), first bring vo_error under "
        "control by increasing w_ev before optimizing startup.\n"
        "Increase w_ts significantly.\n"
        "Accept higher overshoot during startup if settling is faster "
        "ONLY IF vo_error stays < 0.5%."
    ),
    "balanced": (
        "USER PREFERENCE: Balanced optimization across all 7 objectives.\n"
        "IMPORTANT: If P0 vo_error is not met (<0.5%), first bring vo_error under "
        "control by increasing w_ev. Keep all weights roughly equal afterward.\n"
        "Focus on the metric furthest from P0 threshold.\n"
        "Never decrease w_ev before vo_error P0 is satisfied."
    ),
}


class LLMMetaOptimizer:
    """Periodically queries an LLM to suggest hyperparameter / reward-weight
    adjustments based on training progress.

    Supports user semantic preference injection for Pareto navigation —
    the key differentiator vs Random Search.

    Suggested values are clamped to the defined ``HyperparamSpace`` bounds and
    magnitude-limited to prevent destabilising jumps.
    """

    def __init__(
        self,
        config: MetaOptConfig,
        space: HyperparamSpace,
        api_key: str | None = None,
        user_preference: str = "balanced",
    ):
        self.config = config
        self.space = space
        self._api_key = api_key
        self.user_preference = user_preference
        self._client: LLMClient | None = None  # type: ignore[valid-type]

    @property
    def client(self):
        """Lazily resolve LLMClient so that ``@patch`` on the module-level class
        is picked up when the test fixture creates this optimizer before the
        patcher is active."""
        if self._client is None:
            self._client = _llm_client_mod.LLMClient(self.config, self._api_key)
        return self._client

    def analyze_and_suggest(self, training_state: dict, preference: str | None = None) -> dict:
        """Analyze the current training state and return suggested adjustments.

        Args:
            training_state: Dict with keys ``episode``, ``recent_rewards``,
                ``metrics``, ``current_sac``, ``current_weights``.
            preference: Optional per-call preference override.

        Returns:
            Dict with keys ``analysis``, ``sac_updates``, ``weight_updates``.
        """
        pref = preference or self.user_preference
        preference_text = PREFERENCE_MAP.get(pref, PREFERENCE_MAP["balanced"])
        system = SYSTEM_PROMPT.format(
            preference_section=preference_text,
            hyperparam_context=self.space.generate_prompt_context(),
        )
        user = self._build_prompt(training_state, pref)
        result = self._call_with_retry(system, user)

        if "sac_updates" in result:
            result["sac_updates"] = self.space.validate_and_clamp_sac(
                self._apply_magnitude_limit(result["sac_updates"], training_state)
            )
        if "weight_updates" in result:
            result["weight_updates"] = self.space.validate_and_clamp_weights(
                result["weight_updates"]
            )
        return result

    def _call_with_retry(self, system: str, user: str, max_retries: int = 2) -> dict:
        """Call LLM and parse JSON, retrying once with a stricter prompt on failure."""
        raw = self.client.chat(system, user)
        for attempt in range(max_retries):
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                if attempt == max_retries - 1:
                    return {
                        "analysis": "LLM returned unparseable JSON after retry",
                        "sac_updates": {},
                        "weight_updates": {},
                    }
                # Retry with a stronger prompt
                retry_user = (
                    "Your previous response was not valid JSON. "
                    "You MUST respond with ONLY a valid JSON object. "
                    "Do not include any text outside the JSON.\n\n"
                    + user
                )
                raw = self.client.chat(system, retry_user)

    def _build_prompt(self, state: dict, preference: str = "balanced") -> str:
        """Build the user-message text describing current training state.

        P0 gate status is displayed prominently at the top with a CRITICAL
        warning when the primary gate (vo_error) fails.
        """
        metrics = state.get("metrics", {})
        rewards = state.get("recent_rewards", [])
        p0_checks = self._check_p0_status(metrics)

        # Detect whether the primary gate (vo_error P0) is failing
        vo_error = metrics.get("vo_error_pct")
        vo_error_fail = vo_error is not None and vo_error >= 0.5
        critical_warning = ""
        if vo_error_fail:
            critical_warning = (
                "\n"
                "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n"
                "  CRITICAL: vo_error P0 FAIL — this is the PRIMARY gate.\n"
                "  vo_error = {:.2f}% (P0 threshold: < 0.5%)\n"
                "  Fix this before optimizing anything else.\n"
                "  You MUST increase w_ev. Do NOT decrease w_ev.\n"
                "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n"
            ).format(vo_error)

        return f"""Training progress report:
Episode: {state['episode']}
User preference: {preference}
{critical_warning}
P0 Gate Status (PASS/FAIL — vo_error is the PRIMARY gate):
{p0_checks}

Recent episode rewards: {rewards[-5:]}
Current metrics:
  - Voltage error: {metrics.get('vo_error_pct', 'N/A')}%
  - Voltage ripple: {metrics.get('vo_ripple_pct', 'N/A')}%
  - Efficiency: {metrics.get('efficiency_pct', 'N/A')}%
  - Overshoot: {metrics.get('overshoot_pct', 'N/A')}%
  - Undershoot: {metrics.get('undershoot_pct', 'N/A')}%
  - Startup time: {metrics.get('startup_time_ms', 'N/A')}ms
  - Recovery time: {metrics.get('recovery_time_ms', 'N/A')}ms

Current SAC hyperparameters:
{self._dict_to_str(state.get('current_sac', {}))}

Current reward weights:
{self._dict_to_str(state.get('current_weights', {}))}

Please analyze the training progress and suggest adjustments."""

    @staticmethod
    def _check_p0_status(metrics: dict) -> str:
        """Render which P0 thresholds are currently met."""
        from dc_auto_tune.eval.metrics import TIER_SPECS
        p0 = TIER_SPECS.get("P0", {})
        lines = []
        for key, (limit, direction) in p0.items():
            val = metrics.get(key)
            if val is None:
                lines.append(f"  {key}: N/A (target {'<' if direction == 'lt' else '>'} {limit})")
                continue
            if direction == "lt":
                ok = val < limit
            else:
                ok = val > limit
            status = "OK" if ok else "FAIL"
            lines.append(f"  {key}: {val} ({'<' if direction == 'lt' else '>'} {limit}) [{status}]")
        return "\n".join(lines)

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
