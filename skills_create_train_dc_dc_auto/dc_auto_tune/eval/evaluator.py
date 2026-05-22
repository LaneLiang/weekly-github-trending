"""Policy evaluator for SAC-trained DC-DC converter agents."""

import torch
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from dc_auto_tune.env.buck_ccm import BuckCCMEnv
from dc_auto_tune.rl.sac_agent import SACAgent
from dc_auto_tune.utils.types_ import CircuitParams


class Evaluator:
    """Assesses a trained SAC agent on steady-state regulation, load transients,
    and generates diagnostic waveform plots."""

    def __init__(self, agent: SACAgent, circuit: CircuitParams):
        self.agent = agent
        self.circuit = circuit

    def evaluate_steady_state(self, n_steps: int = 2000) -> dict:
        """Run a steady-state evaluation and return regulation metrics.

        Parameters
        ----------
        n_steps : int
            Number of simulation steps to run.

        Returns
        -------
        dict
            Keys: ``vo_mean`` (V), ``vo_ripple_pct`` (%), ``vo_error_pct`` (%).
        """
        env = BuckCCMEnv(self.circuit)
        obs = env.reset()
        vo_history = []
        for _ in range(n_steps):
            action = self.agent.select_action(obs, evaluate=True)
            obs, _, done, _, info = env.step(action)
            vo_history.append(info["vo"])
            if done:
                break
        vos = np.array(vo_history[-500:])
        return {
            "vo_mean": float(np.mean(vos)),
            "vo_ripple_pct": float((np.max(vos) - np.min(vos)) / self.circuit.vout_ref * 100),
            "vo_error_pct": float(abs(np.mean(vos) - self.circuit.vout_ref) / self.circuit.vout_ref * 100),
        }

    def evaluate_load_transient(self, n_steps: int = 1000) -> dict:
        """Run a load-step test (R_load halved at midpoint) and measure
        overshoot / undershoot.

        Parameters
        ----------
        n_steps : int
            Total simulation steps.

        Returns
        -------
        dict
            Keys: ``overshoot_pct``, ``undershoot_pct``.
        """
        env = BuckCCMEnv(self.circuit)
        obs = env.reset()
        vo_history = []
        mid_point = n_steps // 2
        for i in range(n_steps):
            if i == mid_point:
                env.p.R_load *= 0.5  # Double the load
            action = self.agent.select_action(obs, evaluate=True)
            obs, _, done, _, info = env.step(action)
            vo_history.append(info["vo"])
            if done:
                break
        vos = np.array(vo_history)
        vout_ref = self.circuit.vout_ref
        post_step = vos[mid_point:mid_point + 100]
        overshoot = float(np.max(post_step) - vout_ref) / vout_ref * 100 if len(post_step) > 0 else 0
        undershoot = float(vout_ref - np.min(post_step)) / vout_ref * 100 if len(post_step) > 0 else 0
        return {"overshoot_pct": overshoot, "undershoot_pct": undershoot}

    def plot_waveforms(self, save_path: str):
        """Generate and save a three-panel waveform plot (Vo, iL, Duty).

        Parameters
        ----------
        save_path : str
            File path for the output PNG image.
        """
        env = BuckCCMEnv(self.circuit)
        obs = env.reset()
        vos, ils, ds = [], [], []
        for _ in range(1000):
            action = self.agent.select_action(obs, evaluate=True)
            obs, _, _, _, info = env.step(action)
            vos.append(info["vo"])
            ils.append(info["iL"])
            ds.append(info["d"])
        fig, axes = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
        axes[0].plot(vos)
        axes[0].set_ylabel("Vo (V)")
        axes[1].plot(ils)
        axes[1].set_ylabel("iL (A)")
        axes[2].plot(ds)
        axes[2].set_ylabel("Duty")
        axes[2].set_xlabel("Step")
        fig.savefig(save_path, dpi=150)
        plt.close(fig)
