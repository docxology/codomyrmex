import json
import threading
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from codomyrmex.agents.pai import trust_gateway
from codomyrmex.agents.pai.trust_gateway import (
    AuditEntry,
    TrustLevel,
    clear_audit_log,
    export_audit_log,
    get_audit_log,
    get_current_trust_level,
    reset_trust,
    set_require_confirmation,
    set_trust_change_callback,
    trust_all,
    trusted_call_tool,
)


@pytest.fixture(autouse=True)
def reset_trust_gateway_state():
    """Reset global state in trust_gateway before each test."""
    reset_trust()
    clear_audit_log()
    set_require_confirmation(False)
    set_trust_change_callback(None)
    
    # Reset internal globals via direct access if needed (though public APIs should suffice)
    trust_gateway._pending_confirmations.clear()
    
    yield
    
    reset_trust()
    clear_audit_log()
    set_require_confirmation(False)
    set_trust_change_callback(None)


@pytest.fixture
def mock_registry():
    """Mock the MCP tool registry."""
    # Patch where trust_gateway imports (mcp_bridge) gets its tools from, 
    # OR patch the function in mcp_bridge itself if trust_gateway uses the imported name.
    # trust_gateway does `from ...mcp_bridge import get_tool_registry`. 
    # So we must patch `codomyrmex.agents.pai.trust_gateway.get_tool_registry`.
    # However, to be safe, we can patch `codomyrmex.agents.pai.mcp_bridge.get_tool_registry` too.
    
    with patch("codomyrmex.agents.pai.trust_gateway._registry") as mock_reg, \
         patch("codomyrmex.agents.pai.trust_gateway.get_tool_registry") as mock_get_reg:
        
        # Mock internal registry behavior
        mock_reg.is_trusted.return_value = True
        mock_reg.level.return_value = TrustLevel.TRUSTED
        mock_reg.call.return_value = "success"
        
        # Mock public registry discovery
        mock_discovery = MagicMock()
        mock_discovery.list_tools.return_value = [
            "test_tool", "tool_a", "tool_b", "safe_tool", 
            "codomyrmex.write_file", "run_command"
        ]
        # Mock tool entries for schema validation (bypass validation for test tools)
        mock_discovery.get.side_effect = lambda name: {}
        
        mock_get_reg.return_value = mock_discovery
        
        yield mock_reg


class TestAuditLog:
    def test_audit_log_records_success(self, mock_registry):
        """Verify successful tool calls are logged."""
        trusted_call_tool("test_tool", arg1="value")
        
        logs = get_audit_log()
        assert len(logs) == 1
        entry = logs[0]
        assert entry["tool_name"] == "test_tool"
        assert entry["result_status"] == "success"
        assert entry["trust_level"] == "TRUSTED"
        assert entry["error_code"] is None
        assert entry["duration_ms"] >= 0.0

    def test_audit_log_records_error(self, mock_registry):
        """Verify error tool calls are logged."""
        mock_registry.call.side_effect = ValueError("Test error")
        
        with pytest.raises(ValueError):
            trusted_call_tool("test_tool")
            
        logs = get_audit_log()
        assert len(logs) == 1
        assert logs[0]["result_status"] == "error"
        assert logs[0]["error_code"] == "ValueError"

    def test_audit_log_records_blocked(self, mock_registry):
        """Verify untrusted calls are logged as blocked."""
        mock_registry.is_trusted.return_value = False
        mock_registry.is_at_least_verified.return_value = False
        mock_registry.level.return_value = TrustLevel.UNTRUSTED
        
        with pytest.raises(trust_gateway.SecurityError):
            trusted_call_tool("test_tool")
            
        logs = get_audit_log()
        assert len(logs) == 1
        assert logs[0]["result_status"] == "blocked"
        assert logs[0]["trust_level"] == "UNTRUSTED"

    def test_audit_log_filtering(self, mock_registry):
        """Verify filtering logic."""
        trusted_call_tool("tool_a")
        trusted_call_tool("tool_b")
        
        assert len(get_audit_log(tool_name="tool_a")) == 1
        assert len(get_audit_log(tool_name="tool_b")) == 1
        assert len(get_audit_log(tool_name="nonexistent")) == 0

    def test_clear_audit_log(self, mock_registry):
        """Verify clearing logs."""
        trusted_call_tool("tool_a")
        assert len(get_audit_log()) == 1
        
        count = clear_audit_log()
        assert count == 1
        assert len(get_audit_log()) == 0

    def test_export_audit_log(self, mock_registry, tmp_path):
        """Verify export to JSONL."""
        trusted_call_tool("tool_a", foo="bar")
        
        export_path = tmp_path / "audit.jsonl"
        export_audit_log(export_path)
        
        with open(export_path) as f:
            lines = f.readlines()
            assert len(lines) == 1
            data = json.loads(lines[0])
            assert data["tool_name"] == "tool_a"


class TestTrustHooks:
    def test_trust_change_callback(self):
        """Verify callback receives old and new levels."""
        mock_callback = MagicMock()
        set_trust_change_callback(mock_callback)
        
        # Verify initial state
        assert get_current_trust_level() == TrustLevel.UNTRUSTED
        
        # Change to TRUSTED
        trust_all()
        mock_callback.assert_called_with(TrustLevel.UNTRUSTED, TrustLevel.TRUSTED)
        
        # Reset
        reset_trust()
        mock_callback.assert_called_with(TrustLevel.TRUSTED, TrustLevel.UNTRUSTED)

    def test_event_emission(self):
        """Verify EventBus emission."""
        # Mock EventBus at the source
        with patch("codomyrmex.events.EventBus") as mock_bus:
            # We need to ensure logic doesn't fail on import.
            # trust_gateway does a local import. patching sys.modules is safer.
            with patch.dict("sys.modules", {"codomyrmex.events": MagicMock(EventBus=mock_bus)}):
                trust_all()
                
            mock_bus.emit.assert_called()
            args = mock_bus.emit.call_args[0]
            assert args[0] == "TRUST_LEVEL_CHANGED"
            assert args[1]["new_level"] == "TRUSTED"


class TestDestructiveConfirmation:
    @pytest.fixture
    def destructive_setup(self, mock_registry):
        set_require_confirmation(True)
        # Mock 'write_file' as destructive
        with patch.object(trust_gateway, "DESTRUCTIVE_TOOLS", frozenset({"codomyrmex.write_file"})):
            yield

    def test_safe_tool_bypasses_confirmation(self, destructive_setup, mock_registry):
        """Safe tool should not require confirmation."""
        res = trusted_call_tool("safe_tool")
        assert res == "success"

    def test_destructive_tool_requires_confirmation(self, destructive_setup, mock_registry):
        """Destructive tool should return confirmation dict."""
        # Need to provide valid args to pass schema validation if validation was active
        # But our mock_registry.get() returns empty dict, so schema validation is skipped.
        res = trusted_call_tool("codomyrmex.write_file", path="test.txt", content="foo")
        
        assert isinstance(res, dict)
        assert res.get("confirmation_required") is True
        assert "confirm_token" in res
        
        # Verify log state checks pending
        logs = get_audit_log(status="pending_confirmation")
        assert len(logs) == 1

    def test_confirmation_token_execution(self, destructive_setup, mock_registry):
        """Valid token should execute tool."""
        # 1. Get token
        res = trusted_call_tool("codomyrmex.write_file", path="test.txt", content="foo")
        token = res["confirm_token"]
        
        # 2. Use token
        final_res = trusted_call_tool("codomyrmex.write_file", confirmation_token=token, path="test.txt", content="foo")
        assert final_res == "success"
        
        # 3. Verify success log
        logs = get_audit_log(status="success")
        assert len(logs) == 1

    def test_invalid_token_fails(self, destructive_setup, mock_registry):
        """Invalid token should raise SecurityError."""
        with pytest.raises(trust_gateway.SecurityError, match="Invalid or expired"):
            trusted_call_tool("codomyrmex.write_file", confirmation_token="invalid-token", path="test.txt", content="foo")

    def test_mismatched_token_fails(self, destructive_setup, mock_registry):
        """Token for tool A should not work for tool B."""
        # Get token for write_file
        res = trusted_call_tool("codomyrmex.write_file", path="test.txt", content="foo")
        token = res["confirm_token"]
        
        # Try to use for run_command (assuming it's also destructive in this test context)
        # We need to ensure run_command is in the destructive tools set
        # and we need to pass valid args to pass potential validation (if enabled)
        
        # NOTE: patch.object patches the variable in the module where it's DEFINED?
        # or where it's IMPORTED? 
        # trust_gateway.DESTRUCTIVE_TOOLS is what we want.
        
        with patch.object(trust_gateway, "DESTRUCTIVE_TOOLS", frozenset({"codomyrmex.write_file", "run_command"})):
             # run_command needs to require confirmation now.
             
             with pytest.raises(trust_gateway.SecurityError, match="Confirmation token does not match tool"):
                trusted_call_tool("run_command", confirmation_token=token, command="ls")
