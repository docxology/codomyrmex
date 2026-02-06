"""Feature manager implementation."""

import logging
from typing import Any

logger = logging.getLogger(__name__)

class FeatureManager:
    """Manages feature flags and their evaluation."""

    def __init__(self, config: dict[str, Any] | None = None):
        self.flags = config or {}

    def is_enabled(self, key: str, default: bool = False, **context) -> bool:
        """Evaluate a boolean flag.

        Args:
            key: Flag key.
            default: Default value if flag is not found.
            context: Contextual data for evaluation (e.g. user_id).
        """
        flag_def = self.flags.get(key)
        if flag_def is None:
            return default

        if isinstance(flag_def, bool):
            return flag_def

        # Support percentage-based rollout in definition
        if isinstance(flag_def, dict) and "percentage" in flag_def:
            user_id = context.get("user_id", "")
            if not user_id:
                return False
            # Simple deterministic hash for percentage rollout
            score = hash(f"{key}:{user_id}") % 100
            return score < flag_def["percentage"]

        return default

    def get_value(self, key: str, default: Any = None, **context) -> Any:
        """Evaluate a multivariate flag."""
        return self.flags.get(key, default)

    def load_from_file(self, file_path: str):
        """Load flags from a JSON file."""
        import json
        with open(file_path) as f:
            self.flags.update(json.load(f))

    def save_to_file(self, file_path: str):
        """Save flags to a JSON file."""
        import json
        with open(file_path, "w") as f:
            json.dump(self.flags, f, indent=2)
