"""Zero-mock tests for agents/google_workspace module.

Tests that don't require gws binary test configuration and exception classes only.
Tests requiring gws are guarded with skipif.
"""

from __future__ import annotations

import json
import os
import shutil

import pytest

# Skip guard for all tests requiring the gws binary
_GWS_INSTALLED = shutil.which("gws") is not None
_GWS_AUTH_SET = bool(
    os.getenv("GOOGLE_WORKSPACE_CLI_TOKEN")
    or os.getenv("GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE")
)

pytestmark = pytest.mark.google_workspace


class TestGWSExceptions:
    """Test exception class hierarchy and attributes."""

    def test_gws_error_is_exception(self):
        from codomyrmex.agents.google_workspace.exceptions import GWSError

        exc = GWSError("test")
        assert isinstance(exc, Exception)
        assert str(exc) == "test"

    def test_gws_not_installed_error_inherits_gws_error(self):
        from codomyrmex.agents.google_workspace.exceptions import (
            GWSError,
            GWSNotInstalledError,
        )

        exc = GWSNotInstalledError("not found")
        assert isinstance(exc, GWSError)

    def test_gws_timeout_error_inherits_gws_error(self):
        from codomyrmex.agents.google_workspace.exceptions import (
            GWSError,
            GWSTimeoutError,
        )

        exc = GWSTimeoutError("timed out")
        assert isinstance(exc, GWSError)

    def test_gws_auth_error_inherits_gws_error(self):
        from codomyrmex.agents.google_workspace.exceptions import (
            GWSAuthError,
            GWSError,
        )

        exc = GWSAuthError("no creds")
        assert isinstance(exc, GWSError)

    def test_gws_command_error_attrs(self):
        from codomyrmex.agents.google_workspace.exceptions import GWSCommandError

        exc = GWSCommandError("failed", returncode=1, stderr="err output")
        assert exc.returncode == 1
        assert exc.stderr == "err output"
        assert str(exc) == "failed"

    def test_gws_command_error_defaults(self):
        from codomyrmex.agents.google_workspace.exceptions import GWSCommandError

        exc = GWSCommandError("failed")
        assert exc.returncode == 1
        assert exc.stderr == ""

    def test_all_error_types_are_distinct(self):
        from codomyrmex.agents.google_workspace.exceptions import (
            GWSAuthError,
            GWSCommandError,
            GWSError,
            GWSNotInstalledError,
            GWSTimeoutError,
        )

        types = [GWSError, GWSNotInstalledError, GWSTimeoutError, GWSAuthError, GWSCommandError]
        assert len(set(types)) == len(types)


class TestGWSConfig:
    """Test GWSConfig dataclass and get_config() reading env vars."""

    def test_get_config_returns_gws_config(self):
        from codomyrmex.agents.google_workspace.config import GWSConfig, get_config

        cfg = get_config()
        assert isinstance(cfg, GWSConfig)

    def test_has_token_false_when_env_not_set(self):
        original = os.environ.pop("GOOGLE_WORKSPACE_CLI_TOKEN", None)
        try:
            from codomyrmex.agents.google_workspace.config import get_config

            cfg = get_config()
            assert cfg.has_token is False
        finally:
            if original is not None:
                os.environ["GOOGLE_WORKSPACE_CLI_TOKEN"] = original

    def test_has_token_true_when_env_set(self):
        original = os.environ.get("GOOGLE_WORKSPACE_CLI_TOKEN")
        os.environ["GOOGLE_WORKSPACE_CLI_TOKEN"] = "mytoken"
        try:
            from codomyrmex.agents.google_workspace.config import get_config

            cfg = get_config()
            assert cfg.has_token is True
        finally:
            if original is None:
                os.environ.pop("GOOGLE_WORKSPACE_CLI_TOKEN", None)
            else:
                os.environ["GOOGLE_WORKSPACE_CLI_TOKEN"] = original

    def test_has_credentials_false_when_env_not_set(self):
        original = os.environ.pop("GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE", None)
        try:
            from codomyrmex.agents.google_workspace.config import get_config

            cfg = get_config()
            assert cfg.has_credentials is False
        finally:
            if original is not None:
                os.environ["GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE"] = original

    def test_has_auth_false_when_nothing_set(self):
        tok = os.environ.pop("GOOGLE_WORKSPACE_CLI_TOKEN", None)
        cred = os.environ.pop("GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE", None)
        try:
            from codomyrmex.agents.google_workspace.config import get_config

            cfg = get_config()
            assert cfg.has_auth is False
        finally:
            if tok is not None:
                os.environ["GOOGLE_WORKSPACE_CLI_TOKEN"] = tok
            if cred is not None:
                os.environ["GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE"] = cred

    def test_has_auth_true_when_token_set(self):
        original = os.environ.get("GOOGLE_WORKSPACE_CLI_TOKEN")
        os.environ["GOOGLE_WORKSPACE_CLI_TOKEN"] = "tok"
        try:
            from codomyrmex.agents.google_workspace.config import get_config

            cfg = get_config()
            assert cfg.has_auth is True
        finally:
            if original is None:
                os.environ.pop("GOOGLE_WORKSPACE_CLI_TOKEN", None)
            else:
                os.environ["GOOGLE_WORKSPACE_CLI_TOKEN"] = original

    def test_page_all_false_by_default(self):
        original = os.environ.pop("GWS_PAGE_ALL", None)
        try:
            from codomyrmex.agents.google_workspace.config import get_config

            cfg = get_config()
            assert cfg.page_all is False
        finally:
            if original is not None:
                os.environ["GWS_PAGE_ALL"] = original

    def test_page_all_true_when_set_to_1(self):
        original = os.environ.get("GWS_PAGE_ALL")
        os.environ["GWS_PAGE_ALL"] = "1"
        try:
            from codomyrmex.agents.google_workspace.config import get_config

            cfg = get_config()
            assert cfg.page_all is True
        finally:
            if original is None:
                os.environ.pop("GWS_PAGE_ALL", None)
            else:
                os.environ["GWS_PAGE_ALL"] = original

    def test_page_all_true_when_set_to_true(self):
        original = os.environ.get("GWS_PAGE_ALL")
        os.environ["GWS_PAGE_ALL"] = "true"
        try:
            from codomyrmex.agents.google_workspace.config import get_config

            cfg = get_config()
            assert cfg.page_all is True
        finally:
            if original is None:
                os.environ.pop("GWS_PAGE_ALL", None)
            else:
                os.environ["GWS_PAGE_ALL"] = original

    def test_timeout_default_is_60(self):
        original = os.environ.pop("GWS_TIMEOUT", None)
        try:
            from codomyrmex.agents.google_workspace.config import get_config

            cfg = get_config()
            assert cfg.timeout == 60
        finally:
            if original is not None:
                os.environ["GWS_TIMEOUT"] = original

    def test_timeout_reads_env_var(self):
        original = os.environ.get("GWS_TIMEOUT")
        os.environ["GWS_TIMEOUT"] = "120"
        try:
            from codomyrmex.agents.google_workspace.config import get_config

            cfg = get_config()
            assert cfg.timeout == 120
        finally:
            if original is None:
                os.environ.pop("GWS_TIMEOUT", None)
            else:
                os.environ["GWS_TIMEOUT"] = original

    def test_config_account_reads_env_var(self):
        original = os.environ.get("GOOGLE_WORKSPACE_CLI_ACCOUNT")
        os.environ["GOOGLE_WORKSPACE_CLI_ACCOUNT"] = "user@example.com"
        try:
            from codomyrmex.agents.google_workspace.config import get_config

            cfg = get_config()
            assert cfg.account == "user@example.com"
        finally:
            if original is None:
                os.environ.pop("GOOGLE_WORKSPACE_CLI_ACCOUNT", None)
            else:
                os.environ["GOOGLE_WORKSPACE_CLI_ACCOUNT"] = original


class TestHasGWSFlag:
    """Test the HAS_GWS module-level bool."""

    def test_has_gws_is_bool(self):
        from codomyrmex.agents.google_workspace import HAS_GWS

        assert isinstance(HAS_GWS, bool)

    def test_has_gws_matches_which(self):
        from codomyrmex.agents.google_workspace import HAS_GWS

        assert HAS_GWS == _GWS_INSTALLED


class TestGWSRunnerInit:
    """Test GoogleWorkspaceRunner constructor behavior."""

    def test_runner_default_timeout_is_60(self):
        from codomyrmex.agents.google_workspace.core import GoogleWorkspaceRunner

        runner = GoogleWorkspaceRunner()
        assert runner.timeout == 60

    def test_runner_custom_timeout(self):
        from codomyrmex.agents.google_workspace.core import GoogleWorkspaceRunner

        runner = GoogleWorkspaceRunner(timeout=30)
        assert runner.timeout == 30

    def test_runner_account_set_explicitly(self):
        from codomyrmex.agents.google_workspace.core import GoogleWorkspaceRunner

        runner = GoogleWorkspaceRunner(account="admin@example.com")
        assert runner.account == "admin@example.com"


class TestGWSRunnerBuildCmd:
    """Test _build_cmd without invoking any subprocess (requires gws binary)."""

    @pytest.mark.skipif(not _GWS_INSTALLED, reason="gws not installed")
    def test_build_cmd_basic(self):
        from codomyrmex.agents.google_workspace.core import GoogleWorkspaceRunner

        runner = GoogleWorkspaceRunner()
        cmd = runner._build_cmd("drive", "files", "list")
        assert cmd[1] == "drive"
        assert cmd[2] == "files"
        assert cmd[3] == "list"

    @pytest.mark.skipif(not _GWS_INSTALLED, reason="gws not installed")
    def test_build_cmd_with_params(self):
        from codomyrmex.agents.google_workspace.core import GoogleWorkspaceRunner

        runner = GoogleWorkspaceRunner()
        cmd = runner._build_cmd("drive", "files", "list", params={"pageSize": 10})
        assert "--params" in cmd
        params_idx = cmd.index("--params")
        assert json.loads(cmd[params_idx + 1]) == {"pageSize": 10}

    @pytest.mark.skipif(not _GWS_INSTALLED, reason="gws not installed")
    def test_build_cmd_page_all_flag(self):
        from codomyrmex.agents.google_workspace.core import GoogleWorkspaceRunner

        runner = GoogleWorkspaceRunner()
        cmd = runner._build_cmd("drive", "files", "list", page_all=True)
        assert "--page-all" in cmd

    @pytest.mark.skipif(not _GWS_INSTALLED, reason="gws not installed")
    def test_build_cmd_dry_run_flag(self):
        from codomyrmex.agents.google_workspace.core import GoogleWorkspaceRunner

        runner = GoogleWorkspaceRunner()
        cmd = runner._build_cmd("drive", "files", "list", dry_run=True)
        assert "--dry-run" in cmd

    @pytest.mark.skipif(not _GWS_INSTALLED, reason="gws not installed")
    def test_build_cmd_with_body(self):
        from codomyrmex.agents.google_workspace.core import GoogleWorkspaceRunner

        runner = GoogleWorkspaceRunner()
        cmd = runner._build_cmd("calendar", "events", "insert", body={"summary": "Meeting"})
        assert "--json" in cmd
        json_idx = cmd.index("--json")
        assert json.loads(cmd[json_idx + 1]) == {"summary": "Meeting"}


class TestGWSRunnerNotInstalled:
    """Test that GWSNotInstalledError is raised when gws binary missing."""

    @pytest.mark.skipif(_GWS_INSTALLED, reason="gws is installed — skip not-installed test")
    def test_find_gws_raises_when_not_installed(self):
        from codomyrmex.agents.google_workspace.core import GoogleWorkspaceRunner
        from codomyrmex.agents.google_workspace.exceptions import GWSNotInstalledError

        runner = GoogleWorkspaceRunner()
        with pytest.raises(GWSNotInstalledError):
            runner._find_gws()


class TestGWSRunnerParseOutput:
    """Test _parse_output without any subprocess calls."""

    def _make_runner(self):
        from codomyrmex.agents.google_workspace.core import GoogleWorkspaceRunner

        runner = GoogleWorkspaceRunner.__new__(GoogleWorkspaceRunner)
        runner.account = ""
        runner.timeout = 60
        return runner

    def test_parse_valid_json(self):
        runner = self._make_runner()
        result = runner._parse_output('{"files": []}')
        assert result == {"files": []}

    def test_parse_empty_string(self):
        runner = self._make_runner()
        result = runner._parse_output("")
        assert result == ""

    def test_parse_raw_string_fallback(self):
        runner = self._make_runner()
        result = runner._parse_output("plain text output")
        assert result == "plain text output"

    def test_parse_ndjson(self):
        runner = self._make_runner()
        ndjson = '{"id": "1"}\n{"id": "2"}'
        result = runner._parse_output(ndjson)
        assert isinstance(result, list)
        assert len(result) == 2

    def test_parse_ndjson_preserves_items(self):
        runner = self._make_runner()
        ndjson = '{"id": "abc"}\n{"id": "def"}'
        result = runner._parse_output(ndjson)
        assert isinstance(result, list)
        assert result[0] == {"id": "abc"}
        assert result[1] == {"id": "def"}

    def test_parse_whitespace_only_returns_empty(self):
        runner = self._make_runner()
        result = runner._parse_output("   \n  ")
        assert result == ""

    def test_parse_json_list(self):
        runner = self._make_runner()
        result = runner._parse_output('[{"id": "1"}, {"id": "2"}]')
        assert isinstance(result, list)
        assert len(result) == 2

    def test_parse_json_integer(self):
        runner = self._make_runner()
        result = runner._parse_output("42")
        assert result == 42

    def test_parse_ndjson_mixed_invalid_lines(self):
        runner = self._make_runner()
        ndjson = '{"id": "1"}\nnot-json'
        result = runner._parse_output(ndjson)
        assert isinstance(result, list)
        assert result[0] == {"id": "1"}
        assert result[1] == "not-json"


class TestGetGWSVersion:
    """Test get_gws_version module-level function."""

    def test_returns_string(self):
        from codomyrmex.agents.google_workspace.core import get_gws_version

        result = get_gws_version()
        assert isinstance(result, str)

    @pytest.mark.skipif(_GWS_INSTALLED, reason="gws is installed — skip empty test")
    def test_returns_empty_when_not_installed(self):
        from codomyrmex.agents.google_workspace.core import get_gws_version

        assert get_gws_version() == ""


class TestGWSRunnerLive:
    """Live subprocess tests — only run when gws is installed and auth configured."""

    @pytest.mark.slow
    @pytest.mark.skipif(not _GWS_INSTALLED, reason="gws not installed")
    @pytest.mark.skipif(not _GWS_AUTH_SET, reason="gws auth not configured")
    def test_check_returns_version(self):
        from codomyrmex.agents.google_workspace.core import GoogleWorkspaceRunner

        runner = GoogleWorkspaceRunner()
        version = runner.check()
        assert isinstance(version, str)
        assert len(version) > 0
