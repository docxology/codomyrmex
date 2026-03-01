"""Advanced subprocess utilities: streaming command output and retry logic.

This module provides higher-level subprocess utilities built on the core
run_command infrastructure:
- stream_command(): Execute a command and yield output lines in real-time
- run_with_retry(): Execute a command with configurable retry logic
"""

from __future__ import annotations

import subprocess
import time
from collections.abc import Callable, Generator, Mapping, Sequence
from typing import Any

from codomyrmex.logging_monitoring.core.logger_config import get_logger

from .subprocess import (
    SubprocessResult,
    _prepare_command,
    _prepare_environment,
    _validate_working_directory,
    run_command,
)

logger = get_logger(__name__)


def stream_command(
    command: str | list[str],
    *,
    cwd: str | None = None,
    env: Mapping[str, str] | None = None,
    timeout: float | None = None,
    shell: bool = False,
    inherit_env: bool = True,
    combine_streams: bool = False,
    encoding: str = "utf-8",
    errors: str = "replace",
) -> Generator[str, None, SubprocessResult]:
    """Execute a command and yield output lines in real-time.

    This generator function allows processing command output as it's produced,
    useful for long-running commands or showing progress.

    Args:
        command: Command to execute.
        cwd: Working directory for the command.
        env: Additional environment variables to set.
        timeout: Maximum execution time in seconds.
        shell: If True, execute command through the shell.
        inherit_env: If True, inherit current environment variables.
        combine_streams: If True, combine stdout and stderr.
        encoding: Text encoding for output.
        errors: Error handling for encoding issues.

    Yields:
        Output lines from the command (prefixed with 'stdout:' or 'stderr:' if not combined).

    Returns:
        SubprocessResult when the generator is exhausted.

    Example:
        >>> result = None
        >>> for line in stream_command(["python", "-m", "pytest", "-v"]):
        ...     print(line)
        ...     result = line  # The last value will be overwritten
        >>> # After the loop, get the final result
        >>> gen = stream_command(["ls", "-la"])
        >>> lines = list(gen)
        >>> # The result is available via send() at the end

    Note:
        The SubprocessResult is returned when the generator finishes.
        To capture it, use:
        >>> gen = stream_command(cmd)
        >>> lines = []
        >>> try:
        ...     while True:
        ...         lines.append(next(gen))
        ... except StopIteration as e:
        ...     result = e.value
    """
    start_time = time.perf_counter()
    stdout_lines: list[str] = []
    stderr_lines: list[str] = []
    process: subprocess.Popen | None = None

    try:
        # Validate working directory
        cwd = _validate_working_directory(cwd)

        # Prepare command and environment
        prepared_command = _prepare_command(command, shell)
        prepared_env = _prepare_environment(env, inherit_env)

        logger.debug(
            f"Streaming command: {prepared_command if isinstance(prepared_command, str) else ' '.join(prepared_command)}"
        )

        # Use merged stderr if combining
        stderr_pipe = subprocess.STDOUT if combine_streams else subprocess.PIPE

        process = subprocess.Popen(
            prepared_command,
            cwd=cwd,
            env=prepared_env,
            shell=shell,
            stdout=subprocess.PIPE,
            stderr=stderr_pipe,
            text=True,
            encoding=encoding,
            errors=errors,
            bufsize=1,  # Line buffered
        )

        deadline = time.perf_counter() + timeout if timeout else None

        # Read lines from both streams
        while True:
            if deadline and time.perf_counter() > deadline:
                process.kill()
                duration = time.perf_counter() - start_time
                return SubprocessResult(
                    stdout="\n".join(stdout_lines),
                    stderr="\n".join(stderr_lines),
                    return_code=-1,
                    duration=duration,
                    command=command,
                    timed_out=True,
                    error_message=f"Command timed out after {timeout}s",
                )

            # Check if process has ended
            poll_result = process.poll()

            # Use select to wait up to 0.05s on POSIX systems so we don't block
            readable = []
            import sys
            if sys.platform != "win32":
                import select
                rlist = []
                if process.stdout:
                    rlist.append(process.stdout)
                if not combine_streams and process.stderr:
                    rlist.append(process.stderr)
                if rlist:
                    readable, _, _ = select.select(rlist, [], [], 0.05)
            else:
                readable = [process.stdout] if process.stdout else []
                if not combine_streams and process.stderr:
                    readable.append(process.stderr)

            # Read available output
            if process.stdout and process.stdout in readable:
                line = process.stdout.readline()
                if line:
                    line = line.rstrip("\n\r")
                    stdout_lines.append(line)
                    if combine_streams:
                        yield line
                    else:
                        yield f"stdout: {line}"
                    continue

            if not combine_streams and process.stderr and process.stderr in readable:
                line = process.stderr.readline()
                if line:
                    line = line.rstrip("\n\r")
                    stderr_lines.append(line)
                    yield f"stderr: {line}"
                    continue

            # If process ended and no more output, break
            if poll_result is not None:
                # Read any remaining output
                if process.stdout:
                    remaining = process.stdout.read()
                    if remaining:
                        for line in remaining.rstrip("\n\r").split("\n"):
                            stdout_lines.append(line)
                            if combine_streams:
                                yield line
                            else:
                                yield f"stdout: {line}"

                if not combine_streams and process.stderr:
                    remaining = process.stderr.read()
                    if remaining:
                        for line in remaining.rstrip("\n\r").split("\n"):
                            stderr_lines.append(line)
                            yield f"stderr: {line}"
                break

        duration = time.perf_counter() - start_time

        return SubprocessResult(
            stdout="\n".join(stdout_lines),
            stderr="\n".join(stderr_lines),
            return_code=process.returncode if process.returncode is not None else -1,
            duration=duration,
            command=command,
            timed_out=False,
        )

    except FileNotFoundError as e:
        duration = time.perf_counter() - start_time
        return SubprocessResult(
            stdout="\n".join(stdout_lines),
            stderr="\n".join(stderr_lines),
            return_code=-1,
            duration=duration,
            command=command,
            error_message=f"Command not found: {e.filename or command}",
        )

    except Exception as e:
        duration = time.perf_counter() - start_time
        logger.error(f"Error streaming command: {e}", exc_info=True)
        return SubprocessResult(
            stdout="\n".join(stdout_lines),
            stderr="\n".join(stderr_lines),
            return_code=-1,
            duration=duration,
            command=command,
            error_message=f"Error streaming command: {e}",
        )

    finally:
        if process is not None:
            # Ensure process is terminated
            if process.poll() is None:
                process.kill()
                process.wait()
            # Close file handles
            if process.stdout:
                process.stdout.close()
            if process.stderr:
                process.stderr.close()


def run_with_retry(
    command: str | list[str],
    *,
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    retry_on_codes: Sequence[int] | None = None,
    retry_on_timeout: bool = True,
    on_retry: Callable[[int, SubprocessResult], None] | None = None,
    **kwargs: Any,
) -> SubprocessResult:
    """Execute a command with retry logic for flaky commands.

    This function wraps run_command with configurable retry behavior,
    useful for commands that may fail intermittently due to network
    issues or transient errors.

    Args:
        command: Command to execute.
        max_attempts: Maximum number of execution attempts.
        delay: Initial delay between retries in seconds.
        backoff: Multiplier for delay after each retry.
        retry_on_codes: Return codes that should trigger retry. If None,
            retry on any non-zero return code.
        retry_on_timeout: Whether to retry on timeout.
        on_retry: Optional callback called before each retry with
            (attempt_number, last_result).
        **kwargs: Additional arguments passed to run_command.

    Returns:
        SubprocessResult from the last attempt.

    Example:
        >>> # Retry on any failure
        >>> result = run_with_retry(["flaky-command"], max_attempts=3)

        >>> # Retry only on specific exit codes
        >>> result = run_with_retry(
        ...     ["api-call"],
        ...     retry_on_codes=[1, 2, 255],
        ...     delay=5.0,
        ...     backoff=2.0,
        ... )

        >>> # With retry callback
        >>> def log_retry(attempt, result):
        ...     print(f"Attempt {attempt} failed: {result.stderr}")
        >>> result = run_with_retry(cmd, on_retry=log_retry)
    """
    current_delay = delay
    last_result: SubprocessResult | None = None

    for attempt in range(1, max_attempts + 1):
        logger.debug(f"Executing command (attempt {attempt}/{max_attempts})")

        result = run_command(command, **kwargs)
        last_result = result

        # Check if we should retry
        should_retry = False

        if result.timed_out and retry_on_timeout:
            should_retry = True
        elif not result.success:
            if retry_on_codes is None:
                should_retry = True
            elif result.return_code in retry_on_codes:
                should_retry = True

        # If successful or no retry needed, return
        if not should_retry:
            if result.success:
                logger.debug(f"Command succeeded on attempt {attempt}")
            return result

        # If this was the last attempt, return the result
        if attempt >= max_attempts:
            logger.warning(f"Command failed after {max_attempts} attempts")
            return result

        # Call retry callback if provided
        if on_retry:
            try:
                on_retry(attempt, result)
            except Exception as e:
                logger.warning(f"Retry callback raised exception: {e}")

        # Wait before retrying
        logger.debug(f"Retrying in {current_delay:.1f}s...")
        time.sleep(current_delay)
        current_delay *= backoff

    # This should not be reached, but return last result just in case
    return last_result or SubprocessResult(
        return_code=-1,
        command=command,
        error_message="No attempts made",
    )
