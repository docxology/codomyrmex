#!/usr/bin/env python3
"""
Jules Mega Swarm v2 Dispatcher.

Dispatches up to 300 Jules coding agents from a tasks manifest file.
Supports batch control, dry-run, wave filtering, and progress tracking.

Usage:
    # Dry run — preview all tasks without dispatching
    uv run scripts/agents/jules/mega_swarm_v2_dispatcher.py --dry-run

    # Dispatch all tasks (260 agents)
    uv run scripts/agents/jules/mega_swarm_v2_dispatcher.py

    # Dispatch only a specific wave (e.g. Wave 1)
    uv run scripts/agents/jules/mega_swarm_v2_dispatcher.py --wave 1

    # Dispatch first N tasks only
    uv run scripts/agents/jules/mega_swarm_v2_dispatcher.py --limit 10

    # Custom batch size and delay
    uv run scripts/agents/jules/mega_swarm_v2_dispatcher.py --batch-size 10 --delay 5
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
TASKS_FILE = Path(__file__).resolve().parent / "swarm_tasks_v2.md"
TRACKING_FILE = Path(__file__).resolve().parent / "swarm_dispatch_log.json"
REPO_NAME = "docxology/codomyrmex"

DEFAULT_BATCH_SIZE = 8
DEFAULT_BATCH_DELAY = 3.0  # seconds between batches


def parse_tasks(filepath: Path) -> list[dict[str, str]]:
    """Parse the tasks manifest file into structured task records.

    Each non-empty, non-comment line is a task prompt.
    Lines starting with '# ===' are wave headers.
    Lines starting with '# ---' are module markers.

    Args:
        filepath: Path to the tasks manifest file.

    Returns:
        List of dicts with keys: wave, module, prompt, id.
    """
    tasks: list[dict[str, str]] = []
    current_wave = "Unknown"
    current_module = ""
    task_id = 0

    with filepath.open() as f:
        for line in f:
            stripped = line.strip()

            # Skip empty lines
            if not stripped:
                continue

            # Wave header: # WAVE N: DESCRIPTION (count agents)
            wave_match = re.match(
                r"^#\s+WAVE\s+(\d+):\s+(.+?)\s*\(\d+\s+agents?\)\s*$",
                stripped,
            )
            if wave_match:
                current_wave = f"Wave {wave_match.group(1)}: {wave_match.group(2).strip()}"
                continue

            # Module marker: # --- module_name ---
            module_match = re.match(r"^#\s+---\s+(\w+)\s+---\s*$", stripped)
            if module_match:
                current_module = module_match.group(1)
                continue

            # Skip other comment lines (headers, separators, metadata)
            if stripped.startswith("#"):
                continue

            # This is a task prompt
            task_id += 1
            tasks.append(
                {
                    "id": task_id,
                    "wave": current_wave,
                    "module": current_module,
                    "prompt": stripped,
                }
            )

    return tasks


def dispatch_jules(prompt: str, *, dry_run: bool = False) -> bool:
    """Dispatch a single Jules agent with the given prompt.

    Args:
        prompt: The task prompt to send to Jules.
        dry_run: If True, only print the task without dispatching.

    Returns:
        True if dispatch succeeded (or dry_run), False on error.
    """
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
        print("❌ 'jules' CLI not found. Is it installed?", file=sys.stderr)
        return False
    except OSError as e:
        print(f"❌ OS error dispatching agent: {e}", file=sys.stderr)
        return False


def save_dispatch_log(
    dispatched: list[dict[str, str]],
    filepath: Path,
) -> None:
    """Save the dispatch log as JSON for tracking.

    Args:
        dispatched: List of dispatched task records.
        filepath: Path where the log JSON will be saved.
    """
    log = {
        "dispatched_at": datetime.now(tz=timezone.utc).isoformat(),
        "total_agents": len(dispatched),
        "repo": REPO_NAME,
        "tasks": dispatched,
    }
    filepath.write_text(json.dumps(log, indent=2))
    print(f"\n📝 Dispatch log saved to: {filepath}")


def main() -> None:
    """Entry point for the mega swarm v2 dispatcher."""
    parser = argparse.ArgumentParser(
        description="Jules Mega Swarm v2 Dispatcher — dispatch up to 300 agents",
    )
    parser.add_argument(
        "--tasks-file",
        type=Path,
        default=TASKS_FILE,
        help="Path to the tasks manifest file",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview tasks without dispatching",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Maximum number of agents to dispatch",
    )
    parser.add_argument(
        "--wave",
        type=int,
        default=None,
        help="Only dispatch tasks from this wave number",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=DEFAULT_BATCH_SIZE,
        help=f"Agents per batch (default: {DEFAULT_BATCH_SIZE})",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=DEFAULT_BATCH_DELAY,
        help=f"Seconds between batches (default: {DEFAULT_BATCH_DELAY})",
    )
    parser.add_argument(
        "--start-from",
        type=int,
        default=1,
        help="Start dispatching from this task ID (skip earlier tasks)",
    )

    args = parser.parse_args()

    if not args.tasks_file.exists():
        print(f"❌ Tasks file not found: {args.tasks_file}", file=sys.stderr)
        sys.exit(1)

    # Parse all tasks
    all_tasks = parse_tasks(args.tasks_file)
    print(f"📋 Parsed {len(all_tasks)} tasks from {args.tasks_file.name}")

    # Filter by wave if specified
    if args.wave is not None:
        wave_prefix = f"Wave {args.wave}:"
        all_tasks = [t for t in all_tasks if t["wave"].startswith(wave_prefix)]
        print(f"🔍 Filtered to Wave {args.wave}: {len(all_tasks)} tasks")

    # Filter by start-from
    if args.start_from > 1:
        all_tasks = [t for t in all_tasks if t["id"] >= args.start_from]
        print(f"⏩ Starting from task #{args.start_from}: {len(all_tasks)} tasks remaining")

    # Apply limit
    if args.limit is not None:
        all_tasks = all_tasks[: args.limit]
        print(f"🔢 Limited to {args.limit} agents")

    if not all_tasks:
        print("⚠️  No tasks match the filters. Nothing to dispatch.")
        sys.exit(0)

    # Print summary by wave
    wave_counts: dict[str, int] = {}
    for task in all_tasks:
        wave_counts[task["wave"]] = wave_counts.get(task["wave"], 0) + 1

    print("\n📊 Dispatch Plan:")
    print("─" * 60)
    for wave, count in wave_counts.items():
        print(f"  {wave}: {count} agents")
    print("─" * 60)
    print(f"  Total: {len(all_tasks)} agents")
    print()

    if args.dry_run:
        print("🔍 DRY RUN — Previewing tasks:\n")
        for task in all_tasks:
            print(f"  [{task['id']:3d}] [{task['wave']}]")
            prompt_preview = task["prompt"][:120] + ("..." if len(task["prompt"]) > 120 else "")
            print(f"       {prompt_preview}")
            print()
        print(f"\n✅ Dry run complete. {len(all_tasks)} tasks would be dispatched.")
        save_dispatch_log(all_tasks, TRACKING_FILE)
        return

    # Dispatch in batches
    print(f"🚀 Dispatching {len(all_tasks)} Jules agents in batches of {args.batch_size}...")
    dispatched: list[dict[str, str]] = []
    failed = 0

    for i in range(0, len(all_tasks), args.batch_size):
        batch = all_tasks[i : i + args.batch_size]
        batch_num = i // args.batch_size + 1
        total_batches = (len(all_tasks) + args.batch_size - 1) // args.batch_size

        print(f"\n── Batch {batch_num}/{total_batches} ({len(batch)} agents) ──")

        for task in batch:
            success = dispatch_jules(task["prompt"])
            if success:
                dispatched.append(task)
                print(f"  ✅ [{task['id']:3d}] {task['module'] or 'cross-cutting'}")
            else:
                failed += 1
                print(f"  ❌ [{task['id']:3d}] FAILED — {task['module'] or 'cross-cutting'}")

        # Wait between batches (not after the last one)
        if i + args.batch_size < len(all_tasks):
            print(f"  ⏳ Waiting {args.delay}s before next batch...")
            time.sleep(args.delay)

    # Summary
    print("\n" + "═" * 60)
    print(f"✅ Mega Swarm v2 Dispatch Complete")
    print(f"   Dispatched: {len(dispatched)}")
    print(f"   Failed:     {failed}")
    print(f"   Total:      {len(all_tasks)}")
    print("═" * 60)
    print("\n📡 Monitor: jules remote list --session")
    print("📥 Apply:   jules remote pull --session <ID> --apply")

    # Save tracking log
    save_dispatch_log(dispatched, TRACKING_FILE)


if __name__ == "__main__":
    main()
