"""Workflow integration test: /codomyrmexStatus.

Validates the PAI status and awareness endpoints return
well-formed data without errors.
"""

import pytest


@pytest.mark.integration
class TestWorkflowStatus:
    """Tests mirroring the /codomyrmexStatus workflow."""

    def test_pai_status_returns_dict(self):
        """_tool_pai_status returns a dict."""
        from codomyrmex.agents.pai.mcp_bridge import _tool_pai_status

        result = _tool_pai_status()
        assert isinstance(result, dict), f"Expected dict, got {type(result)}"

    def test_pai_awareness_returns_dict(self):
        """_tool_pai_awareness returns a dict."""
        from codomyrmex.agents.pai.mcp_bridge import _tool_pai_awareness

        result = _tool_pai_awareness()
        assert isinstance(result, dict), f"Expected dict, got {type(result)}"

    def test_combined_status_report(self):
        """Combined status + awareness produces a valid report."""
        from codomyrmex.agents.pai.mcp_bridge import (
            _tool_pai_awareness,
            _tool_pai_status,
        )

        status = _tool_pai_status()
        awareness = _tool_pai_awareness()

        report = {
            "system_status": status,
            "pai_awareness": awareness,
        }

        assert "system_status" in report
        assert "pai_awareness" in report
        assert isinstance(report["system_status"], dict)
        assert isinstance(report["pai_awareness"], dict)
