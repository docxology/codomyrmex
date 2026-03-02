"""
Feature flag evaluation strategies.

Provides different strategies for evaluating feature flags.
"""

import hashlib
import random
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)

@dataclass
class EvaluationContext:
    """Context for feature flag evaluation."""
    user_id: str | None = None
    session_id: str | None = None
    environment: str = "production"
    attributes: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    def get_attribute(self, key: str, default: Any = None) -> Any:
        """Get an attribute value."""
        return self.attributes.get(key, default)

    def get_hash_key(self) -> str:
        """Get a consistent hash key for this context."""
        key = f"{self.user_id or ''}-{self.session_id or ''}"
        return hashlib.md5(key.encode()).hexdigest()

@dataclass
class EvaluationResult:
    """Result of a feature flag evaluation."""
    enabled: bool
    variant: str | None = None
    reason: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

class EvaluationStrategy(ABC):
    """Abstract base class for evaluation strategies."""

    @abstractmethod
    def evaluate(self, context: EvaluationContext) -> EvaluationResult:
        """Evaluate the feature flag."""
        pass

    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        """Serialize the strategy to a dictionary."""
        pass

    @classmethod
    @abstractmethod
    def from_dict(cls, data: dict[str, Any]) -> 'EvaluationStrategy':
        """Deserialize a strategy from a dictionary."""
        pass

class BooleanStrategy(EvaluationStrategy):
    """Simple on/off boolean strategy."""

    def __init__(self, enabled: bool = False):
        self.enabled = enabled

    def evaluate(self, context: EvaluationContext) -> EvaluationResult:
        """evaluate ."""
        return EvaluationResult(
            enabled=self.enabled,
            reason="boolean" if self.enabled else "disabled"
        )

    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary representation of this object."""
        return {"type": "boolean", "enabled": self.enabled}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'BooleanStrategy':
        return cls(enabled=data.get("enabled", False))

class PercentageStrategy(EvaluationStrategy):
    """Percentage-based rollout strategy."""

    def __init__(self, percentage: float = 0.0, sticky: bool = True):
        self.percentage = max(0.0, min(100.0, percentage))
        self.sticky = sticky

    def evaluate(self, context: EvaluationContext) -> EvaluationResult:
        """evaluate ."""
        if self.sticky and (context.user_id or context.session_id):
            # Use consistent hashing for sticky sessions
            hash_key = context.get_hash_key()
            hash_value = int(hash_key, 16) % 100
            enabled = hash_value < self.percentage
        else:
            enabled = random.random() * 100 < self.percentage

        return EvaluationResult(
            enabled=enabled,
            reason=f"percentage:{self.percentage}%",
            metadata={"percentage": self.percentage, "sticky": self.sticky}
        )

    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary representation of this object."""
        return {
            "type": "percentage",
            "percentage": self.percentage,
            "sticky": self.sticky
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'PercentageStrategy':
        return cls(
            percentage=data.get("percentage", 0.0),
            sticky=data.get("sticky", True)
        )

class UserListStrategy(EvaluationStrategy):
    """Strategy based on user allowlist/blocklist."""

    def __init__(
        self,
        allowed_users: list[str] | None = None,
        blocked_users: list[str] | None = None,
        default: bool = False
    ):
        self.allowed_users = set(allowed_users or [])
        self.blocked_users = set(blocked_users or [])
        self.default = default

    def evaluate(self, context: EvaluationContext) -> EvaluationResult:
        """evaluate ."""
        if not context.user_id:
            return EvaluationResult(
                enabled=self.default,
                reason="no_user_id"
            )

        if context.user_id in self.blocked_users:
            return EvaluationResult(
                enabled=False,
                reason="blocked_user"
            )

        if context.user_id in self.allowed_users:
            return EvaluationResult(
                enabled=True,
                reason="allowed_user"
            )

        return EvaluationResult(
            enabled=self.default,
            reason="default"
        )

    def add_user(self, user_id: str) -> None:
        """Add a user to the allowlist."""
        self.allowed_users.add(user_id)

    def remove_user(self, user_id: str) -> None:
        """Remove a user from the allowlist."""
        self.allowed_users.discard(user_id)

    def block_user(self, user_id: str) -> None:
        """Add a user to the blocklist."""
        self.blocked_users.add(user_id)

    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary representation of this object."""
        return {
            "type": "user_list",
            "allowed_users": list(self.allowed_users),
            "blocked_users": list(self.blocked_users),
            "default": self.default
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'UserListStrategy':
        return cls(
            allowed_users=data.get("allowed_users"),
            blocked_users=data.get("blocked_users"),
            default=data.get("default", False)
        )

class AttributeStrategy(EvaluationStrategy):
    """Strategy based on context attributes."""

    def __init__(
        self,
        attribute: str,
        operator: str,  # eq, neq, gt, lt, gte, lte, in, contains
        value: Any,
        enabled_value: bool = True
    ):
        self.attribute = attribute
        self.operator = operator
        self.value = value
        self.enabled_value = enabled_value

    def evaluate(self, context: EvaluationContext) -> EvaluationResult:
        """evaluate ."""
        attr_value = context.get_attribute(self.attribute)

        if attr_value is None:
            return EvaluationResult(
                enabled=not self.enabled_value,
                reason="attribute_missing"
            )

        match = self._check_condition(attr_value)
        enabled = match == self.enabled_value

        return EvaluationResult(
            enabled=enabled,
            reason=f"attribute:{self.attribute}:{self.operator}",
            metadata={
                "attribute": self.attribute,
                "operator": self.operator,
                "expected": self.value,
                "actual": attr_value
            }
        )

    def _check_condition(self, attr_value: Any) -> bool:
        """Check if the condition matches."""
        operators = {
            "eq": lambda a, b: a == b,
            "neq": lambda a, b: a != b,
            "gt": lambda a, b: a > b,
            "lt": lambda a, b: a < b,
            "gte": lambda a, b: a >= b,
            "lte": lambda a, b: a <= b,
            "in": lambda a, b: a in b,
            "contains": lambda a, b: b in a,
        }

        op_func = operators.get(self.operator)
        if not op_func:
            return False

        try:
            return op_func(attr_value, self.value)
        except (TypeError, ValueError) as e:
            logger.warning("Attribute condition check failed for %s: %s", self.attribute, e)
            return False

    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary representation of this object."""
        return {
            "type": "attribute",
            "attribute": self.attribute,
            "operator": self.operator,
            "value": self.value,
            "enabled_value": self.enabled_value
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'AttributeStrategy':
        return cls(
            attribute=data["attribute"],
            operator=data["operator"],
            value=data["value"],
            enabled_value=data.get("enabled_value", True)
        )

class EnvironmentStrategy(EvaluationStrategy):
    """Strategy based on environment."""

    def __init__(self, enabled_environments: list[str] | None = None):
        self.enabled_environments = set(enabled_environments or ["development"])

    def evaluate(self, context: EvaluationContext) -> EvaluationResult:
        """evaluate ."""
        enabled = context.environment in self.enabled_environments
        return EvaluationResult(
            enabled=enabled,
            reason=f"environment:{context.environment}",
            metadata={"environments": list(self.enabled_environments)}
        )

    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary representation of this object."""
        return {
            "type": "environment",
            "enabled_environments": list(self.enabled_environments)
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'EnvironmentStrategy':
        return cls(enabled_environments=data.get("enabled_environments"))

class TimeWindowStrategy(EvaluationStrategy):
    """Strategy that enables a flag only within a time window.

    Evaluates to True when the current time falls between
    ``start_time`` and ``end_time`` (inclusive).  This allows
    scheduling feature rollouts for a specific date/time range without
    manual intervention.

    Attributes:
        start_time: The earliest datetime the flag should be enabled.
        end_time: The latest datetime the flag should be enabled.
    """

    def __init__(
        self,
        start_time: datetime,
        end_time: datetime,
    ):
        if end_time <= start_time:
            raise ValueError(
                f"end_time ({end_time.isoformat()}) must be after "
                f"start_time ({start_time.isoformat()})"
            )
        self.start_time = start_time
        self.end_time = end_time

    def evaluate(self, context: EvaluationContext) -> EvaluationResult:
        """Return enabled=True when now is within [start_time, end_time].

        Uses ``context.timestamp`` when available so callers can override
        the evaluation moment for testing or replay scenarios.  Falls back
        to ``datetime.now()`` only when the context has no timestamp.
        """
        now = context.timestamp if context.timestamp else datetime.now()
        enabled = self.start_time <= now <= self.end_time

        reason = "time_window_active" if enabled else "time_window_inactive"
        return EvaluationResult(
            enabled=enabled,
            reason=reason,
            metadata={
                "start_time": self.start_time.isoformat(),
                "end_time": self.end_time.isoformat(),
                "evaluated_at": now.isoformat(),
            },
        )

    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary representation of this strategy."""
        return {
            "type": "time_window",
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'TimeWindowStrategy':
        return cls(
            start_time=datetime.fromisoformat(data["start_time"]),
            end_time=datetime.fromisoformat(data["end_time"]),
        )


class CompositeStrategy(EvaluationStrategy):
    """Strategy that combines multiple strategies with AND/OR logic."""

    def __init__(
        self,
        strategies: list[EvaluationStrategy],
        operator: str = "and"  # "and" or "or"
    ):
        self.strategies = strategies
        self.operator = operator

    def evaluate(self, context: EvaluationContext) -> EvaluationResult:
        """evaluate ."""
        if not self.strategies:
            return EvaluationResult(enabled=False, reason="no_strategies")

        results = [s.evaluate(context) for s in self.strategies]

        if self.operator == "and":
            enabled = all(r.enabled for r in results)
        else:  # or
            enabled = any(r.enabled for r in results)

        return EvaluationResult(
            enabled=enabled,
            reason=f"composite:{self.operator}",
            metadata={
                "results": [{"enabled": r.enabled, "reason": r.reason} for r in results]
            }
        )

    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary representation of this object."""
        return {
            "type": "composite",
            "operator": self.operator,
            "strategies": [s.to_dict() for s in self.strategies]
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'CompositeStrategy':
        strategies = [create_strategy(s) for s in data.get("strategies", [])]
        return cls(strategies=strategies, operator=data.get("operator", "and"))

def create_strategy(data: dict[str, Any]) -> EvaluationStrategy:
    """Factory function to create strategies from config."""
    strategy_types = {
        "boolean": BooleanStrategy,
        "percentage": PercentageStrategy,
        "user_list": UserListStrategy,
        "attribute": AttributeStrategy,
        "environment": EnvironmentStrategy,
        "time_window": TimeWindowStrategy,
        "composite": CompositeStrategy,
    }

    strategy_type = data.get("type", "boolean")
    strategy_class = strategy_types.get(strategy_type)

    if not strategy_class:
        raise ValueError(f"Unknown strategy type: {strategy_type}")

    return strategy_class.from_dict(data)

__all__ = [
    "EvaluationContext",
    "EvaluationResult",
    "EvaluationStrategy",
    "BooleanStrategy",
    "PercentageStrategy",
    "UserListStrategy",
    "AttributeStrategy",
    "EnvironmentStrategy",
    "TimeWindowStrategy",
    "CompositeStrategy",
    "create_strategy",
]
