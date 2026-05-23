"""CLI entry point for manuscript_tracker workflow.

Usage:
    lanes-ceo --role manuscript_tracker --message "nature /path/to/project"
    lanes-ceo --role manuscript_tracker --message "ieee_tpe ./paper --article-type letter"
    lanes-ceo --role manuscript_tracker --message "science ./ --compare-journals nature"
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

logger = logging.getLogger("lanes_ceo.manuscript_tracker.cli")


def build_parser() -> argparse.ArgumentParser:
    """Build argument parser for manuscript_tracker CLI."""
    parser = argparse.ArgumentParser(
        prog="manuscript_tracker",
        description="投稿合规检查 — 检查 LaTeX 稿件是否符合目标期刊投稿要求",
    )

    parser.add_argument(
        "journal_key",
        help="目标期刊 key (nature, science, ieee_jssc, ieee_tpe)",
    )
    parser.add_argument(
        "project_dir",
        type=Path,
        help="LaTeX 项目目录路径",
    )
    parser.add_argument(
        "--main-file",
        type=str,
        default=None,
        help="主 .tex 文件名（默认自动检测 main.tex）",
    )
    parser.add_argument(
        "--article-type",
        type=str,
        default=None,
        help="文章类型 (如 letter, article, regular_paper)",
    )
    parser.add_argument(
        "--baseline",
        type=str,
        default=None,
        help="diff 比较基线 (如 git HEAD~1 或 某 .tex 文件)",
    )
    parser.add_argument(
        "--compare-journals",
        type=str,
        default=None,
        help="对比另一个期刊的 profile 差异 (如 nature vs science)",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="详细输出",
    )

    return parser


def parse_message(message: str) -> argparse.Namespace | None:
    """Try to parse a message string as CLI arguments.

    Returns Namespace with parsed args, or None if not a manuscript_tracker command.
    """

    # Split message, stripping leading whitespace
    parts = message.strip().split()
    if not parts:
        return None

    journal_key = parts[0]

    # Check if first word is a known journal
    known_prefixes = {"nature", "science", "ieee_jssc", "ieee_tpe", "jssc", "tpe", "ieee"}
    is_known = journal_key.lower() in known_prefixes

    # Also accept if message starts with a Path-like argument
    if not is_known:
        return None

    # Parse remaining parts
    remaining = parts[1:]
    args_list = [journal_key]

    for i, part in enumerate(remaining):
        part_lower = part.lower()
        if part_lower in ("--main-file",):
            args_list.append("--main-file")
            if i + 1 < len(remaining) and not remaining[i + 1].startswith("--"):
                args_list.append(remaining[i + 1])
            continue
        if part_lower in ("--article-type",):
            args_list.append("--article-type")
            if i + 1 < len(remaining) and not remaining[i + 1].startswith("--"):
                args_list.append(remaining[i + 1])
            continue
        if part_lower in ("--baseline",):
            args_list.append("--baseline")
            if i + 1 < len(remaining) and not remaining[i + 1].startswith("--"):
                args_list.append(remaining[i + 1])
            continue
        if part_lower in ("--compare-journals",):
            args_list.append("--compare-journals")
            if i + 1 < len(remaining) and not remaining[i + 1].startswith("--"):
                args_list.append(remaining[i + 1])
            continue
        if part_lower in ("--verbose", "-v"):
            args_list.append("--verbose")
            continue

    # Find the project_dir (first positional after journal_key that isn't a flag)
    for part in parts[1:]:
        if not part.startswith("--") and not part.startswith("-"):
            # Check if it's a value for a flag
            prev_idx = parts.index(part) - 1
            if prev_idx >= 1 and parts[prev_idx].startswith("--"):
                continue
            args_list.append(part)
            break

    parser = build_parser()
    try:
        parsed = parser.parse_args(args_list)
        return parsed
    except SystemExit:
        return None


def main(argv: list[str] | None = None) -> int:
    """CLI main entry point.

    Returns exit code (0 for pass, 1 for fail).
    """
    parser = build_parser()
    args = parser.parse_args(argv or sys.argv[1:])

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    from lanes_ceo.workflows.manuscript_tracker.engine import create_tracker

    # Comparison mode
    if args.compare_journals:
        from lanes_ceo.workflows.manuscript_tracker.profiles import ProfileLoader
        try:
            diffs = ProfileLoader.diff_profiles(args.journal_key, args.compare_journals)
            print(f"Profile comparison: {args.journal_key} vs {args.compare_journals}")
            if not diffs:
                print("  All fields are identical.")
            else:
                for d in diffs:
                    compat = "[compatible]" if d.get("compatible") else "[INCOMPATIBLE]"
                    print(f"  {d['field']}: {d['value_a']} vs {d['value_b']} {compat}")
            return 0
        except Exception as exc:
            print(f"Error comparing profiles: {exc}", file=sys.stderr)
            return 1

    # Full check mode
    tracker = create_tracker(
        journal_key=args.journal_key,
        project_dir=args.project_dir,
        main_file=args.main_file,
        article_type=args.article_type,
        baseline=args.baseline,
    )

    try:
        results = tracker.run_full_check()
        report_path = tracker.save_report(results)
    except FileNotFoundError as exc:
        logger.error("Project discovery failed: %s", exc)
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        logger.exception("Engine failure")
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if report_path:
        print(f"\nReport saved: {report_path}")

    failed = sum(1 for r in results if r.failed)
    return 1 if failed > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
