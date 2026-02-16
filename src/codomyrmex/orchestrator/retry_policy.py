"""Configurable retry policies for pipeline steps.

Provides retry policy definitions for orchestrator pipeline steps
with exponential backoff, circuit breaker integration, and dead letter routing.
"""

from __future__ import annotations

import asyncio
import logging
import random
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, TypeVar

logger = logging.getLogger(__name__)
T = TypeVar("T")


class RetryOutcome(Enum):
    """Outcome of a retry attempt."""
    SUCCESS = "success"
    RETRY = "retry"
    ABORT = "abort"
    DEAD_LETTER = "dead_letter"


@dataclass
class RetryPolicy:
    """Policy for retrying failed pipeline steps."""
    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 300.0
    exponential_base: float = 2.0
    jitter: bool = True
    retryable_errors: tuple[type[Exception], ...] = (Exception,)
    non_retryable_errors: tuple[type[Exception], ...] = ()
    on_retry: Callable[[int, Exception], None] | None = None
    on_exhausted: Callable[[Exception], None] | None = None

    def compute_delay(self, attempt: int) -> float:
        """Compute delay for a given attempt number."""
        delay = self.base_delay * (self.exponential_base ** attempt)
        delay = min(delay, self.max_delay)
        if self.jitter:
            delay *= random.uniform(0.5, 1.5)
        return delay

    def should_retry(self, error: Exception, attempt: int) -> RetryOutcome:
        """Determine whether to retry based on error type and attempt."""
        if isinstance(error, self.non_retryable_errors):
            return RetryOutcome.ABORT
        if attempt >= self.max_attempts:
            return RetryOutcome.DEAD_LETTER
        if isinstance(error, self.retryable_errors):
            return RetryOutcome.RETRY
        return RetryOutcome.ABORT


@dataclass
class RetryResult:
    """Result of executing with retry policy."""
    outcome: RetryOutcome
    result: Any = None
    error: Exception | None = None
    attempts: int = 0
    total_delay: float = 0.0


class PipelineRetryExecutor:
    """Execute pipeline steps with configurable retry policies."""

    def __init__(self, default_policy: RetryPolicy | None = None) -> None:
        self._default_policy = default_policy or RetryPolicy()
        self._step_policies: dict[str, RetryPolicy] = {}

    def set_policy(self, step_name: str, policy: RetryPolicy) -> None:
        """Set a custom retry policy for a specific pipeline step."""
        self._step_policies[step_name] = policy

    def get_policy(self, step_name: str) -> RetryPolicy:
        """Get the retry policy for a step (custom or default)."""
        return self._step_policies.get(step_name, self._default_policy)

    def execute(self, step_name: str, func: Callable[..., T],
                *args: Any, **kwargs: Any) -> RetryResult:
        """Execute a function with retry policy."""
        policy = self.get_policy(step_name)
        total_delay = 0.0

        for attempt in range(policy.max_attempts + 1):
            try:
                result = func(*args, **kwargs)
                return RetryResult(
                    outcome=RetryOutcome.SUCCESS,
                    result=result,
                    attempts=attempt + 1,
                    total_delay=total_delay,
                )
            except Exception as e:
                outcome = policy.should_retry(e, attempt + 1)
                if outcome == RetryOutcome.RETRY:
                    delay = policy.compute_delay(attempt)
                    total_delay += delay
                    logger.warning(
                        "Step '%s' attempt %d failed, retrying in %.1fs: %s",
                        step_name, attempt + 1, delay, e,
                    )
                    if policy.on_retry:
                        policy.on_retry(attempt + 1, e)
                    time.sleep(delay)
                else:
                    if policy.on_exhausted:
                        policy.on_exhausted(e)
                    return RetryResult(
                        outcome=outcome, error=e,
                        attempts=attempt + 1, total_delay=total_delay,
                    )

        return RetryResult(
            outcome=RetryOutcome.DEAD_LETTER,
            attempts=policy.max_attempts,
            total_delay=total_delay,
        )

    async def execute_async(self, step_name: str, func: Callable[..., Any],
                            *args: Any, **kwargs: Any) -> RetryResult:
        """Execute an async function with retry policy."""
        policy = self.get_policy(step_name)
        total_delay = 0.0

        for attempt in range(policy.max_attempts + 1):
            try:
                result = await func(*args, **kwargs)
                return RetryResult(
                    outcome=RetryOutcome.SUCCESS,
                    result=result,
                    attempts=attempt + 1,
                    total_delay=total_delay,
                )
            except Exception as e:
                outcome = policy.should_retry(e, attempt + 1)
                if outcome == RetryOutcome.RETRY:
                    delay = policy.compute_delay(attempt)
                    total_delay += delay
                    if policy.on_retry:
                        policy.on_retry(attempt + 1, e)
                    await asyncio.sleep(delay)
                else:
                    if policy.on_exhausted:
                        policy.on_exhausted(e)
                    return RetryResult(
                        outcome=outcome, error=e,
                        attempts=attempt + 1, total_delay=total_delay,
                    )

        return RetryResult(
            outcome=RetryOutcome.DEAD_LETTER,
            attempts=policy.max_attempts,
            total_delay=total_delay,
        )
