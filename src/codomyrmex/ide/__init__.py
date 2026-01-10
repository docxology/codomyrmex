from pathlib import Path
from typing import Any, Optional, Dict, List, Callable
import time

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum











































"""IDE Integration Module

Provides programmatic integration and automation capabilities for various
Integrated Development Environments including Antigravity, Cursor, and VS Code.

This module enables AI agents to achieve maximum agentic operation of IDEs
themselves, allowing sophisticated control and automation of development workflows.

Submodules:
    antigravity: Integration with Google DeepMind's Antigravity IDE
    cursor: Integration with Cursor AI-first code editor
    vscode: Integration with Visual Studio Code

Example:
    >>> from codomyrmex.ide import antigravity
    >>> client = antigravity.AntigravityClient()
    >>> capabilities = client.get_capabilities()
# AGGRESSIVE_REMOVAL_GARBAGE_DOC: # AGGRESSIVE_REMOVAL: """

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
    args: Dict[str, Any] = field(default_factory=dict)
    timeout: float = 30.0
    
    def to_dict(self) -> Dict[str, Any]:


        return {"name": self.name, "args": self.args, "timeout": self.timeout}


@dataclass
class IDECommandResult:
    """Result of an IDE command execution."""
    success: bool
    command: str
    output: Any = None
    error: Optional[str] = None
    execution_time: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:


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
    language: Optional[str] = None
    line_count: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:


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
    
    Provides both abstract methods that must be implemented and concrete 
    helper methods that work across all IDE implementations.
# AGGRESSIVE_REMOVAL_GARBAGE_DOC: # AGGRESSIVE_REMOVAL:     """
    
    def __init__(self):
        """Initialize the IDE client."""
        self._status = IDEStatus.DISCONNECTED
        self._command_history: List[IDECommandResult] = []
        self._event_handlers: Dict[str, List[Callable]] = {}
    
    @property
    def status(self) -> IDEStatus:
        """Get the current connection status."""
        return self._status
    
    @property
    def command_history(self) -> List[IDECommandResult]:
        """Get the history of executed commands."""
        return self._command_history.copy()
    
    # Abstract methods that must be implemented
    @abstractmethod
    def connect(self) -> bool:
        """Establish connection to the IDE.
        
        Returns:
            bool: True if connection successful, False otherwise.
# AGGRESSIVE_REMOVAL_GARBAGE_DOC: # AGGRESSIVE_REMOVAL:         """
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """Disconnect from the IDE."""
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        """Check if currently connected to the IDE.
        
        Returns:
            bool: True if connected, False otherwise.
# AGGRESSIVE_REMOVAL_GARBAGE_DOC: # AGGRESSIVE_REMOVAL:         """
        pass
    
    @abstractmethod
    def get_capabilities(self) -> Dict[str, Any]:
        """Get the capabilities of this IDE integration.
        
        Returns:
            Dict containing capability information.
# AGGRESSIVE_REMOVAL_GARBAGE_DOC: # AGGRESSIVE_REMOVAL:         """
        pass
    
    @abstractmethod
    def execute_command(self, command: str, args: Optional[Dict] = None) -> Any:
        """Execute an IDE command.
        
        Args:
            command: The command to execute.
            args: Optional arguments for the command.
            
        Returns:
            The result of the command execution.
# AGGRESSIVE_REMOVAL_GARBAGE_DOC: # AGGRESSIVE_REMOVAL:         """
        pass
    
    @abstractmethod
    def get_active_file(self) -> Optional[str]:
        """Get the path of the currently active file.
        
        Returns:
            The file path or None if no file is active.
# AGGRESSIVE_REMOVAL_GARBAGE_DOC: # AGGRESSIVE_REMOVAL:         """
        pass
    
    @abstractmethod
    def open_file(self, path: str) -> bool:
        """Open a file in the IDE.
        
        Args:
            path: Path to the file to open.
            
        Returns:
            bool: True if file opened successfully.
# AGGRESSIVE_REMOVAL_GARBAGE_DOC: # AGGRESSIVE_REMOVAL:         """
        pass
    
    @abstractmethod
    def get_open_files(self) -> List[str]:
        """Get list of currently open files.
        
        Returns:
            List of file paths.
# AGGRESSIVE_REMOVAL_GARBAGE_DOC: # AGGRESSIVE_REMOVAL:         """
        pass
    
    # Concrete helper methods available to all implementations
    def execute_command_safe(
        self, 
        command: str, 
        args: Optional[Dict] = None,
        timeout: float = 30.0
    ) -> IDECommandResult:
        """Execute a command with error handling and timing.
        
        Args:
            command: The command to execute.
            args: Optional arguments for the command.
            timeout: Maximum execution time in seconds.
            
        Returns:
            IDECommandResult with success status and output.
# AGGRESSIVE_REMOVAL_GARBAGE_DOC: # AGGRESSIVE_REMOVAL:         """
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
        commands: List[IDECommand],
        stop_on_error: bool = True
    ) -> List[IDECommandResult]:
        """Execute multiple commands in sequence.
        
        Args:
            commands: List of IDECommand objects to execute.
            stop_on_error: If True, stop execution on first error.
            
        Returns:
            List of IDECommandResult objects.
# AGGRESSIVE_REMOVAL_GARBAGE_DOC: # AGGRESSIVE_REMOVAL:         """
        results = []
        for cmd in commands:
            result = self.execute_command_safe(cmd.name, cmd.args, cmd.timeout)
            results.append(result)
            if stop_on_error and not result.success:
                break
        return results
    
    def get_file_info(self, path: str) -> Optional[FileInfo]:
        """Get information about a file.
        
        Args:
            path: Path to the file.
            
        Returns:
            FileInfo object or None if file not found.
# AGGRESSIVE_REMOVAL_GARBAGE_DOC: # AGGRESSIVE_REMOVAL:         """
        file_path = Path(path)
        if not file_path.exists():
            return None
        
        # Detect language from extension
        ext_to_lang = {
            ".py": "python",
            ".js": "javascript", 
            ".ts": "typescript",
            ".java": "java",
            ".go": "go",
            ".rs": "rust",
            ".c": "c",
            ".cpp": "cpp",
            ".md": "markdown",
            ".json": "json",
            ".yaml": "yaml",
            ".yml": "yaml",
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
        """Register a handler for an IDE event.
        
        Args:
            event: Event name to listen for.
            handler: Callable to invoke when event occurs.
# AGGRESSIVE_REMOVAL_GARBAGE_DOC: # AGGRESSIVE_REMOVAL:         """
        if event not in self._event_handlers:
            self._event_handlers[event] = []
        self._event_handlers[event].append(handler)
    
    def emit_event(self, event: str, data: Any = None) -> None:
        """Emit an event to all registered handlers.
        
        Args:
            event: Event name.
            data: Event data to pass to handlers.
# AGGRESSIVE_REMOVAL_GARBAGE_DOC: # AGGRESSIVE_REMOVAL:         """
        if event in self._event_handlers:
            for handler in self._event_handlers[event]:
                try:
                    handler(data)
                except Exception:
                    pass  # Don't let handler errors break emission
    
    def clear_command_history(self) -> None:
        """Clear the command execution history."""
        self._command_history.clear()
    
    def get_last_command(self) -> Optional[IDECommandResult]:
        """Get the most recent command result.
        
        Returns:
            The last IDECommandResult or None if no commands executed.
# AGGRESSIVE_REMOVAL_GARBAGE_DOC: # AGGRESSIVE_REMOVAL:         """
        if self._command_history:
            return self._command_history[-1]
        return None
    
    def get_success_rate(self) -> float:
        """Calculate the command success rate.
        
        Returns:
            Success rate as a float between 0.0 and 1.0.
# AGGRESSIVE_REMOVAL_GARBAGE_DOC: # AGGRESSIVE_REMOVAL:         """
        if not self._command_history:
            return 1.0
        successes = sum(1 for cmd in self._command_history if cmd.success)
        return successes / len(self._command_history)


class IDEError(Exception):
    """Base exception for IDE-related errors."""
    pass


class ConnectionError(IDEError):
    """Raised when IDE connection fails."""
    pass


class CommandExecutionError(IDEError):
    """Raised when an IDE command fails to execute."""
    pass


class SessionError(IDEError):
    """Raised when there's a session-related error."""
    pass


class ArtifactError(IDEError):
    """Raised when artifact operations fail."""
    pass


__all__ = [
    # Base classes
    "IDEClient",
    "IDEStatus",
    "IDECommand",
    "IDECommandResult",
    "FileInfo",
    # Exceptions
    "IDEError",
    "ConnectionError",
    "CommandExecutionError",
    "SessionError",
    "ArtifactError",
]
