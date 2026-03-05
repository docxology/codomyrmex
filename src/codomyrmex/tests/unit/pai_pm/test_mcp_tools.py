"""Tests for pai_pm MCP tools — always-running subset (no server required)."""

from __future__ import annotations

import pytest

from codomyrmex.pai_pm.mcp_tools import (
    pai_pm_dispatch,
    pai_pm_get_awareness,
    pai_pm_get_state,
    pai_pm_health,
    pai_pm_stop,
)


@pytest.mark.unit
@pytest.mark.pai_pm
class TestPaiPmToolsReturnDict:
    """All tools must return a dict (never raise) regardless of server state."""

    def test_pai_pm_health_returns_dict(self) -> None:
        result = pai_pm_health()
        assert isinstance(result, dict)

    def test_pai_pm_health_has_running_key(self) -> None:
        result = pai_pm_health()
        assert "running" in result

    def test_pai_pm_get_state_returns_dict_on_error(self) -> None:
        # Server not running — must return error dict, not raise
        result = pai_pm_get_state()
        assert isinstance(result, dict)
        assert "status" in result or "missions" in result

    def test_pai_pm_get_awareness_returns_dict_on_error(self) -> None:
        result = pai_pm_get_awareness()
        assert isinstance(result, dict)

    def test_pai_pm_dispatch_returns_dict_on_error(self) -> None:
        result = pai_pm_dispatch(action="test_action")
        assert isinstance(result, dict)

    def test_pai_pm_stop_returns_dict(self) -> None:
        result = pai_pm_stop()
        assert isinstance(result, dict)


@pytest.mark.unit
@pytest.mark.pai_pm
class TestPaiPmToolErrorShape:
    """Error responses must follow {status: error, message: str} shape."""

    def test_get_state_error_has_message(self) -> None:
        result = pai_pm_get_state()
        if result.get("status") == "error":
            assert isinstance(result.get("message"), str)

    def test_dispatch_error_has_message(self) -> None:
        result = pai_pm_dispatch(action="nonexistent")
        if result.get("status") == "error":
            assert isinstance(result.get("message"), str)
