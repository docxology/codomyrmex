"""Tests for Sprint 20 (Observability) and Sprint 21 (Code Generation)."""

from __future__ import annotations

from codomyrmex.agents.specialized.review_loop import ReviewLoop
from codomyrmex.coding.generator import CodeBundle, CodeGenerator
from codomyrmex.coding.test_generator import TestGenerator
from codomyrmex.data_visualization.dashboard_export import (
    DashboardExporter,
    Panel,
)
from codomyrmex.git_operations.pr_builder import FileChange, PRBuilder
from codomyrmex.security.audit.audit_trail import AuditTrail
from codomyrmex.telemetry.alerting.alerts import (
    Alert,
    AlertEngine,
    AlertRule,
    AlertSeverity,
)
from codomyrmex.telemetry.otel import MetricCounter, Span, Tracer

# ── Tracer / MetricCounter ───────────────────────────────────────


class TestTracer:
    """Test suite for Tracer."""
    def test_start_span(self) -> None:
        """Test functionality: start span."""
        t = Tracer()
        s = t.start_span("op")
        assert s.trace_id
        assert t.span_count == 1

    def test_parent_span(self) -> None:
        """Test functionality: parent span."""
        t = Tracer()
        parent = t.start_span("parent")
        child = t.start_span("child", parent=parent)
        assert child.parent_id == parent.span_id
        assert child.trace_id == parent.trace_id

    def test_finish(self) -> None:
        """Test functionality: finish."""
        s = Span("test")
        s.finish("ok")
        assert s.duration_ms >= 0

    def test_export(self) -> None:
        """Test functionality: export."""
        t = Tracer()
        t.start_span("a")
        t.start_span("b")
        data = t.export()
        assert len(data) == 2


class TestMetricCounter:
    """Test suite for MetricCounter."""
    def test_increment(self) -> None:
        """Test functionality: increment."""
        m = MetricCounter()
        m.increment("req")
        m.increment("req")
        assert m.get_counter("req") == 2.0

    def test_gauge(self) -> None:
        """Test functionality: gauge."""
        m = MetricCounter()
        m.gauge("conns", 42)
        assert m.get_gauge("conns") == 42


# ── AlertEngine ──────────────────────────────────────────────────


class TestAlertEngine:
    """Test suite for AlertEngine."""
    def test_fire_alert(self) -> None:
        """Test functionality: fire alert."""
        eng = AlertEngine()
        eng.add_rule(AlertRule("high_err", "error_rate", "gt", 0.05))
        alerts = eng.evaluate({"error_rate": 0.08})
        assert len(alerts) == 1
        assert alerts[0].severity == AlertSeverity.WARNING

    def test_no_fire(self) -> None:
        """Test functionality: no fire."""
        eng = AlertEngine()
        eng.add_rule(AlertRule("high_err", "error_rate", "gt", 0.05))
        alerts = eng.evaluate({"error_rate": 0.01})
        assert len(alerts) == 0

    def test_handler_called(self) -> None:
        """Test functionality: handler called."""
        eng = AlertEngine()
        eng.add_rule(AlertRule("r", "m", "gt", 0))
        received: list[Alert] = []
        eng.on_alert(lambda a: received.append(a))
        eng.evaluate({"m": 1.0})
        assert len(received) == 1

    def test_rule_conditions(self) -> None:
        """Test functionality: rule conditions."""
        r_lt = AlertRule("lt", "x", "lt", 10)
        assert r_lt.evaluate(5)
        r_gte = AlertRule("gte", "x", "gte", 10)
        assert r_gte.evaluate(10)


# ── AuditTrail ───────────────────────────────────────────────────


class TestAuditTrail:
    """Test suite for AuditTrail."""
    def test_record(self) -> None:
        """Test functionality: record."""
        trail = AuditTrail()
        e = trail.record("deploy", actor="agent-1")
        assert e.entry_hash
        assert trail.size == 1

    def test_chain_integrity(self) -> None:
        """Test functionality: chain integrity."""
        trail = AuditTrail()
        trail.record("a")
        trail.record("b")
        trail.record("c")
        assert trail.verify_chain()

    def test_entries_by_actor(self) -> None:
        """Test functionality: entries by actor."""
        trail = AuditTrail()
        trail.record("x", actor="alice")
        trail.record("y", actor="bob")
        assert len(trail.entries_by_actor("alice")) == 1

    def test_jsonl(self) -> None:
        """Test functionality: jsonl."""
        trail = AuditTrail()
        trail.record("a")
        jsonl = trail.to_jsonl()
        assert "a" in jsonl


# ── DashboardExporter ────────────────────────────────────────────


class TestDashboardExporter:
    """Test suite for DashboardExporter."""
    def test_add_panel(self) -> None:
        """Test functionality: add panel."""
        exp = DashboardExporter()
        exp.add_panel(Panel("Rate", "graph", "req_rate"))
        assert exp.panel_count == 1

    def test_export(self) -> None:
        """Test functionality: export."""
        exp = DashboardExporter()
        exp.add_panel(Panel("P1"))
        data = exp.export()
        assert "dashboard" in data
        assert len(data["dashboard"]["panels"]) == 1

    def test_agent_dashboard(self) -> None:
        """Test functionality: agent dashboard."""
        exp = DashboardExporter.agent_dashboard()
        assert exp.panel_count == 4


# ── CodeGenerator ────────────────────────────────────────────────


class TestCodeGenerator:
    """Test suite for CodeGenerator."""
    def test_generate_functions(self) -> None:
        """Test functionality: generate functions."""
        gen = CodeGenerator()
        bundle = gen.generate("Create a calculator with add and multiply")
        assert len(bundle.functions) >= 2
        assert bundle.line_count > 5

    def test_generate_class(self) -> None:
        """Test functionality: generate class."""
        gen = CodeGenerator()
        bundle = gen.generate("Build a class with save and load")
        assert len(bundle.classes) >= 1

    def test_empty_spec(self) -> None:
        """Test functionality: empty spec."""
        gen = CodeGenerator()
        bundle = gen.generate("do something")
        assert "main" in bundle.functions

    def test_bundle_to_dict(self) -> None:
        """Test functionality: bundle to dict."""
        b = CodeBundle(filename="x.py", functions=["a"])
        d = b.to_dict()
        assert d["filename"] == "x.py"


# ── TestGenerator ────────────────────────────────────────────────


class TestTestGenerator:
    """Test suite for Generator."""
    def test_from_source(self) -> None:
        """Test functionality: from source."""
        gen = TestGenerator()
        suite = gen.from_source("def greet(name): return f'Hello {name}'")
        assert suite.test_count >= 1

    def test_class_tests(self) -> None:
        """Test functionality: class tests."""
        gen = TestGenerator()
        source = "class Foo:\n    def bar(self): pass\n    def baz(self): pass"
        suite = gen.from_source(source)
        assert suite.test_count >= 3  # instantiation + 2 methods

    def test_render(self) -> None:
        """Test functionality: render."""
        gen = TestGenerator()
        suite = gen.from_source("def hello(): pass")
        rendered = suite.render()
        assert "def test_hello" in rendered


# ── PRBuilder ────────────────────────────────────────────────────


class TestPRBuilder:
    """Test suite for PRBuilder."""
    def test_create(self) -> None:
        """Test functionality: create."""
        builder = PRBuilder()
        pr = builder.create([FileChange("a.py", "code")])
        assert pr.branch.startswith("auto/")
        assert pr.file_count == 1

    def test_auto_title(self) -> None:
        """Test functionality: auto title."""
        builder = PRBuilder()
        pr = builder.create([FileChange("new.py", "x", "add")])
        assert "new.py" in pr.title


# ── ReviewLoop ───────────────────────────────────────────────────


class TestReviewLoop:
    """Test suite for ReviewLoop."""
    def test_converges(self) -> None:
        """Test functionality: converges."""
        loop = ReviewLoop(max_iterations=5, approval_threshold=0.7)
        result = loop.run("Create a module with add and subtract")
        assert result.converged
        assert result.final_code is not None

    def test_has_reviews(self) -> None:
        """Test functionality: has reviews."""
        loop = ReviewLoop(max_iterations=3)
        result = loop.run("Build something")
        assert len(result.reviews) >= 1

    def test_result_to_dict(self) -> None:
        """Test functionality: result to dict."""
        loop = ReviewLoop()
        result = loop.run("Create a tool with process")
        d = result.to_dict()
        assert "converged" in d
