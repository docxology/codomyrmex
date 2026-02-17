"""User profile management for agent personalization.

Reads and writes ``~/.codomyrmex/user_profile.json`` so agents can persist
user preferences, history summaries, and active context across sessions.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


_DEFAULT_DIR = Path.home() / ".codomyrmex"
_DEFAULT_PATH = _DEFAULT_DIR / "user_profile.json"


@dataclass
class UserProfile:
    """Persistent user profile for agent interactions.

    Attributes:
        preferences: Key-value map of user preferences (e.g. language, style).
        history_summary: A short summary of past interactions.
        active_context: Ephemeral context for the current session.
        metadata: Free-form metadata.
    """

    preferences: dict[str, Any] = field(default_factory=dict)
    history_summary: str = ""
    active_context: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save(self, path: Path | str | None = None) -> Path:
        """Write profile to disk as JSON.

        Args:
            path: Target file path.  Defaults to
                ``~/.codomyrmex/user_profile.json``.

        Returns:
            The resolved path that was written.
        """
        target = Path(path) if path else _DEFAULT_PATH
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(asdict(self), indent=2), encoding="utf-8")
        return target

    @classmethod
    def load(cls, path: Path | str | None = None) -> UserProfile:
        """Load profile from disk.

        If the file does not exist, returns a fresh empty profile.

        Args:
            path: Source file path.  Defaults to
                ``~/.codomyrmex/user_profile.json``.

        Returns:
            A ``UserProfile`` instance.
        """
        target = Path(path) if path else _DEFAULT_PATH
        if not target.exists():
            return cls()
        try:
            data = json.loads(target.read_text(encoding="utf-8"))
            return cls(
                preferences=data.get("preferences", {}),
                history_summary=data.get("history_summary", ""),
                active_context=data.get("active_context", {}),
                metadata=data.get("metadata", {}),
            )
        except (json.JSONDecodeError, KeyError):
            return cls()

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------

    def set_preference(self, key: str, value: Any) -> None:
        """Set a single preference key."""
        self.preferences[key] = value

    def get_preference(self, key: str, default: Any = None) -> Any:
        """Get a preference value with optional default."""
        return self.preferences.get(key, default)

    def to_context_string(self) -> str:
        """Format profile as a string suitable for LLM system prompts."""
        lines = []
        if self.preferences:
            prefs = ", ".join(f"{k}={v}" for k, v in self.preferences.items())
            lines.append(f"User preferences: {prefs}")
        if self.history_summary:
            lines.append(f"Session history: {self.history_summary}")
        return "\n".join(lines) if lines else "No user profile available."
