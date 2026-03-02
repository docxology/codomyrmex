"""Subprocess Execution Utilities.

This module provides comprehensive utilities for subprocess execution, reducing
code duplication across the codebase. It includes synchronous and asynchronous
command execution, streaming output, retry logic, and proper error handling.

Usage:
    from codomyrmex.utils.process.subprocess import (
        run_command,
        run_command_async,
        stream_command,
        run_with_retry,
        SubprocessResult,
        CommandError,
    )

    # Synchronous execution
    result = run_command(["git", "status"])
    if result.success:
        print(result.stdout)

    # Async execution
    result = await run_command_async(["npm", "install"])

    # Streaming output
    for line in stream_command(["python", "-m", "pytest"]):
        print(line)

    # With retry logic
    result = run_with_retry(["flaky-command"], max_attempts=3)
"""

from __future__ import annotations

import asyncio
import os
import shlex
import subprocess
import time
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from enum import Enum
from typing import (
    Any,
)

from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)


class CommandErrorType(Enum):
    """Types of command execution errors."""

    EXECUTION_FAILED = "execution_failed"
    TIMEOUT = "timeout"
    FILE_NOT_FOUND = "file_not_found"
    PERMISSION_DENIED = "permission_denied"
    SUBPROCESS_ERROR = "subprocess_error"
    INVALID_COMMAND = "invalid_command"
    WORKING_DIR_NOT_FOUND = "working_dir_not_found"
    UNKNOWN = "unknown"


class CommandError(Exception):
    """Exception raised when command execution fails.

    Attributes:
        message: Human-readable error description.
        error_type: Category of the error.
        command: The command that was executed.
        return_code: The return code if available.
        stdout: Standard output captured before failure.
        stderr: Standard error captured before failure.
        original_exception: The underlying exception if any.
    """

    def __init__(
        self,
        message: str,
        error_type: CommandErrorType = CommandErrorType.EXECUTION_FAILED,
        command: str | list[str] | None = None,
        return_code: int | None = None,
        stdout: str = "",
        stderr: str = "",
        original_exception: Exception | None = None,
    ) -> None:
        """Initialize CommandError.

        Args:
            message: Human-readable error description.
            error_type: Category of the error.
            command: The command that was executed.
            return_code: The return code if available.
            stdout: Standard output captured before failure.
            stderr: Standard error captured before failure.
            original_exception: The underlying exception if any.
        """
        super().__init__(message)
        self.message = message
        self.error_type = error_type
        self.command = command
        self.return_code = return_code
        self.stdout = stdout
        self.stderr = stderr
        self.original_exception = original_exception

    def __str__(self) -> str:
        """Return string representation of the error."""
        parts = [self.message]
        if self.command:
            cmd_str = self.command if isinstance(self.command, str) else " ".join(self.command)
            parts.append(f"Command: {cmd_str}")
        if self.return_code is not None:
            parts.append(f"Return code: {self.return_code}")
        if self.stderr:
            parts.append(f"Stderr: {self.stderr[:500]}")
        return " | ".join(parts)

    def __repr__(self) -> str:
        """Return detailed representation of the error."""
        return (
            f"CommandError(message={self.message!r}, "
            f"error_type={self.error_type.value}, "
            f"return_code={self.return_code})"
        )


@dataclass
class SubprocessResult:
    """Result of a subprocess execution.

    Attributes:
        stdout: Standard output from the command.
        stderr: Standard error from the command.
        return_code: Exit code of the process.
        duration: Execution time in seconds.
        command: The command that was executed.
        success: Whether the command succeeded (return_code == 0).
        timed_out: Whether the command timed out.
        error_message: Human-readable error message if failed.
    """

    stdout: str = ""
    stderr: str = ""
    return_code: int = 0
    duration: float = 0.0
    command: str | list[str] = field(default_factory=list)
    success: bool = True
    timed_out: bool = False
    error_message: str | None = None

    def __post_init__(self) -> None:
        """Update success based on return_code."""
        self.success = self.return_code == 0 and not self.timed_out

    @property
    def output(self) -> str:
        """Return combined stdout and stderr."""
        parts = []
        if self.stdout:
            parts.append(self.stdout)
        if self.stderr:
            parts.append(self.stderr)
        return "\n".join(parts)

    @property
    def command_string(self) -> str:
        """Return command as a string."""
        if isinstance(self.command, str):
            return self.command
        return " ".join(self.command)

    def to_dict(self) -> dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "stdout": self.stdout,
            "stderr": self.stderr,
            "return_code": self.return_code,
            "duration": self.duration,
            "command": self.command_string,
            "success": self.success,
            "timed_out": self.timed_out,
            "error_message": self.error_message,
        }

    def raise_on_error(self, message: str | None = None) -> SubprocessResult:
        """Raise CommandError if the command failed.

        Args:
            message: Custom error message (optional).

        Returns:
            self if successful.

        Raises:
            CommandError: If the command failed.
        """
        if not self.success:
            error_msg = message or self.error_message or f"Command failed with code {self.return_code}"
            error_type = CommandErrorType.TIMEOUT if self.timed_out else CommandErrorType.EXECUTION_FAILED
            raise CommandError(
                message=error_msg,
                error_type=error_type,
                command=self.command,
                return_code=self.return_code,
                stdout=self.stdout,
                stderr=self.stderr,
            )
        return self


def _prepare_command(
    command: str | list[str],
    shell: bool = False,
) -> str | list[str]:
    """Prepare command for execution.

    Args:
        command: Command to execute (string or list).
        shell: Whether to use shell execution.

    Returns:
        Prepared command.
    """
    if shell:
        # For shell mode, ensure it's a string
        if isinstance(command, list):
            return " ".join(command)
        return command
    else:
        # For non-shell mode, ensure it's a list
        if isinstance(command, str):
            return shlex.split(command)
        return list(command)


def _prepare_environment(
    env: Mapping[str, str] | None = None,
    inherit_env: bool = True,
) -> dict[str, str] | None:
    """Prepare environment variables for subprocess.

    Args:
        env: Additional environment variables to set.
        inherit_env: Whether to inherit current process environment.

    Returns:
        Prepared environment dictionary or None.
    """
    if env is None and inherit_env:
        return None  # Let subprocess inherit environment

    if inherit_env:
        result = os.environ.copy()
        if env:
            result.update(env)
        return result

    return dict(env) if env else {}


def _validate_working_directory(cwd: str | None) -> str | None:
    """Validate and resolve working directory.

    Args:
        cwd: Working directory path.

    Returns:
        Validated working directory path.

    Raises:
        CommandError: If directory doesn't exist.
    """
    if cwd is None:
        return None

    if not os.path.isdir(cwd):
        raise CommandError(
            message=f"Working directory does not exist: {cwd}",
            error_type=CommandErrorType.WORKING_DIR_NOT_FOUND,
        )

    return os.path.abspath(cwd)


def run_command(
    command: str | list[str],
    *,
    cwd: str | None = None,
    env: Mapping[str, str] | None = None,
    timeout: float | None = None,
    shell: bool = False,
    capture_output: bool = True,
    check: bool = False,
    inherit_env: bool = True,
    input_data: str | None = None,
    encoding: str = "utf-8",
    errors: str = "replace",
) -> SubprocessResult:
    """Execute a command synchronously.

    This function provides a unified interface for subprocess execution with
    comprehensive error handling, timeout support, and consistent result format.

    Args:
        command: Command to execute. Can be a string (split by shlex if not shell)
            or a list of arguments.
        cwd: Working directory for the command.
        env: Additional environment variables to set.
        timeout: Maximum execution time in seconds. None for no timeout.
        shell: If True, execute command through the shell.
        capture_output: If True, capture stdout and stderr.
        check: If True, raise CommandError on non-zero exit code.
        inherit_env: If True, inherit current environment variables.
        input_data: Data to send to stdin.
        encoding: Text encoding for output.
        errors: Error handling for encoding issues.

    Returns:
        SubprocessResult containing execution details.

    Raises:
        CommandError: If check=True and command fails, or for other errors.

    Example:
        >>> result = run_command(["git", "status"])
        >>> if result.success:
        ...     print(result.stdout)

        >>> # With environment variables
        >>> result = run_command(
        ...     "npm install",
        ...     env={"NODE_ENV": "production"},
        ...     cwd="/path/to/project",
        ...     timeout=300,
        ... )
    """
    start_time = time.perf_counter()

    try:
        # Validate working directory
        cwd = _validate_working_directory(cwd)

        # Prepare command and environment
        prepared_command = _prepare_command(command, shell)
        prepared_env = _prepare_environment(env, inherit_env)

        logger.debug(
            f"Running command: {prepared_command if isinstance(prepared_command, str) else ' '.join(prepared_command)}"
        )

        # Execute the command
        process_result = subprocess.run(
            prepared_command,
            cwd=cwd,
            env=prepared_env,
            timeout=timeout,
            shell=shell,
            capture_output=capture_output,
            text=True,
            input=input_data,
            encoding=encoding,
            errors=errors,
        )

        duration = time.perf_counter() - start_time

        result = SubprocessResult(
            stdout=process_result.stdout or "",
            stderr=process_result.stderr or "",
            return_code=process_result.returncode,
            duration=duration,
            command=command,
            timed_out=False,
            error_message=None if process_result.returncode == 0 else f"Command exited with code {process_result.returncode}",
        )

        logger.debug(
            f"Command completed with return code {result.return_code} in {duration:.3f}s"
        )

        if check:
            result.raise_on_error()

        return result

    except subprocess.TimeoutExpired as e:
        duration = time.perf_counter() - start_time
        error_msg = f"Command timed out after {timeout}s"
        logger.warning(error_msg)

        result = SubprocessResult(
            stdout=e.stdout.decode(encoding, errors=errors) if e.stdout else "",
            stderr=e.stderr.decode(encoding, errors=errors) if e.stderr else "",
            return_code=-1,
            duration=duration,
            command=command,
            timed_out=True,
            error_message=error_msg,
        )

        if check:
            raise CommandError(
                message=error_msg,
                error_type=CommandErrorType.TIMEOUT,
                command=command,
                return_code=-1,
                stdout=result.stdout,
                stderr=result.stderr,
                original_exception=e,
            ) from e

        return result

    except FileNotFoundError as e:
        duration = time.perf_counter() - start_time
        error_msg = f"Command not found: {e.filename or command}"
        logger.error(error_msg)

        if check:
            raise CommandError(
                message=error_msg,
                error_type=CommandErrorType.FILE_NOT_FOUND,
                command=command,
                original_exception=e,
            ) from e

        return SubprocessResult(
            return_code=-1,
            duration=duration,
            command=command,
            error_message=error_msg,
        )

    except PermissionError as e:
        duration = time.perf_counter() - start_time
        error_msg = f"Permission denied: {e}"
        logger.error(error_msg)

        if check:
            raise CommandError(
                message=error_msg,
                error_type=CommandErrorType.PERMISSION_DENIED,
                command=command,
                original_exception=e,
            ) from e

        return SubprocessResult(
            return_code=-1,
            duration=duration,
            command=command,
            error_message=error_msg,
        )

    except subprocess.SubprocessError as e:
        duration = time.perf_counter() - start_time
        error_msg = f"Subprocess error: {e}"
        logger.error(error_msg)

        if check:
            raise CommandError(
                message=error_msg,
                error_type=CommandErrorType.SUBPROCESS_ERROR,
                command=command,
                original_exception=e,
            ) from e

        return SubprocessResult(
            return_code=-1,
            duration=duration,
            command=command,
            error_message=error_msg,
        )

    except CommandError:
        # Re-raise CommandError (from raise_on_error) without wrapping
        raise

    except Exception as e:
        duration = time.perf_counter() - start_time
        error_msg = f"Unexpected error executing command: {e}"
        logger.error(error_msg, exc_info=True)

        if check:
            raise CommandError(
                message=error_msg,
                error_type=CommandErrorType.UNKNOWN,
                command=command,
                original_exception=e,
            ) from e

        return SubprocessResult(
            return_code=-1,
            duration=duration,
            command=command,
            error_message=error_msg,
        )


async def run_command_async(
    command: str | list[str],
    *,
    cwd: str | None = None,
    env: Mapping[str, str] | None = None,
    timeout: float | None = None,
    shell: bool = False,
    inherit_env: bool = True,
    input_data: str | None = None,
    encoding: str = "utf-8",
    errors: str = "replace",
) -> SubprocessResult:
    """Execute a command asynchronously.

    This function provides async subprocess execution using asyncio, suitable
    for concurrent task execution without blocking the event loop.

    Args:
        command: Command to execute. Can be a string or list of arguments.
        cwd: Working directory for the command.
        env: Additional environment variables to set.
        timeout: Maximum execution time in seconds. None for no timeout.
        shell: If True, execute command through the shell.
        inherit_env: If True, inherit current environment variables.
        input_data: Data to send to stdin.
        encoding: Text encoding for output.
        errors: Error handling for encoding issues.

    Returns:
        SubprocessResult containing execution details.

    Example:
        >>> async def main():
        ...     result = await run_command_async(["npm", "install"])
        ...     print(result.stdout)
    """
    start_time = time.perf_counter()

    try:
        # Validate working directory
        cwd = _validate_working_directory(cwd)

        # Prepare environment
        prepared_env = _prepare_environment(env, inherit_env)

        # Prepare input
        input_bytes = input_data.encode(encoding) if input_data else None

        if shell:
            # For shell mode, use string command
            cmd_str = command if isinstance(command, str) else " ".join(command)
            logger.debug(f"Running async shell command: {cmd_str}")

            process = await asyncio.create_subprocess_shell(
                cmd_str,
                cwd=cwd,
                env=prepared_env,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                stdin=asyncio.subprocess.PIPE if input_bytes else None,
            )
        else:
            # For non-shell mode, use list command
            cmd_list = shlex.split(command) if isinstance(command, str) else list(command)
            logger.debug(f"Running async command: {' '.join(cmd_list)}")

            process = await asyncio.create_subprocess_exec(
                *cmd_list,
                cwd=cwd,
                env=prepared_env,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                stdin=asyncio.subprocess.PIPE if input_bytes else None,
            )

        try:
            stdout_bytes, stderr_bytes = await asyncio.wait_for(
                process.communicate(input=input_bytes),
                timeout=timeout,
            )
            timed_out = False
        except TimeoutError:
            process.kill()
            await process.wait()
            stdout_bytes, stderr_bytes = b"", b""
            timed_out = True

        duration = time.perf_counter() - start_time

        stdout = stdout_bytes.decode(encoding, errors=errors) if stdout_bytes else ""
        stderr = stderr_bytes.decode(encoding, errors=errors) if stderr_bytes else ""

        result = SubprocessResult(
            stdout=stdout,
            stderr=stderr,
            return_code=process.returncode if process.returncode is not None else -1,
            duration=duration,
            command=command,
            timed_out=timed_out,
            error_message=f"Command timed out after {timeout}s" if timed_out else None,
        )

        logger.debug(
            f"Async command completed with return code {result.return_code} in {duration:.3f}s"
        )

        return result

    except FileNotFoundError as e:
        duration = time.perf_counter() - start_time
        error_msg = f"Command not found: {e.filename or command}"
        logger.error(error_msg)

        return SubprocessResult(
            return_code=-1,
            duration=duration,
            command=command,
            error_message=error_msg,
        )

    except PermissionError as e:
        duration = time.perf_counter() - start_time
        error_msg = f"Permission denied: {e}"
        logger.error(error_msg)

        return SubprocessResult(
            return_code=-1,
            duration=duration,
            command=command,
            error_message=error_msg,
        )

    except Exception as e:
        duration = time.perf_counter() - start_time
        error_msg = f"Unexpected error executing async command: {e}"
        logger.error(error_msg, exc_info=True)

        return SubprocessResult(
            return_code=-1,
            duration=duration,
            command=command,
            error_message=error_msg,
        )


# Re-export advanced functions from subprocess_advanced for backward compatibility
from .subprocess_advanced import stream_command, run_with_retry  # noqa: E402, I001


def check_command_available(command: str) -> bool:
    """Check if a command is available on the system.

    Args:
        command: Command name to check.

    Returns:
        True if command is available, False otherwise.

    Example:
        >>> if check_command_available("git"):
        ...     result = run_command(["git", "status"])
    """
    import shutil

    return shutil.which(command) is not None


def get_command_version(
    command: str,
    version_args: Sequence[str] = ("--version",),
) -> str | None:
    """Get the version string of a command.

    Args:
        command: Command name.
        version_args: Arguments to get version (default: --version).

    Returns:
        Version string if available, None otherwise.

    Example:
        >>> version = get_command_version("git")
        >>> print(version)  # "git version 2.39.0"
    """
    try:
        result = run_command([command, *version_args], timeout=10)
        if result.success:
            return result.stdout.strip().split("\n")[0]
    except Exception as e:
        logger.debug("Failed to get version for command %s: %s", command, e)
        pass
    return None


def quote_command(command: str | list[str]) -> str:
    """Safely quote a command for shell execution.

    Args:
        command: Command as string or list.

    Returns:
        Properly quoted command string.

    Example:
        >>> quote_command(["echo", "hello world"])
        "echo 'hello world'"
    """
    if isinstance(command, str):
        return command
    return shlex.join(command)


def split_command(command: str) -> list[str]:
    """Split a command string into list of arguments.

    Args:
        command: Command string.

    Returns:
        List of command arguments.

    Example:
        >>> split_command("echo 'hello world'")
        ["echo", "hello world"]
    """
    return shlex.split(command)


__all__ = [
    # Main execution functions
    "run_command",
    "run_command_async",
    "stream_command",
    "run_with_retry",
    # Result and error types
    "SubprocessResult",
    "CommandError",
    "CommandErrorType",
    # Utility functions
    "check_command_available",
    "get_command_version",
    "quote_command",
    "split_command",
]
