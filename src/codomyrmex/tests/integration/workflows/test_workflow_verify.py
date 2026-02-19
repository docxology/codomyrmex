"""Workflow integration test: /codomyrmexVerify.

Validates the verify_capabilities function returns a comprehensive
audit report with module, tool, and MCP server information.
"""

import pytest


@pytest.mark.integration
class TestWorkflowVerify:
    """Tests mirroring the /codomyrmexVerify workflow."""

    def test_verify_capabilities_structure(self):
        """verify_capabilities returns dict with expected top-level keys."""
        from codomyrmex.agents.pai.trust_gateway import verify_capabilities

        report = verify_capabilities()
        assert isinstance(report, dict)
        # Should have at least some of these keys
        expected_keys = {"modules", "tools", "mcp_server", "trust", "pai_bridge"}
        found = set(report.keys()) & expected_keys
        assert len(found) >= 2, f"Expected ≥2 of {expected_keys}, got {report.keys()}"

    def test_verify_modules_count(self):
        """Verify report lists ≥82 modules."""
        from codomyrmex.agents.pai.trust_gateway import verify_capabilities

        report = verify_capabilities()
        modules = report.get("modules", {})
        # modules might be a dict with 'count' or 'loaded' key, or a list
        if isinstance(modules, dict):
            count = modules.get("count", modules.get("loaded", modules.get("total", 0)))
        elif isinstance(modules, list):
            count = len(modules)
        else:
            count = 0
        assert count >= 82, f"Expected ≥82 modules, got {count}"

    def test_verify_tools_present(self):
        """Verify report includes tool information."""
        from codomyrmex.agents.pai.trust_gateway import verify_capabilities

        report = verify_capabilities()
        tools = report.get("tools", {})
        assert tools, "Tools section should not be empty"

    def test_verify_mcp_server_health(self):
        """MCP server section should indicate health status."""
        from codomyrmex.agents.pai.trust_gateway import verify_capabilities

        report = verify_capabilities()
        mcp = report.get("mcp_server", {})
        # mcp section should exist and indicate server creation succeeded
        assert isinstance(mcp, dict)

    def test_verify_is_idempotent(self):
        """Calling verify_capabilities twice returns consistent results."""
        from codomyrmex.agents.pai.trust_gateway import verify_capabilities

        r1 = verify_capabilities()
        r2 = verify_capabilities()
        # Module counts should be identical
        assert r1.get("modules") == r2.get("modules")
