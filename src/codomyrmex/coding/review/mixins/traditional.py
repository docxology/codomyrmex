import json
import re
import subprocess

from codomyrmex.coding.review.models import (
    AnalysisResult,
    Language,
    SeverityLevel,
)
from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)


try:
    from codomyrmex.performance import monitor_performance
except ImportError:
    def monitor_performance(*args, **kwargs):
        def decorator(func):
            return func
        return decorator


class TraditionalMixin:
    """TraditionalMixin functionality."""

    def _run_traditional_analysis(self, file_path: str, analysis_types: list[str]) -> list[AnalysisResult]:
        """Run traditional static analysis tools."""
        results = []
        language = self._detect_language(file_path)

        if language == Language.PYTHON:
            results.extend(self._analyze_python_file(file_path, analysis_types))

        return results

    def _analyze_python_file(self, file_path: str, analysis_types: list[str]) -> list[AnalysisResult]:
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
