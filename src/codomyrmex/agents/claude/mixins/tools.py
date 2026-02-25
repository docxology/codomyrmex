"""ToolsMixin functionality."""

from collections.abc import Callable
from typing import Any

from codomyrmex.agents.core import (
    AgentRequest,
    AgentResponse,
)
from codomyrmex.agents.core.exceptions import ClaudeError
from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)

class ToolsMixin:
    """ToolsMixin class."""

    def register_tool(
        self,
        name: str,
        description: str,
        input_schema: dict[str, Any],
        handler: Callable | None = None,
    ) -> None:
        """Register a tool for function calling.

        Args:
            name: Tool name (must be unique)
            description: Description of what the tool does
            input_schema: JSON Schema for tool input parameters
            handler: Optional callable to handle tool invocations
        """
        tool_def = {
            "name": name,
            "description": description,
            "input_schema": input_schema,
        }

        # Remove existing tool with same name
        self._tools = [t for t in self._tools if t["name"] != name]
        self._tools.append(tool_def)

        if handler:
            if not hasattr(self, "_tool_handlers"):
                self._tool_handlers: dict[str, Callable] = {}
            self._tool_handlers[name] = handler

        self.logger.debug(f"Registered tool: {name}")

    def get_registered_tools(self) -> list[dict[str, Any]]:
        """Get list of registered tools."""
        return self._tools.copy()

    def execute_tool_call(
        self,
        tool_name: str,
        tool_input: dict[str, Any],
    ) -> Any:
        """Execute a tool call using registered handler.

        Args:
            tool_name: Name of the tool to execute
            tool_input: Input parameters for the tool

        Returns:
            Tool execution result

        Raises:
            ClaudeError: If tool not found or execution fails
        """
        if not hasattr(self, "_tool_handlers"):
            raise ClaudeError("No tool handlers registered")

        handler = self._tool_handlers.get(tool_name)
        if not handler:
            raise ClaudeError(f"No handler registered for tool: {tool_name}")

        try:
            return handler(**tool_input)
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            self.logger.error(f"Tool execution failed: {tool_name}", exc_info=True)
            raise ClaudeError(
                f"Tool execution failed: {e}",
                api_error=str(e),
            ) from e

    def execute_with_tools(
        self,
        request: AgentRequest,
        auto_execute: bool = True,
        max_tool_rounds: int = 10,
    ) -> AgentResponse:
        """Execute request with automatic tool execution.

        This method handles the tool use loop, automatically executing
        tool calls and continuing the conversation until Claude provides
        a final response.

        Args:
            request: Agent request
            auto_execute: Whether to automatically execute tool calls
            max_tool_rounds: Maximum number of tool execution rounds

        Returns:
            Final agent response
        """
        messages, system_message = self._build_messages_with_system(request)
        all_tool_calls = []

        for round_num in range(max_tool_rounds):
            # Build API call
            api_kwargs = {
                "model": self.model,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
                "messages": messages,
                "timeout": self.timeout,
            }

            if system_message:
                api_kwargs["system"] = system_message
            if self._tools:
                api_kwargs["tools"] = self._tools

            response = self.client.messages.create(**api_kwargs)

            # Check if we need to execute tools
            if response.stop_reason != "tool_use":
                # Final response
                content, _ = self._extract_response_content(response)
                input_tokens, output_tokens = self._extract_tokens_from_response(
                    response, "anthropic"
                )
                return AgentResponse(
                    content=content,
                    metadata={
                        "usage": {
                            "input_tokens": input_tokens,
                            "output_tokens": output_tokens,
                        },
                        "stop_reason": response.stop_reason,
                        "tool_calls": all_tool_calls,
                        "tool_rounds": round_num + 1,
                    },
                    tokens_used=input_tokens + output_tokens,
                )

            # Extract and execute tool calls
            _, tool_calls = self._extract_response_content(response)

            if not tool_calls or not auto_execute:
                content, _ = self._extract_response_content(response)
                return AgentResponse(
                    content=content,
                    metadata={"tool_calls": tool_calls, "requires_tool_execution": True},
                )

            # Add assistant response to messages
            messages.append({"role": "assistant", "content": response.content})

            # Execute tools and add results
            tool_results = []
            for tool_call in tool_calls:
                all_tool_calls.append(tool_call)
                try:
                    result = self.execute_tool_call(
                        tool_call["name"], tool_call["input"]
                    )
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_call["id"],
                        "content": str(result),
                    })
                except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_call["id"],
                        "content": f"Error: {str(e)}",
                        "is_error": True,
                    })

            messages.append({"role": "user", "content": tool_results})

        # Max rounds exceeded
        raise ClaudeError(
            f"Maximum tool execution rounds ({max_tool_rounds}) exceeded"
        )

