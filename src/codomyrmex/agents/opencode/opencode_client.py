from pathlib import Path
from typing import Any, Iterator, Optional

from codomyrmex.agents.config import get_config
from codomyrmex.agents.core import (
from codomyrmex.agents.exceptions import AgentError, AgentTimeoutError, OpenCodeError
from codomyrmex.agents.generic import CLIAgentBase














"""OpenCode CLI client wrapper."""


    AgentCapabilities,
    AgentRequest,
    AgentResponse,
)


class OpenCodeClient(CLIAgentBase):
    """Client for interacting with OpenCode CLI tool."""

    def __init__(self, config: Optional[dict[str, Any]] = None):
        """
        Initialize OpenCode client.

        Args:
            config: Optional configuration override
        """
        super().__init__(
            name="opencode",
            command="opencode",
            capabilities=[
                AgentCapabilities.CODE_GENERATION,
                AgentCapabilities.CODE_EDITING,
                AgentCapabilities.CODE_ANALYSIS,
                AgentCapabilities.TEXT_COMPLETION,
                AgentCapabilities.STREAMING,
                AgentCapabilities.MULTI_TURN,
            ],
            config=config or {},
            timeout=60,
            working_dir=None,
        )
        
        opencode_command = self.get_config_value("opencode_command", config=config)
        timeout = self.get_config_value("opencode_timeout", config=config)
        working_dir_str = self.get_config_value("opencode_working_dir", config=config)
        working_dir = Path(working_dir_str) if working_dir_str else None

        self.command = opencode_command
        self.timeout = timeout
        self.working_dir = working_dir
        self.api_key = self.get_config_value("opencode_api_key", config=config)

        # Verify opencode is available
        if not self._check_command_available(check_args=["--version"]):
            self.logger.warning(
                "OpenCode command not found, some operations may fail",
                extra={"command": self.command},
            )

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
        prompt = request.prompt
        context = request.context or {}

        # Build opencode command arguments
        opencode_args = self._build_opencode_args(prompt, context)

        try:
            # Execute opencode command using base class method
            result = self._execute_command(args=opencode_args)

            # Build response using base class helper
            return self._build_response_from_result(
                result,
                request,
                additional_metadata={
                    "opencode_success": result.get("success", False),
                    "command_full": " ".join([self.command] + opencode_args),
                },
            )

        except AgentTimeoutError as e:
            # Convert timeout to OpenCodeError
            raise OpenCodeError(
                f"OpenCode command timed out: {str(e)}",
                command=self.command,
            ) from e
        except AgentError as e:
            # Convert base agent error to OpenCodeError
            raise OpenCodeError(
                f"OpenCode command failed: {str(e)}",
                command=self.command,
            ) from e
        except Exception as e:
            # Convert any other exception to OpenCodeError
            self.logger.error(
                f"OpenCode execution failed: {e}",
                exc_info=True,
                extra={"command": self.command, "args": opencode_args, "error": str(e)},
            )
            raise OpenCodeError(f"OpenCode command failed: {str(e)}", command=self.command) from e

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

        # Use base class streaming method
        yield from self._stream_command(args=opencode_args)

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
        working_path = project_path or (self.working_dir if self.working_dir else Path.cwd())

        try:
            result = self._execute_command(args=["--init"], cwd=working_path)
            return {
                "success": result.get("success", False),
                "output": result.get("stdout", ""),
                "error": result.get("stderr") if not result.get("success") else None,
                "exit_code": result.get("exit_code", 0),
            }
        except Exception as e:
            self.logger.error(
                f"Failed to initialize OpenCode project: {e}",
                exc_info=True,
                extra={"command": self.command, "project_path": str(working_path)},
            )
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
            result = self._execute_command(args=["--version"], timeout=5)
            return {
                "version": result.get("stdout", "").strip(),
                "exit_code": result.get("exit_code", 0),
                "available": result.get("success", False),
            }
        except Exception as e:
            self.logger.warning(
                f"Failed to get OpenCode version: {e}",
                extra={"command": self.command, "error": str(e)},
            )
            return {
                "version": "",
                "exit_code": -1,
                "available": False,
                "error": str(e),
            }

