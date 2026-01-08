from typing import Optional, List
import re

from __future__ import annotations
from dataclasses import dataclass

from codomyrmex.logging_monitoring import get_logger




"""Error analyzer for autonomous debugging."""


























































"""Core functionality module

This module provides error_analyzer functionality including:
- 2 functions: __init__, analyze
- 2 classes: ErrorDiagnosis, ErrorAnalyzer

Usage:
    # Example usage here
"""
logger = get_logger(__name__)
@dataclass
class ErrorDiagnosis:
    """Represents a diagnosed error from execution output."""
    error_type: str
    message: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    stack_trace: str = ""
    is_syntax_error: bool = False
    is_timeout: bool = False
    
class ErrorAnalyzer:
    """Analyzes execution output to diagnose errors."""
    
    def __init__(self):
        # Patterns for common Python errors
    """Brief description of __init__.

Args:
    self : Description of self

    Returns: Description of return value
"""
        self.python_traceback_pattern = re.compile(
            r'File "(?P<file>[^"]+)", line (?P<line>\d+), in .*?\n(?P<line_content>.*?)\n(?P<error_type>\w+): (?P<message>.*)',
            re.DOTALL
        )
        self.python_syntax_error_pattern = re.compile(
            r'File "(?P<file>[^"]+)", line (?P<line>\d+)\n(?P<line_content>.*?)\nSyntaxError: (?P<message>.*)',
            re.DOTALL
        )
        
    def analyze(self, stdout: str, stderr: str, exit_code: int) -> Optional[ErrorDiagnosis]:
        """
        Analyze execution output to identify the primary error.
        
        Args:
            stdout: Standard output from execution
            stderr: Standard error from execution
            exit_code: Process exit code
            
        Returns:
            ErrorDiagnosis if an error is found, None otherwise
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
