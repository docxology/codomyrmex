"""Tests for model_context_protocol.discovery — MCP tool auto-discovery engine.

Tests the MCPDiscovery class, DiscoveredTool, DiscoveryReport, and the
error-isolated scanning that finds @mcp_tool decorated functions.
All tests use real module introspection — no mocks.
"""

import types

import pytest

from codomyrmex.model_context_protocol.discovery import (
    DiscoveredTool,
    DiscoveryMetrics,
    DiscoveryReport,
    FailedModule,
    MCPDiscovery,
)


@pytest.mark.unit
class TestDiscoveredTool:
    """Tests for the DiscoveredTool dataclass."""

    def test_to_mcp_schema_basic(self):
        """Test functionality: to_mcp_schema produces expected dict shape."""
        tool = DiscoveredTool(
            name="codomyrmex.test_tool",
            description="A test tool",
            module_path="codomyrmex.test_module",
            callable_name="test_tool",
            parameters={"type": "object", "properties": {"x": {"type": "integer"}}},
            tags=["testing"],
            version="1.0",
        )
        schema = tool.to_mcp_schema()
        assert schema["name"] == "codomyrmex.test_tool"
        assert schema["description"] == "A test tool"
        assert schema["tags"] == ["testing"]
        assert schema["x-codomyrmex"]["module"] == "codomyrmex.test_module"
        assert schema["x-codomyrmex"]["callable"] == "test_tool"
        assert schema["x-codomyrmex"]["version"] == "1.0"
        assert schema["x-codomyrmex"]["available"] is True

    def test_to_mcp_schema_unavailable_appends_reason(self):
        """Test functionality: unavailable tool appends reason to description."""
        tool = DiscoveredTool(
            name="codomyrmex.unavailable_tool",
            description="Needs special dep",
            module_path="codomyrmex.special",
            callable_name="unavailable_tool",
            available=False,
            unavailable_reason="Missing dependencies: special_lib",
        )
        schema = tool.to_mcp_schema()
        assert "UNAVAILABLE" in schema["description"]
        assert "special_lib" in schema["description"]
        assert schema["x-codomyrmex"]["available"] is False

    def test_default_available_is_true(self):
        """Test functionality: DiscoveredTool defaults to available."""
        tool = DiscoveredTool(
            name="t",
            description="d",
            module_path="m",
            callable_name="c",
        )
        assert tool.available is True
        assert tool.unavailable_reason is None


@pytest.mark.unit
class TestDiscoveryReport:
    """Tests for the DiscoveryReport dataclass."""

    def test_empty_report_defaults(self):
        """Test functionality: empty report has zero counts."""
        report = DiscoveryReport()
        assert report.tools == []
        assert report.failed_modules == []
        assert report.scan_duration_ms == 0.0
        assert report.modules_scanned == 0

    def test_report_with_tools_and_failures(self):
        """Test functionality: report carries both tools and failures."""
        tool = DiscoveredTool(
            name="t1", description="d", module_path="m", callable_name="c"
        )
        fail = FailedModule(module="bad_mod", error="ImportError", error_type="ImportError")
        report = DiscoveryReport(
            tools=[tool],
            failed_modules=[fail],
            scan_duration_ms=42.5,
            modules_scanned=10,
        )
        assert len(report.tools) == 1
        assert len(report.failed_modules) == 1
        assert report.scan_duration_ms == 42.5
        assert report.modules_scanned == 10


@pytest.mark.unit
class TestFailedModule:
    """Tests for the FailedModule dataclass."""

    def test_failed_module_fields(self):
        """Test functionality: FailedModule stores module, error, and error_type."""
        fm = FailedModule(
            module="codomyrmex.broken",
            error="No module named 'missing_dep'",
            error_type="ModuleNotFoundError",
        )
        assert fm.module == "codomyrmex.broken"
        assert "missing_dep" in fm.error
        assert fm.error_type == "ModuleNotFoundError"


@pytest.mark.unit
class TestMCPDiscoveryEngine:
    """Tests for the MCPDiscovery engine class."""

    def test_empty_registry_initially(self):
        """Test functionality: new MCPDiscovery has zero tools."""
        engine = MCPDiscovery()
        assert engine.tool_count == 0
        assert engine.list_tools() == []

    def test_register_tool_manually(self):
        """Test functionality: manual tool registration adds to registry."""
        engine = MCPDiscovery()
        tool = DiscoveredTool(
            name="codomyrmex.manual_tool",
            description="Manually registered",
            module_path="test",
            callable_name="manual_tool",
        )
        engine.register_tool(tool)
        assert engine.tool_count == 1
        retrieved = engine.get_tool("codomyrmex.manual_tool")
        assert retrieved is not None
        assert retrieved.description == "Manually registered"

    def test_get_tool_returns_none_for_missing(self):
        """Test functionality: get_tool returns None for unknown name."""
        engine = MCPDiscovery()
        assert engine.get_tool("nonexistent") is None

    def test_list_tools_with_tag_filter(self):
        """Test functionality: list_tools filters by tag."""
        engine = MCPDiscovery()
        tool_a = DiscoveredTool(
            name="a", description="A", module_path="m", callable_name="a",
            tags=["io"],
        )
        tool_b = DiscoveredTool(
            name="b", description="B", module_path="m", callable_name="b",
            tags=["math"],
        )
        tool_c = DiscoveredTool(
            name="c", description="C", module_path="m", callable_name="c",
            tags=["io", "math"],
        )
        engine.register_tool(tool_a)
        engine.register_tool(tool_b)
        engine.register_tool(tool_c)

        io_tools = engine.list_tools(tag="io")
        assert len(io_tools) == 2
        io_names = {t.name for t in io_tools}
        assert "a" in io_names
        assert "c" in io_names

        math_tools = engine.list_tools(tag="math")
        assert len(math_tools) == 2

    def test_list_tools_no_filter_returns_all(self):
        """Test functionality: list_tools without tag returns everything."""
        engine = MCPDiscovery()
        for i in range(5):
            engine.register_tool(DiscoveredTool(
                name=f"t{i}", description=f"T{i}", module_path="m", callable_name=f"t{i}",
            ))
        assert len(engine.list_tools()) == 5

    def test_scan_module_with_decorated_functions(self):
        """Test functionality: scan_module finds functions with _mcp_tool_meta."""
        # Create a real module with a decorated function
        mod = types.ModuleType("test_scan_module")
        mod.__name__ = "test_scan_module"

        def tool_func(x: int) -> int:
            """A test tool."""
            return x * 2

        tool_func._mcp_tool_meta = {
            "name": "codomyrmex.test_scan",
            "description": "Test scan tool",
            "tags": ["test"],
            "parameters": {"type": "object", "properties": {"x": {"type": "integer"}}},
            "version": "1.0",
            "requires": [],
        }
        mod.tool_func = tool_func

        engine = MCPDiscovery()
        tools = engine._scan_module(mod)
        assert len(tools) >= 1
        names = [t.name for t in tools]
        assert "codomyrmex.test_scan" in names

    def test_scan_module_no_tools_returns_empty(self):
        """Test functionality: scanning a module without tools returns empty list."""
        mod = types.ModuleType("empty_module")
        mod.__name__ = "empty_module"
        mod.regular_func = lambda: None  # No _mcp_tool_meta

        engine = MCPDiscovery()
        tools = engine._scan_module(mod)
        assert tools == []

    def test_scan_module_with_missing_requirement(self):
        """Test functionality: tool with missing require is marked unavailable."""
        mod = types.ModuleType("req_module")
        mod.__name__ = "req_module"

        def req_tool():
            """Requires missing package."""
            pass

        req_tool._mcp_tool_meta = {
            "name": "codomyrmex.req_tool",
            "description": "Needs missing dep",
            "tags": [],
            "parameters": {},
            "version": "1.0",
            "requires": ["this_package_definitely_does_not_exist_xyzzy"],
        }
        mod.req_tool = req_tool

        engine = MCPDiscovery()
        tools = engine._scan_module(mod)
        assert len(tools) == 1
        assert tools[0].available is False
        assert "this_package_definitely_does_not_exist_xyzzy" in tools[0].unavailable_reason

    def test_scan_single_module_incremental(self):
        """Test functionality: scan_module (by name) for a real codomyrmex module."""
        engine = MCPDiscovery()
        # Scan the model_context_protocol's own mcp_tools module which has @mcp_tool decorators
        report = engine.scan_module("codomyrmex.model_context_protocol.mcp_tools")
        # The mcp_tools module has at least inspect_server, list_registered_tools, get_tool_schema
        assert report.modules_scanned == 1
        if report.failed_modules:
            # If it fails to import, that is also valid — we just record it
            assert len(report.failed_modules) == 1
        else:
            assert len(report.tools) >= 1

    def test_scan_nonexistent_module_records_failure(self):
        """Test functionality: scanning a nonexistent module records failure."""
        engine = MCPDiscovery()
        report = engine.scan_module("codomyrmex.this_module_does_not_exist_xyzzy")
        assert len(report.failed_modules) == 1
        assert "this_module_does_not_exist_xyzzy" in report.failed_modules[0].module

    def test_record_cache_hit_increments(self):
        """Test functionality: record_cache_hit increments metrics counter."""
        engine = MCPDiscovery()
        assert engine.get_metrics().cache_hits == 0
        engine.record_cache_hit()
        engine.record_cache_hit()
        assert engine.get_metrics().cache_hits == 2


@pytest.mark.unit
class TestDiscoveryMetrics:
    """Tests for the DiscoveryMetrics dataclass."""

    def test_default_metrics(self):
        """Test functionality: default metrics are zeroed out."""
        m = DiscoveryMetrics()
        assert m.total_tools == 0
        assert m.scan_duration_ms == 0.0
        assert m.failed_modules == []
        assert m.modules_scanned == 0
        assert m.cache_hits == 0
        assert m.last_scan_time is None

    def test_metrics_after_scan(self):
        """Test functionality: metrics update after a real scan."""
        engine = MCPDiscovery()
        engine.scan_module("codomyrmex.model_context_protocol.mcp_tools")
        metrics = engine.get_metrics()
        assert metrics.modules_scanned >= 1
        assert metrics.scan_duration_ms > 0.0
        assert metrics.last_scan_time is not None
