"""Error Analyzer for Autonomous Debugging.

Provides intelligent analysis of execution output to diagnose errors,
parse stack traces, and identify error types and locations. Supports
Python error patterns with extensibility for other languages.

Example:
    >>> from codomyrmex.coding.debugging.error_analyzer import ErrorAnalyzer
    >>> analyzer = ErrorAnalyzer()
    >>> diagnosis = analyzer.analyze("", "NameError: name 'x' is not defined", 1)
    >>> print(f"Error type: {diagnosis.error_type}")
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)


@dataclass
class ErrorDiagnosis:
    """Represents a diagnosed error from execution output.

    Contains structured information about an error including its type,
    message, location, and characteristics useful for automated fixing.

    Attributes:
        error_type: The type/class of error (e.g., "NameError", "SyntaxError").
        message: The error message describing what went wrong.
        file_path: Optional path to the file where the error occurred.
        line_number: Optional line number where the error occurred.
        stack_trace: The full stack trace as a string.
        is_syntax_error: True if this is a syntax/parse error.
        is_timeout: True if the error was due to execution timeout.

    Example:
        >>> diagnosis = ErrorDiagnosis(
        ...     error_type="TypeError",
        ...     message="unsupported operand type(s)",
        ...     line_number=42,
        ...     file_path="script.py"
        ... )
    """
    error_type: str
    message: str
    file_path: str | None = None
    line_number: int | None = None
    stack_trace: str = ""
    is_syntax_error: bool = False
    is_timeout: bool = False


class ErrorAnalyzer:
    """Analyzes execution output to diagnose errors.

    Parses stdout, stderr, and exit codes to identify and classify errors.
    Uses regex patterns to extract error types, messages, file locations,
    and line numbers from Python tracebacks.

    Attributes:
        python_traceback_pattern: Compiled regex for standard Python tracebacks.
        python_syntax_error_pattern: Compiled regex for Python syntax errors.

    Example:
        >>> analyzer = ErrorAnalyzer()
        >>> result = analyzer.analyze(stdout="", stderr=traceback_str, exit_code=1)
        >>> if result:
        ...     print(f"Found {result.error_type} at line {result.line_number}")
    """

    def __init__(self):
        """Initialize the ErrorAnalyzer with regex patterns for error parsing."""
        # Patterns for common Python errors
        self.python_traceback_pattern = re.compile(
            r'File "(?P<file>[^"]+)", line (?P<line>\d+), in .*?\n(?P<line_content>.*?)\n(?P<error_type>\w+): (?P<message>.*)',
            re.DOTALL
        )
        self.python_syntax_error_pattern = re.compile(
            r'File "(?P<file>[^"]+)", line (?P<line>\d+)\n(?P<line_content>.*?)\nSyntaxError: (?P<message>.*)',
            re.DOTALL
        )

    def analyze(self, stdout: str, stderr: str, exit_code: int) -> ErrorDiagnosis | None:
        """Analyze execution output to identify and diagnose the primary error.

        Parses the stdout and stderr from a code execution to extract
        structured error information. Handles Python tracebacks, syntax
        errors, and timeout conditions.

        Args:
            stdout: Standard output from the execution.
            stderr: Standard error from the execution, typically containing
                error messages and stack traces.
            exit_code: The process exit code (0 indicates success,
                124 typically indicates timeout on Linux).

        Returns:
            An ErrorDiagnosis object containing structured error information
            if an error was detected, or None if exit_code is 0 (success).

        Example:
            >>> analyzer = ErrorAnalyzer()
            >>> diagnosis = analyzer.analyze(
            ...     stdout="",
            ...     stderr='File "test.py", line 5\\n    x = \\nSyntaxError: invalid syntax',
            ...     exit_code=1
            ... )
            >>> print(diagnosis.error_type)  # "SyntaxError"
            >>> print(diagnosis.is_syntax_error)  # True
        """
        if exit_code == 0:
            return None

        # Combine output for analysis, prioritizing stderr which usually has the traceback
        full_output = f"{stdout}\n{stderr}"

        # Check for timeout (this usually comes from the runner but we might see SIGTERM/124)
        if exit_code == 124: # Standard timeout exit code on linux
             return ErrorDiagnosis(
                error_type="TimeoutError",
                message="Execution timed out",
                is_timeout=True,
                stack_trace=stderr
            )

        # Try to parse Python SyntaxError
        syntax_match = self.python_syntax_error_pattern.search(stderr)
        if syntax_match:
            return ErrorDiagnosis(
                error_type="SyntaxError",
                message=syntax_match.group("message"),
                file_path=syntax_match.group("file"),
                line_number=int(syntax_match.group("line")),
                stack_trace=stderr,
                is_syntax_error=True
            )

        # Try to parse standard Python Traceback
        # We look for the *last* match as that's usually the root cause in a traceback
        matches = list(self.python_traceback_pattern.finditer(stderr))
        if matches:
            last_match = matches[-1]
            return ErrorDiagnosis(
                error_type=last_match.group("error_type"),
                message=last_match.group("message"),
                file_path=last_match.group("file"),
                line_number=int(last_match.group("line")),
                stack_trace=stderr
            )

        # Fallback for generic errors
        lines = stderr.strip().split('\n')
        last_line = lines[-1] if lines else "Unknown Error"
        return ErrorDiagnosis(
            error_type="RuntimeError",
            message=last_line,
            stack_trace=stderr
        )
