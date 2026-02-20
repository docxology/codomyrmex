"""AST-based anti-pattern detection for Python source code.

Scans Python files for common code smells and anti-patterns using
the ``ast`` module.  Each detector returns structured findings with
severity, location, and suggested fixes.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class Severity(Enum):
    """Severity level for detected anti-patterns."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class AntiPattern:
    """A detected anti-pattern.

    Attributes:
        name: Pattern identifier (e.g. ``god-function``).
        message: Human-readable description.
        severity: Severity level.
        file: Source file path.
        line: Line number.
        suggestion: Suggested fix.
    """

    name: str
    message: str
    severity: Severity = Severity.WARNING
    file: str = ""
    line: int = 0
    suggestion: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "message": self.message,
            "severity": self.severity.value,
            "file": self.file,
            "line": self.line,
            "suggestion": self.suggestion,
        }


@dataclass
class AnalysisReport:
    """Aggregated report from anti-pattern analysis.

    Attributes:
        patterns: List of detected anti-patterns.
        files_scanned: Number of files analyzed.
        total_lines: Total lines of code analyzed.
    """

    patterns: list[AntiPattern] = field(default_factory=list)
    files_scanned: int = 0
    total_lines: int = 0

    @property
    def count_by_severity(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for p in self.patterns:
            key = p.severity.value
            counts[key] = counts.get(key, 0) + 1
        return counts

    @property
    def has_errors(self) -> bool:
        return any(p.severity == Severity.ERROR for p in self.patterns)

    def to_dict(self) -> dict[str, Any]:
        return {
            "patterns": [p.to_dict() for p in self.patterns],
            "files_scanned": self.files_scanned,
            "total_lines": self.total_lines,
            "count_by_severity": self.count_by_severity,
        }


class AntiPatternDetector:
    """Detect common Python anti-patterns via AST analysis.

    Configurable thresholds control sensitivity.

    Usage::

        detector = AntiPatternDetector()
        report = detector.analyze_source(source_code, "module.py")
        for pattern in report.patterns:
            print(f"{pattern.name}: {pattern.message} (line {pattern.line})")
    """

    def __init__(
        self,
        max_function_lines: int = 50,
        max_params: int = 6,
        max_complexity: int = 10,
        max_nesting: int = 4,
    ) -> None:
        self._max_function_lines = max_function_lines
        self._max_params = max_params
        self._max_complexity = max_complexity
        self._max_nesting = max_nesting

    def analyze_source(
        self,
        source: str,
        filename: str = "<string>",
    ) -> AnalysisReport:
        """Analyze Python source code for anti-patterns.

        Args:
            source: Python source code string.
            filename: File name for error reporting.

        Returns:
            ``AnalysisReport`` with all detected patterns.
        """
        report = AnalysisReport(files_scanned=1, total_lines=source.count("\n") + 1)

        try:
            tree = ast.parse(source, filename=filename)
        except SyntaxError as exc:
            report.patterns.append(AntiPattern(
                name="syntax-error",
                message=f"Cannot parse: {exc}",
                severity=Severity.ERROR,
                file=filename,
                line=getattr(exc, "lineno", 0) or 0,
            ))
            return report

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self._check_function(node, filename, report)
            elif isinstance(node, ast.ClassDef):
                self._check_class(node, filename, report)

        logger.info(
            "Anti-pattern scan complete",
            extra={
                "file": filename,
                "patterns": len(report.patterns),
                "lines": report.total_lines,
            },
        )

        return report

    def _check_function(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
        filename: str,
        report: AnalysisReport,
    ) -> None:
        """Check a function for anti-patterns."""
        # God function: too many lines
        if hasattr(node, "end_lineno") and node.end_lineno:
            func_lines = node.end_lineno - node.lineno + 1
            if func_lines > self._max_function_lines:
                report.patterns.append(AntiPattern(
                    name="god-function",
                    message=f"Function '{node.name}' is {func_lines} lines "
                            f"(max {self._max_function_lines})",
                    severity=Severity.WARNING,
                    file=filename,
                    line=node.lineno,
                    suggestion="Split into smaller, focused functions",
                ))

        # Too many parameters
        params = node.args
        param_count = (
            len(params.args)
            + len(params.posonlyargs)
            + len(params.kwonlyargs)
        )
        if param_count > self._max_params:
            report.patterns.append(AntiPattern(
                name="too-many-params",
                message=f"Function '{node.name}' has {param_count} parameters "
                        f"(max {self._max_params})",
                severity=Severity.WARNING,
                file=filename,
                line=node.lineno,
                suggestion="Use a config dataclass or kwargs",
            ))

        # Deeply nested code
        max_depth = self._measure_nesting(node.body)
        if max_depth > self._max_nesting:
            report.patterns.append(AntiPattern(
                name="deep-nesting",
                message=f"Function '{node.name}' has nesting depth {max_depth} "
                        f"(max {self._max_nesting})",
                severity=Severity.WARNING,
                file=filename,
                line=node.lineno,
                suggestion="Use early returns or extract helper functions",
            ))

        # Bare except
        for child in ast.walk(node):
            if isinstance(child, ast.ExceptHandler) and child.type is None:
                report.patterns.append(AntiPattern(
                    name="bare-except",
                    message=f"Bare 'except' in '{node.name}'",
                    severity=Severity.ERROR,
                    file=filename,
                    line=getattr(child, "lineno", node.lineno),
                    suggestion="Catch specific exceptions",
                ))

    def _check_class(
        self,
        node: ast.ClassDef,
        filename: str,
        report: AnalysisReport,
    ) -> None:
        """Check a class for anti-patterns."""
        methods = [n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
        if len(methods) > 20:
            report.patterns.append(AntiPattern(
                name="god-class",
                message=f"Class '{node.name}' has {len(methods)} methods (max 20)",
                severity=Severity.WARNING,
                file=filename,
                line=node.lineno,
                suggestion="Apply Single Responsibility Principle",
            ))

    def _measure_nesting(self, body: list[ast.stmt], depth: int = 0) -> int:
        """Recursively measure max nesting depth."""
        max_depth = depth
        for stmt in body:
            for child_body_name in ("body", "orelse", "finalbody", "handlers"):
                child_body = getattr(stmt, child_body_name, None)
                if isinstance(child_body, list) and child_body:
                    child_depth = self._measure_nesting(child_body, depth + 1)
                    max_depth = max(max_depth, child_depth)
        return max_depth


__all__ = [
    "AntiPattern",
    "AntiPatternDetector",
    "AnalysisReport",
    "Severity",
]
