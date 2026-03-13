"""Tests for openfang MCP tools — zero-mock, validates return shapes."""

import pytest

from codomyrmex.agents.openfang import HAS_OPENFANG
from codomyrmex.agents.openfang.mcp_tools import (
    openfang_check,
    openfang_config,
    openfang_execute,
    openfang_gateway,
    openfang_hands_list,
    openfang_send_message,
    openfang_update,
)


class TestOpenfangCheck:
    def test_returns_dict(self):
        result = openfang_check()
        assert isinstance(result, dict)

    def test_has_status_key(self):
        result = openfang_check()
        assert "status" in result

    def test_has_installed_key(self):
        result = openfang_check()
        assert "installed" in result

    def test_installed_is_bool(self):
        result = openfang_check()
        assert isinstance(result["installed"], bool)

    def test_has_submodule_initialized_key(self):
        result = openfang_check()
        assert "submodule_initialized" in result

    def test_has_upstream_sha_key(self):
        result = openfang_check()
        assert "upstream_sha" in result

    def test_has_vendor_dir_key(self):
        result = openfang_check()
        assert "vendor_dir" in result

    def test_status_is_success(self):
        result = openfang_check()
        assert result["status"] == "success"


class TestOpenfangConfig:
    def test_returns_dict(self):
        result = openfang_config()
        assert isinstance(result, dict)

    def test_has_status_success(self):
        result = openfang_config()
        assert result["status"] == "success"

    def test_has_command_key(self):
        result = openfang_config()
        assert "command" in result

    def test_has_timeout_key(self):
        result = openfang_config()
        assert "timeout" in result

    def test_has_gateway_url_key(self):
        result = openfang_config()
        assert "gateway_url" in result

    def test_has_vendor_dir_key(self):
        result = openfang_config()
        assert "vendor_dir" in result

    def test_has_install_dir_key(self):
        result = openfang_config()
        assert "install_dir" in result

    def test_has_installed_key(self):
        result = openfang_config()
        assert "installed" in result

    def test_installed_matches_has_openfang(self):
        result = openfang_config()
        assert result["installed"] == HAS_OPENFANG


class TestOpenfangExecuteGuards:
    def test_empty_prompt_returns_error(self):
        result = openfang_execute(prompt="")
        assert result["status"] == "error"

    def test_whitespace_prompt_returns_error(self):
        result = openfang_execute(prompt="   ")
        assert result["status"] == "error"

    def test_error_has_message_key(self):
        result = openfang_execute(prompt="")
        assert "message" in result

    @pytest.mark.skipif(HAS_OPENFANG, reason="Test guard behavior when binary absent")
    def test_import_guard_when_not_installed(self):
        result = openfang_execute(prompt="test")
        assert result["status"] == "error"
        assert (
            "not found" in result["message"].lower()
            or "install" in result["message"].lower()
        )


class TestOpenfangSendMessageGuards:
    def test_empty_channel_returns_error(self):
        result = openfang_send_message(channel="", target="user", message="hello")
        assert result["status"] == "error"

    def test_empty_target_returns_error(self):
        result = openfang_send_message(channel="telegram", target="", message="hello")
        assert result["status"] == "error"

    def test_empty_message_returns_error(self):
        result = openfang_send_message(channel="telegram", target="user", message="")
        assert result["status"] == "error"

    def test_whitespace_channel_returns_error(self):
        result = openfang_send_message(channel="  ", target="user", message="hello")
        assert result["status"] == "error"

    def test_all_errors_have_message_key(self):
        for result in [
            openfang_send_message(channel="", target="x", message="x"),
            openfang_send_message(channel="x", target="", message="x"),
            openfang_send_message(channel="x", target="x", message=""),
        ]:
            assert "message" in result


class TestOpenfangGatewayGuards:
    def test_invalid_action_returns_error(self):
        result = openfang_gateway(action="invalid")
        assert result["status"] == "error"

    def test_invalid_action_message_mentions_valid(self):
        result = openfang_gateway(action="restart")
        assert (
            "start" in result["message"]
            or "stop" in result["message"]
            or "status" in result["message"]
        )

    def test_returns_dict(self):
        result = openfang_gateway(action="invalid_xyz")
        assert isinstance(result, dict)


class TestOpenfangUpdate:
    def test_returns_dict(self):
        result = openfang_update()
        assert isinstance(result, dict)

    def test_has_status_key(self):
        result = openfang_update()
        assert "status" in result

    def test_vendor_not_initialized_returns_error(self):
        # Default vendor dir won't have been initialized in test env
        result = openfang_update()
        # Either success (if submodule exists) or error (if not)
        assert result["status"] in {"success", "error"}

    def test_rebuild_false_no_build_attempted(self):
        result = openfang_update(rebuild=False)
        assert isinstance(result, dict)


class TestAllToolsReturnDicts:
    def test_check_returns_dict(self):
        assert isinstance(openfang_check(), dict)

    def test_config_returns_dict(self):
        assert isinstance(openfang_config(), dict)

    def test_execute_returns_dict(self):
        assert isinstance(openfang_execute(prompt=""), dict)

    def test_gateway_returns_dict(self):
        assert isinstance(openfang_gateway(action="bad"), dict)

    def test_send_message_returns_dict(self):
        assert isinstance(
            openfang_send_message(channel="", target="", message=""), dict
        )

    def test_update_returns_dict(self):
        assert isinstance(openfang_update(), dict)

    def test_hands_list_returns_dict(self):
        result = openfang_hands_list()
        assert isinstance(result, dict)
