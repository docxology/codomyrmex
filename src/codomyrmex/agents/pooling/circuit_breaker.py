"""CircuitBreaker (pooling-internal): lightweight CLOSED/OPEN/HALF_OPEN gate."""

import threading
import time


class CircuitBreaker:
    """
    Lightweight circuit breaker for agent pool fault tolerance.

    States: closed (normal) → open (failing fast) → half_open (testing).
    """

    def __init__(self, failure_threshold: int = 5, reset_timeout_s: float = 30.0):
        self.failure_threshold = failure_threshold
        self.reset_timeout_s = reset_timeout_s
        self._failures = 0
        self._last_failure_time: float | None = None
        self._state = "closed"
        self._lock = threading.Lock()

    @property
    def is_open(self) -> bool:
        with self._lock:
            if self._state == "open":
                if (
                    self._last_failure_time
                    and time.time() - self._last_failure_time > self.reset_timeout_s
                ):
                    self._state = "half_open"
                    return False
                return True
            return False

    def record_success(self) -> None:
        with self._lock:
            self._failures = 0
            self._state = "closed"

    def record_failure(self) -> None:
        with self._lock:
            self._failures += 1
            self._last_failure_time = time.time()
            if self._failures >= self.failure_threshold:
                self._state = "open"

    def reset(self) -> None:
        with self._lock:
            self._failures = 0
            self._state = "closed"
            self._last_failure_time = None
