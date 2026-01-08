from pathlib import Path
from typing import Any, Dict, Optional, Union, List
import argparse
import json
import sys
import time

from contextlib import contextmanager

from codomyrmex.logging_monitoring.logger_config import get_logger, LogContext






"""
Shared utilities for Codomyrmex orchestrator scripts.

This module provides common functions and patterns used across all
orchestrator scripts to ensure consistency and reduce code duplication.
"""


# Import logging setup

logger = get_logger(__name__)

# Standard output width for formatting
OUTPUT_WIDTH = 80


class ProgressReporter:
    """Progress reporting utility for long-running operations."""

    def __init__(self, total: int = 100, prefix: str = "Progress", suffix: str = "Complete"):
        """
        Initialize progress reporter.

        Args:
            total: Total number of steps
            prefix: Progress bar prefix
            suffix: Progress bar suffix
        """
        self.total = total
        self.prefix = prefix
        self.suffix = suffix
        self.current = 0
        self.start_time = time.time()
        self.last_update = 0

    def update(self, increment: int = 1, message: Optional[str] = None) -> None:
        """
        Update progress.

        Args:
            increment: Number of steps to advance
            message: Optional status message
        """
        self.current += increment
        self.current = min(self.current, self.total)  # Cap at total

        # Throttle updates to avoid spam
        current_time = time.time()
        if current_time - self.last_update < 0.1:  # Update at most every 100ms
            return

        self.last_update = current_time
        self._display_progress(message)

    def set_current(self, current: int, message: Optional[str] = None) -> None:
        """
        Set current progress value.

        Args:
            current: Current progress value
            message: Optional status message
        """
        self.current = current
        self._display_progress(message)

    def complete(self, message: str = "Completed") -> None:
        """Mark progress as complete."""
        self.current = self.total
        self._display_progress(message)
        print()  # New line after progress bar

    def _display_progress(self, message: Optional[str] = None) -> None:
        """Display current progress."""
        percentage = int(100 * self.current / self.total)
        filled_length = int(OUTPUT_WIDTH * self.current // self.total)
        bar = "█" * filled_length + "-" * (OUTPUT_WIDTH - filled_length)

        elapsed = time.time() - self.start_time
        if self.current > 0:
            eta = elapsed * (self.total - self.current) / self.current
            eta_str = f" ETA: {eta:.1f}s"
        else:
            eta_str = ""

        status = f"\r{self.prefix}: [{bar}] {percentage}%{eta_str}"
        if message:
            status += f" - {message}"

        print(status, end="", flush=True)


def format_table(data: List[Dict[str, Any]], headers: List[str]) -> str:
    """
    Format data as a table.

    Args:
        data: List of dictionaries containing row data
        headers: List of column headers

    Returns:
        Formatted table string
    """
    if not data:
        return "No data to display"

    # Calculate column widths
    col_widths = {}
    for header in headers:
        col_widths[header] = len(header)

    for row in data:
        for header in headers:
            value = str(row.get(header, ""))
            col_widths[header] = max(col_widths[header], len(value))

    # Create table
    lines = []

    # Header
    header_line = " | ".join(h.ljust(col_widths[h]) for h in headers)
    lines.append(header_line)
    lines.append("-" * len(header_line))

    # Data rows
    for row in data:
        row_line = " | ".join(str(row.get(h, "")).ljust(col_widths[h]) for h in headers)
        lines.append(row_line)

    return "\n".join(lines)


def print_progress_bar(current: int, total: int, prefix: str = "Progress") -> None:
    """
    Print a simple progress bar.

    Args:
        current: Current progress value
        total: Total progress value
        prefix: Progress bar prefix
    """
    percentage = int(100 * current / total) if total > 0 else 100
    bar_length = 30
    filled_length = int(bar_length * current // total)
    bar = "█" * filled_length + "-" * (bar_length - filled_length)

    print(f"\r{prefix}: [{bar}] {percentage}%", end="", flush=True)
    if current >= total:
        print()  # New line when complete


def validate_dry_run(args: argparse.Namespace) -> bool:
    """
    Validate and confirm dry-run mode.

    Args:
        args: Parsed command line arguments

    Returns:
        True if dry-run should proceed
    """
    if not getattr(args, 'dry_run', False):
        return True

    print_section("DRY RUN MODE", separator="=")
    print("This will show what would be executed without actually running commands.")
    print("No files will be modified, no external services will be contacted.")
    print()

    return True


@contextmanager
def enhanced_error_context(operation: str, context: Optional[Dict[str, Any]] = None):
    """
    Context manager for enhanced error reporting.

    Args:
        operation: Name of the operation being performed
        context: Additional context information
    """
    correlation_id = f"op_{int(time.time() * 1000)}"

    error_context = {
        "operation": operation,
        "correlation_id": correlation_id,
        "timestamp": time.time()
    }

    if context:
        error_context.update(context)

    try:
        with LogContext(**error_context):
            yield
    except Exception as e:
        # Enhance error with context
        enhanced_error = type(e)(
            f"{str(e)} (Operation: {operation}, Correlation ID: {correlation_id})"
        )
        enhanced_error.__cause__ = e
        raise enhanced_error from e


def create_dry_run_plan(args: argparse.Namespace, operations: List[Dict[str, Any]]) -> str:
    """
    Create a dry-run execution plan.

    Args:
        args: Command line arguments
        operations: List of operations that would be performed

    Returns:
        Formatted execution plan
    """
    lines = ["EXECUTION PLAN (DRY RUN)", "=" * 40, ""]

    for i, op in enumerate(operations, 1):
        lines.append(f"{i}. {op.get('description', 'Unknown operation')}")
        if 'details' in op:
            lines.append(f"   Details: {op['details']}")
        if 'target' in op:
            lines.append(f"   Target: {op['target']}")
        lines.append("")

    lines.append("No actual changes will be made.")
    return "\n".join(lines)


def add_common_arguments(parser: argparse.ArgumentParser) -> None:
    """
    Add common arguments to argument parser.

    Args:
        parser: Argument parser to extend
    """
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be executed without actually running commands'
    )

    parser.add_argument(
        '--format',
        choices=['json', 'text'],
        default='text',
        help='Output format (default: text)'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )

    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Suppress non-error output'
    )


def print_with_color(message: str, color: str = "default", **kwargs) -> None:
    """
    Print message with color (if supported).

    Args:
        message: Message to print
        color: Color name (red, green, yellow, blue, default)
        **kwargs: Additional print arguments
    """
    color_codes = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "default": "\033[0m"
    }

    # Check if we're in a TTY and colors are supported
    if hasattr(sys.stdout, 'isatty') and sys.stdout.isatty():
        color_code = color_codes.get(color, color_codes["default"])
        reset_code = color_codes["default"]
        print(f"{color_code}{message}{reset_code}", **kwargs)
    else:
        print(message, **kwargs)


def format_output(
    data: Any,
    format_type: str = "json",
    indent: int = 2,
) -> str:
    """Format output data consistently.

    Args:
        data: Data to format (dict, list, or other)
        format_type: Output format ('json' or 'text')
        indent: Indentation for JSON output

    Returns:
        Formatted string representation
    """
    if format_type == "json":
        if isinstance(data, (dict, list)):
            return json.dumps(data, indent=indent)
        else:
            return json.dumps({"result": str(data)}, indent=indent)
    else:
        return str(data)


def validate_file_path(
    path: Union[str, Path],
    must_exist: bool = True,
    must_be_file: bool = False,
    must_be_dir: bool = False,
) -> Path:
    """Validate and normalize a file path.

    Args:
        path: Path to validate
        must_exist: Whether the path must exist
        must_be_file: Whether the path must be a file
        must_be_dir: Whether the path must be a directory

    Returns:
        Normalized Path object

    Raises:
        FileNotFoundError: If path doesn't exist when must_exist=True
        ValueError: If path type doesn't match requirements
    """
    path_obj = Path(path).resolve()

    if must_exist and not path_obj.exists():
        raise FileNotFoundError(f"Path not found: {path}")

    if must_be_file and not path_obj.is_file():
        raise ValueError(f"Path is not a file: {path}")

    if must_be_dir and not path_obj.is_dir():
        raise ValueError(f"Path is not a directory: {path}")

    return path_obj


def load_json_file(path: Union[str, Path]) -> Dict[str, Any]:
    """Load JSON file with consistent error handling.

    Args:
        path: Path to JSON file

    Returns:
        Parsed JSON data as dictionary

    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If file contains invalid JSON
    """
    file_path = validate_file_path(path, must_exist=True, must_be_file=True)

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in file {path}: {e}")
        raise
    except Exception as e:
        logger.error(f"Failed to read file {path}: {e}")
        raise


def save_json_file(
    data: Any,
    path: Union[str, Path],
    indent: int = 2,
    create_parents: bool = True,
) -> Path:
    """Save data to JSON file with consistent error handling.

    Args:
        data: Data to save (will be JSON-serialized)
        path: Output file path
        indent: JSON indentation
        create_parents: Whether to create parent directories

    Returns:
        Path to saved file

    Raises:
        OSError: If file cannot be written
    """
    output_path = Path(path).resolve()

    if create_parents:
        output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
        return output_path
    except Exception as e:
        logger.error(f"Failed to write file {path}: {e}")
        raise


def print_section(
    title: str,
    separator: str = "-",
    width: int = OUTPUT_WIDTH,
    prefix: str = "",
) -> None:
    """Print a formatted section header.

    Args:
        title: Section title
        separator: Separator character
        width: Width of separator line
        prefix: Optional prefix for title
    """
    if prefix:
        print(f"{prefix} {title}")
    else:
        print(title)
    print(separator * width)


def print_success(message: str, context: Optional[str] = None) -> None:
    """Print a success message consistently.

    Args:
        message: Success message
        context: Optional context information
    """
    if context:
        print(f"✅ {message} ({context})")
    else:
        print(f"✅ {message}")


def print_error(
    message: str,
    context: Optional[str] = None,
    exception: Optional[Exception] = None,
) -> None:
    """Print an error message consistently.

    Args:
        message: Error message
        context: Optional context information
        exception: Optional exception for additional details
    """
    error_msg = f"❌ {message}"
    if context:
        error_msg += f" (Context: {context})"
    if exception:
        error_msg += f" - {str(exception)}"
    print(error_msg)


def print_warning(message: str, context: Optional[str] = None) -> None:
    """Print a warning message consistently.

    Args:
        message: Warning message
        context: Optional context information
    """
    if context:
        print(f"⚠️  {message} ({context})")
    else:
        print(f"⚠️  {message}")


def print_info(message: str) -> None:
    """Print an info message consistently.

    Args:
        message: Info message
    """
    print(f"ℹ️  {message}")


def handle_common_exceptions(
    operation_name: str,
    context: Optional[str] = None,
    verbose: bool = False,
):
    """Decorator for handling common exceptions consistently.

    Args:
        operation_name: Name of the operation for error messages
        context: Optional context information
        verbose: Whether to log detailed exception information

    Returns:
        Decorator function
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except FileNotFoundError as e:
                logger.error(f"{operation_name}: File not found - {e}")
                print_error(f"{operation_name} failed: File not found", context)
                if verbose:
                    logger.exception("Detailed error information:")
                return False
            except PermissionError as e:
                logger.error(f"{operation_name}: Permission denied - {e}")
                print_error(f"{operation_name} failed: Permission denied", context)
                if verbose:
                    logger.exception("Detailed error information:")
                return False
            except json.JSONDecodeError as e:
                logger.error(f"{operation_name}: Invalid JSON - {e}")
                print_error(f"{operation_name} failed: Invalid JSON", context)
                if verbose:
                    logger.exception("Detailed error information:")
                return False
            except Exception as e:
                logger.exception(f"{operation_name}: Unexpected error")
                print_error(f"{operation_name} failed: Unexpected error", context, e)
                if verbose:
                    logger.exception("Detailed error information:")
                return False
        return wrapper
    return decorator


def format_result(
    result: Any,
    success_key: str = "success",
    output_key: Optional[str] = None,
) -> tuple[bool, Optional[str]]:
    """Extract success status and optional message from result.

    Args:
        result: Result dictionary or boolean
        success_key: Key to check for success status in dict
        output_key: Optional key for output message

    Returns:
        Tuple of (success: bool, message: Optional[str])
    """
    if isinstance(result, dict):
        success = result.get(success_key, False)
        message = result.get(output_key) if output_key else None
        return (bool(success), message)
    elif isinstance(result, bool):
        return (result, None)
    else:
        return (bool(result), str(result) if result else None)


def determine_language_from_file(file_path: Union[str, Path]) -> str:
    """Determine programming language from file extension.

    Args:
        file_path: Path to source file

    Returns:
        Language name (e.g., 'python', 'javascript')
    """
    path_obj = Path(file_path)
    ext = path_obj.suffix.lstrip(".")

    language_map = {
        "py": "python",
        "js": "javascript",
        "ts": "typescript",
        "go": "go",
        "rs": "rust",
        "java": "java",
        "cpp": "cpp",
        "c": "c",
        "rb": "ruby",
        "php": "php",
        "swift": "swift",
        "kt": "kotlin",
        "scala": "scala",
    }

    return language_map.get(ext, "python")  # Default to python


def ensure_output_directory(output_path: Union[str, Path]) -> Path:
    """Ensure output directory exists, creating if necessary.

    Args:
        output_path: Path to output file or directory

    Returns:
        Resolved Path object
    """
    path_obj = Path(output_path).resolve()
    path_obj.parent.mkdir(parents=True, exist_ok=True)
    return path_obj


def parse_common_args(args: Any) -> Dict[str, Any]:
    """Extract common arguments from argparse namespace.

    Args:
        args: argparse.Namespace object

    Returns:
        Dictionary of common arguments
    """
    common = {}
    if hasattr(args, "verbose"):
        common["verbose"] = args.verbose
    if hasattr(args, "output"):
        common["output"] = args.output
    if hasattr(args, "dry_run"):
        common["dry_run"] = args.dry_run
    return common
