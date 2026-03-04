"""Documentation Consistency Checker.

Provides documentation validation checking for naming conventions,
formatting standards, and content alignment.
"""

import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)

__all__ = ["ConsistencyIssue", "ConsistencyReport", "DocumentationConsistencyChecker", "check_documentation_consistency"]


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
        self.mandatory_sections = self.config.get("mandatory_sections", ["Overview", "Purpose", "Navigation"])

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
            path = Path(file_path)
            content = path.read_text(encoding='utf-8', errors='ignore')
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

                # Check for broken internal links (simple check)
                internal_links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', line)
                for text, link in internal_links:
                    if link.startswith("./") or (not link.startswith("http") and not link.startswith("#")):
                        link_path = path.parent / link.split("#")[0]
                        if not link_path.exists():
                            issues.append(ConsistencyIssue(
                                file_path=file_path,
                                line_number=i,
                                issue_type="broken_link",
                                description=f"Internal link '{link}' for '{text}' does not exist",
                                severity="warning",
                                suggestion=f"Check if {link} is spelled correctly and exists."
                            ))

            # Check for mandatory sections in RASP files
            if path.name in ["README.md", "SPEC.md", "AGENTS.md", "PAI.md"]:
                for section in self.mandatory_sections:
                    if not re.search(rf'^#+.*{section}', content, re.IGNORECASE | re.MULTILINE):
                        issues.append(ConsistencyIssue(
                            file_path=file_path,
                            line_number=1,
                            issue_type="missing_section",
                            description=f"Mandatory section '{section}' is missing",
                            severity="warning",
                            suggestion=f"Add a '## {section}' section to the file."
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
