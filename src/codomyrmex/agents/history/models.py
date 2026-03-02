import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


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
        """post Init ."""
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


