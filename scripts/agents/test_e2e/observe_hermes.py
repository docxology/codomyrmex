#!/usr/bin/env python3
"""Hermes Agent — Thin Orchestrator Observability Script.

Reads the persistent SQLite session database and telemetry to provide
an interpretability view of recent Hermes agent executions.

Usage:
    python scripts/agents/hermes/observe_hermes.py
    python scripts/agents/hermes/observe_hermes.py --limit 5
    python scripts/agents/hermes/observe_hermes.py --limit 10 --db-path /custom/path.db
"""

import argparse
import sys
from pathlib import Path

# Bootstrap path only — not needed when package is already installed
try:
    from codomyrmex.agents.core.config import get_config
except ImportError:
    sys.path.insert(
        0, str(Path(__file__).resolve().parent.parent.parent.parent / "src")
    )
    from codomyrmex.agents.core.config import get_config

from codomyrmex.utils.cli_helpers import (
    print_error,
    print_info,
    print_success,
    setup_logging,
)

# ── Module-level constants (overridden by hermes.yaml / CLI args) ──────
_DEFAULT_LIMIT: int = 5

# Repo-relative telemetry config path (resolved once at module load)
_REPO_ROOT: Path = Path(__file__).resolve().parent.parent.parent.parent
_HERMES_CONFIG_PATH: Path = _REPO_ROOT / "config" / "agents" / "hermes.yaml"


def _resolve_config() -> dict:
    """Load agent config and extract Hermes-specific settings.

    Returns:
        Flat dict of effective hermes config values.
    """
    try:
        config = get_config()
        return config.get("hermes", {}) if isinstance(config, dict) else {}
    except (OSError, ValueError):
        return {}


def _resolve_db_path(
    cli_override: str | None,
    config_path: str | None,
    client_default: str,
) -> Path:
    """Resolve session database path with 3-level priority.

    Priority: CLI --db-path > hermes.yaml session_db > HermesClient default.

    Args:
        cli_override: Value of --db-path argument (may be None).
        config_path: Path from hermes.yaml session_db (may be None).
        client_default: Fallback path from HermesClient._session_db_path.

    Returns:
        Resolved, expanded absolute Path to the SQLite database.
    """
    raw: str = cli_override or config_path or client_default
    return Path(raw).expanduser().resolve()


def _load_sorted_sessions(store: object, limit: int) -> list:
    """Load all sessions from the store, sorted newest-first, capped at *limit*.

    Args:
        store: An open SQLiteSessionStore context-manager.
        limit: Maximum number of sessions to return.

    Returns:
        List of session objects, most-recent first.
    """
    session_ids: list[str] = store.list_sessions()  # type: ignore[attr-defined]
    all_sessions: list = []
    for sid in session_ids:
        sess = store.load(sid)  # type: ignore[attr-defined]
        if sess:
            all_sessions.append(sess)
    all_sessions.sort(key=lambda s: s.updated_at, reverse=True)
    return all_sessions[:limit]


def _print_session(index: int, session: object) -> None:
    """Display a clean summary of a single Hermes session.

    Args:
        index: 1-based position in the displayed list.
        session: A session object loaded from SQLiteSessionStore.
    """
    name_label = f" — {session.name}" if getattr(session, "name", None) else ""  # type: ignore[attr-defined]
    print_success(f"[{index}] Session: {session.session_id}{name_label}")  # type: ignore[attr-defined]
    print_info(f"    Created:  {session.created_at}")  # type: ignore[attr-defined]
    turns: int = session.message_count // 2  # type: ignore[attr-defined]
    print_info(f"    Turns:    {turns} (Total messages: {session.message_count})")  # type: ignore[attr-defined]

    if session.metadata:  # type: ignore[attr-defined]
        print_info(f"    Traces:   {session.metadata}")  # type: ignore[attr-defined]

    if session.message_count > 0:  # type: ignore[attr-defined]
        first_content: str = session.messages[0]["content"]  # type: ignore[attr-defined]
        preview: str = (
            first_content[:60] + "..." if len(first_content) > 60 else first_content
        )
        print_info(f"    Initial Prompt: {preview}")

    print_info("")


def main() -> int:
    hermes_cfg = _resolve_config()
    log_level: str = hermes_cfg.get("observability", {}).get("log_level", "INFO")
    config_db_path: str | None = hermes_cfg.get("session_db")

    parser = argparse.ArgumentParser(description="Hermes Agent Observability")
    parser.add_argument(
        "--limit",
        type=int,
        default=_DEFAULT_LIMIT,
        help=f"Number of recent sessions to view (default: {_DEFAULT_LIMIT})",
    )
    parser.add_argument(
        "--db-path",
        type=str,
        default=None,
        help="Override path to the SQLite session database (default from hermes.yaml).",
    )
    parser.add_argument(
        "--search",
        type=str,
        default=None,
        help="Filter sessions by name substring (v0.2.0 named sessions).",
    )
    args = parser.parse_args()

    setup_logging(level=log_level)
    print_info("═" * 60)
    print_info(f"  Hermes Agent — Observability (Last {args.limit} Sessions)")
    print_info("═" * 60)

    # Import Hermes modules — fail fast if unavailable (ImportError is a structural issue,
    # not a runtime edge case; surfacing it explicitly helps developers debug broken installs).
    try:
        from codomyrmex.agents.hermes.hermes_client import HermesClient
        from codomyrmex.agents.hermes.session import SQLiteSessionStore
    except ImportError as exc:
        print_error(f"Required Hermes modules unavailable: {exc}")
        print_error("  Ensure codomyrmex package is installed: uv sync")
        return 1

    hermes_client: HermesClient = HermesClient()  # type: ignore

    # Priority: --db-path CLI > hermes.yaml session_db > client default
    db_path: Path = _resolve_db_path(
        args.db_path,
        config_db_path,
        hermes_client._session_db_path,  # type: ignore[attr-defined]
    )

    if not db_path.exists():
        print_error(f"Session database not found at {db_path}.")
        print_info("  (Run 'run_hermes.py' first to create it.)")
        return 1

    # Report telemetry config detection
    if _HERMES_CONFIG_PATH.exists():
        print_info(f"Telemetry settings detected in {_HERMES_CONFIG_PATH.name}.")

    with SQLiteSessionStore(str(db_path)) as store:
        # If --search is provided, filter by name substring (v0.2.0)
        if args.search:
            matches = store.search_sessions(args.search)  # type: ignore[attr-defined]
            if not matches:
                print_info(f"No sessions matching '{args.search}'.")
                return 0
            print_success(f"Found {len(matches)} session(s) matching '{args.search}':")
            print_info("─" * 60)
            for i, match in enumerate(matches[: args.limit], 1):
                sess = store.load(match["session_id"])  # type: ignore[attr-defined]
                if sess:
                    _print_session(i, sess)
        else:
            sessions = _load_sorted_sessions(store, args.limit)

            if not sessions:
                print_info("No execution histories found.")
                return 0

            total_available = len(store.list_sessions())  # type: ignore[attr-defined]
            print_success(f"Total historical sessions recorded: {total_available}")
            print_info("─" * 60)

            for i, session in enumerate(sessions, 1):
                _print_session(i, session)

    print_info("─" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
