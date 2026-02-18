
import pytest
from unittest.mock import MagicMock, patch, PropertyMock
from pathlib import Path
import json
import yaml

from codomyrmex.agents.pai.trust_gateway import (
    verify_capabilities,
    trusted_call_tool,
    TrustLevel,
    TrustRegistry,
    _registry as global_trust_registry,
    SAFE_TOOLS,
    DESTRUCTIVE_TOOLS,
)
from codomyrmex.agents.pai.mcp_bridge import (
    _tool_list_workflows,
    _tool_invalidate_cache,
    call_tool,
)
from codomyrmex.model_context_protocol.discovery import (
    mcp_tool,
    DiscoveredTool,
    MCPDiscovery,
)
from codomyrmex.model_context_protocol.errors import MCPErrorCode


# ── Fixtures ──────────────────────────────────────────────────────────

@pytest.fixture
def mock_project_root(tmp_path):
    """Mock _PROJECT_ROOT in mcp_bridge for file operations."""
    with patch("codomyrmex.agents.pai.mcp_bridge._PROJECT_ROOT", tmp_path):
        yield tmp_path


@pytest.fixture
def fresh_trust_registry():
    """Reset trust registry for each test."""
    global_trust_registry.reset()
    # Ensure our test tools are known/unknown as needed
    # We might need to mock get_tool_registry
    yield global_trust_registry
    global_trust_registry.reset()


# ── Test: verify_capabilities Normalization ───────────────────────────

def test_verify_capabilities_structure():
    """Verify that verify_capabilities returns the normalized shape."""
    with patch("codomyrmex.agents.pai.trust_gateway.get_tool_registry") as mock_get_reg:
        mock_reg = MagicMock()
        mock_reg.list_tools.return_value = ["codomyrmex.read_file", "codomyrmex.write_file"]
        mock_reg.get.side_effect = lambda n: {"schema": {"description": "desc"}}
        mock_get_reg.return_value = mock_reg
        
        with patch("codomyrmex.agents.pai.trust_gateway._discover_dynamic_tools"): # avoid real scan
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
    assert tools["by_category"]["total"] == tools["total"]
    
    # Check trust structure
    trust = report["trust"]
    assert "level" in trust
    assert "report" in trust


# ── Test: trusted_call_tool Validation ────────────────────────────────

def test_trusted_call_tool_validation_success():
    """trusted_call_tool should pass valid arguments."""
    with patch("codomyrmex.agents.pai.trust_gateway.get_tool_registry") as mock_get_reg, \
         patch("codomyrmex.agents.pai.trust_gateway.call_tool") as mock_call_tool:
         
        mock_schema = {
            "type": "object",
            "properties": {"path": {"type": "string"}},
            "required": ["path"]
        }
        mock_reg = MagicMock()
        mock_reg.list_tools.return_value = ["codomyrmex.read_file"]
        mock_reg.get.return_value = {"schema": mock_schema}
        mock_get_reg.return_value = mock_reg
        
        # Verify passed automatically if safe
        # But we need to ensure trust level is ok.
        # read_file is usually safe.
        
        # We need to ensure it's in SAFE_TOOLS or just verified.
        # Safe tools are auto-promoted to VERIFIED by verify_capabilities(),
        # but here we might be UNTRUSTED by default.
        # Let's mock the trust level check or promote it.
        global_trust_registry._levels["codomyrmex.read_file"] = TrustLevel.VERIFIED

        trusted_call_tool("codomyrmex.read_file", path="test.txt")
        mock_call_tool.assert_called_once_with("codomyrmex.read_file", path="test.txt")


def test_trusted_call_tool_validation_failure():
    """trusted_call_tool should raise validation error for invalid arguments."""
    
    with patch("codomyrmex.agents.pai.trust_gateway.get_tool_registry") as mock_get_reg:
        mock_schema = {
            "type": "object",
            "properties": {"path": {"type": "string"}},
            "required": ["path"]
        }
        mock_reg = MagicMock()
        mock_reg.list_tools.return_value = ["codomyrmex.read_file"]
        mock_reg.get.return_value = {"schema": mock_schema}
        mock_get_reg.return_value = mock_reg
        
        # Should raise before trust check
        with pytest.raises(ValueError, match="Tool argument validation failed"):
            trusted_call_tool("codomyrmex.read_file", path=123) # Wrong type


# ── Test: _tool_list_workflows ────────────────────────────────────────

def test_tool_list_workflows(mock_project_root):
    """Test listing workflows from .agent/workflows."""
    workflows_dir = mock_project_root / ".agent" / "workflows"
    workflows_dir.mkdir(parents=True)
    
    # Create a valid workflow
    wf1 = workflows_dir / "test_flow.md"
    wf1.write_text("---\ndescription: Test workflow\n---\nSteps...", encoding="utf-8")
    
    # Create a workflow without frontmatter
    wf2 = workflows_dir / "raw_flow.md"
    wf2.write_text("# Just markdown", encoding="utf-8")
    
    result = _tool_list_workflows()
    
    assert result["count"] == 2
    workflows = result["workflows"]
    
    item1 = next(w for w in workflows if w["name"] == "test_flow")
    assert item1["description"] == "Test workflow"
    
    item2 = next(w for w in workflows if w["name"] == "raw_flow")
    assert item2["description"] == "No description"


def test_tool_list_workflows_no_dir(mock_project_root):
    """Test behavior when workflow directory is missing."""
    result = _tool_list_workflows()
    assert result["count"] == 0
    assert "error" in result


# ── Test: _tool_invalidate_cache ──────────────────────────────────────

def test_tool_invalidate_cache_full():
    """Test full cache invalidation."""
    with patch("codomyrmex.agents.pai.mcp_bridge.invalidate_tool_cache") as mock_invalidate:
        result = _tool_invalidate_cache()
        assert result["cleared"] is True
        mock_invalidate.assert_called_once()


def test_tool_invalidate_cache_module():
    """Test partial module invalidation."""
    with patch("codomyrmex.agents.pai.mcp_bridge._DISCOVERY_ENGINE") as mock_engine:
        # Mock scan report
        mock_report = MagicMock()
        mock_report.tools = [1, 2] # Dummy
        mock_report.failed_modules = []
        mock_engine.scan_module.return_value = mock_report
        
        result = _tool_invalidate_cache(module="foo.bar")
        
        assert result["cleared"] is False
        assert result["rescanned_module"] == "foo.bar"
        assert result["tools_found"] == 2
        mock_engine.scan_module.assert_called_once_with("foo.bar")


# ── Test: @mcp_tool versioning and requirements ───────────────────────

def test_mcp_tool_decorator_metadata():
    """Test that decorator captures version and requires."""
    
    @mcp_tool(version="1.2.3", requires=["numpy", "pandas"])
    def my_tool():
        """Docstring."""
        pass
        
    meta = getattr(my_tool, "_mcp_tool_meta")
    assert meta["version"] == "1.2.3"
    assert meta["requires"] == ["numpy", "pandas"]
    assert meta["name"] is None # Default


def test_discovery_availability():
    """Test DiscoveredTool availability logic based on requirements."""
    
    # Mock importlib.util.find_spec to simulate missing dep
    with patch("importlib.util.find_spec") as mock_find_spec:
        mock_find_spec.side_effect = lambda name: None if name == "missing_lib" else True
        
        # Create a dummy module with a tool
        class DummyModule:
            __name__ = "dummy_mod"
            
            @mcp_tool(requires=["missing_lib"])
            def broken_tool(self): pass
            
            @mcp_tool(requires=["os"]) # usually present
            def working_tool(self): pass
            
        # Manually invoke _scan_module logic (since we can't easily import a dummy class via importlib)
        # We'll instantiate MCPDiscovery and use private _scan_module on the dummy object
        # but _scan_module expects a module object with __name__.
        
        discovery = MCPDiscovery()
        tools = discovery._scan_module(DummyModule)
        
        assert len(tools) == 2
        
        broken = next(t for t in tools if t.callable_name == "broken_tool")
        assert broken.available is False
        assert "Missing dependencies" in broken.unavailable_reason
        assert "missing_lib" in broken.unavailable_reason
        
        working = next(t for t in tools if t.callable_name == "working_tool")
        assert working.available is True

