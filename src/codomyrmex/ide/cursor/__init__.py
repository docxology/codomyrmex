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
from pathlib import Path
from typing import Any

from codomyrmex.ide import CommandExecutionError, IDEClient, IDEError, IDEStatus
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


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
        self._open_files: list[Path] = []
        self._active_model: str | None = None

        # Keep this list explicit and stable to avoid hidden behavior changes.
        self._models = [
            "gpt-4",
            "gpt-4-turbo",
            "gpt-3.5-turbo",
            "claude-3-opus",
            "claude-3-sonnet",
        ]

        self._supported_commands = {
            "cursor.rules.get",
            "cursor.rules.update",
            "cursor.model.get",
            "cursor.model.set",
            "cursor.file.open",
            "cursor.file.close",
            "cursor.file.list_open",
        }
        self._active_model = self._models[0]

    @staticmethod
    def _source_extensions() -> set[str]:
        """Return file extensions treated as source/config files."""
        return {
            ".py",
            ".js",
            ".ts",
            ".jsx",
            ".tsx",
            ".java",
            ".go",
            ".rs",
            ".c",
            ".cpp",
            ".h",
            ".hpp",
            ".md",
            ".json",
            ".yaml",
            ".yml",
            ".toml",
            ".cfg",
            ".ini",
            ".sh",
            ".bash",
            ".zsh",
            ".rb",
            ".swift",
            ".kt",
            ".scala",
            ".html",
            ".css",
            ".scss",
            ".vue",
            ".svelte",
            ".sql",
            ".graphql",
            ".proto",
            ".tf",
            ".dockerfile",
        }

    def _iter_workspace_source_files(self):
        """Yield source files under the workspace, skipping hidden folders."""
        if not self.workspace_path.exists():
            return

        for path in self.workspace_path.rglob("*"):
            if not path.is_file():
                continue
            if any(part.startswith(".") for part in path.parts if part != "."):
                continue
            if path.suffix.lower() in self._source_extensions():
                yield path

    def connect(self) -> bool:
        """Establish connection to Cursor workspace."""
        self._status = IDEStatus.CONNECTING
        cursor_dir = self.workspace_path / ".cursor"
        if cursor_dir.exists() or self._cursorrules_path.exists():
            self._connected = True
            self._status = IDEStatus.CONNECTED
            return True

        if self.workspace_path.exists():
            self._connected = True
            self._status = IDEStatus.CONNECTED
            return True

        self._connected = False
        self._status = IDEStatus.ERROR
        return False

    def disconnect(self) -> None:
        """Disconnect from Cursor."""
        self._connected = False
        self._status = IDEStatus.DISCONNECTED
        self._open_files.clear()

    def is_connected(self) -> bool:
        """Check if currently connected."""
        return self._connected

    def get_capabilities(self) -> dict[str, Any]:
        """Get Cursor capabilities."""
        return {
            "name": "Cursor",
            "version": "latest",
            "features": [
                "composer",
                "chat",
                "inline_edit",
                "code_generation",
                "code_explanation",
                "rules_management",
                "model_selection",
            ],
            "models": self._models,
            "active_model": self._active_model,
            "supported_commands": sorted(self._supported_commands),
            "status": self._status.value,
            "connected": self._connected,
            "workspace": str(self.workspace_path),
        }

    def execute_command(self, command: str, args: dict | None = None) -> Any:
        """Execute a Cursor command."""
        if not self._connected:
            raise CommandExecutionError("Not connected to Cursor")

        payload = args or {}
        if command not in self._supported_commands:
            raise CommandExecutionError(f"Unknown Cursor command: {command}")

        if command == "cursor.rules.get":
            return self.get_rules()
        if command == "cursor.rules.update":
            ok = self.update_rules({"content": payload.get("content", "")})
            return {"status": "success" if ok else "error", "updated": ok}
        if command == "cursor.model.get":
            return {"model": self._active_model}
        if command == "cursor.model.set":
            model = payload.get("model", "")
            ok = self.set_model(model)
            return {"status": "success" if ok else "error", "model": self._active_model}
        if command == "cursor.file.open":
            path = str(payload.get("path", ""))
            return {"opened": self.open_file(path), "path": path}
        if command == "cursor.file.close":
            path = str(payload.get("path", ""))
            return {"closed": self.close_file(path), "path": path}
        if command == "cursor.file.list_open":
            return {"files": self.get_open_files()}

        # Defensive fallback for future command additions.
        raise CommandExecutionError(f"Unhandled Cursor command: {command}")

    def get_active_file(self) -> str | None:
        """Get the currently active file in Cursor IDE.

        When connected, scans the workspace for the most recently modified
        source file and returns its absolute path. Returns None if not
        connected or if no files are found.

        Returns:
            Absolute path to the most recently modified file, or None.
        """
        if not self._connected:
            return None

        best_file: Path | None = None
        best_mtime: float = -1.0

        try:
            for entry in self._iter_workspace_source_files():
                mtime = entry.stat().st_mtime
                if mtime > best_mtime:
                    best_mtime = mtime
                    best_file = entry
        except OSError:
            return None

        if best_file is not None:
            return str(best_file.resolve())
        return None

    def open_file(self, path: str) -> bool:
        """Open a file in Cursor."""
        file_path = Path(path)
        if not file_path.exists() or not file_path.is_file():
            return False

        resolved = file_path.resolve()
        if resolved not in self._open_files:
            self._open_files.append(resolved)
        return True

    def close_file(self, path: str) -> bool:
        """Close a file in Cursor."""
        file_path = Path(path).resolve()
        self._open_files = [p for p in self._open_files if p != file_path]
        return True

    def get_open_files(self) -> list[str]:
        """Get list of open files."""
        if not self._connected:
            return []

        # If explicit open-file state exists, prefer it.
        if self._open_files:
            return [str(p) for p in self._open_files if p.exists()]

        files = []
        for p in self._iter_workspace_source_files():
            files.append(str(p.resolve()))
            if len(files) >= 5:
                break
        return files

    def save_file(self, path: str) -> bool:
        """Save a file in Cursor."""
        if not self._connected:
            return False
        return Path(path).exists()

    def save_all(self) -> bool:
        """Save all open files in Cursor."""
        return self._connected

    def get_rules(self) -> dict[str, Any]:
        """Get current .cursorrules configuration."""
        if self._cursorrules_path.exists():
            try:
                content = self._cursorrules_path.read_text(encoding="utf-8")
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
            self._cursorrules_path.write_text(content, encoding="utf-8")
            return True
        except Exception as e:
            logger.warning("Failed to update Cursor rules: %s", e)
            return False

    def get_models(self) -> list[str]:
        """Get available AI models."""
        return list(self._models)

    def set_model(self, model: str) -> bool:
        """Set the active AI model."""
        if model in self._models:
            self._active_model = model
            return True
        return False


__all__ = ["CursorClient"]
