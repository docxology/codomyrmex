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
from collections.abc import Callable
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
        on_close: Optional callback fired when :meth:`close` is called.  Receives
            this session as its only argument.  Use this hook to trigger KI
            extraction or other lifecycle actions.
    """

    session_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    name: str | None = None
    parent_session_id: str | None = None
    messages: list[dict[str, str]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    on_close: Callable[[HermesSession], None] | None = field(
        default=None, repr=False, compare=False
    )

    def add_message(self, role: str, content: str) -> None:
        """Add a message to the conversation history.

        Args:
            role: Message role (``"user"``, ``"assistant"``, ``"system"``).
            content: Message content.
        """
        self.messages.append({"role": role, "content": content})
        self.updated_at = time.time()

    def close(self) -> None:
        """Mark the session as closed and fire any registered :attr:`on_close` callback.

        The callback is invoked with ``self`` as the sole argument.  Typical
        use-case: trigger KI extraction when a high-quality session finishes::

            def extract_ki(session: HermesSession) -> None:
                if session.message_count >= 3:
                    hermes_extract_ki(session_id=session.session_id)

            sess = HermesSession(on_close=extract_ki)

        The callback is called at most once; after :meth:`close` the
        ``on_close`` attribute is set to ``None``.
        """
        if self.on_close is not None:
            try:
                self.on_close(self)
            except Exception:
                logger.exception(
                    "HermesSession.close() callback failed for session '%s'.",
                    self.session_id,
                )
            finally:
                self.on_close = None

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
        """Initialize an empty in-memory session store."""
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
        """Initialize the SQLite session store.

        Args:
            db_path: Path to the SQLite database file. Use ":memory:" for in-memory storage.
        """
        self._db_path = str(db_path)
        # Increase the default timeout to 5000ms to allow concurrent lockers to wait
        self._conn = sqlite3.connect(
            self._db_path, check_same_thread=False, timeout=5.0
        )
        self._init_schema()

    def _init_schema(self) -> None:
        """Create the sessions table if it doesn't exist and migrate if needed."""
        # Enable Write-Ahead Logging (WAL) for safer cross-process concurrency
        self._conn.execute("PRAGMA journal_mode=WAL;")
        self._conn.execute("PRAGMA synchronous=NORMAL;")
        # Set busy timeout (this is somewhat redundant with timeout=5.0, but explicit)
        self._conn.execute("PRAGMA busy_timeout=5000;")

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

        # FTS5 virtual table for semantic retrieval
        self._conn.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS hermes_sessions_fts USING fts5(
                session_id UNINDEXED,
                name,
                messages,
                content='hermes_sessions',
                content_rowid='rowid',
                tokenize='porter'
            )
        """)

        # Sync triggers for FTS5
        self._conn.execute("""
            CREATE TRIGGER IF NOT EXISTS hermes_sessions_ai AFTER INSERT ON hermes_sessions BEGIN
                INSERT INTO hermes_sessions_fts(rowid, session_id, name, messages)
                VALUES (new.rowid, new.session_id, new.name, new.messages);
            END;
        """)
        self._conn.execute("""
            CREATE TRIGGER IF NOT EXISTS hermes_sessions_ad AFTER DELETE ON hermes_sessions BEGIN
                INSERT INTO hermes_sessions_fts(hermes_sessions_fts, rowid, session_id, name, messages)
                VALUES('delete', old.rowid, old.session_id, old.name, old.messages);
            END;
        """)
        self._conn.execute("""
            CREATE TRIGGER IF NOT EXISTS hermes_sessions_au AFTER UPDATE ON hermes_sessions BEGIN
                INSERT INTO hermes_sessions_fts(hermes_sessions_fts, rowid, session_id, name, messages)
                VALUES('delete', old.rowid, old.session_id, old.name, old.messages);
                INSERT INTO hermes_sessions_fts(rowid, session_id, name, messages)
                VALUES (new.rowid, new.session_id, new.name, new.messages);
            END;
        """)

        self._conn.commit()
        # Migrate: add columns for existing DBs that lack them
        self._migrate_add_columns()
        self._migrate_fts()

    def _migrate_fts(self) -> None:
        """Populate the FTS table with any existing records that are missing."""
        try:
            cursor = self._conn.execute("SELECT rowid FROM hermes_sessions LIMIT 1")
            has_data = cursor.fetchone() is not None

            if has_data:
                # To see if FTS5 has indexed anything, check the shadow table
                c2 = self._conn.execute(
                    "SELECT COUNT(*) FROM hermes_sessions_fts_docsize"
                )
                if c2.fetchone()[0] == 0:
                    self._conn.execute(
                        "INSERT INTO hermes_sessions_fts(hermes_sessions_fts) VALUES('rebuild')"
                    )
                    self._conn.commit()
        except sqlite3.OperationalError:
            pass

    def _migrate_add_columns(self) -> None:
        """Add missing columns for schema evolution (pre-v0.2.0 → v0.2.0)."""
        cursor = self._conn.execute("PRAGMA table_info(hermes_sessions)")
        columns = {row[1] for row in cursor.fetchall()}

        migrations = [
            ("name", "ALTER TABLE hermes_sessions ADD COLUMN name TEXT"),
            (
                "parent_session_id",
                "ALTER TABLE hermes_sessions ADD COLUMN parent_session_id TEXT",
            ),
        ]

        for col_name, sql in migrations:
            if col_name not in columns:
                try:
                    self._conn.execute(sql)
                    self._conn.commit()
                    logger.info(
                        "Migrated hermes_sessions schema: added '%s' column.", col_name
                    )
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

    def search_fts(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        """Perform a full-text search over session contents using FTS5.

        Args:
            query: The FTS MATCH query.
            limit: Maximum number of results to return.

        Returns:
            List of dicts with ``session_id``, ``name``, ``messages_snippet``, and ``rank``.
        """
        cursor = self._conn.execute(
            "SELECT session_id, name, snippet(hermes_sessions_fts, 2, '<b>', '</b>', '...', 64), rank "
            "FROM hermes_sessions_fts WHERE hermes_sessions_fts MATCH ? ORDER BY rank LIMIT ?",
            (query, limit),
        )
        return [
            {
                "session_id": row[0],
                "name": row[1],
                "messages_snippet": row[2],
                "rank": row[3],
            }
            for row in cursor.fetchall()
        ]

    def prune_old_sessions(self, days_old: int = 30) -> int:
        """Archive and delete sessions older than the specified number of days.

        Archived sessions are written as gzipped JSON files in a `sessions_archive`
        directory adjacent to the database file.

        Args:
            days_old: Number of days before a session is pruned.

        Returns:
            The number of sessions archived and deleted.
        """
        import gzip
        import time
        from dataclasses import asdict
        from pathlib import Path

        threshold = time.time() - (days_old * 86400)
        cursor = self._conn.execute(
            "SELECT session_id, name, parent_session_id, messages, metadata, created_at, updated_at "
            "FROM hermes_sessions WHERE updated_at < ?",
            (threshold,),
        )

        rows = cursor.fetchall()
        if not rows:
            return 0

        archive_dir = Path(self._db_path).parent / "sessions_archive"
        archive_dir.mkdir(parents=True, exist_ok=True)

        deleted_count = 0
        for row in rows:
            session = HermesSession(
                session_id=row[0],
                name=row[1],
                parent_session_id=row[2],
                messages=json.loads(row[3]),
                metadata=json.loads(row[4]),
                created_at=row[5],
                updated_at=row[6],
            )

            # Serialize and compress
            archive_path = archive_dir / f"{session.session_id}.json.gz"
            with gzip.open(archive_path, "wt", encoding="utf-8") as f:
                json.dump(asdict(session), f)

            # Delete from DB
            self.delete(session.session_id)
            deleted_count += 1

        # Reclaim space
        self._conn.execute("VACUUM;")

        return deleted_count

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

    def get_stats(self) -> dict[str, Any]:
        """Return summary statistics about the session database.

        Returns:
            dict with keys: ``session_count``, ``db_size_bytes``,
            ``oldest_session_at``, ``newest_session_at``.
        """
        import os

        cursor = self._conn.execute(
            "SELECT COUNT(*), MIN(created_at), MAX(updated_at) FROM hermes_sessions"
        )
        row = cursor.fetchone()
        count = row[0] or 0
        oldest = row[1]
        newest = row[2]

        size = 0
        if self._db_path != ":memory:":
            try:
                size = os.path.getsize(self._db_path)
            except OSError:
                pass

        return {
            "session_count": count,
            "db_size_bytes": size,
            "oldest_session_at": oldest,
            "newest_session_at": newest,
        }

    def export_markdown(self, session_id: str) -> str | None:
        """Export a session as clean Markdown text.

        Args:
            session_id: Session identifier.

        Returns:
            Markdown string, or ``None`` if the session does not exist.
        """
        session = self.load(session_id)
        if session is None:
            return None

        lines: list[str] = []
        title = session.name or session.session_id
        lines.append(f"# Session: {title}\n")
        lines.append(f"**ID**: `{session.session_id}`  ")
        if session.parent_session_id:
            lines.append(f"**Parent**: `{session.parent_session_id}`  ")
        import datetime
        lines.append(
            f"**Created**: {datetime.datetime.fromtimestamp(session.created_at).isoformat()}  "
        )
        lines.append(
            f"**Updated**: {datetime.datetime.fromtimestamp(session.updated_at).isoformat()}\n"
        )

        for msg in session.messages:
            role = msg.get("role", "unknown").capitalize()
            content = msg.get("content", "")
            lines.append(f"\n## {role}\n\n{content}\n")

        if session.metadata:
            lines.append("\n---\n\n## Metadata\n")
            for k, v in session.metadata.items():
                lines.append(f"- **{k}**: {v}")

        return "\n".join(lines)

    def update_system_prompt(self, session_id: str, prompt: str) -> bool:
        """Upsert a persistent system message at index 0 of the session.

        If the first message is already a ``system`` role, it will be replaced;
        otherwise the new system message is prepended.

        Args:
            session_id: Session identifier.
            prompt: The system prompt text.

        Returns:
            ``True`` if the session was updated.
        """
        session = self.load(session_id)
        if session is None:
            return False

        system_msg = {"role": "system", "content": prompt}
        if session.messages and session.messages[0].get("role") == "system":
            session.messages[0] = system_msg
        else:
            session.messages.insert(0, system_msg)

        session.updated_at = time.time()
        self.save(session)
        return True

    def get_detail(self, session_id: str) -> dict[str, Any] | None:
        """Return a rich detail dictionary for a session.

        Args:
            session_id: Session identifier.

        Returns:
            dict with all session fields plus ``message_count``, ``last_message``,
            ``has_system_prompt``, or ``None`` if not found.
        """
        session = self.load(session_id)
        if session is None:
            return None

        last = session.last_message
        has_system = bool(
            session.messages and session.messages[0].get("role") == "system"
        )

        return {
            "session_id": session.session_id,
            "name": session.name,
            "parent_session_id": session.parent_session_id,
            "message_count": session.message_count,
            "last_message": last,
            "has_system_prompt": has_system,
            "metadata": session.metadata,
            "created_at": session.created_at,
            "updated_at": session.updated_at,
        }

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
