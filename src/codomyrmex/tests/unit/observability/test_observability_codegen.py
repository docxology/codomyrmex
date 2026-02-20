"""Tests for Sprint 20 (Observability) and Sprint 21 (Code Generation)."""

from __future__ import annotations

import pytest

from codomyrmex.telemetry.otel import MetricCounter, Span, Tracer
from codomyrmex.telemetry.alerts import (
    Alert, AlertEngine, AlertRule, AlertSeverity, AlertState,
)
from codomyrmex.security.audit_trail import AuditEntry, AuditTrail
from codomyrmex.data_visualization.dashboard_export import (
    Dashboard, DashboardExporter, Panel,
)
from codomyrmex.coding.generator import CodeBundle, CodeGenerator
from codomyrmex.coding.test_generator import TestGenerator, TestSuite
from codomyrmex.git_operations.pr_builder import FileChange, PRBuilder, PRSpec
from codomyrmex.agents.specialized.review_loop import ReviewLoop, ReviewResult


# ── Tracer / MetricCounter ───────────────────────────────────────


class TestTracer:
    def test_start_span(self) -> None:
        t = Tracer()
        s = t.start_span("op")
        assert s.trace_id
        assert t.span_count == 1

    def test_parent_span(self) -> None:
        t = Tracer()
        parent = t.start_span("parent")
        child = t.start_span("child", parent=parent)
        assert child.parent_id == parent.span_id
        assert child.trace_id == parent.trace_id

    def test_finish(self) -> None:
        s = Span("test")
        s.finish("ok")
        assert s.duration_ms > 0

    def test_export(self) -> None:
        t = Tracer()
        t.start_span("a")
        t.start_span("b")
        data = t.export()
        assert len(data) == 2


class TestMetricCounter:
    def test_increment(self) -> None:
        m = MetricCounter()
        m.increment("req")
        m.increment("req")
        assert m.get_counter("req") == 2.0

    def test_gauge(self) -> None:
        m = MetricCounter()
        m.gauge("conns", 42)
        assert m.get_gauge("conns") == 42


# ── AlertEngine ──────────────────────────────────────────────────


class TestAlertEngine:
    def test_fire_alert(self) -> None:
        eng = AlertEngine()
        eng.add_rule(AlertRule("high_err", "error_rate", "gt", 0.05))
        alerts = eng.evaluate({"error_rate": 0.08})
        assert len(alerts) == 1
        assert alerts[0].severity == AlertSeverity.WARNING

    def test_no_fire(self) -> None:
        eng = AlertEngine()
        eng.add_rule(AlertRule("high_err", "error_rate", "gt", 0.05))
        alerts = eng.evaluate({"error_rate": 0.01})
        assert len(alerts) == 0

    def test_handler_called(self) -> None:
        eng = AlertEngine()
        eng.add_rule(AlertRule("r", "m", "gt", 0))
        received: list[Alert] = []
        eng.on_alert(lambda a: received.append(a))
        eng.evaluate({"m": 1.0})
        assert len(received) == 1

    def test_rule_conditions(self) -> None:
        r_lt = AlertRule("lt", "x", "lt", 10)
        assert r_lt.evaluate(5)
        r_gte = AlertRule("gte", "x", "gte", 10)
        assert r_gte.evaluate(10)


# ── AuditTrail ───────────────────────────────────────────────────


class TestAuditTrail:
    def test_record(self) -> None:
        trail = AuditTrail()
        e = trail.record("deploy", actor="agent-1")
        assert e.entry_hash
        assert trail.size == 1

    def test_chain_integrity(self) -> None:
        trail = AuditTrail()
        trail.record("a")
        trail.record("b")
        trail.record("c")
        assert trail.verify_chain()

    def test_entries_by_actor(self) -> None:
        trail = AuditTrail()
        trail.record("x", actor="alice")
        trail.record("y", actor="bob")
        assert len(trail.entries_by_actor("alice")) == 1

    def test_jsonl(self) -> None:
        trail = AuditTrail()
        trail.record("a")
        jsonl = trail.to_jsonl()
        assert "a" in jsonl


# ── DashboardExporter ────────────────────────────────────────────


class TestDashboardExporter:
    def test_add_panel(self) -> None:
        exp = DashboardExporter()
        exp.add_panel(Panel("Rate", "graph", "req_rate"))
        assert exp.panel_count == 1

    def test_export(self) -> None:
        exp = DashboardExporter()
        exp.add_panel(Panel("P1"))
        data = exp.export()
        assert "dashboard" in data
        assert len(data["dashboard"]["panels"]) == 1

    def test_agent_dashboard(self) -> None:
        exp = DashboardExporter.agent_dashboard()
        assert exp.panel_count == 4


# ── CodeGenerator ────────────────────────────────────────────────


class TestCodeGenerator:
    def test_generate_functions(self) -> None:
        gen = CodeGenerator()
        bundle = gen.generate("Create a calculator with add and multiply")
        assert len(bundle.functions) >= 2
        assert bundle.line_count > 5

    def test_generate_class(self) -> None:
        gen = CodeGenerator()
        bundle = gen.generate("Build a class with save and load")
        assert len(bundle.classes) >= 1

    def test_empty_spec(self) -> None:
        gen = CodeGenerator()
        bundle = gen.generate("do something")
        assert "main" in bundle.functions

    def test_bundle_to_dict(self) -> None:
        b = CodeBundle(filename="x.py", functions=["a"])
        d = b.to_dict()
        assert d["filename"] == "x.py"


# ── TestGenerator ────────────────────────────────────────────────


class TestTestGenerator:
    def test_from_source(self) -> None:
        gen = TestGenerator()
        suite = gen.from_source("def greet(name): return f'Hello {name}'")
        assert suite.test_count >= 1

    def test_class_tests(self) -> None:
        gen = TestGenerator()
        source = "class Foo:\n    def bar(self): pass\n    def baz(self): pass"
        suite = gen.from_source(source)
        assert suite.test_count >= 3  # instantiation + 2 methods

    def test_render(self) -> None:
        gen = TestGenerator()
        suite = gen.from_source("def hello(): pass")
        rendered = suite.render()
        assert "def test_hello" in rendered


# ── PRBuilder ────────────────────────────────────────────────────


class TestPRBuilder:
    def test_create(self) -> None:
        builder = PRBuilder()
        pr = builder.create([FileChange("a.py", "code")])
        assert pr.branch.startswith("auto/")
        assert pr.file_count == 1

    def test_auto_title(self) -> None:
        builder = PRBuilder()
        pr = builder.create([FileChange("new.py", "x", "add")])
        assert "new.py" in pr.title


# ── ReviewLoop ───────────────────────────────────────────────────


class TestReviewLoop:
    def test_converges(self) -> None:
        loop = ReviewLoop(max_iterations=5, approval_threshold=0.7)
        result = loop.run("Create a module with add and subtract")
        assert result.converged
        assert result.final_code is not None

    def test_has_reviews(self) -> None:
        loop = ReviewLoop(max_iterations=3)
        result = loop.run("Build something")
        assert len(result.reviews) >= 1

    def test_result_to_dict(self) -> None:
        loop = ReviewLoop()
        result = loop.run("Create a tool with process")
        d = result.to_dict()
        assert "converged" in d
