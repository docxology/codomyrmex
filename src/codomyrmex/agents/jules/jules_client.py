from pathlib import Path
from typing import Any
from collections.abc import Iterator

from codomyrmex.agents.core import (
    AgentCapabilities,
    AgentRequest,
    AgentResponse,
)
from codomyrmex.agents.core.exceptions import AgentError, AgentTimeoutError, JulesError
from codomyrmex.agents.generic import CLIAgentBase


class JulesClient(CLIAgentBase):
    """Client for interacting with Jules CLI tool."""

    def __init__(self, config: dict[str, Any] | None = None):
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
        """Execute Jules command."""
        prompt = request.prompt
        context = request.context or {}
        jules_args = self._build_jules_args(prompt, context)

        retries = 3
        last_error = None

        for attempt in range(retries):
            try:
                result = self._execute_command(args=jules_args)

                # Check for auth errors in output
                stdout = result.get("stdout", "")
                stderr = result.get("stderr", "")
                if any(x in stdout.lower() or x in stderr.lower() for x in ["unauthorized", "unauthenticated", "401"]):
                    raise JulesError("Jules authentication failed. Please run 'jules auth login'.", command=self.command)

                return self._build_response_from_result(
                    result,
                    request,
                    additional_metadata={
                        "jules_success": result.get("success", False),
                        "command_full": " ".join([self.command] + jules_args),
                        "attempt": attempt + 1,
                    },
                )
            except AgentTimeoutError as e:
                # Timeouts might be transient
                last_error = e
                if attempt < retries - 1:
                    continue
                raise JulesError(f"Jules command timed out after {retries} attempts: {str(e)}", command=self.command) from e
            except AgentError as e:
                # Other agent errors
                raise JulesError(f"Jules command failed: {str(e)}", command=self.command) from e
            except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
                self.logger.error(f"Jules execution failed: {e}", exc_info=True)
                raise JulesError(f"Jules command failed: {str(e)}", command=self.command) from e

    def _stream_impl(self, request: AgentRequest) -> Iterator[str]:
        """Stream Jules command output."""
        prompt = request.prompt
        context = request.context or {}
        jules_args = self._build_jules_args(prompt, context)
        yield from self._stream_command(args=jules_args)

    def _build_jules_args(self, prompt: str, context: dict[str, Any]) -> list[str]:
        """Build jules command arguments from prompt and context."""

        # Check for direct commands
        if context.get("command"):
            cmd = context["command"]
            if cmd in ["auth", "config", "login", "logout"]:
                 args = [cmd]
                 if context.get("args"):
                     args.extend(context["args"])
                 return args

        args = ["new"]

        if "repo" in context:
            args.extend(["--repo", str(context["repo"])])

        if "parallel" in context:
            args.extend(["--parallel", str(context["parallel"])])

        args.append(prompt)
        return args

    def get_jules_help(self) -> dict[str, Any]:
        """Get jules help information."""
        try:
            result = self._execute_command(args=["help"], timeout=5)
            return {
                "help_text": result.get("stdout", ""),
                "exit_code": result.get("exit_code", 0),
                "available": result.get("success", False),
            }
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            self.logger.warning(f"Failed to get Jules help: {e}")
            return {"help_text": "", "exit_code": -1, "available": False, "error": str(e)}

    def execute_jules_command(self, command: str, args: list[str] | None = None, config_path: Path | None = None) -> dict[str, Any]:
        """
        Execute a jules command.

        Args:
            command: The jules subcommand (e.g., 'auth', 'config').
            args: Additional arguments.
            config_path: Path to a custom config file to use with --config.
        """
        jules_args = [command]

        if config_path:
            jules_args.extend(["--config", str(config_path)])

        if args:
            jules_args.extend(args)

        return self._execute_command(args=jules_args)
