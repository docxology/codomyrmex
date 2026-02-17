"""
Tests for Static Analysis Complexity Module
"""

import tempfile

import pytest

from codomyrmex.coding.static_analysis.complexity import (
    ComplexityAnalyzer,
    ComplexityLevel,
    ComplexityMetric,
    FileMetrics,
    FunctionMetrics,
    calculate_cyclomatic_complexity,
    count_lines,
)


class TestComplexityMetric:
    """Tests for ComplexityMetric."""

    def test_from_value(self):
        """Should create with auto-level."""
        low = ComplexityMetric.from_value("test", 3)
        high = ComplexityMetric.from_value("test", 25)

        assert low.level == ComplexityLevel.LOW
        assert high.level == ComplexityLevel.VERY_HIGH


class TestFunctionMetrics:
    """Tests for FunctionMetrics."""

    def test_overall_complexity(self):
        """Should determine overall level."""
        low = FunctionMetrics(
            name="simple",
            file_path="",
            line_number=1,
            cyclomatic_complexity=3,
        )
        high = FunctionMetrics(
            name="complex",
            file_path="",
            line_number=1,
            cyclomatic_complexity=20,
        )

        assert low.overall_complexity == ComplexityLevel.LOW
        assert high.overall_complexity == ComplexityLevel.VERY_HIGH


class TestCalculateCyclomaticComplexity:
    """Tests for calculate_cyclomatic_complexity."""

    def test_simple_function(self):
        """Should calculate for simple function."""
        code = """
def simple():
    return 1
"""
        cc = calculate_cyclomatic_complexity(code)
        assert cc == 1

    def test_if_statement(self):
        """Should count if statements."""
        code = """
def check(x):
    if x > 0:
        return True
    return False
"""
        cc = calculate_cyclomatic_complexity(code)
        assert cc >= 2

    def test_loops(self):
        """Should count loops."""
        code = """
def loop(items):
    for item in items:
        while True:
            break
"""
        cc = calculate_cyclomatic_complexity(code)
        assert cc >= 3


class TestCountLines:
    """Tests for count_lines."""

    def test_count(self):
        """Should count line types."""
        code = '''# Comment
def foo():
    """Docstring"""
    x = 1

    return x
'''
        counts = count_lines(code)

        assert counts["total"] >= 6
        assert counts["code"] >= 1
        assert counts["comments"] >= 1
        assert counts["blank"] >= 1


class TestComplexityAnalyzer:
    """Tests for ComplexityAnalyzer."""

    def test_analyze_function(self):
        """Should analyze function."""
        code = """
def process(items):
    result = []
    for item in items:
        if item > 0:
            result.append(item)
    return result
"""
        analyzer = ComplexityAnalyzer()
        metrics = analyzer.analyze_function(code, "process")

        assert metrics.cyclomatic_complexity >= 3
        assert metrics.lines_of_code > 0

    def test_analyze_file(self):
        """Should analyze file."""
        code = """
def func1():
    return 1

def func2(x):
    if x:
        return x
    return 0
"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            f.flush()

            analyzer = ComplexityAnalyzer()
            metrics = analyzer.analyze_file(f.name)

        assert metrics.function_count == 2
        assert len(metrics.functions) == 2

    def test_high_complexity_functions(self):
        """Should identify high complexity functions."""
        analyzer = ComplexityAnalyzer(complexity_threshold=2)

        metrics = FileMetrics(file_path="test.py")
        metrics.functions = [
            FunctionMetrics("low", "", 1, cyclomatic_complexity=1),
            FunctionMetrics("high", "", 10, cyclomatic_complexity=5),
        ]

        high = analyzer.get_high_complexity_functions(metrics)

        assert len(high) == 1
        assert high[0].name == "high"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
