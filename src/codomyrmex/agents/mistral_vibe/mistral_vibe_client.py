from collections.abc import Iterator
from pathlib import Path
from typing import Any

from codomyrmex.agents.core import (
    AgentCapabilities,
    AgentRequest,
    AgentResponse,
)
from codomyrmex.agents.core.exceptions import (
    AgentError,
    AgentTimeoutError,
    MistralVibeError,
)
from codomyrmex.agents.generic import CLIAgentBase


class MistralVibeClient(CLIAgentBase):
    """Client for interacting with Mistral Vibe CLI tool."""

    def __init__(self, config: dict[str, Any] | None = None):
        """
        Initialize Mistral Vibe client.

        Args:
            config: Optional configuration override
        """
        super().__init__(
            name="mistral_vibe",
            command="vibe",
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
            env_vars={},
        )

        vibe_command = self.get_config_value("mistral_vibe_command", config=config)
        timeout = self.get_config_value("mistral_vibe_timeout", config=config)
        working_dir_str = self.get_config_value("mistral_vibe_working_dir", config=config)
        working_dir = Path(working_dir_str) if working_dir_str else None

        api_key = self.get_config_value("mistral_vibe_api_key", config=config)
        if api_key:
            self.env_vars["MISTRAL_API_KEY"] = api_key

        self.command = vibe_command
        self.timeout = timeout
        self.working_dir = working_dir
        self.api_key = api_key

        # Verify vibe is available
        if not self._check_command_available(check_args=["--help"]):
            self.logger.warning(
                "Mistral Vibe command not found, some operations may fail",
                extra={"command": self.command},
            )

    def _execute_impl(self, request: AgentRequest) -> AgentResponse:
        """Execute Mistral Vibe command."""
        prompt = request.prompt
        context = request.context or {}
        vibe_input = self._build_vibe_input(prompt, context)

        try:
            result = self._execute_command(input_text=vibe_input)
            return self._build_response_from_result(
                result,
                request,
                additional_metadata={
                    "vibe_success": result.get("success", False),
                    "input_preview": vibe_input[:200] if len(vibe_input) > 200 else vibe_input,
                },
            )
        except AgentTimeoutError as e:
            raise MistralVibeError(f"Mistral Vibe command timed out: {str(e)}", command=self.command) from e
        except AgentError as e:
            raise MistralVibeError(f"Mistral Vibe command failed: {str(e)}", command=self.command) from e
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            self.logger.error(f"Mistral Vibe execution failed: {e}", exc_info=True)
            raise MistralVibeError(f"Mistral Vibe command failed: {str(e)}", command=self.command) from e

    def _stream_impl(self, request: AgentRequest) -> Iterator[str]:
        """Stream Mistral Vibe command output."""
        prompt = request.prompt
        context = request.context or {}
        vibe_input = self._build_vibe_input(prompt, context)
        yield from self._stream_command(input_text=vibe_input)

    def _build_vibe_input(self, prompt: str, context: dict[str, Any]) -> str:
        """Build vibe command input from prompt and context."""
        input_parts = [prompt]

        if "files" in context:
            for file_path in context["files"]:
                if Path(file_path).exists():
                    input_parts.insert(0, f"@{file_path}\n")

        if "directories" in context:
            for dir_path in context["directories"]:
                if Path(dir_path).is_dir():
                    input_parts.insert(0, f"@directory {dir_path}\n")

        return "\n".join(input_parts)

    def execute_vibe_command(
        self, command: str, args: list[str] | None = None, input_text: str | None = None
    ) -> dict[str, Any]:
        """Execute a vibe command."""
        cmd_input = command
        if args:
            cmd_input += " " + " ".join(args)
        if input_text:
            cmd_input += "\n" + input_text
        return self._execute_command(input_text=cmd_input)

    def get_vibe_help(self) -> dict[str, Any]:
        """Get vibe help information."""
        try:
            result = self._execute_command(args=["--help"], timeout=5)
            return {
                "help_text": result.get("stdout", "") or result.get("stderr", ""),
                "exit_code": result.get("exit_code", 0),
                "available": result.get("success", False),
            }
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            self.logger.warning(f"Failed to get Mistral Vibe help: {e}")
            return {"help_text": "", "exit_code": -1, "available": False, "error": str(e)}
