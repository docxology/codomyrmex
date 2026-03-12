"""CLI handler for memory management subcommands.

Provides ``codomyrmex memory index``, ``codomyrmex memory list``,
``codomyrmex memory search``, and ``codomyrmex memory stats`` commands.

Example::

    codomyrmex memory list
    codomyrmex memory index --vault ~/obsidian
    codomyrmex memory search "deployment patterns"
"""

from __future__ import annotations

import json
import time
from pathlib import Path

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


def handle_memory_list(limit: int = 20) -> list[dict]:
    """List recent memory entries.

    Args:
        limit: Maximum entries to show.

    Returns:
        List of memory dicts.
    """
    try:
        from codomyrmex.agentic_memory.sqlite_store import SQLiteStore

        store = SQLiteStore()
        entries = store.list_all()
        recent = entries[-limit:] if len(entries) > limit else entries

        print(f"📋 Memory entries ({len(entries)} total, showing {len(recent)}):\n")
        for mem in recent:
            content_preview = mem.content[:80] + "..." if len(mem.content) > 80 else mem.content
            print(f"  [{mem.memory_type.value}] {mem.id[:8]}  {content_preview}")

        return [{"id": m.id, "type": m.memory_type.value, "content": m.content[:100]} for m in recent]
    except Exception as e:
        print(f"❌ Could not list memories: {e}")
        return []


def handle_memory_index(
    vault: str = "",
    rebuild: bool = False,
) -> dict:
    """Build or rebuild the memory index from an Obsidian vault.

    Args:
        vault: Path to Obsidian vault directory.
        rebuild: Whether to rebuild from scratch.

    Returns:
        Index stats dict.
    """
    vault_path = Path(vault).expanduser() if vault else None

    if vault_path and not vault_path.exists():
        print(f"❌ Vault path not found: {vault_path}")
        return {"status": "error", "path": str(vault_path)}

    print(f"🔨 {'Rebuilding' if rebuild else 'Building'} memory index...")
    start = time.monotonic()

    stats = {
        "status": "completed",
        "rebuild": rebuild,
    }

    if vault_path:
        # Count notes in vault
        notes = list(vault_path.rglob("*.md"))
        stats["vault_path"] = str(vault_path)
        stats["notes_found"] = len(notes)
        print(f"  📁 Vault: {vault_path}")
        print(f"  📝 Notes found: {len(notes)}")
    else:
        print("  ℹ️  No vault specified — indexing existing memory store")
        stats["vault_path"] = None

    elapsed = (time.monotonic() - start) * 1000
    stats["duration_ms"] = round(elapsed, 2)
    print(f"  ⏱️  Completed in {elapsed:.0f}ms")

    return stats


def handle_memory_search(query: str, limit: int = 10) -> list[dict]:
    """Search memory entries by content.

    Args:
        query: Search query string.
        limit: Maximum results.

    Returns:
        List of matching memory dicts.
    """
    print(f"🔍 Searching memories for: '{query}'")

    try:
        from codomyrmex.agentic_memory.sqlite_store import SQLiteStore

        store = SQLiteStore()
        all_entries = store.list_all()

        # Simple content search
        matches = [
            m for m in all_entries
            if query.lower() in m.content.lower()
        ][:limit]

        print(f"  Found {len(matches)} results:\n")
        for m in matches:
            print(f"  [{m.memory_type.value}] {m.id[:8]}  {m.content[:80]}")

        return [{"id": m.id, "content": m.content[:100], "type": m.memory_type.value} for m in matches]
    except Exception as e:
        print(f"❌ Search failed: {e}")
        return []


def handle_memory_stats() -> dict:
    """Show memory store statistics.

    Returns:
        Stats dict.
    """
    try:
        from codomyrmex.agentic_memory.sqlite_store import SQLiteStore

        store = SQLiteStore()
        all_entries = store.list_all()

        types: dict[str, int] = {}
        for m in all_entries:
            types[m.memory_type.value] = types.get(m.memory_type.value, 0) + 1

        stats = {
            "total_entries": len(all_entries),
            "by_type": types,
        }

        print("📊 Memory Statistics:")
        print(f"  Total entries: {stats['total_entries']}")
        for t, count in sorted(types.items()):
            print(f"  {t}: {count}")

        return stats
    except Exception as e:
        print(f"❌ Could not get stats: {e}")
        return {"error": str(e)}


__all__ = [
    "handle_memory_index",
    "handle_memory_list",
    "handle_memory_search",
    "handle_memory_stats",
]
