import torch
import torch.nn.functional as F
import torch.optim as optim
import numpy as np
from copy import deepcopy
from dc_auto_tune.rl.networks import Actor, Critic
from dc_auto_tune.utils.types_ import SACParams


class SACAgent:
    def __init__(self, obs_dim: int, action_dim: int, params: SACParams):
        self.params = params
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        self.actor = Actor(obs_dim, action_dim, params.hidden_dim, params.n_hidden).to(self.device)
        self.critic1 = Critic(obs_dim, action_dim, params.hidden_dim, params.n_hidden).to(self.device)
        self.critic2 = Critic(obs_dim, action_dim, params.hidden_dim, params.n_hidden).to(self.device)
        self.target_critic1 = deepcopy(self.critic1)
        self.target_critic2 = deepcopy(self.critic2)

        self.actor_opt = optim.Adam(self.actor.parameters(), lr=params.actor_lr)
        self.critic_opt = optim.Adam(
            list(self.critic1.parameters()) + list(self.critic2.parameters()),
            lr=params.critic_lr
        )

        self.log_alpha = torch.tensor(np.log(params.initial_alpha), requires_grad=True, device=self.device)
        self.alpha_opt = optim.Adam([self.log_alpha], lr=params.alpha_lr)
        self.target_entropy = -action_dim

    def select_action(self, obs: torch.Tensor, evaluate: bool = False) -> float:
        self.actor.eval()
        with torch.no_grad():
            obs_t = obs.unsqueeze(0).to(self.device) if obs.dim() == 1 else obs.to(self.device)
            if evaluate:
                _, _, action = self.actor.sample(obs_t)
            else:
                action, _, _ = self.actor.sample(obs_t)
        self.actor.train()
        return float(action.cpu().numpy().flatten()[0])

    def update(self, batch: tuple) -> dict:
        obs, actions, rewards, next_obs, dones = [x.to(self.device) for x in batch]

        with torch.no_grad():
            next_action, next_log_prob, _ = self.actor.sample(next_obs)
            q1_target = self.target_critic1(next_obs, next_action)
            q2_target = self.target_critic2(next_obs, next_action)
            q_target = torch.min(q1_target, q2_target) - self.alpha * next_log_prob
            q_target = rewards + self.params.gamma * (1 - dones) * q_target

        q1 = self.critic1(obs, actions)
        q2 = self.critic2(obs, actions)
        critic_loss = F.mse_loss(q1, q_target) + F.mse_loss(q2, q_target)

        self.critic_opt.zero_grad()
        critic_loss.backward()
        self.critic_opt.step()

        action_sampled, log_prob, _ = self.actor.sample(obs)
        q1_new = self.critic1(obs, action_sampled)
        q2_new = self.critic2(obs, action_sampled)
        q_min = torch.min(q1_new, q2_new)
        actor_loss = (self.alpha.detach() * log_prob - q_min).mean()

        self.actor_opt.zero_grad()
        actor_loss.backward()
        self.actor_opt.step()

        alpha_loss = -(self.log_alpha * (log_prob + self.target_entropy).detach()).mean()
        self.alpha_opt.zero_grad()
        alpha_loss.backward()
        self.alpha_opt.step()

        # Soft target update
        for target, source in [
            (self.target_critic1, self.critic1),
            (self.target_critic2, self.critic2)
        ]:
            for tp, sp in zip(target.parameters(), source.parameters()):
                tp.data.copy_(self.params.tau * sp.data + (1 - self.params.tau) * tp.data)

        return {
            "critic_loss": float(critic_loss.item()),
            "actor_loss": float(actor_loss.item()),
            "alpha_loss": float(alpha_loss.item()),
            "alpha": float(self.alpha.item()),
        }

    @property
    def alpha(self) -> torch.Tensor:
        return self.log_alpha.exp()

    def update_hyperparams(self, **kwargs):
        """Called by LLM meta-optimizer to adjust hyperparameters at runtime."""
        for k, v in kwargs.items():
            if hasattr(self.params, k):
                setattr(self.params, k, v)
        for pg in self.actor_opt.param_groups:
            pg["lr"] = self.params.actor_lr
        for pg in self.critic_opt.param_groups:
            pg["lr"] = self.params.critic_lr
        for pg in self.alpha_opt.param_groups:
            pg["lr"] = self.params.alpha_lr
