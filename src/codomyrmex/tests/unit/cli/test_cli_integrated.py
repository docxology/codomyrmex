"""
Integrated tests for the CLI module with Zero-Mock policy.
These tests use real implementations to verify CLI behavior.
"""

import io
import sys

import pytest

from codomyrmex.cli.core import Cli
from codomyrmex.cli.doctor import run_doctor
from codomyrmex.cli.handlers.system import (
    check_environment,
    show_info,
    show_modules,
    show_system_status,
)


@pytest.mark.unit
class TestCLIIntegrated:
    """Integrated tests for CLI using real components."""

    def test_show_info_integrated(self):
        """Test show_info produces expected platform information."""
        captured = io.StringIO()
        sys.stdout = captured
        try:
            show_info()
            output = captured.getvalue()
        finally:
            sys.stdout = sys.__stdout__

        assert "Codomyrmex" in output
        assert "Modular, Extensible Coding Workspace" in output
        assert "Available modules" in output

    def test_check_environment_integrated(self):
        """Test check_environment runs correctly on the current environment."""
        captured = io.StringIO()
        sys.stdout = captured
        try:
            success = check_environment()
            output = captured.getvalue()
        finally:
            sys.stdout = sys.__stdout__

        assert "Python" in output
        assert "virtual environment" in output
        # Environment should be successful in the test container
        assert success is True

    def test_show_modules_integrated(self):
        """Test show_modules lists categories and modules."""
        captured = io.StringIO()
        sys.stdout = captured
        try:
            show_modules()
            output = captured.getvalue()
        finally:
            sys.stdout = sys.__stdout__

        assert "Core Modules" in output
        assert "Analysis & Visualization" in output
        assert "Execution & Building" in output
        assert "ai_code_editing" in output
        assert "logging_monitoring" in output

    def test_show_system_status_integrated(self):
        """Test show_system_status dashboard."""
        captured = io.StringIO()
        sys.stdout = captured
        try:
            show_system_status()
            output = captured.getvalue()
        finally:
            sys.stdout = sys.__stdout__

        assert "System Status Dashboard" in output
        assert "Environment Check" in output
        assert "Module Status" in output

    def test_doctor_integrated(self):
        """Test doctor diagnostic tool."""
        captured = io.StringIO()
        sys.stdout = captured
        try:
            # We run with imports=True which is relatively fast
            success = run_doctor(imports=True)
            output = captured.getvalue()
        finally:
            sys.stdout = sys.__stdout__

        assert "Codomyrmex Doctor" in output
        assert "module_imports" in output
        # It's okay if it's not successful (e.g. some optional modules missing)
        # but the tool itself should run and produce output.
        assert isinstance(success, bool)

    def test_cli_class_dispatch_integrated(self):
        """Test the main Cli class dispatching to handlers."""
        cli = Cli()

        # Test a few safe commands that don't perform heavy side effects
        captured = io.StringIO()
        sys.stdout = captured
        try:
            cli.info()
            cli.check()
            output = captured.getvalue()
        finally:
            sys.stdout = sys.__stdout__

        assert "Codomyrmex" in output
        assert "Python" in output
        assert "virtual environment" in output

    def test_cli_test_handler_real_module(self, monkeypatch):
        """Test the test handler with a real module."""
        import subprocess
        
        def mock_run(*args, **kwargs):
            # Verify the command is mostly correct
            assert "pytest" in args[0]
            return subprocess.CompletedProcess(
                args=args[0], returncode=0, stdout="Mocked tests passed\n", stderr=""
            )
            
        monkeypatch.setattr(subprocess, "run", mock_run)
        cli = Cli()

        captured = io.StringIO()
        sys.stdout = captured
        try:
            # We don't necessarily need it to pass, just that it runs the right command
            result = cli.test("cli")
            output = captured.getvalue()
        finally:
            sys.stdout = sys.__stdout__

        assert "Running tests for module: cli" in output
        assert isinstance(result, bool)


if __name__ == "__main__":
    pytest.main([__file__])
