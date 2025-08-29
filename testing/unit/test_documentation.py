"""Unit tests for documentation module."""

import pytest
import sys
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock
from pathlib import Path


class TestDocumentation:
    """Test cases for documentation functionality."""

    def test_documentation_import(self, code_dir):
        """Test that we can import documentation module."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        try:
            from codomyrmex.documentation import documentation_website
            assert documentation_website is not None
        except ImportError as e:
            pytest.fail(f"Failed to import documentation_website: {e}")

    def test_documentation_module_structure(self, code_dir):
        """Test that documentation module has expected structure."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.documentation import documentation_website

        assert hasattr(documentation_website, '__file__')
        assert hasattr(documentation_website, 'main')
        assert hasattr(documentation_website, 'check_doc_environment')
        assert hasattr(documentation_website, 'install_dependencies')
        assert hasattr(documentation_website, 'start_dev_server')
        assert hasattr(documentation_website, 'build_static_site')
        assert hasattr(documentation_website, 'serve_static_site')

    @patch('shutil.which')
    def test_command_exists(self, mock_which, code_dir):
        """Test command_exists function."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from documentation.documentation_website import command_exists

        mock_which.return_value = '/usr/bin/node'
        assert command_exists('node') is True

        mock_which.return_value = None
        assert command_exists('nonexistent') is False

    @patch('documentation.documentation_website.command_exists')
    @patch('documentation.documentation_website.logger')
    def test_check_doc_environment_success(self, mock_logger, mock_command_exists, code_dir):
        """Test check_doc_environment with successful environment."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from documentation.documentation_website import check_doc_environment

        mock_command_exists.side_effect = lambda cmd: cmd in ['node', 'npm']
        mock_logger.info = MagicMock()
        mock_logger.error = MagicMock()

        result = check_doc_environment()
        assert result is True
        mock_logger.info.assert_called()

    @patch('documentation.documentation_website.command_exists')
    @patch('documentation.documentation_website.logger')
    def test_check_doc_environment_missing_node(self, mock_logger, mock_command_exists, code_dir):
        """Test check_doc_environment when Node.js is missing."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from documentation.documentation_website import check_doc_environment

        mock_command_exists.side_effect = lambda cmd: cmd != 'node'
        mock_logger.info = MagicMock()
        mock_logger.error = MagicMock()

        result = check_doc_environment()
        assert result is False
        # Check that both error messages are called
        mock_logger.error.assert_any_call("Node.js not found. Please install Node.js (v18+ recommended).")
        mock_logger.error.assert_any_call("See: https://nodejs.org/")

    @patch('documentation.documentation_website.run_command_stream_output')
    @patch('documentation.documentation_website.check_doc_environment')
    @patch('documentation.documentation_website.logger')
    def test_install_dependencies_success(self, mock_logger, mock_check_env, mock_run_command, code_dir):
        """Test install_dependencies function."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from documentation.documentation_website import install_dependencies

        mock_check_env.return_value = True
        mock_run_command.return_value = True
        mock_logger.info = MagicMock()

        result = install_dependencies('npm')
        assert result is True
        mock_run_command.assert_called_once()

    @patch('subprocess.Popen')
    @patch('documentation.documentation_website.logger')
    def test_run_command_stream_output(self, mock_logger, mock_popen, code_dir):
        """Test run_command_stream_output function."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from documentation.documentation_website import run_command_stream_output

        # Mock subprocess.Popen
        mock_process = MagicMock()
        mock_process.stdout.readline.side_effect = ['line 1\n', 'line 2\n', '']
        mock_process.wait.return_value = None
        mock_process.returncode = 0
        mock_popen.return_value = mock_process

        mock_logger.info = MagicMock()

        result = run_command_stream_output(['npm', 'install'], '/test/path')
        assert result is True
        mock_logger.info.assert_called()

    @patch('documentation.documentation_website.check_doc_environment')
    @patch('documentation.documentation_website.start_dev_server')
    @patch('documentation.documentation_website.logger')
    def test_main_full_cycle(self, mock_logger, mock_start_dev, mock_check_env, code_dir):
        """Test main function with full_cycle action."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from documentation.documentation_website import main

        mock_check_env.return_value = True
        mock_start_dev.return_value = True
        mock_logger.info = MagicMock()

        # Mock sys.argv for full_cycle action
        with patch('sys.argv', ['documentation_website.py']):
            # This will default to DEFAULT_ACTION which is 'full_cycle'
            with patch('documentation.documentation_website.install_dependencies', return_value=True):
                with patch('documentation.documentation_website.build_static_site', return_value=True):
                    with patch('documentation.documentation_website.assess_site'):
                        with patch('documentation.documentation_website.serve_static_site', return_value=True):
                            main()

        # Verify the sequence was called
        mock_logger.info.assert_any_call("--- Starting 'full_cycle' sequence ---")

    @patch('webbrowser.open')
    @patch('documentation.documentation_website.logger')
    def test_assess_site(self, mock_logger, mock_webbrowser_open, code_dir):
        """Test assess_site function."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from documentation.documentation_website import assess_site

        mock_webbrowser_open.return_value = True
        mock_logger.info = MagicMock()
        mock_logger.warning = MagicMock()

        assess_site()

        mock_logger.info.assert_called()
        mock_webbrowser_open.assert_called_once()

    def test_print_assessment_checklist(self, capsys, code_dir):
        """Test print_assessment_checklist function."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from documentation.documentation_website import print_assessment_checklist

        print_assessment_checklist()

        captured = capsys.readouterr()
        assert "--- Documentation Website Assessment Checklist ---" in captured.out
        assert "- [ ] Overall Navigation:" in captured.out
        assert "--- End of Checklist ---" in captured.out

    @patch('os.path.exists')
    @patch('documentation.documentation_website.logger')
    def test_serve_static_site_build_missing(self, mock_logger, mock_exists, code_dir):
        """Test serve_static_site when build directory doesn't exist."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from documentation.documentation_website import serve_static_site

        mock_exists.return_value = False
        mock_logger.error = MagicMock()

        result = serve_static_site('npm')
        assert result is False
        mock_logger.error.assert_called()

    def test_constants_and_paths(self, code_dir):
        """Test that module constants are properly defined."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from documentation.documentation_website import (
            DEFAULT_DOCS_PORT,
            DOCUSAURUS_BASE_PATH,
            DEFAULT_ACTION,
            DOCUSAURUS_ROOT_DIR,
            EFFECTIVE_DOCS_URL
        )

        assert DEFAULT_DOCS_PORT == 3000
        assert DOCUSAURUS_BASE_PATH == "/codomyrmex/"
        assert DEFAULT_ACTION == "full_cycle"
        assert DOCUSAURUS_ROOT_DIR is not None
        assert "localhost:3000" in EFFECTIVE_DOCS_URL

    @patch('documentation.documentation_website.logger')
    def test_build_static_site_error_handling(self, mock_logger, code_dir):
        """Test build_static_site error handling."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from documentation.documentation_website import build_static_site

        mock_logger.info = MagicMock()

        with patch('documentation.documentation_website.check_doc_environment', return_value=False):
            result = build_static_site('npm')
            assert result is False

        with patch('documentation.documentation_website.check_doc_environment', return_value=True):
            with patch('documentation.documentation_website.run_command_stream_output', return_value=True):
                result = build_static_site('npm')
                assert result is True
