"""
Agent History Module

Conversation and context persistence for agent sessions.
"""

__version__ = "0.1.0"

import hashlib
import json
import os
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional


class MessageRole(Enum):
    """Standard conversation roles."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"
    FUNCTION = "function"

@dataclass
class HistoryMessage:
    """A message in conversation history."""
    role: MessageRole
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    message_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    tokens: int = 0

    def __post_init__(self):
        if self.message_id is None:
            self.message_id = self._generate_id()

    def _generate_id(self) -> str:
        """Generate unique message ID."""
        data = f"{self.role.value}{self.content}{self.timestamp.isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dict."""
        return {
            "role": self.role.value,
            "content": self.content,
            "message_id": self.message_id,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
            "tokens": self.tokens,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "HistoryMessage":
        """Create from dict."""
        return cls(
            role=MessageRole(data["role"]),
            content=data["content"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            message_id=data.get("message_id"),
            metadata=data.get("metadata", {}),
            tokens=data.get("tokens", 0),
        )

@dataclass
class Conversation:
    """A conversation with metadata."""
    conversation_id: str
    title: str = ""
    messages: list[HistoryMessage] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)

    def add_message(
        self,
        role: MessageRole,
        content: str,
        **kwargs
    ) -> HistoryMessage:
        """Add a message to the conversation."""
        msg = HistoryMessage(role=role, content=content, **kwargs)
        self.messages.append(msg)
        self.updated_at = datetime.now()
        return msg

    def add_user_message(self, content: str, **kwargs) -> HistoryMessage:
        """Add a user message."""
        return self.add_message(MessageRole.USER, content, **kwargs)

    def add_assistant_message(self, content: str, **kwargs) -> HistoryMessage:
        """Add an assistant message."""
        return self.add_message(MessageRole.ASSISTANT, content, **kwargs)

    def get_messages_for_api(self, include_system: bool = True) -> list[dict[str, str]]:
        """Get messages in API-compatible format."""
        result = []
        for msg in self.messages:
            if not include_system and msg.role == MessageRole.SYSTEM:
                continue
            result.append({
                "role": msg.role.value,
                "content": msg.content,
            })
        return result

    @property
    def message_count(self) -> int:
        """Total number of messages."""
        return len(self.messages)

    @property
    def total_tokens(self) -> int:
        """Total tokens in conversation."""
        return sum(msg.tokens for msg in self.messages)

    def truncate(self, max_messages: int) -> list[HistoryMessage]:
        """
        Truncate to max messages, keeping system messages.
        Returns removed messages.
        """
        system_msgs = [m for m in self.messages if m.role == MessageRole.SYSTEM]
        other_msgs = [m for m in self.messages if m.role != MessageRole.SYSTEM]

        if len(other_msgs) <= max_messages:
            return []

        to_remove = other_msgs[:len(other_msgs) - max_messages]
        self.messages = system_msgs + other_msgs[-max_messages:]
        self.updated_at = datetime.now()
        return to_remove

    def to_dict(self) -> dict[str, Any]:
        """Convert to dict."""
        return {
            "conversation_id": self.conversation_id,
            "title": self.title,
            "messages": [m.to_dict() for m in self.messages],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Conversation":
        """Create from dict."""
        return cls(
            conversation_id=data["conversation_id"],
            title=data.get("title", ""),
            messages=[HistoryMessage.from_dict(m) for m in data.get("messages", [])],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            metadata=data.get("metadata", {}),
        )

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

class ConversationManager:
    """
    High-level manager for conversation history.

    Usage:
        manager = ConversationManager()

        # Start a new conversation
        conv = manager.create_conversation("Code Review Session")

        # Add messages
        conv.add_user_message("Review this code...")
        conv.add_assistant_message("Here's my review...")

        # Save
        manager.save(conv)

        # Later, retrieve
        conv = manager.get_conversation(conv_id)
    """

    def __init__(
        self,
        store: InMemoryHistoryStore | None = None,
        max_messages_per_conversation: int = 100,
    ):
        self.store = store or InMemoryHistoryStore()
        self.max_messages = max_messages_per_conversation
        self._active_conversation: Conversation | None = None

    def create_conversation(
        self,
        title: str = "",
        system_prompt: str | None = None,
        **metadata
    ) -> Conversation:
        """Create a new conversation."""
        conv_id = hashlib.sha256(
            f"{datetime.now().isoformat()}{title}".encode()
        ).hexdigest()[:16]

        conv = Conversation(
            conversation_id=conv_id,
            title=title or f"Conversation {conv_id[:8]}",
            metadata=metadata,
        )

        if system_prompt:
            conv.add_message(MessageRole.SYSTEM, system_prompt)

        self._active_conversation = conv
        return conv

    def get_conversation(self, conversation_id: str) -> Conversation | None:
        """Get a conversation by ID."""
        return self.store.load(conversation_id)

    def save(self, conversation: Conversation | None = None) -> None:
        """Save a conversation."""
        conv = conversation or self._active_conversation
        if conv:
            # Truncate if needed
            if len(conv.messages) > self.max_messages:
                conv.truncate(self.max_messages)
            self.store.save(conv)

    def delete(self, conversation_id: str) -> bool:
        """Delete a conversation."""
        return self.store.delete(conversation_id)

    def list_recent(self, limit: int = 20) -> list[Conversation]:
        """List recent conversations."""
        return self.store.list_conversations(limit=limit)

    def search(self, query: str) -> list[Conversation]:
        """Search conversations."""
        return self.store.search(query)

    @property
    def active(self) -> Conversation | None:
        """Get the active conversation."""
        return self._active_conversation

    def set_active(self, conversation_id: str) -> Conversation | None:
        """Set the active conversation."""
        conv = self.store.load(conversation_id)
        if conv:
            self._active_conversation = conv
        return conv

__all__ = [
    # Enums
    "MessageRole",
    # Data classes
    "HistoryMessage",
    "Conversation",
    # Stores
    "InMemoryHistoryStore",
    "FileHistoryStore",
    "SQLiteHistoryStore",
    # Manager
    "ConversationManager",
]
