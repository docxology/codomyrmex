import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

from .models import Conversation, HistoryMessage, MessageRole


class InMemoryHistoryStore:
    """In-memory conversation storage."""

    def __init__(self):
        self._conversations: dict[str, Conversation] = {}

    def save(self, conversation: Conversation) -> None:
        """Save a conversation."""
        self._conversations[conversation.conversation_id] = conversation

    def load(self, conversation_id: str) -> Conversation | None:
        """Load a conversation."""
        return self._conversations.get(conversation_id)

    def delete(self, conversation_id: str) -> bool:
        """Delete a conversation."""
        if conversation_id in self._conversations:
            del self._conversations[conversation_id]
            return True
        return False

    def list_conversations(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Conversation]:
        """List conversations, most recent first."""
        sorted_convs = sorted(
            self._conversations.values(),
            key=lambda c: c.updated_at,
            reverse=True
        )
        return sorted_convs[offset:offset + limit]

    def search(self, query: str) -> list[Conversation]:
        """Search conversations by content."""
        results = []
        query_lower = query.lower()
        for conv in self._conversations.values():
            if query_lower in conv.title.lower():
                results.append(conv)
                continue
            for msg in conv.messages:
                if query_lower in msg.content.lower():
                    results.append(conv)
                    break
        return results

    def clear(self) -> None:
        """Clear all conversations."""
        self._conversations.clear()


class FileHistoryStore:
    """File-based conversation storage (JSON)."""

    def __init__(self, directory: str):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)

    def _get_path(self, conversation_id: str) -> Path:
        """Get file path for a conversation."""
        return self.directory / f"{conversation_id}.json"

    def save(self, conversation: Conversation) -> None:
        """Save a conversation."""
        path = self._get_path(conversation.conversation_id)
        with open(path, 'w') as f:
            json.dump(conversation.to_dict(), f, indent=2)

    def load(self, conversation_id: str) -> Conversation | None:
        """Load a conversation."""
        path = self._get_path(conversation_id)
        if not path.exists():
            return None
        with open(path) as f:
            return Conversation.from_dict(json.load(f))

    def delete(self, conversation_id: str) -> bool:
        """Delete a conversation."""
        path = self._get_path(conversation_id)
        if path.exists():
            path.unlink()
            return True
        return False

    def list_conversations(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Conversation]:
        """List conversations."""
        conversations = []
        for path in self.directory.glob("*.json"):
            conv = self.load(path.stem)
            if conv:
                conversations.append(conv)

        # Sort by updated_at
        conversations.sort(key=lambda c: c.updated_at, reverse=True)
        return conversations[offset:offset + limit]

    def search(self, query: str) -> list[Conversation]:
        """Search conversations."""
        results = []
        query_lower = query.lower()
        for conv in self.list_conversations(limit=1000):
            if query_lower in conv.title.lower():
                results.append(conv)
                continue
            for msg in conv.messages:
                if query_lower in msg.content.lower():
                    results.append(conv)
                    break
        return results


class SQLiteHistoryStore:
    """SQLite-based conversation storage."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        """Initialize database schema."""
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    conversation_id TEXT PRIMARY KEY,
                    title TEXT,
                    created_at TEXT,
                    updated_at TEXT,
                    metadata TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    message_id TEXT PRIMARY KEY,
                    conversation_id TEXT,
                    role TEXT,
                    content TEXT,
                    timestamp TEXT,
                    tokens INTEGER DEFAULT 0,
                    metadata TEXT,
                    FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id)
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_messages_conv
                ON messages(conversation_id)
            """)
            conn.commit()

    @contextmanager
    def _get_connection(self):
        """Get database connection."""
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()

    def save(self, conversation: Conversation) -> None:
        """Save a conversation."""
        with self._get_connection() as conn:
            # Upsert conversation
            conn.execute("""
                INSERT OR REPLACE INTO conversations
                (conversation_id, title, created_at, updated_at, metadata)
                VALUES (?, ?, ?, ?, ?)
            """, (
                conversation.conversation_id,
                conversation.title,
                conversation.created_at.isoformat(),
                conversation.updated_at.isoformat(),
                json.dumps(conversation.metadata),
            ))

            # Delete existing messages
            conn.execute(
                "DELETE FROM messages WHERE conversation_id = ?",
                (conversation.conversation_id,)
            )

            # Insert messages
            for msg in conversation.messages:
                conn.execute("""
                    INSERT INTO messages
                    (message_id, conversation_id, role, content, timestamp, tokens, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    msg.message_id,
                    conversation.conversation_id,
                    msg.role.value,
                    msg.content,
                    msg.timestamp.isoformat(),
                    msg.tokens,
                    json.dumps(msg.metadata),
                ))

            conn.commit()

    def load(self, conversation_id: str) -> Conversation | None:
        """Load a conversation."""
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM conversations WHERE conversation_id = ?",
                (conversation_id,)
            ).fetchone()

            if not row:
                return None

            # Load messages
            msg_rows = conn.execute(
                "SELECT * FROM messages WHERE conversation_id = ? ORDER BY timestamp",
                (conversation_id,)
            ).fetchall()

            messages = [
                HistoryMessage(
                    role=MessageRole(r[2]),
                    content=r[3],
                    timestamp=datetime.fromisoformat(r[4]),
                    message_id=r[0],
                    tokens=r[5],
                    metadata=json.loads(r[6]) if r[6] else {},
                )
                for r in msg_rows
            ]

            return Conversation(
                conversation_id=row[0],
                title=row[1],
                messages=messages,
                created_at=datetime.fromisoformat(row[2]),
                updated_at=datetime.fromisoformat(row[3]),
                metadata=json.loads(row[4]) if row[4] else {},
            )

    def delete(self, conversation_id: str) -> bool:
        """Delete a conversation."""
        with self._get_connection() as conn:
            conn.execute(
                "DELETE FROM messages WHERE conversation_id = ?",
                (conversation_id,)
            )
            result = conn.execute(
                "DELETE FROM conversations WHERE conversation_id = ?",
                (conversation_id,)
            )
            conn.commit()
            return result.rowcount > 0

    def list_conversations(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Conversation]:
        """List conversations."""
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT conversation_id FROM conversations ORDER BY updated_at DESC LIMIT ? OFFSET ?",
                (limit, offset)
            ).fetchall()

            return [self.load(row[0]) for row in rows if row]

    def search(self, query: str) -> list[Conversation]:
        """Search conversations."""
        with self._get_connection() as conn:
            # Search in titles
            conv_ids = set()
            rows = conn.execute(
                "SELECT conversation_id FROM conversations WHERE title LIKE ?",
                (f"%{query}%",)
            ).fetchall()
            conv_ids.update(r[0] for r in rows)

            # Search in messages
            rows = conn.execute(
                "SELECT DISTINCT conversation_id FROM messages WHERE content LIKE ?",
                (f"%{query}%",)
            ).fetchall()
            conv_ids.update(r[0] for r in rows)

            return [self.load(cid) for cid in conv_ids if cid]


