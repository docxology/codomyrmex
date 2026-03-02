"""
Security and File Preparation

Handles security validation and file preparation for code execution.
"""

import os
import shutil
import tempfile

from codomyrmex.coding.execution.language_support import SUPPORTED_LANGUAGES
from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)


def prepare_code_file(code: str, language: str) -> tuple[str, str]:
    """
    Prepare a temporary file containing the code to execute.

    Args:
        code: The source code to write to the file
        language: The programming language for file extension

    Returns:
        Tuple of (temp directory path, code file path relative to temp directory)
    """
    # Create a temporary directory for this execution
    temp_dir = tempfile.mkdtemp(prefix="codomyrmex_sandbox_")

    # Get file extension for the language
    extension = SUPPORTED_LANGUAGES[language]["extension"]

    # Create a file for the code
    rel_file_path = f"code.{extension}"
    abs_file_path = os.path.join(temp_dir, rel_file_path)

    # Write the code to the file
    with open(abs_file_path, "w") as f:
        f.write(code)

    return temp_dir, rel_file_path


def prepare_stdin_file(stdin: str | None, temp_dir: str) -> str | None:
    """
    Prepare a file with stdin content if provided.

    Args:
        stdin: Standard input content or None
        temp_dir: Directory to write the stdin file to

    Returns:
        Path to stdin file or None if no stdin provided
    """
    if stdin is None or stdin == "":
        return None

    stdin_path = os.path.join(temp_dir, "stdin.txt")

    with open(stdin_path, "w") as f:
        f.write(stdin)

    return stdin_path


def cleanup_temp_files(temp_dir: str) -> None:
    """Safely clean up temporary directory and files."""
    try:
        shutil.rmtree(temp_dir)
    except OSError as e:
        logger.warning(f"Failed to clean up temporary directory {temp_dir}: {str(e)}")

