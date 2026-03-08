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
import logging
import sqlite3
import time
import uuid
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class HermesSession:
    """A persistent conversation session.

    Attributes:
        session_id: Unique session identifier.
        messages: Conversation message history.
        metadata: Session metadata.
        created_at: Creation timestamp.
        updated_at: Last update timestamp.
    """

    session_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
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
        """Create the sessions table if it doesn't exist."""
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS hermes_sessions (
                session_id TEXT PRIMARY KEY,
                messages TEXT NOT NULL,
                metadata TEXT NOT NULL DEFAULT '{}',
                created_at REAL NOT NULL,
                updated_at REAL NOT NULL
            )
        """)
        self._conn.commit()

    def save(self, session: HermesSession) -> None:
        """Save or update a session.

        Args:
            session: The session to persist.
        """
        self._conn.execute(
            """
            INSERT OR REPLACE INTO hermes_sessions
            (session_id, messages, metadata, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                session.session_id,
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
            "SELECT session_id, messages, metadata, created_at, updated_at "
            "FROM hermes_sessions WHERE session_id = ?",
            (session_id,),
        )
        row = cursor.fetchone()
        if row is None:
            return None

        return HermesSession(
            session_id=row[0],
            messages=json.loads(row[1]),
            metadata=json.loads(row[2]),
            created_at=row[3],
            updated_at=row[4],
        )

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


__all__ = [
    "HermesSession",
    "InMemorySessionStore",
    "SQLiteSessionStore",
    "SessionStore",
]
