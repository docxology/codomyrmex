"""Cross-session user modeling."""

from __future__ import annotations

import json
import logging
import os
import shutil
import signal
import subprocess
from contextlib import suppress
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

logger = logging.getLogger(__name__)


class UserModel:
    """Cross-session user context persistence.

    Stores user preferences, coding style observations, and context that
    carries across multiple Hermes sessions.  Backed by a JSON file.

    Attributes:
        user_id: Identifier for the user profile.
        preferences: Accumulated user preferences.
        observations: Coding style and behavior observations.

    """

    def __init__(self, storage_dir: str | None = None) -> None:
        """Initialize user model storage.

        Args:
            storage_dir: Directory for user model files.

        """
        self._storage_dir = Path(
            storage_dir or os.path.expanduser("~/.codomyrmex/user_model")
        )
        self._storage_dir.mkdir(parents=True, exist_ok=True)
        self._profile_path = self._storage_dir / "profile.json"
        self._profile: dict[str, Any] = self._load_profile()

    def _load_profile(self) -> dict[str, Any]:
        """Load the user profile from disk."""
        if self._profile_path.exists():
            try:
                return json.loads(self._profile_path.read_text())
            except (json.JSONDecodeError, OSError):
                return self._default_profile()
        return self._default_profile()

    @staticmethod
    def _default_profile() -> dict[str, Any]:
        """Return a fresh default profile."""
        return {
            "preferences": {},
            "observations": [],
            "session_history": [],
            "context_summary": "",
        }

    def save(self) -> None:
        """Persist the current profile to disk."""
        self._profile_path.write_text(json.dumps(self._profile, indent=2))

    def record_session(self, session_id: str, summary: str) -> None:
        """Record a completed session summary for cross-session context.

        Args:
            session_id: Session identifier.
            summary: Brief summary of the session outcome.

        """
        history = self._profile.setdefault("session_history", [])
        history.append({"session_id": session_id, "summary": summary})
        # Keep only last 50 session summaries
        if len(history) > 50:
            self._profile["session_history"] = history[-50:]
        self.save()

    def add_observation(self, observation: str) -> None:
        """Add a coding style or preference observation.

        Args:
            observation: Text description of observed user behavior.

        """
        observations = self._profile.setdefault("observations", [])
        observations.append(observation)
        if len(observations) > 100:
            self._profile["observations"] = observations[-100:]
        self.save()

    def set_preference(self, key: str, value: Any) -> None:
        """set a user preference.

        Args:
            key: Preference key (e.g., ``"language"``, ``"style"``).
            value: Preference value.

        """
        self._profile.setdefault("preferences", {})[key] = value
        self.save()

    def get_context_prompt(self) -> str:
        """Generate a context prompt from accumulated user knowledge.

        Returns:
            A system-level context string summarizing user preferences.

        """
        prefs = self._profile.get("preferences", {})
        obs = self._profile.get("observations", [])
        history = self._profile.get("session_history", [])

        parts: list[str] = []
        if prefs:
            parts.append(
                "User preferences: " + "; ".join(f"{k}={v}" for k, v in prefs.items())
            )
        if obs:
            parts.append("Observations: " + "; ".join(obs[-10:]))
        if history:
            parts.append(
                "Recent sessions: " + "; ".join(h["summary"] for h in history[-5:])
            )
        return "\n".join(parts) if parts else ""

    @property
    def profile(self) -> dict[str, Any]:
        """Return the current profile data."""
        return dict(self._profile)
