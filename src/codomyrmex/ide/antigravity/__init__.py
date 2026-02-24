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
import json
import os
import shutil
import subprocess
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from collections.abc import Callable

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

class AntigravityClient(IDEClient):
    """Client for interacting with Antigravity IDE.

    Provides programmatic access to Antigravity's capabilities including
    tool invocation, artifact management, and context access.

    Attributes:
        artifact_dir: Path to the Antigravity artifacts directory.
        conversation_id: Current conversation ID if connected.
    """

    # Available Antigravity tools
    TOOLS = [
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
    ARTIFACT_TYPES = [
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
            # Find most recent conversation
            conversations = [
                d for d in self.artifact_dir.iterdir()
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
            Dict containing available tools and features.
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

    def execute_command(self, command: str, args: dict | None = None) -> Any:
        """Execute an Antigravity command.

        Note: This method simulates command execution. In a real integration,
        this would interface with the actual Antigravity API.

        Args:
            command: Command name to execute.
            args: Optional command arguments.

        Returns:
            Command result.

        Raises:
            CommandExecutionError: If command execution fails.
        """
        if not self._connected:
            raise CommandExecutionError("Not connected to Antigravity session")

        if command not in self.TOOLS:
            raise CommandExecutionError(f"Unknown command: {command}")

        # Return simulated success response
        return {
            "status": "success",
            "command": command,
            "args": args or {},
            "message": f"Command '{command}' executed successfully",
            "timestamp": datetime.now().isoformat(),
        }

    def get_active_file(self) -> str | None:
        """Get the currently active file in the IDE.

        Returns:
            File path or None if no file is active.
        """
        # In a real integration, this would query the IDE state
        return None

    def open_file(self, path: str) -> bool:
        """Open a file in Antigravity.

        Args:
            path: Path to the file.

        Returns:
            bool: True if successful.
        """
        # In a real integration, this would invoke view_file tool
        return Path(path).exists()

    def get_open_files(self) -> list[str]:
        """Get list of open files.

        Returns:
            List of file paths.
        """
        return []

    # Antigravity-specific methods

    def get_conversation_id(self) -> str | None:
        """Get the current conversation ID.

        Returns:
            Conversation ID or None if not connected.
        """
        return self._conversation_id

    def get_context(self) -> ConversationContext | None:
        """Get the current conversation context.

        Returns:
            ConversationContext or None if not connected.
        """
        return self._context

    def _load_context(self) -> ConversationContext | None:
        """Load conversation context from artifacts."""
        if not self._conversation_id:
            return None

        context = ConversationContext(conversation_id=self._conversation_id)
        context.artifacts = self._scan_artifacts()

        # Try to load task.md for task info
        task_artifact = self._get_artifact_by_name("task")
        if task_artifact:
            context.task_name = "Current Task"
            context.task_status = "Active"

        return context

    def _scan_artifacts(self) -> list[Artifact]:
        """Scan the conversation directory for artifacts."""
        artifacts = []
        if not self._conversation_id:
            return artifacts

        conversation_dir = self.artifact_dir / self._conversation_id
        if not conversation_dir.exists():
            return artifacts

        for item in conversation_dir.iterdir():
            if item.is_file() and item.suffix == ".md":
                # Determine artifact type from name
                artifact_type = "other"
                if item.stem == "task":
                    artifact_type = "task"
                elif "implementation" in item.stem.lower():
                    artifact_type = "implementation_plan"
                elif "walkthrough" in item.stem.lower():
                    artifact_type = "walkthrough"

                artifacts.append(Artifact(
                    name=item.stem,
                    path=str(item),
                    artifact_type=artifact_type,
                    size=item.stat().st_size,
                    modified=item.stat().st_mtime,
                ))

        return artifacts

    def _get_artifact_by_name(self, name: str) -> Artifact | None:
        """Get an artifact by name."""
        if not self._context:
            return None
        for artifact in self._context.artifacts:
            if artifact.name == name:
                return artifact
        return None

    def list_artifacts(self) -> list[dict[str, Any]]:
        """List conversation artifacts.

        Returns:
            List of artifact metadata dictionaries.
        """
        if not self._connected or not self._conversation_id:
            return []

        # Always refresh artifacts on list
        self._context = self._load_context()
        if not self._context:
            return []

        return [a.to_dict() for a in self._context.artifacts]

    def get_artifact(self, name: str) -> dict[str, Any] | None:
        """Get a specific artifact by name.

        Args:
            name: Artifact name (without extension).

        Returns:
            Dict with artifact data including content.
        """
        if not self._connected or not self._conversation_id:
            return None

        conversation_dir = self.artifact_dir / self._conversation_id
        artifact_path = conversation_dir / f"{name}.md"

        if not artifact_path.exists():
            return None

        try:
            content = artifact_path.read_text()
            return {
                "name": name,
                "path": str(artifact_path),
                "content": content,
                "size": len(content),
                "modified": artifact_path.stat().st_mtime,
            }
        except Exception as e:
            return {"error": str(e)}

    def create_artifact(
        self,
        name: str,
        content: str,
        artifact_type: str = "other"
    ) -> dict[str, Any]:
        """Create a new artifact.

        Args:
            name: Artifact name (without extension).
            content: Artifact content.
            artifact_type: Type of artifact (task, implementation_plan, walkthrough, other).

        Returns:
            Dict with artifact metadata.

        Raises:
            ArtifactError: If artifact creation fails.
        """
        if not self._connected or not self._conversation_id:
            raise ArtifactError("Not connected to Antigravity session")

        if artifact_type not in self.ARTIFACT_TYPES:
            raise ArtifactError(f"Invalid artifact type: {artifact_type}")

        conversation_dir = self.artifact_dir / self._conversation_id
        try:
            conversation_dir.mkdir(parents=True, exist_ok=True)

            artifact_path = conversation_dir / f"{name}.md"
            artifact_path.write_text(content)

            # Refresh context
            self._context = self._load_context()

            self.emit_event("artifact_created", {"name": name, "type": artifact_type})

            return {
                "name": name,
                "path": str(artifact_path),
                "type": artifact_type,
                "size": len(content),
                "created": True,
            }
        except Exception as e:
            raise ArtifactError(f"Failed to create artifact: {e}")

    def update_artifact(self, name: str, content: str) -> dict[str, Any]:
        """Update an existing artifact.

        Args:
            name: Artifact name (without extension).
            content: New artifact content.

        Returns:
            Dict with artifact metadata.

        Raises:
            ArtifactError: If artifact doesn't exist or update fails.
        """
        if not self._connected or not self._conversation_id:
            raise ArtifactError("Not connected to Antigravity session")

        conversation_dir = self.artifact_dir / self._conversation_id
        artifact_path = conversation_dir / f"{name}.md"

        if not artifact_path.exists():
            raise ArtifactError(f"Artifact not found: {name}")

        try:
            artifact_path.write_text(content)

            # Refresh context
            self._context = self._load_context()

            self.emit_event("artifact_updated", {"name": name})

            return {
                "name": name,
                "path": str(artifact_path),
                "size": len(content),
                "updated": True,
            }
        except Exception as e:
            raise ArtifactError(f"Failed to update artifact: {e}")

    def delete_artifact(self, name: str) -> bool:
        """Delete an artifact.

        Args:
            name: Artifact name (without extension).

        Returns:
            bool: True if deleted successfully.

        Raises:
            ArtifactError: If artifact doesn't exist.
        """
        if not self._connected or not self._conversation_id:
            raise ArtifactError("Not connected to Antigravity session")

        conversation_dir = self.artifact_dir / self._conversation_id
        artifact_path = conversation_dir / f"{name}.md"

        if not artifact_path.exists():
            raise ArtifactError(f"Artifact not found: {name}")

        try:
            artifact_path.unlink()

            # Refresh context
            self._context = self._load_context()

            self.emit_event("artifact_deleted", {"name": name})

            return True
        except Exception as e:
            raise ArtifactError(f"Failed to delete artifact: {e}")

    def list_conversations(self, limit: int = 10) -> list[dict[str, Any]]:
        """List recent conversations.

        Args:
            limit: Maximum number of conversations to return.

        Returns:
            List of conversation metadata.
        """
        if not self.artifact_dir.exists():
            return []

        conversations = []
        dirs = [
            d for d in self.artifact_dir.iterdir()
            if d.is_dir() and not d.name.startswith(".")
        ]
        dirs.sort(key=lambda p: p.stat().st_mtime, reverse=True)

        for d in dirs[:limit]:
            artifacts = list(d.glob("*.md"))
            conversations.append({
                "id": d.name,
                "path": str(d),
                "artifact_count": len(artifacts),
                "modified": d.stat().st_mtime,
                "is_current": d.name == self._conversation_id,
            })

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

    def get_tool_info(self, tool_name: str) -> dict[str, Any] | None:
        """Get information about a specific tool.

        Args:
            tool_name: Name of the tool.

        Returns:
            Dict with tool information or None if not found.
        """
        tool_info = {
            "task_boundary": {
                "name": "task_boundary",
                "description": "Manage task state and boundaries",
                "parameters": ["TaskName", "Mode", "TaskStatus", "TaskSummary"],
            },
            "notify_user": {
                "name": "notify_user",
                "description": "Send notification to user",
                "parameters": ["Message", "PathsToReview", "BlockedOnUser"],
            },
            "write_to_file": {
                "name": "write_to_file",
                "description": "Create or overwrite a file",
                "parameters": ["TargetFile", "CodeContent", "IsArtifact"],
            },
            "view_file": {
                "name": "view_file",
                "description": "View file contents",
                "parameters": ["AbsolutePath", "StartLine", "EndLine"],
            },
            "view_file_outline": {
                "name": "view_file_outline",
                "description": "View the outline of a file",
                "parameters": ["AbsolutePath", "ItemOffset"],
            },
             "view_code_item": {
                "name": "view_code_item",
                "description": "View specific code items",
                "parameters": ["File", "NodePaths"],
            },
            "run_command": {
                "name": "run_command",
                "description": "Execute a terminal command",
                "parameters": ["CommandLine", "Cwd", "SafeToAutoRun"],
            },
            "grep_search": {
                "name": "grep_search",
                "description": "Search file contents with ripgrep",
                "parameters": ["SearchPath", "Query", "MatchPerLine"],
            },
            "find_by_name": {
                "name": "find_by_name",
                "description": "Find files by name pattern",
                "parameters": ["SearchDirectory", "Pattern", "Extensions"],
            },
            "list_dir": {
                "name": "list_dir",
                "description": "List directory contents",
                "parameters": ["DirectoryPath"],
            },
            "replace_file_content": {
                "name": "replace_file_content",
                "description": "Replace content in a file",
                "parameters": ["TargetFile", "StartLine", "EndLine", "TargetContent", "ReplacementContent"],
            },
             "multi_replace_file_content": {
                "name": "multi_replace_file_content",
                "description": "Make multiple replacements in a file",
                "parameters": ["TargetFile", "ReplacementChunks"],
            },
        }

        return tool_info.get(tool_name)


    def send_chat_gui(self, message: str, app_name: str = "Antigravity") -> IDECommandResult:
        """Send a message using GUI automation (AppleScript).

        This method bypasses the CLI and sends keystrokes directly to the
        active window of the specified application. Useful for targeting
        specific UI panes that the CLI cannot reach.

        Args:
            message: The message to type.
            app_name: The application name to target (default: "Antigravity").

        Returns:
            IDECommandResult indicating success/failure of the AppleScript execution.
        """
        # Escape double quotes for AppleScript
        safe_message = message.replace('"', '\\"')

        apple_script = f'''
        tell application "{app_name}"
            activate
        end tell

        delay 0.5

        tell application "System Events"
            tell process "{app_name}"
                keystroke "{safe_message}"
                delay 0.1
                key code 36
            end tell
        end tell
        '''

        try:
            subprocess.run(["osascript", "-e", apple_script], check=True, capture_output=True)
            return IDECommandResult(
                success=True,
                command="osascript",
                output={"message": message, "method": "gui", "app": app_name}
            )
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode() if e.stderr else str(e)
            return IDECommandResult(
                success=False,
                command="osascript",
                error=f"GUI automation failed: {error_msg}"
            )
        except Exception as e:
            return IDECommandResult(success=False, command="osascript", error=str(e))

    def invoke_tool(self, tool_name: str, parameters: dict[str, Any]) -> IDECommandResult:
        """Invoke an Antigravity tool.

        This is a higher-level method that uses execute_command_safe.

        Args:
            tool_name: Name of the tool to invoke.
            parameters: Tool parameters.

        Returns:
            IDECommandResult with execution details.
        """
        if tool_name not in self.TOOLS:
            return IDECommandResult(
                success=False,
                command=tool_name,
                error=f"Unknown tool: {tool_name}",
            )

        return self.execute_command_safe(tool_name, parameters)

    def send_chat_message(self, message: str, **kwargs) -> IDECommandResult:
        """Send a message to the Antigravity chat.

        Uses the 'antigravity' or 'agy' CLI if available to send a real message
        to the IDE chat interface. Falls back to simulated tool invocation.

        Args:
            message: The message content to send.
            **kwargs: Additional arguments for notify_user.

        Returns:
            IDECommandResult with the execution result.
        """
        # Try real CLI first
        cli = shutil.which("antigravity") or shutil.which("agy")

        if cli:
            try:
                # Build command args
                cmd = [cli, "chat", "--reuse-window"]

                # Add mode if specified
                mode = kwargs.get("mode")
                if mode:
                    cmd.extend(["--mode", mode])

                cmd.append(message)

                # Run the CLI command
                subprocess.run(cmd, check=True, capture_output=True)

                return IDECommandResult(
                    success=True,
                    command=f"{Path(cli).name} chat",
                    output={"message": message, "method": "cli", "cli_path": cli, "mode": mode or "default"}
                )
            except subprocess.CalledProcessError as e:
                # If CLI fails, we continue to fallback but log error
                cli_error = e.stderr.decode() if e.stderr else str(e)
            except Exception as e:
                cli_error = str(e)

        # Fallback implementation
        if not self._connected:
            return IDECommandResult(
                success=False,
                command="notify_user",
                error="Not connected to Antigravity session"
            )

        params = {
            "Message": message,
            "BlockedOnUser": kwargs.get("BlockedOnUser", False),
            "PathsToReview": kwargs.get("PathsToReview", []),
            "ShouldAutoProceed": kwargs.get("ShouldAutoProceed", False)
        }

        return self.invoke_tool("notify_user", params)

    def get_session_stats(self) -> dict[str, Any]:
        """Get statistics about the current session.

        Returns:
            Dict with session statistics.
        """
        return {
            "connected": self._connected,
            "conversation_id": self._conversation_id,
            "artifact_count": len(self._context.artifacts) if self._context else 0,
            "commands_executed": len(self.command_history),
            "success_rate": self.get_success_rate(),
            "last_command": self.get_last_command().to_dict() if self.get_last_command() else None,
        }

# ── Bridge Imports (lazy, optional dependencies) ──────────────────────
try:
    from codomyrmex.ide.antigravity.tool_provider import (
        AntigravityToolProvider,
        SAFE_TOOLS as AG_SAFE_TOOLS,
        DESTRUCTIVE_TOOLS as AG_DESTRUCTIVE_TOOLS,
        CONTROL_TOOLS as AG_CONTROL_TOOLS,
    )
except ImportError:
    AntigravityToolProvider = None
    AG_SAFE_TOOLS = frozenset()
    AG_DESTRUCTIVE_TOOLS = frozenset()
    AG_CONTROL_TOOLS = frozenset()

try:
    from codomyrmex.ide.antigravity.agent_bridge import AntigravityAgent
except ImportError:
    AntigravityAgent = None

try:
    from codomyrmex.ide.antigravity.skill_adapter import (
        AntigravityToolSkill,
        AntigravitySkillFactory,
    )
except ImportError:
    AntigravityToolSkill = None
    AntigravitySkillFactory = None

try:
    from codomyrmex.ide.antigravity.history_bridge import ArtifactHistoryBridge
except ImportError:
    ArtifactHistoryBridge = None

try:
    from codomyrmex.ide.antigravity.agent_relay import AgentRelay, RelayMessage
except ImportError:
    AgentRelay = None
    RelayMessage = None

try:
    from codomyrmex.ide.antigravity.live_bridge import (
        LiveAgentBridge,
        ClaudeCodeEndpoint,
    )
except ImportError:
    LiveAgentBridge = None
    ClaudeCodeEndpoint = None

try:
    from codomyrmex.ide.antigravity.message_scheduler import (
        MessageScheduler,
        SchedulerConfig,
    )
except ImportError:
    MessageScheduler = None
    SchedulerConfig = None

try:
    from codomyrmex.ide.antigravity.relay_endpoint import RelayEndpoint
except ImportError:
    RelayEndpoint = None

try:
    from codomyrmex.ide.antigravity.antigravity_dispatcher import (
        AntigravityDispatcher,
        DispatcherConfig,
    )
except ImportError:
    AntigravityDispatcher = None
    DispatcherConfig = None


__all__ = [
    # Core
    "AntigravityClient",
    "Artifact",
    "ConversationContext",
    # Bridges
    "AntigravityToolProvider",
    "AntigravityAgent",
    "AntigravityToolSkill",
    "AntigravitySkillFactory",
    "ArtifactHistoryBridge",
    # Relay
    "AgentRelay",
    "RelayMessage",
    "LiveAgentBridge",
    "ClaudeCodeEndpoint",
    # Scheduler & Endpoint
    "MessageScheduler",
    "SchedulerConfig",
    "RelayEndpoint",
    "AntigravityDispatcher",
    "DispatcherConfig",
]

