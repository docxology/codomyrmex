"""OpenCode CLI client wrapper."""

import json
import subprocess
import time
from pathlib import Path
from typing import Any, Iterator, Optional

from codomyrmex.agents.config import get_config
from codomyrmex.agents.core import (
    AgentCapabilities,
    AgentRequest,
    AgentResponse,
)
from codomyrmex.agents.exceptions import OpenCodeError
from codomyrmex.agents.generic import BaseAgent
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class OpenCodeClient(BaseAgent):
    """Client for interacting with OpenCode CLI tool."""

    def __init__(self, config: Optional[dict[str, Any]] = None):
        """
        Initialize OpenCode client.

        Args:
            config: Optional configuration override
        """
        agent_config = get_config()
        super().__init__(
            name="opencode",
            capabilities=[
                AgentCapabilities.CODE_GENERATION,
                AgentCapabilities.CODE_EDITING,
                AgentCapabilities.CODE_ANALYSIS,
                AgentCapabilities.TEXT_COMPLETION,
                AgentCapabilities.STREAMING,
                AgentCapabilities.MULTI_TURN,
            ],
            config=config or {},
        )

        self.opencode_command = (
            config.get("opencode_command")
            if config
            else agent_config.opencode_command
        )
        self.timeout = (
            config.get("opencode_timeout")
            if config
            else agent_config.opencode_timeout
        )
        self.working_dir = (
            config.get("opencode_working_dir")
            if config
            else agent_config.opencode_working_dir
        )
        self.api_key = (
            config.get("opencode_api_key")
            if config
            else agent_config.opencode_api_key
        )

        # Verify opencode is available
        if not self._check_opencode_available():
            logger.warning("OpenCode command not found, some operations may fail")

    def _check_opencode_available(self) -> bool:
        """
        Check if opencode command is available.

        Returns:
            True if opencode is available
        """
        try:
            result = subprocess.run(
                [self.opencode_command, "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def _execute_impl(self, request: AgentRequest) -> AgentResponse:
        """
        Execute OpenCode command.

        Note: OpenCode is primarily a TUI (Terminal User Interface) tool.
        Direct subprocess interaction is limited. This implementation attempts
        to work with OpenCode's CLI interface, but full TUI functionality
        requires interactive use of the OpenCode tool directly.

        Args:
            request: Agent request

        Returns:
            Agent response
        """
        start_time = time.time()

        try:
            # Parse request to determine opencode command
            prompt = request.prompt
            context = request.context or {}

            # Build opencode command
            opencode_args = self._build_opencode_args(prompt, context)

            # Execute opencode command
            result = self._execute_opencode_command(opencode_args)

            execution_time = time.time() - start_time

            # Determine if operation was successful
            output = result.get("output", "")
            exit_code = result.get("exit_code", 0)
            stderr_output = result.get("stderr", "")
            success = result.get("success", exit_code == 0)

            error = None
            if not success and stderr_output:
                error = stderr_output
            elif not success and not output:
                error = f"OpenCode command failed with exit code {exit_code}"

            return AgentResponse(
                content=output,
                error=error,
                metadata={
                    "command": " ".join([self.opencode_command] + opencode_args),
                    "exit_code": exit_code,
                    "stdout": result.get("stdout", ""),
                    "stderr": stderr_output,
                    "opencode_success": success,
                },
                execution_time=execution_time,
            )

        except subprocess.TimeoutExpired as e:
            execution_time = time.time() - start_time
            error_msg = f"OpenCode command timed out after {self.timeout}s"
            return AgentResponse(
                content="",
                error=error_msg,
                metadata={
                    "command": " ".join([self.opencode_command] + opencode_args),
                    "timeout": self.timeout,
                },
                execution_time=execution_time,
            )
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"OpenCode command failed: {str(e)}"
            return AgentResponse(
                content="",
                error=error_msg,
                metadata={
                    "command": " ".join([self.opencode_command] + opencode_args),
                    "exception": str(e),
                },
                execution_time=execution_time,
            )

    def _stream_impl(self, request: AgentRequest) -> Iterator[str]:
        """
        Stream OpenCode command output.

        Note: OpenCode CLI is primarily TUI-based. For streaming, we execute
        the command and stream its output. For interactive TUI mode,
        users should use OpenCode CLI directly.

        Args:
            request: Agent request

        Yields:
            Chunks of output
        """
        prompt = request.prompt
        context = request.context or {}

        opencode_args = self._build_opencode_args(prompt, context)

        try:
            process = subprocess.Popen(
                [self.opencode_command] + opencode_args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=self.working_dir,
                bufsize=1,  # Line buffered
            )

            # Stream stdout line by line
            for line in iter(process.stdout.readline, ""):
                if line:
                    yield line.rstrip()
                else:
                    break

            process.wait()

            if process.returncode != 0:
                stderr = process.stderr.read()
                if stderr:
                    yield f"Error: {stderr}"

        except Exception as e:
            logger.error(f"Error streaming OpenCode output: {e}", exc_info=True)
            yield f"Error: {str(e)}"

    def _build_opencode_args(self, prompt: str, context: dict[str, Any]) -> list[str]:
        """
        Build opencode command arguments from prompt and context.

        OpenCode CLI uses various commands. For code generation/editing tasks,
        we can pass the prompt directly. OpenCode also supports initialization
        and configuration commands.

        Args:
            prompt: User prompt (task description)
            context: Additional context (may include init, command, etc.)

        Returns:
            List of command arguments
        """
        args = []

        # Check if initialization is requested
        if context.get("init", False):
            args.append("--init")
            return args

        # Check for specific command in context
        if "command" in context:
            command = context["command"]
            if command == "init":
                args.append("--init")
                return args
            elif command == "connect":
                args.append("--connect")
                return args
            elif command == "share":
                args.append("--share")
                return args

        # For general prompts, OpenCode typically expects them as arguments
        # or via stdin. Since we're using subprocess, we'll pass as argument
        # Note: This is a limitation - full TUI mode requires interactive use
        if prompt:
            # OpenCode may accept prompts via --prompt flag or as positional args
            # We'll try passing as a single argument
            args.append(prompt)

        return args

    def _execute_opencode_command(self, args: list[str]) -> dict[str, Any]:
        """
        Execute opencode command and return result.

        Args:
            args: Command arguments

        Returns:
            Command result dictionary
        """
        try:
            result = subprocess.run(
                [self.opencode_command] + args,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=self.working_dir,
            )

            # OpenCode CLI may return non-zero for some operations but still produce output
            # Check if we got meaningful output even with non-zero exit code
            output = result.stdout.strip()
            stderr_output = result.stderr.strip()

            return {
                "output": output,
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": result.returncode == 0 or (output and not stderr_output),
            }
        except subprocess.TimeoutExpired:
            raise OpenCodeError(
                "OpenCode command timed out",
                command=" ".join([self.opencode_command] + args),
            )
        except FileNotFoundError:
            raise OpenCodeError(
                f"OpenCode command not found: {self.opencode_command}",
                command=self.opencode_command,
            )

    def initialize_project(self, project_path: Optional[Path] = None) -> dict[str, Any]:
        """
        Initialize OpenCode for a project.

        This runs the `/init` command which analyzes the project and creates
        an AGENTS.md file in the project root.

        Args:
            project_path: Optional project path (uses working_dir if not provided)

        Returns:
            Initialization result dictionary
        """
        working_path = project_path or (Path(self.working_dir) if self.working_dir else Path.cwd())

        try:
            result = subprocess.run(
                [self.opencode_command, "--init"],
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=working_path,
            )

            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None,
                "exit_code": result.returncode,
            }
        except Exception as e:
            logger.error(f"Failed to initialize OpenCode project: {e}", exc_info=True)
            return {
                "success": False,
                "output": "",
                "error": str(e),
                "exit_code": -1,
            }

    def get_opencode_version(self) -> dict[str, Any]:
        """
        Get OpenCode version information.

        Returns:
            Version information dictionary
        """
        try:
            result = subprocess.run(
                [self.opencode_command, "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )

            return {
                "version": result.stdout.strip(),
                "exit_code": result.returncode,
                "available": result.returncode == 0,
            }
        except Exception as e:
            return {
                "version": "",
                "exit_code": -1,
                "available": False,
                "error": str(e),
            }

