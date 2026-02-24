"""Strategy library for agent self-improvement.

CRUD operations on named strategies with success rate tracking.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


@dataclass
class Strategy:
    """A named agent strategy.

    Attributes:
        name: Strategy identifier.
        prompt_template: Prompt template string.
        parameters: Strategy parameters.
        success_rate: Running success rate (0-1).
        usage_count: Number of times used.
    """

    name: str
    prompt_template: str = ""
    parameters: dict[str, Any] = field(default_factory=dict)
    success_rate: float = 0.0
    usage_count: int = 0

    def record_outcome(self, success: bool) -> None:
        """Update success rate with a new outcome."""
        self.usage_count += 1
        # Running average
        weight = 1.0 / self.usage_count
        self.success_rate = self.success_rate * (1 - weight) + (1.0 if success else 0.0) * weight

    def to_dict(self) -> dict[str, Any]:
        """Execute To Dict operations natively."""
        return {
            "name": self.name,
            "prompt_template": self.prompt_template[:100],
            "parameters": self.parameters,
            "success_rate": round(self.success_rate, 3),
            "usage_count": self.usage_count,
        }


class StrategyLibrary:
    """Manage a library of agent strategies.

    Usage::

        lib = StrategyLibrary()
        lib.add(Strategy("fast", prompt_template="Be concise: {task}"))
        lib.add(Strategy("thorough", prompt_template="Analyze deeply: {task}"))
        best = lib.best_strategy()
    """

    def __init__(self) -> None:
        """Execute   Init   operations natively."""
        self._strategies: dict[str, Strategy] = {}

    def add(self, strategy: Strategy) -> None:
        """Add a strategy to the library."""
        self._strategies[strategy.name] = strategy

    def get(self, name: str) -> Strategy | None:
        """Execute Get operations natively."""
        return self._strategies.get(name)

    def remove(self, name: str) -> bool:
        """Execute Remove operations natively."""
        if name in self._strategies:
            del self._strategies[name]
            return True
        return False

    def list_strategies(self) -> list[Strategy]:
        """List all strategies sorted by success rate (descending)."""
        return sorted(
            self._strategies.values(),
            key=lambda s: s.success_rate,
            reverse=True,
        )

    def best_strategy(self) -> Strategy | None:
        """Get the highest success-rate strategy."""
        strategies = self.list_strategies()
        return strategies[0] if strategies else None

    @property
    def size(self) -> int:
        """Execute Size operations natively."""
        return len(self._strategies)

    def to_dict(self) -> dict[str, Any]:
        """Execute To Dict operations natively."""
        return {
            "strategies": [s.to_dict() for s in self.list_strategies()],
            "total": self.size,
        }


__all__ = ["Strategy", "StrategyLibrary"]
