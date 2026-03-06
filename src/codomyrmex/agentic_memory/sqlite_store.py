"""SQLite-backed persistent memory store."""

from __future__ import annotations

import json
import sqlite3
import threading
from typing import Any

from codomyrmex.agentic_memory.models import Memory, MemoryImportance, MemoryType


class SQLiteStore:
    """Thread-safe SQLite persistent memory store.
    
    Provides the same CRUD API as InMemoryStore and JSONFileStore,
    but backs the data to a local SQLite database file.
    """

    def __init__(self, db_path: str = "memory.db") -> None:
        self.db_path = db_path
        self._lock = threading.Lock()
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """Get a configured SQLite connection."""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        """Initialise the database schema if it does not exist."""
        with self._lock:
            with self._get_connection() as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS memories (
                        id TEXT PRIMARY KEY,
                        content TEXT NOT NULL,
                        memory_type TEXT NOT NULL,
                        importance INTEGER NOT NULL,
                        metadata TEXT NOT NULL,
                        tags TEXT NOT NULL,
                        created_at REAL NOT NULL,
                        access_count INTEGER NOT NULL,
                        last_accessed REAL NOT NULL
                    )
                    """
                )
                # Create indices for common query patterns
                conn.execute("CREATE INDEX IF NOT EXISTS idx_meminfo ON memories(memory_type, importance)")

    def save(self, memory: Memory) -> None:
        """Upsert a memory entry."""
        with self._lock:
            with self._get_connection() as conn:
                conn.execute(
                    """
                    INSERT INTO memories
                    (id, content, memory_type, importance, metadata, tags, created_at, access_count, last_accessed)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET
                        content=excluded.content,
                        memory_type=excluded.memory_type,
                        importance=excluded.importance,
                        metadata=excluded.metadata,
                        tags=excluded.tags,
                        created_at=excluded.created_at,
                        access_count=excluded.access_count,
                        last_accessed=excluded.last_accessed
                    """,
                    (
                        memory.id,
                        memory.content,
                        memory.memory_type.value,
                        memory.importance.value,
                        json.dumps(memory.metadata),
                        json.dumps(memory.tags),
                        memory.created_at,
                        memory.access_count,
                        memory.last_accessed,
                    ),
                )

    def get(self, memory_id: str) -> Memory | None:
        """Return a memory by id or ``None``."""
        with self._lock:
            with self._get_connection() as conn:
                row = conn.execute("SELECT * FROM memories WHERE id = ?", (memory_id,)).fetchone()
                
        if not row:
            return None
            
        mem = Memory(
            id=row["id"],
            content=row["content"],
            memory_type=MemoryType(row["memory_type"]),
            importance=MemoryImportance(row["importance"]),
            metadata=json.loads(row["metadata"]),
            tags=json.loads(row["tags"]),
            created_at=row["created_at"],
            access_count=row["access_count"],
            last_accessed=row["last_accessed"],
        )
        mem.access()
        # Save the updated access count asynchronously or right away
        # For strict thread-safety and simplicity in this implementation, we re-save it.
        # But we don't want to re-enter the lock recursively if we just call self.save().
        # So we write directly.
        with self._lock:
            with self._get_connection() as update_conn:
                update_conn.execute(
                    "UPDATE memories SET access_count = ?, last_accessed = ? WHERE id = ?",
                    (mem.access_count, mem.last_accessed, mem.id)
                )

        return mem

    def delete(self, memory_id: str) -> bool:
        """Remove a memory. Returns ``True`` if it existed."""
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
                return cursor.rowcount > 0

    def list_all(self) -> list[Memory]:
        """Return every stored memory."""
        memories = []
        with self._lock:
            with self._get_connection() as conn:
                rows = conn.execute("SELECT * FROM memories ORDER BY created_at ASC").fetchall()
                
        for row in rows:
            memories.append(
                Memory(
                    id=row["id"],
                    content=row["content"],
                    memory_type=MemoryType(row["memory_type"]),
                    importance=MemoryImportance(row["importance"]),
                    metadata=json.loads(row["metadata"]),
                    tags=json.loads(row["tags"]),
                    created_at=row["created_at"],
                    access_count=row["access_count"],
                    last_accessed=row["last_accessed"],
                )
            )
        return memories
