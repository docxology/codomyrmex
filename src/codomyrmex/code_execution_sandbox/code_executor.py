"""
Code Execution Sandbox - Core implementation

This module provides a secure sandbox environment for executing untrusted code in various
programming languages. It uses Docker containers to isolate code execution and enforces
strict resource limits to prevent abuse.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import psutil
import resource
import threading
from typing import Any, Optional, Dict
from dataclasses import dataclass
from contextlib import contextmanager

# Add project root to Python path to allow sibling module imports
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
if PROJECT_ROOT not in sys.path:
    pass
#     sys.path.insert(0, PROJECT_ROOT)  # Removed sys.path manipulation

# Import logger setup
from codomyrmex.logging_monitoring.logger_config import get_logger

# Get module logger
logger = get_logger(__name__)

# Constants and configuration
DEFAULT_TIMEOUT = 30
MAX_TIMEOUT = 300
MIN_TIMEOUT = 1

# Supported languages and their corresponding Docker images and file extensions
SUPPORTED_LANGUAGES = {
    "python": {
        "image": "python:3.9-slim",
        "extension": "py",
        "command": ["python", "{filename}"],
        "timeout_factor": 1.2,  # Additional time for container start/stop
    },
    "javascript": {
        "image": "node:14-alpine",
        "extension": "js",
        "command": ["node", "{filename}"],
        "timeout_factor": 1.2,
    },
    "java": {
        "image": "openjdk:11-jre-slim",
        "extension": "java",
        "command": [
            "sh",
            "-c",
            "javac {filename} && java $(basename {filename} .java)",
        ],
        "timeout_factor": 1.5,
    },
    "cpp": {
        "image": "gcc:9",
        "extension": "cpp",
        "command": ["sh", "-c", "g++ -o /tmp/program {filename} && /tmp/program"],
        "timeout_factor": 1.5,
    },
    "c": {
        "image": "gcc:9",
        "extension": "c",
        "command": ["sh", "-c", "gcc -o /tmp/program {filename} && /tmp/program"],
        "timeout_factor": 1.5,
    },
    "go": {
        "image": "golang:1.19-alpine",
        "extension": "go",
        "command": ["go", "run", "{filename}"],
        "timeout_factor": 1.3,
    },
    "rust": {
        "image": "rust:1.65-slim",
        "extension": "rs",
        "command": ["sh", "-c", "rustc {filename} -o /tmp/program && /tmp/program"],
        "timeout_factor": 1.5,
    },
    "bash": {
        "image": "bash:5.1",
        "extension": "sh",
        "command": ["bash", "{filename}"],
        "timeout_factor": 1.2,
    },
}


@dataclass
class ExecutionLimits:
    """Structured configuration for execution resource limits."""
    time_limit: int = 30  # seconds
    memory_limit: int = 256  # MB
    cpu_limit: float = 0.5  # CPU cores
    max_output_chars: int = 100000  # Maximum output size

    def __post_init__(self):
        """Validate limits after initialization."""
        if self.time_limit < 1 or self.time_limit > MAX_TIMEOUT:
            raise ValueError(f"Time limit must be between 1 and {MAX_TIMEOUT} seconds")
        if self.memory_limit < 1:
            raise ValueError("Memory limit must be at least 1 MB")
        if self.cpu_limit <= 0 or self.cpu_limit > 4:
            raise ValueError("CPU limit must be between 0.1 and 4.0 cores")
        if self.max_output_chars < 1000:
            raise ValueError("Max output chars must be at least 1000")


class ResourceMonitor:
    """Monitor resource usage during code execution."""

    def __init__(self):
        self.start_time = None
        self.start_memory = None
        self.peak_memory = 0
        self.cpu_usage = []

    def start_monitoring(self) -> None:
        """Start resource monitoring."""
        self.start_time = time.time()
        try:
            process = psutil.Process()
            self.start_memory = process.memory_info().rss / 1024 / 1024  # MB
            self.peak_memory = self.start_memory
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            logger.warning("Unable to start memory monitoring")
            self.start_memory = 0

    def update_monitoring(self) -> None:
        """Update resource usage metrics."""
        try:
            process = psutil.Process()
            current_memory = process.memory_info().rss / 1024 / 1024  # MB
            self.peak_memory = max(self.peak_memory, current_memory)

            # Get CPU usage (sample for 0.1 seconds)
            cpu_percent = process.cpu_percent(interval=0.1)
            self.cpu_usage.append(cpu_percent)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass  # Process may have ended

    def get_resource_usage(self) -> Dict[str, Any]:
        """Get current resource usage statistics."""
        execution_time = time.time() - self.start_time if self.start_time else 0

        return {
            "execution_time_seconds": round(execution_time, 3),
            "memory_start_mb": round(self.start_memory or 0, 2),
            "memory_peak_mb": round(self.peak_memory, 2),
            "cpu_samples": len(self.cpu_usage),
            "cpu_average_percent": round(sum(self.cpu_usage) / len(self.cpu_usage), 2) if self.cpu_usage else 0,
            "cpu_peak_percent": round(max(self.cpu_usage), 2) if self.cpu_usage else 0,
        }


# Default Docker run arguments for security
DEFAULT_DOCKER_ARGS = [
    "--network=none",  # No network access
    "--cap-drop=ALL",  # Drop all capabilities
    "--security-opt=no-new-privileges",  # Prevent privilege escalation
    "--read-only",  # Read-only container
    "--memory=256m",  # Memory limit
    "--memory-swap=256m",  # Disable swap
    "--cpus=0.5",  # CPU limit
    "--pids-limit=50",  # Process limit
]

# Session management (if needed)
ACTIVE_SESSIONS = {}  # Dictionary to track active session containers


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


def validate_language(language: str) -> bool:
    """Validate that the requested language is supported."""
    return language in SUPPORTED_LANGUAGES


def validate_timeout(timeout: Optional[int]) -> int:
    """Validate and normalize timeout value."""
    if timeout is None:
        return DEFAULT_TIMEOUT

    # Ensure timeout is within allowed range
    timeout = max(MIN_TIMEOUT, min(MAX_TIMEOUT, timeout))
    return timeout


def validate_session_id(session_id: Optional[str]) -> Optional[str]:
    """Validate session ID format if provided."""
    if session_id is None:
        return None

    # Basic validation - alphanumeric plus underscores/hyphens, max length
    if not isinstance(session_id, str) or len(session_id) > 64:
        return None

    for char in session_id:
        if not (char.isalnum() or char in "_-"):
            return None

    return session_id


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


def prepare_stdin_file(stdin: Optional[str], temp_dir: str) -> Optional[str]:
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


def run_code_in_docker(
    language: str,
    code_file_path: str,
    temp_dir: str,
    stdin_file: Optional[str] = None,
    timeout: int = DEFAULT_TIMEOUT,
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


def cleanup_temp_files(temp_dir: str) -> None:
    """Safely clean up temporary directory and files."""
    try:
        shutil.rmtree(temp_dir)
    except OSError as e:
        logger.warning(f"Failed to clean up temporary directory {temp_dir}: {str(e)}")


@contextmanager
def resource_limits_context(limits: ExecutionLimits):
    """Context manager to set and restore resource limits."""
    old_limits = {}

    try:
        # Set CPU time limit (soft limit)
        soft, hard = resource.getrlimit(resource.RLIMIT_CPU)
        old_limits[resource.RLIMIT_CPU] = (soft, hard)
        resource.setrlimit(resource.RLIMIT_CPU, (limits.time_limit, hard))

        # Set memory limit (address space)
        soft, hard = resource.getrlimit(resource.RLIMIT_AS)
        old_limits[resource.RLIMIT_AS] = (soft, hard)
        memory_bytes = limits.memory_limit * 1024 * 1024  # Convert MB to bytes
        resource.setrlimit(resource.RLIMIT_AS, (memory_bytes, memory_bytes))

        yield

    finally:
        # Restore original limits
        for rlimit, (soft, hard) in old_limits.items():
            try:
                resource.setrlimit(rlimit, (soft, hard))
            except Exception as e:
                logger.warning(f"Failed to restore resource limit {rlimit}: {e}")


def execute_with_limits(
    language: str,
    code: str,
    limits: ExecutionLimits,
    stdin: Optional[str] = None,
    session_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Execute code with resource limits and monitoring.

    Args:
        language: Programming language of the code
        code: Source code to execute
        limits: ExecutionLimits configuration
        stdin: Standard input to provide to the program
        session_id: Optional session identifier for persistent environments

    Returns:
        Dictionary with execution results including resource usage
    """
    monitor = ResourceMonitor()

    # Set resource limits for the current process
    with resource_limits_context(limits):
        monitor.start_monitoring()

        # Execute the code
        result = execute_code(language, code, stdin, limits.time_limit, session_id)

        # Update monitoring during execution (in a separate thread for better tracking)
        def monitoring_thread():
            while True:
                monitor.update_monitoring()
                time.sleep(0.1)  # Update every 100ms
                # Stop monitoring when execution completes (this is approximate)

        monitor_thread = threading.Thread(target=monitoring_thread, daemon=True)
        monitor_thread.start()

        # Wait for execution to complete
        time.sleep(result.get("execution_time", 0) + 0.1)

        # Get final resource usage
        resource_usage = monitor.get_resource_usage()

        # Merge resource usage into result
        result.update({
            "resource_usage": resource_usage,
            "limits_applied": {
                "time_limit_seconds": limits.time_limit,
                "memory_limit_mb": limits.memory_limit,
                "cpu_limit_cores": limits.cpu_limit,
                "max_output_chars": limits.max_output_chars,
            }
        })

        return result


def sandbox_process_isolation(
    language: str,
    code: str,
    limits: ExecutionLimits,
    stdin: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Execute code in a completely isolated process environment.

    This function creates a subprocess with its own resource limits,
    completely separate from the main process.

    Args:
        language: Programming language of the code
        code: Source code to execute
        limits: ExecutionLimits configuration
        stdin: Standard input to provide to the program

    Returns:
        Dictionary with execution results
    """
    import multiprocessing

    def execute_in_subprocess(queue):
        """Execute code in a subprocess with resource limits."""
        try:
            # Set resource limits in the subprocess
            resource.setrlimit(resource.RLIMIT_CPU, (limits.time_limit, limits.time_limit + 10))
            memory_bytes = limits.memory_limit * 1024 * 1024
            resource.setrlimit(resource.RLIMIT_AS, (memory_bytes, memory_bytes))

            # Execute the code
            result = execute_code(language, code, stdin, limits.time_limit)

            # Cap output size
            if len(result.get("stdout", "")) > limits.max_output_chars:
                result["stdout"] = result["stdout"][:limits.max_output_chars] + "\n... [Output truncated]"
            if len(result.get("stderr", "")) > limits.max_output_chars:
                result["stderr"] = result["stderr"][:limits.max_output_chars] + "\n... [Error output truncated]"

            queue.put(("success", result))

        except Exception as e:
            queue.put(("error", str(e)))

    # Create a queue for communication
    queue = multiprocessing.Queue()

    # Create and start the subprocess
    process = multiprocessing.Process(target=execute_in_subprocess, args=(queue,))
    process.start()

    # Wait for completion with timeout
    process.join(timeout=limits.time_limit + 5)  # Extra 5 seconds for cleanup

    if process.is_alive():
        # Process is still running (timeout exceeded)
        process.terminate()
        process.join(timeout=2)
        if process.is_alive():
            process.kill()

        return {
            "stdout": "",
            "stderr": f"Execution timeout exceeded ({limits.time_limit} seconds)",
            "exit_code": -1,
            "execution_time": limits.time_limit,
            "status": "timeout",
            "error_message": f"Process terminated due to timeout ({limits.time_limit}s)",
            "resource_usage": {
                "execution_time_seconds": limits.time_limit,
                "memory_start_mb": 0,
                "memory_peak_mb": 0,
                "cpu_samples": 0,
                "cpu_average_percent": 0,
                "cpu_peak_percent": 0,
            },
            "limits_applied": {
                "time_limit_seconds": limits.time_limit,
                "memory_limit_mb": limits.memory_limit,
                "cpu_limit_cores": limits.cpu_limit,
                "max_output_chars": limits.max_output_chars,
            }
        }

    # Get the result from the subprocess
    if not queue.empty():
        status, data = queue.get()
        if status == "success":
            # Add resource usage information
            data.update({
                "resource_usage": {
                    "execution_time_seconds": data.get("execution_time", 0),
                    "memory_start_mb": 0,  # Not available in subprocess
                    "memory_peak_mb": 0,   # Not available in subprocess
                    "cpu_samples": 0,
                    "cpu_average_percent": 0,
                    "cpu_peak_percent": 0,
                },
                "limits_applied": {
                    "time_limit_seconds": limits.time_limit,
                    "memory_limit_mb": limits.memory_limit,
                    "cpu_limit_cores": limits.cpu_limit,
                    "max_output_chars": limits.max_output_chars,
                }
            })
            return data
        else:
            return {
                "stdout": "",
                "stderr": f"Subprocess error: {data}",
                "exit_code": -1,
                "execution_time": 0,
                "status": "subprocess_error",
                "error_message": f"Execution failed in subprocess: {data}",
                "resource_usage": {
                    "execution_time_seconds": 0,
                    "memory_start_mb": 0,
                    "memory_peak_mb": 0,
                    "cpu_samples": 0,
                    "cpu_average_percent": 0,
                    "cpu_peak_percent": 0,
                },
                "limits_applied": {
                    "time_limit_seconds": limits.time_limit,
                    "memory_limit_mb": limits.memory_limit,
                    "cpu_limit_cores": limits.cpu_limit,
                    "max_output_chars": limits.max_output_chars,
                }
            }

    # Queue was empty (unexpected)
    return {
        "stdout": "",
        "stderr": "Unexpected error: no result from subprocess",
        "exit_code": -1,
        "execution_time": 0,
        "status": "communication_error",
        "error_message": "Failed to communicate with execution subprocess",
        "resource_usage": {
            "execution_time_seconds": 0,
            "memory_start_mb": 0,
            "memory_peak_mb": 0,
            "cpu_samples": 0,
            "cpu_average_percent": 0,
            "cpu_peak_percent": 0,
        },
        "limits_applied": {
            "time_limit_seconds": limits.time_limit,
            "memory_limit_mb": limits.memory_limit,
            "cpu_limit_cores": limits.cpu_limit,
            "max_output_chars": limits.max_output_chars,
        }
    }


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


if __name__ == "__main__":
    # Example usage when run directly
    example_code = """
print("Hello from the sandbox!")
import sys
print(f"Python version: {sys.version}")
name = input("Enter your name: ")
print(f"Hello, {name}!")
    """

    result = execute_code(
        language="python", code=example_code, stdin="Test User", timeout=10
    )

    print(json.dumps(result, indent=2))
