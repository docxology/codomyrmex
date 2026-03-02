"""Static Analysis Exception Classes.

This module defines exceptions specific to static analysis operations.
All exceptions inherit from CodomyrmexError for consistent error handling.
"""

from codomyrmex.exceptions import StaticAnalysisError


class ParserError(StaticAnalysisError):
    """Raised when code parsing fails.

    Attributes:
        message: Error description.
        file_path: Path to the file that failed to parse.
        line: Line number where parsing failed.
        column: Column number where parsing failed.
    """

    def __init__(
        self,
        message: str,
        file_path: str | None = None,
        line: int | None = None,
        column: int | None = None,
        **kwargs
    ):
        """Initialize this instance."""
        super().__init__(message, **kwargs)
        if file_path:
            self.context["file_path"] = file_path
        if line is not None:
            self.context["line"] = line
        if column is not None:
            self.context["column"] = column


class LintError(StaticAnalysisError):
    """Raised when linting operations fail."""

    def __init__(
        self,
        message: str,
        linter: str | None = None,
        rule: str | None = None,
        **kwargs
    ):
        """Initialize this instance."""
        super().__init__(message, **kwargs)
        if linter:
            self.context["linter"] = linter
        if rule:
            self.context["rule"] = rule


class TypeCheckError(StaticAnalysisError):
    """Raised when type checking operations fail."""

    def __init__(
        self,
        message: str,
        expected_type: str | None = None,
        actual_type: str | None = None,
        **kwargs
    ):
        """Initialize this instance."""
        super().__init__(message, **kwargs)
        if expected_type:
            self.context["expected_type"] = expected_type
        if actual_type:
            self.context["actual_type"] = actual_type


class ComplexityError(StaticAnalysisError):
    """Raised when code complexity exceeds thresholds."""

    def __init__(
        self,
        message: str,
        metric: str | None = None,
        value: float | None = None,
        threshold: float | None = None,
        **kwargs
    ):
        """Initialize this instance."""
        super().__init__(message, **kwargs)
        if metric:
            self.context["metric"] = metric
        if value is not None:
            self.context["value"] = value
        if threshold is not None:
            self.context["threshold"] = threshold


class DependencyAnalysisError(StaticAnalysisError):
    """Raised when dependency analysis fails."""

    def __init__(
        self,
        message: str,
        dependency: str | None = None,
        version: str | None = None,
        **kwargs
    ):
        """Initialize this instance."""
        super().__init__(message, **kwargs)
        if dependency:
            self.context["dependency"] = dependency
        if version:
            self.context["version"] = version


class SecurityVulnerabilityError(StaticAnalysisError):
    """Raised when security vulnerabilities are detected."""

    def __init__(
        self,
        message: str,
        vulnerability_type: str | None = None,
        severity: str | None = None,
        cwe_id: str | None = None,
        **kwargs
    ):
        """Initialize this instance."""
        super().__init__(message, **kwargs)
        if vulnerability_type:
            self.context["vulnerability_type"] = vulnerability_type
        if severity:
            self.context["severity"] = severity
        if cwe_id:
            self.context["cwe_id"] = cwe_id


class ASTError(StaticAnalysisError):
    """Raised when AST operations fail."""
    pass


class MetricsError(StaticAnalysisError):
    """Raised when code metrics computation fails."""
    pass
