"""
Conversation memory management for LLMs.

Provides different memory strategies for maintaining context across conversations.
"""

import hashlib
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional


class MemoryType(Enum):
    """Types of memory strategies."""
    BUFFER = "buffer"
    WINDOW = "window"
    SUMMARY = "summary"
    VECTOR = "vector"
    ENTITY = "entity"


@dataclass
class MemoryMessage:
    """A message stored in memory."""
    role: str
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)
    token_count: int | None = None

    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary representation of this object."""
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'MemoryMessage':
        """from Dict ."""
        return cls(
            role=data["role"],
            content=data["content"],
            timestamp=datetime.fromisoformat(data.get("timestamp", datetime.now().isoformat())),
            metadata=data.get("metadata", {}),
        )


class Memory(ABC):
    """Abstract base class for conversation memory."""

    memory_type: MemoryType

    def __init__(self, session_id: str | None = None):
        """Initialize this instance."""
        self.session_id = session_id or self._generate_session_id()
        self.messages: list[MemoryMessage] = []

    def _generate_session_id(self) -> str:
        """generate Session Id ."""
        return hashlib.sha256(str(datetime.now().timestamp()).encode()).hexdigest()[:16]

    @abstractmethod
    def add_message(self, role: str, content: str, **metadata) -> None:
        """Add a message to memory."""
        pass

    @abstractmethod
    def get_messages(self) -> list[dict[str, str]]:
        """Get messages in format suitable for LLM API."""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear the memory."""
        pass

    def add_user_message(self, content: str, **metadata) -> None:
        """Add a user message."""
        self.add_message("user", content, **metadata)

    def add_assistant_message(self, content: str, **metadata) -> None:
        """Add an assistant message."""
        self.add_message("assistant", content, **metadata)

    def add_system_message(self, content: str, **metadata) -> None:
        """Add a system message."""
        self.add_message("system", content, **metadata)

    def to_json(self) -> str:
        """Serialize memory to JSON."""
        return json.dumps({
            "session_id": self.session_id,
            "memory_type": self.memory_type.value,
            "messages": [m.to_dict() for m in self.messages],
        })

    @property
    def message_count(self) -> int:
        """message Count ."""
        return len(self.messages)


class BufferMemory(Memory):
    """Simple buffer memory that stores all messages."""

    memory_type = MemoryType.BUFFER

    def __init__(self, session_id: str | None = None, max_messages: int | None = None):
        """Initialize this instance."""
        super().__init__(session_id)
        self.max_messages = max_messages

    def add_message(self, role: str, content: str, **metadata) -> None:
        """add Message ."""
        message = MemoryMessage(role=role, content=content, metadata=metadata)
        self.messages.append(message)

        if self.max_messages and len(self.messages) > self.max_messages:
            # Keep system messages, remove oldest non-system messages
            system_msgs = [m for m in self.messages if m.role == "system"]
            other_msgs = [m for m in self.messages if m.role != "system"]
            keep_count = self.max_messages - len(system_msgs)
            self.messages = system_msgs + other_msgs[-keep_count:]

    def get_messages(self) -> list[dict[str, str]]:
        """get Messages ."""
        return [{"role": m.role, "content": m.content} for m in self.messages]

    def clear(self) -> None:
        """clear ."""
        self.messages = []


class WindowMemory(Memory):
    """Sliding window memory that keeps the last N messages."""

    memory_type = MemoryType.WINDOW

    def __init__(self, session_id: str | None = None, window_size: int = 10):
        """Initialize this instance."""
        super().__init__(session_id)
        self.window_size = window_size
        self.system_messages: list[MemoryMessage] = []

    def add_message(self, role: str, content: str, **metadata) -> None:
        """add Message ."""
        message = MemoryMessage(role=role, content=content, metadata=metadata)

        if role == "system":
            self.system_messages.append(message)
        else:
            self.messages.append(message)
            if len(self.messages) > self.window_size:
                self.messages = self.messages[-self.window_size:]

    def get_messages(self) -> list[dict[str, str]]:
        """get Messages ."""
        all_messages = self.system_messages + self.messages
        return [{"role": m.role, "content": m.content} for m in all_messages]

    def clear(self) -> None:
        """clear ."""
        self.messages = []
        self.system_messages = []


class SummaryMemory(Memory):
    """Memory that maintains a running summary of the conversation."""

    memory_type = MemoryType.SUMMARY

    def __init__(
        self,
        session_id: str | None = None,
        summarizer: Callable | None = None,
        summary_threshold: int = 10
    ):
        """Initialize this instance."""
        super().__init__(session_id)
        self.summarizer = summarizer
        self.summary_threshold = summary_threshold
        self.summary: str = ""
        self.recent_messages: list[MemoryMessage] = []

    def add_message(self, role: str, content: str, **metadata) -> None:
        """add Message ."""
        message = MemoryMessage(role=role, content=content, metadata=metadata)
        self.messages.append(message)
        self.recent_messages.append(message)

        if len(self.recent_messages) >= self.summary_threshold and self.summarizer:
            self._update_summary()

    def _update_summary(self) -> None:
        """update Summary ."""
        if not self.summarizer or not self.recent_messages:
            return

        # Build conversation text
        conversation = "\n".join(
            f"{m.role}: {m.content}" for m in self.recent_messages
        )

        prompt = f"""Summarize the following conversation, incorporating any existing summary:

Existing Summary: {self.summary or 'None'}

New Conversation:
{conversation}

Updated Summary:"""

        self.summary = self.summarizer(prompt)
        self.recent_messages = []

    def get_messages(self) -> list[dict[str, str]]:
        """get Messages ."""
        messages = []

        if self.summary:
            messages.append({
                "role": "system",
                "content": f"Previous conversation summary: {self.summary}"
            })

        for m in self.recent_messages:
            messages.append({"role": m.role, "content": m.content})

        return messages

    def clear(self) -> None:
        """clear ."""
        self.messages = []
        self.recent_messages = []
        self.summary = ""


class EntityMemory(Memory):
    """Memory that tracks entities mentioned in the conversation."""

    memory_type = MemoryType.ENTITY

    def __init__(
        self,
        session_id: str | None = None,
        max_entities: int = 50
    ):
        """Initialize this instance."""
        super().__init__(session_id)
        self.entities: dict[str, dict[str, Any]] = {}
        self.max_entities = max_entities

    def add_message(self, role: str, content: str, **metadata) -> None:
        """add Message ."""
        message = MemoryMessage(role=role, content=content, metadata=metadata)
        self.messages.append(message)

        # Extract and update entities from metadata
        if "entities" in metadata:
            for entity_name, entity_info in metadata["entities"].items():
                self._update_entity(entity_name, entity_info)

    def _update_entity(self, name: str, info: dict[str, Any]) -> None:
        """update Entity ."""
        if name in self.entities:
            self.entities[name].update(info)
            self.entities[name]["mentions"] = self.entities[name].get("mentions", 0) + 1
        else:
            if len(self.entities) >= self.max_entities:
                # Remove least mentioned entity
                min_entity = min(self.entities.keys(),
                                key=lambda k: self.entities[k].get("mentions", 0))
                del self.entities[min_entity]

            self.entities[name] = {**info, "mentions": 1}

    def get_entity(self, name: str) -> dict[str, Any] | None:
        """get Entity ."""
        return self.entities.get(name)

    def get_messages(self) -> list[dict[str, str]]:
        """get Messages ."""
        messages = []

        if self.entities:
            entity_summary = "Known entities:\n" + "\n".join(
                f"- {name}: {json.dumps(info)}"
                for name, info in self.entities.items()
            )
            messages.append({"role": "system", "content": entity_summary})

        for m in self.messages[-10:]:  # Last 10 messages
            messages.append({"role": m.role, "content": m.content})

        return messages

    def clear(self) -> None:
        """clear ."""
        self.messages = []
        self.entities = {}


def create_memory(memory_type: MemoryType, **kwargs) -> Memory:
    """Factory function to create memory instances."""
    memories = {
        MemoryType.BUFFER: BufferMemory,
        MemoryType.WINDOW: WindowMemory,
        MemoryType.SUMMARY: SummaryMemory,
        MemoryType.ENTITY: EntityMemory,
    }

    memory_class = memories.get(memory_type)
    if not memory_class:
        raise ValueError(f"Unsupported memory type: {memory_type}")

    return memory_class(**kwargs)


__all__ = [
    "MemoryType",
    "MemoryMessage",
    "Memory",
    "BufferMemory",
    "WindowMemory",
    "SummaryMemory",
    "EntityMemory",
    "create_memory",
]
