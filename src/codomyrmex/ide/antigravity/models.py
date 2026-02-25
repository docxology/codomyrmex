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
        FileInfo,
        IDEClient,
        IDECommand,
        IDECommandResult,
        IDEError,
        IDEStatus,
        SessionError,
    )
except ImportError:
    # Fallback if ide module not available
    IDEClient = object
    IDEStatus = None
    IDECommand = None
    IDECommandResult = None
    FileInfo = None
    IDEError = Exception
    ConnectionError = Exception
    CommandExecutionError = Exception
    SessionError = Exception
    ArtifactError = Exception



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
        """Execute To Dict operations natively."""
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
        """Execute To Dict operations natively."""
        return {
            "conversation_id": self.conversation_id,
            "task_name": self.task_name,
            "task_status": self.task_status,
            "mode": self.mode,
            "artifacts": [a.to_dict() for a in self.artifacts],
        }

