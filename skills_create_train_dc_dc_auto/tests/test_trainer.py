import pytest
import torch
from unittest.mock import Mock, patch
from dc_auto_tune.train.trainer import Trainer
from dc_auto_tune.utils.types_ import Config, CircuitParams, SACParams, TrainConfig, MetaOptConfig, RewardWeights


class TestTrainer:
    @pytest.fixture
    def config(self):
        c = Config()
        c.train.n_episodes = 5
        c.train.steps_per_episode = 50
        c.train.warmup_steps = 50
        return c

    @patch("dc_auto_tune.meta.llm_client.LLMClient")
    def test_trainer_runs_without_crash(self, mock_llm, config):
        """Smoke test: trainer completes N episodes without exception."""
        trainer = Trainer(config)
        trainer.train()
        assert trainer.current_episode == config.train.n_episodes

    @patch("dc_auto_tune.meta.llm_client.LLMClient")
    def test_trainer_calls_llm_at_intervention(self, mock_llm, config):
        """LLM should be called every intervention_interval episodes."""
        config.meta.intervention_interval = 2
        config.train.n_episodes = 6
        trainer = Trainer(config)
        trainer.train()
        assert trainer.llm_call_count >= 1
