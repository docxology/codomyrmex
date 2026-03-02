"""Comprehensive static analysis functionality for Codomyrmex.

This module provides advanced static analysis capabilities including code quality,
security analysis, performance analysis, and maintainability assessment.
"""

import ast

# from performance import monitor_performance, performance_context # Moved to try/except
import csv
import json
import math
import os
import time
from pathlib import Path

from codomyrmex.logging_monitoring.core.logger_config import get_logger
from codomyrmex.model_context_protocol.decorators import mcp_tool

from .models import (
    AnalysisResult,
    AnalysisSummary,
    AnalysisType,
    CodeMetrics,
    Language,
    SeverityLevel,
)
from .tool_runners import ToolRunner

# Get module logger
logger = get_logger(__name__)

# Import performance monitoring
try:
    from codomyrmex.performance import monitor_performance, performance_context
    PERFORMANCE_MONITORING_AVAILABLE = True
except ImportError:
    logger.warning("Performance monitoring not available - decorators will be no-op")
    PERFORMANCE_MONITORING_AVAILABLE = False

    def monitor_performance(*args, **kwargs):
        def decorator(func):
            """decorator ."""
            return func

        return decorator

    class performance_context:
        """Functional component: performance_context."""
        def __init__(self, *args, **kwargs):
            return None  # Intentional no-op

        def __enter__(self):
            """enter ."""
            return self

        def __exit__(self, *args):
            """exit ."""
            return None  # Intentional no-op


class StaticAnalyzer:
    """Main static analyzer class."""

    def __init__(self, project_root: str = None):
        """
        Initialize the static analyzer.

        Args:
            project_root: Root directory of the project to analyze
        """
        self.project_root = project_root or os.getcwd()
        self.results: list[AnalysisResult] = []
        self.metrics: dict[str, CodeMetrics] = {}
        self.tools_available = self._check_tools_availability()
        self.tool_runner = ToolRunner(self.tools_available, self.project_root)

    def _check_tools_availability(self) -> dict[str, bool]:
        """Check which analysis tools are available."""
        import subprocess

        tools = {
            "pylint": False,
            "flake8": False,
            "mypy": False,
            "bandit": False,
            "black": False,
            "isort": False,
            "pytest": False,
            "coverage": False,
            "radon": False,
            "vulture": False,
            "safety": False,
            "semgrep": False,
            "pyrefly": False,
        }

        for tool in tools:
            try:
                if tool == "pyrefly":
                    subprocess.run(
                        ["pyrefly", "--version"], capture_output=True, check=True, timeout=5
                    )
                else:
                    subprocess.run(
                        [tool, "--version"], capture_output=True, check=True, timeout=5
                    )
                tools[tool] = True
            except (
                subprocess.CalledProcessError,
                FileNotFoundError,
                subprocess.TimeoutExpired,
            ):
                tools[tool] = False

        return tools

    @mcp_tool()
    @monitor_performance("analyze_file")
    def analyze_file(
        self, file_path: str, analysis_types: list[AnalysisType] = None
    ) -> list[AnalysisResult]:
        """
        Analyze a single file for various issues.

        Args:
            file_path: Path to the file to analyze
            analysis_types: Types of analysis to perform

        Returns:
            List of analysis results
        """
        if analysis_types is None:
            analysis_types = [
                AnalysisType.QUALITY,
                AnalysisType.SECURITY,
                AnalysisType.STYLE,
            ]

        file_results = []

        # Determine file language
        language = self._detect_language(file_path)

        # Run different analysis tools based on language and requested types
        if language == Language.PYTHON:
            file_results.extend(self._analyze_python_file(file_path, analysis_types))
        elif language in [Language.JAVASCRIPT, Language.TYPESCRIPT]:
            file_results.extend(
                self._analyze_javascript_file(file_path, analysis_types)
            )
        elif language == Language.JAVA:
            file_results.extend(self._analyze_java_file(file_path, analysis_types))
        else:
            logger.warning(f"Unsupported language for file: {file_path}")

        self.results.extend(file_results)
        return file_results

    def _detect_language(self, file_path: str) -> Language:
        """Detect the programming language of a file."""
        extension = Path(file_path).suffix.lower()

        language_map = {
            ".py": Language.PYTHON,
            ".js": Language.JAVASCRIPT,
            ".ts": Language.TYPESCRIPT,
            ".tsx": Language.TYPESCRIPT,
            ".jsx": Language.JAVASCRIPT,
            ".java": Language.JAVA,
            ".cpp": Language.CPP,
            ".cc": Language.CPP,
            ".cxx": Language.CPP,
            ".cs": Language.CSHARP,
            ".go": Language.GO,
            ".rs": Language.RUST,
            ".php": Language.PHP,
            ".rb": Language.RUBY,
        }

        return language_map.get(extension, Language.PYTHON)

    def _analyze_python_file(
        self, file_path: str, analysis_types: list[AnalysisType]
    ) -> list[AnalysisResult]:
        """Analyze a Python file."""
        results = []

        if AnalysisType.QUALITY in analysis_types and self.tools_available["pylint"]:
            results.extend(self.tool_runner.run_pylint(file_path))

        if AnalysisType.STYLE in analysis_types and self.tools_available["flake8"]:
            results.extend(self.tool_runner.run_flake8(file_path))

        if AnalysisType.QUALITY in analysis_types and self.tools_available["mypy"]:
            results.extend(self.tool_runner.run_mypy(file_path))

        if AnalysisType.SECURITY in analysis_types and self.tools_available["bandit"]:
            results.extend(self.tool_runner.run_bandit(file_path))

        if AnalysisType.COMPLEXITY in analysis_types and self.tools_available["radon"]:
            results.extend(self.tool_runner.run_radon(file_path))

        if AnalysisType.QUALITY in analysis_types and self.tools_available["vulture"]:
            results.extend(self.tool_runner.run_vulture(file_path))

        if AnalysisType.SECURITY in analysis_types and self.tools_available["safety"]:
            results.extend(self.tool_runner.run_safety(file_path))

        if AnalysisType.QUALITY in analysis_types and self.tools_available["pyrefly"]:
            results.extend(self.tool_runner.run_pyrefly(file_path))

        return results

    def _analyze_javascript_file(
        self, file_path: str, analysis_types: list[AnalysisType]
    ) -> list[AnalysisResult]:
        """Analyze a JavaScript/TypeScript file."""
        results = []

        if AnalysisType.QUALITY in analysis_types and self.tools_available.get(
            "eslint", False
        ):
            results.extend(self.tool_runner.run_eslint(file_path))

        if AnalysisType.QUALITY in analysis_types and file_path.endswith(
            (".ts", ".tsx")
        ):
            results.extend(self.tool_runner.run_typescript_compiler(file_path))

        return results

    def _analyze_java_file(
        self, file_path: str, analysis_types: list[AnalysisType]
    ) -> list[AnalysisResult]:
        """Analyze a Java file."""
        results = []

        if AnalysisType.QUALITY in analysis_types and self.tools_available.get(
            "spotbugs", False
        ):
            results.extend(self.tool_runner.run_spotbugs(file_path))

        return results

    @mcp_tool()
    @monitor_performance("analyze_project")
    def analyze_project(
        self,
        target_paths: list[str] = None,
        analysis_types: list[AnalysisType] = None,
        exclude_patterns: list[str] = None,
    ) -> AnalysisSummary:
        """
        Analyze an entire project.

        Args:
            target_paths: List of paths to analyze (defaults to project root)
            analysis_types: Types of analysis to perform
            exclude_patterns: Patterns to exclude from analysis

        Returns:
            Analysis summary
        """
        if target_paths is None:
            target_paths = [self.project_root]

        if analysis_types is None:
            analysis_types = [
                AnalysisType.QUALITY,
                AnalysisType.SECURITY,
                AnalysisType.STYLE,
            ]

        if exclude_patterns is None:
            exclude_patterns = ["__pycache__", ".git", "node_modules", ".venv", "venv"]

        start_time = time.time()
        files_analyzed = 0

        files_to_analyze = []
        for target_path in target_paths:
            if os.path.isfile(target_path):
                files_to_analyze.append(target_path)
            else:
                for root, dirs, files in os.walk(target_path):
                    dirs[:] = [
                        d
                        for d in dirs
                        if not any(pattern in d for pattern in exclude_patterns)
                    ]

                    for file in files:
                        file_path = os.path.join(root, file)
                        if self._should_analyze_file(file_path):
                            files_to_analyze.append(file_path)

        for file_path in files_to_analyze:
            try:
                self.analyze_file(file_path, analysis_types)
                files_analyzed += 1
            except Exception as e:
                logger.error(f"Error analyzing file {file_path}: {e}")

        analysis_time = time.time() - start_time

        summary = self._generate_summary(files_analyzed, analysis_time)

        return summary

    def _should_analyze_file(self, file_path: str) -> bool:
        """Determine if a file should be analyzed."""
        supported_extensions = {
            ".py",
            ".js",
            ".ts",
            ".tsx",
            ".jsx",
            ".java",
            ".cpp",
            ".cc",
            ".cs",
            ".go",
            ".rs",
            ".php",
            ".rb",
        }
        return Path(file_path).suffix.lower() in supported_extensions

    def _generate_summary(
        self, files_analyzed: int, analysis_time: float
    ) -> AnalysisSummary:
        """Generate analysis summary."""
        summary = AnalysisSummary(
            total_issues=len(self.results),
            files_analyzed=files_analyzed,
            analysis_time=analysis_time,
        )

        for result in self.results:
            summary.by_severity[result.severity] = (
                summary.by_severity.get(result.severity, 0) + 1
            )
            summary.by_category[result.category] = (
                summary.by_category.get(result.category, 0) + 1
            )
            summary.by_rule[result.rule_id] = summary.by_rule.get(result.rule_id, 0) + 1

        return summary

    @monitor_performance("calculate_metrics")
    def calculate_metrics(self, file_path: str) -> CodeMetrics:
        """Calculate code quality metrics for a file."""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            lines_of_code = len(
                [
                    line
                    for line in content.split("\n")
                    if line.strip() and not line.strip().startswith("#")
                ]
            )

            cyclomatic_complexity = self._calculate_cyclomatic_complexity(content)

            maintainability_index = max(
                0, 171 - 5.2 * math.log(cyclomatic_complexity) - 0.23 * lines_of_code
            )

            technical_debt = len(self.results) * 0.1  # 0.1 hours per issue

            code_duplication = self._calculate_code_duplication(content)

            metrics = CodeMetrics(
                lines_of_code=lines_of_code,
                cyclomatic_complexity=cyclomatic_complexity,
                maintainability_index=maintainability_index,
                technical_debt=technical_debt,
                code_duplication=code_duplication,
            )

            self.metrics[file_path] = metrics
            return metrics

        except Exception as e:
            logger.error(f"Error calculating metrics for {file_path}: {e}")
            return CodeMetrics(0, 0, 0, 0, 0)

    def _calculate_cyclomatic_complexity(self, content: str) -> int:
        """Calculate cyclomatic complexity."""
        try:
            tree = ast.parse(content)
            complexity = 1  # Base complexity

            for node in ast.walk(tree):
                if isinstance(
                    node,
                    (
                        ast.If,
                        ast.While,
                        ast.For,
                        ast.AsyncFor,
                        ast.ExceptHandler,
                        ast.With,
                        ast.AsyncWith,
                    ),
                ):
                    complexity += 1
                elif isinstance(node, ast.BoolOp):
                    complexity += len(node.values) - 1

            return complexity
        except SyntaxError as e:
            logger.debug("Cannot compute complexity for file with syntax error: %s", e)
            return 1

    def _calculate_code_duplication(self, content: str) -> float:
        """Calculate code duplication percentage."""
        lines = [
            line.strip()
            for line in content.split("\n")
            if line.strip() and not line.strip().startswith("#")
        ]

        if not lines:
            return 0.0

        line_counts = {}
        for line in lines:
            line_counts[line] = line_counts.get(line, 0) + 1

        duplicated_lines = sum(count - 1 for count in line_counts.values() if count > 1)
        return (duplicated_lines / len(lines)) * 100

    def get_results_by_severity(self, severity: SeverityLevel) -> list[AnalysisResult]:
        """Get results filtered by severity."""
        return [result for result in self.results if result.severity == severity]

    def get_results_by_category(self, category: str) -> list[AnalysisResult]:
        """Get results filtered by category."""
        return [result for result in self.results if result.category == category]

    def get_results_by_file(self, file_path: str) -> list[AnalysisResult]:
        """Get results for a specific file."""
        return [result for result in self.results if result.file_path == file_path]

    def export_results(self, output_path: str, format: str = "json") -> bool:
        """Export analysis results to a file."""
        try:
            if format.lower() == "json":
                with open(output_path, "w") as f:
                    json.dump(
                        [
                            {
                                "file_path": result.file_path,
                                "line_number": result.line_number,
                                "column_number": result.column_number,
                                "severity": result.severity.value,
                                "message": result.message,
                                "rule_id": result.rule_id,
                                "category": result.category,
                                "suggestion": result.suggestion,
                                "context": result.context,
                                "fix_available": result.fix_available,
                                "confidence": result.confidence,
                            }
                            for result in self.results
                        ],
                        f,
                        indent=2,
                    )

            elif format.lower() == "csv":
                with open(output_path, "w", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(
                        [
                            "File",
                            "Line",
                            "Column",
                            "Severity",
                            "Message",
                            "Rule",
                            "Category",
                            "Suggestion",
                        ]
                    )
                    for result in self.results:
                        writer.writerow(
                            [
                                result.file_path,
                                result.line_number,
                                result.column_number,
                                result.severity.value,
                                result.message,
                                result.rule_id,
                                result.category,
                                result.suggestion or "",
                            ]
                        )

            else:
                logger.error(f"Unsupported export format: {format}")
                return False

            logger.info(f"Results exported to {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error exporting results: {e}")
            return False

    def clear_results(self):
        """Clear all analysis results."""
        self.results.clear()
        self.metrics.clear()


# Convenience functions
@mcp_tool()
def analyze_file(
    file_path: str, analysis_types: list[AnalysisType] = None
) -> list[AnalysisResult]:
    """Analyze a single file."""
    analyzer = StaticAnalyzer()
    return analyzer.analyze_file(file_path, analysis_types)


@mcp_tool()
def analyze_project(
    project_root: str,
    target_paths: list[str] = None,
    analysis_types: list[AnalysisType] = None,
) -> AnalysisSummary:
    """Analyze an entire project."""
    analyzer = StaticAnalyzer(project_root)
    return analyzer.analyze_project(target_paths, analysis_types)


def get_available_tools() -> dict[str, bool]:
    """Get list of available analysis tools."""
    analyzer = StaticAnalyzer()
    return analyzer.tools_available
