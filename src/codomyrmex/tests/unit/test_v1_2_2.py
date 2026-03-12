"""Tests for v1.2.2 — Codebase Health, API Freeze, Config, Events, Profiling.

Zero-Mock: All tests use real implementations.
"""

from __future__ import annotations

import pytest

# ── Health Reporter ───────────────────────────────────────────────
from codomyrmex.system_discovery.health_reporter import (
    HealthMetrics,
    HealthReporter,
)


class TestHealthReporter:
    """Verify codebase health reporting."""

    def test_generate_report(self) -> None:
        reporter = HealthReporter()
        report = reporter.generate()
        assert report["health_score"] >= 0
        assert report["metrics"]["total_modules"] >= 100

    def test_has_recommendations(self) -> None:
        reporter = HealthReporter()
        report = reporter.generate()
        assert isinstance(report["recommendations"], list)

    def test_health_score_range(self) -> None:
        metrics = HealthMetrics(total_modules=100, healthy_count=80, partial_count=20)
        assert 0 <= metrics.health_score <= 100

    def test_health_score_penalties(self) -> None:
        metrics = HealthMetrics(
            total_modules=10,
            healthy_count=5,
            partial_count=5,
            cycle_count=5,
            modules_without_tests=50,
        )
        assert metrics.health_score < 70  # Penalized

    def test_write_markdown(self, tmp_path) -> None:
        reporter = HealthReporter()
        report = reporter.generate()
        out = reporter.write_markdown(report, str(tmp_path / "health.md"))
        assert out.exists()
        content = out.read_text()
        assert "Health Report" in content

    def test_write_json(self, tmp_path) -> None:
        reporter = HealthReporter()
        report = reporter.generate()
        out = reporter.write_json(report, str(tmp_path / "health.json"))
        assert out.exists()

    def test_largest_modules(self) -> None:
        reporter = HealthReporter()
        report = reporter.generate()
        assert len(report["largest_modules"]) == 10


# ── API Spec Stamper ──────────────────────────────────────────────

from codomyrmex.api.api_spec_stamper import (
    APISpecStamper,
    ModuleAPI,
)


class TestAPISpecStamper:
    """Verify API specification snapshotting."""

    def test_snapshot(self) -> None:
        stamper = APISpecStamper()
        spec = stamper.snapshot(version="v1.2.2")
        assert spec["version"] == "v1.2.2"
        assert spec["total_modules"] >= 100

    def test_surface_counted(self) -> None:
        stamper = APISpecStamper()
        spec = stamper.snapshot()
        assert spec["total_surface"] > 0

    def test_diff_no_changes(self) -> None:
        stamper = APISpecStamper()
        spec = stamper.snapshot()
        diff = stamper.diff(spec, spec)
        assert not diff["is_breaking"]
        assert len(diff["added_modules"]) == 0

    def test_diff_detects_removal(self) -> None:
        stamper = APISpecStamper()
        old = {"modules": [{"name": "foo", "exports": ["bar"]}]}
        new = {"modules": [{"name": "foo", "exports": []}]}
        diff = stamper.diff(old, new)
        assert diff["is_breaking"]

    def test_write_spec(self, tmp_path) -> None:
        stamper = APISpecStamper()
        spec = stamper.snapshot(version="v1.2.2")
        out = stamper.write_spec(spec, str(tmp_path / "API.md"))
        assert out.exists()
        assert "API Specification" in out.read_text()

    def test_module_api_surface(self) -> None:
        api = ModuleAPI(name="test", exports=["a", "b", "c"])
        assert api.surface_size == 3

    def test_module_api_fallback(self) -> None:
        api = ModuleAPI(name="test", classes=["Foo"], functions=["bar"])
        assert api.surface_size == 2  # No exports, falls back


# ── Config Validator ──────────────────────────────────────────────

from codomyrmex.config_management.config_validator import (
    ConfigSchema,
    SchemaField,
    ValidationResult,
)


class TestConfigValidator:
    """Verify config schema validation."""

    def test_valid_config(self) -> None:
        schema = ConfigSchema({
            "port": SchemaField(type=int, required=True, min_val=1, max_val=65535),
            "host": SchemaField(type=str, default="0.0.0.0"),
        })
        result = schema.validate({"port": 8080})
        assert result.valid
        assert result.config["host"] == "0.0.0.0"

    def test_missing_required(self) -> None:
        schema = ConfigSchema({"port": SchemaField(type=int, required=True)})
        result = schema.validate({})
        assert not result.valid
        assert any("Missing required" in e for e in result.errors)

    def test_type_mismatch(self) -> None:
        schema = ConfigSchema({"port": SchemaField(type=int)})
        result = schema.validate({"port": "not_a_number"})
        assert not result.valid

    def test_min_max(self) -> None:
        schema = ConfigSchema({"port": SchemaField(type=int, min_val=1, max_val=100)})
        assert not schema.validate({"port": 0}).valid
        assert not schema.validate({"port": 101}).valid
        assert schema.validate({"port": 50}).valid

    def test_choices(self) -> None:
        schema = ConfigSchema({"env": SchemaField(type=str, choices=["dev", "prod"])})
        assert schema.validate({"env": "dev"}).valid
        assert not schema.validate({"env": "staging"}).valid

    def test_unknown_field_warning(self) -> None:
        schema = ConfigSchema({"port": SchemaField(type=int)})
        result = schema.validate({"port": 80, "extra": "value"})
        assert result.valid
        assert any("Unknown" in w for w in result.warnings)

    def test_defaults(self) -> None:
        schema = ConfigSchema({
            "a": SchemaField(type=int, default=42),
            "b": SchemaField(type=str, default="hello"),
        })
        assert schema.get_defaults() == {"a": 42, "b": "hello"}

    def test_describe(self) -> None:
        schema = ConfigSchema({"port": SchemaField(type=int, description="Listen port")})
        desc = schema.describe()
        assert desc[0]["name"] == "port"
        assert desc[0]["description"] == "Listen port"


# ── Typed Event Bus ───────────────────────────────────────────────

from codomyrmex.events.typed_event_bus import (
    Event,
    Subscription,
    TypedEventBus,
)


class TestTypedEventBus:
    """Verify typed event bus."""

    def test_emit_and_receive(self) -> None:
        bus = TypedEventBus()
        received: list[Event] = []
        bus.subscribe("test.ping", received.append)
        bus.emit(Event(type="test.ping", data={"ok": True}))
        assert len(received) == 1
        assert received[0].data["ok"]

    def test_wildcard(self) -> None:
        bus = TypedEventBus()
        received: list[Event] = []
        bus.subscribe("test.*", received.append)
        bus.emit(Event(type="test.a"))
        bus.emit(Event(type="test.b"))
        bus.emit(Event(type="other.c"))
        assert len(received) == 2

    def test_global_wildcard(self) -> None:
        bus = TypedEventBus()
        received: list[Event] = []
        bus.subscribe("*", received.append)
        bus.emit(Event(type="anything"))
        assert len(received) == 1

    def test_unsubscribe(self) -> None:
        bus = TypedEventBus()
        received: list[Event] = []
        sub_id = bus.subscribe("test", received.append)
        bus.unsubscribe(sub_id)
        bus.emit(Event(type="test"))
        assert len(received) == 0

    def test_priority(self) -> None:
        bus = TypedEventBus()
        order: list[int] = []
        bus.subscribe("test", lambda e: order.append(1), priority=1)
        bus.subscribe("test", lambda e: order.append(2), priority=10)
        bus.emit(Event(type="test"))
        assert order == [2, 1]  # Higher priority first

    def test_history(self) -> None:
        bus = TypedEventBus()
        bus.emit(Event(type="a"))
        bus.emit(Event(type="b"))
        history = bus.get_history()
        assert len(history) == 2

    def test_stats(self) -> None:
        bus = TypedEventBus()
        bus.subscribe("x", lambda e: None)
        bus.emit(Event(type="x"))
        assert bus.stats["subscriptions"] == 1
        assert bus.stats["total_emitted"] == 1

    def test_subscription_matching(self) -> None:
        sub = Subscription(pattern="module.*", callback=lambda e: None)
        assert sub.matches("module.loaded")
        assert not sub.matches("other.loaded")


# ── CLI Profiler ──────────────────────────────────────────────────

from codomyrmex.performance.cli_profiler import (
    CLIProfiler,
    ProfileResult,
)


class TestCLIProfiler:
    """Verify performance profiling."""

    def test_profile_import(self) -> None:
        profiler = CLIProfiler()
        result = profiler.profile_import("json")
        assert result.success
        assert result.duration_ms >= 0

    def test_profile_import_failure(self) -> None:
        profiler = CLIProfiler()
        result = profiler.profile_import("nonexistent_xyz_module")
        assert not result.success

    def test_profile_function(self) -> None:
        profiler = CLIProfiler()
        result = profiler.profile_function(lambda: sum(range(1000)), iterations=3)
        assert result.duration_ms >= 0
        assert result.details["iterations"] == 3

    def test_benchmark_startup(self) -> None:
        profiler = CLIProfiler()
        result = profiler.benchmark_startup()
        assert result.success
        assert result.duration_ms > 0

    def test_profile_result_dataclass(self) -> None:
        result = ProfileResult(name="test", duration_ms=42.5, success=True)
        assert result.name == "test"
        assert result.duration_ms == 42.5
