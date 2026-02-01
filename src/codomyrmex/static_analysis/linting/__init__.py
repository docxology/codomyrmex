"""
Static Analysis Linting Module

Linting and code quality checks.
"""

__version__ = "0.1.0"

import re
import ast
from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from abc import ABC, abstractmethod
from pathlib import Path


class LintSeverity(Enum):
    """Severity of lint issues."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    HINT = "hint"


class LintCategory(Enum):
    """Category of lint issues."""
    STYLE = "style"
    CONVENTION = "convention"
    ERROR = "error"
    WARNING = "warning"
    REFACTOR = "refactor"


@dataclass
class LintIssue:
    """A linting issue."""
    rule_id: str
    message: str
    severity: LintSeverity
    category: LintCategory
    file_path: str = ""
    line_number: int = 0
    column: int = 0
    code_snippet: str = ""
    suggestion: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "rule": self.rule_id,
            "message": self.message,
            "severity": self.severity.value,
            "file": self.file_path,
            "line": self.line_number,
            "column": self.column,
        }


@dataclass
class LintResult:
    """Result of linting."""
    file_path: str
    issues: List[LintIssue] = field(default_factory=list)
    error_count: int = 0
    warning_count: int = 0
    info_count: int = 0
    
    @property
    def has_errors(self) -> bool:
        """Check if there are errors."""
        return self.error_count > 0
    
    @property
    def total_issues(self) -> int:
        """Get total issue count."""
        return len(self.issues)
    
    def add_issue(self, issue: LintIssue) -> None:
        """Add an issue."""
        self.issues.append(issue)
        if issue.severity == LintSeverity.ERROR:
            self.error_count += 1
        elif issue.severity == LintSeverity.WARNING:
            self.warning_count += 1
        else:
            self.info_count += 1


class LintRule(ABC):
    """Base class for lint rules."""
    
    @property
    @abstractmethod
    def id(self) -> str:
        """Get rule ID."""
        pass
    
    @property
    @abstractmethod
    def message(self) -> str:
        """Get rule message."""
        pass
    
    @property
    def severity(self) -> LintSeverity:
        """Get severity."""
        return LintSeverity.WARNING
    
    @property
    def category(self) -> LintCategory:
        """Get category."""
        return LintCategory.STYLE
    
    @abstractmethod
    def check(self, content: str, file_path: str) -> List[LintIssue]:
        """Check content for issues."""
        pass


class LineLengthRule(LintRule):
    """Checks for lines exceeding max length."""
    
    def __init__(self, max_length: int = 120):
        self.max_length = max_length
    
    @property
    def id(self) -> str:
        return "E501"
    
    @property
    def message(self) -> str:
        return f"Line too long (exceeds {self.max_length} characters)"
    
    def check(self, content: str, file_path: str) -> List[LintIssue]:
        issues = []
        for i, line in enumerate(content.split('\n'), 1):
            if len(line) > self.max_length:
                issues.append(LintIssue(
                    rule_id=self.id,
                    message=f"{self.message}: {len(line)} chars",
                    severity=self.severity,
                    category=self.category,
                    file_path=file_path,
                    line_number=i,
                    code_snippet=line[:80] + "...",
                ))
        return issues


class TrailingWhitespaceRule(LintRule):
    """Checks for trailing whitespace."""
    
    @property
    def id(self) -> str:
        return "W291"
    
    @property
    def message(self) -> str:
        return "Trailing whitespace"
    
    def check(self, content: str, file_path: str) -> List[LintIssue]:
        issues = []
        for i, line in enumerate(content.split('\n'), 1):
            if line.rstrip() != line:
                issues.append(LintIssue(
                    rule_id=self.id,
                    message=self.message,
                    severity=self.severity,
                    category=self.category,
                    file_path=file_path,
                    line_number=i,
                    suggestion="Remove trailing whitespace",
                ))
        return issues


class UnusedImportRule(LintRule):
    """Checks for unused imports (simple check)."""
    
    @property
    def id(self) -> str:
        return "F401"
    
    @property
    def message(self) -> str:
        return "Imported but unused"
    
    @property
    def severity(self) -> LintSeverity:
        return LintSeverity.WARNING
    
    def check(self, content: str, file_path: str) -> List[LintIssue]:
        issues = []
        
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return issues
        
        # Collect imports
        imports = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    name = alias.asname or alias.name
                    imports[name] = node.lineno
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    name = alias.asname or alias.name
                    imports[name] = node.lineno
        
        # Check if used (simple text search)
        for name, lineno in imports.items():
            # Count occurrences (excluding import lines)
            pattern = r'\b' + re.escape(name) + r'\b'
            matches = list(re.finditer(pattern, content))
            
            # If only appears once (the import), it's unused
            if len(matches) <= 1:
                issues.append(LintIssue(
                    rule_id=self.id,
                    message=f"'{name}' {self.message}",
                    severity=self.severity,
                    category=LintCategory.WARNING,
                    file_path=file_path,
                    line_number=lineno,
                ))
        
        return issues


class TodoCommentRule(LintRule):
    """Checks for TODO/FIXME comments."""
    
    @property
    def id(self) -> str:
        return "W999"
    
    @property
    def message(self) -> str:
        return "TODO/FIXME comment found"
    
    @property
    def severity(self) -> LintSeverity:
        return LintSeverity.INFO
    
    def check(self, content: str, file_path: str) -> List[LintIssue]:
        issues = []
        pattern = re.compile(r'#\s*(TODO|FIXME|XXX|HACK):', re.IGNORECASE)
        
        for i, line in enumerate(content.split('\n'), 1):
            match = pattern.search(line)
            if match:
                issues.append(LintIssue(
                    rule_id=self.id,
                    message=f"{match.group(1).upper()} comment",
                    severity=self.severity,
                    category=LintCategory.WARNING,
                    file_path=file_path,
                    line_number=i,
                    code_snippet=line.strip(),
                ))
        
        return issues


class Linter:
    """
    Code linter.
    
    Usage:
        linter = Linter()
        
        # Lint a file
        result = linter.lint_file("module.py")
        for issue in result.issues:
            print(f"{issue.line_number}: {issue.message}")
        
        # Lint content
        result = linter.lint("code = 'hello'  ")
    """
    
    def __init__(self):
        self._rules: List[LintRule] = []
        self._register_default_rules()
    
    def _register_default_rules(self) -> None:
        """Register default rules."""
        self._rules.extend([
            LineLengthRule(),
            TrailingWhitespaceRule(),
            UnusedImportRule(),
            TodoCommentRule(),
        ])
    
    def add_rule(self, rule: LintRule) -> "Linter":
        """Add a lint rule."""
        self._rules.append(rule)
        return self
    
    def lint(self, content: str, file_path: str = "<string>") -> LintResult:
        """Lint content."""
        result = LintResult(file_path=file_path)
        
        for rule in self._rules:
            issues = rule.check(content, file_path)
            for issue in issues:
                result.add_issue(issue)
        
        return result
    
    def lint_file(self, file_path: str) -> LintResult:
        """Lint a file."""
        path = Path(file_path)
        if not path.exists():
            result = LintResult(file_path=file_path)
            result.add_issue(LintIssue(
                rule_id="E000",
                message=f"File not found: {file_path}",
                severity=LintSeverity.ERROR,
                category=LintCategory.ERROR,
                file_path=file_path,
            ))
            return result
        
        content = path.read_text(encoding='utf-8', errors='ignore')
        return self.lint(content, file_path)


__all__ = [
    # Enums
    "LintSeverity",
    "LintCategory",
    # Data classes
    "LintIssue",
    "LintResult",
    # Rules
    "LintRule",
    "LineLengthRule",
    "TrailingWhitespaceRule",
    "UnusedImportRule",
    "TodoCommentRule",
    # Core
    "Linter",
]
