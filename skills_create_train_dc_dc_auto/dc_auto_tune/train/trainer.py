"""Main training loop with periodic LLM meta-optimization interventions."""

import torch
import numpy as np
from collections import deque
from dc_auto_tune.utils.types_ import Config
from dc_auto_tune.env.buck_ccm import BuckCCMEnv
from dc_auto_tune.env.rewards import MultiObjectiveReward
from dc_auto_tune.rl.sac_agent import SACAgent
from dc_auto_tune.rl.replay_buffer import ReplayBuffer
from dc_auto_tune.meta.optimizer import LLMMetaOptimizer
from dc_auto_tune.meta.hyperparam_space import HyperparamSpace
from dc_auto_tune.train.logger import TrainingLogger


class Trainer:
    """Orchestrates the RL training loop for DC-DC converter tuning.

    Each episode collects experience via environment interaction, stores
    transitions in a replay buffer, and periodically updates the SAC agent.
    At a configurable interval the LLM meta-optimizer inspects training
    progress and suggests hyperparameter / reward-weight adjustments.
    """

    def __init__(self, config: Config, api_key: str | None = None):
        self.config = config
        self.env = BuckCCMEnv(config.circuit)
        self.reward_fn = MultiObjectiveReward(config.circuit.vout_ref, config.reward_weights)
        self.agent = SACAgent(obs_dim=7, action_dim=1, params=config.sac)
        self.buffer = ReplayBuffer(config.sac.buffer_size, obs_dim=7, action_dim=1)
        self.meta_opt = LLMMetaOptimizer(config.meta, HyperparamSpace(), api_key)
        self.logger = TrainingLogger()
        self.current_episode = 0
        self.global_step = 0
        self.llm_call_count = 0
        self.reward_window = deque(maxlen=20)
        self.metric_window = deque(maxlen=20)

    def train(self):
        """Run the main training loop for ``config.train.n_episodes`` episodes."""
        for ep in range(self.config.train.n_episodes):
            self.current_episode = ep + 1
            obs = self.env.reset()
            ep_reward = 0.0
            ep_metrics = {}

            for step in range(self.config.train.steps_per_episode):
                action = self.agent.select_action(obs, evaluate=False)
                next_obs, reward, done, _, info = self.env.step(action)
                self.buffer.push(obs, torch.tensor([action]), reward, next_obs, done)
                self.global_step += 1
                obs = next_obs
                ep_reward += reward

                if self.global_step >= self.config.train.warmup_steps:
                    batch = self.buffer.sample(self.config.sac.batch_size)
                    if batch is not None:
                        update_info = self.agent.update(batch)
                        ep_metrics = update_info

                if done:
                    break

            self.reward_window.append(ep_reward / (step + 1))
            self.logger.log_episode({
                "episode": self.current_episode,
                "avg_reward": np.mean(self.reward_window),
                "vo_ripple": 0,
                "vo_error": abs(self.config.circuit.vout_ref - info.get("vo", 0)),
                "critic_loss": ep_metrics.get("critic_loss", 0),
                "actor_loss": ep_metrics.get("actor_loss", 0),
                "alpha": ep_metrics.get("alpha", 0),
            })

            if self.current_episode % self.config.meta.intervention_interval == 0:
                self._llm_intervention()

    def _llm_intervention(self):
        """Query the LLM meta-optimizer and apply suggested adjustments.

        The intervention is best-effort: if the LLM is unavailable or
        returns unparseable output the call is counted but the loop
        continues gracefully.
        """
        state = {
            "episode": self.current_episode,
            "recent_rewards": list(self.reward_window),
            "metrics": {},
            "current_sac": self.agent.params,
            "current_weights": self.reward_fn.weights,
        }
        self.llm_call_count += 1
        try:
            result = self.meta_opt.analyze_and_suggest(state)
        except Exception:
            return

        self.logger.save_llm_intervention(self.current_episode, result)

        if "sac_updates" in result:
            self.agent.update_hyperparams(**result["sac_updates"])
        if "weight_updates" in result:
            from dc_auto_tune.utils.types_ import RewardWeights
            new_weights = RewardWeights(**{
                **self.reward_fn.weights.__dict__,
                **result["weight_updates"]
            })
            self.reward_fn.update_weights(new_weights)
