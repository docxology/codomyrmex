"""
Comprehensive code review functionality for Codomyrmex.

This module provides advanced static analysis capabilities including pyscn integration
for high-performance code quality assessment, security scanning, and maintainability analysis.
"""

import json
import os
import re
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any

# Import logger setup
from codomyrmex.logging_monitoring.core.logger_config import get_logger

# Import analyzer
from .analyzer import PyscnAnalyzer

# Import models from this module
from .models import (
    AnalysisResult,
    AnalysisSummary,
    ArchitectureViolation,
    CodeMetrics,
    ComplexityReductionSuggestion,
    DeadCodeFinding,
    Language,
    QualityDashboard,
    QualityGateResult,
    SeverityLevel,
)

logger = get_logger(__name__)

# Import performance monitoring
try:
    from codomyrmex.performance import monitor_performance, performance_context
    PERFORMANCE_MONITORING_AVAILABLE = True
except ImportError:
    logger.warning("Performance monitoring not available - decorators will be no-op")
    PERFORMANCE_MONITORING_AVAILABLE = False

    def monitor_performance(*args, **kwargs):
        """Decorator for performance monitoring (fallback)."""
        def decorator(func):
            """Execute Decorator operations natively."""

            return func
        return decorator

    class performance_context:
        """Functional component: performance_context."""

        def __init__(self, context_name: str = "unknown_context", *args, **kwargs):
            """Initialize performance context (fallback)."""
            self.context_name = context_name
            self.start_time = 0

        def __enter__(self):
            """Enter performance context."""
            self.start_time = time.time()
            logger.debug(f"Entering performance context: {self.context_name}")
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            """Exit performance context."""
            duration = time.time() - self.start_time
            logger.debug(f"Exiting performance context: {self.context_name} (Duration: {duration:.4f}s)")



from .reviewer_impl import (
    LintToolsMixin,
    AnalysisPatternsMixin,
    PerformanceOptMixin,
    DashboardMixin,
    ReportingMixin,
)


class CodeReviewer(
    LintToolsMixin,
    AnalysisPatternsMixin,
    PerformanceOptMixin,
    DashboardMixin,
    ReportingMixin,
):
    """Main code reviewer class with pyscn integration.

    Implementation is organized into five mixins for maintainability:
    - LintToolsMixin: External tool runners (pylint, flake8, mypy, bandit, vulture)
    - AnalysisPatternsMixin: Complexity, dead code, architecture analysis
    - PerformanceOptMixin: Performance optimization suggestions
    - DashboardMixin: Quality dashboard and metrics computation
    - ReportingMixin: HTML/JSON/Markdown report generation
    """

    def __init__(self, project_root: str = None, config_path: str = None):
        """
        Initialize the code reviewer.

        Args:
            project_root: Root directory of the project to analyze
            config_path: Path to configuration file
        """
        self.project_root = project_root or os.getcwd()
        self.config_path = config_path
        self.results: list[AnalysisResult] = []
        self.metrics: dict[str, CodeMetrics] = {}
        self.pyscn_analyzer = PyscnAnalyzer()

        # Load configuration
        self.config = self._load_config()

        # Check available tools
        self.tools_available = self._check_tools_availability()

    def _load_config(self) -> dict[str, Any]:
        """Load configuration from file or use defaults."""
        config = {
            "analysis_types": ["quality", "security", "style"],
            "max_complexity": 15,
            "min_clone_similarity": 0.8,
            "output_format": "html",
            "output_directory": "reports",
            "parallel_processing": True,
            "max_workers": 4,
            "quality_gates": {
                "max_complexity": 15,
                "max_clone_similarity": 0.8,
                "max_issues_per_file": 50
            },
            "pyscn": {
                "enabled": True,
                "auto_lsh": True,
                "lsh_threshold": 500
            }
        }

        # Try to load from .pyscn.toml or pyproject.toml
        if self.config_path and os.path.exists(self.config_path):
            try:
                import tomli
                with open(self.config_path, "rb") as f:
                    file_config = tomli.load(f)

                # Merge with defaults
                if "tool" in file_config and "pyscn" in file_config["tool"]:
                    config.update(file_config["tool"]["pyscn"])
                elif "pyscn" in file_config:
                    config.update(file_config["pyscn"])

            except Exception as e:
                logger.warning(f"Error loading config from {self.config_path}: {e}")

        return config

    def _check_tools_availability(self) -> dict[str, bool]:
        """Check which analysis tools are available."""
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
            "pyscn": True,  # We already checked this in PyscnAnalyzer
        }

        for tool in tools:
            if tool == "pyscn":
                continue  # Already verified

            try:
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

    def _should_analyze_file(self, file_path: str) -> bool:
        """Determine if a file should be analyzed."""
        supported_extensions = {
            ".py", ".js", ".ts", ".tsx", ".jsx", ".java",
            ".cpp", ".cc", ".cs", ".go", ".rs", ".php", ".rb"
        }
        return Path(file_path).suffix.lower() in supported_extensions

    def analyze_file(
        self, file_path: str, analysis_types: list[str] = None
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
            analysis_types = self.config["analysis_types"]

        file_results = []

        # Run pyscn analysis if enabled and file is Python
        file_results.extend(self._run_pyscn_analysis(file_path))

        # Run traditional analysis tools
        file_results.extend(self._run_traditional_analysis(file_path, analysis_types))

        self.results.extend(file_results)
        return file_results

    def analyze_project(
        self,
        target_paths: list[str] = None,
        analysis_types: list[str] = None,
    ) -> AnalysisSummary:
        """
        Analyze an entire project.

        Args:
            target_paths: List of paths to analyze (defaults to project root)
            analysis_types: Types of analysis to perform

        Returns:
            Analysis summary
        """
        if target_paths is None:
            target_paths = [self.project_root]

        if analysis_types is None:
            analysis_types = self.config["analysis_types"]

        start_time = time.time()
        files_analyzed = 0

        # Find all files to analyze
        files_to_analyze = []
        for target_path in target_paths:
            if os.path.isfile(target_path):
                if self._should_analyze_file(target_path):
                    files_to_analyze.append(target_path)
            else:
                for root, dirs, files in os.walk(target_path):
                    # Skip common directories
                    dirs[:] = [d for d in dirs if d not in {".git", "__pycache__", "node_modules", ".venv", "venv"}]

                    for file in files:
                        file_path = os.path.join(root, file)
                        if self._should_analyze_file(file_path):
                            files_to_analyze.append(file_path)

        # Analyze each file
        for file_path in files_to_analyze:
            try:
                self.analyze_file(file_path, analysis_types)
                files_analyzed += 1
            except Exception as e:
                logger.error(f"Error analyzing file {file_path}: {e}")

        analysis_time = time.time() - start_time

        # Generate summary
        summary = self._generate_summary(files_analyzed, analysis_time)

        return summary

    def _generate_summary(self, files_analyzed: int, analysis_time: float) -> AnalysisSummary:
        """Generate analysis summary."""
        summary = AnalysisSummary(
            total_issues=len(self.results),
            files_analyzed=files_analyzed,
            analysis_time=analysis_time,
        )

        # Count by severity and category
        for result in self.results:
            summary.by_severity[result.severity] = (
                summary.by_severity.get(result.severity, 0) + 1
            )
            summary.by_category[result.category] = (
                summary.by_category.get(result.category, 0) + 1
            )
            summary.by_rule[result.rule_id] = summary.by_rule.get(result.rule_id, 0) + 1

        return summary

    def check_quality_gates(self, thresholds: dict[str, int] = None) -> QualityGateResult:
        """Check if code meets quality standards."""
        if thresholds is None:
            thresholds = self.config["quality_gates"]

        failures = []
        passed_checks = 0
        total_checks = 0

        # Check complexity
        total_checks += 1
        max_complexity = thresholds.get("max_complexity", 15)
        complexity_issues = [r for r in self.results if r.rule_id == "PYSCN_COMPLEXITY"]
        if len(complexity_issues) > 0:
            failures.append({
                "gate": "max_complexity",
                "threshold": max_complexity,
                "actual": len(complexity_issues),
                "message": f"Found {len(complexity_issues)} high complexity issues"
            })
        else:
            passed_checks += 1

        # Check total issues per file
        total_checks += 1
        max_issues = thresholds.get("max_issues_per_file", 50)
        files_with_too_many_issues = {}

        for result in self.results:
            file_path = result.file_path
            if file_path not in files_with_too_many_issues:
                files_with_too_many_issues[file_path] = 0
            files_with_too_many_issues[file_path] += 1

        problematic_files = {f: c for f, c in files_with_too_many_issues.items() if c > max_issues}
        if problematic_files:
            failures.append({
                "gate": "max_issues_per_file",
                "threshold": max_issues,
                "actual": problematic_files,
                "message": f"Found {len(problematic_files)} files with too many issues"
            })
        else:
            passed_checks += 1

        return QualityGateResult(
            passed=len(failures) == 0,
            total_checks=total_checks,
            passed_checks=passed_checks,
            failed_checks=len(failures),
            failures=failures
        )

    def clear_results(self):
        """Clear all analysis results."""
        self.results.clear()
        self.metrics.clear()

