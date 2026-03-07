"""Antigravity IDE Integration

Integration with Google DeepMind's Antigravity IDE - the agentic AI coding
assistant. Provides programmatic access to Antigravity's capabilities for
meta-level control and automation.

Example:
    >>> from codomyrmex.ide.antigravity import AntigravityClient
    >>> client = AntigravityClient()
    >>> client.connect()
    >>> capabilities = client.get_capabilities()
"""

from dataclasses import dataclass, field
from typing import Any

try:
    from codomyrmex.ide import (
        ArtifactError,
        CommandExecutionError,
        ConnectionError,
        IDEError,
        SessionError,
    )
except ImportError:
    IDEError = Exception  # type: ignore
    ConnectionError = Exception  # type: ignore
    CommandExecutionError = Exception  # type: ignore
    SessionError = Exception  # type: ignore
    ArtifactError = Exception  # type: ignore


@dataclass
class Artifact:
    """Represents an Antigravity conversation artifact."""

    name: str
    path: str
    artifact_type: str
    content: str | None = None
    size: int = 0
    modified: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "path": self.path,
            "type": self.artifact_type,
            "size": self.size,
            "modified": self.modified,
        }


@dataclass
class ConversationContext:
    """Represents the current Antigravity conversation context."""

    conversation_id: str
    task_name: str | None = None
    task_status: str | None = None
    mode: str | None = None
    artifacts: list[Artifact] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "conversation_id": self.conversation_id,
            "task_name": self.task_name,
            "task_status": self.task_status,
            "mode": self.mode,
            "artifacts": [a.to_dict() for a in self.artifacts],
        }
