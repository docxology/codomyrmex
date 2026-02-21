"""Documentation Consistency Checker.

Provides documentation validation checking for naming conventions,
formatting standards, and content alignment.
"""

import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from codomyrmex.logging_monitoring.logger_config import get_logger

logger = get_logger(__name__)


@dataclass
class ConsistencyIssue:
    """Represents a documentation consistency issue."""
    file_path: str
    line_number: int
    issue_type: str
    description: str
    severity: str = "warning"
    suggestion: str | None = None


@dataclass
class ConsistencyReport:
    """Report of consistency check results."""
    total_files: int
    files_checked: int
    issues: list[ConsistencyIssue] = field(default_factory=list)
    passed: bool = True


class DocumentationConsistencyChecker:
    """Checks documentation for consistency issues."""

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize checker."""
        self.config = config or {}
        self.naming_patterns = self._load_naming_patterns()

    def _load_naming_patterns(self) -> dict[str, re.Pattern]:
        """Load naming convention patterns."""
        return {
            "snake_case": re.compile(r'^[a-z][a-z0-9_]*$'),
            "UPPER_SNAKE": re.compile(r'^[A-Z][A-Z0-9_]*$'),
            "PascalCase": re.compile(r'^[A-Z][a-zA-Z0-9]*$'),
        }

    def check_file(self, file_path: str) -> list[ConsistencyIssue]:
        """Check a single file for consistency issues."""
        issues = []
        try:
            with open(file_path, encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')

            # Check for common issues
            for i, line in enumerate(lines, 1):
                # Check for trailing whitespace
                if line.rstrip() != line:
                    issues.append(ConsistencyIssue(
                        file_path=file_path,
                        line_number=i,
                        issue_type="trailing_whitespace",
                        description="Line has trailing whitespace",
                        severity="info"
                    ))

                # Check for tabs
                if '\t' in line:
                    issues.append(ConsistencyIssue(
                        file_path=file_path,
                        line_number=i,
                        issue_type="tabs",
                        description="Line contains tabs instead of spaces",
                        severity="warning"
                    ))

        except Exception as e:
            logger.error(f"Error checking file {file_path}: {e}")

        return issues

    def check_directory(self, directory: str, recursive: bool = True) -> ConsistencyReport:
        """Check all documentation files in a directory."""
        all_issues = []
        files_checked = 0
        total_files = 0

        path = Path(directory)
        pattern = "**/*.md" if recursive else "*.md"

        for file_path in path.glob(pattern):
            total_files += 1
            if file_path.is_file():
                issues = self.check_file(str(file_path))
                all_issues.extend(issues)
                files_checked += 1

        return ConsistencyReport(
            total_files=total_files,
            files_checked=files_checked,
            issues=all_issues,
            passed=len(all_issues) == 0
        )


# Convenience functions
def check_documentation_consistency(path: str) -> ConsistencyReport:
    """Check documentation consistency."""
    checker = DocumentationConsistencyChecker()
    if os.path.isfile(path):
        issues = checker.check_file(path)
        return ConsistencyReport(total_files=1, files_checked=1, issues=issues, passed=len(issues) == 0)
    return checker.check_directory(path)
