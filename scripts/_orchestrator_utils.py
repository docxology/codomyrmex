"""
Shared utilities for Codomyrmex orchestrator scripts.

This module provides common functions and patterns used across all
orchestrator scripts to ensure consistency and reduce code duplication.
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Union

# Import logging setup
from codomyrmex.logging_monitoring.logger_config import get_logger

logger = get_logger(__name__)

# Standard output width for formatting
OUTPUT_WIDTH = 40


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


