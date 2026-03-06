"""Hermes CLI agent client for Codomyrmex.

Wraps the NousResearch Hermes Agent CLI (``hermes``) for chat completion,
tool-calling pipelines, and skills management.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

from codomyrmex.agents.core import (
    AgentCapabilities,
    AgentRequest,
    AgentResponse,
)
from codomyrmex.agents.core.exceptions import AgentError, AgentTimeoutError
from codomyrmex.agents.generic import CLIAgentBase

if TYPE_CHECKING:
    from collections.abc import Iterator


class HermesError(AgentError):
    """Exception raised when Hermes CLI execution fails."""

    def __init__(self, message: str, command: str | None = None) -> None:
        super().__init__(message)
        self.command = command


class HermesClient(CLIAgentBase):
    """Client for interacting with the Hermes Agent CLI tool.

    Wraps the `hermes` CLI for single-turn chat, task execution,
    and agent skills management.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """
        Initialize Hermes client.

        Args:
            config: Optional configuration override. Recognised keys:
                ``hermes_command`` (str, default ``"hermes"``),
                ``hermes_timeout`` (int, default 120),
                ``hermes_working_dir`` (str | None).
        """
        super().__init__(
            name="hermes",
            command="hermes",
            capabilities=[
                AgentCapabilities.CODE_GENERATION,
                AgentCapabilities.CODE_EDITING,
                AgentCapabilities.TEXT_COMPLETION,
                AgentCapabilities.STREAMING,
            ],
            config=config or {},
            timeout=120,
            working_dir=None,
        )

        hermes_command = self.get_config_value("hermes_command", config=config)
        timeout = self.get_config_value("hermes_timeout", config=config)
        working_dir_str = self.get_config_value("hermes_working_dir", config=config)

        if hermes_command:
            self.command = hermes_command
        if timeout is not None:
            self.timeout = timeout
        if working_dir_str:
            self.working_dir = Path(working_dir_str)

        if not self._check_command_available(check_args=["version"]):
            self.logger.warning(
                "Hermes command not found, operations will fail. "
                "Ensure hermes-agent is installed and in PATH.",
                extra={"command": self.command},
            )

    def _execute_impl(self, request: AgentRequest) -> AgentResponse:
        """Execute Hermes command for a prompt."""
        prompt = request.prompt
        context = request.context or {}

        # Determine if we are running a specialized command or a general chat query
        hermes_args = self._build_hermes_args(prompt, context)

        try:
            result = self._execute_command(args=hermes_args)

            if not result.get("success", False):
                raise HermesError(
                    f"Hermes execution failed with exit code {result.get('exit_code')}:\n"
                    f"{result.get('stderr') or result.get('stdout')}",
                    command=self.command,
                )

            return self._build_response_from_result(
                result,
                request,
                additional_metadata={
                    "command_full": " ".join([self.command, *hermes_args]),
                },
            )

        except AgentTimeoutError as e:
            raise HermesError(
                f"Hermes command timed out after {self.timeout}s: {e}",
                command=self.command,
            ) from e
        except AgentError as e:
            raise HermesError(
                f"Hermes command failed: {e}", command=self.command
            ) from e
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            self.logger.error(f"Hermes execution failed: {e}", exc_info=True)
            raise HermesError(
                f"Hermes command failed: {e}", command=self.command
            ) from e

    def _stream_impl(self, request: AgentRequest) -> Iterator[str]:
        """Stream Hermes command output."""
        prompt = request.prompt
        context = request.context or {}
        hermes_args = self._build_hermes_args(prompt, context)
        yield from self._stream_command(args=hermes_args)

    def _build_hermes_args(self, prompt: str, context: dict[str, Any]) -> list[str]:
        """Build hermes command arguments from prompt and context.

        Args:
            prompt: Text prompt or task description.
            context: Context dictionary which may include keys:
                - `command`: Specific subcommand bypassing chat (e.g. `skills`, `setup`)
                - `args`: List of args for the subcommand

        Returns:
            Argument list suitable for subprocess call.
        """
        # Direct subcommand passthrough for skills management or diagnostics
        if context.get("command"):
            cmd = context["command"]
            args = [cmd]
            if context.get("args"):
                args.extend(context["args"])
            return args

        # Default action: single-turn chat using `-q`
        return ["chat", "-q", prompt]

    def list_skills(self) -> dict[str, Any]:
        """List active skills available to Hermes.

        Returns:
            A dictionary of parsed skill data or raw stdout if parsing fails.
        """
        try:
            # Assumes `hermes skills list` returns output.
            result = self._execute_command(args=["skills", "list"])
            return {
                "success": result.get("success", False),
                "output": result.get("stdout", ""),
            }
        except Exception as e:
            self.logger.warning(f"Failed to list Hermes skills: {e}")
            return {
                "success": False,
                "error": str(e),
            }

    def get_hermes_status(self) -> dict[str, Any]:
        """Get the current Hermes configuration status.

        Returns:
            dict with diagnostic information.
        """
        try:
            result = self._execute_command(args=["status"], timeout=10)
            return {
                "success": result.get("success", False),
                "output": result.get("stdout", ""),
                "exit_code": result.get("exit_code", 0),
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "exit_code": -1,
            }
