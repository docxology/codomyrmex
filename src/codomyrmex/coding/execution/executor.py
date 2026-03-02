"""Code Execution Engine.

Main execution logic for running code in sandboxed Docker environments.
Provides secure code execution with timeout controls, session management,
and multi-language support.

Example:
    >>> from codomyrmex.coding.execution import execute_code
    >>> result = execute_code("python", "print('Hello, World!')")
    >>> print(result["stdout"])  # "Hello, World!"
"""

import os
from typing import Any

from codomyrmex.coding.sandbox.container import (
    check_docker_available,
    run_code_in_docker,
)
from codomyrmex.coding.sandbox.security import (
    cleanup_temp_files,
    prepare_code_file,
    prepare_stdin_file,
)
from codomyrmex.logging_monitoring.core.logger_config import get_logger
from codomyrmex.model_context_protocol.decorators import mcp_tool

from .language_support import SUPPORTED_LANGUAGES, validate_language
from .session_manager import validate_session_id

logger = get_logger(__name__)

# Constants and configuration
DEFAULT_TIMEOUT = 30
MAX_TIMEOUT = 300
MIN_TIMEOUT = 1


def validate_timeout(timeout: int | None) -> int:
    """Validate and normalize a timeout value to be within allowed bounds.

    Ensures the timeout is within the MIN_TIMEOUT and MAX_TIMEOUT range.
    Returns the default timeout if None is provided.

    Args:
        timeout: The requested timeout in seconds, or None for default.

    Returns:
        A valid timeout value clamped to [MIN_TIMEOUT, MAX_TIMEOUT],
        or DEFAULT_TIMEOUT if timeout was None.

    Example:
        >>> validate_timeout(None)  # Returns DEFAULT_TIMEOUT (30)
        30
        >>> validate_timeout(500)   # Clamped to MAX_TIMEOUT (300)
        300
        >>> validate_timeout(0)     # Clamped to MIN_TIMEOUT (1)
        1
    """
    if timeout is None:
        return DEFAULT_TIMEOUT

    # Ensure timeout is within allowed range
    timeout = max(MIN_TIMEOUT, min(MAX_TIMEOUT, timeout))
    return timeout


@mcp_tool()
def execute_code(
    language: str,
    code: str,
    stdin: str | None = None,
    timeout: int | None = None,
    session_id: str | None = None,
) -> dict[str, Any]:
    """Execute a code snippet in a sandboxed Docker environment.

    Runs the provided source code in an isolated Docker container with
    resource limits and timeout controls. Supports multiple programming
    languages and optional session persistence.

    Args:
        language: Programming language of the code. Must be one of the
            supported languages (python, javascript, java, cpp, c, go,
            rust, bash).
        code: Source code to execute as a string.
        stdin: Optional standard input to provide to the program.
        timeout: Maximum execution time in seconds. Defaults to 30,
            with a maximum of 300 seconds.
        session_id: Optional session identifier for persistent environments.
            Allows maintaining state between executions.

    Returns:
        A dictionary containing execution results with keys:
        - stdout (str): Standard output from the program
        - stderr (str): Standard error output
        - exit_code (int): Process exit code (0 for success)
        - execution_time (float): Actual execution time in seconds
        - status (str): Execution status ("success", "timeout", "error", "setup_error")
        - error_message (str): Detailed error message if status is not "success"

    Raises:
        No exceptions are raised; errors are returned in the result dictionary.

    Example:
        >>> result = execute_code("python", "print(sum(range(10)))")
        >>> print(result["stdout"])  # "45"
        >>> print(result["exit_code"])  # 0
        >>>
        >>> result = execute_code("python", "x = input(); print(f'Got: {x}')", stdin="hello")
        >>> print(result["stdout"])  # "Got: hello"
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

