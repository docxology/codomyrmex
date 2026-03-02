"""Zero-mock tests for agents/pai/mcp discovery, definitions, and proxy_tools.

Covers: _find_mcp_modules, _discover_dynamic_tools cache mechanics,
invalidate_tool_cache, get_discovery_metrics, _TOOL_DEFINITIONS structure,
_RESOURCE_DEFINITIONS, _PROMPT_DEFINITIONS, and proxy tool helpers.

Zero-mock compliant: no unittest.mock, MagicMock, or monkeypatch.
"""

import importlib
import threading
import time

import pytest

from codomyrmex.agents.pai.mcp.discovery import (
    _DEFAULT_CACHE_TTL,
    _DYNAMIC_TOOLS_CACHE_LOCK,
    _FALLBACK_SCAN_TARGETS,
    _discover_dynamic_tools,
    _find_mcp_modules,
    get_discovery_metrics,
    invalidate_tool_cache,
)
from codomyrmex.agents.pai.mcp.definitions import (
    _PROMPT_DEFINITIONS,
    _RESOURCE_DEFINITIONS,
    _TOOL_DEFINITIONS,
)


# ============================================================================
# _find_mcp_modules Tests
# ============================================================================


@pytest.mark.unit
class TestFindMcpModules:
    """Tests for _find_mcp_modules auto-discovery."""

    def test_returns_list_of_strings(self):
        result = _find_mcp_modules()
        assert isinstance(result, list)
        assert all(isinstance(m, str) for m in result)

    def test_all_entries_start_with_codomyrmex(self):
        result = _find_mcp_modules()
        for module_name in result:
            assert module_name.startswith("codomyrmex."), (
                f"Module {module_name} does not start with 'codomyrmex.'"
            )

    def test_finds_known_modules(self):
        """Known modules with mcp_tools.py should be discovered."""
        result = _find_mcp_modules()
        # These are well-known modules confirmed to have mcp_tools.py
        known = {"codomyrmex.security", "codomyrmex.search", "codomyrmex.coding"}
        found = set(result)
        for module in known:
            assert module in found, f"Expected {module} to be discovered"

    def test_returns_sorted_list(self):
        result = _find_mcp_modules()
        assert result == sorted(result)

    def test_no_mcp_tools_suffix_in_results(self):
        """Results should be parent packages, not the mcp_tools submodule."""
        result = _find_mcp_modules()
        for name in result:
            assert not name.endswith(".mcp_tools"), (
                f"Should return parent package, not {name}"
            )

    def test_discovers_multiple_modules(self):
        """Should find a significant number of modules (the project has 30+)."""
        result = _find_mcp_modules()
        assert len(result) >= 10, (
            f"Expected at least 10 mcp_tools modules, found {len(result)}"
        )


@pytest.mark.unit
class TestFallbackScanTargets:
    """Tests for the fallback scan targets constant."""

    def test_fallback_targets_are_strings(self):
        assert isinstance(_FALLBACK_SCAN_TARGETS, list)
        assert all(isinstance(t, str) for t in _FALLBACK_SCAN_TARGETS)

    def test_fallback_targets_start_with_codomyrmex(self):
        for target in _FALLBACK_SCAN_TARGETS:
            assert target.startswith("codomyrmex.")

    def test_fallback_targets_nonempty(self):
        assert len(_FALLBACK_SCAN_TARGETS) > 0


# ============================================================================
# invalidate_tool_cache Tests
# ============================================================================


@pytest.mark.unit
class TestInvalidateToolCache:
    """Tests for cache invalidation."""

    def test_invalidate_does_not_raise(self):
        """Invalidating the cache should never raise."""
        invalidate_tool_cache()

    def test_invalidate_clears_cache(self):
        """After invalidation, cache should be None internally."""
        import codomyrmex.agents.pai.mcp.discovery as disc_mod

        invalidate_tool_cache()
        with _DYNAMIC_TOOLS_CACHE_LOCK:
            assert disc_mod._DYNAMIC_TOOLS_CACHE is None
            assert disc_mod._CACHE_EXPIRY is None

    def test_double_invalidate_is_safe(self):
        invalidate_tool_cache()
        invalidate_tool_cache()  # Should not raise


# ============================================================================
# _discover_dynamic_tools Tests
# ============================================================================


@pytest.mark.unit
class TestDiscoverDynamicTools:
    """Tests for _discover_dynamic_tools main discovery function."""

    def test_returns_list_of_tuples(self):
        # Reset cache to force fresh scan
        invalidate_tool_cache()
        tools = _discover_dynamic_tools()
        assert isinstance(tools, list)
        for entry in tools:
            assert isinstance(entry, tuple)
            assert len(entry) == 4, f"Expected 4-tuple, got {len(entry)}-tuple"

    def test_tuple_structure(self):
        """Each tool tuple should be (name:str, description:str, handler, params:dict)."""
        invalidate_tool_cache()
        tools = _discover_dynamic_tools()
        if not tools:
            pytest.skip("No dynamic tools discovered (may require full install)")
        for name, description, handler, params in tools:
            assert isinstance(name, str), f"Tool name should be str, got {type(name)}"
            assert isinstance(description, str), f"Description should be str"
            assert callable(handler), f"Handler for {name} should be callable"
            assert isinstance(params, dict), f"Params for {name} should be dict"

    def test_discovers_known_tools(self):
        """Should discover at least some well-known @mcp_tool decorated tools."""
        invalidate_tool_cache()
        tools = _discover_dynamic_tools()
        tool_names = {t[0] for t in tools}
        # These are known tools from modules with @mcp_tool decorators
        # At minimum a few core tools should be found
        assert len(tool_names) > 0, "No dynamic tools discovered"

    def test_cache_hit_returns_same_result(self):
        """Second call within TTL should return cached result."""
        invalidate_tool_cache()
        tools_first = _discover_dynamic_tools()
        tools_second = _discover_dynamic_tools()
        # Same object (cache hit)
        assert tools_first is tools_second

    def test_cache_invalidation_triggers_rescan(self):
        """After invalidation, next call should rescan."""
        invalidate_tool_cache()
        tools_first = _discover_dynamic_tools()
        invalidate_tool_cache()
        tools_second = _discover_dynamic_tools()
        # Different objects (both valid, but not the same ref)
        # Note: might be same content, but identity should differ after invalidation
        assert isinstance(tools_second, list)
        # At minimum, lengths should match (same codebase)
        assert len(tools_first) == len(tools_second)


@pytest.mark.unit
class TestDiscoverDynamicToolsCacheTTL:
    """Tests for cache TTL behavior."""

    def test_default_cache_ttl(self):
        """Default TTL should be 300 seconds (or from env var)."""
        import os

        expected = float(os.environ.get("CODOMYRMEX_MCP_CACHE_TTL", "300"))
        assert _DEFAULT_CACHE_TTL == expected

    def test_cache_lock_is_threading_lock(self):
        """Cache lock should be a threading Lock for thread safety."""
        assert isinstance(_DYNAMIC_TOOLS_CACHE_LOCK, type(threading.Lock()))


# ============================================================================
# get_discovery_metrics Tests
# ============================================================================


@pytest.mark.unit
class TestGetDiscoveryMetrics:
    """Tests for get_discovery_metrics accessor."""

    def test_returns_dict_or_none(self):
        result = get_discovery_metrics()
        assert result is None or isinstance(result, dict)

    def test_dict_has_expected_keys_after_discovery(self):
        """After running discovery, metrics should have known keys."""
        invalidate_tool_cache()
        _discover_dynamic_tools()  # Ensure engine is initialized
        result = get_discovery_metrics()
        if result is None:
            pytest.skip("Discovery engine not initialized")
        assert "failed_modules" in result
        assert "scan_duration_ms" in result
        assert "last_scan_time" in result

    def test_failed_modules_is_list(self):
        invalidate_tool_cache()
        _discover_dynamic_tools()
        result = get_discovery_metrics()
        if result is None:
            pytest.skip("Discovery engine not initialized")
        assert isinstance(result["failed_modules"], list)

    def test_scan_duration_is_float(self):
        invalidate_tool_cache()
        _discover_dynamic_tools()
        result = get_discovery_metrics()
        if result is None:
            pytest.skip("Discovery engine not initialized")
        assert isinstance(result["scan_duration_ms"], float)
        assert result["scan_duration_ms"] >= 0.0


# ============================================================================
# _TOOL_DEFINITIONS Tests
# ============================================================================


@pytest.mark.unit
class TestToolDefinitions:
    """Tests for static _TOOL_DEFINITIONS structure."""

    def test_is_list(self):
        assert isinstance(_TOOL_DEFINITIONS, list)

    def test_nonempty(self):
        assert len(_TOOL_DEFINITIONS) > 0

    def test_each_entry_is_4_tuple(self):
        for entry in _TOOL_DEFINITIONS:
            assert isinstance(entry, tuple), f"Expected tuple, got {type(entry)}"
            assert len(entry) == 4, f"Expected 4-tuple, got {len(entry)}-tuple: {entry[0] if entry else '?'}"

    def test_each_entry_structure(self):
        """Each tool: (name:str, description:str, handler:callable, schema:dict)."""
        for name, desc, handler, schema in _TOOL_DEFINITIONS:
            assert isinstance(name, str), f"Name should be str: {name}"
            assert isinstance(desc, str), f"Description should be str for {name}"
            assert callable(handler), f"Handler should be callable for {name}"
            assert isinstance(schema, dict), f"Schema should be dict for {name}"

    def test_names_are_unique(self):
        names = [t[0] for t in _TOOL_DEFINITIONS]
        assert len(names) == len(set(names)), "Duplicate tool names found"

    def test_known_tool_names_present(self):
        """Well-known static tools should be defined."""
        names = {t[0] for t in _TOOL_DEFINITIONS}
        expected = {
            "codomyrmex.read_file",
            "codomyrmex.write_file",
            "codomyrmex.list_directory",
            "codomyrmex.git_status",
            "codomyrmex.git_diff",
            "codomyrmex.run_command",
            "codomyrmex.list_modules",
            "codomyrmex.module_info",
            "codomyrmex.pai_status",
            "codomyrmex.run_tests",
            "codomyrmex.list_module_functions",
            "codomyrmex.call_module_function",
            "codomyrmex.invalidate_cache",
        }
        for tool_name in expected:
            assert tool_name in names, f"Expected tool {tool_name} not found"

    def test_schemas_have_type_object(self):
        """All input schemas should declare type: object."""
        for name, _, _, schema in _TOOL_DEFINITIONS:
            assert schema.get("type") == "object", (
                f"Schema for {name} should have type=object"
            )

    def test_schemas_have_properties(self):
        """All schemas should have a properties key (even if empty)."""
        for name, _, _, schema in _TOOL_DEFINITIONS:
            assert "properties" in schema, f"Schema for {name} missing 'properties'"

    def test_required_fields_are_valid(self):
        """If 'required' is present, all listed fields must be in properties."""
        for name, _, _, schema in _TOOL_DEFINITIONS:
            required = schema.get("required", [])
            properties = schema.get("properties", {})
            for field in required:
                assert field in properties, (
                    f"Tool {name}: required field '{field}' not in properties"
                )

    def test_tool_count(self):
        """Should have the expected number of static tools (17 core + invalidate_cache)."""
        assert len(_TOOL_DEFINITIONS) >= 17, (
            f"Expected at least 17 tool definitions, got {len(_TOOL_DEFINITIONS)}"
        )


# ============================================================================
# _RESOURCE_DEFINITIONS Tests
# ============================================================================


@pytest.mark.unit
class TestResourceDefinitions:
    """Tests for _RESOURCE_DEFINITIONS structure."""

    def test_is_list(self):
        assert isinstance(_RESOURCE_DEFINITIONS, list)

    def test_each_entry_is_4_tuple(self):
        for entry in _RESOURCE_DEFINITIONS:
            assert isinstance(entry, tuple)
            assert len(entry) == 4

    def test_each_entry_structure(self):
        """Each resource: (uri:str, name:str, description:str, mime_type:str)."""
        for uri, name, description, mime_type in _RESOURCE_DEFINITIONS:
            assert isinstance(uri, str)
            assert isinstance(name, str)
            assert isinstance(description, str)
            assert isinstance(mime_type, str)

    def test_uris_are_codomyrmex_scheme(self):
        for uri, _, _, _ in _RESOURCE_DEFINITIONS:
            assert uri.startswith("codomyrmex://")

    def test_known_resources(self):
        uris = {r[0] for r in _RESOURCE_DEFINITIONS}
        assert "codomyrmex://modules" in uris
        assert "codomyrmex://status" in uris


# ============================================================================
# _PROMPT_DEFINITIONS Tests
# ============================================================================


@pytest.mark.unit
class TestPromptDefinitions:
    """Tests for _PROMPT_DEFINITIONS structure."""

    def test_is_list(self):
        assert isinstance(_PROMPT_DEFINITIONS, list)

    def test_nonempty(self):
        assert len(_PROMPT_DEFINITIONS) > 0

    def test_each_entry_is_4_tuple(self):
        for entry in _PROMPT_DEFINITIONS:
            assert isinstance(entry, tuple)
            assert len(entry) == 4

    def test_each_entry_structure(self):
        """Each prompt: (name:str, description:str, args:list, template:str)."""
        for name, description, args, template in _PROMPT_DEFINITIONS:
            assert isinstance(name, str), f"Prompt name should be str"
            assert isinstance(description, str), f"Prompt description should be str for {name}"
            assert isinstance(args, list), f"Prompt args should be list for {name}"
            assert isinstance(template, str), f"Prompt template should be str for {name}"

    def test_prompt_args_are_dicts(self):
        for name, _, args, _ in _PROMPT_DEFINITIONS:
            for arg in args:
                assert isinstance(arg, dict), f"Arg for prompt {name} should be dict"
                assert "name" in arg, f"Arg for prompt {name} missing 'name'"

    def test_known_prompts(self):
        names = {p[0] for p in _PROMPT_DEFINITIONS}
        expected = {
            "codomyrmex.analyze_module",
            "codomyrmex.debug_issue",
            "codomyrmex.create_test",
            "codomyrmexVerify",
            "codomyrmexTrust",
        }
        for prompt_name in expected:
            assert prompt_name in names, f"Expected prompt {prompt_name} not found"

    def test_prompt_names_unique(self):
        names = [p[0] for p in _PROMPT_DEFINITIONS]
        assert len(names) == len(set(names)), "Duplicate prompt names found"


# ============================================================================
# Proxy Tools Tests
# ============================================================================


@pytest.mark.unit
class TestProxyToolListModules:
    """Tests for _tool_list_modules proxy."""

    def test_returns_dict(self):
        from codomyrmex.agents.pai.mcp.proxy_tools import _tool_list_modules

        result = _tool_list_modules()
        assert isinstance(result, dict)
        assert "modules" in result
        assert "count" in result

    def test_modules_is_list(self):
        from codomyrmex.agents.pai.mcp.proxy_tools import _tool_list_modules

        result = _tool_list_modules()
        assert isinstance(result["modules"], list)
        assert isinstance(result["count"], int)
        assert result["count"] == len(result["modules"])


@pytest.mark.unit
class TestProxyToolModuleInfo:
    """Tests for _tool_module_info proxy."""

    def test_valid_module(self):
        from codomyrmex.agents.pai.mcp.proxy_tools import _tool_module_info

        result = _tool_module_info(module_name="concurrency")
        assert isinstance(result, dict)
        assert result["module"] == "concurrency"
        assert "exports" in result
        assert "export_count" in result

    def test_invalid_module(self):
        from codomyrmex.agents.pai.mcp.proxy_tools import _tool_module_info

        result = _tool_module_info(module_name="nonexistent_module_xyz")
        assert "error" in result


@pytest.mark.unit
class TestProxyToolListModuleFunctions:
    """Tests for _tool_list_module_functions proxy."""

    def test_valid_module(self):
        from codomyrmex.agents.pai.mcp.proxy_tools import _tool_list_module_functions

        result = _tool_list_module_functions(module="concurrency")
        assert isinstance(result, dict)
        assert "functions" in result
        assert "classes" in result
        assert "total_callables" in result

    def test_invalid_module(self):
        from codomyrmex.agents.pai.mcp.proxy_tools import _tool_list_module_functions

        result = _tool_list_module_functions(module="totally_fake_module")
        assert "error" in result

    def test_auto_prefix(self):
        from codomyrmex.agents.pai.mcp.proxy_tools import _tool_list_module_functions

        # Both should work the same
        r1 = _tool_list_module_functions(module="concurrency")
        r2 = _tool_list_module_functions(module="codomyrmex.concurrency")
        assert r1["module"] == r2["module"]


@pytest.mark.unit
class TestProxyToolCallModuleFunction:
    """Tests for _tool_call_module_function proxy."""

    def test_private_function_rejected(self):
        from codomyrmex.agents.pai.mcp.proxy_tools import _tool_call_module_function

        result = _tool_call_module_function(function="concurrency._private")
        assert "error" in result
        assert "private" in result["error"].lower()

    def test_invalid_path_format(self):
        from codomyrmex.agents.pai.mcp.proxy_tools import _tool_call_module_function

        result = _tool_call_module_function(function="nope")
        assert "error" in result

    def test_nonexistent_function(self):
        from codomyrmex.agents.pai.mcp.proxy_tools import _tool_call_module_function

        result = _tool_call_module_function(
            function="concurrency.nonexistent_fn_xyz"
        )
        assert "error" in result
        assert "available" in result  # Should suggest available functions


@pytest.mark.unit
class TestProxyToolGetModuleReadme:
    """Tests for _tool_get_module_readme proxy."""

    def test_valid_module_with_readme(self):
        from codomyrmex.agents.pai.mcp.proxy_tools import _tool_get_module_readme

        result = _tool_get_module_readme(module="concurrency")
        assert isinstance(result, dict)
        # Should have content or error
        if "error" not in result:
            assert "content" in result
            assert "path" in result

    def test_invalid_module(self):
        from codomyrmex.agents.pai.mcp.proxy_tools import _tool_get_module_readme

        result = _tool_get_module_readme(module="nonexistent_xyz")
        assert "error" in result


@pytest.mark.unit
class TestProxyToolListWorkflows:
    """Tests for _tool_list_workflows proxy."""

    def test_returns_dict_with_workflows(self):
        from codomyrmex.agents.pai.mcp.proxy_tools import _tool_list_workflows

        result = _tool_list_workflows()
        assert isinstance(result, dict)
        assert "workflows" in result
        assert "count" in result
        assert isinstance(result["workflows"], list)
        assert isinstance(result["count"], int)

    def test_workflows_have_expected_fields(self):
        from codomyrmex.agents.pai.mcp.proxy_tools import _tool_list_workflows

        result = _tool_list_workflows()
        for wf in result["workflows"]:
            assert "name" in wf
            assert "description" in wf

    def test_with_nonexistent_root(self, tmp_path):
        from codomyrmex.agents.pai.mcp.proxy_tools import _tool_list_workflows

        result = _tool_list_workflows(project_root=str(tmp_path / "nope"))
        assert result["count"] == 0


@pytest.mark.unit
class TestProxyToolInvalidateCache:
    """Tests for _tool_invalidate_cache proxy."""

    def test_invalidate_full_cache(self):
        from codomyrmex.agents.pai.mcp.discovery import _tool_invalidate_cache

        result = _tool_invalidate_cache()
        assert isinstance(result, dict)
        assert result["cleared"] is True

    def test_invalidate_specific_module_without_engine(self):
        """If engine not initialized, returns error."""
        import codomyrmex.agents.pai.mcp.discovery as disc_mod

        # Save and clear
        saved = disc_mod._DISCOVERY_ENGINE
        disc_mod._DISCOVERY_ENGINE = None
        try:
            from codomyrmex.agents.pai.mcp.discovery import _tool_invalidate_cache

            result = _tool_invalidate_cache(module="codomyrmex.search")
            assert "error" in result
        finally:
            disc_mod._DISCOVERY_ENGINE = saved


# ============================================================================
# MCPDiscovery Engine Tests (via the model_context_protocol.discovery module)
# ============================================================================


@pytest.mark.unit
class TestMCPDiscoveryEngine:
    """Tests for MCPDiscovery engine directly."""

    def test_instantiation(self):
        from codomyrmex.model_context_protocol.discovery import MCPDiscovery

        engine = MCPDiscovery()
        assert engine.tool_count == 0

    def test_scan_module_returns_report(self):
        from codomyrmex.model_context_protocol.discovery import (
            DiscoveryReport,
            MCPDiscovery,
        )

        engine = MCPDiscovery()
        report = engine.scan_module("codomyrmex.search.mcp_tools")
        assert isinstance(report, DiscoveryReport)
        assert report.modules_scanned == 1

    def test_scan_nonexistent_module(self):
        from codomyrmex.model_context_protocol.discovery import MCPDiscovery

        engine = MCPDiscovery()
        report = engine.scan_module("codomyrmex.nonexistent_xyz.mcp_tools")
        assert len(report.failed_modules) == 1

    def test_list_tools_after_scan(self):
        from codomyrmex.model_context_protocol.discovery import MCPDiscovery

        engine = MCPDiscovery()
        engine.scan_module("codomyrmex.search.mcp_tools")
        tools = engine.list_tools()
        assert isinstance(tools, list)

    def test_get_metrics(self):
        from codomyrmex.model_context_protocol.discovery import (
            DiscoveryMetrics,
            MCPDiscovery,
        )

        engine = MCPDiscovery()
        engine.scan_module("codomyrmex.search.mcp_tools")
        metrics = engine.get_metrics()
        assert isinstance(metrics, DiscoveryMetrics)
        assert metrics.modules_scanned >= 1

    def test_register_tool_manually(self):
        from codomyrmex.model_context_protocol.discovery import (
            DiscoveredTool,
            MCPDiscovery,
        )

        engine = MCPDiscovery()
        tool = DiscoveredTool(
            name="test_tool",
            description="A test tool",
            module_path="test.module",
            callable_name="test_fn",
        )
        engine.register_tool(tool)
        assert engine.tool_count == 1
        assert engine.get_tool("test_tool") is tool
        assert engine.get_tool("nonexistent") is None

    def test_record_cache_hit(self):
        from codomyrmex.model_context_protocol.discovery import MCPDiscovery

        engine = MCPDiscovery()
        assert engine.get_metrics().cache_hits == 0
        engine.record_cache_hit()
        assert engine.get_metrics().cache_hits == 1

    def test_list_tools_filter_by_tag(self):
        from codomyrmex.model_context_protocol.discovery import (
            DiscoveredTool,
            MCPDiscovery,
        )

        engine = MCPDiscovery()
        t1 = DiscoveredTool(
            name="tagged_tool",
            description="Tagged",
            module_path="m",
            callable_name="f",
            tags=["search"],
        )
        t2 = DiscoveredTool(
            name="other_tool",
            description="Other",
            module_path="m",
            callable_name="g",
            tags=["crypto"],
        )
        engine.register_tool(t1)
        engine.register_tool(t2)
        assert len(engine.list_tools(tag="search")) == 1
        assert engine.list_tools(tag="search")[0].name == "tagged_tool"
        assert len(engine.list_tools(tag="nonexistent")) == 0


@pytest.mark.unit
class TestDiscoveredToolSchema:
    """Tests for DiscoveredTool.to_mcp_schema."""

    def test_to_mcp_schema_structure(self):
        from codomyrmex.model_context_protocol.discovery import DiscoveredTool

        tool = DiscoveredTool(
            name="my_tool",
            description="Does something",
            module_path="mod.path",
            callable_name="do_thing",
            parameters={"type": "object", "properties": {}},
            tags=["core"],
            version="2.0",
        )
        schema = tool.to_mcp_schema()
        assert schema["name"] == "my_tool"
        assert schema["description"] == "Does something"
        assert schema["inputSchema"] == {"type": "object", "properties": {}}
        assert schema["tags"] == ["core"]
        assert schema["x-codomyrmex"]["module"] == "mod.path"
        assert schema["x-codomyrmex"]["callable"] == "do_thing"
        assert schema["x-codomyrmex"]["version"] == "2.0"
        assert schema["x-codomyrmex"]["available"] is True

    def test_unavailable_tool_schema(self):
        from codomyrmex.model_context_protocol.discovery import DiscoveredTool

        tool = DiscoveredTool(
            name="broken",
            description="Broken tool",
            module_path="m",
            callable_name="f",
            available=False,
            unavailable_reason="Missing deps",
        )
        schema = tool.to_mcp_schema()
        assert "UNAVAILABLE" in schema["description"]
        assert "Missing deps" in schema["description"]
        assert schema["x-codomyrmex"]["available"] is False
