"""Pyrefly Runner for Codomyrmex Static Analysis module.

Provides integration with Pyrefly static analysis tool.
"""

import json
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)


@dataclass
class PyreflyIssue:
    """Represents a Pyrefly issue."""
    file_path: str
    line: int
    column: int
    severity: str
    message: str
    rule_id: str | None = None


@dataclass
class PyreflyResult:
    """Result of Pyrefly analysis."""
    success: bool
    issues: list[PyreflyIssue] = field(default_factory=list)
    error_message: str | None = None
    files_analyzed: int = 0


class PyreflyRunner:
    """Runs Pyrefly static analysis."""

    def __init__(self, config_path: str | None = None):
        """Initialize runner."""
        self.config_path = config_path
        self.pyrefly_available = self._check_pyrefly()

    def _check_pyrefly(self) -> bool:
        """Check if Pyrefly is available."""
        try:
            subprocess.run(["pyrefly", "--version"], capture_output=True, timeout=5)
            return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def analyze_file(self, file_path: str) -> PyreflyResult:
        """Analyze a single file."""
        if not self.pyrefly_available:
            return PyreflyResult(
                success=False,
                error_message="Pyrefly is not installed"
            )

        try:
            result = subprocess.run(
                ["pyrefly", "check", file_path, "--output-format", "json"],
                capture_output=True,
                text=True,
                timeout=60
            )

            issues = self._parse_output(result.stdout)
            return PyreflyResult(
                success=True,
                issues=issues,
                files_analyzed=1
            )

        except subprocess.TimeoutExpired:
            return PyreflyResult(success=False, error_message="Pyrefly timed out")
        except Exception as e:
            return PyreflyResult(success=False, error_message=str(e))

    def analyze_directory(self, directory: str) -> PyreflyResult:
        """Analyze all Python files in a directory."""
        if not self.pyrefly_available:
            return PyreflyResult(
                success=False,
                error_message="Pyrefly is not installed"
            )

        try:
            result = subprocess.run(
                ["pyrefly", "check", directory, "--output-format", "json"],
                capture_output=True,
                text=True,
                timeout=300
            )

            issues = self._parse_output(result.stdout)
            files_count = len(list(Path(directory).rglob("*.py")))

            return PyreflyResult(
                success=True,
                issues=issues,
                files_analyzed=files_count
            )

        except subprocess.TimeoutExpired:
            return PyreflyResult(success=False, error_message="Pyrefly timed out")
        except Exception as e:
            return PyreflyResult(success=False, error_message=str(e))

    def _parse_output(self, output: str) -> list[PyreflyIssue]:
        """Parse Pyrefly JSON output."""
        issues = []
        if not output.strip():
            return issues

        try:
            data = json.loads(output)
            for item in data.get("issues", []):
                issues.append(PyreflyIssue(
                    file_path=item.get("file", ""),
                    line=item.get("line", 0),
                    column=item.get("column", 0),
                    severity=item.get("severity", "warning"),
                    message=item.get("message", ""),
                    rule_id=item.get("rule_id")
                ))
        except json.JSONDecodeError:
            logger.warning("Failed to parse Pyrefly output as JSON")

        return issues


# Convenience functions
def run_pyrefly(path: str) -> PyreflyResult:
    """Run Pyrefly analysis on a path."""
    runner = PyreflyRunner()
    if Path(path).is_file():
        return runner.analyze_file(path)
    return runner.analyze_directory(path)

def check_pyrefly_available() -> bool:
    """Check if Pyrefly is available."""
    runner = PyreflyRunner()
    return runner.pyrefly_available
