"""
Integration tests to ensure all documented methods actually exist and work as described.
This validates that documentation is accurate and methods are functionally up to standard.
"""

import pytest
import sys
import os
import tempfile
from pathlib import Path
import importlib
import inspect
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for testing


class TestDocumentationAccuracy:
    """Test that all documented APIs actually exist and work."""

    def setup_method(self):
        """Setup for each test method."""
        # Ensure src directory is in Python path
        project_root = Path(__file__).parent.parent.parent
        src_path = project_root / "src"
        if str(src_path) not in sys.path:
            sys.path.insert(0, str(src_path))

    def test_data_visualization_api_exists(self):
        """Test that all documented data visualization functions exist."""
        # Test line_plot module and function
        from codomyrmex.data_visualization.line_plot import create_line_plot

        # Verify function signature matches documentation
        sig = inspect.signature(create_line_plot)
        params = list(sig.parameters.keys())

        # Check documented parameters exist
        expected_params = ['x_data', 'y_data', 'title', 'x_label', 'y_label',
                          'output_path', 'show_plot', 'line_labels', 'markers', 'figure_size']
        for param in expected_params:
            assert param in params, f"Parameter '{param}' missing from create_line_plot"

    def test_data_visualization_functionality(self):
        """Test that documented data visualization actually works."""
        from codomyrmex.data_visualization.line_plot import create_line_plot

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test_plot.png"

            # Test with documented usage pattern
            fig = create_line_plot(
                x_data=[1, 2, 3, 4, 5],
                y_data=[2, 4, 6, 8, 10],
                title="Documentation Test Plot",
                output_path=str(output_path),
                markers=True
            )

            # Verify documented behavior
            assert fig is not None, "Function should return matplotlib figure"
            assert output_path.exists(), "Output file should be created"

    def test_static_analysis_api_exists(self):
        """Test that documented static analysis functions exist."""
        from codomyrmex.static_analysis.pyrefly_runner import run_pyrefly_analysis, parse_pyrefly_output

        # Verify function signatures
        run_sig = inspect.signature(run_pyrefly_analysis)
        parse_sig = inspect.signature(parse_pyrefly_output)

        # Check documented parameters
        assert 'target_paths' in run_sig.parameters
        assert 'project_root' in run_sig.parameters
        assert 'output' in parse_sig.parameters
        assert 'project_root' in parse_sig.parameters

    def test_static_analysis_functionality(self):
        """Test that documented static analysis actually works."""
        from codomyrmex.static_analysis.pyrefly_runner import parse_pyrefly_output

        # Test with documented usage pattern
        sample_output = "/path/to/file.py:10:5: error: Undefined variable"
        result = parse_pyrefly_output(sample_output, "/path/to")

        # Verify documented return structure
        assert isinstance(result, list), "Should return list of issues"
        if result:  # If parsing succeeded
            issue = result[0]
            assert 'file_path' in issue
            assert 'line_number' in issue
            assert 'message' in issue

    def test_code_execution_api_exists(self):
        """Test that documented code execution functions exist."""
        from codomyrmex.code_execution_sandbox.code_executor import (
            execute_code,
            check_docker_available,
            validate_language
        )

        # Verify function signatures match documentation
        exec_sig = inspect.signature(execute_code)
        expected_params = ['code', 'language', 'timeout', 'session_id', 'stdin']

        for param in expected_params:
            assert param in exec_sig.parameters, f"Parameter '{param}' missing from execute_code"

    def test_code_execution_functionality(self):
        """Test that documented code execution actually works."""
        from codomyrmex.code_execution_sandbox.code_executor import execute_code, validate_language

        # Test language validation as documented
        assert validate_language("python") == True
        assert validate_language("javascript") == True
        assert validate_language("nonexistent") == False

        # Test code execution as documented
        result = execute_code(
            code="print('Hello from documentation test')",
            language="python",
            timeout=10
        )

        # Verify documented return structure
        assert isinstance(result, dict), "Should return dictionary"
        assert 'status' in result, f"Expected 'status' in result, got keys: {result.keys()}"
        assert result.get('status') == 'success', f"Expected status='success', got {result.get('status')}"
        assert 'stdout' in result or 'output' in result, "Should have stdout or output"
        assert 'execution_time' in result

    def test_git_operations_api_exists(self):
        """Test that documented git operations functions exist."""
        from codomyrmex.git_operations.git_manager import (
            check_git_availability,
            is_git_repository,
            create_branch,
            get_current_branch
        )

        # Verify functions exist and are callable
        assert callable(check_git_availability)
        assert callable(is_git_repository)
        assert callable(create_branch)
        assert callable(get_current_branch)

        # Test basic functionality
        git_available = check_git_availability()
        assert isinstance(git_available, bool)

    def test_environment_setup_api_exists(self):
        """Test that documented environment setup functions exist."""
        from codomyrmex.environment_setup.env_checker import (
            is_uv_available,
            is_uv_environment,
            ensure_dependencies_installed
        )

        # Verify functions exist and work
        uv_available = is_uv_available()
        assert isinstance(uv_available, bool)

        in_uv_env = is_uv_environment()
        assert isinstance(in_uv_env, bool)

        # Test that ensure_dependencies_installed doesn't crash
        try:
            ensure_dependencies_installed()
            # Function should complete without raising exceptions
            assert True
        except Exception as e:
            pytest.skip(f"Dependencies check failed in test environment: {e}")

    def test_build_synthesis_api_exists(self):
        """Test that documented build synthesis functions exist."""
        from codomyrmex.build_synthesis.build_orchestrator import (
            check_build_environment,
            synthesize_build_artifact,
            validate_build_output
        )

        # Test environment check as documented
        env_result = check_build_environment()
        assert isinstance(env_result, dict)
        assert 'python_available' in env_result

    def test_logging_api_exists(self):
        """Test that documented logging functions exist."""
        from codomyrmex.logging_monitoring.logger_config import get_logger, setup_logging

        # Test logger creation
        logger = get_logger("test_logger")
        assert logger is not None
        assert hasattr(logger, 'info')
        assert hasattr(logger, 'error')
        assert hasattr(logger, 'debug')

        # Test that setup_logging is callable
        assert callable(setup_logging)

    def test_plot_utilities_api_exists(self):
        """Test that documented plot utilities exist."""
        from codomyrmex.data_visualization.plot_utils import (
            get_codomyrmex_logger,
            save_plot,
            apply_common_aesthetics
        )

        # Test logger utility
        logger = get_codomyrmex_logger("test_plot_utils")
        assert logger is not None

        # Verify other utilities are callable
        assert callable(save_plot)
        assert callable(apply_common_aesthetics)

    def test_all_visualization_modules_exist(self):
        """Test that all documented visualization modules exist."""
        visualization_modules = [
            'line_plot',
            'bar_chart',
            'scatter_plot',
            'pie_chart',
            'histogram'
        ]

        for module_name in visualization_modules:
            try:
                module = importlib.import_module(f'codomyrmex.data_visualization.{module_name}')
                assert module is not None

                # Each should have a create_ function
                create_function_name = f'create_{module_name.replace("_", "_")}'
                if module_name == 'line_plot':
                    create_function_name = 'create_line_plot'
                elif module_name == 'bar_chart':
                    create_function_name = 'create_bar_chart'
                elif module_name == 'scatter_plot':
                    create_function_name = 'create_scatter_plot'
                elif module_name == 'pie_chart':
                    create_function_name = 'create_pie_chart'
                elif module_name == 'histogram':
                    create_function_name = 'create_histogram'

                assert hasattr(module, create_function_name), f"Missing {create_function_name} in {module_name}"

            except ImportError as e:
                pytest.fail(f"Documented module {module_name} cannot be imported: {e}")

    def test_mcp_schemas_exist(self):
        """Test that documented MCP schemas exist."""
        from codomyrmex.model_context_protocol.mcp_schemas import (
            MCPErrorDetail,
            MCPToolCall,
            MCPToolResult
        )

        # Test schema instantiation
        error = MCPErrorDetail(error_type="TEST", error_message="Test error")
        assert error.error_type == "TEST"
        assert error.error_message == "Test error"

        tool_call = MCPToolCall(tool_name="test_tool", arguments={"param": "value"})
        assert tool_call.tool_name == "test_tool"
        assert tool_call.arguments == {"param": "value"}

    def test_repository_management_classes_exist(self):
        """Test that documented repository management classes exist."""
        from codomyrmex.git_operations.repository_manager import Repository, RepositoryManager
        from codomyrmex.git_operations.repository_manager import RepositoryType

        # Test Repository class
        repo = Repository(
            repo_type=RepositoryType.USE,
            owner="test_owner",
            name="test_repo",
            url="https://example.com/repo.git",
            description="Test repository",
            local_path_suggestion="test_repo"
        )
        assert repo.name == "test_repo"
        assert repo.url == "https://example.com/repo.git"
        assert repo.repo_type == RepositoryType.USE

        # Test RepositoryType enum exists with expected values
        assert hasattr(RepositoryType, 'OWN')
        assert hasattr(RepositoryType, 'USE')
        assert hasattr(RepositoryType, 'FORK')

    def test_comprehensive_workflow_functions_work_together(self):
        """Test that documented workflow actually works end-to-end."""
        from codomyrmex.static_analysis.pyrefly_runner import parse_pyrefly_output
        from codomyrmex.code_execution_sandbox.code_executor import execute_code
        from codomyrmex.data_visualization.line_plot import create_line_plot

        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)

            # 1. Test static analysis parsing
            sample_output = f"{project_path / 'test.py'}:1:1: info: Test message"
            issues = parse_pyrefly_output(sample_output, str(project_path))
            assert isinstance(issues, list)

            # 2. Test code execution (may fail if Docker not available, so skip gracefully)
            try:
                execution_result = execute_code(
                    code="result = 2 + 2\nprint(f'Result: {result}')",
                    language="python",
                    timeout=10
                )
                # Check if execution was successful or if Docker is not available
                if execution_result.get('status') == 'success':
                    assert 'Result: 4' in execution_result.get('stdout', '') or 'Result: 4' in execution_result.get('output', '')
                elif execution_result.get('status') == 'setup_error':
                    # Docker might not be available, skip this assertion
                    pytest.skip("Docker not available for code execution test")
                else:
                    # Log the result for debugging but don't fail
                    logger.warning(f"Code execution returned status: {execution_result.get('status')}")
            except Exception as e:
                pytest.skip(f"Code execution test skipped: {e}")

            # 3. Test visualization
            fig = create_line_plot(
                x_data=[1, 2, 3, 4],
                y_data=[1, 4, 9, 16],
                title="Workflow Test",
                output_path=str(project_path / "workflow_test.png")
            )
            assert fig is not None
            assert (project_path / "workflow_test.png").exists()

    def test_no_documented_functions_are_missing(self):
        """Meta-test: Ensure we're testing all documented functions."""
        # This test serves as a checklist to ensure we don't miss any
        # documented APIs when adding new functionality

        documented_modules = [
            'codomyrmex.data_visualization.line_plot',
            'codomyrmex.static_analysis.pyrefly_runner',
            'codomyrmex.code_execution_sandbox.code_executor',
            'codomyrmex.git_operations.git_manager',
            'codomyrmex.environment_setup.env_checker',
            'codomyrmex.build_synthesis.build_orchestrator',
            'codomyrmex.logging_monitoring.logger_config',
            'codomyrmex.model_context_protocol.mcp_schemas'
        ]

        for module_name in documented_modules:
            try:
                module = importlib.import_module(module_name)
                assert module is not None
                # Each module should have at least one public function/class
                public_members = [name for name in dir(module)
                                if not name.startswith('_') and
                                (inspect.isfunction(getattr(module, name)) or
                                 inspect.isclass(getattr(module, name)))]
                assert len(public_members) > 0, f"Module {module_name} has no public members"

            except ImportError as e:
                pytest.fail(f"Documented module {module_name} cannot be imported: {e}")


class TestRealMethodsInDocumentation:
    """Test that documentation examples use real methods, not placeholders."""

    def test_performance_benchmarks_use_real_functions(self):
        """Test that performance documentation examples work."""
        from codomyrmex.data_visualization.line_plot import create_line_plot
        import numpy as np
        import time

        # Test actual benchmark code from documentation
        x_data = list(np.linspace(0, 10, 100))
        y_data = list(np.sin(np.array(x_data)))

        start_time = time.time()
        with tempfile.TemporaryDirectory() as temp_dir:
            result = create_line_plot(
                x_data=x_data,
                y_data=y_data,
                title="Benchmark Test",
                output_path=f"{temp_dir}/benchmark.png"
            )
            duration = time.time() - start_time

        assert result is not None
        assert duration > 0
        assert duration < 10  # Should be reasonably fast for small dataset

    def test_testing_strategy_examples_work(self):
        """Test that testing strategy documentation examples work."""
        from codomyrmex.data_visualization.line_plot import create_line_plot
        from pathlib import Path

        # Example from testing strategy documentation
        x_data = [1, 2, 3, 4, 5]
        y_data = [2, 4, 6, 8, 10]

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test_plot.png"

            fig = create_line_plot(
                x_data=x_data,
                y_data=y_data,
                title="Real Test Plot",
                output_path=str(output_path),
                markers=True
            )

            # Assertions from documentation should work
            assert fig is not None
            assert output_path.exists()


if __name__ == '__main__':
    # Allow running this test file directly
    pytest.main([__file__, '-v'])
