import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.distributions import Normal

LOG_STD_MIN = -20
LOG_STD_MAX = 2
ACTION_MIN = 0.0
ACTION_MAX = 1.0


def build_mlp(in_dim: int, out_dim: int, hidden_dim: int, n_hidden: int) -> nn.Sequential:
    layers = []
    for i in range(n_hidden):
        layers.append(nn.Linear(in_dim if i == 0 else hidden_dim, hidden_dim))
        layers.append(nn.ReLU())
    layers.append(nn.Linear(hidden_dim, out_dim))
    return nn.Sequential(*layers)


class Actor(nn.Module):
    def __init__(self, obs_dim: int, action_dim: int, hidden_dim: int = 256, n_hidden: int = 2):
        super().__init__()
        self.backbone = build_mlp(obs_dim, hidden_dim, hidden_dim, n_hidden)
        self.mean_head = nn.Linear(hidden_dim, action_dim)
        self.log_std_head = nn.Linear(hidden_dim, action_dim)

    def forward(self, obs: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        x = F.relu(self.backbone(obs))
        mean = self.mean_head(x)
        log_std = torch.clamp(self.log_std_head(x), LOG_STD_MIN, LOG_STD_MAX)
        return mean, log_std

    def sample(self, obs: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        mean, log_std = self.forward(obs)
        std = log_std.exp()
        dist = Normal(mean, std)
        z = dist.rsample()
        action = torch.tanh(z)
        log_prob = dist.log_prob(z) - torch.log(1 - action.pow(2) + 1e-6)
        log_prob = log_prob.sum(dim=-1, keepdim=True)
        action_scaled = ACTION_MIN + (ACTION_MAX - ACTION_MIN) * (action + 1) / 2
        mean_scaled = ACTION_MIN + (ACTION_MAX - ACTION_MIN) * (torch.tanh(mean) + 1) / 2
        return action_scaled, log_prob, mean_scaled


class Critic(nn.Module):
    def __init__(self, obs_dim: int, action_dim: int, hidden_dim: int = 256, n_hidden: int = 2):
        super().__init__()
        self.q_net = build_mlp(obs_dim + action_dim, 1, hidden_dim, n_hidden)

    def forward(self, obs: torch.Tensor, action: torch.Tensor) -> torch.Tensor:
        return self.q_net(torch.cat([obs, action], dim=-1))
