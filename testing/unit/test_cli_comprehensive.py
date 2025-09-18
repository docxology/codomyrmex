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
from pathlib import Path
from unittest.mock import patch, MagicMock, call, mock_open
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


class TestCLIEnvironment:
    """Test CLI environment checking functionality."""

    @patch('builtins.print')
    def test_check_environment_python_version_success(self, mock_print):
        """Test environment check with valid Python version."""
        # Don't mock sys.version_info as it breaks other imports
        # Just test the function with current environment
        check_environment()

        # Should print some messages
        mock_print.assert_called()
        assert mock_print.call_count > 0

    @patch('builtins.print')
    def test_check_environment_virtual_env(self, mock_print):
        """Test environment check with virtual environment detection."""
        # Mock virtual environment detection
        with patch('sys.real_prefix', '/path/to/venv'):
            check_environment()

        # Should print some messages
        mock_print.assert_called()
        assert mock_print.call_count > 0


class TestCLIInfo:
    """Test CLI info display functionality."""

    @patch('builtins.print')
    def test_show_info(self, mock_print):
        """Test info display functionality."""
        show_info()

        # Should print info messages
        mock_print.assert_called()
        info_calls = [call for call in mock_print.call_args_list
                     if 'Codomyrmex' in str(call)]
        assert len(info_calls) > 0


class TestCLIModules:
    """Test CLI module listing functionality."""

    @patch('builtins.print')
    @patch('importlib.import_module')
    def test_show_modules_success(self, mock_import, mock_print):
        """Test module listing with successful imports."""
        mock_import.return_value = MagicMock()

        show_modules()

        mock_print.assert_called()

    @patch('builtins.print')
    @patch('importlib.import_module', side_effect=ImportError("Module not found"))
    def test_show_modules_import_error(self, mock_import, mock_print):
        """Test module listing with import errors."""
        show_modules()

        mock_print.assert_called()


class TestCLIInteractiveShell:
    """Test CLI interactive shell functionality."""

    @patch('codomyrmex.cli.TERMINAL_INTERFACE_AVAILABLE', True)
    @patch('codomyrmex.cli.InteractiveShell')
    def test_run_interactive_shell_available(self, mock_shell_class):
        """Test interactive shell when available."""
        mock_shell_instance = MagicMock()
        mock_shell_class.return_value = mock_shell_instance

        run_interactive_shell()

        mock_shell_class.assert_called_once()
        mock_shell_instance.run.assert_called_once()

    @patch('codomyrmex.cli.TERMINAL_INTERFACE_AVAILABLE', False)
    @patch('builtins.print')
    def test_run_interactive_shell_unavailable(self, mock_print):
        """Test interactive shell when unavailable."""
        run_interactive_shell()

        mock_print.assert_called()


class TestCLIWorkflows:
    """Test CLI workflow management functionality."""

    @patch('builtins.print')
    def test_list_workflows(self, mock_print):
        """Test workflow listing."""
        list_workflows()

        mock_print.assert_called()

    @patch('builtins.print')
    @patch('codomyrmex.cli.logger')
    def test_run_workflow_success(self, mock_logger, mock_print):
        """Test workflow execution success."""
        # Mock successful workflow execution
        with patch('codomyrmex.project_orchestration.workflow_manager.get_workflow_manager') as mock_get_manager:
            mock_manager = MagicMock()
            mock_workflow = MagicMock()
            mock_workflow.status.value = "completed"
            mock_manager.execute_workflow.return_value = mock_workflow
            mock_get_manager.return_value = mock_manager

            result = run_workflow("test_workflow")

            assert result is True
            mock_logger.info.assert_called()

    @patch('builtins.print')
    @patch('codomyrmex.cli.logger')
    def test_run_workflow_failure(self, mock_logger, mock_print):
        """Test workflow execution failure."""
        # Mock failed workflow execution
        with patch('codomyrmex.project_orchestration.workflow_manager.get_workflow_manager') as mock_get_manager:
            mock_manager = MagicMock()
            mock_workflow = MagicMock()
            mock_workflow.status.value = "failed"
            mock_manager.execute_workflow.return_value = mock_workflow
            mock_get_manager.return_value = mock_manager

            result = run_workflow("test_workflow")

            assert result is False
            mock_logger.error.assert_called()


class TestCLISystemStatus:
    """Test CLI system status functionality."""

    @patch('builtins.print')
    def test_show_system_status(self, mock_print):
        """Test system status display."""
        show_system_status()

        mock_print.assert_called()
        assert mock_print.call_count > 0


class TestCLIAI:
    """Test CLI AI functionality."""

    def test_handle_ai_generate_success(self):
        """Test AI code generation success."""
        with patch('codomyrmex.ai_code_editing.generate_code_snippet') as mock_generate:
            mock_result = {'status': 'success', 'generated_code': 'print("hello")'}
            mock_generate.return_value = mock_result

            result = handle_ai_generate("print hello", "python", "openai")

            assert result is True
            mock_generate.assert_called_once_with(
                prompt="print hello",
                language="python",
                llm_provider="openai"
            )

    def test_handle_ai_generate_failure(self):
        """Test AI code generation failure."""
        with patch('codomyrmex.ai_code_editing.generate_code_snippet') as mock_generate:
            mock_generate.side_effect = Exception("API error")

            result = handle_ai_generate("print hello", "python", "openai")

            assert result is False
            mock_generate.assert_called_once_with(
                prompt="print hello",
                language="python",
                llm_provider="openai"
            )

    def test_handle_ai_refactor_success(self):
        """Test AI code refactoring success."""
        with patch('codomyrmex.ai_code_editing.refactor_code_snippet') as mock_refactor:
            mock_result = {'status': 'success', 'refactored_code': 'print("hello")'}
            mock_refactor.return_value = mock_result

            with patch('builtins.open', mock_open(read_data='old code')):
                result = handle_ai_refactor("test.py", "make it better")

            assert result is True
            mock_refactor.assert_called_once()

    def test_handle_ai_refactor_file_not_found(self):
        """Test AI refactoring with missing file."""
        with patch('builtins.open', side_effect=FileNotFoundError):
            result = handle_ai_refactor("nonexistent.py", "make it better")

            assert result is False


class TestCLIAnalysis:
    """Test CLI analysis functionality."""

    def test_handle_code_analysis_success(self):
        """Test code analysis success."""
        with patch('codomyrmex.static_analysis.analyze_project') as mock_analyze:
            mock_result = {'issues': [], 'summary': {'total_files': 5}}
            mock_analyze.return_value = mock_result

            result = handle_code_analysis("/path/to/code", "/tmp/output")

            assert result is True
            mock_analyze.assert_called_once_with(
                project_root="/path/to/code",
                analysis_types=None
            )

    def test_handle_git_analysis_success(self):
        """Test git analysis success."""
        with patch('codomyrmex.data_visualization.git_visualizer.visualize_git_repository') as mock_visualize:
            mock_visualize.return_value = True

            result = handle_git_analysis("/path/to/repo")

            assert result is True
            mock_visualize.assert_called_once_with(
                "/path/to/repo",
                output_dir="./git_analysis"
            )


class TestCLIBuild:
    """Test CLI build functionality."""

    @patch('codomyrmex.cli.logger')
    def test_handle_project_build_success(self, mock_logger):
        """Test project build success."""
        with patch('codomyrmex.build_synthesis.trigger_build') as mock_build:
            mock_result = {'success': True, 'artifacts': []}
            mock_build.return_value = mock_result

            result = handle_project_build("build_config.json")

            assert result is True
            mock_logger.info.assert_called()


class TestCLITesting:
    """Test CLI testing functionality."""

    @patch('codomyrmex.cli.logger')
    @patch('subprocess.run')
    def test_handle_module_test_success(self, mock_subprocess, mock_logger):
        """Test module testing success."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_subprocess.return_value = mock_result

        result = handle_module_test("data_visualization")

        assert result is True
        mock_logger.info.assert_called()

    @patch('codomyrmex.cli.logger')
    @patch('subprocess.run')
    def test_handle_module_test_failure(self, mock_subprocess, mock_logger):
        """Test module testing failure."""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_subprocess.return_value = mock_result

        result = handle_module_test("data_visualization")

        assert result is False
        mock_logger.error.assert_called()


class TestCLIDemos:
    """Test CLI demo functionality."""

    @patch('codomyrmex.cli.logger')
    def test_handle_module_demo_success(self, mock_logger):
        """Test module demo success."""
        with patch('codomyrmex.cli.demo_data_visualization') as mock_demo:
            mock_demo.return_value = True

            result = handle_module_demo("data_visualization")

            assert result is True
            mock_logger.info.assert_called()

    @patch('codomyrmex.cli.logger')
    def test_demo_data_visualization_success(self, mock_logger):
        """Test data visualization demo success."""
        with patch('codomyrmex.data_visualization.create_line_plot') as mock_plot:
            mock_plot.return_value = MagicMock()

            result = demo_data_visualization()

            assert result is True

    @patch('codomyrmex.cli.logger')
    def test_demo_ai_code_editing_success(self, mock_logger):
        """Test AI code editing demo success."""
        with patch('codomyrmex.ai_code_editing.generate_code_snippet') as mock_generate:
            mock_result = {'status': 'success', 'generated_code': 'print("hello")'}
            mock_generate.return_value = mock_result

            result = demo_ai_code_editing()

            assert result is True

    @patch('codomyrmex.cli.logger')
    def test_demo_code_execution_success(self, mock_logger):
        """Test code execution demo success."""
        with patch('codomyrmex.code_execution_sandbox.execute_code') as mock_execute:
            mock_result = {'success': True, 'stdout': 'Hello World', 'exit_code': 0}
            mock_execute.return_value = mock_result

            result = demo_code_execution()

            assert result is True

    def test_demo_code_execution_functionality(self):
        """Test that demo_code_execution function exists and is callable."""
        # Test that the function exists and can be called
        assert callable(demo_code_execution)
        # Note: We don't run it here as it might require external dependencies

    @patch('codomyrmex.cli.logger')
    def test_demo_git_operations_success(self, mock_logger):
        """Test git operations demo success."""
        with patch('codomyrmex.git_operations.repository_manager.RepositoryManager') as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo_class.return_value = mock_repo

            result = demo_git_operations()

            assert result is True


class TestCLIWorkflowManagement:
    """Test CLI workflow creation and management."""

    @patch('codomyrmex.cli.logger')
    def test_handle_workflow_create_success(self, mock_logger):
        """Test workflow creation success."""
        with patch('codomyrmex.project_orchestration.workflow_manager.get_workflow_manager') as mock_get_manager:
            mock_manager = MagicMock()
            mock_get_manager.return_value = mock_manager

            result = handle_workflow_create("test_workflow", "ai_analysis")

            assert result is True
            mock_logger.info.assert_called()


class TestCLIProjectManagement:
    """Test CLI project creation and management."""

    @patch('codomyrmex.cli.logger')
    def test_handle_project_create_success(self, mock_logger):
        """Test project creation success."""
        with patch('codomyrmex.project_orchestration.project_manager.ProjectManager') as mock_proj_class:
            mock_project = MagicMock()
            mock_proj_class.return_value = mock_project

            result = handle_project_create("test_project", "ai_analysis")

            assert result is True
            mock_logger.info.assert_called()

    @patch('codomyrmex.cli.logger')
    @patch('builtins.print')
    def test_handle_project_list_success(self, mock_logger, mock_print):
        """Test project listing success."""
        with patch('codomyrmex.project_orchestration.project_manager.ProjectManager') as mock_proj_class:
            mock_project = MagicMock()
            mock_project.list_projects.return_value = ['project1', 'project2']
            mock_proj_class.return_value = mock_project

            result = handle_project_list()

            assert result is True
            mock_print.assert_called()


class TestCLIOrchestration:
    """Test CLI orchestration status and health."""

    @patch('codomyrmex.cli.logger')
    @patch('builtins.print')
    def test_handle_orchestration_status_success(self, mock_logger, mock_print):
        """Test orchestration status success."""
        with patch('codomyrmex.project_orchestration.orchestration_engine.OrchestrationEngine') as mock_engine_class:
            mock_engine = MagicMock()
            mock_engine.get_status.return_value = {'status': 'healthy', 'active_workflows': 5}
            mock_engine_class.return_value = mock_engine

            result = handle_orchestration_status()

            assert result is True
            mock_print.assert_called()

    @patch('codomyrmex.cli.logger')
    @patch('builtins.print')
    def test_handle_orchestration_health_success(self, mock_logger, mock_print):
        """Test orchestration health success."""
        with patch('codomyrmex.project_orchestration.orchestration_engine.OrchestrationEngine') as mock_engine_class:
            mock_engine = MagicMock()
            mock_engine.check_health.return_value = {'healthy': True, 'issues': []}
            mock_engine_class.return_value = mock_engine

            result = handle_orchestration_health()

            assert result is True
            mock_print.assert_called()


class TestCLIMain:
    """Test CLI main function and argument parsing."""

    @patch('sys.argv', ['codomyrmex', '--help'])
    @patch('argparse.ArgumentParser.print_help')
    def test_main_help(self, mock_print_help):
        """Test main function with help argument."""
        with pytest.raises(SystemExit):
            main()

        mock_print_help.assert_called_once()

    @patch('sys.argv', ['codomyrmex', 'check'])
    @patch('codomyrmex.cli.check_environment')
    def test_main_check_command(self, mock_check_env):
        """Test main function with check command."""
        main()

        mock_check_env.assert_called_once()

    @patch('sys.argv', ['codomyrmex', 'info'])
    @patch('codomyrmex.cli.show_info')
    def test_main_info_command(self, mock_show_info):
        """Test main function with info command."""
        main()

        mock_show_info.assert_called_once()

    @patch('sys.argv', ['codomyrmex', 'modules'])
    @patch('codomyrmex.cli.show_modules')
    def test_main_modules_command(self, mock_show_modules):
        """Test main function with modules command."""
        main()

        mock_show_modules.assert_called_once()

    @patch('sys.argv', ['codomyrmex', 'shell'])
    @patch('codomyrmex.cli.run_interactive_shell')
    def test_main_shell_command(self, mock_shell):
        """Test main function with shell command."""
        main()

        mock_shell.assert_called_once()

    @patch('sys.argv', ['codomyrmex', 'workflow', 'list'])
    @patch('codomyrmex.cli.list_workflows')
    def test_main_workflows_command(self, mock_list_workflows):
        """Test main function with workflows command."""
        main()

        mock_list_workflows.assert_called_once()

    @patch('sys.argv', ['codomyrmex', 'status'])
    @patch('codomyrmex.cli.show_system_status')
    def test_main_status_command(self, mock_status):
        """Test main function with status command."""
        main()

        mock_status.assert_called_once()

    @patch('sys.argv', ['codomyrmex', 'ai', 'generate', 'test prompt', '--language', 'python'])
    @patch('codomyrmex.cli.handle_ai_generate')
    def test_main_ai_generate_command(self, mock_generate):
        """Test main function with AI generate command."""
        mock_generate.return_value = True

        result = main()

        mock_generate.assert_called_once_with('test prompt', 'python', 'openai')

    @patch('sys.argv', ['codomyrmex', 'ai', 'refactor', 'test.py', 'optimize'])
    @patch('codomyrmex.cli.handle_ai_refactor')
    def test_main_ai_refactor_command(self, mock_refactor):
        """Test main function with AI refactor command."""
        mock_refactor.return_value = True

        result = main()

        mock_refactor.assert_called_once_with('test.py', 'optimize')

    @patch('sys.argv', ['codomyrmex', 'analyze', 'code', './src'])
    @patch('codomyrmex.cli.handle_code_analysis')
    def test_main_analyze_code_command(self, mock_analyze):
        """Test main function with code analysis command."""
        mock_analyze.return_value = True

        result = main()

        mock_analyze.assert_called_once_with('./src', None)

    @patch('sys.argv', ['codomyrmex', 'analyze', 'git', '--repo', './repo'])
    @patch('codomyrmex.cli.handle_git_analysis')
    def test_main_analyze_git_command(self, mock_analyze):
        """Test main function with git analysis command."""
        mock_analyze.return_value = True

        result = main()

        mock_analyze.assert_called_once_with('./repo')

    @patch('sys.argv', ['codomyrmex', 'build', 'project'])
    @patch('codomyrmex.cli.handle_project_build')
    def test_main_build_command(self, mock_build):
        """Test main function with build command."""
        mock_build.return_value = True

        result = main()

        mock_build.assert_called_once_with(None)

    @patch('sys.argv', ['codomyrmex', 'module', 'test', 'data_visualization'])
    @patch('codomyrmex.cli.handle_module_test')
    def test_main_test_command(self, mock_test):
        """Test main function with test command."""
        mock_test.return_value = True

        result = main()

        mock_test.assert_called_once_with('data_visualization')

    @patch('sys.argv', ['codomyrmex', 'module', 'demo', 'data_visualization'])
    @patch('codomyrmex.cli.handle_module_demo')
    def test_main_demo_command(self, mock_demo):
        """Test main function with demo command."""
        mock_demo.return_value = True

        result = main()

        mock_demo.assert_called_once_with('data_visualization')

    @patch('sys.argv', ['codomyrmex', 'workflow', 'create', 'my_workflow'])
    @patch('codomyrmex.cli.handle_workflow_create')
    def test_main_workflow_create_command(self, mock_create):
        """Test main function with workflow create command."""
        mock_create.return_value = True

        result = main()

        mock_create.assert_called_once_with('my_workflow', None)

    @patch('sys.argv', ['codomyrmex', 'project', 'create', 'my_project'])
    @patch('codomyrmex.cli.handle_project_create')
    def test_main_project_create_command(self, mock_create):
        """Test main function with project create command."""
        mock_create.return_value = True

        result = main()

        mock_create.assert_called_once()

    @patch('sys.argv', ['codomyrmex', 'project', 'list'])
    @patch('codomyrmex.cli.handle_project_list')
    def test_main_project_list_command(self, mock_list):
        """Test main function with project list command."""
        mock_list.return_value = True

        result = main()

        mock_list.assert_called_once()

    @patch('sys.argv', ['codomyrmex', 'orchestration', 'status'])
    @patch('codomyrmex.cli.handle_orchestration_status')
    def test_main_orchestration_status_command(self, mock_status):
        """Test main function with orchestration status command."""
        mock_status.return_value = True

        result = main()

        mock_status.assert_called_once()

    @patch('sys.argv', ['codomyrmex', 'orchestration', 'health'])
    @patch('codomyrmex.cli.handle_orchestration_health')
    def test_main_orchestration_health_command(self, mock_health):
        """Test main function with orchestration health command."""
        mock_health.return_value = True

        result = main()

        mock_health.assert_called_once()

    @patch('sys.argv', ['codomyrmex', 'invalid_command'])
    @patch('builtins.print')
    @patch('codomyrmex.cli.logger')
    def test_main_invalid_command(self, mock_logger, mock_print):
        """Test main function with invalid command."""
        result = main()

        # Should return False for invalid command
        assert result is False
        mock_logger.error.assert_called()


if __name__ == "__main__":
    pytest.main([__file__])
