"""Hermes MCP tools — sessions category."""
from __future__ import annotations

from typing import Any

from codomyrmex.agents.hermes.mcp_tools_pkg._client import _get_client
from codomyrmex.model_context_protocol.decorators import mcp_tool


@mcp_tool(
    category="hermes",
    description="list all active persistent Hermes session IDs.",
)
def hermes_session_list() -> dict[str, Any]:
    """list available Hermes session IDs.

    Returns:
        dict with keys: status, sessions (list of str), count

    """
    try:
        from codomyrmex.agents.hermes.session import SQLiteSessionStore

        client = _get_client()
        with SQLiteSessionStore(client._session_db_path) as store:
            sessions = store.list_sessions()
            return {"status": "success", "sessions": sessions, "count": len(sessions)}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}

@mcp_tool(
    category="hermes",
    description="Clear a specific Hermes chat session by ID.",
)
def hermes_session_clear(session_id: str) -> dict[str, Any]:
    """Delete a Hermes session.

    Args:
        session_id: ID of the session to delete.

    Returns:
        dict with keys: status, deleted, message

    """
    try:
        from codomyrmex.agents.hermes.session import SQLiteSessionStore

        client = _get_client()
        with SQLiteSessionStore(client._session_db_path) as store:
            deleted = store.delete(session_id)
            return {
                "status": "success",
                "deleted": deleted,
                "message": f"Deleted session {session_id}"
                if deleted
                else f"Session {session_id} not found.",
            }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}

@mcp_tool(
    category="hermes",
    description=(
        "Return summary statistics about the Hermes session database: "
        "session count, disk size, and timestamps of oldest and newest sessions."
    ),
)
def hermes_session_stats() -> dict[str, Any]:
    """Get Hermes session database statistics.

    Returns:
        dict with keys: status, session_count, db_size_bytes,
        oldest_session_at, newest_session_at

    """
    try:
        client = _get_client()
        stats = client.get_session_stats()
        return {"status": "success", **stats}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}

@mcp_tool(
    category="hermes",
    description=(
        "Fork an existing Hermes session into an independent child session. "
        "The child inherits the full message history and can diverge independently."
    ),
)
def hermes_session_fork(
    session_id: str,
    new_name: str | None = None,
) -> dict[str, Any]:
    """Fork a Hermes session.

    Args:
        session_id: Source session to fork.
        new_name: Optional name for the child session.

    Returns:
        dict with keys: status, child_session_id, name, parent_session_id

    """
    try:
        client = _get_client()
        child = client.fork_session(session_id, new_name=new_name)
        if child is None:
            return {"status": "error", "message": f"Session {session_id!r} not found"}
        return {
            "status": "success",
            "child_session_id": child.session_id,
            "name": child.name,
            "parent_session_id": child.parent_session_id,
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}

@mcp_tool(
    category="hermes",
    description=(
        "Export a Hermes session as formatted Markdown text. "
        "Useful for archiving conversations or sharing context with other agents."
    ),
)
def hermes_session_export_md(session_id: str) -> dict[str, Any]:
    """Export a Hermes session as Markdown.

    Args:
        session_id: Session to export.

    Returns:
        dict with keys: status, markdown, session_id

    """
    try:
        client = _get_client()
        md = client.export_session_markdown(session_id)
        if md is None:
            return {"status": "error", "message": f"Session {session_id!r} not found"}
        return {"status": "success", "session_id": session_id, "markdown": md}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}

@mcp_tool(
    category="hermes",
    description=(
        "Retrieve full detail about a specific Hermes session, including "
        "message count, last message, system prompt flag, and all metadata."
    ),
)
def hermes_session_detail(session_id: str) -> dict[str, Any]:
    """Get detailed information about a Hermes session.

    Args:
        session_id: Session to describe.

    Returns:
        dict with keys: status, session_id, name, message_count, last_message,
        has_system_prompt, metadata, created_at, updated_at

    """
    try:
        client = _get_client()
        detail = client.get_session_detail(session_id)
        if detail is None:
            return {"status": "error", "message": f"Session {session_id!r} not found"}
        return {"status": "success", **detail}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}

@mcp_tool(
    category="hermes",
    description=(
        "Merge multiple source sessions into a destination session. "
        "Useful for consolidating research or combining context from parallel tasks."
    ),
)
def hermes_session_merge(
    target_id: str,
    source_ids: list[str],
    deduplicate: bool = True,
) -> dict[str, Any]:
    """Consolidate multiple sessions into one.

    Args:
        target_id: Destination session ID (created if missing).
        source_ids: list of session IDs to pull messages from.
        deduplicate: Skip exact back-to-back duplicates (default True).

    Returns:
        dict with status, message

    """
    try:
        client = _get_client()
        ok = client.session_merge(target_id, source_ids, deduplicate=deduplicate)
        return {
            "status": "success" if ok else "error",
            "message": f"Merged sources into {target_id}"
            if ok
            else "Merge failed or no sessions found",
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}

@mcp_tool(
    category="hermes",
    description=(
        "Archive and delete Hermes sessions older than the specified number of days. "
        "Archived sessions are gzip-compressed and saved to sessions_archive/ next to the DB."
    ),
)
def hermes_prune_sessions(days_old: int = 30) -> dict[str, Any]:
    """Archive and prune old Hermes sessions.

    Args:
        days_old: Remove sessions not updated within this many days (default 30).

    Returns:
        dict with keys: status, pruned_count, message

    """
    try:
        from codomyrmex.agents.hermes.session import SQLiteSessionStore

        client = _get_client()
        with SQLiteSessionStore(client._session_db_path) as store:
            count = store.prune_old_sessions(days_old=days_old)
        return {
            "status": "success",
            "pruned_count": count,
            "message": f"Archived and deleted {count} sessions older than {days_old} days.",
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}

@mcp_tool(
    category="hermes",
    description=(
        "Archive and prune Hermes sessions when the database exceeds a size threshold. "
        "Sessions are compressed to .json.gz files in a sessions_archive/ directory "
        "adjacent to the DB, then removed from SQLite to keep the store lean. "
        "set dry_run=True to see what would be pruned without deleting anything."
    ),
)
def hermes_archive_sessions(
    max_size_mb: float = 50.0,
    days_old: int = 7,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Prune Hermes sessions by DB size and age, archiving to .json.gz.

    Runs GC only when ``db_size_bytes / 1_048_576 >= max_size_mb``.  Deletes
    sessions older than *days_old* days to bring the store back under threshold.

    Args:
        max_size_mb: Trigger threshold in megabytes (default 50).
        days_old: Age cutoff in days for sessions to archive (default 7).
        dry_run: If True, return stats without modifying the DB.

    Returns:
        dict with status, db_size_mb, threshold_mb, pruned_count, and
        archived_dir path.
    """
    try:
        import os
        from pathlib import Path

        from codomyrmex.agents.hermes.session import SQLiteSessionStore

        WORKSPACE_ROOT = Path(os.path.abspath(".")).resolve()
        db_path = WORKSPACE_ROOT / ".codomyrmex" / "hermes_sessions.db"

        stats: dict[str, Any] = {
            "status": "ok",
            "threshold_mb": max_size_mb,
            "db_size_mb": 0.0,
            "pruned_count": 0,
            "archived_dir": str(db_path.parent / "sessions_archive"),
            "dry_run": dry_run,
        }

        if not db_path.exists():
            stats["message"] = "Session DB not found; nothing to archive."
            return stats

        size_bytes = os.path.getsize(db_path)
        size_mb = size_bytes / 1_048_576
        stats["db_size_mb"] = round(size_mb, 3)

        if size_mb < max_size_mb:
            stats["message"] = (
                f"DB is {size_mb:.2f} MB — under threshold {max_size_mb} MB. "
                "No pruning needed."
            )
            return stats

        if dry_run:
            # Count sessions that would be pruned without touching anything
            import sqlite3
            import time

            threshold = time.time() - (days_old * 86400)
            conn = sqlite3.connect(str(db_path))
            try:
                cursor = conn.execute(
                    "SELECT COUNT(*) FROM hermes_sessions WHERE updated_at < ?",
                    (threshold,),
                )
                would_prune = cursor.fetchone()[0]
            finally:
                conn.close()
            stats["pruned_count"] = would_prune
            stats["message"] = f"Dry run: would prune {would_prune} session(s)."
            return stats

        with SQLiteSessionStore(db_path) as store:
            pruned = store.prune_old_sessions(days_old=days_old)
            stats["pruned_count"] = pruned
            stats["message"] = (
                f"Pruned {pruned} session(s) older than {days_old} day(s). "
                f"DB was {size_mb:.2f} MB (threshold: {max_size_mb} MB)."
            )
        return stats

    except Exception as exc:
        return {"status": "error", "message": str(exc)}

@mcp_tool(
    category="hermes",
    description=(
        "Create an isolated git worktree for a Hermes session, "
        "enabling parallel agent execution without branch conflicts."
    ),
)
def hermes_worktree_create(session_id: str) -> dict[str, Any]:
    """Create an isolated git worktree for a session.

    Args:
        session_id: Session identifier for the worktree branch name.

    Returns:
        dict with keys: status, worktree_path, branch_name

    """
    try:
        client = _get_client()
        path = client.create_worktree(session_id)
        if path:
            return {
                "status": "success",
                "worktree_path": str(path),
                "branch_name": f"hermes/{session_id}",
            }
        return {"status": "error", "message": "Failed to create worktree"}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}

@mcp_tool(
    category="hermes",
    description="Remove an isolated git worktree after a session completes.",
)
def hermes_worktree_cleanup(session_id: str) -> dict[str, Any]:
    """Clean up a git worktree for a session.

    Args:
        session_id: Session identifier matching the worktree.

    Returns:
        dict with keys: status, cleaned

    """
    try:
        client = _get_client()
        cleaned = client.cleanup_worktree(session_id)
        return {"status": "success" if cleaned else "error", "cleaned": cleaned}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}
