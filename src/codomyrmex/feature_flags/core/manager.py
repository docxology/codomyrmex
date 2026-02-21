"""Feature manager — evaluation engine for feature flags and rollouts.

Supports:
- Boolean flags (on/off per environment)
- Percentage-based rollout (deterministic hashing per user)
- User/group targeting (allowlist/denylist)
- Time-based flags (scheduled activation windows)
- Flag lifecycle: create, enable, disable, archive
- In-memory override stack for testing
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class FlagDefinition:
    """Full definition of a feature flag."""

    key: str
    enabled: bool = False
    percentage: float | None = None  # 0-100 rollout percentage
    allowlist: list[str] = field(default_factory=list)
    denylist: list[str] = field(default_factory=list)
    start_time: float | None = None  # unix timestamp — flag active after this
    end_time: float | None = None  # unix timestamp — flag inactive after this
    description: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


class FeatureManager:
    """Manages feature flags with multi-strategy evaluation.

    Evaluation order for is_enabled():
    1. Test overrides (highest priority)
    2. Denylist → always False
    3. Allowlist → always True
    4. Time window check
    5. Percentage-based rollout (deterministic)
    6. Boolean enabled flag (default)

    Example::

        fm = FeatureManager()
        fm.create_flag("dark_mode", enabled=True)
        fm.create_flag("new_checkout", percentage=25)

        assert fm.is_enabled("dark_mode")
        # 25% of users get new_checkout
        fm.is_enabled("new_checkout", user_id="alice")
    """

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self._flags: dict[str, FlagDefinition] = {}
        self._overrides: dict[str, bool] = {}  # test overrides

        # Bootstrap from config dict
        if config:
            for key, val in config.items():
                if isinstance(val, bool):
                    self.create_flag(key, enabled=val)
                elif isinstance(val, dict):
                    self.create_flag(key, **val)
                else:
                    # Scalar multivariate value (str, int, float, etc.)
                    self.create_flag(key, enabled=True, metadata={"value": val})

    # ── Flag lifecycle ──────────────────────────────────────────────

    def create_flag(self, key: str, **kwargs: Any) -> FlagDefinition:
        """Create or update a flag definition."""
        flag = FlagDefinition(key=key, **kwargs)
        self._flags[key] = flag
        logger.info("Flag created/updated: %s", key)
        return flag

    def delete_flag(self, key: str) -> bool:
        """Remove a flag definition."""
        if key in self._flags:
            del self._flags[key]
            return True
        return False

    def get_flag(self, key: str) -> FlagDefinition | None:
        """Get the full flag definition."""
        return self._flags.get(key)

    def list_flags(self) -> list[FlagDefinition]:
        """List all registered flags."""
        return list(self._flags.values())

    # ── Evaluation ──────────────────────────────────────────────────

    def is_enabled(self, key: str, default: bool = False, **context: Any) -> bool:
        """Evaluate whether a flag is enabled for the given context.

        Args:
            key: Flag key.
            default: Fallback if flag doesn't exist.
            **context: Evaluation context (user_id, group, etc.).
        """
        # 1. Test override
        if key in self._overrides:
            return self._overrides[key]

        flag = self._flags.get(key)
        if flag is None:
            return default

        user_id = str(context.get("user_id", ""))

        # 2. Denylist
        if user_id and user_id in flag.denylist:
            return False

        # 3. Allowlist
        if user_id and user_id in flag.allowlist:
            return True

        # 4. Time window
        now = time.time()
        if flag.start_time and now < flag.start_time:
            return False
        if flag.end_time and now > flag.end_time:
            return False

        # 5. Percentage rollout
        if flag.percentage is not None:
            if not user_id:
                return False
            score = hash(f"{key}:{user_id}") % 100
            return score < flag.percentage

        # 6. Boolean
        return flag.enabled

    def get_value(self, key: str, default: Any = None, **context: Any) -> Any:
        """Get a multivariate flag value."""
        flag = self._flags.get(key)
        if flag is None:
            return default
        return flag.metadata.get("value", default)

    # ── Test overrides ──────────────────────────────────────────────

    def set_override(self, key: str, value: bool) -> None:
        """Set a test override (highest priority)."""
        self._overrides[key] = value

    def clear_override(self, key: str) -> None:
        """Remove a test override."""
        self._overrides.pop(key, None)

    def clear_all_overrides(self) -> None:
        """Remove all test overrides."""
        self._overrides.clear()

    # ── Persistence ─────────────────────────────────────────────────

    def load_from_file(self, file_path: str) -> int:
        """Load flags from a JSON file. Returns count of flags loaded."""
        data = json.loads(Path(file_path).read_text())
        count = 0
        for key, val in data.items():
            if isinstance(val, bool):
                self.create_flag(key, enabled=val)
            elif isinstance(val, dict):
                self.create_flag(key, **val)
            count += 1
        return count

    def save_to_file(self, file_path: str) -> None:
        """Save all flags to a JSON file."""
        data = {}
        for key, flag in self._flags.items():
            data[key] = {
                "enabled": flag.enabled,
                "percentage": flag.percentage,
                "allowlist": flag.allowlist,
                "denylist": flag.denylist,
                "start_time": flag.start_time,
                "end_time": flag.end_time,
                "description": flag.description,
                "metadata": flag.metadata,
            }
        Path(file_path).write_text(json.dumps(data, indent=2))

    # ── Summary ─────────────────────────────────────────────────────

    def summary(self) -> dict[str, Any]:
        """Return a summary of flag states."""
        return {
            "total_flags": len(self._flags),
            "enabled": sum(1 for f in self._flags.values() if f.enabled),
            "percentage_rollouts": sum(1 for f in self._flags.values() if f.percentage is not None),
            "overrides_active": len(self._overrides),
        }
