from pathlib import Path
from typing import Optional
import ast
import json
import math
import os
import re
import subprocess
import sys
import time

from dataclasses import dataclass, field
from enum import Enum
from performance import monitor_performance, performance_context
import csv

from codomyrmex.logging_monitoring.logger_config import get_logger
from codomyrmex.static_analysis.pyrefly_runner import run_pyrefly_analysis






"""
Comprehensive static analysis functionality for Codomyrmex.

This module provides advanced static analysis capabilities including code quality,
security analysis, performance analysis, and maintainability assessment.
"""


# Add project root to Python path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
if PROJECT_ROOT not in sys.path:
    pass
#     sys.path.insert(0, PROJECT_ROOT)  # Removed sys.path manipulation

# Import logger setup

# Get module logger
logger = get_logger(__name__)

# Import performance monitoring
try:

    PERFORMANCE_MONITORING_AVAILABLE = True
except ImportError:
    logger.warning("Performance monitoring not available - decorators will be no-op")
    PERFORMANCE_MONITORING_AVAILABLE = False

    def monitor_performance(*args, **kwargs):
        def decorator(func):
            return func

        return decorator

    class performance_context:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass


# Enums for analysis types and severity levels
class AnalysisType(Enum):
    """Types of static analysis."""

    QUALITY = "quality"
    SECURITY = "security"
    PERFORMANCE = "performance"
    MAINTAINABILITY = "maintainability"
    COMPLEXITY = "complexity"
    STYLE = "style"
    DOCUMENTATION = "documentation"
    TESTING = "testing"


class SeverityLevel(Enum):
    """Severity levels for analysis results."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class Language(Enum):
    """Supported programming languages."""

    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    CPP = "cpp"
    CSHARP = "csharp"
    GO = "go"
    RUST = "rust"
    PHP = "php"
    RUBY = "ruby"


@dataclass
class AnalysisResult:
    """Result of a static analysis operation."""

    file_path: str
    line_number: int
    column_number: int
    severity: SeverityLevel
    message: str
    rule_id: str
    category: str
    suggestion: Optional[str] = None
    context: Optional[str] = None
    fix_available: bool = False
    confidence: float = 1.0


@dataclass
class AnalysisSummary:
    """Summary of analysis results for a file or project."""

    total_issues: int
    by_severity: dict[SeverityLevel, int] = field(default_factory=dict)
    by_category: dict[str, int] = field(default_factory=dict)
    by_rule: dict[str, int] = field(default_factory=dict)
    files_analyzed: int = 0
    analysis_time: float = 0.0
    language: Optional[Language] = None


@dataclass
class CodeMetrics:
    """Code quality metrics."""

    lines_of_code: int
    cyclomatic_complexity: int
    maintainability_index: float
    technical_debt: float
    code_duplication: float
    test_coverage: Optional[float] = None
    documentation_coverage: Optional[float] = None


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
            "pyrefly": False,
        }

        for tool in tools:
            try:
                if tool == "pyrefly":
                    # Pyrefly uses 'pyrefly check --version' or just 'pyrefly --version'
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

        # Pylint analysis
        if AnalysisType.QUALITY in analysis_types and self.tools_available["pylint"]:
            results.extend(self._run_pylint(file_path))

        # Flake8 analysis
        if AnalysisType.STYLE in analysis_types and self.tools_available["flake8"]:
            results.extend(self._run_flake8(file_path))

        # MyPy type checking
        if AnalysisType.QUALITY in analysis_types and self.tools_available["mypy"]:
            results.extend(self._run_mypy(file_path))

        # Bandit security analysis
        if AnalysisType.SECURITY in analysis_types and self.tools_available["bandit"]:
            results.extend(self._run_bandit(file_path))

        # Radon complexity analysis
        if AnalysisType.COMPLEXITY in analysis_types and self.tools_available["radon"]:
            results.extend(self._run_radon(file_path))

        # Vulture dead code analysis
        if AnalysisType.QUALITY in analysis_types and self.tools_available["vulture"]:
            results.extend(self._run_vulture(file_path))

        # Safety dependency analysis
        if AnalysisType.SECURITY in analysis_types and self.tools_available["safety"]:
            results.extend(self._run_safety(file_path))

        # Pyrefly type checking
        if AnalysisType.QUALITY in analysis_types and self.tools_available["pyrefly"]:
            results.extend(self._run_pyrefly(file_path))

        return results

    def _run_pylint(self, file_path: str) -> list[AnalysisResult]:
        """Run pylint analysis on a file."""
        results = []

        try:
            cmd = ["pylint", "--output-format=json", file_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode != 0 and result.stdout:
                pylint_results = json.loads(result.stdout)

                for issue in pylint_results:
                    severity_map = {
                        "convention": SeverityLevel.INFO,
                        "refactor": SeverityLevel.WARNING,
                        "warning": SeverityLevel.WARNING,
                        "error": SeverityLevel.ERROR,
                        "fatal": SeverityLevel.CRITICAL,
                    }

                    results.append(
                        AnalysisResult(
                            file_path=issue["path"],
                            line_number=issue["line"],
                            column_number=issue["column"],
                            severity=severity_map.get(
                                issue["type"], SeverityLevel.WARNING
                            ),
                            message=issue["message"],
                            rule_id=issue["message-id"],
                            category="pylint",
                            suggestion=issue.get("suggestion"),
                            context=issue.get("context"),
                        )
                    )

        except (subprocess.TimeoutExpired, json.JSONDecodeError, Exception) as e:
            logger.error(f"Error running pylint on {file_path}: {e}")

        return results

    def _run_flake8(self, file_path: str) -> list[AnalysisResult]:
        """Run flake8 analysis on a file."""
        results = []

        try:
            cmd = [
                "flake8",
                "--format=%(path)s:%(row)d:%(col)d: %(code)s %(text)s",
                file_path,
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.stdout:
                for line in result.stdout.strip().split("\n"):
                    if ":" in line:
                        parts = line.split(":", 3)
                        if len(parts) >= 4:
                            file_path, line_num, col_num, message = parts

                            # Parse flake8 error codes
                            code_match = re.match(r"^([A-Z]\d{3})", message.strip())
                            rule_id = code_match.group(1) if code_match else "E999"

                            # Determine severity based on error code
                            severity = SeverityLevel.WARNING
                            if rule_id.startswith("E"):
                                severity = SeverityLevel.ERROR
                            elif rule_id.startswith("W"):
                                severity = SeverityLevel.WARNING
                            elif rule_id.startswith("F"):
                                severity = SeverityLevel.ERROR

                            results.append(
                                AnalysisResult(
                                    file_path=file_path,
                                    line_number=int(line_num),
                                    column_number=int(col_num),
                                    severity=severity,
                                    message=message.strip(),
                                    rule_id=rule_id,
                                    category="flake8",
                                )
                            )

        except (subprocess.TimeoutExpired, Exception) as e:
            logger.error(f"Error running flake8 on {file_path}: {e}")

        return results

    def _run_mypy(self, file_path: str) -> list[AnalysisResult]:
        """Run mypy type checking on a file."""
        results = []

        try:
            cmd = ["mypy", "--show-error-codes", "--no-error-summary", file_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.stdout:
                for line in result.stdout.strip().split("\n"):
                    if ":" in line and "error:" in line:
                        # Parse mypy output format
                        match = re.match(
                            r"([^:]+):(\d+):(\d+): error: (.+) \[([^\]]+)\]", line
                        )
                        if match:
                            file_path, line_num, col_num, message, error_code = (
                                match.groups()
                            )

                            results.append(
                                AnalysisResult(
                                    file_path=file_path,
                                    line_number=int(line_num),
                                    column_number=int(col_num),
                                    severity=SeverityLevel.ERROR,
                                    message=message,
                                    rule_id=error_code,
                                    category="mypy",
                                )
                            )

        except (subprocess.TimeoutExpired, Exception) as e:
            logger.error(f"Error running mypy on {file_path}: {e}")

        return results

    def _run_bandit(self, file_path: str) -> list[AnalysisResult]:
        """Run bandit security analysis on a file."""
        results = []

        try:
            cmd = ["bandit", "-f", "json", file_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.stdout:
                bandit_results = json.loads(result.stdout)

                for issue in bandit_results.get("results", []):
                    severity_map = {
                        "LOW": SeverityLevel.INFO,
                        "MEDIUM": SeverityLevel.WARNING,
                        "HIGH": SeverityLevel.ERROR,
                        "CRITICAL": SeverityLevel.CRITICAL,
                    }

                    results.append(
                        AnalysisResult(
                            file_path=issue["filename"],
                            line_number=issue["line_number"],
                            column_number=0,
                            severity=severity_map.get(
                                issue["issue_severity"], SeverityLevel.WARNING
                            ),
                            message=issue["issue_text"],
                            rule_id=issue["test_id"],
                            category="security",
                            suggestion=issue.get("more_info"),
                        )
                    )

        except (subprocess.TimeoutExpired, json.JSONDecodeError, Exception) as e:
            logger.error(f"Error running bandit on {file_path}: {e}")

        return results

    def _run_radon(self, file_path: str) -> list[AnalysisResult]:
        """Run radon complexity analysis on a file."""
        results = []

        try:
            cmd = ["radon", "cc", "-j", file_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.stdout:
                radon_results = json.loads(result.stdout)

                for file_data in radon_results.values():
                    for function_data in file_data:
                        complexity = function_data.get("complexity", 0)
                        if complexity > 10:  # High complexity threshold
                            results.append(
                                AnalysisResult(
                                    file_path=file_path,
                                    line_number=function_data.get("lineno", 0),
                                    column_number=0,
                                    severity=(
                                        SeverityLevel.WARNING
                                        if complexity <= 20
                                        else SeverityLevel.ERROR
                                    ),
                                    message=f"High cyclomatic complexity: {complexity}",
                                    rule_id="RADON_CC",
                                    category="complexity",
                                    suggestion=f"Consider refactoring to reduce complexity (current: {complexity})",
                                )
                            )

        except (subprocess.TimeoutExpired, json.JSONDecodeError, Exception) as e:
            logger.error(f"Error running radon on {file_path}: {e}")

        return results

    def _run_vulture(self, file_path: str) -> list[AnalysisResult]:
        """Run vulture dead code analysis on a file."""
        results = []

        try:
            cmd = ["vulture", "--min-confidence", "60", file_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.stdout:
                for line in result.stdout.strip().split("\n"):
                    if ":" in line:
                        parts = line.split(":", 2)
                        if len(parts) >= 3:
                            file_path, line_num, message = parts

                            results.append(
                                AnalysisResult(
                                    file_path=file_path,
                                    line_number=int(line_num),
                                    column_number=0,
                                    severity=SeverityLevel.WARNING,
                                    message=message.strip(),
                                    rule_id="VULTURE",
                                    category="quality",
                                    suggestion="Consider removing unused code or adding tests",
                                )
                            )

        except (subprocess.TimeoutExpired, Exception) as e:
            logger.error(f"Error running vulture on {file_path}: {e}")

        return results

    def _run_safety(self, file_path: str) -> list[AnalysisResult]:
        """Run safety dependency analysis."""
        results = []

        try:
            # Safety analyzes requirements files, not individual Python files
            req_files = self._find_requirements_files()

            for req_file in req_files:
                cmd = ["safety", "check", "--json", "--file", req_file]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

                if result.stdout:
                    safety_results = json.loads(result.stdout)

                    for vuln in safety_results:
                        results.append(
                            AnalysisResult(
                                file_path=req_file,
                                line_number=0,
                                column_number=0,
                                severity=SeverityLevel.ERROR,
                                message=f"Vulnerable dependency: {vuln.get('package', 'unknown')}",
                                rule_id="SAFETY",
                                category="security",
                                suggestion=f"Update to version {vuln.get('safe_version', 'latest')}",
                            )
                        )

        except (subprocess.TimeoutExpired, json.JSONDecodeError, Exception) as e:
            logger.error(f"Error running safety: {e}")

        return results

    def _run_pyrefly(self, file_path: str) -> list[AnalysisResult]:
        """Run Pyrefly type checking on a file."""
        results = []

        try:
            # Import pyrefly_runner here to avoid circular imports

            # Run Pyrefly analysis on the file
            pyrefly_result = run_pyrefly_analysis(
                target_paths=[file_path],
                project_root=self.project_root
            )

            # Convert Pyrefly results to AnalysisResult format
            if pyrefly_result.get("issues"):
                severity_map = {
                    "error": SeverityLevel.ERROR,
                    "warning": SeverityLevel.WARNING,
                    "info": SeverityLevel.INFO,
                }

                for issue in pyrefly_result["issues"]:
                    results.append(
                        AnalysisResult(
                            file_path=issue.get("file_path", file_path),
                            line_number=issue.get("line_number", 0),
                            column_number=issue.get("column_number", 0),
                            severity=severity_map.get(
                                issue.get("severity", "error"), SeverityLevel.ERROR
                            ),
                            message=issue.get("message", ""),
                            rule_id=issue.get("code", "PYREFLY_ERROR"),
                            category="type_checking",
                        )
                    )

            # Log any errors from Pyrefly execution
            if pyrefly_result.get("error"):
                logger.warning(f"Pyrefly reported error for {file_path}: {pyrefly_result['error']}")

        except (ImportError, subprocess.SubprocessError, FileNotFoundError, Exception) as e:
            logger.error(f"Error running Pyrefly on {file_path}: {e}")

        return results

    def _find_requirements_files(self) -> list[str]:
        """Find requirements files in the project."""
        req_files = []
        req_patterns = ["requirements*.txt", "Pipfile", "pyproject.toml", "setup.py"]

        for pattern in req_patterns:
            for root, _dirs, files in os.walk(self.project_root):
                for file in files:
                    if file == pattern or file.startswith("requirements"):
                        req_files.append(os.path.join(root, file))

        return req_files

    def _analyze_javascript_file(
        self, file_path: str, analysis_types: list[AnalysisType]
    ) -> list[AnalysisResult]:
        """Analyze a JavaScript/TypeScript file."""
        results = []

        # ESLint analysis
        if AnalysisType.QUALITY in analysis_types and self.tools_available.get(
            "eslint", False
        ):
            results.extend(self._run_eslint(file_path))

        # TypeScript compiler
        if AnalysisType.QUALITY in analysis_types and file_path.endswith(
            (".ts", ".tsx")
        ):
            results.extend(self._run_typescript_compiler(file_path))

        return results

    def _run_eslint(self, file_path: str) -> list[AnalysisResult]:
        """Run ESLint analysis on a JavaScript/TypeScript file."""
        results = []

        try:
            cmd = ["eslint", "--format=json", file_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.stdout:
                eslint_results = json.loads(result.stdout)

                for file_data in eslint_results:
                    for message in file_data.get("messages", []):
                        severity_map = {
                            1: SeverityLevel.WARNING,
                            2: SeverityLevel.ERROR,
                        }

                        results.append(
                            AnalysisResult(
                                file_path=file_data["filePath"],
                                line_number=message["line"],
                                column_number=message["column"],
                                severity=severity_map.get(
                                    message["severity"], SeverityLevel.WARNING
                                ),
                                message=message["message"],
                                rule_id=message["ruleId"],
                                category="eslint",
                                suggestion=message.get("fix"),
                            )
                        )

        except (subprocess.TimeoutExpired, json.JSONDecodeError, Exception) as e:
            logger.error(f"Error running eslint on {file_path}: {e}")

        return results

    def _run_typescript_compiler(self, file_path: str) -> list[AnalysisResult]:
        """Run TypeScript compiler analysis."""
        results = []

        try:
            cmd = ["tsc", "--noEmit", "--pretty", "false", file_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.stderr:
                for line in result.stderr.strip().split("\n"):
                    if ":" in line and "error" in line:
                        # Parse TypeScript error format
                        match = re.match(
                            r"([^:]+):(\d+):(\d+) - error TS(\d+): (.+)", line
                        )
                        if match:
                            file_path, line_num, col_num, error_code, message = (
                                match.groups()
                            )

                            results.append(
                                AnalysisResult(
                                    file_path=file_path,
                                    line_number=int(line_num),
                                    column_number=int(col_num),
                                    severity=SeverityLevel.ERROR,
                                    message=message,
                                    rule_id=f"TS{error_code}",
                                    category="typescript",
                                )
                            )

        except (subprocess.TimeoutExpired, Exception) as e:
            logger.error(f"Error running TypeScript compiler on {file_path}: {e}")

        return results

    def _analyze_java_file(
        self, file_path: str, analysis_types: list[AnalysisType]
    ) -> list[AnalysisResult]:
        """Analyze a Java file."""
        results = []

        # SpotBugs analysis
        if AnalysisType.QUALITY in analysis_types and self.tools_available.get(
            "spotbugs", False
        ):
            results.extend(self._run_spotbugs(file_path))

        return results

    def _run_spotbugs(self, file_path: str) -> list[AnalysisResult]:
        """Run SpotBugs analysis on a Java file."""
        results = []

        try:
            cmd = ["spotbugs", "-textui", "-output", "json", file_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.stdout:
                spotbugs_results = json.loads(result.stdout)

                for bug in spotbugs_results.get("bugs", []):
                    severity_map = {
                        "LOW": SeverityLevel.INFO,
                        "MEDIUM": SeverityLevel.WARNING,
                        "HIGH": SeverityLevel.ERROR,
                    }

                    results.append(
                        AnalysisResult(
                            file_path=bug["file"],
                            line_number=bug["line"],
                            column_number=0,
                            severity=severity_map.get(
                                bug["priority"], SeverityLevel.WARNING
                            ),
                            message=bug["message"],
                            rule_id=bug["type"],
                            category="spotbugs",
                            suggestion=bug.get("suggestion"),
                        )
                    )

        except (subprocess.TimeoutExpired, json.JSONDecodeError, Exception) as e:
            logger.error(f"Error running spotbugs on {file_path}: {e}")

        return results

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

        # Find all files to analyze
        files_to_analyze = []
        for target_path in target_paths:
            if os.path.isfile(target_path):
                files_to_analyze.append(target_path)
            else:
                for root, dirs, files in os.walk(target_path):
                    # Filter out excluded directories
                    dirs[:] = [
                        d
                        for d in dirs
                        if not any(pattern in d for pattern in exclude_patterns)
                    ]

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

        # Count by severity
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

            # Basic metrics
            lines_of_code = len(
                [
                    line
                    for line in content.split("\n")
                    if line.strip() and not line.strip().startswith("#")
                ]
            )

            # Cyclomatic complexity (simplified)
            cyclomatic_complexity = self._calculate_cyclomatic_complexity(content)

            # Maintainability index (simplified)
            maintainability_index = max(
                0, 171 - 5.2 * math.log(cyclomatic_complexity) - 0.23 * lines_of_code
            )

            # Technical debt (simplified)
            technical_debt = len(self.results) * 0.1  # 0.1 hours per issue

            # Code duplication (simplified)
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
        except SyntaxError:
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

        # Simple duplication detection
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
def analyze_file(
    file_path: str, analysis_types: list[AnalysisType] = None
) -> list[AnalysisResult]:
    """Analyze a single file."""
    analyzer = StaticAnalyzer()
    return analyzer.analyze_file(file_path, analysis_types)


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
