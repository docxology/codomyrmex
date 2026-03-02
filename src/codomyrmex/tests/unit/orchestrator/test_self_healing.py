"""Tests for Sprint 16: Self-Healing Orchestration.

Tests for failure_taxonomy, self_healing, retry_engine,
agent_circuit_breaker, healing_log.
"""

from __future__ import annotations

from codomyrmex.orchestrator.resilience.agent_circuit_breaker import (
    AgentHealth,
    CircuitBreaker,
    CircuitState,
)
from codomyrmex.orchestrator.resilience.failure_taxonomy import (
    FailureCategory,
    classify_error,
)
from codomyrmex.orchestrator.resilience.healing_log import (
    HealingEvent,
    HealingLog,
)
from codomyrmex.orchestrator.resilience.retry_engine import (
    RetryEngine,
    RetryResult,
)
from codomyrmex.orchestrator.resilience.self_healing import (
    Diagnoser,
)

# ── FailureTaxonomy ──────────────────────────────────────────────


class TestClassifyError:
    """Test suite for ClassifyError."""
    def test_config_error(self) -> None:
        """Test functionality: config error."""
        result = classify_error("Invalid config value for model")
        assert result.category == FailureCategory.CONFIG_ERROR

    def test_resource_error(self) -> None:
        """Test functionality: resource error."""
        result = classify_error("Out of memory (OOM)")
        assert result.category == FailureCategory.RESOURCE_EXHAUSTION

    def test_dependency_error(self) -> None:
        """Test functionality: dependency error."""
        result = classify_error("Connection refused to API")
        assert result.category == FailureCategory.DEPENDENCY_FAILURE

    def test_timeout(self) -> None:
        """Test functionality: timeout."""
        result = classify_error("Request timed out")
        assert result.category == FailureCategory.TIMEOUT

    def test_permission(self) -> None:
        """Test functionality: permission."""
        result = classify_error("Permission denied")
        assert result.category == FailureCategory.PERMISSION_ERROR

    def test_logic_error(self) -> None:
        """Test functionality: logic error."""
        result = classify_error("Assertion failed: expected True")
        assert result.category == FailureCategory.LOGIC_ERROR

    def test_unknown(self) -> None:
        """Test functionality: unknown."""
        result = classify_error("Something weird happened")
        assert result.category == FailureCategory.UNKNOWN
        assert result.confidence < 1.0

    def test_classified_to_dict(self) -> None:
        """Test functionality: classified to dict."""
        result = classify_error("Config issue")
        d = result.to_dict()
        assert "category" in d
        assert "strategies" in d

    def test_strategies_populated(self) -> None:
        """Test functionality: strategies populated."""
        result = classify_error("Config problem")
        assert len(result.suggested_strategies) >= 1


# ── Diagnoser ────────────────────────────────────────────────────


class TestDiagnoser:
    """Test suite for Diagnoser."""
    def test_diagnose_config_error(self) -> None:
        """Test functionality: diagnose config error."""
        diag = Diagnoser()
        diagnosis = diag.diagnose("Invalid config value")
        assert diagnosis.root_cause
        assert len(diagnosis.recovery_plan) >= 1
        assert diagnosis.impact == "medium"

    def test_diagnose_timeout(self) -> None:
        """Test functionality: diagnose timeout."""
        diag = Diagnoser()
        diagnosis = diag.diagnose("Request timed out after 30s")
        assert diagnosis.error.category == FailureCategory.TIMEOUT
        assert diagnosis.impact == "low"

    def test_diagnose_with_context(self) -> None:
        """Test functionality: diagnose with context."""
        diag = Diagnoser()
        diagnosis = diag.diagnose("OOM error", context={"agent": "agent-1"})
        assert diagnosis.error.context.get("agent") == "agent-1"
        assert diagnosis.impact == "high"

    def test_diagnosis_to_dict(self) -> None:
        """Test functionality: diagnosis to dict."""
        diag = Diagnoser()
        d = diag.diagnose("Some error").to_dict()
        assert "root_cause" in d
        assert "steps" in d


# ── RetryEngine ──────────────────────────────────────────────────


class TestRetryEngine:
    """Test suite for RetryEngine."""
    def test_immediate_success(self) -> None:
        """Test functionality: immediate success."""
        engine = RetryEngine(max_retries=3, base_delay=0.001)
        result = engine.execute(lambda: 42)
        assert result.success
        assert result.result == 42
        assert result.attempts == 1

    def test_retry_then_success(self) -> None:
        """Test functionality: retry then success."""
        call_count = {"n": 0}
        def flaky():
            call_count["n"] += 1
            if call_count["n"] < 3:
                raise RuntimeError("Temporary failure")
            return "ok"

        engine = RetryEngine(max_retries=5, base_delay=0.001)
        result = engine.execute(flaky)
        assert result.success
        assert result.attempts == 3

    def test_all_retries_fail(self) -> None:
        """Test functionality: all retries fail."""
        engine = RetryEngine(max_retries=2, base_delay=0.001)
        result = engine.execute(lambda: 1 / 0)
        assert not result.success
        assert result.attempts == 3
        assert len(result.errors) == 3

    def test_result_to_dict(self) -> None:
        """Test functionality: result to dict."""
        r = RetryResult(success=True, attempts=1)
        d = r.to_dict()
        assert d["success"] is True


# ── CircuitBreaker ───────────────────────────────────────────────


class TestCircuitBreaker:
    """Test suite for CircuitBreaker."""
    def test_allow_when_closed(self) -> None:
        """Test functionality: allow when closed."""
        cb = CircuitBreaker(failure_threshold=3)
        cb.register("a1")
        assert cb.allow("a1") is True

    def test_open_after_failures(self) -> None:
        """Test functionality: open after failures."""
        cb = CircuitBreaker(failure_threshold=3)
        cb.register("a1")
        for _ in range(3):
            cb.record_failure("a1")
        assert cb.allow("a1") is False
        health = cb.get_health("a1")
        assert health is not None
        assert health.state == CircuitState.OPEN

    def test_half_open_after_cooldown(self) -> None:
        """Test functionality: half open after cooldown."""
        cb = CircuitBreaker(failure_threshold=2, cooldown_seconds=0.01)
        cb.register("a1")
        cb.record_failure("a1")
        cb.record_failure("a1")
        assert cb.allow("a1") is False
        import time
        time.sleep(0.02)
        assert cb.allow("a1") is True
        health = cb.get_health("a1")
        assert health is not None
        assert health.state == CircuitState.HALF_OPEN

    def test_close_after_success(self) -> None:
        """Test functionality: close after success."""
        cb = CircuitBreaker(failure_threshold=2, cooldown_seconds=0.01)
        cb.register("a1")
        cb.record_failure("a1")
        cb.record_failure("a1")
        import time
        time.sleep(0.02)
        cb.allow("a1")  # Transitions to HALF_OPEN
        cb.record_success("a1")
        health = cb.get_health("a1")
        assert health is not None
        assert health.state == CircuitState.CLOSED

    def test_reset(self) -> None:
        """Test functionality: reset."""
        cb = CircuitBreaker(failure_threshold=1)
        cb.register("a1")
        cb.record_failure("a1")
        cb.reset("a1")
        assert cb.allow("a1") is True

    def test_health_to_dict(self) -> None:
        """Test functionality: health to dict."""
        h = AgentHealth(agent_id="x", total_successes=8, total_failures=2)
        d = h.to_dict()
        assert d["failure_rate"] == 0.2

    def test_unknown_agent(self) -> None:
        """Test functionality: unknown agent."""
        cb = CircuitBreaker()
        assert cb.allow("unknown") is True


# ── HealingLog ───────────────────────────────────────────────────


class TestHealingEvent:
    """Test suite for HealingEvent."""
    def test_auto_id(self) -> None:
        """Test functionality: auto id."""
        e = HealingEvent(error_category="timeout")
        assert e.event_id.startswith("heal-")

    def test_to_jsonl(self) -> None:
        """Test functionality: to jsonl."""
        e = HealingEvent(error_category="config_error", outcome="success")
        j = e.to_jsonl()
        assert "config_error" in j
        assert "success" in j


class TestHealingLog:
    """Test suite for HealingLog."""
    def test_record_and_size(self) -> None:
        """Test functionality: record and size."""
        log = HealingLog()
        log.record(HealingEvent(outcome="success"))
        assert log.size == 1

    def test_success_rate(self) -> None:
        """Test functionality: success rate."""
        log = HealingLog()
        log.record(HealingEvent(outcome="success"))
        log.record(HealingEvent(outcome="failure"))
        assert log.success_rate == 0.5

    def test_events_by_category(self) -> None:
        """Test functionality: events by category."""
        log = HealingLog()
        log.record(HealingEvent(error_category="timeout", outcome="success"))
        log.record(HealingEvent(error_category="config", outcome="success"))
        assert len(log.events_by_category("timeout")) == 1

    def test_summary(self) -> None:
        """Test functionality: summary."""
        log = HealingLog()
        log.record(HealingEvent(error_category="timeout", outcome="success"))
        s = log.summary()
        assert s["total_events"] == 1
        assert "timeout" in s["by_category"]

    def test_to_jsonl(self) -> None:
        """Test functionality: to jsonl."""
        log = HealingLog()
        log.record(HealingEvent(outcome="success"))
        log.record(HealingEvent(outcome="failure"))
        lines = log.to_jsonl().strip().split("\n")
        assert len(lines) == 2
