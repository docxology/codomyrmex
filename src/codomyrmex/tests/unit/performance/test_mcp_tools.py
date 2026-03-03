"""Zero-mock unit tests for performance MCP tools."""

from codomyrmex.performance.mcp_tools import (
    performance_check_regression,
    performance_compare_benchmarks,
)


def test_performance_check_regression_success():
    """Test successful regression check without mocking."""
    result = performance_check_regression(
        benchmark_name="test_bench",
        measured_value=1.5,
        baseline_mean=1.0,
        baseline_stddev=0.1,
        warning_threshold=0.10,
        critical_threshold=0.25,
        higher_is_better=False,
    )
    assert result["status"] == "ok"
    assert result["benchmark"] == "test_bench"
    assert "is_regression" in result
    assert "severity" in result


def test_performance_check_regression_error():
    """Test error handling in regression check without mocking."""
    # Pass invalid type for measured_value to trigger TypeError inside the function
    result = performance_check_regression(
        benchmark_name="test_bench",
        measured_value=None,  # type: ignore
        baseline_mean=1.0,
    )
    assert result["status"] == "error"
    assert "error" in result


def test_performance_compare_benchmarks_success():
    """Test successful benchmark comparison without mocking."""
    result = performance_compare_benchmarks(
        name="test_compare",
        before=1.0,
        after=1.5,
        higher_is_better=False,
    )
    assert result["status"] == "ok"
    assert result["name"] == "test_compare"
    assert result["before"] == 1.0
    assert result["after"] == 1.5
    assert result["improved"] is False


def test_performance_compare_benchmarks_error():
    """Test error handling in benchmark comparison without mocking."""
    # Pass invalid type for before to trigger TypeError inside the function
    result = performance_compare_benchmarks(
        name="test_compare",
        before=None,  # type: ignore
        after=1.5,
    )
    assert result["status"] == "error"
    assert "error" in result
