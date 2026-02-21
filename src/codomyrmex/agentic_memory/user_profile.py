"""User profile with preferences, save/load, and context generation."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


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
        """Load a profile from disk.  Returns a default profile if the file
        does not exist."""
        path = Path(path)
        if not path.exists():
            return cls()
        with open(path) as fh:
            data = json.load(fh)
        return cls(
            preferences=data.get("preferences", {}),
            history_summary=data.get("history_summary", ""),
        )

    # ── helpers ──────────────────────────────────────────────────

    def set_preference(self, key: str, value: Any) -> None:
        self.preferences[key] = value

    def get_preference(self, key: str, default: Any = None) -> Any:
        return self.preferences.get(key, default)

    def to_context_string(self) -> str:
        """Render a compact context string for prompt injection."""
        parts = [f"{k}={v}" for k, v in self.preferences.items()]
        return "; ".join(parts) if parts else "(no preferences)"
