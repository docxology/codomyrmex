"""Dead-letter queue for failed operations.

Captures failed invocations (MCP tool calls, workflow steps, etc.)
with full context so they can be inspected, replayed, or purged.

Storage is JSON-Lines on disk — no external dependencies.

Usage::

    dlq = DeadLetterQueue(path="/tmp/codomyrmex-dlq.jsonl")
    dlq.add(operation="call_tool", args={"name": "x"}, error="timeout")
    entries = dlq.list_entries()
    replayed = dlq.replay(entries[0]["id"], callback=my_retry_fn)
    dlq.purge(before=datetime(2026, 1, 1))
"""

from __future__ import annotations

import json
import threading
import uuid
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any


class DeadLetterQueue:
    """Persistent dead-letter queue backed by JSONL files.

    Args:
        path: Path to the JSONL file for persistence.
    """

    def __init__(self, path: str | Path = "/tmp/codomyrmex-dlq.jsonl"):
        self._path = Path(path)
        self._lock = threading.Lock()
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def add(
        self,
        *,
        operation: str,
        args: dict[str, Any] | None = None,
        error: str,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """Record a failed operation.

        Args:
            operation: Name of the failed operation (e.g. tool name).
            args: Original arguments.
            error: Error message or traceback.
            metadata: Additional context (correlation_id, etc.).

        Returns:
            Entry ID (UUID).
        """
        entry_id = str(uuid.uuid4())
        entry = {
            "id": entry_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "operation": operation,
            "args": args or {},
            "error": error,
            "metadata": metadata or {},
            "replayed": False,
        }
        with self._lock:
            with self._path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
        return entry_id

    def list_entries(
        self,
        *,
        operation: str | None = None,
        since: datetime | None = None,
        include_replayed: bool = False,
    ) -> list[dict[str, Any]]:
        """List dead-letter entries with optional filtering.

        Args:
            operation: Filter by operation name.
            since: Only entries after this timestamp.
            include_replayed: Include already-replayed entries.

        Returns:
            List of entry dicts.
        """
        entries: list[dict[str, Any]] = []
        with self._lock:
            if not self._path.exists():
                return entries
            for line in self._path.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if not include_replayed and entry.get("replayed"):
                    continue
                if operation and entry.get("operation") != operation:
                    continue
                if since:
                    ts = entry.get("timestamp", "")
                    if ts < since.isoformat():
                        continue
                entries.append(entry)
        return entries

    def replay(
        self,
        entry_id: str,
        callback: Callable[[str, dict[str, Any]], Any],
    ) -> dict[str, Any]:
        """Replay a dead-letter entry via the callback.

        Args:
            entry_id: ID of the entry to replay.
            callback: Function(operation, args) -> result.

        Returns:
            Dict with replay outcome.
        """
        entries = self.list_entries(include_replayed=True)
        target = next((e for e in entries if e["id"] == entry_id), None)
        if target is None:
            return {"success": False, "error": f"Entry {entry_id} not found"}

        try:
            result = callback(target["operation"], target.get("args", {}))
            self._mark_replayed(entry_id)
            return {"success": True, "result": result}
        except Exception as exc:
            return {"success": False, "error": str(exc)}

    def _mark_replayed(self, entry_id: str) -> None:
        """Mark an entry as replayed by rewriting the file."""
        with self._lock:
            if not self._path.exists():
                return
            lines = self._path.read_text(encoding="utf-8").splitlines()
            new_lines: list[str] = []
            for line in lines:
                if not line.strip():
                    continue
                try:
                    entry = json.loads(line)
                    if entry.get("id") == entry_id:
                        entry["replayed"] = True
                        entry["replayed_at"] = datetime.utcnow().isoformat() + "Z"
                    new_lines.append(json.dumps(entry))
                except json.JSONDecodeError:
                    new_lines.append(line)
            self._path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")

    def purge(self, *, before: datetime | None = None) -> int:
        """Remove entries from the queue.

        Args:
            before: Remove entries older than this. If None, remove all.

        Returns:
            Number of entries removed.
        """
        with self._lock:
            if not self._path.exists():
                return 0
            lines = self._path.read_text(encoding="utf-8").splitlines()
            if before is None:
                count = len([line for line in lines if line.strip()])
                self._path.write_text("", encoding="utf-8")
                return count

            keep: list[str] = []
            removed = 0
            cutoff = before.isoformat()
            for line in lines:
                if not line.strip():
                    continue
                try:
                    entry = json.loads(line)
                    if entry.get("timestamp", "") < cutoff:
                        removed += 1
                    else:
                        keep.append(line)
                except json.JSONDecodeError:
                    keep.append(line)
            self._path.write_text("\n".join(keep) + "\n" if keep else "", encoding="utf-8")
            return removed
