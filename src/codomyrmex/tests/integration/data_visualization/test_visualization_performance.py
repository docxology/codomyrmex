#!/usr/bin/env python3
"""
Integration Test: Data Visualization → Performance Monitoring Workflow

This integration test validates the workflow from data visualization to performance
monitoring, ensuring that visualization components work correctly with performance
tracking and monitoring systems.
"""

import statistics
import tempfile
import time
from typing import Any

import pytest

# Import modules for integration testing
try:
    from codomyrmex.data_visualization import (
        create_bar_chart,  # noqa: F401
        create_line_plot,  # noqa: F401
    )
    DATA_VISUALIZATION_AVAILABLE = True
except ImportError:
    DATA_VISUALIZATION_AVAILABLE = False

try:
    from codomyrmex.performance import (
        PerformanceProfiler,  # noqa: F401
        profile_function,  # noqa: F401
        run_benchmark,  # noqa: F401
    )
    PERFORMANCE_AVAILABLE = True
except ImportError:
    PERFORMANCE_AVAILABLE = False

try:
    from codomyrmex.logging_monitoring.core.logger_config import PerformanceLogger
    PERFORMANCE_LOGGING_AVAILABLE = True
except ImportError:
    PERFORMANCE_LOGGING_AVAILABLE = False

try:
    from codomyrmex.logging_monitoring.core.logger_config import (
        get_logger,
        setup_logging,
    )
    LOGGING_AVAILABLE = True
except ImportError:
    LOGGING_AVAILABLE = False

# Set up logging for tests
if LOGGING_AVAILABLE and callable(setup_logging):
    try:
        setup_logging()
    except Exception:
        pass

logger = get_logger(__name__) if LOGGING_AVAILABLE else None


class TestVisualizationPerformanceWorkflow:
    """Integration tests for data visualization → performance monitoring workflow."""

    def setup_method(self):
        """Set up test environment."""
        self.test_data = self._generate_test_data()
        self.output_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.output_dir, ignore_errors=True)

    def _generate_test_data(self) -> dict[str, Any]:
        """Generate test data for visualization and performance testing."""
        return {
            "simple_list": [1, 2, 3, 4, 5],
            "performance_data": {
                "function_times": [0.1, 0.15, 0.12, 0.18, 0.09, 0.14, 0.11, 0.16],
                "memory_usage": [45.2, 46.1, 44.8, 47.3, 45.9, 46.7, 45.5, 46.8],
                "cpu_usage": [12.3, 15.6, 13.8, 18.2, 11.9, 14.7, 13.2, 16.4]
            },
            "comparison_data": {
                "algorithms": ["Bubble Sort", "Quick Sort", "Merge Sort", "Heap Sort"],
                "times": [120.5, 15.2, 25.8, 18.9],
                "memory": [50.2, 45.8, 52.1, 48.3]
            }
        }

    @pytest.mark.skipif(not DATA_VISUALIZATION_AVAILABLE,
                       reason="Data visualization module not available")
    def test_basic_visualization_creation(self):
        """Test that basic visualizations can be created."""
        from codomyrmex.data_visualization import create_bar_chart, create_line_plot

        # Test bar chart creation
        bar_data = {"categories": ["A", "B", "C"], "values": [10, 20, 15]}
        bar_result = create_bar_chart(bar_data, "Test Bar Chart")

        assert isinstance(bar_result, str)
        assert len(bar_result) > 0

        # Test line plot creation
        line_data = {"x": [1, 2, 3, 4], "y": [10, 15, 12, 18]}
        line_result = create_line_plot(line_data, "Test Line Plot")

        assert isinstance(line_result, str)
        assert len(line_result) > 0

    @pytest.mark.skipif(not PERFORMANCE_AVAILABLE,
                       reason="Performance module not available")
    def test_performance_function_profiling(self):
        """Test that functions can be profiled for performance."""
        from codomyrmex.performance import profile_function

        def test_function(n):
            """Simple function to profile."""
            result = 0
            for i in range(n):
                result += i * i
            return result

        # Profile the function
        profile_result = profile_function(test_function, 1000)

        assert isinstance(profile_result, dict)
        assert "execution_time" in profile_result
        assert "memory_usage" in profile_result
        assert profile_result["execution_time"] > 0

    @pytest.mark.skipif(not PERFORMANCE_AVAILABLE,
                       reason="Performance module not available")
    def test_benchmark_execution(self):
        """Test running benchmarks on functions."""
        from codomyrmex.performance import run_benchmark

        def simple_computation():
            return sum(range(1000))

        # Run benchmark
        benchmark_result = run_benchmark(simple_computation)

        assert isinstance(benchmark_result, dict)
        assert "average_time" in benchmark_result
        assert "min_time" in benchmark_result
        assert "max_time" in benchmark_result
        assert "iterations" in benchmark_result

    @pytest.mark.skipif(not PERFORMANCE_LOGGING_AVAILABLE,
                       reason="Performance logging not available")
    def test_performance_logger_integration(self):
        """Test performance logger with visualization data."""
        perf_logger = PerformanceLogger("visualization_performance")

        # Simulate visualization operations with timing
        with perf_logger.time_operation("create_bar_chart"):
            time.sleep(0.01)  # Simulate chart creation time

        with perf_logger.time_operation("render_plot"):
            time.sleep(0.005)  # Simulate rendering time

        # Log some metrics
        perf_logger.log_metric("charts_created", 5, "count")
        perf_logger.log_metric("render_time_avg", 0.015, "seconds")

        # The logger should have recorded these operations
        # (We can't easily test the internal state, but no exceptions should occur)

    @pytest.mark.skipif(not all([DATA_VISUALIZATION_AVAILABLE, PERFORMANCE_AVAILABLE]),
                       reason="Required modules not available")
    def test_visualization_performance_integration(self):
        """Test the integrated workflow of visualization with performance monitoring."""
        from codomyrmex.data_visualization import create_bar_chart
        from codomyrmex.performance import profile_function

        def create_test_chart():
            """Function to create a test chart."""
            data = {
                "categories": ["Jan", "Feb", "Mar", "Apr", "May"],
                "values": [100, 120, 140, 110, 160]
            }
            return create_bar_chart(data, "Monthly Sales")

        # Profile the chart creation
        profile_result = profile_function(create_test_chart)

        assert profile_result["execution_time"] > 0
        # Chart creation should be reasonably fast
        assert profile_result["execution_time"] < 1.0  # Less than 1 second

    @pytest.mark.skipif(not all([DATA_VISUALIZATION_AVAILABLE, PERFORMANCE_AVAILABLE]),
                       reason="Required modules not available")
    def test_performance_data_visualization(self):
        """Test visualizing performance data."""
        from codomyrmex.data_visualization import create_line_plot
        from codomyrmex.performance import run_benchmark

        def benchmark_function():
            """Function to benchmark."""
            data = list(range(1000))
            return [x * x for x in data]

        # Run benchmark to get performance data
        benchmark_result = run_benchmark(benchmark_function, iterations=5)

        # Create visualization of the performance data
        perf_data = {
            "iterations": list(range(1, benchmark_result["iterations"] + 1)),
            "times": benchmark_result.get("all_times", [benchmark_result["average_time"]] * benchmark_result["iterations"])
        }

        plot_result = create_line_plot(perf_data, "Benchmark Performance")

        assert isinstance(plot_result, str)
        assert len(plot_result) > 0

    @pytest.mark.skipif(not DATA_VISUALIZATION_AVAILABLE,
                       reason="Data visualization module not available")
    def test_visualization_error_handling(self):
        """Test error handling in visualization components."""
        from codomyrmex.data_visualization import create_bar_chart

        # Test with invalid data
        invalid_data = {"invalid": "data"}
        result = create_bar_chart(invalid_data, "Invalid Chart")

        # Should handle gracefully (either return error or empty result)
        assert isinstance(result, str)

        # Test with empty data
        empty_data = {"categories": [], "values": []}
        result = create_bar_chart(empty_data, "Empty Chart")

        assert isinstance(result, str)

    @pytest.mark.skipif(not PERFORMANCE_AVAILABLE,
                       reason="Performance module not available")
    def test_performance_error_handling(self):
        """Test error handling in performance monitoring."""
        from codomyrmex.performance import profile_function

        def failing_function():
            """Function that raises an exception."""
            raise ValueError("Test error")

        # Should handle exceptions gracefully
        profile_result = profile_function(failing_function)

        assert isinstance(profile_result, dict)
        # Should still have basic profiling info even if function failed
        assert "execution_time" in profile_result

    @pytest.mark.skipif(not PERFORMANCE_AVAILABLE,
                       reason="Performance module not available")
    def test_performance_profiler_class(self):
        """Test the PerformanceProfiler class."""
        from codomyrmex.performance import PerformanceProfiler

        profiler = PerformanceProfiler()

        # Profile a simple function
        def test_func():
            """Test functionality: func."""
            return sum(range(100))

        result = profiler.profile_function(test_func)

        assert isinstance(result, dict)
        assert "execution_time" in result
        assert "memory_usage" in result
        assert result["execution_time"] > 0

    def test_workflow_data_consistency(self):
        """Test that data flows correctly between visualization and performance modules."""
        # Create some test data
        test_data = {
            "performance_metrics": [0.1, 0.2, 0.15, 0.18, 0.12],
            "chart_labels": ["Test1", "Test2", "Test3", "Test4", "Test5"]
        }

        # Test that both modules can work with the same data structure
        if DATA_VISUALIZATION_AVAILABLE:
            from codomyrmex.data_visualization import create_bar_chart

            viz_data = {
                "categories": test_data["chart_labels"],
                "values": test_data["performance_metrics"]
            }
            chart = create_bar_chart(viz_data, "Performance Chart")
            assert isinstance(chart, str)

        if PERFORMANCE_AVAILABLE:
            from codomyrmex.performance import run_benchmark

            def process_data():
                return statistics.mean(test_data["performance_metrics"])

            benchmark = run_benchmark(process_data, iterations=3)
            assert isinstance(benchmark, dict)
            assert benchmark["iterations"] == 3

    def test_memory_performance_tracking(self):
        """Test memory usage tracking in performance operations."""
        if PERFORMANCE_AVAILABLE:
            from codomyrmex.performance import profile_function

            def memory_intensive_function():
                """Function that uses some memory."""
                data = []
                for _i in range(1000):
                    data.append(list(range(100)))
                return len(data)

            profile_result = profile_function(memory_intensive_function)

            assert "memory_usage" in profile_result
            assert profile_result["memory_usage"] >= 0

    def test_cpu_performance_tracking(self):
        """Test CPU usage tracking in performance operations."""
        if PERFORMANCE_AVAILABLE:
            from codomyrmex.performance import profile_function

            def cpu_intensive_function():
                """Function that uses CPU."""
                result = 0
                for i in range(100000):
                    result += i ** 2
                return result

            profile_result = profile_function(cpu_intensive_function)

            assert "execution_time" in profile_result
            assert profile_result["execution_time"] > 0
            # CPU intensive function should take measurable time
            assert profile_result["execution_time"] > 0.001

    def test_visualization_output_formats(self):
        """Test that visualizations support different output formats."""
        if DATA_VISUALIZATION_AVAILABLE:
            from codomyrmex.data_visualization import create_bar_chart

            data = {"categories": ["A", "B", "C"], "values": [1, 2, 3]}

            # Test basic creation
            result = create_bar_chart(data, "Format Test")
            assert isinstance(result, str)
            assert len(result) > 0

            # Could test different formats if supported
            # (Currently assuming single format, but extensible)

    def test_performance_benchmark_statistics(self):
        """Test that benchmark results include proper statistics."""
        if PERFORMANCE_AVAILABLE:
            from codomyrmex.performance import run_benchmark

            def variable_time_function():
                """Function with variable execution time."""
                import random
                time.sleep(random.uniform(0.001, 0.01))
                return 42

            benchmark = run_benchmark(variable_time_function, iterations=10)

            assert benchmark["iterations"] == 10
            assert "average_time" in benchmark
            assert "min_time" in benchmark
            assert "max_time" in benchmark
            assert benchmark["min_time"] <= benchmark["average_time"] <= benchmark["max_time"]
            assert benchmark["average_time"] > 0

    def test_integration_workflow_performance(self):
        """Test the overall performance of the integrated workflow."""
        start_time = time.time()

        # Run a complete workflow
        workflow_steps = 0

        # Step 1: Create visualization data
        if DATA_VISUALIZATION_AVAILABLE:
            from codomyrmex.data_visualization import create_bar_chart
            data = {"categories": ["X", "Y", "Z"], "values": [10, 20, 30]}
            create_bar_chart(data, "Integration Test")
            workflow_steps += 1

        # Step 2: Profile a function
        if PERFORMANCE_AVAILABLE:
            from codomyrmex.performance import profile_function
            profile_function(lambda: sum(range(100)))
            workflow_steps += 1

        # Step 3: Log performance metrics
        if PERFORMANCE_LOGGING_AVAILABLE:
            perf_logger = PerformanceLogger("integration_test")
            with perf_logger.time_operation("complete_workflow"):
                time.sleep(0.001)
            workflow_steps += 1

        end_time = time.time()
        total_time = end_time - start_time

        if workflow_steps > 0:
            # Should complete within reasonable time (5 seconds for integrated workflow)
            assert total_time < 5.0
            avg_time_per_step = total_time / workflow_steps
            # Each step should be reasonably fast
            assert avg_time_per_step < 2.0


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])
