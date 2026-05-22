"""Boost converter CCM/DCM environment with Euler integration of ODE."""

import torch
import numpy as np
from dc_auto_tune.env.base import DCDCEnv
from dc_auto_tune.utils.types_ import CircuitParams


class BoostCCMEnv(DCDCEnv):
    """Boost converter with CCM/DCM dual-mode simulation via Euler integration.

    State: [Vo, iL, error, integral_error, d_prev, load_current, Vin, mode_flag]
    """

    def __init__(self, params: CircuitParams, dt_per_cycle: int = 50):
        super().__init__()
        self.p = params
        self.dt_per_cycle = dt_per_cycle
        self.T_sw = 1.0 / params.f_sw
        self.dt = self.T_sw / dt_per_cycle

        self.vo: float = 0.0
        self.iL: float = 0.0
        self.d_prev: float = 0.0
        self.integral_error: float = 0.0
        self.step_count: int = 0
        self.max_steps: int = 2000
        self._in_dcm: bool = False
        self._dcm_entered_this_cycle: bool = False

    def reset(self) -> torch.Tensor:
        """Reset environment to zero initial conditions."""
        self.vo = 0.0
        self.iL = 0.0
        self.d_prev = 0.0
        self.integral_error = 0.0
        self.step_count = 0
        self._in_dcm = False
        self._dcm_entered_this_cycle = False
        return self._get_obs()

    def step(self, action: float) -> tuple[torch.Tensor, float, bool, bool, dict]:
        """Advance by one switching cycle.

        Parameters
        ----------
        action : float
            Duty-cycle command, clamped to [0, 1].

        Returns
        -------
        obs, reward, terminated, truncated, info
        """
        d = float(np.clip(action, 0.0, 1.0))
        self._dcm_entered_this_cycle = False

        on_substeps = int(d * self.dt_per_cycle)

        for i in range(self.dt_per_cycle):
            is_on = i < on_substeps

            if self._in_dcm:
                if is_on:
                    self._in_dcm = False
                else:
                    # DCM IDLE: only capacitor discharge
                    dvo_dt = -self.vo / (self.p.R_load * self.p.C)
                    self.vo += dvo_dt * self.dt
                    self.step_count += 1
                    continue

            if is_on:
                # ON phase: switch closed, inductor charges from Vin
                diL_dt = (self.p.vin - self.iL * self.p.rds_on) / self.p.L
                dvo_dt = -self.vo / (self.p.R_load * self.p.C)
            else:
                # OFF phase: switch open, inductor discharges to output
                diL_dt = (self.p.vin - self.vo - self.iL * self.p.esr_c) / self.p.L
                dvo_dt = (self.iL - self.vo / self.p.R_load) / self.p.C

            self.iL += diL_dt * self.dt
            self.vo += dvo_dt * self.dt

            if self.iL <= 0 and not is_on:
                self.iL = 0.0
                self._in_dcm = True
                self._dcm_entered_this_cycle = True

            self.step_count += 1

        self.d_prev = d
        error = self.p.vout_ref - self.vo
        self.integral_error += error * self.T_sw
        info = {
            "vo": self.vo,
            "iL": self.iL,
            "d": d,
            "mode": "DCM" if self._dcm_entered_this_cycle else "CCM",
        }
        terminated = self.step_count >= self.max_steps
        reward = float(-abs(error) / self.p.vout_ref)
        return self._get_obs(), reward, terminated, False, info

    def _get_obs(self) -> torch.Tensor:
        """Build observation vector of shape (8,) including mode_flag."""
        error = self.p.vout_ref - self.vo
        i_load = self.vo / max(self.p.R_load, 1e-6)
        return torch.tensor(
            [
                self.vo,
                self.iL,
                error,
                self.integral_error,
                self.d_prev,
                i_load,
                self.p.vin,
                float(self._in_dcm),
            ],
            dtype=torch.float32,
        )
