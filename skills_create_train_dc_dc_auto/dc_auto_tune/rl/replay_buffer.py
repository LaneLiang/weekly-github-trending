import torch
import numpy as np


class ReplayBuffer:
    def __init__(self, capacity: int, obs_dim: int, action_dim: int):
        self.capacity = capacity
        self.ptr = 0
        self.size = 0
        self.obs = np.zeros((capacity, obs_dim), dtype=np.float32)
        self.actions = np.zeros((capacity, action_dim), dtype=np.float32)
        self.rewards = np.zeros((capacity, 1), dtype=np.float32)
        self.next_obs = np.zeros((capacity, obs_dim), dtype=np.float32)
        self.dones = np.zeros((capacity, 1), dtype=np.float32)

    def push(self, obs, action, reward, next_obs, done):
        idx = self.ptr % self.capacity
        self.obs[idx] = obs.numpy() if isinstance(obs, torch.Tensor) else obs
        self.actions[idx] = action.numpy().reshape(-1) if isinstance(action, torch.Tensor) else action
        self.rewards[idx] = reward
        self.next_obs[idx] = next_obs.numpy() if isinstance(next_obs, torch.Tensor) else next_obs
        self.dones[idx] = float(done)
        self.ptr += 1
        self.size = min(self.size + 1, self.capacity)

    def sample(self, batch_size: int) -> tuple | None:
        if self.size < batch_size:
            return None
        idxs = np.random.randint(0, self.size, size=batch_size)
        return (
            torch.from_numpy(self.obs[idxs]),
            torch.from_numpy(self.actions[idxs]),
            torch.from_numpy(self.rewards[idxs]),
            torch.from_numpy(self.next_obs[idxs]),
            torch.from_numpy(self.dones[idxs]),
        )

    def __len__(self):
        return self.size
