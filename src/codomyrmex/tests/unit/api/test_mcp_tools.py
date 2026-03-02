"""Zero-mock tests for api MCP tools."""

from __future__ import annotations

import os
from codomyrmex.api.mcp_tools import api_health_check, api_list_endpoints, api_get_spec

def test_api_health_check():
    """Test api_health_check tool."""
    result = api_health_check()
    assert result is not None
    assert "status" in result
    assert result["status"] in ["healthy", "degraded", "unhealthy"]
    assert "components" in result

def test_api_list_endpoints(tmp_path):
    """Test api_list_endpoints tool."""
    # Test with empty directory
    result = api_list_endpoints(str(tmp_path))
    assert result is not None
    assert result.get("status") in ["success", "error"]

def test_api_get_spec(tmp_path):
    """Test api_get_spec tool."""
    # Test with empty directory
    result = api_get_spec(source_paths=str(tmp_path))
    assert result is not None
    assert result.get("status") in ["success", "error"]
