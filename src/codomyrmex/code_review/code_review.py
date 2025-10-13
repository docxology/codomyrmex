"""
Comprehensive code review functionality for Codomyrmex.

This module provides advanced static analysis capabilities including pyscn integration
for high-performance code quality assessment, security scanning, and maintainability analysis.
"""

import os
import sys
import json
import ast
import subprocess
import tempfile
import re
import math
from typing import Dict, List, Any, Optional, Tuple, Union, Set
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import time
import shutil
from codomyrmex.exceptions import CodomyrmexError

# Add project root to Python path for imports
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Import logger setup
try:
    from logging_monitoring import setup_logging, get_logger
except ImportError:
    import logging

    def get_logger(name):
        logger = logging.getLogger(name)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

# Get module logger
logger = get_logger(__name__)

# Import performance monitoring
try:
    from performance import monitor_performance, performance_context
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
    PYSCN = "pyscn"  # Advanced pyscn analysis


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
    by_severity: Dict[SeverityLevel, int] = field(default_factory=dict)
    by_category: Dict[str, int] = field(default_factory=dict)
    by_rule: Dict[str, int] = field(default_factory=dict)
    files_analyzed: int = 0
    analysis_time: float = 0.0
    language: Optional[Language] = None
    pyscn_metrics: Optional[Dict[str, Any]] = None


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


@dataclass
class ComplexityReductionSuggestion:
    """Suggestion for reducing function complexity."""

    function_name: str
    file_path: str
    current_complexity: int
    suggested_refactoring: str
    estimated_effort: str  # "low", "medium", "high"
    benefits: List[str]
    code_example: Optional[str] = None


@dataclass
class DeadCodeFinding:
    """Enhanced dead code finding with suggestions."""

    file_path: str
    line_number: int
    code_snippet: str
    reason: str
    severity: str
    suggestion: str
    fix_available: bool = False
    estimated_savings: str = ""


@dataclass
class ArchitectureViolation:
    """Architecture compliance violation."""

    file_path: str
    violation_type: str
    description: str
    severity: str
    suggestion: str
    affected_modules: List[str] = field(default_factory=list)


@dataclass
class QualityDashboard:
    """Comprehensive code quality dashboard."""

    overall_score: float
    grade: str
    analysis_timestamp: str
    total_files: int
    total_functions: int
    total_lines: int

    # Category scores
    complexity_score: float
    maintainability_score: float
    testability_score: float
    reliability_score: float
    security_score: float
    performance_score: float

    # Detailed metrics
    complexity_metrics: Dict[str, Any]
    dead_code_metrics: Dict[str, Any]
    duplication_metrics: Dict[str, Any]
    coupling_metrics: Dict[str, Any]
    architecture_metrics: Dict[str, Any]

    # Top issues
    top_complexity_issues: List[Dict[str, Any]]
    top_dead_code_issues: List[Dict[str, Any]]
    top_duplication_issues: List[Dict[str, Any]]

    # Recommendations
    priority_actions: List[Dict[str, Any]]
    quick_wins: List[Dict[str, Any]]
    long_term_improvements: List[Dict[str, Any]]

    # Trends (if historical data available)
    trend_direction: Optional[str] = None
    trend_percentage: Optional[float] = None


@dataclass
class QualityGateResult:
    """Result of quality gate check."""

    passed: bool
    total_checks: int
    passed_checks: int
    failed_checks: int
    failures: List[Dict[str, Any]] = field(default_factory=list)


class CodeReviewError(CodomyrmexError):
    """Base exception for code review operations."""
    pass


class PyscnError(CodeReviewError):
    """Error in pyscn analysis."""
    pass


class ToolNotFoundError(CodeReviewError):
    """Required analysis tool not found."""
    pass


class ConfigurationError(CodeReviewError):
    """Invalid configuration provided."""
    pass


class PyscnAnalyzer:
    """Specialized analyzer using pyscn for advanced static analysis."""

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize pyscn analyzer with configuration.

        Args:
            config: Pyscn configuration options
        """
        self.config = config or {}
        self._check_pyscn_availability()

    def _check_pyscn_availability(self):
        """Check if pyscn is available and working."""
        try:
            # Try to run pyscn --version
            result = subprocess.run(
                ["pyscn", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode != 0:
                raise ToolNotFoundError("pyscn not available or not working")
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            raise ToolNotFoundError(
                "pyscn not found. Install with: pipx install pyscn"
            )

    @monitor_performance("pyscn_analyze_complexity")
    def analyze_complexity(self, file_path: str) -> List[Dict[str, Any]]:
        """Analyze cyclomatic complexity using pyscn."""
        try:
            # Pyscn writes JSON to a file, we need to read it from there
            import glob
            import os

            # Get the most recent .pyscn/reports file
            reports_dir = ".pyscn/reports"
            if os.path.exists(reports_dir):
                json_files = glob.glob(os.path.join(reports_dir, "*.json"))
                if json_files:
                    # Get the most recent file
                    latest_file = max(json_files, key=os.path.getmtime)

                    with open(latest_file, 'r') as f:
                        data = json.load(f)

                    # Pyscn returns data under "complexity" key in the main object
                    complexity_data = data.get("complexity", {})
                    if "Functions" in complexity_data:
                        # Extract functions from the Functions array
                        functions = []
                        for func_data in complexity_data["Functions"]:
                            # Extract complexity from Metrics
                            complexity = func_data.get("Metrics", {}).get("Complexity", 0)
                            functions.append({
                                "name": func_data.get("Name", ""),
                                "complexity": complexity,
                                "line_number": func_data.get("StartLine", 0),
                                "file_path": func_data.get("FilePath", ""),
                                "risk_level": func_data.get("RiskLevel", "")
                            })
                        return functions
            return []

        except (json.JSONDecodeError, FileNotFoundError, Exception) as e:
            logger.error(f"Error running pyscn complexity analysis on {file_path}: {e}")
            return []

    @monitor_performance("pyscn_detect_dead_code")
    def detect_dead_code(self, file_path: str) -> List[Dict[str, Any]]:
        """Detect dead code using CFG analysis."""
        try:
            # Pyscn writes JSON to a file, we need to read it from there
            import glob
            import os

            # Get the most recent .pyscn/reports file
            reports_dir = ".pyscn/reports"
            if os.path.exists(reports_dir):
                json_files = glob.glob(os.path.join(reports_dir, "*.json"))
                if json_files:
                    # Get the most recent file
                    latest_file = max(json_files, key=os.path.getmtime)

                    with open(latest_file, 'r') as f:
                        data = json.load(f)

                    # Pyscn returns data under "dead_code" key
                    dead_code_data = data.get("dead_code", {})
                    if "files" in dead_code_data:
                        # Extract findings from all files
                        findings = []
                        for file_data in dead_code_data["files"]:
                            for function_data in file_data.get("functions", []):
                                findings.extend(function_data.get("findings", []))
                        return findings
            return []

        except (json.JSONDecodeError, FileNotFoundError, Exception) as e:
            logger.error(f"Error running pyscn dead code analysis on {file_path}: {e}")
            return []

    @monitor_performance("pyscn_find_clones")
    def find_clones(self, files: List[str], threshold: float = 0.8) -> List[Dict[str, Any]]:
        """Find code clones using APTED with LSH acceleration."""
        try:
            # For single file analysis, pyscn doesn't need a file list
            if len(files) == 1:
                cmd = [
                    "pyscn", "analyze", "--select", "clones",
                    "--json", f"--clone-threshold={threshold}",
                    files[0]
                ]
            else:
                # For multiple files, create temporary file list
                with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                    for file_path in files:
                        f.write(file_path + '\n')
                    file_list_path = f.name

                cmd = [
                    "pyscn", "analyze", "--select", "clones",
                    "--json", f"--clone-threshold={threshold}",
                    f"@{file_list_path}"
                ]

                subprocess.run(cmd, capture_output=True, text=True, timeout=120)

                # Clean up temporary file
                os.unlink(file_list_path)

            # Read from the generated JSON file
            import glob
            import os

            reports_dir = ".pyscn/reports"
            if os.path.exists(reports_dir):
                json_files = glob.glob(os.path.join(reports_dir, "*.json"))
                if json_files:
                    # Get the most recent file
                    latest_file = max(json_files, key=os.path.getmtime)

                    with open(latest_file, 'r') as f:
                        data = json.load(f)

                    # Pyscn returns clone data under "clones" key
                    clones_data = data.get("clones", {})
                    if "groups" in clones_data:
                        return clones_data["groups"]
            return []

        except (json.JSONDecodeError, FileNotFoundError, Exception) as e:
            logger.error(f"Error running pyscn clone detection: {e}")
            return []

    @monitor_performance("pyscn_analyze_coupling")
    def analyze_coupling(self, file_path: str) -> List[Dict[str, Any]]:
        """Analyze Coupling Between Objects (CBO) metrics."""
        try:
            cmd = ["pyscn", "analyze", "--select", "cbo", "--json", file_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            if result.stdout:
                data = json.loads(result.stdout)
                # Pyscn returns CBO data under "cbo" key
                cbo_data = data.get("cbo", {})
                if "files" in cbo_data:
                    # Extract coupling data from all files
                    coupling_data = []
                    for file_data in cbo_data["files"]:
                        coupling_data.extend(file_data.get("classes", []))
                    return coupling_data
                return []
            return []

        except (subprocess.TimeoutExpired, json.JSONDecodeError, Exception) as e:
            logger.error(f"Error running pyscn coupling analysis on {file_path}: {e}")
            return []

    @monitor_performance("pyscn_generate_report")
    def generate_report(self, output_dir: str = "reports") -> str:
        """Generate comprehensive pyscn HTML report."""
        try:
            # Ensure output directory exists
            os.makedirs(output_dir, exist_ok=True)

            # Change to the directory we want to analyze
            old_cwd = os.getcwd()
            os.chdir(output_dir)

            try:
                # Generate comprehensive report
                cmd = ["pyscn", "analyze", "--format", "html", ".."]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

                report_path = "index.html"
                if os.path.exists(report_path):
                    return os.path.abspath(report_path)
                else:
                    logger.warning("Pyscn report generation completed but no HTML file found")
                    return ""
            finally:
                os.chdir(old_cwd)

        except (subprocess.TimeoutExpired, Exception) as e:
            logger.error(f"Error generating pyscn report: {e}")
            return ""


class CodeReviewer:
    """Main code reviewer class with pyscn integration."""

    def __init__(self, project_root: str = None, config_path: str = None):
        """
        Initialize the code reviewer.

        Args:
            project_root: Root directory of the project to analyze
            config_path: Path to configuration file
        """
        self.project_root = project_root or os.getcwd()
        self.config_path = config_path
        self.results: List[AnalysisResult] = []
        self.metrics: Dict[str, CodeMetrics] = {}
        self.pyscn_analyzer = PyscnAnalyzer()

        # Load configuration
        self.config = self._load_config()

        # Check available tools
        self.tools_available = self._check_tools_availability()

    def _load_config(self) -> Dict[str, Any]:
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

    def _check_tools_availability(self) -> Dict[str, bool]:
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

    def _run_pyscn_analysis(self, file_path: str) -> List[AnalysisResult]:
        """Run comprehensive pyscn analysis on a file."""
        results = []

        # Only run pyscn if it's enabled and file is Python
        if not self.config["pyscn"]["enabled"]:
            return results

        language = self._detect_language(file_path)
        if language != Language.PYTHON:
            return results

        try:
            # Complexity analysis
            complexity_results = self.pyscn_analyzer.analyze_complexity(file_path)
            for func in complexity_results:
                complexity = func.get("complexity", 0)
                if complexity > self.config["max_complexity"]:
                    severity = (
                        SeverityLevel.WARNING
                        if complexity <= self.config["max_complexity"] * 1.5
                        else SeverityLevel.ERROR
                    )

                    results.append(AnalysisResult(
                        file_path=file_path,
                        line_number=func.get("line_number", func.get("line", 0)),
                        column_number=0,
                        severity=severity,
                        message=f"High cyclomatic complexity: {complexity}",
                        rule_id="PYSCN_COMPLEXITY",
                        category="complexity",
                        suggestion=f"Consider refactoring to reduce complexity (current: {complexity})",
                    ))

            # Dead code detection
            dead_code_results = self.pyscn_analyzer.detect_dead_code(file_path)
            for finding in dead_code_results:
                # Map pyscn severity to our severity levels
                severity_map = {
                    "critical": SeverityLevel.CRITICAL,
                    "warning": SeverityLevel.WARNING,
                    "info": SeverityLevel.INFO
                }

                severity = severity_map.get(finding.get("severity", "warning"), SeverityLevel.WARNING)

                results.append(AnalysisResult(
                    file_path=file_path,
                    line_number=finding.get("location", {}).get("start_line", 0),
                    column_number=finding.get("location", {}).get("start_column", 0),
                    severity=severity,
                    message=finding.get("description", "Dead code detected"),
                    rule_id="PYSCN_DEAD_CODE",
                    category="quality",
                    suggestion="Remove unreachable code or fix control flow",
                ))

        except Exception as e:
            logger.error(f"Error in pyscn analysis for {file_path}: {e}")

        return results

    def _run_traditional_analysis(self, file_path: str, analysis_types: List[str]) -> List[AnalysisResult]:
        """Run traditional static analysis tools."""
        results = []
        language = self._detect_language(file_path)

        if language == Language.PYTHON:
            results.extend(self._analyze_python_file(file_path, analysis_types))

        return results

    def _analyze_python_file(self, file_path: str, analysis_types: List[str]) -> List[AnalysisResult]:
        """Analyze a Python file using traditional tools."""
        results = []

        # Pylint analysis
        if "quality" in analysis_types and self.tools_available["pylint"]:
            results.extend(self._run_pylint(file_path))

        # Flake8 analysis
        if "style" in analysis_types and self.tools_available["flake8"]:
            results.extend(self._run_flake8(file_path))

        # MyPy type checking
        if "quality" in analysis_types and self.tools_available["mypy"]:
            results.extend(self._run_mypy(file_path))

        # Bandit security analysis
        if "security" in analysis_types and self.tools_available["bandit"]:
            results.extend(self._run_bandit(file_path))

        # Vulture dead code analysis (fallback)
        if "quality" in analysis_types and self.tools_available["vulture"]:
            results.extend(self._run_vulture(file_path))

        return results

    def _run_pylint(self, file_path: str) -> List[AnalysisResult]:
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

                    results.append(AnalysisResult(
                        file_path=issue["path"],
                        line_number=issue["line"],
                        column_number=issue["column"],
                        severity=severity_map.get(issue["type"], SeverityLevel.WARNING),
                        message=issue["message"],
                        rule_id=issue["message-id"],
                        category="pylint",
                        suggestion=issue.get("suggestion"),
                    ))

        except (subprocess.TimeoutExpired, json.JSONDecodeError, Exception) as e:
            logger.error(f"Error running pylint on {file_path}: {e}")

        return results

    def _run_flake8(self, file_path: str) -> List[AnalysisResult]:
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

                            results.append(AnalysisResult(
                                file_path=file_path,
                                line_number=int(line_num),
                                column_number=int(col_num),
                                severity=severity,
                                message=message.strip(),
                                rule_id=rule_id,
                                category="flake8",
                            ))

        except (subprocess.TimeoutExpired, Exception) as e:
            logger.error(f"Error running flake8 on {file_path}: {e}")

        return results

    def _run_mypy(self, file_path: str) -> List[AnalysisResult]:
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
                            file_path, line_num, col_num, message, error_code = match.groups()

                            results.append(AnalysisResult(
                                file_path=file_path,
                                line_number=int(line_num),
                                column_number=int(col_num),
                                severity=SeverityLevel.ERROR,
                                message=message,
                                rule_id=error_code,
                                category="mypy",
                            ))

        except (subprocess.TimeoutExpired, Exception) as e:
            logger.error(f"Error running mypy on {file_path}: {e}")

        return results

    def _run_bandit(self, file_path: str) -> List[AnalysisResult]:
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

                    results.append(AnalysisResult(
                        file_path=issue["filename"],
                        line_number=issue["line_number"],
                        column_number=0,
                        severity=severity_map.get(issue["issue_severity"], SeverityLevel.WARNING),
                        message=issue["issue_text"],
                        rule_id=issue["test_id"],
                        category="security",
                        suggestion=issue.get("more_info"),
                    ))

        except (subprocess.TimeoutExpired, json.JSONDecodeError, Exception) as e:
            logger.error(f"Error running bandit on {file_path}: {e}")

        return results

    def _run_vulture(self, file_path: str) -> List[AnalysisResult]:
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

                            results.append(AnalysisResult(
                                file_path=file_path,
                                line_number=int(line_num),
                                column_number=0,
                                severity=SeverityLevel.WARNING,
                                message=message.strip(),
                                rule_id="VULTURE",
                                category="quality",
                                suggestion="Consider removing unused code or adding tests",
                            ))

        except (subprocess.TimeoutExpired, Exception) as e:
            logger.error(f"Error running vulture on {file_path}: {e}")

        return results

    @monitor_performance("analyze_file")
    def analyze_file(
        self, file_path: str, analysis_types: List[str] = None
    ) -> List[AnalysisResult]:
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

    @monitor_performance("analyze_project")
    def analyze_project(
        self,
        target_paths: List[str] = None,
        analysis_types: List[str] = None,
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

    def check_quality_gates(self, thresholds: Dict[str, int] = None) -> QualityGateResult:
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

    def generate_report(self, output_path: str, format: str = "html") -> bool:
        """Generate comprehensive analysis report."""
        try:
            if format.lower() == "html":
                return self._generate_html_report(output_path)
            elif format.lower() == "json":
                return self._generate_json_report(output_path)
            elif format.lower() == "markdown":
                return self._generate_markdown_report(output_path)
            else:
                logger.error(f"Unsupported report format: {format}")
                return False

        except Exception as e:
            logger.error(f"Error generating report: {e}")
            return False

    def _generate_html_report(self, output_path: str) -> bool:
        """Generate HTML report."""
        # Use pyscn to generate HTML report if available
        report_path = self.pyscn_analyzer.generate_report(os.path.dirname(output_path))
        if report_path:
            # Copy to desired location if different
            if report_path != output_path:
                shutil.copy2(report_path, output_path)
            return True

        # Fallback to basic HTML generation
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Code Review Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .summary {{ background: #f5f5f5; padding: 15px; margin: 10px 0; }}
                .issue {{ border-left: 4px solid #ddd; padding: 10px; margin: 10px 0; }}
                .error {{ border-color: #e74c3c; }}
                .warning {{ border-color: #f39c12; }}
                .info {{ border-color: #3498db; }}
            </style>
        </head>
        <body>
            <h1>Code Review Report</h1>
            <div class="summary">
                <h2>Summary</h2>
                <p>Total Issues: {len(self.results)}</p>
                <p>Files Analyzed: {len(set(r.file_path for r in self.results))}</p>
            </div>
            <h2>Issues</h2>
        """

        for result in self.results:
            severity_class = result.severity.value
            html_content += f"""
            <div class="issue {severity_class}">
                <h3>{result.file_path}:{result.line_number}</h3>
                <p><strong>{result.severity.value.upper()}:</strong> {result.message}</p>
                <p><em>Category:</em> {result.category} | <em>Rule:</em> {result.rule_id}</p>
                {f"<p><em>Suggestion:</em> {result.suggestion}</p>" if result.suggestion else ""}
            </div>
            """

        html_content += """
        </body>
        </html>
        """

        with open(output_path, "w") as f:
            f.write(html_content)

        return True

    def _generate_json_report(self, output_path: str) -> bool:
        """Generate JSON report."""
        report_data = {
            "summary": {
                "total_issues": len(self.results),
                "files_analyzed": len(set(r.file_path for r in self.results)),
                "analysis_time": 0,  # Would need to track this
            },
            "results": [
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
            ]
        }

        with open(output_path, "w") as f:
            json.dump(report_data, f, indent=2)

        return True

    def _generate_markdown_report(self, output_path: str) -> bool:
        """Generate Markdown report."""
        md_content = "# Code Review Report\n\n"

        # Summary
        md_content += "## Summary\n\n"
        md_content += f"- **Total Issues**: {len(self.results)}\n"
        md_content += f"- **Files Analyzed**: {len(set(r.file_path for r in self.results))}\n"
        md_content += f"- **Analysis Time**: N/A\n\n"

        # Issues by severity
        severity_counts = {}
        for result in self.results:
            severity_counts[result.severity] = severity_counts.get(result.severity, 0) + 1

        md_content += "## Issues by Severity\n\n"
        for severity, count in severity_counts.items():
            md_content += f"- **{severity.value.upper()}**: {count}\n"
        md_content += "\n"

        # Detailed issues
        md_content += "## Detailed Issues\n\n"
        for result in self.results:
            md_content += f"### {result.file_path}:{result.line_number}\n\n"
            md_content += f"- **Severity**: {result.severity.value}\n"
            md_content += f"- **Message**: {result.message}\n"
            md_content += f"- **Category**: {result.category}\n"
            md_content += f"- **Rule**: {result.rule_id}\n"
            if result.suggestion:
                md_content += f"- **Suggestion**: {result.suggestion}\n"
            md_content += "\n"

        with open(output_path, "w") as f:
            f.write(md_content)

        return True

    def clear_results(self):
        """Clear all analysis results."""
        self.results.clear()
        self.metrics.clear()

    @monitor_performance("analyze_complexity_patterns")
    def analyze_complexity_patterns(self) -> List[ComplexityReductionSuggestion]:
        """Analyze complexity patterns and provide reduction suggestions."""
        suggestions = []

        try:
            # Get complexity data from pyscn
            complexity_results = self.pyscn_analyzer.analyze_complexity(self.project_root)

            for func in complexity_results:
                complexity = func.get("complexity", 0)
                if complexity > self.config["max_complexity"]:
                    suggestion = self._generate_complexity_suggestion(func)
                    if suggestion:
                        suggestions.append(suggestion)

        except Exception as e:
            logger.error(f"Error analyzing complexity patterns: {e}")

        return suggestions

    def _generate_complexity_suggestion(self, func_data: Dict[str, Any]) -> Optional[ComplexityReductionSuggestion]:
        """Generate a specific suggestion for reducing complexity."""
        function_name = func_data.get("name", "unknown")
        complexity = func_data.get("complexity", 0)
        file_path = func_data.get("file_path", "")

        # Analyze the complexity and suggest appropriate refactoring
        if complexity >= 25:
            refactoring = "Extract method refactoring"
            effort = "medium"
            benefits = [
                "Improved readability",
                "Easier testing",
                "Better maintainability",
                "Reduced cognitive load"
            ]
            code_example = f"""
def {function_name}(...):
    # Extract complex logic into separate methods
    result = self._process_data(...)
    return self._format_result(result)
"""
        elif complexity >= 15:
            refactoring = "Guard clause refactoring"
            effort = "low"
            benefits = [
                "Early returns reduce nesting",
                "Improved readability",
                "Reduced complexity"
            ]
            code_example = """
def complex_function(data):
    if not data:
        return None  # Guard clause

    if len(data) > 100:
        return self._handle_large_dataset(data)

    # Main logic here...
"""
        else:
            return None

        return ComplexityReductionSuggestion(
            function_name=function_name,
            file_path=file_path,
            current_complexity=complexity,
            suggested_refactoring=refactoring,
            estimated_effort=effort,
            benefits=benefits,
            code_example=code_example
        )

    @monitor_performance("analyze_dead_code_patterns")
    def analyze_dead_code_patterns(self) -> List[DeadCodeFinding]:
        """Analyze dead code patterns and provide enhanced findings."""
        findings = []

        try:
            # Get dead code data from pyscn
            dead_code_results = self.pyscn_analyzer.detect_dead_code(self.project_root)

            for finding in dead_code_results:
                enhanced_finding = self._enhance_dead_code_finding(finding)
                if enhanced_finding:
                    findings.append(enhanced_finding)

        except Exception as e:
            logger.error(f"Error analyzing dead code patterns: {e}")

        return findings

    def _enhance_dead_code_finding(self, finding: Dict[str, Any]) -> Optional[DeadCodeFinding]:
        """Enhance a dead code finding with better suggestions."""
        location = finding.get("location", {})
        file_path = location.get("file_path", "")
        line_number = location.get("start_line", 0)
        reason = finding.get("reason", "")
        severity = finding.get("severity", "warning")

        # Generate specific suggestions based on the reason
        suggestion = self._get_dead_code_suggestion(reason, severity)

        return DeadCodeFinding(
            file_path=file_path,
            line_number=line_number,
            code_snippet=finding.get("code", ""),
            reason=reason,
            severity=severity,
            suggestion=suggestion,
            fix_available=self._can_auto_fix_dead_code(reason),
            estimated_savings=self._estimate_dead_code_savings(reason)
        )

    def _get_dead_code_suggestion(self, reason: str, severity: str) -> str:
        """Get specific suggestion for dead code issue."""
        suggestions = {
            "unreachable_after_return": "Remove code after return statement - it will never execute",
            "unreachable_after_raise": "Remove code after exception - it will never execute",
            "unreachable_after_break": "Remove code after break statement - it will never execute",
            "unreachable_after_continue": "Remove code after continue statement - it will never execute",
            "unused_variable": "Remove unused variable or add underscore prefix if intentionally unused",
            "unused_function": "Remove unused function or add proper usage",
            "unused_import": "Remove unused import to reduce namespace pollution",
            "unused_class": "Remove unused class or add proper usage"
        }

        return suggestions.get(reason, f"Remove unreachable code (reason: {reason})")

    def _can_auto_fix_dead_code(self, reason: str) -> bool:
        """Determine if dead code can be automatically fixed."""
        auto_fixable = {
            "unreachable_after_return",
            "unreachable_after_raise",
            "unreachable_after_break",
            "unreachable_after_continue"
        }
        return reason in auto_fixable

    def _estimate_dead_code_savings(self, reason: str) -> str:
        """Estimate the savings from removing dead code."""
        if reason.startswith("unreachable"):
            return "Reduces file size and improves readability"
        elif "unused" in reason:
            return "Reduces memory usage and namespace pollution"
        else:
            return "Improves code clarity and maintainability"

    @monitor_performance("analyze_architecture_compliance")
    def analyze_architecture_compliance(self) -> List[ArchitectureViolation]:
        """Analyze architecture compliance and identify violations."""
        violations = []

        try:
            # This would typically use pyscn's system analysis
            # For now, implement basic checks
            violations.extend(self._check_layering_violations())
            violations.extend(self._check_circular_dependencies())
            violations.extend(self._check_naming_conventions())

        except Exception as e:
            logger.error(f"Error analyzing architecture compliance: {e}")

        return violations

    def _check_layering_violations(self) -> List[ArchitectureViolation]:
        """Check for layering violations in the architecture."""
        violations = []

        # Check if data access layer depends on presentation layer
        presentation_files = self._find_files_in_layer("presentation")
        data_files = self._find_files_in_layer("data")

        for data_file in data_files:
            # This is a simplified check - in reality would need AST analysis
            if self._file_imports_presentation_layer(data_file, presentation_files):
                violations.append(ArchitectureViolation(
                    file_path=data_file,
                    violation_type="layering_violation",
                    description="Data layer should not depend on presentation layer",
                    severity="high",
                    suggestion="Move shared code to a common layer or use dependency injection",
                    affected_modules=["data_access", "presentation"]
                ))

        return violations

    def _check_circular_dependencies(self) -> List[ArchitectureViolation]:
        """Check for circular dependencies."""
        violations = []

        # This would require more sophisticated analysis
        # For now, return empty list
        return violations

    def _check_naming_conventions(self) -> List[ArchitectureViolation]:
        """Check naming convention compliance."""
        violations = []

        # Check for files that don't follow naming conventions
        for root, dirs, files in os.walk(self.project_root):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)

                    # Check if test files follow naming convention
                    if 'test' in file.lower() and not file.startswith('test_') and not file.endswith('_test.py'):
                        violations.append(ArchitectureViolation(
                            file_path=file_path,
                            violation_type="naming_convention",
                            description=f"Test file '{file}' should follow naming convention (test_*.py or *_test.py)",
                            severity="low",
                            suggestion="Rename file to follow test naming conventions"
                        ))

        return violations

    def _find_files_in_layer(self, layer: str) -> List[str]:
        """Find files belonging to a specific architectural layer."""
        layer_patterns = {
            "presentation": ["ui", "interface", "view", "controller", "handler"],
            "business": ["service", "manager", "orchestrator", "engine"],
            "data": ["repository", "dao", "model", "entity"]
        }

        matching_files = []
        patterns = layer_patterns.get(layer, [])

        for root, dirs, files in os.walk(self.project_root):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)

                    # Simple pattern matching
                    for pattern in patterns:
                        if pattern.lower() in file.lower() or pattern.lower() in root.lower():
                            matching_files.append(file_path)
                            break

        return matching_files

    def _file_imports_presentation_layer(self, file_path: str, presentation_files: List[str]) -> bool:
        """Check if a file imports from presentation layer (simplified check)."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Look for import statements that might reference presentation layer
            for pres_file in presentation_files:
                pres_module = os.path.splitext(os.path.basename(pres_file))[0]
                if f"from {pres_module} import" in content or f"import {pres_module}" in content:
                    return True

        except Exception:
            pass

        return False

    @monitor_performance("generate_refactoring_plan")
    def generate_refactoring_plan(self) -> Dict[str, Any]:
        """Generate a comprehensive refactoring plan based on analysis."""
        plan = {
            "complexity_reductions": [],
            "dead_code_removals": [],
            "architecture_improvements": [],
            "priority_actions": [],
            "estimated_effort": "medium",
            "expected_benefits": [
                "Improved maintainability",
                "Reduced technical debt",
                "Better testability",
                "Enhanced readability"
            ]
        }

        try:
            # Get complexity suggestions
            complexity_suggestions = self.analyze_complexity_patterns()
            plan["complexity_reductions"] = [
                {
                    "function": s.function_name,
                    "file": s.file_path,
                    "refactoring": s.suggested_refactoring,
                    "effort": s.estimated_effort,
                    "benefits": s.benefits
                }
                for s in complexity_suggestions
            ]

            # Get dead code findings
            dead_code_findings = self.analyze_dead_code_patterns()
            plan["dead_code_removals"] = [
                {
                    "file": f.file_path,
                    "line": f.line_number,
                    "reason": f.reason,
                    "suggestion": f.suggestion,
                    "fix_available": f.fix_available
                }
                for f in dead_code_findings
            ]

            # Get architecture violations
            architecture_violations = self.analyze_architecture_compliance()
            plan["architecture_improvements"] = [
                {
                    "file": v.file_path,
                    "violation": v.violation_type,
                    "description": v.description,
                    "suggestion": v.suggestion,
                    "severity": v.severity
                }
                for v in architecture_violations
            ]

            # Determine priority actions
            plan["priority_actions"] = self._determine_priority_actions(
                complexity_suggestions, dead_code_findings, architecture_violations
            )

        except Exception as e:
            logger.error(f"Error generating refactoring plan: {e}")

        return plan

    def _determine_priority_actions(self, complexity_suggestions, dead_code_findings, architecture_violations) -> List[Dict[str, Any]]:
        """Determine the highest priority refactoring actions."""
        actions = []

        # High complexity functions are high priority
        for suggestion in complexity_suggestions:
            if suggestion.current_complexity >= 20:
                actions.append({
                    "type": "complexity_reduction",
                    "priority": "high",
                    "function": suggestion.function_name,
                    "file": suggestion.file_path,
                    "description": f"Reduce complexity of {suggestion.function_name} from {suggestion.current_complexity} to under 15"
                })

        # Critical dead code is high priority
        for finding in dead_code_findings:
            if finding.severity == "critical":
                actions.append({
                    "type": "dead_code_removal",
                    "priority": "high",
                    "file": finding.file_path,
                    "line": finding.line_number,
                    "description": f"Remove critical dead code: {finding.reason}"
                })

        # Architecture violations are medium priority
        for violation in architecture_violations:
            if violation.severity == "high":
                actions.append({
                    "type": "architecture_fix",
                    "priority": "medium",
                    "file": violation.file_path,
                    "description": violation.description
                })

        return actions

    @monitor_performance("optimize_performance")
    def optimize_performance(self) -> Dict[str, Any]:
        """Generate performance optimization suggestions."""
        optimizations = {
            "memory_optimizations": [],
            "cpu_optimizations": [],
            "io_optimizations": [],
            "caching_opportunities": []
        }

        try:
            # Analyze for common performance issues
            optimizations["memory_optimizations"] = self._find_memory_optimizations()
            optimizations["cpu_optimizations"] = self._find_cpu_optimizations()
            optimizations["io_optimizations"] = self._find_io_optimizations()
            optimizations["caching_opportunities"] = self._find_caching_opportunities()

        except Exception as e:
            logger.error(f"Error generating performance optimizations: {e}")

        return optimizations

    def _find_memory_optimizations(self) -> List[str]:
        """Find potential memory optimization opportunities."""
        suggestions = [
            "Use generators instead of lists for large datasets",
            "Implement object pooling for frequently created objects",
            "Use slots in classes to reduce memory overhead",
            "Consider lazy loading for expensive resources"
        ]
        return suggestions

    def _find_cpu_optimizations(self) -> List[str]:
        """Find potential CPU optimization opportunities."""
        suggestions = [
            "Cache expensive computations",
            "Use sets for membership tests instead of lists",
            "Avoid repeated string concatenations",
            "Use list comprehensions instead of loops where appropriate"
        ]
        return suggestions

    def _find_io_optimizations(self) -> List[str]:
        """Find potential I/O optimization opportunities."""
        suggestions = [
            "Batch file operations",
            "Use buffered I/O for large files",
            "Consider asynchronous I/O for network operations",
            "Use compression for large data transfers"
        ]
        return suggestions

    def _find_caching_opportunities(self) -> List[str]:
        """Find potential caching opportunities."""
        suggestions = [
            "Cache parsed configuration files",
            "Cache expensive database queries",
            "Cache computed results with TTL",
            "Use Redis/Memcached for distributed caching"
        ]
        return suggestions

    @monitor_performance("generate_quality_dashboard")
    def generate_quality_dashboard(self) -> QualityDashboard:
        """Generate a comprehensive quality dashboard."""
        from datetime import datetime

        # Collect all analysis data
        complexity_data = self._get_complexity_metrics()
        dead_code_data = self._get_dead_code_metrics()
        duplication_data = self._get_duplication_metrics()
        coupling_data = self._get_coupling_metrics()
        architecture_data = self._get_architecture_metrics()

        # Calculate overall score
        overall_score = self._calculate_overall_score(
            complexity_data, dead_code_data, duplication_data, coupling_data, architecture_data
        )

        # Determine grade
        grade = self._calculate_grade(overall_score)

        # Get top issues
        top_complexity = self._get_top_complexity_issues()
        top_dead_code = self._get_top_dead_code_issues()
        top_duplication = self._get_top_duplication_issues()

        # Generate recommendations
        priority_actions = self._determine_priority_actions_from_dashboard(
            top_complexity, top_dead_code, top_duplication
        )
        quick_wins = self._identify_quick_wins(top_dead_code)
        long_term_improvements = self._identify_long_term_improvements(complexity_data)

        return QualityDashboard(
            overall_score=overall_score,
            grade=grade,
            analysis_timestamp=datetime.now().isoformat(),
            total_files=self._count_total_files(),
            total_functions=complexity_data.get("total_functions", 0),
            total_lines=self._count_total_lines(),
            complexity_score=complexity_data.get("score", 0.0),
            maintainability_score=self._calculate_maintainability_score(),
            testability_score=self._calculate_testability_score(),
            reliability_score=self._calculate_reliability_score(),
            security_score=self._calculate_security_score(),
            performance_score=self._calculate_performance_score(),
            complexity_metrics=complexity_data,
            dead_code_metrics=dead_code_data,
            duplication_metrics=duplication_data,
            coupling_metrics=coupling_data,
            architecture_metrics=architecture_data,
            top_complexity_issues=top_complexity,
            top_dead_code_issues=top_dead_code,
            top_duplication_issues=top_duplication,
            priority_actions=priority_actions,
            quick_wins=quick_wins,
            long_term_improvements=long_term_improvements
        )

    def _get_complexity_metrics(self) -> Dict[str, Any]:
        """Get comprehensive complexity metrics."""
        try:
            complexity_results = self.pyscn_analyzer.analyze_complexity(self.project_root)

            if not complexity_results:
                return {"total_functions": 0, "average_complexity": 0, "high_risk_count": 0, "score": 100.0}

            total_complexity = sum(func.get("complexity", 0) for func in complexity_results)
            average_complexity = total_complexity / len(complexity_results) if complexity_results else 0

            # Calculate high-risk functions (complexity > 15)
            high_risk_count = sum(1 for func in complexity_results if func.get("complexity", 0) > 15)

            # Calculate score (lower average and fewer high-risk = higher score)
            base_score = 100.0
            complexity_penalty = min(average_complexity * 2, 30.0)  # Max 30 point penalty for complexity
            risk_penalty = min(high_risk_count * 5, 40.0)  # Max 40 point penalty for high-risk functions

            score = max(0.0, base_score - complexity_penalty - risk_penalty)

            return {
                "total_functions": len(complexity_results),
                "average_complexity": average_complexity,
                "high_risk_count": high_risk_count,
                "score": score
            }

        except Exception as e:
            logger.error(f"Error getting complexity metrics: {e}")
            return {"total_functions": 0, "average_complexity": 0, "high_risk_count": 0, "score": 0.0}

    def _get_dead_code_metrics(self) -> Dict[str, Any]:
        """Get comprehensive dead code metrics."""
        try:
            dead_code_results = self.pyscn_analyzer.detect_dead_code(self.project_root)

            if not dead_code_results:
                return {"total_findings": 0, "critical_count": 0, "warning_count": 0, "score": 100.0}

            critical_count = sum(1 for finding in dead_code_results if finding.get("severity") == "critical")
            warning_count = sum(1 for finding in dead_code_results if finding.get("severity") == "warning")

            # Calculate score (fewer findings = higher score)
            base_score = 100.0
            critical_penalty = min(critical_count * 10, 50.0)  # Max 50 point penalty for critical issues
            warning_penalty = min(warning_count * 2, 20.0)  # Max 20 point penalty for warnings

            score = max(0.0, base_score - critical_penalty - warning_penalty)

            return {
                "total_findings": len(dead_code_results),
                "critical_count": critical_count,
                "warning_count": warning_count,
                "score": score
            }

        except Exception as e:
            logger.error(f"Error getting dead code metrics: {e}")
            return {"total_findings": 0, "critical_count": 0, "warning_count": 0, "score": 0.0}

    def _get_duplication_metrics(self) -> Dict[str, Any]:
        """Get comprehensive duplication metrics."""
        # This would typically use pyscn's clone detection
        # For now, return placeholder data
        return {
            "total_groups": 0,
            "duplication_percentage": 0.0,
            "score": 100.0
        }

    def _get_coupling_metrics(self) -> Dict[str, Any]:
        """Get comprehensive coupling metrics."""
        try:
            coupling_results = self.pyscn_analyzer.analyze_coupling(self.project_root)

            if not coupling_results:
                return {"total_classes": 0, "high_coupling_count": 0, "average_coupling": 0.0, "score": 100.0}

            # Calculate metrics
            total_classes = len(coupling_results)
            high_coupling_count = sum(1 for cls in coupling_results if cls.get("coupling", 0) > 10)
            average_coupling = sum(cls.get("coupling", 0) for cls in coupling_results) / total_classes if total_classes > 0 else 0

            # Calculate score (lower coupling = higher score)
            base_score = 100.0
            coupling_penalty = min(average_coupling * 5, 40.0)  # Max 40 point penalty for coupling
            high_coupling_penalty = min(high_coupling_count * 10, 30.0)  # Max 30 point penalty for high coupling

            score = max(0.0, base_score - coupling_penalty - high_coupling_penalty)

            return {
                "total_classes": total_classes,
                "high_coupling_count": high_coupling_count,
                "average_coupling": average_coupling,
                "score": score
            }

        except Exception as e:
            logger.error(f"Error getting coupling metrics: {e}")
            return {"total_classes": 0, "high_coupling_count": 0, "average_coupling": 0.0, "score": 0.0}

    def _get_architecture_metrics(self) -> Dict[str, Any]:
        """Get comprehensive architecture metrics."""
        violations = self.analyze_architecture_compliance()

        high_severity_violations = sum(1 for v in violations if v.severity == "high")
        medium_severity_violations = sum(1 for v in violations if v.severity == "medium")
        low_severity_violations = sum(1 for v in violations if v.severity == "low")

        # Calculate score (fewer violations = higher score)
        base_score = 100.0
        high_penalty = min(high_severity_violations * 15, 60.0)  # Max 60 point penalty
        medium_penalty = min(medium_severity_violations * 5, 25.0)  # Max 25 point penalty
        low_penalty = min(low_severity_violations * 1, 10.0)  # Max 10 point penalty

        score = max(0.0, base_score - high_penalty - medium_penalty - low_penalty)

        return {
            "total_violations": len(violations),
            "high_severity_violations": high_severity_violations,
            "medium_severity_violations": medium_severity_violations,
            "low_severity_violations": low_severity_violations,
            "score": score
        }

    def _calculate_overall_score(self, complexity, dead_code, duplication, coupling, architecture) -> float:
        """Calculate overall quality score."""
        # Weighted average of category scores
        weights = {
            "complexity": 0.25,
            "dead_code": 0.20,
            "duplication": 0.15,
            "coupling": 0.20,
            "architecture": 0.20
        }

        scores = {
            "complexity": complexity.get("score", 0.0),
            "dead_code": dead_code.get("score", 0.0),
            "duplication": duplication.get("score", 0.0),
            "coupling": coupling.get("score", 0.0),
            "architecture": architecture.get("score", 0.0)
        }

        overall_score = sum(scores[category] * weight for category, weight in weights.items())
        return min(100.0, max(0.0, overall_score))

    def _calculate_grade(self, score: float) -> str:
        """Calculate letter grade from score."""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"

    def _calculate_maintainability_score(self) -> float:
        """Calculate maintainability score based on various factors."""
        # This is a simplified calculation
        # In practice, would use more sophisticated metrics
        return 85.0  # Placeholder

    def _calculate_testability_score(self) -> float:
        """Calculate testability score."""
        return 80.0  # Placeholder

    def _calculate_reliability_score(self) -> float:
        """Calculate reliability score."""
        return 90.0  # Placeholder

    def _calculate_security_score(self) -> float:
        """Calculate security score."""
        return 95.0  # Placeholder

    def _calculate_performance_score(self) -> float:
        """Calculate performance score."""
        return 88.0  # Placeholder

    def _get_top_complexity_issues(self) -> List[Dict[str, Any]]:
        """Get top complexity issues."""
        try:
            complexity_results = self.pyscn_analyzer.analyze_complexity(self.project_root)
            # Sort by complexity (highest first) and return top 5
            sorted_results = sorted(
                complexity_results,
                key=lambda x: x.get("complexity", 0),
                reverse=True
            )[:5]

            return [
                {
                    "function_name": func.get("name", ""),
                    "file_path": func.get("file_path", ""),
                    "complexity": func.get("complexity", 0),
                    "line_number": func.get("line_number", 0)
                }
                for func in sorted_results
            ]

        except Exception as e:
            logger.error(f"Error getting top complexity issues: {e}")
            return []

    def _get_top_dead_code_issues(self) -> List[Dict[str, Any]]:
        """Get top dead code issues."""
        try:
            dead_code_results = self.pyscn_analyzer.detect_dead_code(self.project_root)

            # Sort by severity and return top 5
            severity_order = {"critical": 3, "warning": 2, "info": 1}

            sorted_results = sorted(
                dead_code_results,
                key=lambda x: severity_order.get(x.get("severity", "info"), 0),
                reverse=True
            )[:5]

            return [
                {
                    "file_path": finding.get("location", {}).get("file_path", ""),
                    "line_number": finding.get("location", {}).get("start_line", 0),
                    "reason": finding.get("reason", ""),
                    "severity": finding.get("severity", "unknown")
                }
                for finding in sorted_results
            ]

        except Exception as e:
            logger.error(f"Error getting top dead code issues: {e}")
            return []

    def _get_top_duplication_issues(self) -> List[Dict[str, Any]]:
        """Get top duplication issues."""
        # Placeholder for now
        return []

    def _determine_priority_actions_from_dashboard(self, complexity_issues, dead_code_issues, duplication_issues) -> List[Dict[str, Any]]:
        """Determine priority actions for the dashboard."""
        actions = []

        # Add complexity actions
        for issue in complexity_issues:
            if issue["complexity"] >= 20:
                actions.append({
                    "type": "complexity_reduction",
                    "priority": "high",
                    "function": issue["function_name"],
                    "file": issue["file_path"],
                    "description": f"Reduce complexity of {issue['function_name']} from {issue['complexity']} to under 15"
                })

        # Add dead code actions
        for issue in dead_code_issues:
            if issue["severity"] == "critical":
                actions.append({
                    "type": "dead_code_removal",
                    "priority": "high",
                    "file": issue["file_path"],
                    "line": issue["line_number"],
                    "description": f"Remove critical dead code: {issue['reason']}"
                })

        return actions

    def _identify_quick_wins(self, dead_code_issues) -> List[Dict[str, Any]]:
        """Identify quick win improvements."""
        quick_wins = []

        # Dead code removal is usually a quick win
        for issue in dead_code_issues:
            if issue["severity"] == "critical":
                quick_wins.append({
                    "type": "dead_code_cleanup",
                    "effort": "low",
                    "impact": "high",
                    "description": f"Remove dead code in {os.path.basename(issue['file_path'])}:{issue['line_number']}"
                })

        return quick_wins

    def _identify_long_term_improvements(self, complexity_data) -> List[Dict[str, Any]]:
        """Identify long-term architectural improvements."""
        improvements = []

        if complexity_data.get("high_risk_count", 0) > 10:
            improvements.append({
                "type": "architecture_refactoring",
                "effort": "high",
                "impact": "very_high",
                "description": "Consider microservices or modular architecture to reduce function complexity"
            })

        return improvements

    def _count_total_files(self) -> int:
        """Count total files in project."""
        count = 0
        for root, dirs, files in os.walk(self.project_root):
            # Skip common directories
            dirs[:] = [d for d in dirs if d not in {".git", "__pycache__", "node_modules", ".venv", "venv", ".pyscn"}]
            count += len([f for f in files if f.endswith('.py')])
        return count

    def _count_total_lines(self) -> int:
        """Count total lines of code in project."""
        total_lines = 0
        for root, dirs, files in os.walk(self.project_root):
            # Skip common directories
            dirs[:] = [d for d in dirs if d not in {".git", "__pycache__", "node_modules", ".venv", "venv", ".pyscn"}]
            for file in files:
                if file.endswith('.py'):
                    try:
                        with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                            total_lines += len(f.readlines())
                    except Exception:
                        pass
        return total_lines

    @monitor_performance("detect_code_smells")
    def detect_code_smells(self) -> List[Dict[str, Any]]:
        """Detect common code smells and anti-patterns."""
        code_smells = []

        try:
            # Analyze for common code smells
            code_smells.extend(self._detect_long_methods())
            code_smells.extend(self._detect_large_classes())
            code_smells.extend(self._detect_feature_envy())
            code_smells.extend(self._detect_data_clumps())
            code_smells.extend(self._detect_primitive_obsession())

        except Exception as e:
            logger.error(f"Error detecting code smells: {e}")

        return code_smells

    def _detect_long_methods(self) -> List[Dict[str, Any]]:
        """Detect methods that are too long."""
        smells = []

        try:
            complexity_results = self.pyscn_analyzer.analyze_complexity(self.project_root)

            for func in complexity_results:
                if func.get("complexity", 0) > 20:  # Very high complexity
                    smells.append({
                        "type": "long_method",
                        "file_path": func.get("file_path", ""),
                        "function_name": func.get("name", ""),
                        "line_number": func.get("line_number", 0),
                        "complexity": func.get("complexity", 0),
                        "description": f"Method '{func.get('name', '')}' is too long and complex",
                        "suggestion": "Consider breaking this method into smaller, more focused methods"
                    })

        except Exception as e:
            logger.error(f"Error detecting long methods: {e}")

        return smells

    def _detect_large_classes(self) -> List[Dict[str, Any]]:
        """Detect classes that are too large."""
        smells = []

        try:
            coupling_results = self.pyscn_analyzer.analyze_coupling(self.project_root)

            for cls in coupling_results:
                if cls.get("coupling", 0) > 15:  # High coupling
                    smells.append({
                        "type": "large_class",
                        "file_path": cls.get("file_path", ""),
                        "class_name": cls.get("name", ""),
                        "coupling": cls.get("coupling", 0),
                        "description": f"Class '{cls.get('name', '')}' has too many dependencies",
                        "suggestion": "Consider splitting this class or using dependency injection"
                    })

        except Exception as e:
            logger.error(f"Error detecting large classes: {e}")

        return smells

    def _detect_feature_envy(self) -> List[Dict[str, Any]]:
        """Detect feature envy (methods that use more external data than local)."""
        # This would require more sophisticated AST analysis
        # For now, return placeholder
        return []

    def _detect_data_clumps(self) -> List[Dict[str, Any]]:
        """Detect data clumps (groups of parameters that are always passed together)."""
        # This would require more sophisticated AST analysis
        # For now, return placeholder
        return []

    def _detect_primitive_obsession(self) -> List[Dict[str, Any]]:
        """Detect primitive obsession (using primitives where objects would be better)."""
        # This would require more sophisticated AST analysis
        # For now, return placeholder
        return []

    @monitor_performance("suggest_automated_fixes")
    def suggest_automated_fixes(self) -> Dict[str, Any]:
        """Suggest automated fixes for common issues."""
        fixes = {
            "dead_code_removal": [],
            "import_optimization": [],
            "naming_convention_fixes": [],
            "complexity_reductions": []
        }

        try:
            # Get dead code findings that can be auto-fixed
            dead_code_findings = self.analyze_dead_code_patterns()

            for finding in dead_code_findings:
                if finding.fix_available and finding.severity == "critical":
                    fixes["dead_code_removal"].append({
                        "file_path": finding.file_path,
                        "line_number": finding.line_number,
                        "action": "remove_dead_code",
                        "description": finding.suggestion,
                        "confidence": 0.95  # High confidence for dead code removal
                    })

            # Get architecture violations for naming fixes
            architecture_violations = self.analyze_architecture_compliance()

            for violation in architecture_violations:
                if violation.violation_type == "naming_convention":
                    fixes["naming_convention_fixes"].append({
                        "file_path": violation.file_path,
                        "action": "rename_file",
                        "old_name": os.path.basename(violation.file_path),
                        "new_name": self._suggest_proper_name(os.path.basename(violation.file_path)),
                        "description": violation.suggestion,
                        "confidence": 0.85
                    })

        except Exception as e:
            logger.error(f"Error suggesting automated fixes: {e}")

        return fixes

    def _suggest_proper_name(self, current_name: str) -> str:
        """Suggest a proper name for a file."""
        if 'test' in current_name.lower() and not current_name.startswith('test_'):
            # Convert test_file.py to test_file.py (add test_ prefix)
            if not current_name.startswith('test_'):
                return f"test_{current_name}"
        elif current_name.endswith('_test.py') and not current_name.startswith('test_'):
            # Convert file_test.py to test_file.py
            base_name = current_name.replace('_test.py', '.py')
            return f"test_{base_name}"

        return current_name

    @monitor_performance("analyze_technical_debt")
    def analyze_technical_debt(self) -> Dict[str, Any]:
        """Analyze and quantify technical debt."""
        debt_analysis = {
            "total_debt_hours": 0,
            "debt_by_category": {},
            "debt_by_severity": {},
            "debt_by_file": {},
            "top_debt_items": []
        }

        try:
            # Analyze complexity debt
            complexity_suggestions = self.analyze_complexity_patterns()
            complexity_debt = len(complexity_suggestions) * 4  # 4 hours per complex function
            debt_analysis["debt_by_category"]["complexity"] = complexity_debt

            # Analyze dead code debt
            dead_code_findings = self.analyze_dead_code_patterns()
            dead_code_debt = len([f for f in dead_code_findings if f.severity == "critical"]) * 1  # 1 hour per critical dead code
            debt_analysis["debt_by_category"]["dead_code"] = dead_code_debt

            # Analyze architecture debt
            architecture_violations = self.analyze_architecture_compliance()
            high_severity_violations = [v for v in architecture_violations if v.severity == "high"]
            architecture_debt = len(high_severity_violations) * 8  # 8 hours per high-severity violation
            debt_analysis["debt_by_category"]["architecture"] = architecture_debt

            # Calculate total debt
            debt_analysis["total_debt_hours"] = sum(debt_analysis["debt_by_category"].values())

            # Get top debt items
            debt_analysis["top_debt_items"] = self._get_top_technical_debt_items(
                complexity_suggestions, dead_code_findings, architecture_violations
            )

        except Exception as e:
            logger.error(f"Error analyzing technical debt: {e}")

        return debt_analysis

    def _get_top_technical_debt_items(self, complexity_suggestions, dead_code_findings, architecture_violations) -> List[Dict[str, Any]]:
        """Get the top technical debt items by estimated effort."""
        debt_items = []

        # Add complexity debt items
        for suggestion in complexity_suggestions:
            debt_items.append({
                "type": "complexity",
                "file_path": suggestion.file_path,
                "function_name": suggestion.function_name,
                "estimated_hours": 4,
                "description": f"Refactor complex function: {suggestion.suggested_refactoring}",
                "priority": "medium" if suggestion.current_complexity < 25 else "high"
            })

        # Add critical dead code debt items
        for finding in dead_code_findings:
            if finding.severity == "critical":
                debt_items.append({
                    "type": "dead_code",
                    "file_path": finding.file_path,
                    "line_number": finding.line_number,
                    "estimated_hours": 1,
                    "description": f"Remove dead code: {finding.reason}",
                    "priority": "high"
                })

        # Add architecture debt items
        for violation in architecture_violations:
            if violation.severity == "high":
                debt_items.append({
                    "type": "architecture",
                    "file_path": violation.file_path,
                    "estimated_hours": 8,
                    "description": violation.description,
                    "priority": "high"
                })

        # Sort by estimated hours (descending) and return top 10
        debt_items.sort(key=lambda x: x["estimated_hours"], reverse=True)
        return debt_items[:10]

    @monitor_performance("generate_comprehensive_report")
    def generate_comprehensive_report(self, output_path: str = "comprehensive_report.html") -> bool:
        """Generate a comprehensive quality report including dashboard and all analysis."""
        try:
            # Generate quality dashboard
            dashboard = self.generate_quality_dashboard()

            # Generate HTML report with dashboard data
            html_content = self._generate_dashboard_html(dashboard)

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)

            logger.info(f"Comprehensive report generated: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error generating comprehensive report: {e}")
            return False

    def _generate_dashboard_html(self, dashboard: QualityDashboard) -> str:
        """Generate HTML for the quality dashboard."""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Code Quality Dashboard - {dashboard.grade} ({dashboard.overall_score}%)</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .score {{ font-size: 48px; font-weight: bold; color: {self._get_score_color(dashboard.overall_score)}; }}
        .grade {{ font-size: 24px; color: #666; }}
        .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 30px 0; }}
        .metric-card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; }}
        .metric-value {{ font-size: 24px; font-weight: bold; }}
        .metric-label {{ color: #666; margin-top: 5px; }}
        .section {{ margin: 30px 0; }}
        .section h3 {{ color: #333; border-bottom: 2px solid #eee; padding-bottom: 10px; }}
        .issue-list {{ background: #fff; border: 1px solid #ddd; border-radius: 5px; }}
        .issue-item {{ padding: 15px; border-bottom: 1px solid #eee; }}
        .issue-item:last-child {{ border-bottom: none; }}
        .priority-high {{ border-left: 4px solid #dc3545; }}
        .priority-medium {{ border-left: 4px solid #ffc107; }}
        .priority-low {{ border-left: 4px solid #28a745; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Code Quality Dashboard</h1>
            <div class="score">{dashboard.overall_score:.1f}%</div>
            <div class="grade">Grade: {dashboard.grade}</div>
            <p>Analysis Date: {dashboard.analysis_timestamp}</p>
        </div>

        <div class="metrics">
            <div class="metric-card">
                <div class="metric-value">{dashboard.total_files}</div>
                <div class="metric-label">Files Analyzed</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{dashboard.total_functions}</div>
                <div class="metric-label">Functions</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{dashboard.total_lines:,}</div>
                <div class="metric-label">Lines of Code</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{dashboard.complexity_score:.1f}%</div>
                <div class="metric-label">Complexity Score</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{dashboard.maintainability_score:.1f}%</div>
                <div class="metric-label">Maintainability</div>
            </div>
        </div>

        <div class="section">
            <h3>🚨 Priority Actions</h3>
            <div class="issue-list">
"""

        for action in dashboard.priority_actions[:5]:  # Top 5
            priority_class = f"priority-{action['priority']}"
            html += f"""
                <div class="issue-item {priority_class}">
                    <strong>{action['type'].replace('_', ' ').title()}</strong><br>
                    {action['description']}
                </div>
"""

        html += """
            </div>
        </div>

        <div class="section">
            <h3>💡 Quick Wins</h3>
            <div class="issue-list">
"""

        for win in dashboard.quick_wins[:3]:  # Top 3
            html += f"""
                <div class="issue-item">
                    <strong>{win['type'].replace('_', ' ').title()}</strong><br>
                    {win['description']} (Effort: {win['effort']}, Impact: {win['impact']})
                </div>
"""

        html += """
            </div>
        </div>

        <div class="section">
            <h3>📈 Long-term Improvements</h3>
            <div class="issue-list">
"""

        for improvement in dashboard.long_term_improvements[:3]:  # Top 3
            html += f"""
                <div class="issue-item">
                    <strong>{improvement['type'].replace('_', ' ').title()}</strong><br>
                    {improvement['description']} (Effort: {improvement['effort']}, Impact: {improvement['impact']})
                </div>
"""

        html += f"""
            </div>
        </div>

        <div class="section">
            <p><em>Generated by Codomyrmex Code Review Module</em></p>
        </div>
    </div>
</body>
</html>
"""
        return html

    def _get_score_color(self, score: float) -> str:
        """Get color for score display."""
        if score >= 90:
            return "#28a745"  # Green
        elif score >= 80:
            return "#ffc107"  # Yellow
        elif score >= 70:
            return "#fd7e14"  # Orange
        else:
            return "#dc3545"  # Red


# Convenience functions
def analyze_file(file_path: str, analysis_types: List[str] = None) -> List[AnalysisResult]:
    """Analyze a single file."""
    reviewer = CodeReviewer()
    return reviewer.analyze_file(file_path, analysis_types)


def analyze_project(
    project_root: str,
    target_paths: List[str] = None,
    analysis_types: List[str] = None,
) -> AnalysisSummary:
    """Analyze an entire project."""
    reviewer = CodeReviewer(project_root)
    return reviewer.analyze_project(target_paths, analysis_types)


def check_quality_gates(project_root: str, thresholds: Dict[str, int] = None) -> QualityGateResult:
    """Check if project meets quality standards."""
    reviewer = CodeReviewer(project_root)
    reviewer.analyze_project()
    return reviewer.check_quality_gates(thresholds)


def generate_report(
    project_root: str,
    output_path: str,
    format: str = "html",
    analysis_types: List[str] = None
) -> bool:
    """Generate analysis report."""
    reviewer = CodeReviewer(project_root)
    reviewer.analyze_project(analysis_types=analysis_types)
    return reviewer.generate_report(output_path, format)
