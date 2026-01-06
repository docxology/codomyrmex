"""Jules CLI client wrapper."""

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
from codomyrmex.agents.exceptions import JulesError
from codomyrmex.agents.generic import BaseAgent
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class JulesClient(BaseAgent):
    """Client for interacting with Jules CLI tool."""

    def __init__(self, config: Optional[dict[str, Any]] = None):
        """
        Initialize Jules client.

        Args:
            config: Optional configuration override
        """
        agent_config = get_config()
        super().__init__(
            name="jules",
            capabilities=[
                AgentCapabilities.CODE_GENERATION,
                AgentCapabilities.CODE_EDITING,
                AgentCapabilities.CODE_ANALYSIS,
                AgentCapabilities.TEXT_COMPLETION,
                AgentCapabilities.STREAMING,
            ],
            config=config or {},
        )

        self.jules_command = (
            config.get("jules_command")
            if config
            else agent_config.jules_command
        )
        self.timeout = (
            config.get("jules_timeout")
            if config
            else agent_config.jules_timeout
        )
        self.working_dir = (
            config.get("jules_working_dir")
            if config
            else agent_config.jules_working_dir
        )

        # Verify jules is available
        if not self._check_jules_available():
            logger.warning("Jules command not found, some operations may fail")

    def _check_jules_available(self) -> bool:
        """
        Check if jules command is available.

        Returns:
            True if jules is available
        """
        try:
            result = subprocess.run(
                [self.jules_command, "help"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def _execute_impl(self, request: AgentRequest) -> AgentResponse:
        """
        Execute Jules command.

        Args:
            request: Agent request

        Returns:
            Agent response
        """
        start_time = time.time()

        try:
            # Parse request to determine jules command
            prompt = request.prompt
            context = request.context or {}

            # Build jules command
            jules_args = self._build_jules_args(prompt, context)

            # Execute jules command
            result = self._execute_jules_command(jules_args)

            execution_time = time.time() - start_time

            # Determine if operation was successful
            # Jules may return non-zero but still produce useful output
            output = result.get("output", "")
            exit_code = result.get("exit_code", 0)
            stderr_output = result.get("stderr", "")
            success = result.get("success", exit_code == 0)

            error = None
            if not success and stderr_output:
                error = stderr_output
            elif not success and not output:
                error = f"Jules command failed with exit code {exit_code}"

            return AgentResponse(
                content=output,
                error=error,
                metadata={
                    "command": " ".join([self.jules_command] + jules_args),
                    "exit_code": exit_code,
                    "stdout": result.get("stdout", ""),
                    "stderr": stderr_output,
                    "jules_success": success,
                },
                execution_time=execution_time,
            )

        except subprocess.TimeoutExpired as e:
            execution_time = time.time() - start_time
            error_msg = f"Jules command timed out after {self.timeout}s"
            return AgentResponse(
                content="",
                error=error_msg,
                metadata={
                    "command": " ".join([self.jules_command] + jules_args),
                    "timeout": self.timeout,
                },
                execution_time=execution_time,
            )
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Jules command failed: {str(e)}"
            return AgentResponse(
                content="",
                error=error_msg,
                metadata={
                    "command": " ".join([self.jules_command] + jules_args),
                    "exception": str(e),
                },
                execution_time=execution_time,
            )

    def _stream_impl(self, request: AgentRequest) -> Iterator[str]:
        """
        Stream Jules command output.

        Note: Jules CLI is primarily TUI-based. For streaming, we execute
        the command and stream its output. For interactive TUI mode,
        users should use Jules CLI directly.

        Args:
            request: Agent request

        Yields:
            Chunks of output
        """
        prompt = request.prompt
        context = request.context or {}

        jules_args = self._build_jules_args(prompt, context)

        try:
            process = subprocess.Popen(
                [self.jules_command] + jules_args,
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
            logger.error(f"Error streaming Jules output: {e}", exc_info=True)
            yield f"Error: {str(e)}"

    def _build_jules_args(self, prompt: str, context: dict[str, Any]) -> list[str]:
        """
        Build jules command arguments from prompt and context.

        Jules CLI uses task-based commands. For code generation/editing tasks,
        we use 'jules new' to create a session with the task description.

        Args:
            prompt: User prompt (task description)
            context: Additional context (may include repo, parallel, etc.)

        Returns:
            List of command arguments
        """
        args = ["new"]

        # Add repository if specified in context
        if "repo" in context:
            args.extend(["--repo", str(context["repo"])])

        # Add parallel sessions if specified
        if "parallel" in context:
            args.extend(["--parallel", str(context["parallel"])])

        # Add prompt as task description
        args.append(prompt)

        return args

    def _execute_jules_command(self, args: list[str]) -> dict[str, Any]:
        """
        Execute jules command and return result.

        Args:
            args: Command arguments

        Returns:
            Command result dictionary
        """
        try:
            result = subprocess.run(
                [self.jules_command] + args,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=self.working_dir,
            )

            # Jules CLI may return non-zero for some operations but still produce output
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
            raise JulesError(
                "Jules command timed out",
                command=" ".join([self.jules_command] + args),
            )
        except FileNotFoundError:
            raise JulesError(
                f"Jules command not found: {self.jules_command}",
                command=self.jules_command,
            )

    def get_jules_help(self) -> dict[str, Any]:
        """
        Get jules help information.

        Returns:
            Help information dictionary
        """
        try:
            result = subprocess.run(
                [self.jules_command, "help"],
                capture_output=True,
                text=True,
                timeout=5,
            )

            return {
                "help_text": result.stdout,
                "exit_code": result.returncode,
                "available": result.returncode == 0,
            }
        except Exception as e:
            return {
                "help_text": "",
                "exit_code": -1,
                "available": False,
                "error": str(e),
            }

    def execute_jules_command(
        self, command: str, args: Optional[list[str]] = None
    ) -> dict[str, Any]:
        """
        Execute a jules command.

        Args:
            command: Jules command name
            args: Optional command arguments

        Returns:
            Command result dictionary
        """
        jules_args = [command]
        if args:
            jules_args.extend(args)

        return self._execute_jules_command(jules_args)

