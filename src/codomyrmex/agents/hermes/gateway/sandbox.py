"""Hermes Gateway Tool Sandbox.

Restricts tool execution (`run_command`, `write_file`) originating from unauthenticated external adapters.
"""

from typing import Any

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class SandboxViolation(Exception):
    """Raised when an unauthenticated session attempts a restricted tool call."""


class GatewayToolSandbox:
    """Intercepts and validates tool requests against session authentication thresholds."""

    # list of tool names that are strictly forbidden for untrusted origin sessions
    RESTRICTED_TOOLS = {"run_command", "write_file", "delete_file"}

    def __init__(self, is_authenticated: bool = False) -> None:
        """
        Initialize the sandbox for a specific invocation context.

        Args:
            is_authenticated: True if the user has cryptographically proven identity.
                              False (default) for arbitrary platform interactions (e.g., public Telegram bot).
        """
        self.is_authenticated = is_authenticated

    def validate_tool_call(self, tool_name: str, tool_args: dict[str, Any]) -> None:
        """
        Validate whether the given tool call is permitted.

        Raises:
            SandboxViolation: If the tool is blocked for the current session state.
        """
        if self.is_authenticated:
            # Trusted owners can trigger anything.
            return

        if tool_name in self.RESTRICTED_TOOLS:
            logger.warning(
                f"Sandbox blocked restricted tool '{tool_name}' from unauthenticated origin. "
                f"Args: {tool_args}"
            )
            raise SandboxViolation(
                f"Tool '{tool_name}' is restricted for external/unauthenticated sessions."
            )

    def wrap_execution(
        self, tool_name: str, tool_args: dict[str, Any], executor_func: Any
    ) -> Any:
        """
        Execute the tool only if sandbox constraints pass.

        Args:
            tool_name: Name of the requested tool.
            tool_args: Dictionary of arguments for the tool.
            executor_func: A callable that actually runs the tool and returns the result.
        """
        self.validate_tool_call(tool_name, tool_args)
        return executor_func(tool_name, tool_args)
