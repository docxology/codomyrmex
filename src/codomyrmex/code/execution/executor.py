"""
Code Execution Engine

Main execution logic for running code in sandboxed environments.
"""

import os
import tempfile
from typing import Any, Optional

from codomyrmex.logging_monitoring.logger_config import get_logger

from ..sandbox.container import run_code_in_docker, check_docker_available
from ..sandbox.security import prepare_code_file, prepare_stdin_file, cleanup_temp_files
from .language_support import SUPPORTED_LANGUAGES, validate_language
from .session_manager import validate_session_id

logger = get_logger(__name__)

# Constants and configuration
DEFAULT_TIMEOUT = 30
MAX_TIMEOUT = 300
MIN_TIMEOUT = 1


def validate_timeout(timeout: Optional[int]) -> int:
    """Validate and normalize timeout value."""
    if timeout is None:
        return DEFAULT_TIMEOUT

    # Ensure timeout is within allowed range
    timeout = max(MIN_TIMEOUT, min(MAX_TIMEOUT, timeout))
    return timeout


def execute_code(
    language: str,
    code: str,
    stdin: Optional[str] = None,
    timeout: Optional[int] = None,
    session_id: Optional[str] = None,
) -> dict[str, Any]:
    """
    Execute a code snippet in a sandboxed environment.

    Args:
        language: Programming language of the code
        code: Source code to execute
        stdin: Standard input to provide to the program
        timeout: Maximum execution time in seconds (default: 30)
        session_id: Optional session identifier for persistent environments

    Returns:
        Dictionary with execution results: stdout, stderr, exit_code, execution_time, status
    """
    logger.info(f"Executing {language} code (session_id: {session_id or 'none'})")

    # Validate inputs
    if not validate_language(language):
        return {
            "stdout": "",
            "stderr": f"Unsupported language: {language}",
            "exit_code": -1,
            "execution_time": 0,
            "status": "setup_error",
            "error_message": f"Language '{language}' is not supported. Supported languages: {', '.join(SUPPORTED_LANGUAGES.keys())}",
        }

    if not code or not isinstance(code, str):
        return {
            "stdout": "",
            "stderr": "No code provided or invalid code format",
            "exit_code": -1,
            "execution_time": 0,
            "status": "setup_error",
            "error_message": "Code must be a non-empty string",
        }

    timeout = validate_timeout(timeout)
    session_id = validate_session_id(session_id)

    # Check if Docker is available
    if not check_docker_available():
        return {
            "stdout": "",
            "stderr": "Docker is not available",
            "exit_code": -1,
            "execution_time": 0,
            "status": "setup_error",
            "error_message": "Docker is required but not available or not running",
        }

    # Prepare files for execution
    temp_dir = None
    try:
        # Create code file
        temp_dir, code_file_path = prepare_code_file(code, language)

        # Create stdin file if needed
        stdin_file = prepare_stdin_file(stdin, temp_dir) if stdin else None

        # Execute the code
        result = run_code_in_docker(
            language=language,
            code_file_path=code_file_path,
            temp_dir=temp_dir,
            stdin_file=stdin_file,
            timeout=timeout,
            session_id=session_id,
        )

        return result

    except Exception as e:
        logger.error(f"Unexpected error executing code: {str(e)}", exc_info=True)
        return {
            "stdout": "",
            "stderr": f"Internal error: {str(e)}",
            "exit_code": -1,
            "execution_time": 0,
            "status": "setup_error",
            "error_message": f"Sandbox execution failed: {str(e)}",
        }

    finally:
        # Clean up temporary files
        if temp_dir and os.path.exists(temp_dir):
            cleanup_temp_files(temp_dir)

