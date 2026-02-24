"""
Linting submodule for static analysis.

Provides a pluggable rule-based linter with built-in rules for
common code quality issues.
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod


class LintSeverity(Enum):
    """Severity levels for lint issues."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class LintIssue:
    """A single lint issue found in code."""
    rule_id: str
    message: str
    severity: LintSeverity
    line_number: int | None
    file_path: str


@dataclass
class LintResult:
    """Collection of lint issues for a file."""
    file_path: str
    issues: list[LintIssue] = field(default_factory=list)

    def add_issue(self, issue: LintIssue) -> None:
        """Add an issue to the result."""
        self.issues.append(issue)

    @property
    def error_count(self) -> int:
        """Execute Error Count operations natively."""
        return sum(1 for i in self.issues if i.severity == LintSeverity.ERROR)

    @property
    def warning_count(self) -> int:
        """Execute Warning Count operations natively."""
        return sum(1 for i in self.issues if i.severity == LintSeverity.WARNING)

    @property
    def info_count(self) -> int:
        """Execute Info Count operations natively."""
        return sum(1 for i in self.issues if i.severity == LintSeverity.INFO)

    @property
    def has_errors(self) -> bool:
        """Execute Has Errors operations natively."""
        return self.error_count > 0

    @property
    def total_issues(self) -> int:
        """Execute Total Issues operations natively."""
        return len(self.issues)


class LintRule(ABC):
    """Abstract base class for lint rules."""

    @abstractmethod
    def check(self, code: str, file_path: str = "") -> list[LintIssue]:
        """Check code against this rule.

        Args:
            code: Source code to check.
            file_path: Path of the file being checked.

        Returns:
            List of issues found.
        """
        ...


class LineLengthRule(LintRule):
    """Check for lines exceeding maximum length."""

    def __init__(self, max_length: int = 88):
        """Execute   Init   operations natively."""
        self.max_length = max_length

    def check(self, code: str, file_path: str = "") -> list[LintIssue]:
        """Execute Check operations natively."""
        issues = []
        for i, line in enumerate(code.split("\n"), 1):
            if len(line) > self.max_length:
                issues.append(LintIssue(
                    rule_id="E501",
                    message=f"Line too long ({len(line)} > {self.max_length})",
                    severity=LintSeverity.WARNING,
                    line_number=i,
                    file_path=file_path,
                ))
        return issues


class TrailingWhitespaceRule(LintRule):
    """Check for trailing whitespace."""

    def check(self, code: str, file_path: str = "") -> list[LintIssue]:
        """Execute Check operations natively."""
        issues = []
        for i, line in enumerate(code.split("\n"), 1):
            if line != line.rstrip():
                issues.append(LintIssue(
                    rule_id="W291",
                    message="Trailing whitespace",
                    severity=LintSeverity.WARNING,
                    line_number=i,
                    file_path=file_path,
                ))
        return issues


class UnusedImportRule(LintRule):
    """Check for potentially unused imports (heuristic-based)."""

    def check(self, code: str, file_path: str = "") -> list[LintIssue]:
        """Execute Check operations natively."""
        issues = []
        lines = code.split("\n")
        import_names: list[tuple[str, int]] = []

        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith("import ") and " as " not in stripped:
                module = stripped.replace("import ", "").strip()
                # Take the last part of dotted import
                name = module.split(".")[-1]
                import_names.append((name, i))
            elif stripped.startswith("from ") and " import " in stripped:
                # Skip 'from X import Y' — harder to heuristically check
                continue

        # Check if each imported name appears elsewhere in the code
        non_import_code = "\n".join(
            line for line in lines
            if not line.strip().startswith("import ")
            and not line.strip().startswith("from ")
        )

        for name, line_no in import_names:
            if name not in non_import_code:
                issues.append(LintIssue(
                    rule_id="F401",
                    message=f"'{name}' imported but unused",
                    severity=LintSeverity.WARNING,
                    line_number=line_no,
                    file_path=file_path,
                ))

        return issues


class TodoCommentRule(LintRule):
    """Check for TODO/FIXME comments."""

    _PATTERN = re.compile(r"#\s*(TODO|FIXME|HACK|XXX)\b", re.IGNORECASE)

    def check(self, code: str, file_path: str = "") -> list[LintIssue]:
        """Execute Check operations natively."""
        issues = []
        for i, line in enumerate(code.split("\n"), 1):
            for match in self._PATTERN.finditer(line):
                issues.append(LintIssue(
                    rule_id="W0511",
                    message=f"{match.group(1)} comment found",
                    severity=LintSeverity.INFO,
                    line_number=i,
                    file_path=file_path,
                ))
        return issues


class Linter:
    """Pluggable rule-based linter.

    Comes with default rules. Additional rules can be added via add_rule().
    """

    def __init__(self):
        """Execute   Init   operations natively."""
        self.rules: list[LintRule] = [
            TrailingWhitespaceRule(),
            TodoCommentRule(),
        ]

    def add_rule(self, rule: LintRule) -> None:
        """Add a custom lint rule."""
        self.rules.append(rule)

    def lint(self, code: str, file_path: str = "") -> LintResult:
        """Lint source code.

        Args:
            code: Source code string.
            file_path: Optional file path for reporting.

        Returns:
            LintResult with all issues.
        """
        result = LintResult(file_path=file_path)
        for rule in self.rules:
            for issue in rule.check(code, file_path):
                result.add_issue(issue)
        return result

    def lint_file(self, path: str) -> LintResult:
        """Lint a file on disk.

        Args:
            path: Path to the file to lint.

        Returns:
            LintResult with all issues.
        """
        with open(path) as f:
            code = f.read()
        return self.lint(code, file_path=path)


__all__ = [
    "LintSeverity",
    "LintIssue",
    "LintResult",
    "LintRule",
    "LineLengthRule",
    "TrailingWhitespaceRule",
    "UnusedImportRule",
    "TodoCommentRule",
    "Linter",
]
