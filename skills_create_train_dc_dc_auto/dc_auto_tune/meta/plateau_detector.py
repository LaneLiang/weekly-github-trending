"""Training plateau detector for event-triggered LLM intervention.

Replaces fixed-interval intervention with intelligent triggering:
fires when reward improvement stalls, not on an arbitrary clock.
"""

from collections import deque
import numpy as np


class PlateauDetector:
    """Monitors reward progress and triggers when learning plateaus.

    Detection algorithm:
    1. Maintain rolling window of recent episode rewards
    2. Compare recent half vs. older half mean improvement
    3. If relative improvement < threshold for ``patience`` consecutive
       checks, signal a plateau
    4. Enforce min_interval (cooling) and max_interval (safety net)

    Usage::

        detector = PlateauDetector(window=20, patience=5)
        for episode in range(n_episodes):
            avg_reward = train_one_episode()
            if detector.update(episode, avg_reward):
                trigger_llm_intervention()
    """

    def __init__(
        self,
        window: int = 20,
        patience: int = 5,
        improvement_threshold: float = 0.02,
        min_interval: int = 10,
        max_interval: int = 100,
    ):
        if window < 4:
            raise ValueError("window must be >= 4")
        if patience < 2:
            raise ValueError("patience must be >= 2")
        if min_interval < 1:
            raise ValueError("min_interval must be >= 1")
        if max_interval <= min_interval:
            raise ValueError("max_interval must be > min_interval")

        self.window = window
        self.patience = patience
        self.improvement_threshold = improvement_threshold
        self.min_interval = min_interval
        self.max_interval = max_interval

        self._rewards: deque[float] = deque(maxlen=window)
        self._plateau_counter: int = 0
        self._last_intervention_ep: int = 0  # no prior intervention
        self._trigger_count: int = 0

    def update(self, episode: int, avg_reward: float) -> bool:
        """Ingest a new episode reward; return True if LLM should intervene.

        Args:
            episode: Current episode number (1-indexed).
            avg_reward: Mean reward for the completed episode.

        Returns:
            True if an LLM intervention should be triggered now.
        """
        self._rewards.append(avg_reward)

        # Not enough data yet — let the agent explore
        if len(self._rewards) < self.window // 2:
            return False

        # Safety net: force intervention if max_interval exceeded
        if episode - self._last_intervention_ep >= self.max_interval:
            return self._fire(episode)

        # Cooling period: respect minimum interval
        if episode - self._last_intervention_ep < self.min_interval:
            return False

        # Plateau check: compare recent vs. older reward means
        half = self.window // 2
        rewards = list(self._rewards)
        older = rewards[:half]
        recent = rewards[-half:]

        older_mean = float(np.mean(older))
        recent_mean = float(np.mean(recent))

        # Compute relative improvement (handle negative reward range)
        denom = max(abs(older_mean), 1e-8)
        improvement = (recent_mean - older_mean) / denom

        if improvement < self.improvement_threshold:
            self._plateau_counter += 1
        else:
            self._plateau_counter = max(0, self._plateau_counter - 1)

        if self._plateau_counter >= self.patience:
            return self._fire(episode)

        return False

    def _fire(self, episode: int) -> bool:
        """Record intervention and reset plateau state."""
        self._last_intervention_ep = episode
        self._plateau_counter = 0
        self._trigger_count += 1
        return True

    @property
    def trigger_count(self) -> int:
        return self._trigger_count

    @property
    def plateau_counter(self) -> int:
        return self._plateau_counter

    @property
    def last_intervention_ep(self) -> int:
        return self._last_intervention_ep
