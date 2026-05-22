"""Tests for PlateauDetector event-triggered intervention logic."""

import pytest
from dc_auto_tune.meta.plateau_detector import PlateauDetector


class TestPlateauDetector:
    """Unit tests for plateau detection algorithm."""

    def test_no_trigger_with_insufficient_data(self):
        """Should not trigger before enough reward history accumulates."""
        detector = PlateauDetector(window=20, patience=5, min_interval=5)
        for ep in range(1, 6):
            assert not detector.update(ep, 0.0)

    def test_no_trigger_when_improving(self):
        """Should not fire when reward is steadily improving."""
        detector = PlateauDetector(window=10, patience=3, min_interval=5)
        # Steady improvement: -1.0 → -0.1
        rewards = [-1.0 + i * 0.05 for i in range(20)]
        triggers = 0
        for ep, r in enumerate(rewards, start=1):
            if detector.update(ep, r):
                triggers += 1
        assert triggers == 0, f"Expected 0 triggers during improvement, got {triggers}"

    def test_triggers_on_plateau(self):
        """Should fire when reward stagnates."""
        detector = PlateauDetector(
            window=10, patience=3, improvement_threshold=0.01,
            min_interval=5, max_interval=50,
        )
        # First 10 episodes: improvement
        for ep in range(1, 11):
            r = -1.0 + ep * 0.08
            detector.update(ep, r)
        # Next 15 episodes: flat plateau at ~-0.1
        triggers = []
        for ep in range(11, 26):
            r = -0.1 + (ep % 3) * 0.001  # tiny noise
            if detector.update(ep, r):
                triggers.append(ep)
        assert len(triggers) >= 1, f"Expected at least 1 plateau trigger, got {triggers}"

    def test_triggers_on_degradation(self):
        """Should fire when reward gets worse (negative improvement)."""
        detector = PlateauDetector(
            window=10, patience=3, improvement_threshold=0.01,
            min_interval=5, max_interval=50,
        )
        # First 10 episodes: improvement to -0.2
        for ep in range(1, 11):
            r = -1.0 + ep * 0.08
            detector.update(ep, r)
        # Next 15 episodes: degradation back toward -0.5
        triggers = []
        for ep in range(11, 26):
            r = -0.2 - (ep - 10) * 0.02
            if detector.update(ep, r):
                triggers.append(ep)
        assert len(triggers) >= 1, f"Expected trigger on degradation, got {triggers}"

    def test_min_interval_respected(self):
        """Should not trigger again within min_interval even on plateau."""
        detector = PlateauDetector(
            window=10, patience=2, improvement_threshold=0.01,
            min_interval=10, max_interval=50,
        )
        # First generate enough data to fill window
        for ep in range(1, 12):
            detector.update(ep, -0.5)
        # Now stay flat — should trigger
        triggered = False
        trigger_ep = None
        for ep in range(12, 30):
            if detector.update(ep, -0.5):
                if not triggered:
                    triggered = True
                    trigger_ep = ep
                elif ep - trigger_ep < 10:
                    pytest.fail(f"Triggered again at ep {ep}, only {ep - trigger_ep} after last (min_interval=10)")

    def test_max_interval_safety_net(self):
        """Should force-trigger when max_interval is exceeded."""
        detector = PlateauDetector(
            window=10, patience=10, improvement_threshold=0.01,
            min_interval=5, max_interval=15,
        )
        # Steady improvement — should NOT trigger by plateau detection
        for ep in range(1, 10):
            r = -1.0 + ep * 0.1
            assert not detector.update(ep, r), f"Unexpected trigger at ep {ep}"
        # After max_interval, should force-trigger even with improvement
        forced = False
        for ep in range(10, 25):
            r = -1.0 + ep * 0.1
            if detector.update(ep, r):
                forced = True
                break
        assert forced, "Safety net did not trigger within max_interval"

    def test_trigger_count_increments(self):
        """Trigger count should track number of interventions."""
        detector = PlateauDetector(
            window=10, patience=2, improvement_threshold=0.01,
            min_interval=5, max_interval=15,
        )
        assert detector.trigger_count == 0
        # Fill with flat rewards to trigger
        for ep in range(1, 30):
            detector.update(ep, -0.5)
        assert detector.trigger_count >= 1

    def test_validation_rejects_invalid_params(self):
        """Constructor should reject nonsensical parameter combinations."""
        with pytest.raises(ValueError):
            PlateauDetector(window=2)  # too small
        with pytest.raises(ValueError):
            PlateauDetector(patience=1)  # too small
        with pytest.raises(ValueError):
            PlateauDetector(min_interval=0)  # must be >= 1
        with pytest.raises(ValueError):
            PlateauDetector(min_interval=10, max_interval=5)  # max must exceed min
