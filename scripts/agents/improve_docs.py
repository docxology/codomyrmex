#!/usr/bin/env python3
"""
improve_docs.py

Holistic Improvement Swarm Generator for docs/
Dispatches parallel jules agents to audit and optimize documentation.

Usage:
  ./improve_docs.py --dry-run
  ./improve_docs.py --limit 10
"""

import argparse
import subprocess
import sys
import time
from pathlib import Path

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DOCS_DIR = REPO_ROOT / "docs"
REPO_NAME = "docxology/codomyrmex"

DEFAULT_BATCH_SIZE = 8
DEFAULT_BATCH_DELAY = 10.0


def get_target_docs() -> list[Path]:
    """Find all top-level subdirectories and key docs in docs/."""
    targets = []
    if not DOCS_DIR.exists():
        logger.error(f"Docs directory not found: {DOCS_DIR}")
        return targets
        
    for item in DOCS_DIR.iterdir():
        if item.name.startswith("__"):
            continue
        if item.is_dir() or (item.is_file() and item.suffix == ".md"):
            targets.append(item)
    return sorted(targets)


def generate_prompt(target_path: Path) -> str:
    """Generate a specialized prompt for improving documentation."""
    target_name = target_path.name
    type_str = "directory" if target_path.is_dir() else "document"
    return (
        f"In `docs/{target_name}`, perform a holistic audit and architectural alignment of this {type_str}. "
        "Focus on: "
        "1. Ensuring absolute congruence with the structural realities of the live system codebase. "
        "2. Verify cross-referencing signposting (links between docs) is fully accurate and not broken. "
        "3. Eliminate 'thin' generic content. Replace it with dense, technically accurate architectural intelligence. "
        "4. Enforce that module-specific `README.md` and `AGENTS.md` exactly mirror their implementations in `src/codomyrmex/`. "
        "Proceed accurately and comprehensively to establish a perfect ground-truth reference."
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
    parser = argparse.ArgumentParser(description="Massive Parallel Improver for docs/")
    parser.add_argument("--dry-run", action="store_true", help="Preview tasks without dispatching")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE)
    parser.add_argument("--delay", type=float, default=DEFAULT_BATCH_DELAY)
    args = parser.parse_args()

    targets = get_target_docs()
    if not targets:
        logger.error("No docs found.")
        sys.exit(1)

    tasks = [{"target": t.name, "prompt": generate_prompt(t)} for t in targets]
    
    if args.limit:
        tasks = tasks[:args.limit]

    logger.info(f"Generated {len(tasks)} improvement tasks for docs/")

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
        batch = tasks[i:i + args.batch_size]
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

    print("\n" + "="*40)
    print(f"✅ docs/ Improvement Swarm Complete ({dispatched} dispatched)")


if __name__ == "__main__":
    main()
