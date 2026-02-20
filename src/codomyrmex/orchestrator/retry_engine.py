"""Config-aware retry engine with exponential backoff.

Retries operations with configurable backoff, detecting config
errors and adjusting parameters between attempts.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, TypeVar

from codomyrmex.orchestrator.failure_taxonomy import classify_error, FailureCategory
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


@dataclass
class RetryResult:
    """Result of a retry operation.

    Attributes:
        success: Whether the operation succeeded.
        result: The return value (if successful).
        attempts: Number of attempts made.
        errors: Errors from failed attempts.
        adjustments: Config adjustments made.
    """

    success: bool = False
    result: Any = None
    attempts: int = 0
    errors: list[str] = field(default_factory=list)
    adjustments: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "attempts": self.attempts,
            "errors": self.errors,
            "adjustments": self.adjustments,
        }


class RetryEngine:
    """Execute operations with config-aware retry.

    Detects config errors and can adjust parameters between retries.

    Usage::

        engine = RetryEngine(max_retries=3)
        result = engine.execute(my_function)
        if result.success:
            print(f"Done in {result.attempts} attempts")
    """

    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 0.01,
        max_delay: float = 1.0,
        backoff_factor: float = 2.0,
    ) -> None:
        self._max_retries = max_retries
        self._base_delay = base_delay
        self._max_delay = max_delay
        self._backoff_factor = backoff_factor

    def execute(
        self,
        operation: Callable[..., T],
        *args: Any,
        adjusters: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] | None = None,
        config: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> RetryResult:
        """Execute an operation with retry.

        Args:
            operation: The callable to execute.
            *args: Positional arguments.
            adjusters: Mapping of FailureCategory.value → config adjuster.
            config: Mutable config dict passed to adjusters.
            **kwargs: Keyword arguments.

        Returns:
            ``RetryResult`` with outcome.
        """
        result = RetryResult()
        current_config = dict(config) if config else {}
        adjusters = adjusters or {}

        for attempt in range(self._max_retries + 1):
            result.attempts = attempt + 1
            try:
                ret = operation(*args, **kwargs)
                result.success = True
                result.result = ret
                logger.info("Operation succeeded", extra={"attempt": attempt + 1})
                return result
            except Exception as exc:
                result.errors.append(str(exc))
                classified = classify_error(exc)

                logger.warning(
                    "Retry attempt failed",
                    extra={
                        "attempt": attempt + 1,
                        "category": classified.category.value,
                        "error": str(exc)[:100],
                    },
                )

                # Try config adjustment
                cat_key = classified.category.value
                if cat_key in adjusters and current_config:
                    try:
                        current_config = adjusters[cat_key](current_config)
                        result.adjustments.append(
                            f"Adjusted config for {cat_key}"
                        )
                    except Exception:
                        pass

                if attempt < self._max_retries:
                    delay = min(
                        self._base_delay * (self._backoff_factor ** attempt),
                        self._max_delay,
                    )
                    time.sleep(delay)

        return result


__all__ = [
    "RetryEngine",
    "RetryResult",
]
