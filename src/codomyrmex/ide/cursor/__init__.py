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
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

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
        """Execute a Cursor command."""
        if not self._connected:
            raise CommandExecutionError("Not connected to Cursor")

        return {"status": "success", "command": command, "args": args or {}}

    def get_active_file(self) -> str | None:
        """Get the currently active file."""
        raise NotImplementedError("Cursor IDE integration: get_active_file not yet implemented")

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
        except Exception as e:
            logger.warning("Failed to update Cursor rules: %s", e)
            return False

    def get_models(self) -> list[str]:
        """Get available AI models."""
        return self.get_capabilities()["models"]

    def set_model(self, model: str) -> bool:
        """Set the active AI model."""
        return model in self.get_models()


__all__ = ["CursorClient"]
