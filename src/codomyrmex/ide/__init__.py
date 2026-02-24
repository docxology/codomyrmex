"""IDE Integration Module.

Provides programmatic integration and automation capabilities for various
Integrated Development Environments including Antigravity, Cursor, and VS Code.

This module enables AI agents to achieve maximum agentic operation of IDEs
themselves, allowing sophisticated control and automation of development workflows.

Submodules:
    antigravity: Integration with Google DeepMind's Antigravity IDE
    cursor: Integration with Cursor AI-first code editor
    vscode: Integration with Visual Studio Code

Example:
    >>> from codomyrmex.ide import IDEClient
    >>> # Subclass IDEClient for specific IDE implementations
"""

import logging
import time
from abc import ABC, abstractmethod

# Shared schemas for cross-module interop
try:
    from codomyrmex.validation.schemas import Result, ResultStatus
except ImportError:
    Result = None
    ResultStatus = None
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
from collections.abc import Callable


class IDEStatus(Enum):
    """Status of an IDE session."""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"


@dataclass
class IDECommand:
    """Represents an IDE command to be executed."""
    name: str
    args: dict[str, Any] = field(default_factory=dict)
    timeout: float = 30.0

    def to_dict(self) -> dict[str, Any]:
        """Execute To Dict operations natively."""
        return {"name": self.name, "args": self.args, "timeout": self.timeout}


@dataclass
class IDECommandResult:
    """Result of an IDE command execution."""
    success: bool
    command: str
    output: Any = None
    error: str | None = None
    execution_time: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Execute To Dict operations natively."""
        return {
            "success": self.success,
            "command": self.command,
            "output": self.output,
            "error": self.error,
            "execution_time": self.execution_time,
        }


@dataclass
class FileInfo:
    """Information about a file in the IDE."""
    path: str
    name: str
    is_modified: bool = False
    language: str | None = None
    line_count: int | None = None

    def to_dict(self) -> dict[str, Any]:
        """Execute To Dict operations natively."""
        return {
            "path": self.path,
            "name": self.name,
            "is_modified": self.is_modified,
            "language": self.language,
            "line_count": self.line_count,
        }


class IDEClient(ABC):
    """Abstract base class for IDE integrations.

    All IDE-specific clients should inherit from this class and implement
    the required abstract methods to ensure a consistent API across integrations.
    """

    def __init__(self):
        """Initialize the IDE client."""
        self._status = IDEStatus.DISCONNECTED
        self._command_history: list[IDECommandResult] = []
        self._event_handlers: dict[str, list[Callable]] = {}

    @property
    def status(self) -> IDEStatus:
        """Get the current connection status."""
        return self._status

    @property
    def command_history(self) -> list[IDECommandResult]:
        """Get the history of executed commands."""
        return self._command_history.copy()

    @abstractmethod
    def connect(self) -> bool:
        """Establish connection to the IDE."""
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Disconnect from the IDE."""
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        """Check if currently connected to the IDE."""
        pass

    @abstractmethod
    def get_capabilities(self) -> dict[str, Any]:
        """Get the capabilities of this IDE integration."""
        pass

    @abstractmethod
    def execute_command(self, command: str, args: dict | None = None) -> Any:
        """Execute an IDE command."""
        pass

    @abstractmethod
    def get_active_file(self) -> str | None:
        """Get the path of the currently active file."""
        pass

    @abstractmethod
    def open_file(self, path: str) -> bool:
        """Open a file in the IDE."""
        pass

    @abstractmethod
    def get_open_files(self) -> list[str]:
        """Get list of currently open files."""
        pass

    def execute_command_safe(
        self,
        command: str,
        args: dict | None = None,
        timeout: float = 30.0
    ) -> IDECommandResult:
        """Execute a command with error handling and timing."""
        start_time = time.time()
        try:
            result = self.execute_command(command, args)
            execution_time = time.time() - start_time
            cmd_result = IDECommandResult(
                success=True,
                command=command,
                output=result,
                execution_time=execution_time,
            )
        except Exception as e:
            execution_time = time.time() - start_time
            cmd_result = IDECommandResult(
                success=False,
                command=command,
                error=str(e),
                execution_time=execution_time,
            )

        self._command_history.append(cmd_result)
        return cmd_result

    def execute_batch(
        self,
        commands: list[IDECommand],
        stop_on_error: bool = True
    ) -> list[IDECommandResult]:
        """Execute multiple commands in sequence."""
        results = []
        for cmd in commands:
            result = self.execute_command_safe(cmd.name, cmd.args, cmd.timeout)
            results.append(result)
            if stop_on_error and not result.success:
                break
        return results

    def get_file_info(self, path: str) -> FileInfo | None:
        """Get information about a file."""
        file_path = Path(path)
        if not file_path.exists():
            return None

        ext_to_lang = {
            ".py": "python", ".js": "javascript", ".ts": "typescript",
            ".java": "java", ".go": "go", ".rs": "rust",
            ".c": "c", ".cpp": "cpp", ".md": "markdown",
            ".json": "json", ".yaml": "yaml", ".yml": "yaml",
        }

        language = ext_to_lang.get(file_path.suffix.lower())

        try:
            line_count = len(file_path.read_text().splitlines())
        except Exception:
            line_count = None

        return FileInfo(
            path=str(file_path.absolute()),
            name=file_path.name,
            language=language,
            line_count=line_count,
        )

    def register_event_handler(self, event: str, handler: Callable) -> None:
        """Register a handler for an IDE event."""
        if event not in self._event_handlers:
            self._event_handlers[event] = []
        self._event_handlers[event].append(handler)

    def emit_event(self, event: str, data: Any = None) -> None:
        """Emit an event to all registered handlers."""
        if event in self._event_handlers:
            for handler in self._event_handlers[event]:
                try:
                    handler(data)
                except Exception as e:
                    logging.getLogger(__name__).warning("Event handler failed for %r: %s", event, e)

    def clear_command_history(self) -> None:
        """Clear the command execution history."""
        self._command_history.clear()

    def get_last_command(self) -> IDECommandResult | None:
        """Get the most recent command result."""
        if self._command_history:
            return self._command_history[-1]
        return None

    def get_success_rate(self) -> float:
        """Calculate the command success rate."""
        if not self._command_history:
            return 1.0
        successes = sum(1 for cmd in self._command_history if cmd.success)
        return successes / len(self._command_history)


from codomyrmex.exceptions import (
    ArtifactError,
    CommandExecutionError,
    IDEError,
    SessionError,
)
from codomyrmex.exceptions import (
    IDEConnectionError as ConnectionError,
)

# Import submodule clients
from codomyrmex.ide.cursor import CursorClient

def cli_commands():
    """Return CLI commands for the IDE module."""
    def _list_extensions():
        """List IDE extensions."""
        print("IDE Integration Extensions:")
        print("  cursor    - Cursor AI-first code editor")
        print("  vscode    - Visual Studio Code")
        print("  antigravity - Google DeepMind Antigravity IDE")

    def _ide_status():
        """Show IDE integration status."""
        print("IDE Module Status:")
        print(f"  IDEClient: available (abstract base)")
        print(f"  CursorClient: {'available' if CursorClient else 'unavailable'}")
        print(f"  Statuses: {', '.join(s.value for s in IDEStatus)}")

    return {
        "extensions": _list_extensions,
        "status": _ide_status,
    }


__all__ = [
    "IDEClient",
    "IDEStatus",
    "IDECommand",
    "IDECommandResult",
    "FileInfo",
    "IDEError",
    "ConnectionError",
    "CommandExecutionError",
    "SessionError",
    "ArtifactError",
    # Submodule clients
    "CursorClient",
    "cli_commands",
]
