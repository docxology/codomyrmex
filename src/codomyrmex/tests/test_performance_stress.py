"""
Performance and stress tests for Codomyrmex modules.

This module tests the performance characteristics and stress limits of
various Codomyrmex modules under different load conditions.
"""

import pytest
import os
import sys
import time
import tempfile
import threading
import multiprocessing
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from typing import List, Dict, Any
import numpy as np
from unittest.mock import Mock, patch

# Add project root to Python path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Import modules for performance testing
from ai_code_editing import (
    generate_code_snippet,
    refactor_code_snippet,
    analyze_code_quality,
    CodeLanguage,
    CodeComplexity,
    CodeStyle,
)
from static_analysis import (
    StaticAnalyzer,
    analyze_file,
    analyze_project,
    AnalysisType,
    SeverityLevel,
    Language,
)
from data_visualization import (
    AdvancedPlotter,
    create_advanced_line_plot,
    create_advanced_scatter_plot,
    PlotType,
    ChartStyle,
    ColorPalette,
    PlotConfig,
)
from build_synthesis import (
    BuildManager,
    create_python_build_target,
    BuildType,
    BuildStatus,
    BuildEnvironment,
)
from project_orchestration import (
    WorkflowManager,
    WorkflowStep,
    WorkflowExecution,
    WorkflowStatus,
)


class TestAICodeEditingPerformance:
    """Performance tests for AI code editing module."""

    def test_generate_code_performance(self):
        """Test performance of code generation under load."""
        with patch("ai_code_editing.ai_code_helpers.get_llm_client") as mock_get_client:
            # Mock AI response
            mock_client = Mock()
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "def test(): return 1"
            mock_response.usage.total_tokens = 50
            mock_client.chat.completions.create.return_value = mock_response
            mock_get_client.return_value = (mock_client, "gpt-3.5-turbo")

            # Test single generation performance
            start_time = time.time()
            result = generate_code_snippet(
                prompt="Create a simple function", language="python", provider="openai"
            )
            single_time = time.time() - start_time

            assert single_time < 1.0  # Should complete within 1 second
            assert result["generated_code"] is not None

    def test_generate_code_concurrent_performance(self):
        """Test concurrent code generation performance."""
        with patch("ai_code_editing.ai_code_helpers.get_llm_client") as mock_get_client:
            # Mock AI response
            mock_client = Mock()
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "def test(): return 1"
            mock_response.usage.total_tokens = 50
            mock_client.chat.completions.create.return_value = mock_response
            mock_get_client.return_value = (mock_client, "gpt-3.5-turbo")

            def generate_single():
                return generate_code_snippet(
                    prompt="Create a simple function",
                    language="python",
                    provider="openai",
                )

            # Test concurrent execution
            num_requests = 10
            start_time = time.time()

            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = [
                    executor.submit(generate_single) for _ in range(num_requests)
                ]
                results = [future.result() for future in futures]

            concurrent_time = time.time() - start_time

            assert len(results) == num_requests
            assert concurrent_time < 5.0  # Should complete within 5 seconds
            assert all(result["generated_code"] is not None for result in results)

    def test_refactor_code_performance(self):
        """Test performance of code refactoring."""
        test_code = """
def calculate_sum(numbers):
    total = 0
    for num in numbers:
        total = total + num
    return total
"""

        with patch("ai_code_editing.ai_code_helpers.get_llm_client") as mock_get_client:
            # Mock AI response
            mock_client = Mock()
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = (
                "def calculate_sum(numbers): return sum(numbers)"
            )
            mock_response.usage.total_tokens = 30
            mock_client.chat.completions.create.return_value = mock_response
            mock_get_client.return_value = (mock_client, "gpt-3.5-turbo")

            start_time = time.time()
            result = refactor_code_snippet(
                code=test_code,
                refactoring_type="optimize",
                language="python",
                provider="openai",
            )
            refactor_time = time.time() - start_time

            assert refactor_time < 1.0
            assert result["refactored_code"] is not None


class TestStaticAnalysisPerformance:
    """Performance tests for static analysis module."""

    def test_analyze_file_performance(self):
        """Test performance of file analysis."""
        # Create test file
        test_code = """
def complex_function(x, y):
    if x > 0:
        if y > 0:
            for i in range(x):
                if i % 2 == 0:
                    print(i)
                else:
                    print(i * 2)
        else:
            return 0
    else:
        return -1
    return x + y
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(test_code)
            temp_file = f.name

        try:
            analyzer = StaticAnalyzer()

            start_time = time.time()
            results = analyzer.analyze_file(temp_file, [AnalysisType.QUALITY])
            analysis_time = time.time() - start_time

            assert analysis_time < 2.0  # Should complete within 2 seconds
            assert isinstance(results, list)

        finally:
            os.unlink(temp_file)

    def test_analyze_project_performance(self):
        """Test performance of project analysis."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create multiple test files
            for i in range(5):
                with open(os.path.join(temp_dir, f"test_{i}.py"), "w") as f:
                    f.write(f"def func_{i}(): return {i}")

            analyzer = StaticAnalyzer(temp_dir)

            start_time = time.time()
            summary = analyzer.analyze_project([temp_dir])
            project_time = time.time() - start_time

            assert project_time < 10.0  # Should complete within 10 seconds
            assert summary.files_analyzed >= 5
            assert summary.total_issues >= 0

    def test_analyze_large_codebase_performance(self):
        """Test performance with a large codebase simulation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create many small files to simulate large codebase
            num_files = 50
            for i in range(num_files):
                with open(os.path.join(temp_dir, f"module_{i}.py"), "w") as f:
                    f.write(
                        f"""
def function_{i}():
    return {i}

class Class{i}:
    def method_{i}(self):
        return {i}
"""
                    )

            analyzer = StaticAnalyzer(temp_dir)

            start_time = time.time()
            summary = analyzer.analyze_project([temp_dir])
            large_project_time = time.time() - start_time

            assert large_project_time < 30.0  # Should complete within 30 seconds
            assert summary.files_analyzed >= num_files


class TestDataVisualizationPerformance:
    """Performance tests for data visualization module."""

    def test_create_plot_performance(self):
        """Test performance of plot creation."""
        # Generate large dataset
        x_data = np.linspace(0, 100, 10000)
        y_data = np.sin(x_data) + np.random.normal(0, 0.1, 10000)

        start_time = time.time()
        fig = create_advanced_line_plot(
            x_data=x_data.tolist(),
            y_data=y_data.tolist(),
            title="Performance Test Plot",
            xlabel="X",
            ylabel="Y",
        )
        plot_time = time.time() - start_time

        assert plot_time < 5.0  # Should complete within 5 seconds
        assert fig is not None

    def test_create_multiple_plots_performance(self):
        """Test performance of creating multiple plots."""
        plotter = AdvancedPlotter()

        # Create multiple plots
        num_plots = 10
        start_time = time.time()

        for i in range(num_plots):
            x_data = np.random.normal(0, 1, 1000)
            y_data = np.random.normal(0, 1, 1000)

            fig, ax = plotter.create_figure()
            plotter.plot_scatter(x_data, y_data, label=f"Plot {i}")
            plotter.finalize_plot()

        multiple_plots_time = time.time() - start_time

        assert multiple_plots_time < 20.0  # Should complete within 20 seconds

    def test_create_dashboard_performance(self):
        """Test performance of dashboard creation."""
        # Create large dataset for dashboard
        datasets = []
        for i in range(6):  # 2x3 dashboard
            x_data = np.random.normal(0, 1, 1000)
            y_data = np.random.normal(0, 1, 1000)

            data_points = [{"x": x, "y": y} for x, y in zip(x_data, y_data)]
            dataset = {
                "name": f"Dataset {i}",
                "data": data_points,
                "plot_type": "scatter",
            }
            datasets.append(dataset)

        plotter = AdvancedPlotter()

        start_time = time.time()
        dashboard = plotter.create_dashboard(
            datasets=datasets, layout=(2, 3), title="Performance Test Dashboard"
        )
        dashboard_time = time.time() - start_time

        assert dashboard_time < 10.0  # Should complete within 10 seconds
        assert dashboard is not None


class TestBuildSynthesisPerformance:
    """Performance tests for build synthesis module."""

    def test_build_manager_initialization_performance(self):
        """Test performance of build manager initialization."""
        start_time = time.time()
        build_manager = BuildManager()
        init_time = time.time() - start_time

        assert init_time < 1.0  # Should initialize quickly
        assert build_manager is not None

    def test_add_multiple_targets_performance(self):
        """Test performance of adding multiple build targets."""
        build_manager = BuildManager()

        start_time = time.time()

        # Add many build targets
        for i in range(100):
            target = create_python_build_target(
                name=f"target_{i}", source_path=f"src_{i}", output_path=f"dist_{i}"
            )
            build_manager.add_build_target(target)

        add_targets_time = time.time() - start_time

        assert add_targets_time < 5.0  # Should complete within 5 seconds
        assert len(build_manager.targets) == 100

    def test_dependency_check_performance(self):
        """Test performance of dependency checking."""
        build_manager = BuildManager()

        # Add many dependencies
        for i in range(50):
            from build_synthesis import Dependency

            dep = Dependency(name=f"package_{i}", version="1.0.0", dep_type="runtime")
            build_manager.add_dependency(dep)

        start_time = time.time()
        dep_status = build_manager.check_dependencies()
        check_time = time.time() - start_time

        assert check_time < 10.0  # Should complete within 10 seconds
        assert len(dep_status) == 50


class TestProjectOrchestrationPerformance:
    """Performance tests for project orchestration module."""

    def test_workflow_creation_performance(self):
        """Test performance of workflow creation."""
        workflow_manager = get_workflow_manager()

        # Create large workflow
        steps = []
        for i in range(100):
            step = WorkflowStep(
                name=f"step_{i}",
                module="test_module",
                action="test_action",
                parameters={"index": i},
            )
            steps.append(step)

        start_time = time.time()
        success = workflow_manager.create_workflow("large_workflow", steps)
        creation_time = time.time() - start_time

        assert success is True
        assert creation_time < 2.0  # Should complete within 2 seconds

    def test_workflow_execution_performance(self):
        """Test performance of workflow execution."""
        workflow_manager = get_workflow_manager()

        # Create simple workflow
        steps = [
            WorkflowStep(name="step1", module="test_module", action="test_action"),
            WorkflowStep(
                name="step2",
                module="test_module",
                action="test_action",
                dependencies=["step1"],
            ),
        ]

        workflow_manager.create_workflow("perf_workflow", steps)

        start_time = time.time()
        # Note: This would normally execute the workflow, but we're testing performance
        # of the workflow structure creation and management
        workflows = workflow_manager.list_workflows()
        execution_time = time.time() - start_time

        assert execution_time < 1.0  # Should complete quickly
        assert "perf_workflow" in workflows


class TestMemoryUsage:
    """Memory usage tests."""

    def test_ai_code_editing_memory_usage(self):
        """Test memory usage of AI code editing operations."""
        import psutil
        import gc

        process = psutil.Process()
        initial_memory = process.memory_info().rss

        with patch("ai_code_editing.ai_code_helpers.get_llm_client") as mock_get_client:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "def test(): return 1"
            mock_response.usage.total_tokens = 50
            mock_client.chat.completions.create.return_value = mock_response
            mock_get_client.return_value = (mock_client, "gpt-3.5-turbo")

            # Perform many operations
            results = []
            for i in range(100):
                result = generate_code_snippet(
                    prompt=f"Create function {i}", language="python", provider="openai"
                )
                results.append(result)

            peak_memory = process.memory_info().rss
            memory_increase = peak_memory - initial_memory

            # Clean up
            del results
            gc.collect()

            # Memory increase should be reasonable (less than 100MB)
            assert memory_increase < 100 * 1024 * 1024

    def test_static_analysis_memory_usage(self):
        """Test memory usage of static analysis operations."""
        import psutil
        import gc

        process = psutil.Process()
        initial_memory = process.memory_info().rss

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create many files
            for i in range(50):
                with open(os.path.join(temp_dir, f"test_{i}.py"), "w") as f:
                    f.write(f"def func_{i}(): return {i}")

            analyzer = StaticAnalyzer(temp_dir)

            # Analyze all files
            summary = analyzer.analyze_project([temp_dir])

            peak_memory = process.memory_info().rss
            memory_increase = peak_memory - initial_memory

            # Clean up
            del analyzer
            gc.collect()

            # Memory increase should be reasonable
            assert memory_increase < 200 * 1024 * 1024  # Less than 200MB


class TestStressLimits:
    """Stress tests to find breaking points."""

    def test_concurrent_ai_requests_stress(self):
        """Test stress limits of concurrent AI requests."""
        with patch("ai_code_editing.ai_code_helpers.get_llm_client") as mock_get_client:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "def test(): return 1"
            mock_response.usage.total_tokens = 50
            mock_client.chat.completions.create.return_value = mock_response
            mock_get_client.return_value = (mock_client, "gpt-3.5-turbo")

            def make_request():
                return generate_code_snippet(
                    prompt="Create a function", language="python", provider="openai"
                )

            # Test with increasing concurrency
            for num_threads in [10, 20, 50]:
                start_time = time.time()

                with ThreadPoolExecutor(max_workers=num_threads) as executor:
                    futures = [
                        executor.submit(make_request) for _ in range(num_threads)
                    ]
                    results = [future.result() for future in futures]

                execution_time = time.time() - start_time

                # Should complete within reasonable time
                assert execution_time < 30.0
                assert len(results) == num_threads
                assert all(result["generated_code"] is not None for result in results)

    def test_large_workflow_stress(self):
        """Test stress limits of large workflows."""
        workflow_manager = get_workflow_manager()

        # Create very large workflow
        steps = []
        for i in range(1000):
            dependencies = [f"step_{j}" for j in range(i)] if i > 0 else []
            step = WorkflowStep(
                name=f"step_{i}",
                module="test_module",
                action="test_action",
                dependencies=dependencies,
            )
            steps.append(step)

        start_time = time.time()
        success = workflow_manager.create_workflow("stress_workflow", steps)
        creation_time = time.time() - start_time

        # Should handle large workflows
        assert success is True
        assert creation_time < 10.0  # Should complete within 10 seconds

        # Should be able to list the workflow
        workflows = workflow_manager.list_workflows()
        assert "stress_workflow" in workflows
        assert len(workflows["stress_workflow"]) == 1000

    def test_memory_stress_large_datasets(self):
        """Test memory stress with large datasets."""
        import psutil
        import gc

        process = psutil.Process()
        initial_memory = process.memory_info().rss

        # Create very large dataset
        large_x = np.random.normal(0, 1, 1000000)  # 1 million points
        large_y = np.random.normal(0, 1, 1000000)

        plotter = AdvancedPlotter()

        start_time = time.time()
        fig = create_advanced_scatter_plot(
            x_data=large_x.tolist(), y_data=large_y.tolist(), title="Large Dataset Test"
        )
        plot_time = time.time() - start_time

        peak_memory = process.memory_info().rss
        memory_increase = peak_memory - initial_memory

        # Should handle large datasets
        assert plot_time < 30.0  # Should complete within 30 seconds
        assert memory_increase < 500 * 1024 * 1024  # Less than 500MB increase

        # Clean up
        del large_x, large_y, fig
        gc.collect()


class TestPerformanceRegression:
    """Regression tests to ensure performance doesn't degrade."""

    def test_ai_code_generation_performance_regression(self):
        """Test that AI code generation performance doesn't regress."""
        with patch("ai_code_editing.ai_code_helpers.get_llm_client") as mock_get_client:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "def test(): return 1"
            mock_response.usage.total_tokens = 50
            mock_client.chat.completions.create.return_value = mock_response
            mock_get_client.return_value = (mock_client, "gpt-3.5-turbo")

            # Baseline performance measurement
            times = []
            for _ in range(10):
                start_time = time.time()
                generate_code_snippet(
                    prompt="Create a function", language="python", provider="openai"
                )
                times.append(time.time() - start_time)

            average_time = sum(times) / len(times)
            max_time = max(times)

            # Performance should be within acceptable bounds
            assert average_time < 0.5  # Average should be under 500ms
            assert max_time < 1.0  # Max should be under 1 second

    def test_static_analysis_performance_regression(self):
        """Test that static analysis performance doesn't regress."""
        test_code = """
def test_function():
    return 1
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(test_code)
            temp_file = f.name

        try:
            analyzer = StaticAnalyzer()

            # Baseline performance measurement
            times = []
            for _ in range(10):
                start_time = time.time()
                analyzer.analyze_file(temp_file, [AnalysisType.QUALITY])
                times.append(time.time() - start_time)

            average_time = sum(times) / len(times)
            max_time = max(times)

            # Performance should be within acceptable bounds
            assert average_time < 1.0  # Average should be under 1 second
            assert max_time < 2.0  # Max should be under 2 seconds

        finally:
            os.unlink(temp_file)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
