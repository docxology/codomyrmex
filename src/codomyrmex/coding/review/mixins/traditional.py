import json
import re
import subprocess

from codomyrmex.coding.review.models import (
    AnalysisResult,
    Language,
    SeverityLevel,
)
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class TraditionalMixin:
    """TraditionalMixin functionality."""

    def _run_traditional_analysis(
        self, file_path: str, analysis_types: list[str]
    ) -> list[AnalysisResult]:
        """Run traditional static analysis tools."""
        results = []
        language = self._detect_language(file_path)

        if language == Language.PYTHON:
            results.extend(self._analyze_python_file(file_path, analysis_types))

        return results

    def _analyze_python_file(
        self, file_path: str, analysis_types: list[str]
    ) -> list[AnalysisResult]:
        """Analyze a Python file using traditional tools."""
        results = []

        # Pylint analysis
        if "quality" in analysis_types and self.tools_available["pylint"]:
            results.extend(self._run_pylint(file_path))

        # Ruff analysis
        if "style" in analysis_types and self.tools_available["ruff"]:
            results.extend(self._run_ruff(file_path))

        # Ty type checking
        if "quality" in analysis_types and self.tools_available["ty"]:
            results.extend(self._run_ty(file_path))

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
                        )
                    )

        except (subprocess.TimeoutExpired, json.JSONDecodeError, Exception) as e:
            logger.error("Error running pylint on %s: %s", file_path, e)

        return results

    def _run_ruff(self, file_path: str) -> list[AnalysisResult]:
        """Run the repository Ruff rules on a file."""
        results = []

        try:
            cmd = ["ruff", "check", "--output-format", "concise", file_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.stdout:
                for line in result.stdout.strip().split("\n"):
                    match = re.match(r"(.+?):(\d+):(\d+):\s+([A-Z]\d+)\s+(.+)", line)
                    if match:
                        fp, line_num, col_num, rule_id, message = match.groups()
                        severity = (
                            SeverityLevel.ERROR
                            if rule_id.startswith(("E", "F", "B", "S"))
                            else SeverityLevel.WARNING
                        )
                        results.append(
                            AnalysisResult(
                                file_path=fp,
                                line_number=int(line_num),
                                column_number=int(col_num),
                                severity=severity,
                                message=message.strip(),
                                rule_id=rule_id,
                                category="ruff",
                            )
                        )

        except (subprocess.TimeoutExpired, Exception) as e:
            logger.error("Error running ruff on %s: %s", file_path, e)

        return results

    def _run_ty(self, file_path: str) -> list[AnalysisResult]:
        """Run repository type checking with Ty on a file."""
        results = []

        try:
            cmd = ["ty", "check", "--output-format", "concise", file_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            output = "\n".join(part for part in (result.stdout, result.stderr) if part)
            for line in output.strip().splitlines():
                match = re.match(
                    r"(.+?):(\d+):(\d+):\s+(error|warning|note):\s+(.+?)(?:\s+\[([^\]]+)\])?$",
                    line,
                )
                if match:
                    fp, line_num, col_num, level, message, error_code = match.groups()
                    severity = {
                        "error": SeverityLevel.ERROR,
                        "warning": SeverityLevel.WARNING,
                        "note": SeverityLevel.INFO,
                    }[level]
                    results.append(
                        AnalysisResult(
                            file_path=fp,
                            line_number=int(line_num),
                            column_number=int(col_num),
                            severity=severity,
                            message=message,
                            rule_id=error_code or "TY",
                            category="ty",
                        )
                    )

        except (subprocess.TimeoutExpired, Exception) as e:
            logger.error("Error running ty on %s: %s", file_path, e)

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
            logger.error("Error running bandit on %s: %s", file_path, e)

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
            logger.error("Error running vulture on %s: %s", file_path, e)

        return results
