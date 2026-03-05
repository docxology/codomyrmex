"""demo_jules_swarm.py — Jules parallel swarm dispatch demonstration.

Parses open TODO items from TODO.md and dispatches them as a Jules CLI swarm
using ``julius new --repo <repo> --parallel <N>``.

Usage::

    # Preview tasks without calling Jules (no auth needed):
    uv run python scripts/demos/demo_jules_swarm.py --dry-run

    # Run full swarm (requires jules CLI + authentication):
    uv run python scripts/demos/demo_jules_swarm.py \\
        --repo danielmiessler/codomyrmex \\
        --parallel 100

    # Only dispatch CRITICAL priority items:
    uv run python scripts/demos/demo_jules_swarm.py \\
        --repo danielmiessler/codomyrmex \\
        --priority CRITICAL \\
        --dry-run
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    repo_root = Path(__file__).resolve().parent.parent.parent
    default_todo = repo_root / "TODO.md"

    parser = argparse.ArgumentParser(
        description="Dispatch a Jules parallel swarm for all open TODO items.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--todo",
        type=Path,
        default=default_todo,
        help="Path to TODO.md (default: repo root TODO.md)",
    )
    parser.add_argument(
        "--repo",
        default="",
        help="GitHub slug or local path (e.g. 'owner/repo'). Required unless --dry-run.",
    )
    parser.add_argument(
        "--parallel",
        type=int,
        default=100,
        help="Jules --parallel value per batch (default: 100)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=10,
        dest="batch_size",
        help="Tasks per Jules invocation (default: 10)",
    )
    parser.add_argument(
        "--priority",
        default="",
        help="Filter to a priority section keyword, e.g. 'CRITICAL' or 'HIGH'.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        dest="dry_run",
        help="Print parsed tasks without calling Jules.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if not args.dry_run and not args.repo:
        print("ERROR: --repo is required unless --dry-run is set.", file=sys.stderr)
        return 1

    if not args.todo.exists():
        print(f"ERROR: TODO file not found: {args.todo}", file=sys.stderr)
        return 1

    try:
        from codomyrmex.agents.jules import JulesClient, JulesSwarmDispatcher
    except ImportError as exc:
        print(f"ERROR: Could not import jules module: {exc}", file=sys.stderr)
        print("Run: uv sync", file=sys.stderr)
        return 1

    client = JulesClient()
    dispatcher = JulesSwarmDispatcher.from_todo_md(
        client=client,
        repo=args.repo,
        todo_path=args.todo,
        priority_filter=args.priority or None,
    )

    task_count = len(dispatcher.tasks)
    batch_count = (task_count + args.batch_size - 1) // args.batch_size if task_count else 0

    print("Jules Swarm Dispatcher")
    print(f"  TODO file  : {args.todo}")
    print(f"  Repo       : {args.repo or '(not set — dry run)'}")
    print(f"  Priority   : {args.priority or 'ALL'}")
    print(f"  Tasks found: {task_count}")
    print(f"  Batches    : {batch_count} × {args.batch_size} tasks")
    print(f"  Parallel   : {args.parallel} agents/batch")
    print()

    if task_count == 0:
        print("No open TODO items found. Nothing to dispatch.")
        return 0

    if args.dry_run:
        print("--- DRY RUN — tasks that would be dispatched ---")
        for i, task in enumerate(dispatcher.tasks, 1):
            print(f"  {i:3}. {task}")
        print()
        print(f"[dry-run] Would dispatch {task_count} tasks in {batch_count} batch(es).")
        return 0

    # Check jules availability before dispatching
    help_info = client.get_jules_help()
    if not help_info.get("available"):
        print("ERROR: Jules CLI not found. Install via your Jules account.", file=sys.stderr)
        print("  Hint: ensure 'jules' (or 'julius') is in PATH and authenticated.", file=sys.stderr)
        return 1

    print(f"Dispatching {task_count} tasks across {batch_count} batches...")
    responses = dispatcher.dispatch(parallel=args.parallel, batch_size=args.batch_size)

    success_count = sum(1 for r in responses if r.is_success())
    fail_count = len(responses) - success_count

    print()
    print(f"Swarm complete: {success_count}/{len(responses)} batches succeeded.")
    if fail_count:
        print(f"  {fail_count} batch(es) failed — check logs for details.")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
