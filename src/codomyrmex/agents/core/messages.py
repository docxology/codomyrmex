"""Typed agent message protocol.

Provides ``AgentMessage`` — a structured, serializable message format for
inter-agent and agent-LLM communication.  This replaces raw ``dict`` usage
in the ReAct loop and should be the standard transport between all agent
components.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class MessageRole(str, Enum):
    """Standard message roles."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


@dataclass
class ToolCall:
    """A tool invocation requested by the agent."""

    name: str
    arguments: dict[str, Any] = field(default_factory=dict)
    call_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])


@dataclass
class ToolResult:
    """Result from executing a tool call."""

    call_id: str
    output: Any = None
    error: str | None = None

    @property
    def is_success(self) -> bool:
        """Return True if the tool call succeeded."""
        return self.error is None


@dataclass
class AgentMessage:
    """A single message in an agent conversation.

    This is the canonical message type for all agent interactions.  It is
    compatible with the existing ``session.Message`` (role + content) but
    adds structured tool calls, timestamps, and unique IDs.

    Attributes:
        role: The role of the message sender.
        content: Text content of the message.
        tool_calls: Optional list of tool invocations.
        tool_results: Optional list of tool execution results.
        metadata: Free-form metadata dict.
        timestamp: UTC timestamp of message creation.
        message_id: Unique identifier.
    """

    role: MessageRole
    content: str
    tool_calls: list[ToolCall] = field(default_factory=list)
    tool_results: list[ToolResult] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    message_id: str = field(default_factory=lambda: uuid.uuid4().hex)

    # ------------------------------------------------------------------
    # Conversion helpers
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a plain dictionary."""
        d: dict[str, Any] = {
            "role": self.role.value,
            "content": self.content,
            "message_id": self.message_id,
            "timestamp": self.timestamp.isoformat(),
        }
        if self.tool_calls:
            d["tool_calls"] = [
                {"name": tc.name, "arguments": tc.arguments, "call_id": tc.call_id}
                for tc in self.tool_calls
            ]
        if self.tool_results:
            d["tool_results"] = [
                {"call_id": tr.call_id, "output": tr.output, "error": tr.error}
                for tr in self.tool_results
            ]
        if self.metadata:
            d["metadata"] = self.metadata
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AgentMessage:
        """Deserialize from a plain dictionary."""
        tool_calls = [
            ToolCall(name=tc["name"], arguments=tc.get("arguments", {}), call_id=tc.get("call_id", ""))
            for tc in data.get("tool_calls", [])
        ]
        tool_results = [
            ToolResult(call_id=tr["call_id"], output=tr.get("output"), error=tr.get("error"))
            for tr in data.get("tool_results", [])
        ]
        return cls(
            role=MessageRole(data["role"]),
            content=data["content"],
            tool_calls=tool_calls,
            tool_results=tool_results,
            metadata=data.get("metadata", {}),
            timestamp=datetime.fromisoformat(data["timestamp"]) if "timestamp" in data else datetime.now(timezone.utc),
            message_id=data.get("message_id", uuid.uuid4().hex),
        )

    def to_llm_dict(self) -> dict[str, str]:
        """Convert to the minimal ``{"role": ..., "content": ...}`` format
        expected by most LLM chat APIs."""
        return {"role": self.role.value, "content": self.content}

    @classmethod
    def system(cls, content: str, **kwargs: Any) -> AgentMessage:
        """Create a system message."""
        return cls(role=MessageRole.SYSTEM, content=content, **kwargs)

    @classmethod
    def user(cls, content: str, **kwargs: Any) -> AgentMessage:
        """Create a user message."""
        return cls(role=MessageRole.USER, content=content, **kwargs)

    @classmethod
    def assistant(cls, content: str, **kwargs: Any) -> AgentMessage:
        """Create an assistant message."""
        return cls(role=MessageRole.ASSISTANT, content=content, **kwargs)

    @classmethod
    def tool(cls, content: str, results: list[ToolResult] | None = None, **kwargs: Any) -> AgentMessage:
        """Create a tool result message."""
        return cls(role=MessageRole.TOOL, content=content, tool_results=results or [], **kwargs)
