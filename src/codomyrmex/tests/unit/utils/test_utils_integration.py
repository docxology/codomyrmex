"""Tests for utils.integration module."""

import asyncio
import logging
import time

import pytest

try:
    from codomyrmex.utils.integration import (
        HealthChecker,
        HealthStatus,
        ModuleRegistry,
        RetryConfig,
        async_timed_operation,
        gather_with_concurrency,
        log_performance,
        make_async,
        registry,
        run_async,
        setup_module_logging,
        timed_operation,
        with_retry,
    )
    HAS_MODULE = True
except ImportError:
    HAS_MODULE = False

if not HAS_MODULE:
    pytest.skip("utils.integration module not available", allow_module_level=True)


def _run(coro):
    """Helper to run async code in sync tests."""
    return asyncio.run(coro)


# ---------------------------------------------------------------------------
# setup_module_logging
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestSetupModuleLogging:
    """Test suite for SetupModuleLogging."""
    def test_creates_logger(self):
        """Test functionality: creates logger."""
        log = setup_module_logging("test_module")
        assert isinstance(log, logging.Logger)
        assert log.name == "codomyrmex.test_module"

    def test_sets_level(self):
        """Test functionality: sets level."""
        log = setup_module_logging("test_level", level=logging.DEBUG)
        assert log.level == logging.DEBUG

    def test_custom_format(self):
        """Test functionality: custom format."""
        log = setup_module_logging("test_fmt", format_str="%(message)s")
        assert log is not None

    def test_idempotent_handlers(self):
        """Calling setup twice should not add duplicate handlers."""
        log1 = setup_module_logging("test_idem")
        handler_count = len(log1.handlers)
        log2 = setup_module_logging("test_idem")
        assert len(log2.handlers) == handler_count


# ---------------------------------------------------------------------------
# log_performance decorator
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestLogPerformance:
    """Test suite for LogPerformance."""
    def test_decorator_preserves_return_value(self):
        """Test functionality: decorator preserves return value."""
        @log_performance("test_op")
        def add(a, b):
            return a + b

        assert add(1, 2) == 3

    def test_decorator_preserves_function_name(self):
        """Test functionality: decorator preserves function name."""
        @log_performance("test_op")
        def my_func():
            pass

        assert my_func.__name__ == "my_func"

    def test_decorator_raises_on_error(self):
        """Test functionality: decorator raises on error."""
        @log_performance("test_op")
        def failing():
            raise ValueError("fail")

        with pytest.raises(ValueError, match="fail"):
            failing()


# ---------------------------------------------------------------------------
# run_async
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestRunAsync:
    """Test suite for RunAsync."""
    def test_runs_coroutine(self):
        """Test functionality: runs coroutine."""
        async def coro():
            return 42

        result = run_async(coro())
        assert result == 42

    def test_returns_value(self):
        """Test functionality: returns value."""
        async def coro():
            return "hello"

        assert run_async(coro()) == "hello"


# ---------------------------------------------------------------------------
# make_async
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestMakeAsync:
    """Test suite for MakeAsync."""
    def test_converts_sync_to_async(self):
        """Test functionality: converts sync to async."""
        def sync_fn(x):
            return x * 2

        async def _test():
            async_fn = make_async(sync_fn)
            result = await async_fn(5)
            assert result == 10

        _run(_test())

    def test_preserves_function_name(self):
        """Test functionality: preserves function name."""
        def my_function():
            pass

        wrapped = make_async(my_function)
        assert wrapped.__name__ == "my_function"


# ---------------------------------------------------------------------------
# RetryConfig
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestRetryConfig:
    """Test suite for RetryConfig."""
    def test_defaults(self):
        """Test functionality: defaults."""
        config = RetryConfig()
        assert config.max_attempts == 3
        assert config.initial_delay == 0.1
        assert config.max_delay == 10.0
        assert config.exponential_base == 2.0
        assert config.jitter is True

    def test_custom(self):
        """Test functionality: custom."""
        config = RetryConfig(
            max_attempts=5,
            initial_delay=0.5,
            max_delay=30.0,
            exponential_base=3.0,
            jitter=False,
        )
        assert config.max_attempts == 5
        assert config.jitter is False


# ---------------------------------------------------------------------------
# with_retry decorator
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestWithRetry:
    """Test suite for WithRetry."""
    def test_succeeds_first_try(self):
        """Test functionality: succeeds first try."""
        call_count = 0

        @with_retry(RetryConfig(max_attempts=3, initial_delay=0.001))
        def succeed():
            nonlocal call_count
            call_count += 1
            return "ok"

        result = succeed()
        assert result == "ok"
        assert call_count == 1

    def test_retries_on_failure(self):
        """Test functionality: retries on failure."""
        call_count = 0

        @with_retry(RetryConfig(max_attempts=3, initial_delay=0.001, jitter=False))
        def fail_twice():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("not yet")
            return "ok"

        result = fail_twice()
        assert result == "ok"
        assert call_count == 3

    def test_raises_after_max_attempts(self):
        """Test functionality: raises after max attempts."""
        @with_retry(RetryConfig(max_attempts=2, initial_delay=0.001, jitter=False))
        def always_fail():
            raise RuntimeError("always")

        with pytest.raises(RuntimeError, match="always"):
            always_fail()

    def test_only_retries_specified_exceptions(self):
        """Test functionality: only retries specified exceptions."""
        @with_retry(RetryConfig(
            max_attempts=3,
            initial_delay=0.001,
            retryable_exceptions=(ValueError,),
        ))
        def wrong_error():
            raise TypeError("wrong type")

        with pytest.raises(TypeError):
            wrong_error()


# ---------------------------------------------------------------------------
# timed_operation
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestTimedOperation:
    """Test suite for TimedOperation."""
    def test_context_manager(self):
        """Test functionality: context manager."""
        with timed_operation("test_op"):
            time.sleep(0.01)
        # Should not raise

    def test_yields_control(self):
        """Test functionality: yields control."""
        result = None
        with timed_operation("test_op"):
            result = 42
        assert result == 42


# ---------------------------------------------------------------------------
# async_timed_operation
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestAsyncTimedOperation:
    """Test suite for AsyncTimedOperation."""
    def test_async_context_manager(self):
        """Test functionality: async context manager."""
        async def _test():
            async with async_timed_operation("test_op"):
                await asyncio.sleep(0.01)

        _run(_test())

    def test_yields_control(self):
        """Test functionality: yields control."""
        async def _test():
            result = None
            async with async_timed_operation("test_op"):
                result = 42
            assert result == 42

        _run(_test())


# ---------------------------------------------------------------------------
# ModuleRegistry
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestModuleRegistry:
    """Test suite for ModuleRegistry."""
    def test_singleton(self):
        """Test functionality: singleton."""
        r1 = ModuleRegistry()
        r2 = ModuleRegistry()
        assert r1 is r2

    def test_register_and_get(self):
        """Test functionality: register and get."""
        reg = ModuleRegistry()
        reg.register("test_module_xyz", {"name": "test"})
        result = reg.get("test_module_xyz")
        assert result is not None
        assert result["name"] == "test"

    def test_get_nonexistent(self):
        """Test functionality: get nonexistent."""
        reg = ModuleRegistry()
        assert reg.get("nonexistent_module_abc") is None

    def test_add_hook_and_trigger(self):
        """Test functionality: add hook and trigger."""
        reg = ModuleRegistry()
        results = []
        reg.add_hook("test_event_xyz", lambda: results.append("called"))
        reg.trigger("test_event_xyz")
        assert len(results) == 1

    def test_trigger_with_args(self):
        """Test functionality: trigger with args."""
        reg = ModuleRegistry()
        received = []
        reg.add_hook("test_args_xyz", lambda x, y: received.append((x, y)))
        reg.trigger("test_args_xyz", 1, 2)
        assert received == [(1, 2)]

    def test_trigger_nonexistent_event(self):
        """Test functionality: trigger nonexistent event."""
        reg = ModuleRegistry()
        results = reg.trigger("nonexistent_event_abc")
        assert results == []

    def test_global_registry_instance(self):
        """Test functionality: global registry instance."""
        assert registry is not None
        assert isinstance(registry, ModuleRegistry)


# ---------------------------------------------------------------------------
# HealthStatus
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestHealthStatus:
    """Test suite for HealthStatus."""
    def test_create_healthy(self):
        """Test functionality: create healthy."""
        status = HealthStatus(healthy=True, name="test_service")
        assert status.healthy is True
        assert status.name == "test_service"
        assert status.message == ""

    def test_create_unhealthy(self):
        """Test functionality: create unhealthy."""
        status = HealthStatus(
            healthy=False,
            name="db",
            message="Connection refused",
        )
        assert status.healthy is False
        assert "Connection refused" in status.message

    def test_defaults(self):
        """Test functionality: defaults."""
        status = HealthStatus(healthy=True, name="test")
        assert status.latency_ms == 0.0
        assert status.details == {}


# ---------------------------------------------------------------------------
# HealthChecker
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestHealthChecker:
    """Test suite for HealthChecker."""
    def test_create(self):
        """Test functionality: create."""
        checker = HealthChecker()
        assert checker._checks == {}

    def test_register_check(self):
        """Test functionality: register check."""
        checker = HealthChecker()
        checker.register("db", lambda: HealthStatus(healthy=True, name="db"))
        assert "db" in checker._checks

    def test_check_all_healthy(self):
        """Test functionality: check all healthy."""
        checker = HealthChecker()
        checker.register("db", lambda: HealthStatus(healthy=True, name="db"))
        checker.register("cache", lambda: HealthStatus(healthy=True, name="cache"))
        results = checker.check_all()
        assert len(results) == 2
        assert all(s.healthy for s in results.values())

    def test_check_all_with_failure(self):
        """Test functionality: check all with failure."""
        checker = HealthChecker()
        checker.register("db", lambda: HealthStatus(healthy=True, name="db"))
        checker.register("broken", lambda: HealthStatus(healthy=False, name="broken"))
        results = checker.check_all()
        assert results["db"].healthy is True
        assert results["broken"].healthy is False

    def test_check_all_handles_exception(self):
        """Test functionality: check all handles exception."""
        checker = HealthChecker()

        def exploding_check():
            raise ConnectionError("boom")

        checker.register("bad", exploding_check)
        results = checker.check_all()
        assert results["bad"].healthy is False
        assert "boom" in results["bad"].message

    def test_is_healthy_all_good(self):
        """Test functionality: is healthy all good."""
        checker = HealthChecker()
        checker.register("a", lambda: HealthStatus(healthy=True, name="a"))
        assert checker.is_healthy() is True

    def test_is_healthy_one_bad(self):
        """Test functionality: is healthy one bad."""
        checker = HealthChecker()
        checker.register("a", lambda: HealthStatus(healthy=True, name="a"))
        checker.register("b", lambda: HealthStatus(healthy=False, name="b"))
        assert checker.is_healthy() is False

    def test_latency_measured(self):
        """Test functionality: latency measured."""
        checker = HealthChecker()

        def slow_check():
            time.sleep(0.02)
            return HealthStatus(healthy=True, name="slow")

        checker.register("slow", slow_check)
        results = checker.check_all()
        assert results["slow"].latency_ms >= 10  # At least 10ms


# ---------------------------------------------------------------------------
# gather_with_concurrency
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestGatherWithConcurrency:
    """Test suite for GatherWithConcurrency."""
    def test_runs_coroutines(self):
        """Test functionality: runs coroutines."""
        async def _test():
            async def double(x):
                return x * 2

            results = await gather_with_concurrency(
                [double(1), double(2), double(3)],
                max_concurrent=2,
            )
            assert sorted(results) == [2, 4, 6]

        _run(_test())

    def test_respects_concurrency_limit(self):
        """Test functionality: respects concurrency limit."""
        async def _test():
            running = 0
            max_running = 0

            async def track():
                nonlocal running, max_running
                running += 1
                max_running = max(max_running, running)
                await asyncio.sleep(0.01)
                running -= 1

            await gather_with_concurrency(
                [track() for _ in range(10)],
                max_concurrent=3,
            )
            assert max_running <= 3

        _run(_test())
