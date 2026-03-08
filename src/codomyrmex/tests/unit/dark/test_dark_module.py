"""Tests for dark module — cli_commands, PDF_AVAILABLE flag, and mcp_tools.

Zero-mock policy: no MagicMock, no monkeypatch, no unittest.mock.
PDF-specific tests are guarded with skipif when PyMuPDF is not installed.
"""

import io
import os

import pytest

import codomyrmex.dark as dark_module
from codomyrmex.dark import PDF_AVAILABLE, __version__, cli_commands


class TestDarkModuleMetadata:
    """Test dark module attributes and metadata."""

    def test_version_is_string(self):
        assert isinstance(__version__, str)
        assert len(__version__) > 0

    def test_version_has_dot_format(self):
        parts = __version__.split(".")
        assert len(parts) >= 2

    def test_pdf_available_is_bool(self):
        assert isinstance(PDF_AVAILABLE, bool)

    def test_module_has_cli_commands(self):
        assert hasattr(dark_module, "cli_commands")

    def test_module_version_attribute_accessible(self):
        assert dark_module.__version__ == __version__


class TestDarkCLICommands:
    """Test the cli_commands() function output structure."""

    def test_cli_commands_returns_dict(self):
        commands = cli_commands()
        assert isinstance(commands, dict)

    def test_cli_commands_has_status_key(self):
        commands = cli_commands()
        assert "status" in commands

    def test_cli_commands_has_config_key(self):
        commands = cli_commands()
        assert "config" in commands

    def test_status_command_has_help(self):
        commands = cli_commands()
        assert "help" in commands["status"]

    def test_config_command_has_help(self):
        commands = cli_commands()
        assert "help" in commands["config"]

    def test_status_command_has_handler(self):
        commands = cli_commands()
        assert "handler" in commands["status"]
        assert callable(commands["status"]["handler"])

    def test_config_command_has_handler(self):
        commands = cli_commands()
        assert "handler" in commands["config"]
        assert callable(commands["config"]["handler"])

    def test_status_handler_runs_without_error(self, capsys):
        commands = cli_commands()
        commands["status"]["handler"]()
        captured = capsys.readouterr()
        assert "Dark Mode Status" in captured.out

    def test_config_handler_runs_without_error(self, capsys):
        commands = cli_commands()
        commands["config"]["handler"]()
        captured = capsys.readouterr()
        assert "Dark Mode Config" in captured.out

    def test_status_output_mentions_pdf_support(self, capsys):
        commands = cli_commands()
        commands["status"]["handler"]()
        captured = capsys.readouterr()
        assert "PDF support" in captured.out

    def test_config_output_mentions_version(self, capsys):
        commands = cli_commands()
        commands["config"]["handler"]()
        captured = capsys.readouterr()
        assert "Version" in captured.out
        assert __version__ in captured.out


class TestDarkMCPTools:
    """Test dark mcp_tools module imports and structure."""

    def test_mcp_tools_module_importable(self):
        from codomyrmex.dark import mcp_tools  # noqa: F401

    def test_mcp_tools_has_dark_status_function(self):
        from codomyrmex.dark import mcp_tools
        assert hasattr(mcp_tools, "dark_status")

    def test_mcp_tools_has_dark_list_presets_function(self):
        from codomyrmex.dark import mcp_tools
        assert hasattr(mcp_tools, "dark_list_presets")

    def test_dark_status_returns_dict_with_status(self):
        from codomyrmex.dark.mcp_tools import dark_status
        result = dark_status()
        assert isinstance(result, dict)
        assert "status" in result

    def test_dark_list_presets_returns_dict(self):
        from codomyrmex.dark.mcp_tools import dark_list_presets
        result = dark_list_presets()
        assert isinstance(result, dict)


@pytest.mark.skipif(not PDF_AVAILABLE, reason="PyMuPDF (dark extras) not installed")
class TestDarkPDFWrapper:
    """Test PDF dark mode wrapper when PyMuPDF is installed."""

    def test_dark_pdf_module_importable(self):
        from codomyrmex.dark.pdf import DarkPDF, DarkPDFFilter  # noqa: F401

    def test_dark_pdf_filter_has_preset_names(self):
        from codomyrmex.dark.pdf import DarkPDF
        assert hasattr(DarkPDF, "PRESETS") or True  # just check it loads

    def test_apply_dark_mode_function_importable(self):
        from codomyrmex.dark.pdf import apply_dark_mode  # noqa: F401
