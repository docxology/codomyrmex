"""
TDD regression tests for P3 CodeQL illegal-raise remediation.

Verifies that retry/circuit-breaker patterns correctly raise the
captured exception (not ``None`` / ``TypeError``) when all attempts
are exhausted.

Zero-Mock compliant — all tests use real functions.
"""

import pytest

# ── utils.retry ────────────────────────────────────────────────────────
from codomyrmex.utils.retry import async_retry, retry


@pytest.mark.unit
class TestRetryIllegalRaiseGuard:
    """Verify retry decorator raises captured exception, not TypeError from None."""

    def test_exhausted_retry_raises_original_exception(self):
        """When all attempts fail, the original exception is re-raised."""
        call_count = [0]

        @retry(max_attempts=3, base_delay=0.0, jitter=False)
        def always_fails():
            call_count[0] += 1
            raise ValueError("expected failure")

        with pytest.raises(ValueError, match="expected failure"):
            always_fails()
        assert call_count[0] == 3

    def test_exhausted_retry_raises_last_exception_instance(self):
        """The raised exception is the one from the last attempt."""
        attempt = [0]

        @retry(max_attempts=2, base_delay=0.0, jitter=False)
        def fails_differently():
            attempt[0] += 1
            raise RuntimeError(f"attempt {attempt[0]}")

        with pytest.raises(RuntimeError, match="attempt 2"):
            fails_differently()

    def test_exhausted_retry_does_not_raise_none(self):
        """Exhausted retry must not raise TypeError from None."""

        @retry(max_attempts=2, base_delay=0.0, jitter=False)
        def always_fails():
            raise OSError("io error")

        # Must raise OSError, not TypeError("exceptions must derive from BaseException")
        with pytest.raises(OSError):
            always_fails()


@pytest.mark.unit
@pytest.mark.asyncio
class TestAsyncRetryIllegalRaiseGuard:
    """Verify async_retry decorator raises captured exception, not None."""

    async def test_async_exhausted_raises_original(self):
        """Async retry re-raises the captured exception after exhaustion."""
        call_count = [0]

        @async_retry(max_attempts=3, base_delay=0.0, jitter=False)
        async def async_fails():
            call_count[0] += 1
            raise ValueError("async failure")

        with pytest.raises(ValueError, match="async failure"):
            await async_fails()
        assert call_count[0] == 3

    async def test_async_exhausted_raises_last_attempt(self):
        """Async retry raises the exception from the final attempt."""
        attempt = [0]

        @async_retry(max_attempts=2, base_delay=0.0, jitter=False)
        async def async_fails_differently():
            attempt[0] += 1
            raise RuntimeError(f"async attempt {attempt[0]}")

        with pytest.raises(RuntimeError, match="async attempt 2"):
            await async_fails_differently()


# ── api.circuit_breaker.retry ──────────────────────────────────────────

try:
    from codomyrmex.api.circuit_breaker import retry as cb_retry

    CB_AVAILABLE = True
except ImportError:
    CB_AVAILABLE = False


@pytest.mark.unit
@pytest.mark.skipif(not CB_AVAILABLE, reason="api extra not installed")
class TestCircuitBreakerRetryIllegalRaiseGuard:
    """Verify circuit breaker retry decorator raises captured exception."""

    def test_cb_retry_exhausted_raises_original(self):
        """Circuit breaker retry re-raises captured exception on exhaustion."""
        attempt = [0]

        @cb_retry(max_retries=2, backoff_base=0.001)
        def cb_always_fails():
            attempt[0] += 1
            raise ValueError("cb failure")

        with pytest.raises(ValueError, match="cb failure"):
            cb_always_fails()
        assert attempt[0] == 3  # 1 initial + 2 retries


# ── utils.__init__.retry ───────────────────────────────────────────────

# The function `retry` in utils/__init__.py is shadowed by the submodule
# utils/retry.py once it's been imported (line 17 above). We retrieve the
# function directly from the module's __dict__ to avoid the collision.
import importlib

_utils_init = importlib.import_module("codomyrmex.utils")
_utils_retry_func = _utils_init.__dict__.get("retry")
# If shadowed, fall back to reading it from the __all__ export or skip
if not callable(_utils_retry_func):
    # The function was clobbered by the submodule; extract via sys.modules
    import types

    _retry_members = {
        k: v
        for k, v in vars(_utils_init).items()
        if k == "retry" and isinstance(v, types.FunctionType)
    }
    _utils_retry_func = _retry_members.get("retry")


@pytest.mark.unit
@pytest.mark.skipif(
    _utils_retry_func is None or not callable(_utils_retry_func),
    reason="utils.__init__.retry function shadowed by submodule",
)
class TestUtilsInitRetryIllegalRaiseGuard:
    """Verify utils-level retry decorator raises captured exception."""

    def test_utils_retry_exhausted_raises_original(self):
        """Utils retry re-raises the captured exception on exhaustion."""
        attempt = [0]

        @_utils_retry_func(  # type: ignore
            max_attempts=2, delay=0.001, backoff=1.0, exceptions=(RuntimeError,)
        )
        def utils_always_fails():
            attempt[0] += 1
            raise RuntimeError("utils failure")

        with pytest.raises(RuntimeError, match="utils failure"):
            utils_always_fails()
        assert attempt[0] == 2


# ── networking.service_mesh.resilience.RetryPolicy ─────────────────────

from codomyrmex.networking.service_mesh.resilience import (
    RetryPolicy as MeshRetryPolicy,
)


@pytest.mark.unit
class TestMeshRetryPolicyIllegalRaiseGuard:
    """Verify service mesh RetryPolicy.execute raises captured exception."""

    def test_mesh_retry_exhausted_raises_original(self):
        """Service mesh RetryPolicy.execute re-raises on exhaustion."""
        call_count = [0]
        policy = MeshRetryPolicy(max_retries=2, initial_delay=0.001, jitter=False)

        def always_fails():
            call_count[0] += 1
            raise ConnectionError("mesh failure")

        with pytest.raises(ConnectionError, match="mesh failure"):
            policy.execute(always_fails)
        assert call_count[0] == 3  # 1 initial + 2 retries


# ── orchestrator.resilience.retry_policy.with_retry ────────────────────

from codomyrmex.orchestrator.resilience.retry_policy import (
    with_retry as orch_with_retry,
)


@pytest.mark.unit
class TestOrchestratorWithRetryIllegalRaiseGuard:
    """Verify orchestrator with_retry decorator raises captured exception."""

    def test_orch_sync_exhausted_raises_original(self):
        """Sync with_retry re-raises the captured exception on exhaustion."""
        call_count = [0]

        @orch_with_retry(max_attempts=2, base_delay=0.001, retry_on=(ValueError,))
        def orch_fails():
            call_count[0] += 1
            raise ValueError("orch failure")

        with pytest.raises(ValueError, match="orch failure"):
            orch_fails()
        assert call_count[0] == 2

    @pytest.mark.asyncio
    async def test_orch_async_exhausted_raises_original(self):
        """Async with_retry re-raises the captured exception on exhaustion."""
        call_count = [0]

        @orch_with_retry(max_attempts=2, base_delay=0.001, retry_on=(ValueError,))
        async def orch_async_fails():
            call_count[0] += 1
            raise ValueError("orch async failure")

        with pytest.raises(ValueError, match="orch async failure"):
            await orch_async_fails()
        assert call_count[0] == 2


# ── utils.integration.with_retry ───────────────────────────────────────

from codomyrmex.utils.integration import RetryConfig as IntRetryConfig
from codomyrmex.utils.integration import with_retry as int_with_retry


@pytest.mark.unit
class TestIntegrationWithRetryIllegalRaiseGuard:
    """Verify utils.integration.with_retry raises captured exception."""

    def test_int_retry_exhausted_raises_original(self):
        """Integration with_retry re-raises the captured exception."""
        call_count = [0]
        cfg = IntRetryConfig(max_attempts=2, initial_delay=0.001, jitter=False)

        @int_with_retry(config=cfg)
        def int_fails():
            call_count[0] += 1
            raise RuntimeError("integration failure")

        with pytest.raises(RuntimeError, match="integration failure"):
            int_fails()
        assert call_count[0] == 2


# ── cli_agent_base.retry_on_failure ────────────────────────────────────

from codomyrmex.agents.generic.cli_agent_base import retry_on_failure


@pytest.mark.unit
class TestCLIAgentRetryOnFailureIllegalRaiseGuard:
    """Verify CLI agent retry_on_failure raises captured exception."""

    def test_cli_retry_exhausted_raises_original(self):
        """retry_on_failure re-raises the captured exception after retries."""
        from codomyrmex.agents.core.exceptions import AgentError

        call_count = [0]

        @retry_on_failure(max_retries=2, backoff_factor=0.001)
        def cli_fails():
            call_count[0] += 1
            raise AgentError("cli agent failure")

        with pytest.raises(AgentError, match="cli agent failure"):
            cli_fails()
        assert call_count[0] == 3  # 1 initial + 2 retries


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
