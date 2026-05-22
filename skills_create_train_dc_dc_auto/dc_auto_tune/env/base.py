"""Abstract base class for DC-DC converter Gymnasium environments."""

from abc import ABC, abstractmethod

import torch
from gymnasium import spaces


class DCDCEnv(ABC):
    """Abstract base for all DC-DC converter environments.

    All concrete environments (BuckCCMEnv, BuckDCMEnv, BoostCCMEnv, etc.)
    must subclass this and implement :meth:`reset` and :meth:`step`.
    """

    def __init__(self):
        self.observation_space = spaces.Box(
            low=-1e3, high=1e3, shape=(7,), dtype=float
        )
        self.action_space = spaces.Box(
            low=0.0, high=1.0, shape=(1,), dtype=float
        )

    @abstractmethod
    def reset(self) -> torch.Tensor:
        """Reset environment to initial state.

        Returns
        -------
        torch.Tensor
            Initial observation vector of shape (7,).
        """
        ...

    @abstractmethod
    def step(self, action: float) -> tuple[torch.Tensor, float, bool, bool, dict]:
        """Advance environment by one time-step.

        Parameters
        ----------
        action : float
            Duty-cycle command in [0, 1].

        Returns
        -------
        obs : torch.Tensor
            Next observation vector of shape (7,).
        reward : float
            Scalar reward.
        terminated : bool
            Whether episode has terminated.
        truncated : bool
            Whether episode was truncated (e.g. time limit).
        info : dict
            Auxiliary diagnostics.
        """
        ...
