"""Hermes agent session persistence.

Provides session state management with SQLite-backed storage
for conversation continuity across invocations.

Example::

    store = SQLiteSessionStore()
    session = HermesSession(session_id="task-42")
    session.add_message("user", "Analyze this code")
    session.add_message("assistant", "I see a potential issue...")
    store.save(session)

    # Later...
    restored = store.load("task-42")
    print(restored.messages)
"""

from __future__ import annotations

import json
import sqlite3
import time
import uuid
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Protocol, Self, runtime_checkable

from codomyrmex.logging_monitoring import get_logger

if TYPE_CHECKING:
    from pathlib import Path

logger = get_logger(__name__)


@dataclass
class HermesSession:
    """A persistent conversation session.

    Attributes:
        session_id: Unique session identifier.
        name: Human-friendly session name (v0.2.0).
        parent_session_id: ID of the parent session for lineage tracking (v0.2.0).
        messages: Conversation message history.
        metadata: Session metadata.
        created_at: Creation timestamp.
        updated_at: Last update timestamp.
    """

    session_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    name: str | None = None
    parent_session_id: str | None = None
    messages: list[dict[str, str]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

    def add_message(self, role: str, content: str) -> None:
        """Add a message to the conversation history.

        Args:
            role: Message role (``"user"``, ``"assistant"``, ``"system"``).
            content: Message content.
        """
        self.messages.append({"role": role, "content": content})
        self.updated_at = time.time()

    @property
    def message_count(self) -> int:
        """Return the number of messages."""
        return len(self.messages)

    @property
    def last_message(self) -> dict[str, str] | None:
        """Return the most recent message, or None."""
        return self.messages[-1] if self.messages else None

    def fork(self, new_name: str | None = None) -> HermesSession:
        """Fork a child session inheriting this session's history.

        Args:
            new_name: Name for the child session.

        Returns:
            A new HermesSession with this session as its parent.
        """
        child = HermesSession(
            name=new_name,
            parent_session_id=self.session_id,
            messages=list(self.messages),
            metadata={**self.metadata, "forked_from": self.session_id},
        )
        return child


@runtime_checkable
class SessionStore(Protocol):
    """Protocol for session persistence backends."""

    def save(self, session: HermesSession) -> None:
        """Save a session."""
        ...

    def load(self, session_id: str) -> HermesSession | None:
        """Load a session by ID."""
        ...

    def list_sessions(self) -> list[str]:
        """List all session IDs."""
        ...

    def delete(self, session_id: str) -> bool:
        """Delete a session."""
        ...


class InMemorySessionStore:
    """In-memory session store (for testing and ephemeral use)."""

    def __init__(self) -> None:
        self._sessions: dict[str, HermesSession] = {}

    def save(self, session: HermesSession) -> None:
        """Save a session."""
        self._sessions[session.session_id] = session

    def load(self, session_id: str) -> HermesSession | None:
        """Load a session."""
        return self._sessions.get(session_id)

    def list_sessions(self) -> list[str]:
        """List session IDs."""
        return list(self._sessions.keys())

    def delete(self, session_id: str) -> bool:
        """Delete a session."""
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False


class SQLiteSessionStore:
    """SQLite-backed session persistence.

    Args:
        db_path: Path to the SQLite database file.

    Example::

        store = SQLiteSessionStore("/tmp/hermes_sessions.db")
        store.save(session)
    """

    def __init__(self, db_path: str | Path = ":memory:") -> None:
        self._db_path = str(db_path)
        self._conn = sqlite3.connect(self._db_path, check_same_thread=False)
        self._init_schema()

    def _init_schema(self) -> None:
        """Create the sessions table if it doesn't exist and migrate if needed."""
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS hermes_sessions (
                session_id TEXT PRIMARY KEY,
                name TEXT,
                parent_session_id TEXT,
                messages TEXT NOT NULL,
                metadata TEXT NOT NULL DEFAULT '{}',
                created_at REAL NOT NULL,
                updated_at REAL NOT NULL
            )
        """)
        self._conn.commit()
        # Migrate: add columns for existing DBs that lack them
        self._migrate_add_columns()

    def _migrate_add_columns(self) -> None:
        """Add missing columns for schema evolution (pre-v0.2.0 → v0.2.0)."""
        cursor = self._conn.execute("PRAGMA table_info(hermes_sessions)")
        columns = {row[1] for row in cursor.fetchall()}

        migrations = [
            ("name", "ALTER TABLE hermes_sessions ADD COLUMN name TEXT"),
            ("parent_session_id", "ALTER TABLE hermes_sessions ADD COLUMN parent_session_id TEXT"),
        ]

        for col_name, sql in migrations:
            if col_name not in columns:
                try:
                    self._conn.execute(sql)
                    self._conn.commit()
                    logger.info("Migrated hermes_sessions schema: added '%s' column.", col_name)
                except sqlite3.OperationalError:
                    pass  # Column already exists or DB is read-only

    def save(self, session: HermesSession) -> None:
        """Save or update a session.

        Args:
            session: The session to persist.
        """
        self._conn.execute(
            """
            INSERT OR REPLACE INTO hermes_sessions
            (session_id, name, parent_session_id, messages, metadata, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                session.session_id,
                session.name,
                session.parent_session_id,
                json.dumps(session.messages),
                json.dumps(session.metadata),
                session.created_at,
                session.updated_at,
            ),
        )
        self._conn.commit()

    def load(self, session_id: str) -> HermesSession | None:
        """Load a session by ID.

        Args:
            session_id: Session identifier.

        Returns:
            The :class:`HermesSession` or ``None``.
        """
        cursor = self._conn.execute(
            "SELECT session_id, name, parent_session_id, messages, metadata, created_at, updated_at "
            "FROM hermes_sessions WHERE session_id = ?",
            (session_id,),
        )
        row = cursor.fetchone()
        if row is None:
            return None

        return HermesSession(
            session_id=row[0],
            name=row[1],
            parent_session_id=row[2],
            messages=json.loads(row[3]),
            metadata=json.loads(row[4]),
            created_at=row[5],
            updated_at=row[6],
        )

    def find_by_name(self, name: str) -> HermesSession | None:
        """Find a session by its human-friendly name.

        Args:
            name: Session name to look up.

        Returns:
            The :class:`HermesSession` or ``None``.
        """
        cursor = self._conn.execute(
            "SELECT session_id, name, parent_session_id, messages, metadata, created_at, updated_at "
            "FROM hermes_sessions WHERE name = ? ORDER BY updated_at DESC LIMIT 1",
            (name,),
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return HermesSession(
            session_id=row[0],
            name=row[1],
            parent_session_id=row[2],
            messages=json.loads(row[3]),
            metadata=json.loads(row[4]),
            created_at=row[5],
            updated_at=row[6],
        )

    def search_sessions(self, query: str) -> list[dict[str, Any]]:
        """Search sessions by name substring.

        Args:
            query: Substring to match against session names.

        Returns:
            List of dicts with ``session_id``, ``name``, ``updated_at``.
        """
        cursor = self._conn.execute(
            "SELECT session_id, name, updated_at FROM hermes_sessions "
            "WHERE name LIKE ? ORDER BY updated_at DESC",
            (f"%{query}%",),
        )
        return [
            {"session_id": row[0], "name": row[1], "updated_at": row[2]}
            for row in cursor.fetchall()
        ]

    def list_sessions(self) -> list[str]:
        """List all session IDs.

        Returns:
            List of session ID strings.
        """
        cursor = self._conn.execute(
            "SELECT session_id FROM hermes_sessions ORDER BY updated_at DESC"
        )
        return [row[0] for row in cursor.fetchall()]

    def delete(self, session_id: str) -> bool:
        """Delete a session.

        Args:
            session_id: Session identifier.

        Returns:
            ``True`` if the session was deleted.
        """
        cursor = self._conn.execute(
            "DELETE FROM hermes_sessions WHERE session_id = ?",
            (session_id,),
        )
        self._conn.commit()
        return cursor.rowcount > 0

    def close(self) -> None:
        """Close the database connection."""
        self._conn.close()

    def __enter__(self) -> Self:
        """Support use as a context manager."""
        return self

    def __exit__(self, *_: object) -> None:
        """Close the connection on context exit."""
        self.close()


__all__ = [
    "HermesSession",
    "InMemorySessionStore",
    "SQLiteSessionStore",
    "SessionStore",
]
