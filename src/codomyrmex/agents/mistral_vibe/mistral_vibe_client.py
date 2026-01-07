"""Mistral Vibe CLI client wrapper."""

from pathlib import Path
from typing import Any, Iterator, Optional

from codomyrmex.agents.config import get_config
from codomyrmex.agents.core import (
    AgentCapabilities,
    AgentRequest,
    AgentResponse,
)
from codomyrmex.agents.exceptions import AgentError, AgentTimeoutError, MistralVibeError
from codomyrmex.agents.generic import CLIAgentBase


class MistralVibeClient(CLIAgentBase):
    """Client for interacting with Mistral Vibe CLI tool."""

    def __init__(self, config: Optional[dict[str, Any]] = None):
        """
        Initialize Mistral Vibe client.

        Args:
            config: Optional configuration override
        """
        agent_config = get_config()
        vibe_command = (
            config.get("mistral_vibe_command")
            if config
            else agent_config.mistral_vibe_command
        )
        timeout = (
            config.get("mistral_vibe_timeout")
            if config
            else agent_config.mistral_vibe_timeout
        )
        working_dir = (
            Path(config.get("mistral_vibe_working_dir"))
            if config and config.get("mistral_vibe_working_dir")
            else Path(agent_config.mistral_vibe_working_dir)
            if agent_config.mistral_vibe_working_dir
            else None
        )

        # Set up environment variables
        env_vars = {}
        api_key = (
            config.get("mistral_vibe_api_key")
            if config
            else agent_config.mistral_vibe_api_key
        )
        if api_key:
            env_vars["MISTRAL_API_KEY"] = api_key

        super().__init__(
            name="mistral_vibe",
            command=vibe_command,
            capabilities=[
                AgentCapabilities.CODE_GENERATION,
                AgentCapabilities.CODE_EDITING,
                AgentCapabilities.CODE_ANALYSIS,
                AgentCapabilities.TEXT_COMPLETION,
                AgentCapabilities.STREAMING,
                AgentCapabilities.MULTI_TURN,
            ],
            config=config or {},
            timeout=timeout,
            working_dir=working_dir,
            env_vars=env_vars,
        )

        self.api_key = api_key

        # Verify vibe is available
        if not self._check_command_available(check_args=["--help"]):
            self.logger.warning(
                "Mistral Vibe command not found, some operations may fail",
                extra={"command": self.command},
            )

    def _execute_impl(self, request: AgentRequest) -> AgentResponse:
        """
        Execute Mistral Vibe command.

        Args:
            request: Agent request

        Returns:
            Agent response
        """
        prompt = request.prompt
        context = request.context or {}

        # Build vibe command input
        vibe_input = self._build_vibe_input(prompt, context)

        try:
            # Execute vibe command using base class method
            result = self._execute_command(input_text=vibe_input)

            # Build response using base class helper
            return self._build_response_from_result(
                result,
                request,
                additional_metadata={
                    "vibe_success": result.get("success", False),
                    "input_preview": vibe_input[:200] if len(vibe_input) > 200 else vibe_input,
                },
            )

        except AgentTimeoutError as e:
            # Convert timeout to MistralVibeError
            raise MistralVibeError(
                f"Mistral Vibe command timed out: {str(e)}",
                command=self.command,
            ) from e
        except AgentError as e:
            # Convert base agent error to MistralVibeError
            raise MistralVibeError(
                f"Mistral Vibe command failed: {str(e)}",
                command=self.command,
            ) from e
        except Exception as e:
            # Convert any other exception to MistralVibeError
            self.logger.error(
                f"Mistral Vibe execution failed: {e}",
                exc_info=True,
                extra={"command": self.command, "error": str(e)},
            )
            raise MistralVibeError(f"Mistral Vibe command failed: {str(e)}", command=self.command) from e

    def _stream_impl(self, request: AgentRequest) -> Iterator[str]:
        """
        Stream Mistral Vibe command output.

        Args:
            request: Agent request

        Yields:
            Chunks of output
        """
        prompt = request.prompt
        context = request.context or {}

        vibe_input = self._build_vibe_input(prompt, context)

        # Use base class streaming method
        yield from self._stream_command(input_text=vibe_input)

    def _build_vibe_input(self, prompt: str, context: dict[str, Any]) -> str:
        """
        Build vibe command input from prompt and context.

        Args:
            prompt: User prompt
            context: Additional context (may include files, directories, etc.)

        Returns:
            Formatted input string for Mistral Vibe CLI
        """
        # Handle different input types
        input_parts = []

        # Handle @ commands (file inclusion)
        if "@" in prompt:
            # Extract @ commands and validate file paths
            parts = prompt.split("@")
            for i, part in enumerate(parts):
                if i == 0:
                    input_parts.append(part)
                else:
                    # Extract file path from @command
                    file_part = part.split()[0] if part.split() else ""
                    if file_part and Path(file_part).exists():
                        input_parts.append(f"@{file_part}")
                        input_parts.append(part[len(file_part):].lstrip())
                    else:
                        input_parts.append(f"@{part}")
        else:
            input_parts.append(prompt)

        # Handle context parameters
        if "files" in context:
            for file_path in context["files"]:
                if Path(file_path).exists():
                    input_parts.insert(0, f"@{file_path}\n")

        if "directories" in context:
            for dir_path in context["directories"]:
                if Path(dir_path).is_dir():
                    input_parts.insert(0, f"@directory {dir_path}\n")

        # Join all parts
        return "\n".join(input_parts)


    def execute_vibe_command(
        self, command: str, args: Optional[list[str]] = None, input_text: Optional[str] = None
    ) -> dict[str, Any]:
        """
        Execute a vibe command.

        Args:
            command: Vibe command name
            args: Optional command arguments
            input_text: Optional input text to send

        Returns:
            Command result dictionary
        """
        # Build command input
        cmd_input = command
        if args:
            cmd_input += " " + " ".join(args)
        if input_text:
            cmd_input += "\n" + input_text

        return self._execute_command(input_text=cmd_input)

    def get_vibe_help(self) -> dict[str, Any]:
        """
        Get vibe help information.

        Returns:
            Help information dictionary
        """
        try:
            result = self._execute_command(args=["--help"], timeout=5)
            return {
                "help_text": result.get("stdout", "") or result.get("stderr", ""),
                "exit_code": result.get("exit_code", 0),
                "available": result.get("success", False),
            }
        except Exception as e:
            self.logger.warning(
                f"Failed to get Mistral Vibe help: {e}",
                extra={"command": self.command, "error": str(e)},
            )
            return {
                "help_text": "",
                "exit_code": -1,
                "available": False,
                "error": str(e),
            }

