"""Zero-mock hardening tests for PAI MCP bridge and trust gateway.

Every test in this module exercises real production code paths with no
unittest.mock, MagicMock, or @patch usage — in compliance with the
project's zero-mock policy.
"""

import sys
import pytest
from pathlib import Path

from codomyrmex.agents.pai.trust_gateway import (
    verify_capabilities,
    trusted_call_tool,
    TrustLevel,
    TrustRegistry,
    _registry as global_trust_registry,
    SAFE_TOOLS,
    DESTRUCTIVE_TOOLS,
    SecurityError,
)
from codomyrmex.agents.pai.mcp_bridge import (
    _tool_list_workflows,
    _tool_invalidate_cache,
    call_tool,
    get_tool_registry,
    invalidate_tool_cache,
    _PROJECT_ROOT,
    _DISCOVERY_ENGINE,
    _DYNAMIC_TOOLS_CACHE,
)
from codomyrmex.model_context_protocol.discovery import (
    mcp_tool,
    DiscoveredTool,
    MCPDiscovery,
)


# ── Fixtures ──────────────────────────────────────────────────────────


@pytest.fixture
def fresh_trust_registry():
    """Reset trust registry for each test, restore after."""
    global_trust_registry.reset()
    yield global_trust_registry
    global_trust_registry.reset()


@pytest.fixture
def _cleanup_workflow_dir():
    """Create and tear down a temporary .agent/workflows dir at _PROJECT_ROOT.

    If the directory already exists we leave it untouched and only
    remove files that this fixture created.
    """
    workflows_dir = _PROJECT_ROOT / ".agent" / "workflows"
    preexisting = workflows_dir.exists()
    created_files: list[Path] = []

    if not preexisting:
        workflows_dir.mkdir(parents=True, exist_ok=True)

    yield workflows_dir, created_files

    # Cleanup: only delete files we explicitly created
    for f in created_files:
        if f.exists():
            f.unlink()

    # Remove directories only if we created them
    if not preexisting:
        try:
            workflows_dir.rmdir()
            (workflows_dir.parent).rmdir()
        except OSError:
            pass  # Directory not empty (had other files) — leave it


# ── Test: verify_capabilities Normalization ───────────────────────────


@pytest.mark.slow
def test_verify_capabilities_structure():
    """Verify that verify_capabilities returns the normalized shape.

    Calls the real function which runs full discovery, module inventory,
    MCP server creation, and trust promotion. Marked slow because it
    exercises the entire stack.
    """
    report = verify_capabilities()

    # Check top-level keys
    assert "tools" in report
    assert "modules" in report
    assert "trust" in report
    assert "mcp" in report
    assert "discovery" in report

    # Check tools structure
    tools = report["tools"]
    assert "safe" in tools
    assert "destructive" in tools
    assert "total" in tools
    assert "by_category" in tools
    assert tools["by_category"]["safe"] + tools["by_category"]["destructive"] == tools["total"]

    # Check trust structure
    trust = report["trust"]
    assert "level" in trust
    assert "report" in trust

    # Verify modules structure
    modules = report["modules"]
    assert "loaded" in modules
    assert modules["loaded"] > 0  # At least some modules should load

    # Verify MCP structure
    mcp = report["mcp"]
    assert "server_name" in mcp
    assert "resources" in mcp
    assert "prompts" in mcp


# ── Test: trusted_call_tool Validation ────────────────────────────────


def test_trusted_call_tool_validation_success(fresh_trust_registry):
    """trusted_call_tool should execute a real safe tool when VERIFIED.

    Uses the real registry and a real safe tool (codomyrmex.list_modules)
    to verify the complete call path without any mocks.
    """
    # Promote safe tools so codomyrmex.list_modules is at least VERIFIED
    fresh_trust_registry.verify_all_safe()

    # codomyrmex.list_modules is a safe tool — should be VERIFIED now
    assert fresh_trust_registry.is_at_least_verified("codomyrmex.list_modules")

    result = trusted_call_tool("codomyrmex.list_modules")

    # Functional assertion: the tool should return modules data
    assert isinstance(result, dict)
    assert "modules" in result or "result" in result


def test_trusted_call_tool_blocked_when_untrusted(fresh_trust_registry):
    """trusted_call_tool should raise SecurityError for untrusted tools.

    With a freshly reset registry, all tools are UNTRUSTED. Calling
    a safe tool should fail because it needs at least VERIFIED.
    """
    # Registry is reset — everything is UNTRUSTED
    with pytest.raises(SecurityError, match="not trusted"):
        trusted_call_tool("codomyrmex.list_modules")


def test_trusted_call_tool_unknown_tool(fresh_trust_registry):
    """trusted_call_tool should raise KeyError for an unknown tool name."""
    fresh_trust_registry.verify_all_safe()

    with pytest.raises(KeyError, match="Unknown tool"):
        trusted_call_tool("codomyrmex.nonexistent_tool_xyz")


def test_trusted_call_tool_validation_failure(fresh_trust_registry):
    """trusted_call_tool should raise ValueError for invalid arguments.

    Uses a real tool with a known schema (codomyrmex.read_file requires
    path as string). Passing path=123 should trigger schema validation
    failure before the trust check.
    """
    # Even without trust promotion, validation happens first
    # codomyrmex.read_file has schema: {"required": ["path"], "properties": {"path": {"type": "string"}}}
    with pytest.raises(ValueError, match="Tool argument validation failed"):
        trusted_call_tool("codomyrmex.read_file", path=123)


# ── Test: _tool_list_workflows ────────────────────────────────────────


def test_tool_list_workflows_structure():
    """Test that _tool_list_workflows returns a well-structured dict.

    Calls the real function against the real _PROJECT_ROOT. We verify
    the return shape regardless of whether workflows exist.
    """
    result = _tool_list_workflows()

    assert isinstance(result, dict)
    assert "count" in result
    assert "workflows" in result
    assert isinstance(result["count"], int)
    assert isinstance(result["workflows"], list)
    assert result["count"] >= 0


def test_tool_list_workflows_with_files(_cleanup_workflow_dir):
    """Test listing workflows when .agent/workflows contains .md files."""
    workflows_dir, created_files = _cleanup_workflow_dir

    # Create a valid workflow with frontmatter
    wf1 = workflows_dir / "_test_hardening_flow.md"
    wf1.write_text(
        "---\ndescription: Test workflow\n---\nSteps...", encoding="utf-8"
    )
    created_files.append(wf1)

    # Create a workflow without frontmatter
    wf2 = workflows_dir / "_test_hardening_raw.md"
    wf2.write_text("# Just markdown", encoding="utf-8")
    created_files.append(wf2)

    result = _tool_list_workflows()

    # We created 2 files; there may be others already present
    assert result["count"] >= 2
    workflows = result["workflows"]

    item1 = next(
        (w for w in workflows if w["name"] == "_test_hardening_flow"), None
    )
    assert item1 is not None, "Did not find _test_hardening_flow in results"
    assert item1["description"] == "Test workflow"

    item2 = next(
        (w for w in workflows if w["name"] == "_test_hardening_raw"), None
    )
    assert item2 is not None, "Did not find _test_hardening_raw in results"
    assert item2["description"] == "No description"


# ── Test: _tool_invalidate_cache ──────────────────────────────────────


def test_tool_invalidate_cache_full():
    """Test full cache invalidation using real functions.

    Calls the real invalidate_tool_cache, then verifies that the bridge
    cache state was actually cleared by checking the returned dict.
    """
    # Ensure cache is populated first by calling get_tool_registry
    get_tool_registry()

    result = _tool_invalidate_cache()
    assert isinstance(result, dict)
    assert result["cleared"] is True


@pytest.mark.slow
def test_tool_invalidate_cache_module():
    """Test partial module rescan using a real module.

    Scans a real codomyrmex module with @mcp_tool decorators and
    verifies the returned report structure.
    """
    # First ensure discovery engine is initialized
    get_tool_registry()

    # Rescan a real module — git_analysis.mcp_tools has @mcp_tool decorators
    result = _tool_invalidate_cache(module="codomyrmex.git_analysis.mcp_tools")

    assert isinstance(result, dict)
    assert result["cleared"] is False
    assert result["rescanned_module"] == "codomyrmex.git_analysis.mcp_tools"
    assert isinstance(result["tools_found"], int)
    # The module may or may not have tools depending on import success
    # (git_analysis uses the decorators.mcp_tool which accepts category=)
    assert result["tools_found"] >= 0


# ── Test: @mcp_tool versioning and requirements ───────────────────────


def test_mcp_tool_decorator_metadata():
    """Test that the discovery.mcp_tool decorator captures version and requires."""

    @mcp_tool(version="1.2.3", requires=["numpy", "pandas"])
    def my_tool():
        """Docstring."""
        pass

    meta = getattr(my_tool, "_mcp_tool_meta")
    assert meta["version"] == "1.2.3"
    assert meta["requires"] == ["numpy", "pandas"]
    assert meta["name"] is None  # Default


def test_discovery_availability_missing_dep():
    """Test DiscoveredTool availability when a required dependency is missing.

    Uses sys.modules poisoning to make a fake package name appear
    unimportable, then verifies that MCPDiscovery marks the tool
    as unavailable.
    """
    # Poison sys.modules so importlib.util.find_spec returns None
    # for our sentinel package name.
    sentinel = "_codomyrmex_test_missing_dep_xyz"
    original = sys.modules.get(sentinel, "NOT_SET")
    sys.modules[sentinel] = None  # type: ignore[assignment]

    try:

        class FakeModule:
            __name__ = "_test_discovery_module"

            @mcp_tool(requires=[sentinel])
            def broken_tool():  # type: ignore[misc]
                """A tool that requires a missing dep."""
                pass

            @mcp_tool(requires=["os"])
            def working_tool():  # type: ignore[misc]
                """A tool that requires a stdlib module."""
                pass

        discovery = MCPDiscovery()
        tools = discovery._scan_module(FakeModule)

        assert len(tools) == 2

        broken = next(t for t in tools if t.callable_name == "broken_tool")
        assert broken.available is False
        assert "Missing dependencies" in broken.unavailable_reason
        assert sentinel in broken.unavailable_reason

        working = next(t for t in tools if t.callable_name == "working_tool")
        assert working.available is True

    finally:
        # Restore sys.modules
        if original == "NOT_SET":
            sys.modules.pop(sentinel, None)
        else:
            sys.modules[sentinel] = original


def test_discovery_scan_real_module():
    """Test MCPDiscovery on a real codomyrmex module with @mcp_tool decorators.

    Verifies that scanning a real module produces a valid DiscoveryReport
    with the expected structure.
    """
    discovery = MCPDiscovery()
    report = discovery.scan_module("codomyrmex.git_analysis.mcp_tools")

    assert hasattr(report, "tools")
    assert hasattr(report, "failed_modules")
    assert hasattr(report, "scan_duration_ms")
    assert report.scan_duration_ms >= 0
    assert report.modules_scanned == 1

    # The module should either have tools or have failed
    if not report.failed_modules:
        assert isinstance(report.tools, list)
        for tool in report.tools:
            assert isinstance(tool, DiscoveredTool)
            assert tool.name
            assert tool.description


# ── Test: TrustRegistry state transitions ─────────────────────────────


def test_trust_registry_lifecycle(fresh_trust_registry):
    """Test the full TrustRegistry lifecycle: reset -> verify -> trust.

    Exercises real state transitions instead of mocking internal calls.
    """
    reg = fresh_trust_registry

    # After reset, all tools should be UNTRUSTED
    for tool_name in list(reg._levels.keys())[:5]:
        assert reg.level(tool_name) == TrustLevel.UNTRUSTED

    # Promote safe tools to VERIFIED
    promoted = reg.verify_all_safe()
    assert isinstance(promoted, list)

    # At least some tools should have been promoted
    if promoted:
        assert reg.level(promoted[0]) == TrustLevel.VERIFIED

    # Trust a specific tool
    some_tool = list(reg._levels.keys())[0]
    reg.trust_tool(some_tool)
    assert reg.level(some_tool) == TrustLevel.TRUSTED

    # Trust report should reflect the changes
    report = reg.get_report()
    assert "total_tools" in report
    assert "by_level" in report
    assert "counts" in report
    assert report["total_tools"] > 0
