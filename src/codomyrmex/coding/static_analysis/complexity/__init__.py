"""
Complexity analysis submodule for static analysis.

Provides cyclomatic complexity calculation, line counting,
and function/file-level metrics.
"""

import ast
import re
from dataclasses import dataclass, field
from enum import Enum
import logging
logger = logging.getLogger(__name__)


class ComplexityLevel(Enum):
    """Complexity classification levels."""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"


def _level_from_value(value: int) -> ComplexityLevel:
    """Map a numeric complexity value to a level."""
    if value <= 5:
        return ComplexityLevel.LOW
    elif value <= 10:
        return ComplexityLevel.MODERATE
    elif value < 20:
        return ComplexityLevel.HIGH
    else:
        return ComplexityLevel.VERY_HIGH


@dataclass
class ComplexityMetric:
    """A single complexity measurement."""
    name: str
    value: int
    level: ComplexityLevel

    @classmethod
    def from_value(cls, name: str, value: int) -> "ComplexityMetric":
        """Create a metric with auto-determined level."""
        return cls(name=name, value=value, level=_level_from_value(value))


@dataclass
class FunctionMetrics:
    """Metrics for a single function."""
    name: str
    file_path: str
    line_number: int
    cyclomatic_complexity: int = 1
    lines_of_code: int = 0
    parameter_count: int = 0

    @property
    def overall_complexity(self) -> ComplexityLevel:
        """Determine overall complexity level from cyclomatic complexity."""
        return _level_from_value(self.cyclomatic_complexity)


@dataclass
class FileMetrics:
    """Metrics for a file."""
    file_path: str
    functions: list[FunctionMetrics] = field(default_factory=list)

    @property
    def function_count(self) -> int:
        """function Count ."""
        return len(self.functions)

    @property
    def average_complexity(self) -> float:
        """average Complexity ."""
        if not self.functions:
            return 0.0
        return sum(f.cyclomatic_complexity for f in self.functions) / len(self.functions)


def calculate_cyclomatic_complexity(code: str) -> int:
    """Calculate cyclomatic complexity for a code snippet.

    Counts decision points: if, elif, for, while, except, and, or,
    assert, with, comprehension conditions.

    Args:
        code: Python source code string.

    Returns:
        Cyclomatic complexity number (minimum 1).
    """
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        logger.debug("Cannot compute complexity, invalid syntax: %s", e)
        return 1

    complexity = 1
    for node in ast.walk(tree):
        if isinstance(node, (ast.If, ast.IfExp)):
            complexity += 1
        elif isinstance(node, ast.For):
            complexity += 1
        elif isinstance(node, ast.While):
            complexity += 1
        elif isinstance(node, ast.ExceptHandler):
            complexity += 1
        elif isinstance(node, ast.Assert):
            complexity += 1
        elif isinstance(node, ast.With):
            complexity += 1
        elif isinstance(node, ast.BoolOp):
            # Each 'and'/'or' adds a decision point
            complexity += len(node.values) - 1

    return complexity


def count_lines(code: str) -> dict[str, int]:
    """Count different types of lines in source code.

    Args:
        code: Python source code string.

    Returns:
        Dictionary with keys: total, code, comments, blank, docstrings.
    """
    lines = code.split("\n")
    total = len(lines)
    blank = 0
    comments = 0
    code_lines = 0

    in_docstring = False
    for line in lines:
        stripped = line.strip()

        if not stripped:
            blank += 1
            continue

        # Track triple-quote docstrings
        triple_count = stripped.count('"""') + stripped.count("'''")
        if triple_count >= 2:
            # Single-line docstring
            comments += 1
            continue
        elif triple_count == 1:
            in_docstring = not in_docstring
            comments += 1
            continue

        if in_docstring:
            comments += 1
            continue

        if stripped.startswith("#"):
            comments += 1
        else:
            code_lines += 1

    return {
        "total": total,
        "code": code_lines,
        "comments": comments,
        "blank": blank,
    }


class ComplexityAnalyzer:
    """Analyze complexity of Python code."""

    def __init__(self, complexity_threshold: int = 10):
        """Initialize analyzer.

        Args:
            complexity_threshold: Threshold above which a function is
                considered high complexity.
        """
        self.complexity_threshold = complexity_threshold

    def analyze_function(self, code: str, function_name: str) -> FunctionMetrics:
        """Analyze a single function within code.

        Args:
            code: Source code containing the function.
            function_name: Name of the function to analyze.

        Returns:
            FunctionMetrics for the target function.
        """
        cc = calculate_cyclomatic_complexity(code)
        loc = len([ln for ln in code.strip().split("\n") if ln.strip()])
        return FunctionMetrics(
            name=function_name,
            file_path="",
            line_number=1,
            cyclomatic_complexity=cc,
            lines_of_code=loc,
        )

    def analyze_file(self, file_path: str) -> FileMetrics:
        """Analyze all functions in a file.

        Args:
            file_path: Path to the Python file.

        Returns:
            FileMetrics with per-function breakdowns.
        """
        with open(file_path) as f:
            source = f.read()

        try:
            tree = ast.parse(source)
        except SyntaxError:
            return FileMetrics(file_path=file_path)

        metrics = FileMetrics(file_path=file_path)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                func_source = ast.get_source_segment(source, node) or ""
                cc = calculate_cyclomatic_complexity(func_source)
                loc = len([ln for ln in func_source.split("\n") if ln.strip()])
                fm = FunctionMetrics(
                    name=node.name,
                    file_path=file_path,
                    line_number=node.lineno,
                    cyclomatic_complexity=cc,
                    lines_of_code=loc,
                    parameter_count=len(node.args.args),
                )
                metrics.functions.append(fm)

        return metrics

    def get_high_complexity_functions(
        self, metrics: FileMetrics
    ) -> list[FunctionMetrics]:
        """Return functions exceeding the complexity threshold.

        Args:
            metrics: FileMetrics to filter.

        Returns:
            List of FunctionMetrics above threshold.
        """
        return [
            f for f in metrics.functions
            if f.cyclomatic_complexity > self.complexity_threshold
        ]


__all__ = [
    "ComplexityLevel",
    "ComplexityMetric",
    "FunctionMetrics",
    "FileMetrics",
    "ComplexityAnalyzer",
    "calculate_cyclomatic_complexity",
    "count_lines",
]
