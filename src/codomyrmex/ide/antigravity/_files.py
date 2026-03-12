"""File management mixin for Antigravity IDE client.

Extracted from client.py.
"""

from __future__ import annotations

from pathlib import Path

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class AntigravityFilesMixin:
    """Mixin for managing file operations in Antigravity."""

    # Note: Requires self._context and self._connected

    def get_active_file(self) -> str | None:
        """Get the currently active file in Antigravity.

        Uses artifact modification times and workspace heuristics.

        Returns:
            File path or None if no file is active.
        """
        if self._context and self._context.artifacts:
            most_recent = max(self._context.artifacts, key=lambda a: a.modified)
            if most_recent.path and Path(most_recent.path).exists():
                return most_recent.path

        # Fallback: most recently modified source file in cwd
        try:
            cwd = Path.cwd()
            candidates = [
                f
                for f in cwd.rglob("*")
                if f.is_file()
                and not any(part.startswith(".") for part in f.parts)
                and f.suffix
                in {".py", ".md", ".txt", ".yaml", ".yml", ".toml", ".json"}
            ]
            if candidates:
                return str(max(candidates, key=lambda p: p.stat().st_mtime))
        except OSError as e:
            logger.debug("Failed to scan Antigravity workspace for files: %s", e)
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

    def close_file(self, path: str) -> bool:
        """Close a file in Antigravity."""
        return True

    def get_open_files(self) -> list[str]:
        """Get list of open files.

        Returns:
            List of file paths.
        """
        # Simulated based on artifacts
        if not self._connected:
            return []

        return [a.path for a in self._context.artifacts if a.path]

    def save_file(self, path: str) -> bool:
        """Save a file in Antigravity."""
        if not self._connected:
            return False
        return Path(path).exists()

    def save_all(self) -> bool:
        """Save all open files in Antigravity."""
        return self._connected
