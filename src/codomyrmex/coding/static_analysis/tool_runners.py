"""
Tool-specific runner methods for static analysis.

Each method runs a specific external analysis tool and converts its output
into a list of AnalysisResult objects.
"""

import json
import os
import re
import subprocess

from codomyrmex.coding.static_analysis.pyrefly_runner import run_pyrefly
from codomyrmex.logging_monitoring.core.logger_config import get_logger

from .models import AnalysisResult, SeverityLevel

logger = get_logger(__name__)


class ToolRunner:
    """Runs external analysis tools and converts their output to AnalysisResult."""

    def __init__(self, tools_available: dict[str, bool], project_root: str) -> None:
        self.tools_available = tools_available
        self.project_root = project_root

    # ------------------------------------------------------------------ Python

    def run_pylint(self, file_path: str) -> list[AnalysisResult]:
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

    def run_flake8(self, file_path: str) -> list[AnalysisResult]:
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
                            fp, line_num, col_num, message = parts

                            code_match = re.match(r"^([A-Z]\d{3})", message.strip())
                            rule_id = code_match.group(1) if code_match else "E999"

                            severity = SeverityLevel.WARNING
                            if rule_id.startswith("E"):
                                severity = SeverityLevel.ERROR
                            elif rule_id.startswith("W"):
                                severity = SeverityLevel.WARNING
                            elif rule_id.startswith("F"):
                                severity = SeverityLevel.ERROR

                            try:
                                ln = int(line_num)
                                col = int(col_num)
                            except ValueError:
                                logger.debug("flake8: could not parse line/col from: %r", line)
                                continue

                            results.append(
                                AnalysisResult(
                                    file_path=fp,
                                    line_number=ln,
                                    column_number=col,
                                    severity=severity,
                                    message=message.strip(),
                                    rule_id=rule_id,
                                    category="flake8",
                                )
                            )

        except (subprocess.TimeoutExpired, Exception) as e:
            logger.error(f"Error running flake8 on {file_path}: {e}")

        return results

    def run_mypy(self, file_path: str) -> list[AnalysisResult]:
        """Run mypy type checking on a file."""
        results = []
        try:
            cmd = ["mypy", "--show-error-codes", "--no-error-summary", file_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.stdout:
                for line in result.stdout.strip().split("\n"):
                    if ":" in line and "error:" in line:
                        match = re.match(
                            r"([^:]+):(\d+):(\d+): error: (.+) \[([^\]]+)\]", line
                        )
                        if match:
                            fp, line_num, col_num, message, error_code = match.groups()

                            results.append(
                                AnalysisResult(
                                    file_path=fp,
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

    def run_bandit(self, file_path: str) -> list[AnalysisResult]:
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

    def run_radon(self, file_path: str) -> list[AnalysisResult]:
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
                        if complexity > 10:
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

    def run_vulture(self, file_path: str) -> list[AnalysisResult]:
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
                            fp, line_num, message = parts

                            try:
                                ln = int(line_num)
                            except ValueError:
                                logger.debug("vulture: could not parse line from: %r", line)
                                continue

                            results.append(
                                AnalysisResult(
                                    file_path=fp,
                                    line_number=ln,
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

    def run_safety(self, file_path: str) -> list[AnalysisResult]:
        """Run safety dependency analysis."""
        results = []
        try:
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

    def run_pyrefly(self, file_path: str) -> list[AnalysisResult]:
        """Run Pyrefly type checking on a file."""
        results = []
        try:
            pyrefly_result = run_pyrefly(file_path)

            if pyrefly_result.success and pyrefly_result.issues:
                severity_map = {
                    "error": SeverityLevel.ERROR,
                    "warning": SeverityLevel.WARNING,
                    "info": SeverityLevel.INFO,
                }

                for issue in pyrefly_result.issues:
                    results.append(
                        AnalysisResult(
                            file_path=issue.file_path or file_path,
                            line_number=issue.line,
                            column_number=issue.column,
                            severity=severity_map.get(
                                issue.severity, SeverityLevel.ERROR
                            ),
                            message=issue.message,
                            rule_id=issue.rule_id or "PYREFLY_ERROR",
                            category="type_checking",
                        )
                    )

            if pyrefly_result.error_message:
                logger.warning(
                    f"Pyrefly reported error for {file_path}: {pyrefly_result.error_message}"
                )

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

    # --------------------------------------------------------------- JavaScript

    def run_eslint(self, file_path: str) -> list[AnalysisResult]:
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

    def run_typescript_compiler(self, file_path: str) -> list[AnalysisResult]:
        """Run TypeScript compiler analysis."""
        results = []
        try:
            cmd = ["tsc", "--noEmit", "--pretty", "false", file_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.stderr:
                for line in result.stderr.strip().split("\n"):
                    if ":" in line and "error" in line:
                        match = re.match(
                            r"([^:]+):(\d+):(\d+) - error TS(\d+): (.+)", line
                        )
                        if match:
                            fp, line_num, col_num, error_code, message = match.groups()

                            results.append(
                                AnalysisResult(
                                    file_path=fp,
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

    # -------------------------------------------------------------------- Java

    def run_spotbugs(self, file_path: str) -> list[AnalysisResult]:
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
