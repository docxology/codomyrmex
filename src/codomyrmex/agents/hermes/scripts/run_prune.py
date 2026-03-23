#!/usr/bin/env python3
"""Hermes session pruning script.

Archives sessions older than N days (default: 30) and removes them from the
database.  Archived sessions are gzip-compressed JSON files in sessions_archive/
next to the database.

Usage::

    # Prune sessions older than 30 days
    uv run python -m codomyrmex.agents.hermes.scripts.run_prune

    # Prune sessions older than 7 days
    uv run python -m codomyrmex.agents.hermes.scripts.run_prune --days 7

    # Dry run — report how many would be pruned without deleting
    uv run python -m codomyrmex.agents.hermes.scripts.run_prune --dry-run --days 30

    # Custom DB path
    uv run python -m codomyrmex.agents.hermes.scripts.run_prune \\
        --db /path/to/hermes_sessions.db --days 14
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="run_prune",
        description="Archive and delete old Hermes sessions.",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="Prune sessions not updated within this many days (default: 30).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report how many sessions would be pruned without deleting them.",
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=None,
        help="Path to hermes_sessions.db (auto-discovers from ~/.codomyrmex/ if omitted).",
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Suppress informational output.",
    )
    return parser.parse_args()


def main() -> int:
    """Entry point."""
    args = _parse_args()

    from codomyrmex.agents.hermes.session import SQLiteSessionStore

    db_path = args.db or (Path.home() / ".codomyrmex" / "hermes_sessions.db")

    if not db_path.exists():
        if not args.quiet:
            print(
                f"No session database found at {db_path}. Nothing to prune.",
                file=sys.stderr,
            )
        return 0

    threshold = time.time() - (args.days * 86400)

    with SQLiteSessionStore(db_path) as store:
        if args.dry_run:
            # Count without deleting
            cursor = store._conn.execute(
                "SELECT COUNT(*) FROM hermes_sessions WHERE updated_at < ?",
                (threshold,),
            )
            count = cursor.fetchone()[0]
            stats = store.get_stats()
            print(
                f"Dry run: {count} session(s) would be pruned "
                f"(out of {stats['session_count']} total, db={stats['db_size_bytes']} bytes)."
            )
            return 0

        count = store.prune_old_sessions(days_old=args.days)
        if not args.quiet:
            stats = store.get_stats()
            print(
                f"Pruned {count} session(s) older than {args.days} days. "
                f"{stats['session_count']} session(s) remain."
            )

    return 0


if __name__ == "__main__":
    sys.exit(main())
