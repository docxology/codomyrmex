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
                AgentCapabilities.TEXT_COMPLETION,
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

            return AgentResponse(
                content=result.get("output", ""),
                metadata={
                    "command": " ".join([self.jules_command] + jules_args),
                    "exit_code": result.get("exit_code", 0),
                    "stdout": result.get("stdout", ""),
                    "stderr": result.get("stderr", ""),
                },
                execution_time=execution_time,
            )

        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            raise JulesError(
                "Jules command timed out",
                command=" ".join([self.jules_command] + jules_args),
                timeout=self.timeout,
            )
        except Exception as e:
            execution_time = time.time() - start_time
            raise JulesError(
                f"Jules command failed: {str(e)}",
                command=" ".join([self.jules_command] + jules_args),
            ) from e

    def _stream_impl(self, request: AgentRequest) -> Iterator[str]:
        """
        Stream Jules command output.

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
            )

            # Stream stdout
            for line in process.stdout:
                yield line.rstrip()

            process.wait()

            if process.returncode != 0:
                stderr = process.stderr.read()
                yield f"Error: {stderr}"

        except Exception as e:
            yield f"Error: {str(e)}"

    def _build_jules_args(self, prompt: str, context: dict[str, Any]) -> list[str]:
        """
        Build jules command arguments from prompt and context.

        Args:
            prompt: User prompt
            context: Additional context

        Returns:
            List of command arguments
        """
        args = []

        # Add context as JSON if provided
        if context:
            context_json = json.dumps(context)
            args.extend(["--context", context_json])

        # Add prompt
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

            return {
                "output": result.stdout,
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }
        except subprocess.TimeoutExpired:
            raise JulesError(
                "Jules command timed out",
                command=" ".join([self.jules_command] + args),
                timeout=self.timeout,
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

