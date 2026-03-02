"""Feature manager — thin orchestrator for feature flags and rollouts.

This module integrates evaluation logic, storage backends, and rollout management.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from codomyrmex.feature_flags.evaluation import FlagDefinition, FlagEvaluator, TargetingRule
from codomyrmex.feature_flags.rollout import RolloutManager, RolloutConfig
from codomyrmex.feature_flags.storage import FlagStore, InMemoryFlagStore
from codomyrmex.feature_flags.strategies import EvaluationContext
from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)


class FeatureManager:
    """Manages feature flags by orchestrating evaluation, storage, and rollouts.

    Example::

        fm = FeatureManager()
        fm.create_flag("dark_mode", enabled=True)
        fm.create_flag("new_checkout", percentage=25.0)

        if fm.is_enabled("dark_mode"):
            # ...
    """

    def __init__(
        self,
        storage: Optional[FlagStore] = None,
        evaluator: Optional[FlagEvaluator] = None,
        rollout_manager: Optional[RolloutManager] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        self._storage = storage or InMemoryFlagStore()
        self._evaluator = evaluator or FlagEvaluator()
        self._rollout_manager = rollout_manager or RolloutManager()
        self._overrides: Dict[str, bool] = {}

        if config:
            self._bootstrap_config(config)

    def _bootstrap_config(self, config: Dict[str, Any]) -> None:
        """Bootstrap flags from a configuration dictionary."""
        for key, val in config.items():
            if isinstance(val, bool):
                self.create_flag(key, enabled=val)
            elif isinstance(val, dict):
                self.create_flag(key, **val)
            else:
                # Multivariate value
                self.create_flag(key, enabled=True, metadata={"value": val})

    # ── Flag Lifecycle ──────────────────────────────────────────────

    def create_flag(
        self,
        name: str,
        enabled: bool = True,
        percentage: float = 100.0,
        targeting_rules: Optional[List[TargetingRule]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        description: str = "",
        **kwargs: Any,
    ) -> FlagDefinition:
        """Create or update a flag definition."""
        # Handle legacy kwargs mapping
        if "allowlist" in kwargs:
            targeting_rules = targeting_rules or []
            targeting_rules.append(TargetingRule("user_id", "in", kwargs["allowlist"]))
        if "denylist" in kwargs:
            targeting_rules = targeting_rules or []
            targeting_rules.append(TargetingRule("user_id", "not_in", kwargs["denylist"]))
        
        flag = FlagDefinition(
            name=name,
            enabled=enabled,
            percentage=percentage,
            targeting_rules=targeting_rules or [],
            description=description,
            metadata=metadata or {},
        )
        self._storage.set(name, flag.__dict__) # Simple serialization for now
        logger.info("Flag created/updated: %s", name)
        return flag

    def delete_flag(self, name: str) -> bool:
        """Remove a flag definition."""
        return self._storage.delete(name)

    def get_flag(self, name: str) -> Optional[FlagDefinition]:
        """Get the full flag definition."""
        data = self._storage.get(name)
        if data:
            # Reconstruct FlagDefinition
            # Note: targeting_rules need special handling if they are dicts
            rules_data = data.get("targeting_rules", [])
            rules = [TargetingRule(**r) if isinstance(r, dict) else r for r in rules_data]
            return FlagDefinition(
                name=data["name"],
                enabled=data["enabled"],
                percentage=data["percentage"],
                targeting_rules=rules,
                description=data.get("description", ""),
                metadata=data.get("metadata", {}),
            )
        return None

    def list_flags(self) -> List[FlagDefinition]:
        """List all registered flags."""
        return [self.get_flag(name) for name in self._storage.list_all().keys()] # type: ignore

    # ── Evaluation ──────────────────────────────────────────────────

    def is_enabled(self, name: str, default: bool = False, **context_attrs: Any) -> bool:
        """Evaluate whether a flag is enabled for the given context."""
        if name in self._overrides:
            return self._overrides[name]

        flag = self.get_flag(name)
        if flag is None:
            return default

        # Create EvaluationContext
        user_id = context_attrs.pop("user_id", None)
        session_id = context_attrs.pop("session_id", None)
        environment = context_attrs.pop("environment", "production")
        
        context = EvaluationContext(
            user_id=user_id,
            session_id=session_id,
            environment=environment,
            attributes=context_attrs,
        )

        result = self._evaluator.evaluate(flag, context)
        return result.enabled

    def get_value(self, name: str, default: Any = None, **context_attrs: Any) -> Any:
        """Get a multivariate flag value."""
        flag = self.get_flag(name)
        if flag is None:
            return default
        
        # If enabled, return the value from metadata
        if self.is_enabled(name, **context_attrs):
            return flag.metadata.get("value", default)
        return default

    # ── Overrides ───────────────────────────────────────────────────

    def set_override(self, name: str, enabled: bool) -> None:
        """Set a runtime override for a flag."""
        self._overrides[name] = enabled

    def clear_override(self, name: str) -> None:
        """Clear a runtime override."""
        self._overrides.pop(name, None)

    # ── Persistence ─────────────────────────────────────────────────

    def load_from_file(self, file_path: str) -> int:
        """Load flags from a JSON file."""
        path = Path(file_path)
        if not path.exists():
            return 0
        
        with open(path, "r") as f:
            data = json.load(f)
            self._bootstrap_config(data)
            return len(data)

    def save_to_file(self, file_path: str) -> None:
        """Save all flags to a JSON file."""
        flags_data = {}
        for flag in self.list_flags():
            flags_data[flag.name] = {
                "enabled": flag.enabled,
                "percentage": flag.percentage,
                "description": flag.description,
                "metadata": flag.metadata,
                "targeting_rules": [r.__dict__ for r in flag.targeting_rules],
            }
        
        with open(file_path, "w") as f:
            json.dump(flags_data, f, indent=2)

    # ── Summary ─────────────────────────────────────────────────────

    def summary(self) -> Dict[str, Any]:
        """Return a summary of the managed flags."""
        all_flags = self.list_flags()
        return {
            "total_flags": len(all_flags),
            "enabled_globally": sum(1 for f in all_flags if f.enabled),
            "with_rollout": sum(1 for f in all_flags if f.percentage < 100.0),
            "with_rules": sum(1 for f in all_flags if f.targeting_rules),
            "overrides": len(self._overrides),
        }
