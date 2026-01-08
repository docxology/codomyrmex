from pathlib import Path
from typing import Any, Iterator, Optional
import json

from codomyrmex.agents.config import get_config
from codomyrmex.agents.core import (
from codomyrmex.logging_monitoring import get_logger

























"""
    AgentCapabilities,
    AgentRequest,
    AgentResponse,
)









"""Jules CLI client wrapper."""


class JulesClient(CLIAgentBase):
    """Client for interacting with Jules CLI tool."""

    def __init__(self, config: Optional[dict[str, Any]] = None):
        """
        Initialize Jules client.

        Args:
            config: Optional configuration override
        """
        super().__init__(
            name="jules",
            command="jules",
            capabilities=[
                AgentCapabilities.CODE_GENERATION,
                AgentCapabilities.CODE_EDITING,
                AgentCapabilities.CODE_ANALYSIS,
                AgentCapabilities.TEXT_COMPLETION,
                AgentCapabilities.STREAMING,
            ],
            config=config or {},
            timeout=30,
            working_dir=None,
        )
        
        jules_command = self.get_config_value("jules_command", config=config)
        timeout = self.get_config_value("jules_timeout", config=config)
        working_dir_str = self.get_config_value("jules_working_dir", config=config)
        working_dir = Path(working_dir_str) if working_dir_str else None

        self.command = jules_command
        self.timeout = timeout
        self.working_dir = working_dir

        # Verify jules is available
        if not self._check_command_available(check_args=["help"]):
            self.logger.warning(
                "Jules command not found, some operations may fail",
                extra={"command": self.command},
            )

    def _execute_impl(self, request: AgentRequest) -> AgentResponse:
        """
        Execute Jules command.

        Args:
            request: Agent request

        Returns:
            Agent response
        """
        prompt = request.prompt
        context = request.context or {}

        # Build jules command arguments
        jules_args = self._build_jules_args(prompt, context)

        try:
            # Execute jules command using base class method
            result = self._execute_command(args=jules_args)

            # Build response using base class helper
            return self._build_response_from_result(
                result,
                request,
                additional_metadata={
                    "jules_success": result.get("success", False),
                    "command_full": " ".join([self.command] + jules_args),
                },
            )

        except AgentTimeoutError as e:
            # Convert timeout to JulesError
            raise JulesError(
                f"Jules command timed out: {str(e)}",
                command=self.command,
            ) from e
        except AgentError as e:
            # Convert base agent error to JulesError
            raise JulesError(
                f"Jules command failed: {str(e)}",
                command=self.command,
            ) from e
        except Exception as e:
            # Convert any other exception to JulesError
            self.logger.error(
                f"Jules execution failed: {e}",
                exc_info=True,
                extra={"command": self.command, "args": jules_args, "error": str(e)},
            )
            raise JulesError(f"Jules command failed: {str(e)}", command=self.command) from e

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

        # Use base class streaming method
        yield from self._stream_command(args=jules_args)

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


    def get_jules_help(self) -> dict[str, Any]:
        """
        Get jules help information.

        Returns:
            Help information dictionary
        """
        try:
            result = self._execute_command(args=["help"], timeout=5)
            return {
                "help_text": result.get("stdout", ""),
                "exit_code": result.get("exit_code", 0),
                "available": result.get("success", False),
            }
        except Exception as e:
            self.logger.warning(
                f"Failed to get Jules help: {e}",
                extra={"command": self.command, "error": str(e)},
            )
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

        return self._execute_command(args=jules_args)
