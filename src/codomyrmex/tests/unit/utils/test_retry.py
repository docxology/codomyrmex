"""
Unit tests for utils.retry — Zero-Mock compliant.

Covers: RetryConfig (defaults), _compute_delay (jitter on/off, max_delay),
retry decorator (success first try, success after retries, exhaustion,
non-retryable exception, preserves return value), async_retry decorator.
Uses base_delay=0.0 to avoid real sleeps in tests.
"""


import pytest

from codomyrmex.utils.retry import RetryConfig, _compute_delay, async_retry, retry

# ── RetryConfig ────────────────────────────────────────────────────────


@pytest.mark.unit
class TestRetryConfig:
    def test_defaults(self):
        c = RetryConfig()
        assert c.max_attempts == 3
        assert c.base_delay == pytest.approx(1.0)
        assert c.max_delay == pytest.approx(60.0)
        assert c.exponential_base == pytest.approx(2.0)
        assert c.jitter is True
        assert c.retryable_exceptions == (Exception,)

    def test_custom_values(self):
        c = RetryConfig(max_attempts=5, base_delay=0.5, jitter=False)
        assert c.max_attempts == 5
        assert c.base_delay == pytest.approx(0.5)
        assert c.jitter is False


# ── _compute_delay ─────────────────────────────────────────────────────


@pytest.mark.unit
class TestComputeDelay:
    def test_no_jitter_attempt_zero(self):
        c = RetryConfig(base_delay=1.0, exponential_base=2.0, jitter=False, max_delay=60.0)
        delay = _compute_delay(0, c)
        # 1.0 * 2^0 = 1.0
        assert delay == pytest.approx(1.0)

    def test_no_jitter_attempt_one(self):
        c = RetryConfig(base_delay=1.0, exponential_base=2.0, jitter=False, max_delay=60.0)
        delay = _compute_delay(1, c)
        # 1.0 * 2^1 = 2.0
        assert delay == pytest.approx(2.0)

    def test_no_jitter_attempt_three(self):
        c = RetryConfig(base_delay=1.0, exponential_base=2.0, jitter=False, max_delay=60.0)
        delay = _compute_delay(3, c)
        # 1.0 * 2^3 = 8.0
        assert delay == pytest.approx(8.0)

    def test_max_delay_capped(self):
        c = RetryConfig(base_delay=1.0, exponential_base=2.0, jitter=False, max_delay=5.0)
        delay = _compute_delay(10, c)
        assert delay == pytest.approx(5.0)

    def test_jitter_produces_value_in_range(self):
        c = RetryConfig(base_delay=1.0, exponential_base=2.0, jitter=True, max_delay=60.0)
        # With jitter, delay = 1.0 * uniform(0.5, 1.5) → [0.5, 1.5]
        for _ in range(20):
            delay = _compute_delay(0, c)
            assert 0.5 <= delay <= 1.5

    def test_zero_base_delay(self):
        c = RetryConfig(base_delay=0.0, exponential_base=2.0, jitter=False, max_delay=60.0)
        delay = _compute_delay(5, c)
        assert delay == pytest.approx(0.0)


# ── retry decorator ────────────────────────────────────────────────────


@pytest.mark.unit
class TestRetryDecorator:
    def test_success_on_first_try(self):
        call_count = [0]

        @retry(max_attempts=3, base_delay=0.0, jitter=False)
        def succeed():
            call_count[0] += 1
            return "ok"

        result = succeed()
        assert result == "ok"
        assert call_count[0] == 1

    def test_succeeds_after_one_retry(self):
        call_count = [0]

        @retry(max_attempts=3, base_delay=0.0, jitter=False)
        def fail_once():
            call_count[0] += 1
            if call_count[0] < 2:
                raise ValueError("transient")
            return "success"

        result = fail_once()
        assert result == "success"
        assert call_count[0] == 2

    def test_exhausts_all_attempts_and_raises(self):
        call_count = [0]

        @retry(max_attempts=3, base_delay=0.0, jitter=False)
        def always_fail():
            call_count[0] += 1
            raise RuntimeError("permanent")

        with pytest.raises(RuntimeError, match="permanent"):
            always_fail()
        assert call_count[0] == 3

    def test_non_retryable_exception_propagates_immediately(self):
        call_count = [0]

        @retry(max_attempts=3, base_delay=0.0, jitter=False, retryable_exceptions=(ValueError,))
        def wrong_exception():
            call_count[0] += 1
            raise TypeError("not retryable")

        with pytest.raises(TypeError, match="not retryable"):
            wrong_exception()
        # Should NOT be retried — only 1 attempt
        assert call_count[0] == 1

    def test_preserves_return_value(self):
        @retry(max_attempts=2, base_delay=0.0, jitter=False)
        def give_number():
            return 42

        assert give_number() == 42

    def test_preserves_function_name(self):
        @retry(max_attempts=2, base_delay=0.0)
        def my_function():
            return None

        assert my_function.__name__ == "my_function"

    def test_passes_arguments(self):
        @retry(max_attempts=2, base_delay=0.0, jitter=False)
        def add(a, b):
            return a + b

        assert add(2, 3) == 5

    def test_max_attempts_one_no_retry(self):
        call_count = [0]

        @retry(max_attempts=1, base_delay=0.0, jitter=False)
        def fail():
            call_count[0] += 1
            raise ValueError("fail")

        with pytest.raises(ValueError):
            fail()
        assert call_count[0] == 1

    def test_specific_retryable_exception(self):
        call_count = [0]

        @retry(max_attempts=3, base_delay=0.0, jitter=False, retryable_exceptions=(OSError,))
        def os_error():
            call_count[0] += 1
            raise OSError("io error")

        with pytest.raises(OSError):
            os_error()
        assert call_count[0] == 3


# ── async_retry decorator ──────────────────────────────────────────────


@pytest.mark.unit
@pytest.mark.asyncio
class TestAsyncRetryDecorator:
    async def test_async_success_first_try(self):
        call_count = [0]

        @async_retry(max_attempts=3, base_delay=0.0, jitter=False)
        async def async_succeed():
            call_count[0] += 1
            return "async_ok"

        result = await async_succeed()
        assert result == "async_ok"
        assert call_count[0] == 1

    async def test_async_succeeds_after_retry(self):
        call_count = [0]

        @async_retry(max_attempts=3, base_delay=0.0, jitter=False)
        async def async_fail_once():
            call_count[0] += 1
            if call_count[0] < 2:
                raise ValueError("transient")
            return "recovered"

        result = await async_fail_once()
        assert result == "recovered"
        assert call_count[0] == 2

    async def test_async_exhausts_attempts(self):
        call_count = [0]

        @async_retry(max_attempts=3, base_delay=0.0, jitter=False)
        async def async_always_fail():
            call_count[0] += 1
            raise RuntimeError("permanent async")

        with pytest.raises(RuntimeError, match="permanent async"):
            await async_always_fail()
        assert call_count[0] == 3

    async def test_async_preserves_return_value(self):
        @async_retry(max_attempts=2, base_delay=0.0, jitter=False)
        async def get_data():
            return {"key": "value"}

        result = await get_data()
        assert result == {"key": "value"}

    async def test_async_preserves_function_name(self):
        @async_retry(max_attempts=2, base_delay=0.0)
        async def my_async_fn():
            pass

        assert my_async_fn.__name__ == "my_async_fn"

    async def test_async_non_retryable_propagates(self):
        call_count = [0]

        @async_retry(max_attempts=3, base_delay=0.0, jitter=False, retryable_exceptions=(OSError,))
        async def async_type_error():
            call_count[0] += 1
            raise TypeError("not retryable async")

        with pytest.raises(TypeError):
            await async_type_error()
        assert call_count[0] == 1
