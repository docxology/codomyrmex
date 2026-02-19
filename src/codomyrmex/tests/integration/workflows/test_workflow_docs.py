"""Workflow integration test: /codomyrmexDocs.

Validates that module README retrieval works for core modules
and returns well-formed markdown content.
"""

import pytest


CORE_MODULES = [
    "orchestrator",
    "events",
    "agents",
    "model_context_protocol",
    "logging_monitoring",
]


@pytest.mark.integration
class TestWorkflowDocs:
    """Tests mirroring the /codomyrmexDocs workflow."""

    @pytest.mark.parametrize("module_name", CORE_MODULES)
    def test_get_module_readme(self, module_name):
        """Each core module README is retrievable and non-empty."""
        from codomyrmex.agents.pai.mcp_bridge import _tool_get_module_readme

        result = _tool_get_module_readme(module=module_name)
        assert isinstance(result, dict), f"Expected dict, got {type(result)}"
        assert "error" not in result, f"Error fetching {module_name}: {result.get('error')}"
        content = result.get("content", "")
        assert len(content) > 10, f"README for {module_name} too short: {len(content)} chars"

    @pytest.mark.parametrize("module_name", CORE_MODULES)
    def test_readme_has_heading(self, module_name):
        """Each module README starts with a markdown heading."""
        from codomyrmex.agents.pai.mcp_bridge import _tool_get_module_readme

        result = _tool_get_module_readme(module=module_name)
        content = result.get("content", "")
        assert content.lstrip().startswith("#"), (
            f"README for {module_name} missing heading: {content[:80]!r}"
        )

    def test_nonexistent_module_returns_error(self):
        """Requesting a nonexistent module returns an error dict."""
        from codomyrmex.agents.pai.mcp_bridge import _tool_get_module_readme

        result = _tool_get_module_readme(module="nonexistent_module_xyz")
        assert isinstance(result, dict)
        assert "error" in result
