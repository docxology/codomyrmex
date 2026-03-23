#!/usr/bin/env python3
"""
improve_scripts.py

Holistic Improvement Swarm Generator for scripts/
Dispatches parallel jules agents to optimize the automation layer.

Usage:
  ./improve_scripts.py --dry-run
  ./improve_scripts.py --limit 5
"""

import argparse
import subprocess
import sys
import time
from pathlib import Path

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
REPO_NAME = "docxology/codomyrmex"

DEFAULT_BATCH_SIZE = 5
DEFAULT_BATCH_DELAY = 10.0


def get_target_scripts() -> list[Path]:
    """Find all top-level subdirectories and key scripts in scripts/."""
    targets = []
    if not SCRIPTS_DIR.exists():
        logger.error(f"Scripts directory not found: {SCRIPTS_DIR}")
        return targets

    for item in SCRIPTS_DIR.iterdir():
        if item.name.startswith("__") or item.name == "node_modules":
            continue
        if item.is_dir() or (item.is_file() and item.suffix in {".sh", ".py"}):
            targets.append(item)
    return sorted(targets)


def generate_prompt(target_path: Path) -> str:
    """Generate a specialized prompt for improving scripts."""
    target_name = target_path.name
    type_str = "directory" if target_path.is_dir() else "script"
    return (
        f"In `scripts/{target_name}`, perform a holistic architectural review of this automation {type_str}. "
        "Focus on: "
        "1. Ensuring the scripts act as 'thin orchestration layers'. Remove heavy business logic and push it into `src/codomyrmex` modules if applicable. "
        "2. Make scripts bulletproof: add clear argument parsing, standardized logging (using Codomyrmex logger), and rigorous error handling. "
        "3. Standardize execution context (e.g. `uv run`, correct bash `set -euo pipefail`). "
        "4. Align documentation to ensure `README.md` and `AGENTS.md` accurately reflect script usage and constraints. "
        "Proceed accurately and comprehensively to maximize reliable operational leverage."
    )


def dispatch_agent(prompt: str, dry_run: bool) -> bool:
    if dry_run:
        return True
    try:
        subprocess.Popen(
            ["jules", "new", "--repo", REPO_NAME, prompt],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return True
    except FileNotFoundError:
        logger.error("'jules' CLI not found.")
        return False
    except OSError as e:
        logger.error(f"OS error: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Massive Parallel Improver for scripts/"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Preview tasks without dispatching"
    )
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE)
    parser.add_argument("--delay", type=float, default=DEFAULT_BATCH_DELAY)
    args = parser.parse_args()

    targets = get_target_scripts()
    if not targets:
        logger.error("No scripts found.")
        sys.exit(1)

    tasks = [{"target": t.name, "prompt": generate_prompt(t)} for t in targets]

    if args.limit:
        tasks = tasks[: args.limit]

    logger.info(f"Generated {len(tasks)} improvement tasks for scripts/")

    if args.dry_run:
        print("\n--- DRY RUN PREVIEW ---")
        for i, t in enumerate(tasks, 1):
            print(f"[{i}] Target: {t['target']}")
            print(f"    Prompt: {t['prompt']}\n")
        sys.exit(0)

    dispatched = 0
    failed = 0

    print(f"🚀 Dispatching {len(tasks)} Jules agents...")
    for i in range(0, len(tasks), args.batch_size):
        batch = tasks[i : i + args.batch_size]
        print(f"\n── Batch {i // args.batch_size + 1} ──")

        for task in batch:
            if dispatch_agent(task["prompt"], args.dry_run):
                dispatched += 1
                print(f"  ✅ Dispatched -> {task['target']}")
            else:
                failed += 1
                print(f"  ❌ Failed -> {task['target']}")

        if i + args.batch_size < len(tasks):
            time.sleep(args.delay)

    print("\n" + "=" * 40)
    print(f"✅ scripts/ Improvement Swarm Complete ({dispatched} dispatched)")


if __name__ == "__main__":
    main()
