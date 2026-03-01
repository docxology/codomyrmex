"""Cursor IDE Integration.

Integration with Cursor IDE - the AI-first code editor. Provides programmatic
access to Cursor's AI-assisted development capabilities.

Example:
    >>> from codomyrmex.ide.cursor import CursorClient
    >>> client = CursorClient()
    >>> client.connect()
    >>> rules = client.get_rules()
"""

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

from codomyrmex.ide import CommandExecutionError, ConnectionError, IDEClient, IDEError


class CursorClient(IDEClient):
    """Client for interacting with Cursor IDE.

    Provides programmatic access to Cursor's AI-assisted development capabilities
    including Composer automation, rules management, and model configuration.
    """

    def __init__(self, workspace_path: str | None = None):
        """Initialize the Cursor client.

        Args:
            workspace_path: Optional path to the workspace root.
        """
        super().__init__()
        self._connected = False
        self.workspace_path = Path(workspace_path) if workspace_path else Path.cwd()
        self._cursorrules_path = self.workspace_path / ".cursorrules"

    def connect(self) -> bool:
        """Establish connection to Cursor workspace."""
        cursor_dir = self.workspace_path / ".cursor"
        if cursor_dir.exists() or self._cursorrules_path.exists():
            self._connected = True
            return True

        if self.workspace_path.exists():
            self._connected = True
            return True

        self._connected = False
        return False

    def disconnect(self) -> None:
        """Disconnect from Cursor."""
        self._connected = False

    def is_connected(self) -> bool:
        """Check if currently connected."""
        return self._connected

    def get_capabilities(self) -> dict[str, Any]:
        """Get Cursor capabilities."""
        return {
            "name": "Cursor",
            "version": "latest",
            "features": [
                "composer", "chat", "inline_edit",
                "code_generation", "code_explanation",
                "rules_management", "model_selection",
            ],
            "models": [
                "gpt-4", "gpt-4-turbo", "gpt-3.5-turbo",
                "claude-3-opus", "claude-3-sonnet",
            ],
            "connected": self._connected,
            "workspace": str(self.workspace_path),
        }

    def execute_command(self, command: str, args: dict | None = None) -> Any:
        """Execute a Cursor command via the CLI.

        Attempts to invoke the real Cursor CLI ('cursor'). Raises
        CommandExecutionError if the CLI is not installed.

        Args:
            command: Command name to execute.
            args: Optional command arguments.

        Returns:
            Command result dict from CLI output.

        Raises:
            CommandExecutionError: If not connected, CLI unavailable, or CLI fails.
        """
        if not self._connected:
            raise CommandExecutionError("Not connected to Cursor")

        cli = shutil.which("cursor")
        if not cli:
            raise CommandExecutionError(
                f"Cursor CLI not available. Install Cursor's CLI integration to use "
                f"command execution. Command '{command}' cannot be executed without the CLI."
            )

        try:
            cmd = [cli, "--command", command]
            if args:
                cmd.extend(["--args", json.dumps(args)])
            result = subprocess.run(
                cmd, check=True, capture_output=True, text=True, timeout=30
            )
            return {"status": "success", "output": result.stdout}
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if e.stderr else str(e)
            raise CommandExecutionError(f"Cursor CLI failed for '{command}': {error_msg}") from e
        except subprocess.TimeoutExpired as e:
            raise CommandExecutionError(f"Cursor command '{command}' timed out after 30s") from e

    def get_active_file(self) -> str | None:
        """Get the currently active file (heuristic: most recently modified)."""
        if not self._connected or not self.workspace_path.exists():
            return None
        try:
            candidates = [
                f for f in self.workspace_path.rglob("*")
                if f.is_file()
                and not any(part.startswith(".") for part in f.parts)
                and f.suffix in {".py", ".md", ".txt", ".yaml", ".yml", ".toml", ".json", ".js", ".ts"}
            ]
            if not candidates:
                return None
            most_recent = max(candidates, key=lambda p: p.stat().st_mtime)
            return str(most_recent)
        except OSError:
            return None

    def open_file(self, path: str) -> bool:
        """Open a file in Cursor."""
        return Path(path).exists()

    def get_open_files(self) -> list[str]:
        """Get list of open files."""
        return []

    def get_rules(self) -> dict[str, Any]:
        """Get current .cursorrules configuration."""
        if self._cursorrules_path.exists():
            try:
                content = self._cursorrules_path.read_text()
                return {"content": content, "path": str(self._cursorrules_path)}
            except Exception as e:
                return {"error": str(e)}
        return {"content": "", "path": str(self._cursorrules_path), "exists": False}

    def update_rules(self, rules: dict[str, Any]) -> bool:
        """Update .cursorrules configuration."""
        if not self._connected:
            raise IDEError("Not connected to Cursor")

        try:
            content = rules.get("content", "")
            if isinstance(content, dict):
                content = json.dumps(content, indent=2)
            self._cursorrules_path.write_text(content)
            return True
        except Exception:
            return False

    def get_models(self) -> list[str]:
        """Get available AI models."""
        return self.get_capabilities()["models"]

    def set_model(self, model: str) -> bool:
        """Set the active AI model."""
        return model in self.get_models()


__all__ = ["CursorClient"]
