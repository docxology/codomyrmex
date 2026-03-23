"""User profile with preferences, save/load, and context generation.

Provides a persistent UserProfile dataclass for storing user preferences
and session history. Profiles are serialized as JSON files.

Example:
    >>> from codomyrmex.agentic_memory.user_profile import UserProfile
    >>> profile = UserProfile()
    >>> profile.set_preference("theme", "dark")
    >>> profile.save("/tmp/profile.json")
    >>> loaded = UserProfile.load("/tmp/profile.json")
    >>> loaded.get_preference("theme")
    'dark'
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class UserProfile:
    """Persistent user profile for preferences and session history."""

    preferences: dict[str, Any] = field(default_factory=dict)
    history_summary: str = ""

    # ── persistence ──────────────────────────────────────────────

    def save(self, path: str | Path) -> None:
        """Write profile to a JSON file."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as fh:
            json.dump(
                {
                    "preferences": self.preferences,
                    "history_summary": self.history_summary,
                },
                fh,
                indent=2,
            )

    @classmethod
    def load(cls, path: str | Path) -> UserProfile:
        """Load a profile from disk.

        Returns a default profile if the file does not exist or is corrupt.

        Args:
            path: File path to the JSON profile file.

        Returns:
            A UserProfile instance, either loaded from disk or default.

        Example:
            >>> profile = UserProfile.load("/nonexistent.json")
            >>> profile.preferences
            {}
        """
        path = Path(path)
        if not path.exists():
            logger.debug("Profile file not found: %s — using defaults", path)
            return cls()
        try:
            with open(path) as fh:
                data = json.load(fh)
            return cls(
                preferences=data.get("preferences", {}),
                history_summary=data.get("history_summary", ""),
            )
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning(
                "Failed to load profile from %s: %s — using defaults", path, exc
            )
            return cls()

    # ── helpers ──────────────────────────────────────────────────

    def set_preference(self, key: str, value: Any) -> None:
        """Set a user preference.

        Args:
            key: Preference identifier (e.g., "theme", "language").
            value: The preference value.
        """
        self.preferences[key] = value

    def get_preference(self, key: str, default: Any = None) -> Any:
        """Get a user preference by key.

        Args:
            key: Preference identifier to look up.
            default: Value to return if key is not set.

        Returns:
            The preference value, or *default* if not found.
        """
        return self.preferences.get(key, default)

    def to_context_string(self) -> str:
        """Render a compact context string for prompt injection.

        Returns:
            Semicolon-separated key=value pairs, or "(no preferences)" if empty.

        Example:
            >>> p = UserProfile(preferences={"theme": "dark", "lang": "en"})
            >>> p.to_context_string()
            'theme=dark; lang=en'
        """
        parts = [f"{k}={v}" for k, v in self.preferences.items()]
        return "; ".join(parts) if parts else "(no preferences)"
