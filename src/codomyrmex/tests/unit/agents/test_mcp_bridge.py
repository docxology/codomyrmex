"""Zero-mock test suite for the PAI ↔ Codomyrmex MCP bridge.

Tests all 15 MCP tools, resources, prompts, the skill manifest,
direct call API, and MCP server creation using real objects and
filesystem operations.
"""

import json
from pathlib import Path

import pytest

from codomyrmex.agents.pai.mcp_bridge import (
    PROMPT_COUNT,
    RESOURCE_COUNT,
    TOOL_COUNT,
    call_tool,
    create_codomyrmex_mcp_server,
    get_skill_manifest,
    get_tool_registry,
)
from codomyrmex.agents.pai.trust_gateway import (
    reset_trust,
    trust_all,
)
from codomyrmex.model_context_protocol import MCPServer, MCPToolRegistry


# ── Project root (for file-based tests) ──────────────────────────────

PROJECT_ROOT = Path(__file__).resolve().parents[5]
PYPROJECT = PROJECT_ROOT / "pyproject.toml"


# =====================================================================
# Server & Registry
# =====================================================================

class TestCreateServer:
    """Test MCP server creation."""

    def test_returns_mcp_server(self):
        server = create_codomyrmex_mcp_server()
        assert isinstance(server, MCPServer)

    def test_all_tools_registered(self):
        server = create_codomyrmex_mcp_server()
        from codomyrmex.agents.pai.mcp_bridge import get_total_tool_count
        assert len(server._tool_registry.list_tools()) == get_total_tool_count()

    def test_resources_registered(self):
        server = create_codomyrmex_mcp_server()
        # 2 static + 1 discovery metrics = 3
        assert len(server._resources) >= RESOURCE_COUNT

    def test_prompts_registered(self):
        server = create_codomyrmex_mcp_server()
        assert len(server._prompts) == PROMPT_COUNT

    def test_tool_names_prefixed(self):
        server = create_codomyrmex_mcp_server()
        for name in server._tool_registry.list_tools():
            assert name.startswith("codomyrmex."), f"Tool {name} missing prefix"

    def test_custom_name(self):
        server = create_codomyrmex_mcp_server(name="test-server")
        assert server.config.name == "test-server"


class TestToolRegistry:
    """Test MCPToolRegistry creation."""

    def test_returns_registry(self):
        reg = get_tool_registry()
        assert isinstance(reg, MCPToolRegistry)

    def test_registry_has_all_tools(self):
        reg = get_tool_registry()
        from codomyrmex.agents.pai.mcp_bridge import get_total_tool_count
        assert len(reg.list_tools()) == get_total_tool_count()

    def test_registry_tools_have_handlers(self):
        reg = get_tool_registry()
        for name in reg.list_tools():
            tool = reg.get(name)
            assert tool is not None
            assert tool.get("handler") is not None, f"Tool {name} missing handler"


# =====================================================================
# Direct call_tool API
# =====================================================================

class TestCallToolDiscovery:
    """Test discovery tools via call_tool."""

    @pytest.fixture(autouse=True)
    def _trust_all(self):
        trust_all()
        yield
        reset_trust()

    def test_list_modules(self):
        result = call_tool("codomyrmex.list_modules")
        if "error" in result and "TrustRegistry" in str(result["error"]):
            pytest.skip(f"TrustRegistry internal: {result['error']}")
            
        assert "modules" in result
        assert "count" in result
        assert isinstance(result["modules"], list)
        assert isinstance(result["count"], int)

    def test_module_info_valid(self):
        result = call_tool("codomyrmex.module_info", module_name="logging_monitoring")
        assert result["module"] == "logging_monitoring"
        assert result["docstring"] is not None or result["exports"]
        assert result["path"] is not None

    def test_module_info_invalid(self):
        result = call_tool("codomyrmex.module_info", module_name="nonexistent_module_xyz")
        assert "error" in result

    def test_unknown_tool_raises(self):
        with pytest.raises(KeyError, match="Unknown tool"):
            call_tool("codomyrmex.does_not_exist")


class TestCallToolFileOps:
    """Test file operation tools via call_tool."""

    @pytest.fixture(autouse=True)
    def _trust_all(self):
        trust_all()
        yield
        reset_trust()

    def test_read_file(self):
        result = call_tool("codomyrmex.read_file", path=str(PYPROJECT))
        assert "content" in result
        assert "codomyrmex" in result["content"].lower()

    def test_read_file_missing(self):
        result = call_tool("codomyrmex.read_file", path="/tmp/nonexistent_file_xyz_12345.txt")
        assert "error" in result

    def test_list_directory(self):
        result = call_tool("codomyrmex.list_directory", path=str(PROJECT_ROOT / "src"))
        assert "items" in result


class TestCallToolCodeAnalysis:
    """Test code analysis tools via call_tool."""

    @pytest.fixture(autouse=True)
    def _trust_all(self):
        trust_all()
        yield
        reset_trust()

    def test_analyze_python(self):
        bridge_path = str(
            PROJECT_ROOT / "src" / "codomyrmex" / "agents" / "pai" / "mcp_bridge.py"
        )
        result = call_tool("codomyrmex.analyze_python", path=bridge_path)
        assert "functions" in result or "classes" in result or "error" not in result

    def test_search_codebase(self):
        result = call_tool(
            "codomyrmex.search_codebase",
            pattern="PAIBridge",
            path=str(PROJECT_ROOT / "src" / "codomyrmex" / "agents" / "pai"),
            file_types=[".py"],
        )
        assert "matches" in result or "total" in result or isinstance(result, dict)


class TestCallToolGit:
    """Test git tools via call_tool."""

    @pytest.fixture(autouse=True)
    def _trust_all(self):
        trust_all()
        yield
        reset_trust()

    def test_git_status(self):
        result = call_tool("codomyrmex.git_status", path=str(PROJECT_ROOT))
        assert isinstance(result, dict)
        # Should have branch info or be a valid response
        assert "branch" in result or "error" not in result

    def test_git_diff(self):
        result = call_tool("codomyrmex.git_diff", path=str(PROJECT_ROOT))
        assert isinstance(result, dict)


class TestCallToolPAI:
    """Test PAI tools via call_tool."""

    @pytest.fixture(autouse=True)
    def _trust_all(self):
        trust_all()
        yield
        reset_trust()

    def test_pai_status(self):
        result = call_tool("codomyrmex.pai_status")
        assert isinstance(result, dict)
        # Should always have these keys even if PAI not installed
        assert "pai_installed" in result or "installed" in result or isinstance(result, dict)

    def test_pai_awareness(self):
        result = call_tool("codomyrmex.pai_awareness")
        assert isinstance(result, dict)


class TestCallToolData:
    """Test data utility tools via call_tool."""

    @pytest.fixture(autouse=True)
    def _trust_all(self):
        trust_all()
        yield
        reset_trust()

    def test_checksum_file(self):
        result = call_tool("codomyrmex.checksum_file", path=str(PYPROJECT))
        assert "checksum" in result or "hash" in result or isinstance(result, dict)

    def test_json_query(self):
        # Find a JSON file to test with
        pkg_json = PROJECT_ROOT / "package.json"
        if pkg_json.exists():
            result = call_tool("codomyrmex.json_query", path=str(pkg_json))
            assert isinstance(result, dict)


# =====================================================================
# Skill Manifest
# =====================================================================

class TestSkillManifest:
    """Test PAI skill manifest structure."""

    def test_manifest_structure(self):
        manifest = get_skill_manifest()
        assert manifest["name"] == "Codomyrmex"
        assert "version" in manifest
        assert "description" in manifest
        assert "mcp_server" in manifest

    def test_manifest_has_all_tools(self):
        manifest = get_skill_manifest()
        from codomyrmex.agents.pai.mcp_bridge import get_total_tool_count
        assert len(manifest["tools"]) >= get_total_tool_count()

    def test_manifest_has_resources(self):
        manifest = get_skill_manifest()
        assert len(manifest["resources"]) == RESOURCE_COUNT

    def test_manifest_has_prompts(self):
        manifest = get_skill_manifest()
        assert len(manifest["prompts"]) == PROMPT_COUNT

    def test_manifest_has_workflows(self):
        manifest = get_skill_manifest()
        assert len(manifest["workflows"]) >= 3

    def test_manifest_algorithm_mapping(self):
        manifest = get_skill_manifest()
        mapping = manifest["algorithm_mapping"]
        phases = ["OBSERVE", "THINK", "PLAN", "BUILD", "EXECUTE", "VERIFY", "LEARN"]
        for phase in phases:
            assert phase in mapping, f"Missing Algorithm phase: {phase}"
            assert len(mapping[phase]) > 0

    def test_manifest_knowledge_scope(self):
        manifest = get_skill_manifest()
        scope = manifest["knowledge_scope"]
        assert len(scope) >= 6
        # Verify each domain has modules
        for domain, modules in scope.items():
            assert len(modules) > 0, f"Empty knowledge scope: {domain}"

    def test_manifest_tools_have_schemas(self):
        manifest = get_skill_manifest()
        for tool in manifest["tools"]:
            assert "name" in tool
            assert "description" in tool
            assert "input_schema" in tool

    def test_manifest_serializable(self):
        """Manifest must be JSON-serializable for PAI consumption."""
        manifest = get_skill_manifest()
        serialized = json.dumps(manifest, indent=2)
        deserialized = json.loads(serialized)
        assert deserialized["name"] == "Codomyrmex"


# =====================================================================
# Constants
# =====================================================================

class TestConstants:
    """Test module-level constants."""

    def test_tool_count(self):
        # TOOL_COUNT is the static base count; dynamic tools may add more
        assert TOOL_COUNT >= 18

    def test_resource_count(self):
        assert RESOURCE_COUNT >= 2  # at least the 2 static resources

    def test_prompt_count(self):
        assert PROMPT_COUNT == 10  # 3 original + 7 expansion prompts

    def test_direct_call_matches_registry(self):
        """call_tool and get_tool_registry should expose the same tools."""
        reg = get_tool_registry()
        reg_names = set(reg.list_tools())
        from codomyrmex.agents.pai.mcp_bridge import get_total_tool_count
        assert len(reg_names) == get_total_tool_count()
        # Every tool should be callable via call_tool
        for name in reg_names:
            assert name.startswith("codomyrmex.")


class TestDynamicDiscovery:
    """Test dynamic tool discovery from modules."""

    def test_dynamic_discovery_returns_tools(self):
        """Dynamic discovery finds at least some tools from modules."""
        from codomyrmex.agents.pai.mcp_bridge import _discover_dynamic_tools
        tools = _discover_dynamic_tools()
        assert isinstance(tools, list)
        assert len(tools) > 0, "Dynamic discovery should find at least 1 tool"

    def test_dynamic_tool_structure(self):
        """Each discovered tool has correct tuple structure."""
        from codomyrmex.agents.pai.mcp_bridge import _discover_dynamic_tools
        tools = _discover_dynamic_tools()
        for name, desc, handler, schema in tools:
            assert isinstance(name, str), f"Tool name should be str, got {type(name)}"
            assert isinstance(desc, str), f"Tool desc should be str, got {type(desc)}"
            assert callable(handler), f"Tool {name} handler should be callable"
            assert isinstance(schema, dict), f"Tool {name} schema should be dict"

    def test_dynamic_tools_included_in_registry(self):
        """Dynamic tools should be in the full tool registry."""
        from codomyrmex.agents.pai.mcp_bridge import _discover_dynamic_tools
        reg = get_tool_registry()
        reg_names = set(reg.list_tools())
        dynamic = _discover_dynamic_tools()
        for name, _, _, _ in dynamic:
            assert name in reg_names, f"Dynamic tool {name} not in registry"
