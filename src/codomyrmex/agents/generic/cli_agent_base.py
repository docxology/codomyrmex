from pathlib import Path
from typing import Any, Iterator, Optional
import os
import subprocess
import time

from codomyrmex.agents.core import AgentRequest, AgentResponse
from codomyrmex.agents.exceptions import AgentError, AgentTimeoutError
from codomyrmex.agents.generic.base_agent import BaseAgent
from codomyrmex.logging_monitoring import get_logger
























"""Base class for CLI-based agents with common subprocess patterns."""

"""Core functionality module

This module provides cli_agent_base functionality including:
- 6 functions: __init__, _check_command_available, _build_env...
- 1 classes: CLIAgentBase

Usage:
    from cli_agent_base import FunctionName, ClassName
    # Example usage here
"""
class CLIAgentBase(BaseAgent):
    """Base class for CLI-based agents with common subprocess execution patterns."""

    def __init__(
        self,
        name: str,
        command: str,
        capabilities: list,
        config: Optional[dict[str, Any]] = None,
        timeout: Optional[int] = None,
        working_dir: Optional[Path] = None,
        env_vars: Optional[dict[str, str]] = None,
    ):
        """
        Initialize CLI agent base.

        Args:
            name: Agent name
            command: CLI command name
            capabilities: List of capabilities
            config: Optional configuration override
            timeout: Command timeout in seconds
            working_dir: Working directory for commands
            env_vars: Environment variables to set
        """
        super().__init__(name, capabilities, config)
        self.command = command
        self.timeout = timeout or self.get_config_value("timeout", 30)
        self.working_dir = working_dir or self.get_config_value(
            "working_dir", Path.cwd()
        )
        self.env_vars = env_vars or {}
        self._command_available = None

    def _check_command_available(
        self, command: Optional[str] = None, check_args: Optional[list[str]] = None
    ) -> bool:
        """
        Check if command is available.

        Args:
            command: Command to check (uses self.command if None)
            check_args: Arguments for availability check (default: ["--help"])

        Returns:
            True if command is available
        """
        if self._command_available is not None:
            return self._command_available

        cmd = command or self.command
        check_args = check_args or ["--help"]

        try:
            result = subprocess.run(
                [cmd] + check_args,
                capture_output=True,
                text=True,
                timeout=5,
            )
            available = (
                result.returncode == 0
                or any(arg in (result.stdout or "") for arg in check_args)
                or any(arg in (result.stderr or "") for arg in check_args)
            )
            self._command_available = available
            if not available:
                self.logger.warning(
                    f"Command '{cmd}' not found or not responding correctly",
                    extra={"command": cmd, "exit_code": result.returncode},
                )
            return available
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            self._command_available = False
            self.logger.debug(
                f"Command '{cmd}' availability check failed: {e}",
                extra={"command": cmd, "error": str(e)},
            )
            return False
        except Exception as e:
            self._command_available = False
            self.logger.warning(
                f"Error checking command '{cmd}' availability: {e}",
                extra={"command": cmd, "error": str(e)},
            )
            return False

    def _build_env(self) -> dict[str, str]:
        """
        Build environment variables for subprocess.

        Returns:
            Environment dictionary
        """
        env = os.environ.copy()
        env.update(self.env_vars)
        return env

    def _execute_command(
        self,
        args: Optional[list[str]] = None,
        input_text: Optional[str] = None,
        timeout: Optional[int] = None,
        cwd: Optional[Path] = None,
        env: Optional[dict[str, str]] = None,
    ) -> dict[str, Any]:
        """
        Execute CLI command and return result.

        Args:
            args: Command arguments
            input_text: Optional input text to send via stdin
            timeout: Command timeout (uses self.timeout if None)
            cwd: Working directory (uses self.working_dir if None)
            env: Environment variables (uses _build_env() if None)

        Returns:
            Command result dictionary with keys: output, exit_code, stdout, stderr, success

        Raises:
            AgentTimeoutError: If command times out
            AgentError: If command not found
        """
        cmd = [self.command]
        if args:
            cmd.extend(args)

        timeout = timeout or self.timeout
        cwd = cwd or self.working_dir
        env = env or self._build_env()

        self.logger.debug(
            f"Executing command: {' '.join(cmd)}",
            extra={
                "command": " ".join(cmd),
                "timeout": timeout,
                "cwd": str(cwd),
                "has_input": input_text is not None,
            },
        )

        start_time = time.time()
        try:
            result = subprocess.run(
                cmd,
                input=input_text,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=cwd,
                env=env,
            )

            execution_time = time.time() - start_time
            output = result.stdout.strip()
            stderr_output = result.stderr.strip()

            # Determine success: exit code 0 OR meaningful output without errors
            success = result.returncode == 0 or (output and not stderr_output)

            self.logger.debug(
                f"Command completed in {execution_time:.2f}s",
                extra={
                    "command": " ".join(cmd),
                    "exit_code": result.returncode,
                    "success": success,
                    "execution_time": execution_time,
                    "output_length": len(output),
                },
            )

            return {
                "output": output,
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": success,
                "execution_time": execution_time,
            }

        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            self.logger.error(
                f"Command timed out after {timeout}s",
                extra={
                    "command": " ".join(cmd),
                    "timeout": timeout,
                    "execution_time": execution_time,
                },
            )
            raise AgentTimeoutError(
                f"Command timed out after {timeout}s",
                timeout=timeout,
                command=" ".join(cmd),
            )
        except FileNotFoundError:
            self.logger.error(
                f"Command not found: {self.command}",
                extra={"command": self.command},
            )
            raise AgentError(
                f"Command not found: {self.command}",
                command=self.command,
            )
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(
                f"Command execution failed: {e}",
                exc_info=True,
                extra={
                    "command": " ".join(cmd),
                    "error": str(e),
                    "execution_time": execution_time,
                },
            )
            raise AgentError(f"Command execution failed: {str(e)}", command=" ".join(cmd)) from e

    def _stream_command(
        self,
        args: Optional[list[str]] = None,
        input_text: Optional[str] = None,
        cwd: Optional[Path] = None,
        env: Optional[dict[str, str]] = None,
    ) -> Iterator[str]:
        """
        Stream CLI command output line by line.

        Args:
            args: Command arguments
            input_text: Optional input text to send via stdin
            cwd: Working directory (uses self.working_dir if None)
            env: Environment variables (uses _build_env() if None)

        Yields:
            Lines of output
        """
        cmd = [self.command]
        if args:
            cmd.extend(args)

        cwd = cwd or self.working_dir
        env = env or self._build_env()

        self.logger.debug(
            f"Streaming command: {' '.join(cmd)}",
            extra={"command": " ".join(cmd), "cwd": str(cwd), "has_input": input_text is not None},
        )

        try:
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE if input_text else None,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=cwd,
                env=env,
                bufsize=1,  # Line buffered
            )

            # Send input if provided
            if input_text:
                process.stdin.write(input_text)
                process.stdin.close()

            # Stream stdout line by line
            line_count = 0
            for line in iter(process.stdout.readline, ""):
                if line:
                    line_count += 1
                    yield line.rstrip()
                else:
                    break

            process.wait()

            if process.returncode != 0:
                stderr = process.stderr.read()
                if stderr:
                    self.logger.warning(
                        f"Command returned non-zero exit code: {process.returncode}",
                        extra={
                            "command": " ".join(cmd),
                            "exit_code": process.returncode,
                            "stderr": stderr[:200],  # Truncate for logging
                        },
                    )
                    yield f"Error: {stderr}"

            self.logger.debug(
                f"Stream completed with {line_count} lines",
                extra={
                    "command": " ".join(cmd),
                    "exit_code": process.returncode,
                    "line_count": line_count,
                },
            )

        except Exception as e:
            self.logger.error(
                f"Error streaming command output: {e}",
                exc_info=True,
                extra={"command": " ".join(cmd), "error": str(e)},
            )
            yield f"Error: {str(e)}"

    def _build_response_from_result(
        self,
        result: dict[str, Any],
        request: AgentRequest,
        execution_time: Optional[float] = None,
        additional_metadata: Optional[dict[str, Any]] = None,
    ) -> AgentResponse:
        """
        Build AgentResponse from command result.

        Args:
            result: Command result dictionary
            request: Original agent request
            execution_time: Execution time (uses result if available)
            additional_metadata: Additional metadata to include

        Returns:
            AgentResponse
        """
        output = result.get("output", "")
        exit_code = result.get("exit_code", 0)
        stderr_output = result.get("stderr", "")
        success = result.get("success", exit_code == 0)
        exec_time = execution_time or result.get("execution_time", 0.0)

        error = None
        if not success and stderr_output:
            error = stderr_output
        elif not success and not output:
            error = f"Command failed with exit code {exit_code}"

        metadata = {
            "command": self.command,
            "exit_code": exit_code,
            "stdout": result.get("stdout", ""),
            "stderr": stderr_output,
            "success": success,
        }
        if additional_metadata:
            metadata.update(additional_metadata)

        return AgentResponse(
            content=output,
            error=error,
            metadata=metadata,
            execution_time=exec_time,
        )


