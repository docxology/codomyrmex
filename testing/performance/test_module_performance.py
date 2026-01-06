#!/usr/bin/env python3
"""
Performance Baseline Tests for Codomyrmex Modules

This module establishes performance baselines for all Codomyrmex modules and
detects performance regressions by comparing current performance against
historical baselines.
"""

import pytest
import time
import statistics
from typing import Dict, Any, List, Callable
from dataclasses import dataclass

# Import modules for performance testing
MODULE_AVAILABILITY = {}

try:
    from codomyrmex.code_execution_sandbox import execute_code, execute_with_limits, ExecutionLimits
    MODULE_AVAILABILITY["code_execution"] = True
except ImportError:
    MODULE_AVAILABILITY["code_execution"] = False

try:
    from codomyrmex.static_analysis import analyze_file
    MODULE_AVAILABILITY["static_analysis"] = True
except ImportError:
    MODULE_AVAILABILITY["static_analysis"] = False

try:
    from codomyrmex.security.digital import analyze_file_security, check_compliance
    MODULE_AVAILABILITY["security"] = True
except ImportError:
    MODULE_AVAILABILITY["security"] = False

try:
    from codomyrmex.ai_code_editing import generate_code_snippet
    MODULE_AVAILABILITY["ai_code_editing"] = True
except ImportError:
    MODULE_AVAILABILITY["ai_code_editing"] = False

try:
    from codomyrmex.data_visualization import create_bar_chart
    MODULE_AVAILABILITY["data_visualization"] = True
except ImportError:
    MODULE_AVAILABILITY["data_visualization"] = False

try:
    from codomyrmex.performance import profile_function, run_benchmark, PerformanceProfiler
    MODULE_AVAILABILITY["performance"] = True
except ImportError:
    MODULE_AVAILABILITY["performance"] = False

try:
    from codomyrmex.logging_monitoring.logger_config import PerformanceLogger
    MODULE_AVAILABILITY["performance_logging"] = True
except ImportError:
    MODULE_AVAILABILITY["performance_logging"] = False

try:
    from codomyrmex.logging_monitoring.logger_config import setup_logging, get_logger
    LOGGING_AVAILABLE = True
except ImportError:
    LOGGING_AVAILABLE = False


@dataclass
class PerformanceBaseline:
    """Performance baseline data for a module operation."""
    module_name: str
    operation_name: str
    baseline_time: float  # seconds
    baseline_memory: float  # MB
    tolerance_percent: float = 50.0  # Allow 50% degradation before flagging
    measurements: List[float] = None

    def __post_init__(self):
        if self.measurements is None:
            self.measurements = []


@dataclass
class PerformanceResult:
    """Result of a performance measurement."""
    operation: str
    execution_time: float
    memory_usage: float
    cpu_usage: float = 0.0
    status: str = "success"  # "success", "failed", "timeout"
    regression_detected: bool = False
    baseline_comparison: Dict[str, Any] = None


class PerformanceBaselineManager:
    """Manages performance baselines and regression detection."""

    def __init__(self):
        self.baselines: Dict[str, PerformanceBaseline] = {}
        self._load_baselines()

    def _load_baselines(self):
        """Load performance baselines."""
        # These would typically be loaded from a configuration file
        # For now, using hardcoded baseline values
        self.baselines = {
            "code_execution.execute_code": PerformanceBaseline(
                "code_execution", "execute_code",
                baseline_time=0.5, baseline_memory=50.0
            ),
            "static_analysis.analyze_file": PerformanceBaseline(
                "static_analysis", "analyze_file",
                baseline_time=0.2, baseline_memory=30.0
            ),
            "security_audit.analyze_file_security": PerformanceBaseline(
                "security_audit", "analyze_file_security",
                baseline_time=1.0, baseline_memory=80.0
            ),
            "data_visualization.create_bar_chart": PerformanceBaseline(
                "data_visualization", "create_bar_chart",
                baseline_time=0.1, baseline_memory=20.0
            ),
            "performance.profile_function": PerformanceBaseline(
                "performance", "profile_function",
                baseline_time=0.05, baseline_memory=15.0
            ),
        }

    def check_regression(self, operation: str, execution_time: float,
                        memory_usage: float) -> Dict[str, Any]:
        """Check if performance regressed against baseline."""
        if operation not in self.baselines:
            return {"regression": False, "reason": "no_baseline"}

        baseline = self.baselines[operation]

        # Check time regression
        time_regression = execution_time > baseline.baseline_time * (1 + baseline.tolerance_percent / 100)

        # Check memory regression
        memory_regression = memory_usage > baseline.baseline_memory * (1 + baseline.tolerance_percent / 100)

        regression = time_regression or memory_regression

        return {
            "regression": regression,
            "time_regression": time_regression,
            "memory_regression": memory_regression,
            "baseline_time": baseline.baseline_time,
            "baseline_memory": baseline.baseline_memory,
            "actual_time": execution_time,
            "actual_memory": memory_usage,
            "tolerance_percent": baseline.tolerance_percent
        }


class PerformanceTestSuite:
    """Suite of performance tests for module benchmarking."""

    def __init__(self, baseline_manager: PerformanceBaselineManager = None):
        self.baseline_manager = baseline_manager or PerformanceBaselineManager()
        self.results: List[PerformanceResult] = []

    def run_performance_test(self, operation_name: str, test_function: Callable,
                           iterations: int = 5, warmup_iterations: int = 2) -> PerformanceResult:
        """Run a performance test and return results."""
        import psutil
        import os

        # Warmup iterations
        for _ in range(warmup_iterations):
            try:
                test_function()
            except Exception:
                pass  # Ignore warmup errors

        # Actual measurements
        execution_times = []
        memory_usages = []
        cpu_usages = []

        process = psutil.Process(os.getpid())

        for _ in range(iterations):
            # Measure memory before
            memory_before = process.memory_info().rss / 1024 / 1024  # MB

            # Execute function and measure time
            start_time = time.time()
            try:
                test_function()
                status = "success"
            except Exception as e:
                status = "failed"

            end_time = time.time()
            execution_time = end_time - start_time

            # Measure memory after
            memory_after = process.memory_info().rss / 1024 / 1024  # MB
            memory_usage = max(memory_before, memory_after)

            # Get CPU usage (rough estimate)
            try:
                cpu_usage = process.cpu_percent(interval=0.1)
            except Exception:
                cpu_usage = 0.0

            execution_times.append(execution_time)
            memory_usages.append(memory_usage)
            cpu_usages.append(cpu_usage)

        # Calculate averages
        avg_time = statistics.mean(execution_times)
        avg_memory = statistics.mean(memory_usages)
        avg_cpu = statistics.mean(cpu_usages) if cpu_usages else 0.0

        # Check for regression
        baseline_check = self.baseline_manager.check_regression(
            operation_name, avg_time, avg_memory
        )

        result = PerformanceResult(
            operation=operation_name,
            execution_time=avg_time,
            memory_usage=avg_memory,
            cpu_usage=avg_cpu,
            status=status,
            regression_detected=baseline_check["regression"],
            baseline_comparison=baseline_check
        )

        self.results.append(result)
        return result

    def get_summary_report(self) -> Dict[str, Any]:
        """Generate a summary report of all performance tests."""
        if not self.results:
            return {"status": "no_tests_run"}

        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r.status == "success"])
        regressed_tests = len([r for r in self.results if r.regression_detected])

        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "regressed_tests": regressed_tests,
            "success_rate": (passed_tests / total_tests) * 100 if total_tests > 0 else 0,
            "regression_rate": (regressed_tests / total_tests) * 100 if total_tests > 0 else 0,
            "results": [
                {
                    "operation": r.operation,
                    "execution_time": r.execution_time,
                    "memory_usage": r.memory_usage,
                    "status": r.status,
                    "regression": r.regression_detected
                }
                for r in self.results
            ]
        }


# Test fixtures
@pytest.fixture
def baseline_manager():
    """Performance baseline manager fixture."""
    return PerformanceBaselineManager()


@pytest.fixture
def performance_suite(baseline_manager):
    """Performance test suite fixture."""
    return PerformanceTestSuite(baseline_manager)


class TestModulePerformanceBaselines:
    """Test performance baselines for all modules."""

    @pytest.mark.skipif(not MODULE_AVAILABILITY.get("code_execution", False),
                       reason="Code execution module not available")
    def test_code_execution_performance(self, performance_suite, tmp_path):
        """Test code execution performance baselines."""
        # Create a simple test script
        test_script = tmp_path / "perf_test.py"
        test_script.write_text("print(sum(range(100)))")

        def execute_test():
            result = execute_code("python", test_script.read_text(), timeout=10)
            return result["status"] == "success"

        result = performance_suite.run_performance_test(
            "code_execution.execute_code", execute_test, iterations=3
        )

        assert result.status == "success"
        assert result.execution_time > 0
        assert result.memory_usage > 0

        # Should not have major regression
        assert not result.regression_detected or result.baseline_comparison["time_regression"] is False

    @pytest.mark.skipif(not MODULE_AVAILABILITY.get("static_analysis", False),
                       reason="Static analysis module not available")
    def test_static_analysis_performance(self, performance_suite, tmp_path):
        """Test static analysis performance baselines."""
        # Create a test Python file
        test_file = tmp_path / "analysis_test.py"
        test_file.write_text('''
def test_function():
    x = 1
    y = 2
    return x + y

class TestClass:
    def method(self):
        pass
''')

        def analyze_test():
            from codomyrmex.static_analysis import analyze_file
            return analyze_file(str(test_file))

        result = performance_suite.run_performance_test(
            "static_analysis.analyze_file", analyze_test, iterations=3
        )

        assert result.execution_time > 0
        assert result.memory_usage > 0

    @pytest.mark.skipif(not MODULE_AVAILABILITY.get("security_audit", False),
                       reason="Security audit module not available")
    def test_security_audit_performance(self, performance_suite, tmp_path):
        """Test security audit performance baselines."""
        # Create a test file with some security issues
        test_file = tmp_path / "security_test.py"
        test_file.write_text('''
import os

def insecure_function(user_input):
    # Command injection vulnerability
    os.system(user_input)

# Hard-coded password
PASSWORD = "admin123"
''')

        def security_test():
            from codomyrmex.security_audit import analyze_file_security
            return analyze_file_security(str(test_file))

        result = performance_suite.run_performance_test(
            "security_audit.analyze_file_security", security_test, iterations=3
        )

        assert result.execution_time > 0
        assert result.memory_usage > 0

    @pytest.mark.skipif(not MODULE_AVAILABILITY.get("data_visualization", False),
                       reason="Data visualization module not available")
    def test_data_visualization_performance(self, performance_suite):
        """Test data visualization performance baselines."""
        test_data = {
            "categories": ["A", "B", "C", "D", "E"],
            "values": [10, 20, 15, 25, 30]
        }

        def visualize_test():
            from codomyrmex.data_visualization import create_bar_chart
            return create_bar_chart(test_data, "Performance Test Chart")

        result = performance_suite.run_performance_test(
            "data_visualization.create_bar_chart", visualize_test, iterations=5
        )

        assert result.execution_time > 0
        assert result.memory_usage > 0
        assert result.status == "success"

    @pytest.mark.skipif(not MODULE_AVAILABILITY.get("performance", False),
                       reason="Performance module not available")
    def test_performance_module_performance(self, performance_suite):
        """Test performance module's own performance."""

        def profile_test():
            from codomyrmex.performance import profile_function
            return profile_function(lambda: sum(range(100)))

        result = performance_suite.run_performance_test(
            "performance.profile_function", profile_test, iterations=5
        )

        assert result.execution_time > 0
        assert result.memory_usage > 0
        assert result.status == "success"


class TestPerformanceRegressionDetection:
    """Test performance regression detection."""

    def test_baseline_comparison(self, baseline_manager):
        """Test baseline comparison logic."""
        # Test normal performance (should not regress)
        result = baseline_manager.check_regression(
            "code_execution.execute_code", 0.3, 40.0
        )

        assert not result["regression"]
        assert not result["time_regression"]
        assert not result["memory_regression"]

        # Test performance regression
        result = baseline_manager.check_regression(
            "code_execution.execute_code", 2.0, 100.0  # Much slower and more memory
        )

        assert result["regression"]
        assert result["time_regression"]
        assert result["memory_regression"]

    def test_missing_baseline(self, baseline_manager):
        """Test handling of missing baselines."""
        result = baseline_manager.check_regression(
            "nonexistent.operation", 1.0, 50.0
        )

        assert not result["regression"]
        assert result["reason"] == "no_baseline"


class TestPerformanceReporting:
    """Test performance reporting functionality."""

    def test_performance_summary_report(self, performance_suite):
        """Test generation of performance summary reports."""
        # Add some mock results
        mock_result1 = PerformanceResult(
            operation="test.operation1",
            execution_time=0.5,
            memory_usage=25.0,
            status="success"
        )
        mock_result2 = PerformanceResult(
            operation="test.operation2",
            execution_time=1.2,
            memory_usage=60.0,
            status="success",
            regression_detected=True
        )

        performance_suite.results = [mock_result1, mock_result2]

        report = performance_suite.get_summary_report()

        assert report["total_tests"] == 2
        assert report["passed_tests"] == 2
        assert report["regressed_tests"] == 1
        assert report["success_rate"] == 100.0
        assert report["regression_rate"] == 50.0
        assert len(report["results"]) == 2

    def test_empty_performance_suite(self, performance_suite):
        """Test performance suite with no results."""
        report = performance_suite.get_summary_report()

        assert report["status"] == "no_tests_run"


class TestPerformanceBenchmarking:
    """Test performance benchmarking utilities."""

    @pytest.mark.skipif(not MODULE_AVAILABILITY.get("performance", False),
                       reason="Performance module not available")
    def test_benchmark_vs_profile_comparison(self):
        """Compare results between benchmark and profile functions."""
        from codomyrmex.performance import profile_function, run_benchmark

        def test_function():
            return sum(range(1000))

        # Profile the function
        profile_result = profile_function(test_function)

        # Benchmark the function
        benchmark_result = run_benchmark(test_function, iterations=3)

        # Both should succeed and provide timing information
        assert profile_result["execution_time"] > 0
        assert benchmark_result["average_time"] > 0

        # Benchmark should have multiple iterations
        assert benchmark_result["iterations"] == 3
        assert "min_time" in benchmark_result
        assert "max_time" in benchmark_result

    def test_performance_logger_integration(self):
        """Test integration with performance logger."""
        if not MODULE_AVAILABILITY.get("performance_logging", False):
            pytest.skip("Performance logging not available")

        from codomyrmex.logging_monitoring.logger_config import PerformanceLogger

        perf_logger = PerformanceLogger("test_performance")

        # Simulate a performance test
        with perf_logger.time_operation("test_operation"):
            time.sleep(0.01)  # Small delay

        perf_logger.log_metric("test_metric", 42.5, "ms")

        # The logger should handle this without errors
        # (We can't easily verify internal state)


if __name__ == "__main__":
    # Run the performance tests
    pytest.main([__file__, "-v", "--tb=short"])
