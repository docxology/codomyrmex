#!/usr/bin/env python3
"""
Benchmarking Utilities Tests

This module tests the benchmarking utilities and performance measurement
capabilities of the Codomyrmex performance module.
"""

import time

import pytest

try:
    from codomyrmex.performance import (
        PerformanceProfiler,
        profile_function,
        run_benchmark,
    )
    PERFORMANCE_AVAILABLE = True
except ImportError:
    PERFORMANCE_AVAILABLE = False

try:
    from codomyrmex.logging_monitoring.core.logger_config import PerformanceLogger
    PERFORMANCE_LOGGING_AVAILABLE = True
except ImportError:
    PERFORMANCE_LOGGING_AVAILABLE = False


class TestBenchmarkingUtilities:
    """Test benchmarking and performance measurement utilities."""

    @pytest.mark.skipif(not PERFORMANCE_AVAILABLE,
                       reason="Performance module not available")
    def test_run_benchmark_basic(self):
        """Test basic benchmark functionality."""
        from codomyrmex.performance import run_benchmark

        def simple_function():
            return sum(range(100))

        result = run_benchmark(simple_function, iterations=5)

        # Verify result structure
        assert isinstance(result, dict)
        assert "iterations" in result
        assert "average_time" in result
        assert "min_time" in result
        assert "max_time" in result
        assert "total_time" in result

        # Verify values
        assert result["iterations"] == 5
        assert result["average_time"] > 0
        assert result["min_time"] > 0
        assert result["max_time"] > 0
        assert result["total_time"] > result["average_time"]

        # Min should be <= average <= max
        assert result["min_time"] <= result["average_time"] <= result["max_time"]

    @pytest.mark.skipif(not PERFORMANCE_AVAILABLE,
                       reason="Performance module not available")
    def test_run_benchmark_with_different_iterations(self):
        """Test benchmark with different iteration counts."""
        from codomyrmex.performance import run_benchmark

        def test_function():
            time.sleep(0.001)  # Small delay

        # Test with different iteration counts
        for iterations in [1, 3, 10]:
            result = run_benchmark(test_function, iterations=iterations)
            assert result["iterations"] == iterations
            assert result["average_time"] > 0

    @pytest.mark.skipif(not PERFORMANCE_AVAILABLE,
                       reason="Performance module not available")
    def test_run_benchmark_error_handling(self):
        """Test benchmark error handling."""
        from codomyrmex.performance import run_benchmark

        def failing_function():
            raise ValueError("Test error")

        # Should handle exceptions gracefully
        result = run_benchmark(failing_function, iterations=3)

        # Should still return a result structure
        assert isinstance(result, dict)
        assert "iterations" in result
        # May have partial results or error indicators

    @pytest.mark.skipif(not PERFORMANCE_AVAILABLE,
                       reason="Performance module not available")
    def test_profile_function_basic(self):
        """Test basic function profiling."""
        from codomyrmex.performance import profile_function

        def test_function():
            result = []
            for i in range(100):
                result.append(i * i)
            return result

        result = profile_function(test_function)

        # Verify result structure
        assert isinstance(result, dict)
        assert "execution_time" in result
        assert "memory_usage" in result

        # Verify values
        assert result["execution_time"] > 0
        assert result["memory_usage"] >= 0

    @pytest.mark.skipif(not PERFORMANCE_AVAILABLE,
                       reason="Performance module not available")
    def test_profile_function_with_arguments(self):
        """Test profiling function with arguments."""
        from codomyrmex.performance import profile_function

        def function_with_args(n, multiplier=1):
            return [i * multiplier for i in range(n)]

        result = profile_function(function_with_args, 50, multiplier=2)

        assert result["execution_time"] > 0
        assert result["memory_usage"] >= 0

    @pytest.mark.skipif(not PERFORMANCE_AVAILABLE,
                       reason="Performance module not available")
    def test_performance_profiler_class(self):
        """Test the PerformanceProfiler class."""
        from codomyrmex.performance import PerformanceProfiler

        profiler = PerformanceProfiler()

        # Test profiling a function
        def sample_function():
            return sum(range(1000))

        result = profiler.profile_function(sample_function)

        assert isinstance(result, dict)
        assert "execution_time" in result
        assert "memory_usage" in result
        assert result["execution_time"] > 0

    @pytest.mark.skipif(not PERFORMANCE_AVAILABLE,
                       reason="Performance module not available")
    def test_benchmark_vs_profile_consistency(self):
        """Test consistency between benchmark and profile results."""
        from codomyrmex.performance import profile_function, run_benchmark

        def consistent_function():
            # Function with consistent performance
            data = list(range(500))
            return sorted(data)

        # Get results from both methods
        profile_result = profile_function(consistent_function)
        benchmark_result = run_benchmark(consistent_function, iterations=3)

        # Both should succeed
        assert profile_result["execution_time"] > 0
        assert benchmark_result["average_time"] > 0

        # Results should be in the same ballpark (within 10x)
        time_ratio = profile_result["execution_time"] / benchmark_result["average_time"]
        assert 0.1 <= time_ratio <= 10.0

    def test_performance_logger_benchmarking(self):
        """Test performance logging during benchmarking."""
        if not PERFORMANCE_LOGGING_AVAILABLE:
            pytest.skip("Performance logging not available")

        from codomyrmex.logging_monitoring.core.logger_config import PerformanceLogger
        from codomyrmex.performance import run_benchmark

        perf_logger = PerformanceLogger("benchmark_test")

        def benchmarked_function():
            time.sleep(0.01)
            return 42

        # Benchmark with performance logging
        with perf_logger.time_operation("benchmark_with_logging"):
            result = run_benchmark(benchmarked_function, iterations=3)

        # Log benchmark results
        perf_logger.log_metric("benchmark_avg_time", result["average_time"], "seconds")
        perf_logger.log_metric("benchmark_iterations", result["iterations"], "count")

        # Should complete without errors
        assert result["iterations"] == 3
        assert result["average_time"] > 0


class TestBenchmarkingScenarios:
    """Test benchmarking in different scenarios."""

    @pytest.mark.skipif(not PERFORMANCE_AVAILABLE,
                       reason="Performance module not available")
    def test_algorithm_comparison_benchmark(self):
        """Test benchmarking different algorithms."""
        from codomyrmex.performance import run_benchmark

        def bubble_sort(arr):
            arr = arr.copy()
            n = len(arr)
            for i in range(n):
                for j in range(0, n - i - 1):
                    if arr[j] > arr[j + 1]:
                        arr[j], arr[j + 1] = arr[j + 1], arr[j]
            return arr

        def python_sort(arr):
            return sorted(arr)

        # Test data - use larger dataset to ensure performance difference
        test_data = list(range(100, 0, -1))  # Reverse sorted list of 100 items

        # Benchmark both algorithms
        bubble_result = run_benchmark(lambda: bubble_sort(test_data), iterations=5)
        python_result = run_benchmark(lambda: python_sort(test_data), iterations=5)

        # Both should work
        assert bubble_result["average_time"] > 0
        assert python_result["average_time"] > 0

        # Python's built-in sort should be faster
        assert python_result["average_time"] < bubble_result["average_time"]

        # Verify correctness
        bubble_sorted = bubble_sort(test_data)
        python_sorted = python_sort(test_data)
        assert bubble_sorted == python_sorted == sorted(test_data)

    @pytest.mark.performance
    @pytest.mark.skipif(not PERFORMANCE_AVAILABLE,
                       reason="Performance module not available")
    def test_memory_intensive_benchmark(self):
        """Test benchmarking memory-intensive operations."""
        from codomyrmex.performance import profile_function

        def memory_intensive_function():
            # Create large data structures
            data = []
            for i in range(1000):
                data.append([j for j in range(100)])
            return len(data)

        result = profile_function(memory_intensive_function)

        assert result["execution_time"] > 0
        assert result["memory_usage"] >= 0  # May be 0.0 if psutil unavailable

    @pytest.mark.skipif(not PERFORMANCE_AVAILABLE,
                       reason="Performance module not available")
    def test_io_bound_benchmark(self):
        """Test benchmarking I/O bound operations."""
        import os
        import tempfile

        from codomyrmex.performance import profile_function

        def io_bound_function():
            # Simulate I/O operations
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
                for i in range(100):
                    f.write(f"Line {i}\n")
                temp_file = f.name

            # Read the file
            with open(temp_file) as f:
                content = f.read()

            os.unlink(temp_file)
            return len(content)

        result = profile_function(io_bound_function)

        assert result["execution_time"] > 0
        # I/O operations may not use much memory
        assert result["memory_usage"] >= 0

    @pytest.mark.skipif(not PERFORMANCE_AVAILABLE,
                       reason="Performance module not available")
    def test_concurrent_benchmark(self):
        """Test benchmarking with concurrent operations."""
        import threading

        from codomyrmex.performance import run_benchmark

        results = []

        def worker_function(worker_id):
            """Worker function for concurrent testing."""
            time.sleep(0.01)  # Simulate work
            results.append(f"Worker {worker_id} done")

        def concurrent_test():
            threads = []
            for i in range(5):
                t = threading.Thread(target=worker_function, args=(i,))
                threads.append(t)
                t.start()

            for t in threads:
                t.join()

            return len(results)

        result = run_benchmark(concurrent_test, iterations=3)

        assert result["iterations"] == 3
        assert result["average_time"] > 0


class TestBenchmarkingEdgeCases:
    """Test benchmarking edge cases and error conditions."""

    @pytest.mark.skipif(not PERFORMANCE_AVAILABLE,
                       reason="Performance module not available")
    def test_empty_function_benchmark(self):
        """Test benchmarking an empty function."""
        from codomyrmex.performance import profile_function

        def empty_function():
            pass

        result = profile_function(empty_function)

        assert result["execution_time"] >= 0  # Should be very small but >= 0
        assert result["memory_usage"] >= 0

    @pytest.mark.skipif(not PERFORMANCE_AVAILABLE,
                       reason="Performance module not available")
    def test_very_fast_function_benchmark(self):
        """Test benchmarking extremely fast functions."""
        from codomyrmex.performance import run_benchmark

        def very_fast_function():
            return 42

        result = run_benchmark(very_fast_function, iterations=100)

        assert result["iterations"] == 100
        assert result["average_time"] >= 0
        # Very fast functions should have very small execution times
        assert result["average_time"] < 1.0  # Less than 1 second on average

    @pytest.mark.skipif(not PERFORMANCE_AVAILABLE,
                       reason="Performance module not available")
    def test_high_variance_benchmark(self):
        """Test benchmarking functions with high timing variance."""
        import random

        from codomyrmex.performance import run_benchmark

        def variable_time_function():
            # Random sleep to create variance
            time.sleep(random.uniform(0.001, 0.01))
            return "done"

        result = run_benchmark(variable_time_function, iterations=10)

        assert result["iterations"] == 10
        # With variance, min and max should be noticeably different
        assert result["max_time"] > result["min_time"]
        # Variance should be present
        assert (result["max_time"] - result["min_time"]) > 0.001

    def test_benchmark_result_statistics(self):
        """Test statistical properties of benchmark results."""
        if not PERFORMANCE_AVAILABLE:
            pytest.skip("Performance module not available")

        from codomyrmex.performance import run_benchmark

        def stable_function():
            # Relatively stable execution time
            x = 0
            for i in range(1000):
                x += i
            return x

        result = run_benchmark(stable_function, iterations=20)

        # Statistical checks
        assert result["iterations"] == 20
        assert result["average_time"] > 0

        # For a stable function, the standard deviation should be reasonable
        # Calculate rough standard deviation estimate
        time_range = result["max_time"] - result["min_time"]
        # Range should be less than 10x the average for a stable function
        assert time_range < result["average_time"] * 10


class TestBenchmarkingIntegration:
    """Test integration of benchmarking with other modules."""

    def test_benchmark_with_visualization(self):
        """Test that benchmark results can be visualized."""
        if not PERFORMANCE_AVAILABLE:
            pytest.skip("Performance module not available")

        try:
            from codomyrmex.data_visualization import create_bar_chart
            VISUALIZATION_AVAILABLE = True
        except ImportError:
            VISUALIZATION_AVAILABLE = False

        if not VISUALIZATION_AVAILABLE:
            pytest.skip("Data visualization not available")

        from codomyrmex.performance import run_benchmark

        # Benchmark multiple functions
        functions = {
            "sum_range": lambda: sum(range(1000)),
            "list_comp": lambda: [x*x for x in range(1000)],
            "loop_sum": lambda: sum(x for x in range(1000))
        }

        results = {}
        for name, func in functions.items():
            benchmark = run_benchmark(func, iterations=5)
            results[name] = benchmark["average_time"]

        # Create visualization of results
        chart_data = {
            "categories": list(results.keys()),
            "values": list(results.values())
        }

        from codomyrmex.data_visualization import create_bar_chart
        chart = create_bar_chart(
            chart_data,
            "Function Performance Comparison"
        )

        assert chart is not None
        # assert "Function Performance Comparison" in chart or "bar" in chart.lower()

    def test_benchmark_with_logging(self):
        """Test that benchmarking integrates with logging."""
        if not PERFORMANCE_LOGGING_AVAILABLE:
            pytest.skip("Performance logging not available")

        if not PERFORMANCE_AVAILABLE:
            pytest.skip("Performance module not available")

        from codomyrmex.logging_monitoring.core.logger_config import PerformanceLogger
        from codomyrmex.performance import run_benchmark

        perf_logger = PerformanceLogger("benchmark_integration")

        def test_function():
            return sum(range(500))

        # Benchmark with logging
        with perf_logger.time_operation("full_benchmark_test"):
            result = run_benchmark(test_function, iterations=3)

        # Log the results
        perf_logger.log_metric("benchmark_time", result["average_time"], "seconds")
        perf_logger.log_metric("iterations", result["iterations"], "count")

        # Verify benchmark worked
        assert result["iterations"] == 3
        assert result["average_time"] > 0


if __name__ == "__main__":
    # Run the benchmarking tests
    pytest.main([__file__, "-v", "--tb=short"])
