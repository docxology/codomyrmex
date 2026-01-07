"""Gemini CLI client wrapper."""

import os
from pathlib import Path
from typing import Any, Iterator, Optional

from codomyrmex.agents.config import get_config
from codomyrmex.agents.core import (
    AgentCapabilities,
    AgentRequest,
    AgentResponse,
)
from codomyrmex.agents.exceptions import AgentError, AgentTimeoutError, GeminiError
from codomyrmex.agents.generic import CLIAgentBase


class GeminiClient(CLIAgentBase):
    """Client for interacting with Gemini CLI tool."""

    def __init__(self, config: Optional[dict[str, Any]] = None):
        """
        Initialize Gemini client.

        Args:
            config: Optional configuration override
        """
        agent_config = get_config()
        gemini_command = (
            config.get("gemini_command") if config else agent_config.gemini_command
        )
        timeout = (
            config.get("gemini_timeout") if config else agent_config.gemini_timeout
        )
        working_dir = (
            Path(config.get("gemini_working_dir"))
            if config and config.get("gemini_working_dir")
            else Path(agent_config.gemini_working_dir)
            if agent_config.gemini_working_dir
            else None
        )

        # Set up environment variables
        env_vars = {}
        api_key = (
            config.get("gemini_api_key") if config else agent_config.gemini_api_key
        )
        auth_method = (
            config.get("gemini_auth_method")
            if config
            else agent_config.gemini_auth_method
        )
        if api_key and auth_method == "api_key":
            env_vars["GEMINI_API_KEY"] = api_key

        super().__init__(
            name="gemini",
            command=gemini_command,
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
        self.auth_method = auth_method
        self.settings_path = (
            config.get("gemini_settings_path")
            if config
            else agent_config.gemini_settings_path
        )
        self.enable_shell_commands = (
            config.get("gemini_enable_shell_commands", False) if config else False
        )

        # Verify gemini is available
        if not self._check_command_available(check_args=["--help"]):
            self.logger.warning(
                "Gemini command not found, some operations may fail",
                extra={"command": self.command},
            )

    def _execute_impl(self, request: AgentRequest) -> AgentResponse:
        """
        Execute Gemini command.

        Args:
            request: Agent request

        Returns:
            Agent response
        """
        prompt = request.prompt
        context = request.context or {}

        # Build gemini command input
        gemini_input = self._build_gemini_input(prompt, context)

        try:
            # Execute gemini command using base class method
            result = self._execute_command(input_text=gemini_input)

            # Build response using base class helper
            return self._build_response_from_result(
                result,
                request,
                additional_metadata={
                    "gemini_success": result.get("success", False),
                    "input_preview": gemini_input[:200] if len(gemini_input) > 200 else gemini_input,
                },
            )

        except AgentTimeoutError as e:
            # Convert timeout to GeminiError
            raise GeminiError(
                f"Gemini command timed out: {str(e)}",
                command=self.command,
            ) from e
        except AgentError as e:
            # Convert base agent error to GeminiError
            raise GeminiError(
                f"Gemini command failed: {str(e)}",
                command=self.command,
            ) from e
        except Exception as e:
            # Convert any other exception to GeminiError
            self.logger.error(
                f"Gemini execution failed: {e}",
                exc_info=True,
                extra={"command": self.command, "error": str(e)},
            )
            raise GeminiError(f"Gemini command failed: {str(e)}", command=self.command) from e

    def _stream_impl(self, request: AgentRequest) -> Iterator[str]:
        """
        Stream Gemini command output.

        Args:
            request: Agent request

        Yields:
            Chunks of output
        """
        prompt = request.prompt
        context = request.context or {}

        gemini_input = self._build_gemini_input(prompt, context)

        # Use base class streaming method
        yield from self._stream_command(input_text=gemini_input)

    def _build_gemini_input(self, prompt: str, context: dict[str, Any]) -> str:
        """
        Build gemini command input from prompt and context.

        Args:
            prompt: User prompt
            context: Additional context (may include files, commands, etc.)

        Returns:
            Formatted input string for Gemini CLI
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

        # Handle ! commands (shell execution) - only if enabled
        if "!" in prompt and not self.enable_shell_commands:
            self.logger.warning(
                "Shell commands (!) are disabled. Enable via config to use.",
                extra={"agent": "gemini"},
            )
            # Remove ! commands or replace with comment
            input_parts = [p.replace("!", "# ") if p.strip().startswith("!") else p for p in input_parts]

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


    def execute_gemini_command(
        self, command: str, args: Optional[list[str]] = None, input_text: Optional[str] = None
    ) -> dict[str, Any]:
        """
        Execute a gemini slash command.

        Args:
            command: Gemini command name (e.g., "/model", "/settings")
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

    def get_gemini_help(self) -> dict[str, Any]:
        """
        Get gemini help information.

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
                f"Failed to get Gemini help: {e}",
                extra={"command": self.command, "error": str(e)},
            )
            return {
                "help_text": "",
                "exit_code": -1,
                "available": False,
                "error": str(e),
            }

    def save_chat(self, tag: str, prompt: Optional[str] = None) -> dict[str, Any]:
        """
        Save current chat session.

        Args:
            tag: Tag for identifying the conversation
            prompt: Optional prompt to save

        Returns:
            Save result dictionary
        """
        cmd = f"/chat save {tag}"
        if prompt:
            cmd += f"\n{prompt}"

        return self.execute_gemini_command("/chat", ["save", tag], prompt)

    def resume_chat(self, tag: str) -> dict[str, Any]:
        """
        Resume a saved chat session.

        Args:
            tag: Tag of the conversation to resume

        Returns:
            Resume result dictionary
        """
        return self.execute_gemini_command("/chat", ["resume", tag])

    def list_chats(self) -> dict[str, Any]:
        """
        List available chat sessions.

        Returns:
            List of available chats
        """
        return self.execute_gemini_command("/chat", ["list"])

