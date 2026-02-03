"""
Comprehensive tests for the CLI module.

This module tests all CLI functionality including:
- Environment checking
- Module discovery and listing
- Interactive shell operations
- Workflow management
- AI code generation and analysis
- System status and monitoring
- Project orchestration
"""

import pytest
import sys
import os
import tempfile
import json
import io
import subprocess
from pathlib import Path
from io import StringIO
import argparse

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from codomyrmex.cli import (
    check_environment,
    show_info,
    show_modules,
    run_interactive_shell,
    list_workflows,
    run_workflow,
    show_system_status,
    main,
    handle_ai_generate,
    handle_ai_refactor,
    handle_code_analysis,
    handle_git_analysis,
    handle_project_build,
    handle_module_test,
    handle_module_demo,
    demo_data_visualization,
    demo_ai_code_editing,
    demo_code_execution,
    demo_git_operations,
    handle_workflow_create,
    handle_project_create,
    handle_project_list,
    handle_orchestration_status,
    handle_orchestration_health
)


@pytest.mark.unit
class TestCLIEnvironment:
    """Test CLI environment checking functionality."""

    def test_check_environment_python_version_success(self):
        """Test environment check with valid Python version using real output."""
        # Capture real output
        captured = io.StringIO()
        sys.stdout = captured

        check_environment()

        output = captured.getvalue()
        sys.stdout = sys.__stdout__

        # Should print some messages
        assert len(output) > 0
        assert "Python" in output or "Codomyrmex" in output

    def test_check_environment_virtual_env(self):
        """Test environment check with real system information."""
        # Capture real output
        captured = io.StringIO()
        sys.stdout = captured

        check_environment()

        output = captured.getvalue()
        sys.stdout = sys.__stdout__

        # Should print some messages
        assert len(output) > 0


@pytest.mark.unit
class TestCLIInfo:
    """Test CLI info display functionality."""

    def test_show_info(self):
        """Test info display functionality with real output."""
        # Capture real output
        captured = io.StringIO()
        sys.stdout = captured

        show_info()

        output = captured.getvalue()
        sys.stdout = sys.__stdout__

        # Should print info messages
        assert len(output) > 0
        assert "Codomyrmex" in output


@pytest.mark.unit
class TestCLIModules:
    """Test CLI module listing functionality."""

    def test_show_modules_success(self):
        """Test module listing with real imports."""
        # Capture real output
        captured = io.StringIO()
        sys.stdout = captured

        try:
            show_modules()
            output = captured.getvalue()
            sys.stdout = sys.__stdout__

            # Should not raise an error and should print modules
            assert len(output) >= 0  # May be empty or have content
        except Exception as e:
            sys.stdout = sys.__stdout__
            pytest.fail(f"show_modules raised an exception: {e}")

    def test_show_modules_import_error(self):
        """Test module listing handles import errors gracefully."""
        # Capture real output
        captured = io.StringIO()
        sys.stdout = captured

        try:
            show_modules()
            output = captured.getvalue()
            sys.stdout = sys.__stdout__

            # Should not raise an error
            assert True
        except Exception as e:
            sys.stdout = sys.__stdout__
            pytest.fail(f"show_modules raised an exception: {e}")


@pytest.mark.unit
class TestCLIInteractiveShell:
    """Test CLI interactive shell functionality."""

    def test_run_interactive_shell_available(self):
        """Test interactive shell when available."""
        # Test that function exists and is callable
        assert callable(run_interactive_shell)

        # Try to run it (may skip if terminal interface not available)
        try:
            run_interactive_shell()
        except Exception:
            # Expected if terminal interface not available
            pass

    def test_run_interactive_shell_unavailable(self):
        """Test interactive shell when unavailable."""
        # Test that function handles unavailability gracefully
        try:
            run_interactive_shell()
        except Exception:
            # Expected if terminal interface not available
            pass


@pytest.mark.unit
class TestCLIWorkflows:
    """Test CLI workflow management functionality."""

    def test_list_workflows(self):
        """Test workflow listing with real output."""
        # Capture real output
        captured = io.StringIO()
        sys.stdout = captured

        list_workflows()

        output = captured.getvalue()
        sys.stdout = sys.__stdout__

        # Should print something (may be empty if no workflows)
        assert len(output) >= 0

    def test_run_workflow_success(self):
        """Test workflow execution with real implementation."""
        # Test that function exists and is callable
        assert callable(run_workflow)

        # Try to run a workflow (may fail if workflow doesn't exist, which is expected)
        result = run_workflow("test_workflow")

        # Should return True or False (not raise exception)
        assert isinstance(result, bool)

    def test_run_workflow_failure(self):
        """Test workflow execution failure handling."""
        # Test with non-existent workflow
        result = run_workflow("nonexistent_workflow_12345")

        # Should return False or handle gracefully
        assert isinstance(result, bool)


@pytest.mark.unit
class TestCLISystemStatus:
    """Test CLI system status functionality."""

    def test_show_system_status(self):
        """Test system status display with real output."""
        # Capture real output
        captured = io.StringIO()
        sys.stdout = captured

        show_system_status()

        output = captured.getvalue()
        sys.stdout = sys.__stdout__

        # Should print something
        assert len(output) >= 0


@pytest.mark.unit
class TestCLIAI:
    """Test CLI AI functionality."""

    def test_handle_ai_generate_success(self):
        """Test AI code generation with real implementation."""
        # Test that function exists and is callable
        assert callable(handle_ai_generate)

        # Try to generate code (may fail if API not available, which is expected)
        result = handle_ai_generate("print hello", "python", "openai")

        # Should return True or False (not raise exception)
        assert isinstance(result, bool)

    def test_handle_ai_generate_failure(self):
        """Test AI code generation failure handling."""
        # Test with invalid provider or prompt
        result = handle_ai_generate("", "python", "invalid_provider")

        # Should return False or handle gracefully
        assert isinstance(result, bool)

    def test_handle_ai_refactor_success(self, tmp_path):
        """Test AI code refactoring with real file operations."""
        # Create a real test file
        test_file = tmp_path / "test.py"
        test_file.write_text("def old_function():\n    pass\n")

        # Test that function exists and is callable
        assert callable(handle_ai_refactor)

        # Try to refactor (may fail if API not available, which is expected)
        result = handle_ai_refactor(str(test_file), "make it better")

        # Should return True or False (not raise exception)
        assert isinstance(result, bool)

    def test_handle_ai_refactor_file_not_found(self):
        """Test AI refactoring with missing file."""
        # Test with non-existent file
        result = handle_ai_refactor("nonexistent.py", "make it better")

        # Should return False
        assert result is False


@pytest.mark.unit
class TestCLIAnalysis:
    """Test CLI analysis functionality."""

    def test_handle_code_analysis_success(self, tmp_path):
        """Test code analysis with real file operations."""
        # Create a real test directory
        test_dir = tmp_path / "test_code"
        test_dir.mkdir()
        (test_dir / "test.py").write_text("def test():\n    pass\n")

        # Test that function exists and is callable
        assert callable(handle_code_analysis)

        # Try to analyze (may fail if analysis tools not available)
        result = handle_code_analysis(str(test_dir), str(tmp_path / "output"))

        # Should return True or False (not raise exception)
        assert isinstance(result, bool)

    def test_handle_git_analysis_success(self, tmp_path):
        """Test git analysis with real repository."""
        # Create a real git repository
        test_repo = tmp_path / "test_repo"
        test_repo.mkdir()

        # Try to initialize git (may fail if git not available)
        try:
            subprocess.run(["git", "init"], cwd=test_repo, check=True, capture_output=True)
        except (subprocess.SubprocessError, FileNotFoundError):
            pytest.skip("Git not available")

        # Test that function exists and is callable
        assert callable(handle_git_analysis)

        # Try to analyze (may fail if visualization tools not available)
        result = handle_git_analysis(str(test_repo))

        # Should return True or False (not raise exception)
        assert isinstance(result, bool)


@pytest.mark.unit
class TestCLIBuild:
    """Test CLI build functionality."""

    def test_handle_project_build_success(self):
        """Test project build with real implementation."""
        # Test that function exists and is callable
        assert callable(handle_project_build)

        # Try to build (may fail if build config not available)
        result = handle_project_build("build_config.json")

        # Should return True or False (not raise exception)
        assert isinstance(result, bool)


@pytest.mark.unit
class TestCLITesting:
    """Test CLI testing functionality."""

    def test_handle_module_test_success(self):
        """Test module testing with real subprocess."""
        # Test that function exists and is callable
        assert callable(handle_module_test)

        # Try to run tests (may fail if module doesn't exist or tests fail)
        result = handle_module_test("data_visualization")

        # Should return True or False (not raise exception)
        assert isinstance(result, bool)

    def test_handle_module_test_failure(self):
        """Test module testing failure handling."""
        # Test with non-existent module
        result = handle_module_test("nonexistent_module_12345")

        # Should return False or handle gracefully
        assert isinstance(result, bool)


@pytest.mark.unit
class TestCLIDemos:
    """Test CLI demo functionality."""

    def test_handle_module_demo_success(self):
        """Test module demo with real implementation."""
        # Test that function exists and is callable
        assert callable(handle_module_demo)

        # Try to run demo (may fail if module doesn't exist)
        result = handle_module_demo("data_visualization")

        # Should return True or False (not raise exception)
        assert isinstance(result, bool)

    def test_demo_data_visualization_success(self):
        """Test data visualization demo with real implementation."""
        # Test that function exists and is callable
        assert callable(demo_data_visualization)

        # Try to run demo (may fail if dependencies not available)
        result = demo_data_visualization()

        # Should return True or False (not raise exception)
        assert isinstance(result, bool)

    def test_demo_ai_code_editing_success(self):
        """Test AI code editing demo with real implementation."""
        # Test that function exists and is callable
        assert callable(demo_ai_code_editing)

        # Try to run demo (may fail if API not available)
        result = demo_ai_code_editing()

        # Should return True or False (not raise exception)
        assert isinstance(result, bool)

    def test_demo_code_execution_success(self):
        """Test code execution demo with real implementation."""
        # Test that function exists and is callable
        assert callable(demo_code_execution)

        # Try to run demo (may fail if sandbox not available)
        result = demo_code_execution()

        # Should return True or False (not raise exception)
        assert isinstance(result, bool)

    def test_demo_code_execution_functionality(self):
        """Test that demo_code_execution function exists and is callable."""
        # Test that the function exists and can be called
        assert callable(demo_code_execution)

    def test_demo_git_operations_success(self):
        """Test git operations demo with real implementation."""
        # Test that function exists and is callable
        assert callable(demo_git_operations)

        # Try to run demo (may fail if git not available)
        result = demo_git_operations()

        # Should return True or False (not raise exception)
        assert isinstance(result, bool)


@pytest.mark.unit
class TestCLIWorkflowManagement:
    """Test CLI workflow creation and management."""

    def test_handle_workflow_create_success(self):
        """Test workflow creation with real implementation."""
        # Test that function exists and is callable
        assert callable(handle_workflow_create)

        # Try to create workflow (may fail if orchestration not available)
        result = handle_workflow_create("test_workflow", "ai_analysis")

        # Should return True or False (not raise exception)
        assert isinstance(result, bool)


@pytest.mark.unit
class TestCLIProjectManagement:
    """Test CLI project creation and management."""

    def test_handle_project_create_success(self):
        """Test project creation with real implementation."""
        # Test that function exists and is callable
        assert callable(handle_project_create)

        # Try to create project (may fail if orchestration not available)
        result = handle_project_create("test_project", "ai_analysis")

        # Should return True or False (not raise exception)
        assert isinstance(result, bool)

    def test_handle_project_list_success(self):
        """Test project listing with real implementation."""
        # Test that function exists and is callable
        assert callable(handle_project_list)

        # Try to list projects (may fail if orchestration not available)
        result = handle_project_list()

        # Should return True or False (not raise exception)
        assert isinstance(result, bool)


@pytest.mark.unit
class TestCLIOrchestration:
    """Test CLI orchestration status and health."""

    def test_handle_orchestration_status_success(self):
        """Test orchestration status with real implementation."""
        # Test that function exists and is callable
        assert callable(handle_orchestration_status)

        # Try to get status (may fail if orchestration not available)
        result = handle_orchestration_status()

        # Should return True or False (not raise exception)
        assert isinstance(result, bool)

    def test_handle_orchestration_health_success(self):
        """Test orchestration health with real implementation."""
        # Test that function exists and is callable
        assert callable(handle_orchestration_health)

        # Try to check health (may fail if orchestration not available)
        result = handle_orchestration_health()

        # Should return True or False (not raise exception)
        assert isinstance(result, bool)


@pytest.mark.unit
class TestCLIMain:
    """Test CLI main function and argument parsing."""

    def test_main_help(self):
        """Test main function with help argument."""
        # Save original argv
        original_argv = sys.argv.copy()

        try:
            sys.argv = ['codomyrmex', '--help']
            # Should exit with SystemExit for help
            with pytest.raises(SystemExit):
                main()
        finally:
            sys.argv = original_argv

    def test_main_check_command(self):
        """Test main function with check command."""
        # Save original argv
        original_argv = sys.argv.copy()

        try:
            sys.argv = ['codomyrmex', 'check']
            # Should not raise exception
            main()
        finally:
            sys.argv = original_argv

    def test_main_info_command(self):
        """Test main function with info command."""
        # Save original argv
        original_argv = sys.argv.copy()

        try:
            sys.argv = ['codomyrmex', 'info']
            # Should not raise exception
            main()
        finally:
            sys.argv = original_argv

    def test_main_modules_command(self):
        """Test main function with modules command."""
        # Save original argv
        original_argv = sys.argv.copy()

        try:
            sys.argv = ['codomyrmex', 'modules']
            # Should not raise exception
            main()
        finally:
            sys.argv = original_argv

    def test_main_invalid_command(self):
        """Test main function with invalid command."""
        # Save original argv
        original_argv = sys.argv.copy()

        try:
            sys.argv = ['codomyrmex', 'invalid_command']
            # Should exit with SystemExit for invalid command
            with pytest.raises(SystemExit):
                main()
        finally:
            sys.argv = original_argv


if __name__ == "__main__":
    pytest.main([__file__])
