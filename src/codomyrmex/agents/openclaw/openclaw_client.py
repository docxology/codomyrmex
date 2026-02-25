from pathlib import Path
from typing import Any
from collections.abc import Iterator

from codomyrmex.agents.core import (
    AgentCapabilities,
    AgentRequest,
    AgentResponse,
)
from codomyrmex.agents.core.exceptions import (
    AgentError,
    AgentTimeoutError,
    OpenClawError,
)
from codomyrmex.agents.generic import CLIAgentBase


class OpenClawClient(CLIAgentBase):
    """Client for interacting with OpenClaw CLI tool.

    OpenClaw is an autonomous AI agent framework with multi-channel messaging
    (WhatsApp, Telegram, Slack, Discord, Signal, etc.), a Gateway/WebSocket
    architecture, and LLM-agnostic support.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """
        Initialize OpenClaw client.

        Args:
            config: Optional configuration override
        """
        super().__init__(
            name="openclaw",
            command="openclaw",
            capabilities=[
                AgentCapabilities.CODE_GENERATION,
                AgentCapabilities.CODE_EDITING,
                AgentCapabilities.CODE_ANALYSIS,
                AgentCapabilities.TEXT_COMPLETION,
                AgentCapabilities.STREAMING,
                AgentCapabilities.MULTI_TURN,
                AgentCapabilities.TOOL_USE,
            ],
            config=config or {},
            timeout=60,
            working_dir=None,
        )

        openclaw_command = self.get_config_value("openclaw_command", config=config)
        timeout = self.get_config_value("openclaw_timeout", config=config)
        working_dir_str = self.get_config_value("openclaw_working_dir", config=config)
        working_dir = Path(working_dir_str) if working_dir_str else None

        self.command = openclaw_command
        self.timeout = timeout
        self.working_dir = working_dir
        self.thinking_level = self.get_config_value(
            "openclaw_thinking_level", config=config
        )

        # Verify openclaw is available
        if not self._check_command_available(check_args=["--version"]):
            self.logger.warning(
                "OpenClaw command not found, some operations may fail",
                extra={"command": self.command},
            )

    def _execute_impl(self, request: AgentRequest) -> AgentResponse:
        """Execute OpenClaw command."""
        prompt = request.prompt
        context = request.context or {}
        openclaw_args = self._build_openclaw_args(prompt, context)

        try:
            result = self._execute_command(args=openclaw_args)
            return self._build_response_from_result(
                result,
                request,
                additional_metadata={
                    "openclaw_success": result.get("success", False),
                    "command_full": " ".join([self.command] + openclaw_args),
                },
            )
        except AgentTimeoutError as e:
            raise OpenClawError(
                f"OpenClaw command timed out: {str(e)}", command=self.command
            ) from e
        except AgentError as e:
            raise OpenClawError(
                f"OpenClaw command failed: {str(e)}", command=self.command
            ) from e
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            self.logger.error(f"OpenClaw execution failed: {e}", exc_info=True)
            raise OpenClawError(
                f"OpenClaw command failed: {str(e)}", command=self.command
            ) from e

    def _stream_impl(self, request: AgentRequest) -> Iterator[str]:
        """Stream OpenClaw command output."""
        prompt = request.prompt
        context = request.context or {}
        openclaw_args = self._build_openclaw_args(prompt, context)
        yield from self._stream_command(args=openclaw_args)

    def _build_openclaw_args(
        self, prompt: str, context: dict[str, Any]
    ) -> list[str]:
        """Build openclaw command arguments from prompt and context.

        Supports subcommands:
        - ``agent --message "prompt"`` for AI agent invocation
        - ``message send --to <target> --message "text"`` for channel routing
        - ``gateway`` for control plane management
        - ``doctor`` for health diagnostics
        """
        args: list[str] = []

        if context.get("doctor", False):
            args.append("doctor")
            return args

        if "command" in context:
            command = context["command"]
            if command == "doctor":
                args.append("doctor")
                return args
            elif command == "gateway":
                action = context.get("gateway_action", "status")
                args.extend(["gateway", action])
                return args
            elif command == "message_send":
                target = context.get("to", "")
                message = context.get("message", prompt)
                args.extend(["message", "send", "--to", target, "--message", message])
                return args

        # Default: agent invocation
        args.extend(["agent", "--message", prompt])

        # Optional thinking level
        thinking = context.get("thinking") or self.thinking_level
        if thinking:
            args.extend(["--thinking", thinking])

        return args

    def get_openclaw_version(self) -> dict[str, Any]:
        """Get OpenClaw version information."""
        try:
            result = self._execute_command(args=["--version"], timeout=5)
            return {
                "version": result.get("stdout", "").strip(),
                "exit_code": result.get("exit_code", 0),
                "available": result.get("success", False),
            }
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            self.logger.warning(f"Failed to get OpenClaw version: {e}")
            return {"version": "", "exit_code": -1, "available": False, "error": str(e)}

    def run_doctor(self) -> dict[str, Any]:
        """Run OpenClaw doctor for health diagnostics."""
        try:
            result = self._execute_command(args=["doctor"], timeout=15)
            return {
                "success": result.get("success", False),
                "output": result.get("stdout", ""),
                "error": result.get("stderr") if not result.get("success") else None,
                "exit_code": result.get("exit_code", 0),
            }
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            self.logger.error(f"OpenClaw doctor failed: {e}", exc_info=True)
            return {"success": False, "output": "", "error": str(e), "exit_code": -1}

    def send_message(
        self, target: str, message: str
    ) -> dict[str, Any]:
        """Send a message via OpenClaw channel routing.

        Args:
            target: Channel target (e.g. phone number, username, channel ID)
            message: Message text to send
        """
        try:
            result = self._execute_command(
                args=["message", "send", "--to", target, "--message", message],
                timeout=30,
            )
            return {
                "success": result.get("success", False),
                "output": result.get("stdout", ""),
                "error": result.get("stderr") if not result.get("success") else None,
                "exit_code": result.get("exit_code", 0),
            }
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            self.logger.error(f"OpenClaw send_message failed: {e}", exc_info=True)
            return {"success": False, "output": "", "error": str(e), "exit_code": -1}

    def start_gateway(self) -> dict[str, Any]:
        """Start the OpenClaw Gateway control plane."""
        try:
            result = self._execute_command(args=["gateway"], timeout=15)
            return {
                "success": result.get("success", False),
                "output": result.get("stdout", ""),
                "error": result.get("stderr") if not result.get("success") else None,
                "exit_code": result.get("exit_code", 0),
            }
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            self.logger.error(f"OpenClaw gateway start failed: {e}", exc_info=True)
            return {"success": False, "output": "", "error": str(e), "exit_code": -1}

    def get_gateway_status(self) -> dict[str, Any]:
        """Check Gateway status."""
        try:
            result = self._execute_command(
                args=["gateway", "status"], timeout=10
            )
            return {
                "success": result.get("success", False),
                "output": result.get("stdout", ""),
                "error": result.get("stderr") if not result.get("success") else None,
                "exit_code": result.get("exit_code", 0),
            }
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            self.logger.warning(f"Failed to get Gateway status: {e}")
            return {"success": False, "output": "", "error": str(e), "exit_code": -1}
