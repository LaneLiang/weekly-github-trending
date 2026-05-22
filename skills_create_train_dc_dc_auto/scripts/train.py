#!/usr/bin/env python3
"""CLI entry point for DC-DC auto-tune training."""
import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dc_auto_tune.utils.config import load_config
from dc_auto_tune.train.trainer import Trainer


def main():
    parser = argparse.ArgumentParser(description="DC-DC Auto Tune Trainer")
    parser.add_argument(
        "--config",
        default="dc_auto_tune/configs/default.yaml",
        help="Path to YAML config file",
    )
    parser.add_argument(
        "--api-key",
        default=os.getenv("OPENAI_API_KEY"),
        help="LLM API key (or set OPENAI_API_KEY env var)",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    trainer = Trainer(config, api_key=args.api_key)
    trainer.train()
    print(f"Training complete. {trainer.llm_call_count} LLM interventions made.")
    print(f"Logs saved to: {trainer.logger.run_dir}")


if __name__ == "__main__":
    main()
