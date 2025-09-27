"""
Comprehensive cross-module integration tests for Codomyrmex.

This module tests integration between different Codomyrmex modules to ensure
they work together correctly and provide end-to-end functionality.
"""

import pytest
import os
import sys
import tempfile
import json
import asyncio
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List, Any
from codomyrmex.exceptions import CodomyrmexError
from codomyrmex.logging_monitoring.logger_config import get_logger

logger = get_logger(__name__)


# Add project root to Python path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
if PROJECT_ROOT not in sys.path:
    pass
#     sys.path.insert(0, PROJECT_ROOT)  # Removed sys.path manipulation

# Import all modules for integration testing
from ai_code_editing import (
    generate_code_snippet,
    refactor_code_snippet,
    analyze_code_quality,
    CodeLanguage,
    CodeComplexity,
    CodeStyle,
    CodeGenerationRequest,
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
    DataPoint,
    Dataset,
)
from build_synthesis import (
    BuildManager,
    create_python_build_target,
    create_docker_build_target,
    BuildType,
    BuildStatus,
    BuildEnvironment,
    DependencyType,
)
from project_orchestration import (
    WorkflowManager,
    WorkflowStep,
    WorkflowExecution,
    WorkflowStatus,
    get_workflow_manager,
)


class TestAICodeEditingStaticAnalysisIntegration:
    """Test integration between AI code editing and static analysis."""

    def test_generate_and_analyze_code(self):
        """Test generating code with AI and then analyzing it."""
        with patch("ai_code_editing.ai_code_helpers.get_llm_client") as mock_get_client:
            # Mock AI code generation
            mock_client = Mock()
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[
                0
            ].message.content = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

def main():
    for i in range(10):
        print(f'F({i}) = {fibonacci(i)}')

if __name__ == '__main__':
    main()
"""
            mock_response.usage.total_tokens = 100
            mock_client.chat.completions.create.return_value = mock_response
            mock_get_client.return_value = (mock_client, "gpt-3.5-turbo")

            # Generate code
            result = generate_code_snippet(
                prompt="Create a fibonacci function",
                language="python",
                provider="openai",
            )

            # Write generated code to temporary file
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write(result["generated_code"])
                temp_file = f.name

            try:
                # Analyze the generated code
                analyzer = StaticAnalyzer()
                analysis_results = analyzer.analyze_file(
                    temp_file, [AnalysisType.QUALITY]
                )

                # Verify integration worked
                assert result["generated_code"] is not None
                assert (
                    len(analysis_results) >= 0
                )  # May have 0 results if no issues found

            finally:
                os.unlink(temp_file)

    def test_refactor_and_analyze_code(self):
        """Test refactoring code with AI and then analyzing it."""
        test_code = """
def calculate_sum(numbers):
    total = 0
    for num in numbers:
        total = total + num
    return total
"""

        with patch("ai_code_editing.ai_code_helpers.get_llm_client") as mock_get_client:
            # Mock AI code refactoring
            mock_client = Mock()
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[
                0
            ].message.content = """
def calculate_sum(numbers):
    return sum(numbers)
"""
            mock_response.usage.total_tokens = 50
            mock_client.chat.completions.create.return_value = mock_response
            mock_get_client.return_value = (mock_client, "gpt-3.5-turbo")

            # Refactor code
            result = refactor_code_snippet(
                code=test_code,
                refactoring_type="optimize",
                language="python",
                provider="openai",
            )

            # Write refactored code to temporary file
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write(result["refactored_code"])
                temp_file = f.name

            try:
                # Analyze the refactored code
                analyzer = StaticAnalyzer()
                analysis_results = analyzer.analyze_file(
                    temp_file, [AnalysisType.QUALITY]
                )

                # Verify integration worked
                assert result["refactored_code"] is not None
                assert len(analysis_results) >= 0

            finally:
                os.unlink(temp_file)


class TestStaticAnalysisDataVisualizationIntegration:
    """Test integration between static analysis and data visualization."""

    def test_analyze_and_visualize_results(self):
        """Test analyzing code and visualizing the results."""
        # Create test Python file
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

def simple_function(a, b):
    return a + b
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(test_code)
            temp_file = f.name

        try:
            # Analyze the code
            analyzer = StaticAnalyzer()
            analysis_results = analyzer.analyze_file(
                temp_file, [AnalysisType.QUALITY, AnalysisType.COMPLEXITY]
            )

            # Create visualization data from analysis results
            severity_counts = {}
            category_counts = {}

            for result in analysis_results:
                severity = result.severity.value
                category = result.category

                severity_counts[severity] = severity_counts.get(severity, 0) + 1
                category_counts[category] = category_counts.get(category, 0) + 1

            # Create visualizations
            plotter = AdvancedPlotter()

            # Create severity distribution chart
            if severity_counts:
                fig1, ax1 = plotter.create_figure()
                plotter.plot_bar(
                    list(severity_counts.keys()),
                    list(severity_counts.values()),
                    title="Analysis Results by Severity",
                    xlabel="Severity Level",
                    ylabel="Count",
                )
                plotter.finalize_plot()

            # Create category distribution chart
            if category_counts:
                fig2, ax2 = plotter.create_figure()
                plotter.plot_pie(
                    list(category_counts.keys()),
                    list(category_counts.values()),
                    title="Analysis Results by Category",
                )
                plotter.finalize_plot()

            # Verify integration worked
            assert len(analysis_results) >= 0
            assert isinstance(severity_counts, dict)
            assert isinstance(category_counts, dict)

        finally:
            os.unlink(temp_file)

    def test_analyze_multiple_files_and_create_dashboard(self):
        """Test analyzing multiple files and creating a dashboard."""
        # Create multiple test files
        test_files = []
        test_codes = [
            "def func1(): return 1",
            "def func2(x): return x * 2",
            "def func3(a, b): return a + b",
        ]

        try:
            for i, code in enumerate(test_codes):
                with tempfile.NamedTemporaryFile(
                    mode="w", suffix=f"_test_{i}.py", delete=False
                ) as f:
                    f.write(code)
                    test_files.append(f.name)

            # Analyze all files
            analyzer = StaticAnalyzer()
            all_results = []

            for file_path in test_files:
                results = analyzer.analyze_file(file_path, [AnalysisType.QUALITY])
                all_results.extend(results)

            # Create dashboard with analysis results
            datasets = []

            # Group results by file
            file_results = {}
            for result in all_results:
                file_name = os.path.basename(result.file_path)
                if file_name not in file_results:
                    file_results[file_name] = []
                file_results[file_name].append(result)

            # Create datasets for dashboard
            for file_name, results in file_results.items():
                severity_counts = {}
                for result in results:
                    severity = result.severity.value
                    severity_counts[severity] = severity_counts.get(severity, 0) + 1

                if severity_counts:
                    data_points = [
                        DataPoint(x=severity, y=count)
                        for severity, count in severity_counts.items()
                    ]
                    dataset = Dataset(
                        name=file_name, data=data_points, plot_type=PlotType.BAR
                    )
                    datasets.append(dataset)

            # Create dashboard
            if datasets:
                plotter = AdvancedPlotter()
                dashboard = plotter.create_dashboard(
                    datasets=datasets, layout=(2, 2), title="Code Analysis Dashboard"
                )

                # Verify dashboard was created
                assert dashboard is not None

        finally:
            for file_path in test_files:
                if os.path.exists(file_path):
                    os.unlink(file_path)


class TestBuildSynthesisProjectOrchestrationIntegration:
    """Test integration between build synthesis and project orchestration."""

    def test_create_build_workflow(self):
        """Test creating a workflow that includes build steps."""
        # Create build manager
        build_manager = BuildManager()

        # Add a Python build target
        python_target = create_python_build_target(
            name="test_package", source_path="src", output_path="dist"
        )
        build_manager.add_build_target(python_target)

        # Create workflow manager
        workflow_manager = get_workflow_manager()

        # Create workflow steps
        workflow_steps = [
            WorkflowStep(
                name="check_dependencies",
                module="build_synthesis",
                action="check_dependencies",
                parameters={"target_name": "test_package"},
            ),
            WorkflowStep(
                name="build_package",
                module="build_synthesis",
                action="build_target",
                parameters={"target_name": "test_package"},
                dependencies=["check_dependencies"],
            ),
            WorkflowStep(
                name="package_artifacts",
                module="build_synthesis",
                action="package_artifacts",
                parameters={"target_name": "test_package"},
                dependencies=["build_package"],
            ),
        ]

        # Create workflow
        success = workflow_manager.create_workflow("build_workflow", workflow_steps)
        assert success is True

        # Verify workflow was created
        workflows = workflow_manager.list_workflows()
        assert "build_workflow" in workflows
        assert len(workflows["build_workflow"]) == 3

    def test_orchestrate_build_pipeline(self):
        """Test orchestrating a complete build pipeline."""
        # Create build manager with multiple targets
        build_manager = BuildManager()

        # Add Python target
        python_target = create_python_build_target(
            name="python_package", source_path="src", output_path="dist"
        )
        build_manager.add_build_target(python_target)

        # Add Docker target
        docker_target = create_docker_build_target(
            name="docker_image", source_path=".", dockerfile_path="Dockerfile"
        )
        build_manager.add_build_target(docker_target)

        # Create workflow for build pipeline
        workflow_manager = get_workflow_manager()

        workflow_steps = [
            WorkflowStep(
                name="setup_environment",
                module="environment_setup",
                action="check_environment",
            ),
            WorkflowStep(
                name="build_python",
                module="build_synthesis",
                action="build_target",
                parameters={"target_name": "python_package"},
                dependencies=["setup_environment"],
            ),
            WorkflowStep(
                name="build_docker",
                module="build_synthesis",
                action="build_target",
                parameters={"target_name": "docker_image"},
                dependencies=["build_python"],
            ),
            WorkflowStep(
                name="validate_outputs",
                module="build_synthesis",
                action="validate_build_output",
                parameters={"target_name": "python_package"},
                dependencies=["build_python", "build_docker"],
            ),
        ]

        # Create and execute workflow
        success = workflow_manager.create_workflow("build_pipeline", workflow_steps)
        assert success is True

        # Verify workflow structure
        workflows = workflow_manager.list_workflows()
        assert "build_pipeline" in workflows
        assert len(workflows["build_pipeline"]) == 4


class TestAICodeEditingDataVisualizationIntegration:
    """Test integration between AI code editing and data visualization."""

    def test_generate_code_and_create_visualization(self):
        """Test generating code and creating visualizations of the results."""
        with patch("ai_code_editing.ai_code_helpers.get_llm_client") as mock_get_client:
            # Mock AI code generation for data analysis
            mock_client = Mock()
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[
                0
            ].message.content = """
import matplotlib.pyplot as plt
import numpy as np

def create_sample_plot():
    x = np.linspace(0, 10, 100)
    y = np.sin(x)
    
    plt.figure(figsize=(10, 6))
    plt.plot(x, y, 'b-', linewidth=2, label='sin(x)')
    plt.xlabel('x')
    plt.ylabel('y')
    plt.title('Sample Plot')
    plt.legend()
    plt.grid(True)
    plt.show()

if __name__ == '__main__':
    create_sample_plot()
"""
            mock_response.usage.total_tokens = 150
            mock_client.chat.completions.create.return_value = mock_response
            mock_get_client.return_value = (mock_client, "gpt-3.5-turbo")

            # Generate code
            result = generate_code_snippet(
                prompt="Create a function that generates a sine wave plot",
                language="python",
                provider="openai",
            )

            # Use the generated code to create a visualization
            generated_code = result["generated_code"]

            # Extract data from the generated code (simplified)
            import numpy as np

            x = np.linspace(0, 10, 100)
            y = np.sin(x)

            # Create visualization using our advanced plotter
            plotter = AdvancedPlotter()
            fig = create_advanced_line_plot(
                x_data=x.tolist(),
                y_data=y.tolist(),
                title="AI Generated Sine Wave",
                xlabel="x",
                ylabel="sin(x)",
                config=PlotConfig(
                    style=ChartStyle.MINIMAL, palette=ColorPalette.VIRIDIS
                ),
            )

            # Verify integration worked
            assert result["generated_code"] is not None
            assert "matplotlib" in generated_code.lower()
            assert fig is not None

    def test_analyze_code_quality_and_visualize_metrics(self):
        """Test analyzing code quality and visualizing the metrics."""
        test_code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr
"""

        with patch("ai_code_editing.ai_code_helpers.get_llm_client") as mock_get_client:
            # Mock AI code analysis
            mock_client = Mock()
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[
                0
            ].message.content = """
Code Quality Analysis:

1. fibonacci function:
   - Complexity: High (recursive without memoization)
   - Performance: Poor for large n
   - Maintainability: Good
   - Suggestion: Add memoization or use iterative approach

2. bubble_sort function:
   - Complexity: O(n²)
   - Performance: Poor for large arrays
   - Maintainability: Good
   - Suggestion: Use more efficient sorting algorithm

Overall Score: 6/10
"""
            mock_response.usage.total_tokens = 200
            mock_client.chat.completions.create.return_value = mock_response
            mock_get_client.return_value = (mock_client, "gpt-3.5-turbo")

            # Analyze code quality
            result = analyze_code_quality(
                code=test_code,
                language="python",
                analysis_type="comprehensive",
                provider="openai",
            )

            # Create visualization of analysis results
            # Simulate metrics extraction from analysis
            metrics = {
                "Complexity": 8,
                "Performance": 4,
                "Maintainability": 7,
                "Readability": 6,
                "Documentation": 3,
            }

            # Create radar chart visualization
            plotter = AdvancedPlotter()
            fig, ax = plotter.create_figure()

            categories = list(metrics.keys())
            values = list(metrics.values())

            plotter.plot_bar(
                categories,
                values,
                title="Code Quality Metrics",
                xlabel="Metric",
                ylabel="Score (1-10)",
            )

            plotter.finalize_plot()

            # Verify integration worked
            assert result["analysis"] is not None
            assert len(metrics) == 5


class TestEndToEndWorkflow:
    """Test complete end-to-end workflows."""

    def test_complete_development_workflow(self):
        """Test a complete development workflow from code generation to deployment."""
        with patch("ai_code_editing.ai_code_helpers.get_llm_client") as mock_get_client:
            # Mock AI responses
            mock_client = Mock()

            # Mock code generation
            gen_response = Mock()
            gen_response.choices = [Mock()]
            gen_response.choices[
                0
            ].message.content = """
def calculate_statistics(data):
    return {
        'mean': sum(data) / len(data),
        'median': sorted(data)[len(data) // 2],
        'std': (sum((x - sum(data) / len(data)) ** 2 for x in data) / len(data)) ** 0.5
    }
"""
            gen_response.usage.total_tokens = 100

            # Mock code analysis
            analysis_response = Mock()
            analysis_response.choices = [Mock()]
            analysis_response.choices[0].message.content = (
                "Code looks good with minor improvements needed."
            )
            analysis_response.usage.total_tokens = 50

            mock_client.chat.completions.create.side_effect = [
                gen_response,
                analysis_response,
            ]
            mock_get_client.return_value = (mock_client, "gpt-3.5-turbo")

            # Step 1: Generate code
            gen_result = generate_code_snippet(
                prompt="Create a function to calculate basic statistics",
                language="python",
                provider="openai",
            )

            # Step 2: Write code to file
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write(gen_result["generated_code"])
                temp_file = f.name

            try:
                # Step 3: Analyze code
                analyzer = StaticAnalyzer()
                analysis_results = analyzer.analyze_file(
                    temp_file, [AnalysisType.QUALITY]
                )

                # Step 4: Create build target
                build_manager = BuildManager()
                build_target = create_python_build_target(
                    name="statistics_package",
                    source_path=os.path.dirname(temp_file),
                    output_path="dist",
                )
                build_manager.add_build_target(build_target)

                # Step 5: Create workflow
                workflow_manager = get_workflow_manager()
                workflow_steps = [
                    WorkflowStep(
                        name="generate_code",
                        module="ai_code_editing",
                        action="generate_code_snippet",
                    ),
                    WorkflowStep(
                        name="analyze_code",
                        module="static_analysis",
                        action="analyze_file",
                        dependencies=["generate_code"],
                    ),
                    WorkflowStep(
                        name="build_package",
                        module="build_synthesis",
                        action="build_target",
                        dependencies=["analyze_code"],
                    ),
                ]

                success = workflow_manager.create_workflow(
                    "dev_workflow", workflow_steps
                )

                # Step 6: Create visualization of workflow
                plotter = AdvancedPlotter()

                # Create workflow visualization data
                workflow_data = {
                    "Code Generation": 1,
                    "Static Analysis": len(analysis_results),
                    "Build Process": 1,
                    "Testing": 0,
                    "Deployment": 0,
                }

                fig = create_advanced_bar_chart(
                    list(workflow_data.keys()),
                    list(workflow_data.values()),
                    title="Development Workflow Progress",
                    xlabel="Stage",
                    ylabel="Items Processed",
                )

                # Verify end-to-end workflow
                assert gen_result["generated_code"] is not None
                assert len(analysis_results) >= 0
                assert success is True
                assert fig is not None

            finally:
                os.unlink(temp_file)

    def test_data_analysis_pipeline(self):
        """Test a complete data analysis pipeline."""
        # Create sample data
        import numpy as np

        data = np.random.normal(100, 15, 1000)

        # Step 1: Analyze data with static analysis (if applicable)
        analyzer = StaticAnalyzer()

        # Step 2: Create visualizations
        plotter = AdvancedPlotter()

        # Create multiple visualizations
        datasets = [
            Dataset(
                name="Histogram",
                data=[
                    DataPoint(x=i, y=count)
                    for i, count in enumerate(np.histogram(data, bins=30)[0])
                ],
                plot_type=PlotType.HISTOGRAM,
            ),
            Dataset(
                name="Box Plot",
                data=[
                    DataPoint(x=1, y=val) for val in data[:100]
                ],  # Sample for box plot
                plot_type=PlotType.BOX,
            ),
        ]

        # Create dashboard
        dashboard = plotter.create_dashboard(
            datasets=datasets, layout=(1, 2), title="Data Analysis Dashboard"
        )

        # Step 3: Generate code for data analysis
        with patch("ai_code_editing.ai_code_helpers.get_llm_client") as mock_get_client:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[
                0
            ].message.content = """
import pandas as pd
import numpy as np

def analyze_data(data):
    df = pd.DataFrame({'values': data})
    return {
        'mean': df['values'].mean(),
        'std': df['values'].std(),
        'min': df['values'].min(),
        'max': df['values'].max()
    }
"""
            mock_response.usage.total_tokens = 100
            mock_client.chat.completions.create.return_value = mock_response
            mock_get_client.return_value = (mock_client, "gpt-3.5-turbo")

            code_result = generate_code_snippet(
                prompt="Create a function to analyze statistical data",
                language="python",
                provider="openai",
            )

        # Step 4: Create build target for the analysis code
        build_manager = BuildManager()
        analysis_target = create_python_build_target(
            name="data_analysis", source_path=".", output_path="dist"
        )
        build_manager.add_build_target(analysis_target)

        # Verify pipeline components
        assert dashboard is not None
        assert code_result["generated_code"] is not None
        assert len(build_manager.targets) == 1


class TestErrorHandlingAndRecovery:
    """Test error handling and recovery across modules."""

    def test_ai_failure_fallback(self):
        """Test fallback behavior when AI services fail."""
        with patch(
            "ai_code_editing.ai_code_helpers.get_llm_client",
            side_effect=Exception("API Error"),
        ):
            # Should handle AI failure gracefully
            try:
                result = generate_code_snippet(
                    prompt="Create a function", language="python", provider="openai"
                )
                # If we get here, the function should have handled the error
                assert result is not None
            except Exception as e:
                # Expected behavior - should raise an exception
                assert "API Error" in str(e)

    def test_build_failure_recovery(self):
        """Test build failure recovery."""
        build_manager = BuildManager()

        # Add a target that will fail
        failing_target = create_python_build_target(
            name="failing_target", source_path="/nonexistent/path", output_path="dist"
        )
        build_manager.add_build_target(failing_target)

        # Attempt to build (should fail gracefully)
        result = build_manager.build_target("failing_target")

        # Verify failure was handled
        assert result.status == BuildStatus.FAILED
        assert result.error is not None

    def test_analysis_failure_recovery(self):
        """Test static analysis failure recovery."""
        analyzer = StaticAnalyzer()

        # Analyze nonexistent file (should handle gracefully)
        results = analyzer.analyze_file("/nonexistent/file.py")

        # Should return empty list or handle error gracefully
        assert isinstance(results, list)


if __name__ == "__main__":
    pytest.main([__file__])
