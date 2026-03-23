#!/usr/bin/env python3
"""
improve_src.py

Holistic Improvement Swarm Generator for src/codomyrmex/
Dispatches massive parallel jules agents to improve the core modules.

Usage:
  ./improve_src.py --dry-run
  ./improve_src.py --limit 10
  ./improve_src.py --batch-size 10 --delay 5
"""

import argparse
import subprocess
import sys
import time
from pathlib import Path

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SRC_DIR = REPO_ROOT / "src" / "codomyrmex"
REPO_NAME = "docxology/codomyrmex"

DEFAULT_BATCH_SIZE = 8
DEFAULT_BATCH_DELAY = 10.0


def get_core_modules() -> list[Path]:
    """Find all functional module directories in src/codomyrmex/."""
    modules = []
    if not SRC_DIR.exists():
        logger.error(f"Source directory not found: {SRC_DIR}")
        return modules

    for item in SRC_DIR.iterdir():
        if (
            item.is_dir()
            and not item.name.startswith("__")
            and item.name not in ("tests", "examples", "docs")
        ):
            modules.append(item)
    return sorted(modules)


def generate_prompt(module_path: Path) -> str:
    """Generate a specialized prompt for improving a core module."""
    module_name = module_path.name
    return (
        f"In `src/codomyrmex/{module_name}/`, perform a holistic architectural and AGI capability improvement. "
        "Focus on: "
        "1. Ensuring absolutely strict zero-mock testing compliance with >= 35% coverage. "
        "2. Expose any relevant sub-functions natively as MCP tools via `@mcp_tool` where valuable. "
        "3. Improve inter-agent skill interoperability. "
        "4. Eliminate any accumulated technical debt or complex cyclomatic chains (Desloppify). "
        "5. Ensure docstrings strictly match the implementations, aligning with `AGENTS.md` and `README.md`. "
        "Proceed accurately and comprehensively. Build real, tested functionality."
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
        logger.error(f"OS error dispatching: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Massive Parallel Improver for src/")
    parser.add_argument(
        "--dry-run", action="store_true", help="Preview tasks without dispatching"
    )
    parser.add_argument(
        "--limit", type=int, default=None, help="Max agents to dispatch"
    )
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE)
    parser.add_argument("--delay", type=float, default=DEFAULT_BATCH_DELAY)
    args = parser.parse_args()

    modules = get_core_modules()
    if not modules:
        logger.error("No modules found.")
        sys.exit(1)

    tasks = [{"module": m.name, "prompt": generate_prompt(m)} for m in modules]

    if args.limit:
        tasks = tasks[: args.limit]

    logger.info(f"Generated {len(tasks)} improvement tasks for src/codomyrmex/")

    if args.dry_run:
        print("\n--- DRY RUN PREVIEW ---")
        for i, t in enumerate(tasks, 1):
            print(f"[{i}] Module: {t['module']}")
            print(f"    Prompt: {t['prompt']}\n")
        sys.exit(0)

    dispatched = 0
    failed = 0

    print(
        f"🚀 Dispatching {len(tasks)} Jules agents in batches of {args.batch_size}..."
    )
    for i in range(0, len(tasks), args.batch_size):
        batch = tasks[i : i + args.batch_size]
        print(f"\n── Batch {i // args.batch_size + 1} ({len(batch)} agents) ──")

        for task in batch:
            if dispatch_agent(task["prompt"], args.dry_run):
                dispatched += 1
                print(f"  ✅ Dispatched -> {task['module']}")
            else:
                failed += 1
                print(f"  ❌ Failed dispatch -> {task['module']}")

        if i + args.batch_size < len(tasks):
            print(f"  ⏳ Waiting {args.delay}s...")
            time.sleep(args.delay)

    print("\n" + "=" * 40)
    print("✅ src/ Improvement Swarm Complete")
    print(f"   Success: {dispatched}")
    print(f"   Failed:  {failed}")
    print("Monitor with: jules remote list --session")


if __name__ == "__main__":
    main()
