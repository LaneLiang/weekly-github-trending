import csv
import json
from pathlib import Path
from datetime import datetime


class TrainingLogger:
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.run_dir = self.log_dir / timestamp
        self.run_dir.mkdir(exist_ok=True)
        self.csv_path = self.run_dir / "metrics.csv"
        self._init_csv()

    def _init_csv(self):
        with open(self.csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "episode", "avg_reward", "vo_ripple", "vo_error",
                "recovery_time", "overshoot", "undershoot",
                "critic_loss", "actor_loss", "alpha"
            ])

    def log_episode(self, metrics: dict):
        with open(self.csv_path, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                metrics.get("episode", 0),
                metrics.get("avg_reward", 0),
                metrics.get("vo_ripple", 0),
                metrics.get("vo_error", 0),
                metrics.get("recovery_time", 0),
                metrics.get("overshoot", 0),
                metrics.get("undershoot", 0),
                metrics.get("critic_loss", 0),
                metrics.get("actor_loss", 0),
                metrics.get("alpha", 0),
            ])

    def save_llm_intervention(self, episode: int, result: dict):
        path = self.run_dir / f"llm_intervention_{episode:06d}.json"
        with open(path, "w") as f:
            json.dump(result, f, indent=2, default=str)
