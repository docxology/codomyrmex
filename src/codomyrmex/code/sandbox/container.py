"""
Docker Container Management

Handles Docker container creation, execution, and cleanup for sandboxed code execution.
"""

import os
import subprocess
import time
from typing import Any, Optional

from codomyrmex.logging_monitoring.logger_config import get_logger

from ..execution.language_support import SUPPORTED_LANGUAGES
from .resource_limits import DEFAULT_DOCKER_ARGS

logger = get_logger(__name__)


def check_docker_available() -> bool:
    """Check if Docker is available on the system."""
    try:
        result = subprocess.run(
            ["docker", "--version"],
            capture_output=True,
            timeout=5,
        )
        return result.returncode == 0
    except (subprocess.SubprocessError, FileNotFoundError):
        return False


def run_code_in_docker(
    language: str,
    code_file_path: str,
    temp_dir: str,
    stdin_file: Optional[str] = None,
    timeout: int = 30,
    session_id: Optional[str] = None,
) -> dict[str, Any]:
    """
    Execute code in a Docker container with security constraints.

    Args:
        language: Programming language of the code
        code_file_path: Path to the code file relative to temp_dir
        temp_dir: Directory containing code and input files
        stdin_file: Path to stdin file or None
        timeout: Maximum execution time in seconds
        session_id: Optional session identifier for persistent environments

    Returns:
        Dictionary with execution results
    """
    start_time = time.time()
    language_config = SUPPORTED_LANGUAGES[language]

    # Prepare Docker command
    docker_args = DEFAULT_DOCKER_ARGS.copy()

    # Add volume mapping for code and working directory
    docker_args.append(f"-v={temp_dir}:/sandbox")
    docker_args.append("-w=/sandbox")  # Set working directory

    # Prepare the command to run inside the container
    container_cmd = [
        cmd.format(filename=code_file_path) for cmd in language_config["command"]
    ]

    # Handle stdin if provided
    stdin_redirect = f" < {os.path.basename(stdin_file)}" if stdin_file else ""

    # Final command to run
    if stdin_redirect:
        # For stdin redirection, we need to use shell
        container_cmd = ["sh", "-c", f"{' '.join(container_cmd)}{stdin_redirect}"]

    # Calculate the docker command timeout (slightly longer than the code timeout)
    docker_timeout = timeout * language_config.get("timeout_factor", 1.2)

    # Construct the full Docker command
    docker_cmd = (
        ["docker", "run", "--rm"]
        + docker_args
        + [language_config["image"]]
        + container_cmd
    )

    logger.info(f"Executing code in Docker: {' '.join(docker_cmd)}")

    try:
        # Run the Docker command
        process = subprocess.Popen(
            docker_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            bufsize=1,
        )

        try:
            stdout, stderr = process.communicate(timeout=docker_timeout)
            exit_code = process.returncode
            status = "success"
            error_message = None

        except subprocess.TimeoutExpired:
            # Kill the container if it times out
            process.kill()
            stdout, stderr = process.communicate()
            exit_code = -1
            status = "timeout"
            error_message = f"Execution timed out after {timeout} seconds."

            # Try to find and kill the running container
            try:
                container_id_cmd = [
                    "docker",
                    "ps",
                    "-q",
                    "--filter",
                    f"ancestor={language_config['image']}",
                ]
                container_ids = (
                    subprocess.check_output(container_id_cmd, universal_newlines=True)
                    .strip()
                    .split("\n")
                )
                for container_id in container_ids:
                    if container_id:
                        subprocess.run(
                            ["docker", "kill", container_id],
                            capture_output=True,
                        )
            except subprocess.SubprocessError:
                pass  # Ignore errors in cleanup

    except subprocess.SubprocessError as e:
        stdout = ""
        stderr = f"Failed to run Docker container: {str(e)}"
        exit_code = -1
        status = "setup_error"
        error_message = f"Container setup failed: {str(e)}"

    execution_time = time.time() - start_time

    # Cap very long output to prevent memory issues
    MAX_OUTPUT_CHARS = 100000  # 100KB
    if len(stdout) > MAX_OUTPUT_CHARS:
        stdout = (
            stdout[:MAX_OUTPUT_CHARS] + "\n... [Output truncated due to size limits]"
        )
    if len(stderr) > MAX_OUTPUT_CHARS:
        stderr = (
            stderr[:MAX_OUTPUT_CHARS]
            + "\n... [Error output truncated due to size limits]"
        )

    return {
        "stdout": stdout,
        "stderr": stderr,
        "exit_code": exit_code,
        "execution_time": round(execution_time, 3),
        "status": status,
        "error_message": error_message,
    }

