"""RetryPolicy: configurable exponential backoff with jitter."""

import random
import time


class RetryPolicy:
    """
    Configurable retry policy with exponential backoff.

    Usage:
        policy = RetryPolicy(max_retries=3, backoff_base=0.1)

        for attempt in policy.attempts():
            try:
                result = make_api_call()
                break
            except Exception as e:
                if not policy.should_retry(e):
                    raise
    """

    def __init__(
        self,
        max_retries: int = 3,
        backoff_base: float = 0.1,
        backoff_multiplier: float = 2.0,
        backoff_max: float = 30.0,
        jitter: bool = True,
        retryable_exceptions: tuple | None = None,
    ):
        self.max_retries = max_retries
        self.backoff_base = backoff_base
        self.backoff_multiplier = backoff_multiplier
        self.backoff_max = backoff_max
        self.jitter = jitter
        self.retryable_exceptions = retryable_exceptions or (Exception,)

    def get_delay(self, attempt: int) -> float:
        """Calculate delay for an attempt using exponential backoff."""
        delay = self.backoff_base * (self.backoff_multiplier**attempt)
        delay = min(delay, self.backoff_max)

        if self.jitter:
            delay *= 0.5 + random.random()

        return delay

    def should_retry(self, exception: Exception) -> bool:
        """Return True if the exception type is retryable."""
        return isinstance(exception, self.retryable_exceptions)

    def attempts(self):
        """Generator yielding attempt indices, sleeping between attempts."""
        for attempt in range(self.max_retries + 1):
            if attempt > 0:
                time.sleep(self.get_delay(attempt - 1))
            yield attempt
