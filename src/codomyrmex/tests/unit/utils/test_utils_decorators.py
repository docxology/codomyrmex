"""Unit tests for timing and retry decorator utilities."""

import asyncio
import time

import pytest


@pytest.mark.unit
class TestTimingDecorator:
    """Tests for timing_decorator."""

    def test_timing_with_dict_result(self):
        """Test timing decorator adds execution_time_ms to dict result."""
        from codomyrmex.utils import timing_decorator

        @timing_decorator
        def func_returning_dict():
            return {"status": "ok"}

        result = func_returning_dict()

        assert "execution_time_ms" in result
        assert result["status"] == "ok"

    def test_timing_with_non_dict_result(self):
        """Test timing decorator with non-dict result."""
        from codomyrmex.utils import timing_decorator

        @timing_decorator
        def func_returning_string():
            return "result"

        result = func_returning_string()

        assert result == "result"

    def test_timing_preserves_function_name(self):
        """Test timing decorator preserves function name."""
        from codomyrmex.utils import timing_decorator

        @timing_decorator
        def my_function():
            return {}

        assert my_function.__name__ == "my_function"

    def test_timing_measures_actual_time(self):
        """Test timing decorator measures actual execution time."""
        from codomyrmex.utils import timing_decorator

        @timing_decorator
        def slow_function():
            time.sleep(0.1)
            return {}

        result = slow_function()

        assert result["execution_time_ms"] >= 100


@pytest.mark.unit
class TestRetryDecorator:
    """Tests for retry decorator."""

    def test_retry_success_first_try(self):
        """Test function succeeding on first try."""
        from codomyrmex.utils import retry

        call_count = 0

        @retry(max_attempts=3, delay=0.01)
        def always_succeeds():
            nonlocal call_count
            call_count += 1
            return "success"

        result = always_succeeds()

        assert result == "success"
        assert call_count == 1

    def test_retry_success_after_failures(self):
        """Test function succeeding after failures."""
        from codomyrmex.utils import retry

        call_count = 0

        @retry(max_attempts=3, delay=0.01)
        def fails_twice():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Temporary failure")
            return "success"

        result = fails_twice()

        assert result == "success"
        assert call_count == 3

    def test_retry_all_attempts_fail(self):
        """Test function failing all attempts."""
        from codomyrmex.utils import retry

        @retry(max_attempts=2, delay=0.01)
        def always_fails():
            raise ValueError("Always fails")

        with pytest.raises(ValueError):
            always_fails()

    def test_retry_specific_exceptions(self):
        """Test retry with specific exception types."""
        from codomyrmex.utils import retry

        @retry(max_attempts=2, delay=0.01, exceptions=(ValueError,))
        def raises_type_error():
            raise TypeError("Not caught")

        with pytest.raises(TypeError):
            raises_type_error()

    def test_retry_with_backoff(self):
        """Test retry with exponential backoff."""
        from codomyrmex.utils import retry

        call_times = []

        @retry(max_attempts=3, delay=0.05, backoff=2.0)
        def track_calls():
            call_times.append(time.time())
            if len(call_times) < 3:
                raise ValueError("Fail")
            return "success"

        result = track_calls()

        assert result == "success"
        # Check delays increase
        if len(call_times) >= 3:
            delay1 = call_times[1] - call_times[0]
            delay2 = call_times[2] - call_times[1]
            assert delay2 > delay1


# From test_coverage_boost.py
class TestRetryConfig:
    """Tests for RetryConfig dataclass."""

    def test_defaults(self):
        from codomyrmex.utils.retry import RetryConfig

        cfg = RetryConfig()
        assert cfg.max_attempts == 3
        assert cfg.base_delay == 1.0
        assert cfg.max_delay == 60.0
        assert cfg.jitter is True

    def test_custom_values(self):
        from codomyrmex.utils.retry import RetryConfig

        cfg = RetryConfig(max_attempts=5, base_delay=0.1, jitter=False)
        assert cfg.max_attempts == 5
        assert cfg.jitter is False


# From test_coverage_boost.py
class TestComputeDelay:
    """Tests for _compute_delay helper."""

    def test_exponential_growth(self):
        from codomyrmex.utils.retry import RetryConfig, _compute_delay

        cfg = RetryConfig(base_delay=1.0, exponential_base=2.0, jitter=False)
        assert _compute_delay(0, cfg) == 1.0
        assert _compute_delay(1, cfg) == 2.0
        assert _compute_delay(2, cfg) == 4.0

    def test_max_delay_cap(self):
        from codomyrmex.utils.retry import RetryConfig, _compute_delay

        cfg = RetryConfig(base_delay=1.0, max_delay=5.0, jitter=False)
        assert _compute_delay(10, cfg) == 5.0  # Capped at max_delay

    def test_jitter_varies_output(self):
        from codomyrmex.utils.retry import RetryConfig, _compute_delay

        cfg = RetryConfig(base_delay=1.0, jitter=True)
        delays = {_compute_delay(1, cfg) for _ in range(20)}
        assert len(delays) > 1  # Jitter should produce different values


# From test_coverage_boost.py
class TestAsyncRetry:
    """Tests for the async retry decorator."""

    def test_async_succeeds(self):
        from codomyrmex.utils.retry import async_retry

        @async_retry(max_attempts=2, base_delay=0.001)
        async def succeed():
            return "async_ok"

        result = asyncio.new_event_loop().run_until_complete(succeed())
        assert result == "async_ok"

    def test_async_retries_then_succeeds(self):
        from codomyrmex.utils.retry import async_retry

        call_count = 0

        @async_retry(max_attempts=3, base_delay=0.001, jitter=False)
        async def flaky():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise OSError("retry me")
            return "recovered"

        result = asyncio.new_event_loop().run_until_complete(flaky())
        assert result == "recovered"
        assert call_count == 2

    def test_async_raises_after_exhaustion(self):
        from codomyrmex.utils.retry import async_retry

        @async_retry(max_attempts=2, base_delay=0.001, jitter=False)
        async def always_fail():
            raise OSError("async boom")

        with pytest.raises(OSError, match="async boom"):
            asyncio.new_event_loop().run_until_complete(always_fail())
