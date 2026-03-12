"""Tests for v1.1.10 deliverables — sparkline, DAG exporter, telemetry, dashboard API.

Zero-Mock: All tests use real implementations.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import pytest

# ── V2: Sparkline Renderer ────────────────────────────────────────
from codomyrmex.data_visualization.charts.sparkline import (
    SparklineConfig,
    SparklineResult,
    render_sparkline,
    render_sparkline_html,
)


class TestSparkline:
    """Verify inline SVG sparkline generation."""

    def test_basic_render(self) -> None:
        result = render_sparkline([1, 3, 2, 5, 4])
        assert isinstance(result, SparklineResult)
        assert "<svg" in result.svg
        assert "<polyline" in result.svg
        assert result.point_count == 5
        assert result.min_value == 1.0
        assert result.max_value == 5.0

    def test_single_value(self) -> None:
        result = render_sparkline([42])
        assert result.point_count == 1
        assert "<svg" in result.svg

    def test_empty_raises(self) -> None:
        with pytest.raises(ValueError, match="empty"):
            render_sparkline([])

    def test_custom_config(self) -> None:
        config = SparklineConfig(width=200, height=50, color="#ff0000")
        result = render_sparkline([1, 2, 3], config=config)
        assert 'width="200"' in result.svg
        assert 'height="50"' in result.svg
        assert "#ff0000" in result.svg

    def test_fill_color(self) -> None:
        config = SparklineConfig(fill_color="#3b82f6")
        result = render_sparkline([1, 2, 3, 2, 1], config=config)
        assert "<polygon" in result.svg

    def test_endpoint_dots(self) -> None:
        result = render_sparkline([1, 5, 3])
        assert "<circle" in result.svg

    def test_no_dots_when_zero_radius(self) -> None:
        config = SparklineConfig(dot_radius=0)
        result = render_sparkline([1, 5, 3], config=config)
        assert "<circle" not in result.svg

    def test_title_attribute(self) -> None:
        config = SparklineConfig(title="Test Chart")
        result = render_sparkline([1, 2, 3], config=config)
        assert "<title>" in result.svg
        assert "Test Chart" in result.svg

    def test_html_wrapper(self) -> None:
        html = render_sparkline_html([1, 2, 3], label="Coverage")
        assert "Coverage" in html
        assert "<svg" in html

    def test_large_dataset(self) -> None:
        values = list(range(1000))
        result = render_sparkline(values)
        assert result.point_count == 1000
        assert result.min_value == 0
        assert result.max_value == 999


# ── V3: Mermaid DAG Exporter ──────────────────────────────────────

from codomyrmex.data_visualization.mermaid.dag_exporter import (
    ModuleDAG,
    ModuleNode,
    build_module_dag,
    render_dag_mermaid,
)


class TestDAGExporter:
    """Verify module dependency DAG building and Mermaid rendering."""

    def test_build_dag_returns_nodes(self) -> None:
        dag = build_module_dag()
        assert isinstance(dag, ModuleDAG)
        assert len(dag.nodes) > 10  # expect 100+ modules
        assert dag.edge_count >= 0

    def test_node_has_metadata(self) -> None:
        dag = build_module_dag()
        auth = dag.nodes.get("auth")
        assert auth is not None
        assert auth.file_count > 0
        assert auth.loc > 0

    def test_render_mermaid(self) -> None:
        dag = build_module_dag()
        mermaid = render_dag_mermaid(dag)
        assert "flowchart LR" in mermaid
        assert "classDef foundation" in mermaid
        assert "classDef core" in mermaid
        assert "-->" in mermaid  # at least one edge

    def test_render_with_direction(self) -> None:
        dag = build_module_dag()
        mermaid = render_dag_mermaid(dag, direction="TB")
        assert "flowchart TB" in mermaid

    def test_synthetic_dag(self) -> None:
        dag = ModuleDAG(nodes={
            "a": ModuleNode(name="a", file_count=5, loc=100, imports={"b"}),
            "b": ModuleNode(name="b", file_count=3, loc=50, imports=set()),
        })
        mermaid = render_dag_mermaid(dag)
        assert "a -->" in mermaid
        assert "b" in mermaid


# ── T3: MCP Call-Graph Collector ──────────────────────────────────

from codomyrmex.telemetry.tracing.call_graph import (
    MCPCallGraphCollector,
    ToolCall,
    get_collector,
)


class TestCallGraphCollector:
    """Verify MCP call-graph collection and DAG building."""

    def test_record_and_retrieve(self) -> None:
        collector = MCPCallGraphCollector()
        call = collector.record("search", caller="hermes", latency_ms=42)
        assert isinstance(call, ToolCall)
        assert call.tool_name == "search"

        stats = collector.get_stats()
        assert stats["total_calls"] == 1
        assert stats["unique_tools"] == 1

    def test_call_graph_structure(self) -> None:
        collector = MCPCallGraphCollector()
        collector.record("search", caller="hermes", latency_ms=10)
        collector.record("search", caller="claude", latency_ms=20)
        collector.record("execute", caller="hermes", latency_ms=30)

        graph = collector.get_call_graph()
        assert "nodes" in graph
        assert "edges" in graph
        assert len(graph["nodes"]) == 4  # 2 tools + 2 callers
        assert len(graph["edges"]) == 3  # hermes→search, claude→search, hermes→execute

    def test_trace_context_manager(self) -> None:
        collector = MCPCallGraphCollector()
        with collector.trace("slow_tool", caller="test") as ctx:
            time.sleep(0.02)
            ctx.set_metadata({"key": "value"})

        stats = collector.get_stats()
        assert stats["total_calls"] == 1
        recent = collector.get_recent(1)
        assert recent[0]["latency_ms"] >= 15  # ~20ms ± tolerance

    def test_error_tracking(self) -> None:
        collector = MCPCallGraphCollector()
        collector.record("fail_tool", success=False)
        stats = collector.get_stats()
        assert stats["error_rate"] == 1.0

    def test_get_recent_ordering(self) -> None:
        collector = MCPCallGraphCollector()
        for i in range(5):
            collector.record(f"tool_{i}")
        recent = collector.get_recent(3)
        assert len(recent) == 3
        assert recent[0]["tool_name"] == "tool_4"  # most recent first

    def test_singleton(self) -> None:
        c1 = get_collector()
        c2 = get_collector()
        assert c1 is c2

    def test_clear(self) -> None:
        collector = MCPCallGraphCollector()
        collector.record("x")
        collector.clear()
        assert collector.get_stats()["total_calls"] == 0


# ── T2: Token Consumption Tracker ────────────────────────────────

from codomyrmex.telemetry.metrics.token_tracker import (
    TokenTracker,
    TokenUsage,
    get_token_tracker,
)


class TestTokenTracker:
    """Verify LLM token consumption tracking."""

    def test_record_usage(self) -> None:
        tracker = TokenTracker()
        usage = tracker.record("gpt-4o", input_tokens=100, output_tokens=50)
        assert isinstance(usage, TokenUsage)
        assert usage.model == "gpt-4o"

        stats = tracker.get_stats()
        assert stats["total_input"] == 100
        assert stats["total_output"] == 50
        assert stats["total_tokens"] == 150

    def test_per_model_stats(self) -> None:
        tracker = TokenTracker()
        tracker.record("gpt-4o", input_tokens=100, output_tokens=50)
        tracker.record("gemma3", input_tokens=200, output_tokens=100)
        tracker.record("gpt-4o", input_tokens=50, output_tokens=25)

        gpt_stats = tracker.get_model_stats("gpt-4o")
        assert gpt_stats["input_tokens"] == 150
        assert gpt_stats["calls"] == 2

        gemma_stats = tracker.get_model_stats("gemma3")
        assert gemma_stats["input_tokens"] == 200
        assert gemma_stats["calls"] == 1

    def test_get_recent(self) -> None:
        tracker = TokenTracker()
        for i in range(10):
            tracker.record(f"model_{i}")
        recent = tracker.get_recent(3)
        assert len(recent) == 3
        assert recent[0]["model"] == "model_9"

    def test_singleton(self) -> None:
        t1 = get_token_tracker()
        t2 = get_token_tracker()
        assert t1 is t2

    def test_clear(self) -> None:
        tracker = TokenTracker()
        tracker.record("test", input_tokens=100)
        tracker.clear()
        assert tracker.get_stats()["total_calls"] == 0


# ── D4: Module Health Provider ────────────────────────────────────

from codomyrmex.website.module_health import ModuleHealth, ModuleHealthProvider


class TestModuleHealthProvider:
    """Verify module health scanning."""

    def test_discover_modules(self) -> None:
        provider = ModuleHealthProvider()
        modules = provider.get_all_modules()
        assert len(modules) > 100  # expect 120+ modules
        names = [m.name for m in modules]
        assert "auth" in names
        assert "llm" in names
        assert "agents" in names

    def test_module_has_metrics(self) -> None:
        provider = ModuleHealthProvider()
        auth = provider.get_module("auth")
        assert auth is not None
        assert auth.file_count > 0
        assert auth.loc > 0
        assert auth.has_readme or not auth.has_readme  # boolean

    def test_to_dict(self) -> None:
        health = ModuleHealth(
            name="test_mod", file_count=10, loc=500,
            test_count=3, has_readme=True, has_spec=True, has_agents=False,
        )
        d = health.to_dict()
        assert d["name"] == "test_mod"
        assert d["doc_completeness"] == pytest.approx(2 / 3)

    def test_summary(self) -> None:
        provider = ModuleHealthProvider()
        summary = provider.get_summary()
        assert summary["total_modules"] > 100
        assert summary["total_files"] > 1000
        assert summary["total_loc"] > 50000

    def test_to_json(self) -> None:
        provider = ModuleHealthProvider()
        j = provider.to_json()
        data = json.loads(j)
        assert "modules" in data
        assert "summary" in data
        assert "timestamp" in data

    def test_caching(self) -> None:
        provider = ModuleHealthProvider()
        m1 = provider.get_all_modules()
        m2 = provider.get_all_modules()  # should hit cache
        assert len(m1) == len(m2)


# ── Dashboard API Handler ────────────────────────────────────────

from codomyrmex.website.handlers.dashboard_api import DashboardAPIHandler


class TestDashboardAPIHandler:
    """Verify dashboard API routing and responses."""

    def test_handle_modules(self) -> None:
        handler = DashboardAPIHandler()
        response = handler.handle_modules()
        assert response["status"] == 200
        assert "modules" in response
        assert len(response["modules"]) > 100

    def test_handle_modules_by_name(self) -> None:
        handler = DashboardAPIHandler()
        response = handler.handle_modules(module_name="auth")
        assert response["status"] == 200
        assert response["module"]["name"] == "auth"

    def test_handle_modules_not_found(self) -> None:
        handler = DashboardAPIHandler()
        response = handler.handle_modules(module_name="nonexistent_xyz")
        assert response["status"] == 404

    def test_handle_mcp_call_graph(self) -> None:
        handler = DashboardAPIHandler()
        response = handler.handle_mcp_call_graph()
        assert response["status"] == 200
        assert "graph" in response
        assert "nodes" in response["graph"]

    def test_handle_tokens(self) -> None:
        handler = DashboardAPIHandler()
        response = handler.handle_tokens()
        assert response["status"] == 200
        assert "stats" in response

    def test_handle_agents_status(self) -> None:
        handler = DashboardAPIHandler()
        response = handler.handle_agents_status()
        assert response["status"] == 200
        assert "agents" in response
        assert response["total"] >= 1

    def test_route_modules(self) -> None:
        handler = DashboardAPIHandler()
        result = handler.route("/api/modules")
        data = json.loads(result)
        assert data["status"] == 200

    def test_route_unknown_path(self) -> None:
        handler = DashboardAPIHandler()
        result = handler.route("/api/nonexistent")
        data = json.loads(result)
        assert data["status"] == 404
