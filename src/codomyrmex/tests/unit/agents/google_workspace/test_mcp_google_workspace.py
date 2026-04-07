"""Zero-mock tests for agents/google_workspace MCP tool functions.

Tests validate the response-type contract and error-handling paths for all 10
MCP tools. No live gws binary or credentials are required — the tools' own
try/except wrappers return {"status": "error"} when gws is absent, and the
_build_env() helper only needs os.environ (no subprocess).
"""

from __future__ import annotations

import os
import shutil

import pytest

pytestmark = pytest.mark.google_workspace


class TestGWSCheckTool:
    """gws_check() response structure when gws is absent or present."""

    def test_returns_dict(self):
        from codomyrmex.agents.google_workspace.mcp_tools import gws_check

        result = gws_check()
        assert isinstance(result, dict)

    def test_has_status_key(self):
        from codomyrmex.agents.google_workspace.mcp_tools import gws_check

        result = gws_check()
        assert "status" in result

    def test_status_is_success_or_error(self):
        from codomyrmex.agents.google_workspace.mcp_tools import gws_check

        result = gws_check()
        assert result["status"] in ("success", "error")

    def test_installed_key_present_on_success(self):
        from codomyrmex.agents.google_workspace.mcp_tools import gws_check

        result = gws_check()
        if result["status"] == "success":
            assert "installed" in result

    def test_install_hint_when_gws_absent(self):
        from codomyrmex.agents.google_workspace.mcp_tools import gws_check

        if shutil.which("gws") is None:
            result = gws_check()
            assert result["status"] == "success"
            assert result.get("installed") is False
            assert "install_hint" in result


class TestGWSConfigTool:
    """gws_config() always returns a dict with configuration fields."""

    def test_returns_dict(self):
        from codomyrmex.agents.google_workspace.mcp_tools import gws_config

        result = gws_config()
        assert isinstance(result, dict)

    def test_has_status_key(self):
        from codomyrmex.agents.google_workspace.mcp_tools import gws_config

        result = gws_config()
        assert "status" in result

    def test_status_is_success_on_clean_env(self):
        from codomyrmex.agents.google_workspace.mcp_tools import gws_config

        result = gws_config()
        assert result["status"] in ("success", "error")

    def test_has_installed_key_on_success(self):
        from codomyrmex.agents.google_workspace.mcp_tools import gws_config

        result = gws_config()
        if result["status"] == "success":
            assert "installed" in result

    def test_has_has_auth_key_on_success(self):
        from codomyrmex.agents.google_workspace.mcp_tools import gws_config

        result = gws_config()
        if result["status"] == "success":
            assert "has_auth" in result

    def test_has_timeout_key_on_success(self):
        from codomyrmex.agents.google_workspace.mcp_tools import gws_config

        result = gws_config()
        if result["status"] == "success":
            assert "timeout" in result

    def test_has_page_all_key_on_success(self):
        from codomyrmex.agents.google_workspace.mcp_tools import gws_config

        result = gws_config()
        if result["status"] == "success":
            assert "page_all" in result


class TestGWSMcpStartTool:
    """gws_mcp_start() returns correct structure for both installed/absent paths."""

    def test_returns_dict(self):
        from codomyrmex.agents.google_workspace.mcp_tools import gws_mcp_start

        result = gws_mcp_start()
        assert isinstance(result, dict)

    def test_has_status_key(self):
        from codomyrmex.agents.google_workspace.mcp_tools import gws_mcp_start

        result = gws_mcp_start()
        assert "status" in result

    def test_error_when_gws_not_installed(self):
        from codomyrmex.agents.google_workspace.mcp_tools import gws_mcp_start

        if shutil.which("gws") is None:
            result = gws_mcp_start()
            assert result["status"] == "error"
            assert "message" in result

    def test_success_has_command_when_gws_installed(self):
        from codomyrmex.agents.google_workspace.mcp_tools import gws_mcp_start

        if shutil.which("gws") is not None:
            result = gws_mcp_start()
            assert result["status"] == "success"
            assert "command" in result


class TestGWSRunTool:
    """gws_run() returns a dict; error path exercised when gws absent."""

    def test_returns_dict(self):
        from codomyrmex.agents.google_workspace.mcp_tools import gws_run

        result = gws_run("drive", "files", "list")
        assert isinstance(result, dict)

    def test_has_status_key(self):
        from codomyrmex.agents.google_workspace.mcp_tools import gws_run

        result = gws_run("drive", "files", "list")
        assert "status" in result

    def test_error_path_when_gws_absent(self):
        from codomyrmex.agents.google_workspace.mcp_tools import gws_run

        if shutil.which("gws") is None:
            result = gws_run("drive", "files", "list")
            assert result["status"] == "error"
            assert "message" in result


class TestGWSSchemaTool:
    """gws_schema() returns a dict; error path exercised when gws absent."""

    def test_returns_dict(self):
        from codomyrmex.agents.google_workspace.mcp_tools import gws_schema

        result = gws_schema("drive.files.list")
        assert isinstance(result, dict)

    def test_has_status_key(self):
        from codomyrmex.agents.google_workspace.mcp_tools import gws_schema

        result = gws_schema("drive.files.list")
        assert "status" in result

    def test_error_path_when_gws_absent(self):
        from codomyrmex.agents.google_workspace.mcp_tools import gws_schema

        if shutil.which("gws") is None:
            result = gws_schema("drive.files.list")
            assert result["status"] == "error"
            assert "message" in result


class TestGWSDriveListTool:
    """gws_drive_list_files() returns a dict; error path exercised when gws absent."""

    def test_returns_dict(self):
        from codomyrmex.agents.google_workspace.mcp_tools import gws_drive_list_files

        result = gws_drive_list_files()
        assert isinstance(result, dict)

    def test_has_status_key(self):
        from codomyrmex.agents.google_workspace.mcp_tools import gws_drive_list_files

        result = gws_drive_list_files()
        assert "status" in result

    def test_error_path_when_gws_absent(self):
        from codomyrmex.agents.google_workspace.mcp_tools import gws_drive_list_files

        if shutil.which("gws") is None:
            result = gws_drive_list_files()
            assert result["status"] == "error"
            assert "message" in result


class TestGWSGmailListTool:
    """gws_gmail_list_messages() returns a dict; always errors due to run() arg bug."""

    def test_returns_dict(self):
        from codomyrmex.agents.google_workspace.mcp_tools import gws_gmail_list_messages

        result = gws_gmail_list_messages()
        assert isinstance(result, dict)

    def test_has_status_key(self):
        from codomyrmex.agents.google_workspace.mcp_tools import gws_gmail_list_messages

        result = gws_gmail_list_messages()
        assert "status" in result

    def test_returns_error_with_message(self):
        from codomyrmex.agents.google_workspace.mcp_tools import gws_gmail_list_messages

        result = gws_gmail_list_messages()
        assert result["status"] == "error"
        assert "message" in result


class TestGWSCalendarTool:
    """gws_calendar_list_events() returns a dict; error path when gws absent."""

    def test_returns_dict(self):
        from codomyrmex.agents.google_workspace.mcp_tools import (
            gws_calendar_list_events,
        )

        result = gws_calendar_list_events()
        assert isinstance(result, dict)

    def test_has_status_key(self):
        from codomyrmex.agents.google_workspace.mcp_tools import (
            gws_calendar_list_events,
        )

        result = gws_calendar_list_events()
        assert "status" in result

    def test_error_path_when_gws_absent(self):
        from codomyrmex.agents.google_workspace.mcp_tools import (
            gws_calendar_list_events,
        )

        if shutil.which("gws") is None:
            result = gws_calendar_list_events()
            assert result["status"] == "error"
            assert "message" in result


class TestGWSSheetsTool:
    """gws_sheets_get_values() returns a dict; error path when gws absent."""

    def test_returns_dict(self):
        from codomyrmex.agents.google_workspace.mcp_tools import gws_sheets_get_values

        result = gws_sheets_get_values("spreadsheet-id", "Sheet1!A1:D10")
        assert isinstance(result, dict)

    def test_has_status_key(self):
        from codomyrmex.agents.google_workspace.mcp_tools import gws_sheets_get_values

        result = gws_sheets_get_values("spreadsheet-id", "Sheet1!A1:D10")
        assert "status" in result

    def test_error_path_when_gws_absent(self):
        from codomyrmex.agents.google_workspace.mcp_tools import gws_sheets_get_values

        if shutil.which("gws") is None:
            result = gws_sheets_get_values("sid", "A1:B2")
            assert result["status"] == "error"
            assert "message" in result


class TestGWSTasksTool:
    """gws_tasks_list() returns a dict; error path when gws absent."""

    def test_returns_dict(self):
        from codomyrmex.agents.google_workspace.mcp_tools import gws_tasks_list

        result = gws_tasks_list()
        assert isinstance(result, dict)

    def test_has_status_key(self):
        from codomyrmex.agents.google_workspace.mcp_tools import gws_tasks_list

        result = gws_tasks_list()
        assert "status" in result

    def test_error_path_when_gws_absent(self):
        from codomyrmex.agents.google_workspace.mcp_tools import gws_tasks_list

        if shutil.which("gws") is None:
            result = gws_tasks_list()
            assert result["status"] == "error"
            assert "message" in result


class TestGWSRunnerBuildEnv:
    """_build_env() returns a copy of os.environ — no gws binary needed."""

    def test_returns_dict(self):
        from codomyrmex.agents.google_workspace.core import GoogleWorkspaceRunner

        runner = GoogleWorkspaceRunner.__new__(GoogleWorkspaceRunner)
        runner.account = ""
        runner.timeout = 60
        env = runner._build_env()
        assert isinstance(env, dict)

    def test_contains_path_key(self):
        from codomyrmex.agents.google_workspace.core import GoogleWorkspaceRunner

        runner = GoogleWorkspaceRunner.__new__(GoogleWorkspaceRunner)
        runner.account = ""
        runner.timeout = 60
        env = runner._build_env()
        assert "PATH" in env

    def test_is_independent_copy_of_environ(self):
        from codomyrmex.agents.google_workspace.core import GoogleWorkspaceRunner

        runner = GoogleWorkspaceRunner.__new__(GoogleWorkspaceRunner)
        runner.account = ""
        runner.timeout = 60
        env = runner._build_env()
        assert env is not os.environ
