from pathlib import Path
from typing import Any, ClassVar

from codomyrmex.ide import IDEStatus
from codomyrmex.logging_monitoring import get_logger

from ._artifacts import AntigravityArtifactsMixin
from ._files import AntigravityFilesMixin
from ._tools import AntigravityToolsMixin
from .models import (
    ConversationContext,
    IDEClient,
)

logger = get_logger(__name__)


class _AntigravityClientMixin:
    """Mixin that provides lazy-init access to a shared AntigravityClient.

    Subclasses must initialise ``self._client = None`` (or an existing client)
    in their own ``__init__``.
    """

    _client: Any

    @property
    def client(self) -> "AntigravityClient":
        """Lazy-initialise and return the AntigravityClient instance."""
        if self._client is None:
            self._client = AntigravityClient()
        return self._client


class AntigravityClient(
    IDEClient, AntigravityArtifactsMixin, AntigravityFilesMixin, AntigravityToolsMixin
):
    """Client for interacting with Antigravity IDE.

    Provides programmatic access to Antigravity's capabilities including
    tool invocation, artifact management, and context access.

    Attributes:
        artifact_dir: Path to the Antigravity artifacts directory.
        conversation_id: Current conversation ID if connected.
    """

    # Available Antigravity tools
    TOOLS: ClassVar[list] = [
        "task_boundary",
        "notify_user",
        "write_to_file",
        "replace_file_content",
        "multi_replace_file_content",
        "view_file",
        "view_file_outline",
        "view_code_item",
        "run_command",
        "command_status",
        "send_command_input",
        "find_by_name",
        "grep_search",
        "list_dir",
        "browser_subagent",
        "generate_image",
        "search_web",
        "read_url_content",
    ]

    # Supported artifact types
    ARTIFACT_TYPES: ClassVar[list] = [
        "task",
        "implementation_plan",
        "walkthrough",
        "other",
    ]

    def __init__(self, artifact_dir: str | None = None):
        """Initialize the Antigravity client.

        Args:
            artifact_dir: Optional path to artifacts directory.
                         Defaults to ~/.gemini/antigravity/brain/
        """
        super().__init__()
        self._connected = False
        self._conversation_id: str | None = None
        self._context: ConversationContext | None = None

        if artifact_dir:
            self.artifact_dir = Path(artifact_dir)
        else:
            self.artifact_dir = Path.home() / ".gemini" / "antigravity" / "brain"

    def connect(self) -> bool:
        """Establish connection to Antigravity session.

        Attempts to detect an active Antigravity session by checking
        for conversation artifacts.

        Returns:
            bool: True if connection successful.

        Raises:
            ConnectionError: If no active session found.
        """
        self._status = IDEStatus.CONNECTING

        if self.artifact_dir.exists():
            conversations = [
                d
                for d in self.artifact_dir.iterdir()
                if d.is_dir() and not d.name.startswith(".")
            ]
            if conversations:
                # Sort by modification time, most recent first
                conversations.sort(key=lambda p: p.stat().st_mtime, reverse=True)
                self._conversation_id = conversations[0].name
                self._connected = True
                self._status = IDEStatus.CONNECTED
                self._context = self._load_context()
                self.emit_event("connected", {"conversation_id": self._conversation_id})
                return True

        self._connected = False
        self._status = IDEStatus.DISCONNECTED
        return False

    def disconnect(self) -> None:
        """Disconnect from Antigravity session."""
        self._connected = False
        self._conversation_id = None
        self._context = None
        self._status = IDEStatus.DISCONNECTED
        self.emit_event("disconnected", None)

    def is_connected(self) -> bool:
        """Check if currently connected.

        Returns:
            bool: True if connected.
        """
        return self._connected

    def get_capabilities(self) -> dict[str, Any]:
        """Get Antigravity capabilities.

        Returns:
            dict containing available tools and features.
        """
        return {
            "name": "Antigravity",
            "version": "1.0.0",
            "provider": "Google DeepMind",
            "tools": self.TOOLS.copy(),
            "artifact_types": self.ARTIFACT_TYPES.copy(),
            "features": [
                "artifact_management",
                "task_tracking",
                "browser_automation",
                "code_editing",
                "file_operations",
                "command_execution",
                "web_search",
                "image_generation",
            ],
            "connected": self._connected,
            "conversation_id": self._conversation_id,
            "status": self._status.value if self._status else "unknown",
        }

    # Antigravity-specific methods

    def get_conversation_id(self) -> str | None:
        """Get the current conversation ID.

        Returns:
            Conversation ID or None if not connected.
        """
        return self._conversation_id

    def list_conversations(self, limit: int = 10) -> list[dict[str, Any]]:
        """list recent conversations.

        Args:
            limit: Maximum number of conversations to return.

        Returns:
            list of conversation metadata.
        """
        if not self.artifact_dir.exists():
            return []

        conversations = []
        dirs = [
            d
            for d in self.artifact_dir.iterdir()
            if d.is_dir() and not d.name.startswith(".")
        ]
        dirs.sort(key=lambda p: p.stat().st_mtime, reverse=True)

        for d in dirs[:limit]:
            artifacts = list(d.glob("*.md"))
            conversations.append(
                {
                    "id": d.name,
                    "path": str(d),
                    "artifact_count": len(artifacts),
                    "modified": d.stat().st_mtime,
                    "is_current": d.name == self._conversation_id,
                }
            )

        return conversations

    def switch_conversation(self, conversation_id: str) -> bool:
        """Switch to a different conversation.

        Args:
            conversation_id: ID of the conversation to switch to.

        Returns:
            bool: True if switch successful.
        """
        conversation_dir = self.artifact_dir / conversation_id
        if not conversation_dir.exists():
            return False

        self._conversation_id = conversation_id
        self._context = self._load_context()

        self.emit_event("conversation_switched", {"conversation_id": conversation_id})

        return True

    def get_session_stats(self) -> dict[str, Any]:
        """Get statistics about the current session."""
        return {
            "connected": self._connected,
            "conversation_id": self._conversation_id,
            "artifact_count": len(self._context.artifacts) if self._context else 0,
            "commands_executed": len(self.command_history),
            "success_rate": self.get_success_rate(),
            "last_command": self.get_last_command().to_dict()
            if self.get_last_command()
            else None,
        }
