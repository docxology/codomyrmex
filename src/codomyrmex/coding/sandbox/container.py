"""
Docker Container Management

Handles Docker container creation, execution, and cleanup for sandboxed code execution.
"""

import os
import subprocess
import tempfile
import time
from typing import Any

from codomyrmex.logging_monitoring.core.logger_config import get_logger

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
    except (subprocess.SubprocessError, FileNotFoundError) as e:
        logger.warning("Docker availability check failed: %s", e)
        return False


def run_code_in_docker(
    language: str,
    code_file_path: str,
    temp_dir: str,
    stdin_file: str | None = None,
    timeout: int = 30,
    session_id: str | None = None,
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

    # Validate temp_dir is within system temp to prevent path traversal (C4)
    real_temp = os.path.realpath(temp_dir)
    _tmp_base = os.path.realpath(tempfile.gettempdir())
    if not (real_temp == _tmp_base or real_temp.startswith(_tmp_base + os.sep)):
        raise ValueError(
            f"temp_dir must be within system temp directory: {temp_dir!r}"
        )

    # Add volume mapping for code and working directory
    docker_args.append(f"-v={real_temp}:/sandbox")
    docker_args.append("-w=/sandbox")  # Set working directory

    # Prepare the command to run inside the container
    container_cmd = [
        cmd.format(filename=code_file_path) for cmd in language_config["command"]
    ]

    # Validate stdin_file is inside temp_dir (no path traversal, no shell injection) (C3)
    if stdin_file:
        real_stdin = os.path.realpath(stdin_file)
        if not real_stdin.startswith(real_temp + os.sep):
            raise ValueError(
                f"stdin_file must be inside temp_dir: {stdin_file!r}"
            )

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
        # Open stdin file outside shell (no shell injection possible) (C3)
        _stdin_fh = open(os.path.realpath(stdin_file)) if stdin_file else None  # noqa: WPS515
        try:
            process = subprocess.Popen(
                docker_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=_stdin_fh,
                universal_newlines=True,
                bufsize=1,
            )
        finally:
            # Popen dups the fd; safe to close our handle immediately
            if _stdin_fh is not None:
                _stdin_fh.close()

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
            except subprocess.SubprocessError as e:
                logger.warning("Container cleanup error — orphaned container may remain: %s", e)

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

