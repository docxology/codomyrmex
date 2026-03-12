"""Tests for v1.2.1 — Utilities, Skills & Codebase Awareness.

Zero-Mock: All tests use real implementations.
"""

from __future__ import annotations

import logging

import pytest

# ── A1: Module Introspector ───────────────────────────────────────
from codomyrmex.system_discovery.module_introspector import (
    ModuleInfo,
    ModuleIntrospector,
)


class TestModuleIntrospector:
    """Verify deep module scanning."""

    def test_scan_all_finds_modules(self) -> None:
        intro = ModuleIntrospector()
        report = intro.scan_all()
        assert report["total_modules"] >= 100

    def test_scan_all_has_loc(self) -> None:
        intro = ModuleIntrospector()
        report = intro.scan_all()
        assert report["total_loc"] > 50000

    def test_scan_all_has_classes(self) -> None:
        intro = ModuleIntrospector()
        report = intro.scan_all()
        assert report["total_classes"] > 100

    def test_scan_all_health_distribution(self) -> None:
        intro = ModuleIntrospector()
        report = intro.scan_all()
        dist = report["health_distribution"]
        assert dist["healthy"] + dist["partial"] + dist["minimal"] == report["total_modules"]

    def test_scan_single_module(self) -> None:
        from pathlib import Path

        intro = ModuleIntrospector()
        utils_path = Path(intro._root) / "utils"
        info = intro.scan_module(utils_path)
        assert info.name == "utils"
        assert info.file_count > 5
        assert info.has_init

    def test_module_info_health(self) -> None:
        info = ModuleInfo(name="test", path="/tmp/test")
        info.has_readme = True
        info.has_agents = True
        info.has_spec = True
        info.has_init = True
        info.has_tests = True
        assert info.health == "healthy"
        assert info.doc_score == 1.0

    def test_module_info_minimal(self) -> None:
        info = ModuleInfo(name="minimal", path="/tmp/minimal")
        assert info.health == "minimal"
        assert info.doc_score == 0.0

    def test_top_modules(self) -> None:
        intro = ModuleIntrospector()
        top = intro.get_top_modules(n=5, by="loc")
        assert len(top) == 5
        assert top[0]["loc"] >= top[1]["loc"]  # Sorted descending

    def test_mcp_tools_detected(self) -> None:
        intro = ModuleIntrospector()
        report = intro.scan_all()
        assert report["total_mcp_tools"] > 50


# ── B1: Structured Log Context ────────────────────────────────────

from codomyrmex.logging_monitoring.log_context import (
    CorrelationFilter,
    LogContext,
    get_correlation_id,
    get_log_tags,
)


class TestLogContext:
    """Verify structured log context."""

    def test_auto_correlation_id(self) -> None:
        with LogContext(module="test", operation="verify") as ctx:
            assert len(ctx.correlation_id) == 12

    def test_explicit_correlation_id(self) -> None:
        with LogContext(correlation_id="abc123") as ctx:
            assert ctx.correlation_id == "abc123"

    def test_extra_dict(self) -> None:
        ctx = LogContext(module="agents", operation="start", tags={"model": "gemma3"})
        with ctx:
            extra = ctx.extra()
            assert extra["module"] == "agents"
            assert extra["operation"] == "start"
            assert extra["model"] == "gemma3"

    def test_context_var_set(self) -> None:
        with LogContext(module="test") as ctx:
            assert get_correlation_id() == ctx.correlation_id
            tags = get_log_tags()
            assert tags["module"] == "test"

    def test_elapsed_ms(self) -> None:
        import time

        with LogContext() as ctx:
            time.sleep(0.01)
            assert ctx.elapsed_ms > 5  # At least 5ms

    def test_correlation_filter(self) -> None:
        f = CorrelationFilter()
        record = logging.LogRecord("test", logging.INFO, "", 0, "msg", (), None)
        with LogContext(correlation_id="xyz789"):
            f.filter(record)
            assert record.correlation_id == "xyz789"  # type: ignore[attr-defined]


# ── C1: Skill Health Checker ──────────────────────────────────────

from codomyrmex.skills.skill_health import (
    SkillHealth,
    SkillHealthChecker,
)


class TestSkillHealthChecker:
    """Verify skill health checking."""

    def test_check_all(self) -> None:
        checker = SkillHealthChecker()
        report = checker.check_all()
        assert report["total_skills"] >= 1

    def test_health_distribution(self) -> None:
        checker = SkillHealthChecker()
        report = checker.check_all()
        dist = report["health_distribution"]
        total = dist["complete"] + dist["functional"] + dist["stub"]
        assert total == report["total_skills"]

    def test_skill_health_properties(self) -> None:
        h = SkillHealth(name="test", path="/tmp/test")
        h.has_skill_md = True
        h.has_init = True
        assert h.health == "functional"  # No tests → functional not complete

    def test_skill_completeness(self) -> None:
        h = SkillHealth(name="test", path="/tmp/test")
        h.has_skill_md = True
        h.has_init = True
        h.has_scripts = True
        h.has_examples = True
        h.has_tests = True
        assert h.completeness == 1.0
        assert h.health == "complete"


# ── C2: Dependency Mapper ────────────────────────────────────────

from codomyrmex.system_discovery.dependency_mapper import (
    DependencyMapper,
)


class TestDependencyMapper:
    """Verify AST-based dependency mapping."""

    def test_build_graph(self) -> None:
        mapper = DependencyMapper()
        graph = mapper.build_graph()
        assert graph["total_modules"] >= 100
        assert graph["total_edges"] > 50

    def test_top_imported(self) -> None:
        mapper = DependencyMapper()
        graph = mapper.build_graph()
        assert len(graph["top_imported"]) > 0
        # logging_monitoring and utils should be highly imported
        top_names = [n for n, _ in graph["top_imported"]]
        assert "logging_monitoring" in top_names or "utils" in top_names

    def test_get_dependencies(self) -> None:
        mapper = DependencyMapper()
        deps = mapper.get_dependencies("cli")
        assert isinstance(deps, list)
        # CLI depends on logging_monitoring
        assert "logging_monitoring" in deps

    def test_get_dependents(self) -> None:
        mapper = DependencyMapper()
        dependents = mapper.get_dependents("logging_monitoring")
        assert len(dependents) > 10  # Many modules use logging

    def test_nonexistent_module(self) -> None:
        mapper = DependencyMapper()
        deps = mapper.get_dependencies("nonexistent_xyz")
        assert deps == []


# ── D1: Enhanced Retry ────────────────────────────────────────────

from codomyrmex.utils.retry_enhanced import (
    RetryStats,
    retry,
    retry_with_stats,
)


class TestRetryEnhanced:
    """Verify enhanced retry decorator."""

    def test_succeeds_first_try(self) -> None:
        call_count = 0

        @retry(max_attempts=3, base_delay=0.01)
        def succeeding():
            nonlocal call_count
            call_count += 1
            return 42

        assert succeeding() == 42
        assert call_count == 1

    def test_retries_on_failure(self) -> None:
        call_count = 0

        @retry(max_attempts=3, base_delay=0.01)
        def fails_twice():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                msg = "Not yet"
                raise ValueError(msg)
            return "ok"

        assert fails_twice() == "ok"
        assert call_count == 3

    def test_raises_after_max_attempts(self) -> None:
        @retry(max_attempts=2, base_delay=0.01)
        def always_fails():
            msg = "always"
            raise RuntimeError(msg)

        with pytest.raises(RuntimeError, match="always"):
            always_fails()

    def test_retryable_exceptions(self) -> None:
        @retry(max_attempts=3, base_delay=0.01, retryable_exceptions=(ValueError,))
        def type_error():
            msg = "not retryable"
            raise TypeError(msg)

        with pytest.raises(TypeError):
            type_error()

    def test_on_retry_callback(self) -> None:
        callbacks: list[int] = []

        def on_retry(attempt: int, exc: Exception, delay: float) -> None:
            callbacks.append(attempt)

        call_count = 0

        @retry(max_attempts=3, base_delay=0.01, on_retry=on_retry)
        def fails_once():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                msg = "first"
                raise ValueError(msg)
            return "ok"

        assert fails_once() == "ok"
        assert callbacks == [1]

    def test_retry_config_attribute(self) -> None:
        @retry(max_attempts=5, base_delay=2.0)
        def func():
            return None

        assert func._retry_config["max_attempts"] == 5
        assert func._retry_config["base_delay"] == 2.0

    def test_retry_with_stats(self) -> None:
        call_count = 0

        @retry_with_stats(max_attempts=3, base_delay=0.01)
        def flaky():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                msg = "flaky"
                raise ValueError(msg)
            return 99

        result, stats = flaky()
        assert result == 99
        assert stats.attempts == 2
        assert stats.succeeded
