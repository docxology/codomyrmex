#!/usr/bin/env python3
"""Hermes session export script.

Exports one or more Hermes sessions to Markdown files (or stdout).

Usage::

    # List all session IDs
    uv run python -m codomyrmex.agents.hermes.scripts.run_session_export --list

    # Export a specific session to stdout
    uv run python -m codomyrmex.agents.hermes.scripts.run_session_export --session-id abc123

    # Export to a file
    uv run python -m codomyrmex.agents.hermes.scripts.run_session_export \\
        --session-id abc123 --output session.md

    # Export ALL sessions to a directory
    uv run python -m codomyrmex.agents.hermes.scripts.run_session_export --all --dir ./exports
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="run_session_export",
        description="Export Hermes sessions to Markdown.",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--list", action="store_true", help="List all session IDs.")
    group.add_argument("--session-id", metavar="ID", help="Export a single session.")
    group.add_argument("--all", action="store_true", help="Export ALL sessions.")

    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=None,
        help="Output file for single-session export (stdout if omitted).",
    )
    parser.add_argument(
        "--dir",
        "-d",
        type=Path,
        default=Path("hermes_exports"),
        help="Output directory for --all exports (default: ./hermes_exports).",
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=None,
        help="Path to hermes_sessions.db (auto-discovers from ~/.codomyrmex/ if omitted).",
    )
    return parser.parse_args()


def _get_store(db_path: Path | None):
    from pathlib import Path as _Path

    from codomyrmex.agents.hermes.session import SQLiteSessionStore

    if db_path:
        return SQLiteSessionStore(db_path)
    default = _Path.home() / ".codomyrmex" / "hermes_sessions.db"
    return SQLiteSessionStore(default)


def main() -> int:
    """Entry point."""
    args = _parse_args()

    store = _get_store(args.db)

    try:
        if args.list:
            ids = store.list_sessions()
            if not ids:
                print("No sessions found.", file=sys.stderr)
                return 0
            for sid in ids:
                detail = store.get_detail(sid)
                name = detail.get("name") or "(unnamed)" if detail else "(unknown)"
                msg_count = detail.get("message_count", "?") if detail else "?"
                print(f"{sid}  {name}  ({msg_count} messages)")
            return 0

        if args.session_id:
            md = store.export_markdown(args.session_id)
            if md is None:
                print(f"Error: session {args.session_id!r} not found.", file=sys.stderr)
                return 1
            if args.output:
                args.output.write_text(md, encoding="utf-8")
                print(f"Written to {args.output}", file=sys.stderr)
            else:
                print(md)
            return 0

        if args.all:
            ids = store.list_sessions()
            if not ids:
                print("No sessions to export.", file=sys.stderr)
                return 0
            args.dir.mkdir(parents=True, exist_ok=True)
            exported = 0
            for sid in ids:
                md = store.export_markdown(sid)
                if md:
                    out = args.dir / f"{sid}.md"
                    out.write_text(md, encoding="utf-8")
                    exported += 1
            print(f"Exported {exported} sessions to {args.dir}/", file=sys.stderr)
            return 0

    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    finally:
        store.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
