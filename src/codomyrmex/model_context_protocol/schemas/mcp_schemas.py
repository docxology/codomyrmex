from collections.abc import Callable
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)

class MCPErrorDetail(BaseModel):
    """Standard structure for detailed error information in MCP responses."""

    error_type: str = Field(
        ...,
        description="A unique code or type for the error (e.g., ValidationError, FileNotFoundError).",
    )
    error_message: str = Field(
        ..., description="A descriptive message explaining the error."
    )
    error_details: dict[str, Any] | str | None = Field(
        None,
        description="Optional structured details or a string containing more info about the error.",
    )


class MCPToolCall(BaseModel):
    """Represents a call to an MCP tool."""

    tool_name: str = Field(..., description="The unique invocation name of the tool.")
    arguments: dict[str, Any] = Field(
        ...,
        description="An object containing the arguments for the tool. The schema for this object is defined by the specific tool being called.",
    )

    model_config = ConfigDict(extra="allow")  # Allow arbitrary arguments, tool-specific validation happens elsewhere


class MCPToolResult(BaseModel):
    """Represents the result of an MCP tool execution."""

    status: str = Field(
        ...,
        description="The outcome of the tool execution (e.g., success, failure, no_change_needed).",
    )
    data: dict[str, Any] | None = Field(
        None,
        description="The output data from the tool if successful. Schema is tool-specific.",
    )
    error: MCPErrorDetail | None = Field(
        None, description="Details of the error if execution failed."
    )
    explanation: str | None = Field(
        None, description="Optional human-readable explanation of the result."
    )

    @field_validator("error")
    @classmethod
    def check_error_if_failed(cls, v, info):
        """Check Error If Failed.

            Args:
                v: The value of the error field
                info: Validation info containing field context

            Returns:
                The validated value
            """
        if hasattr(info, 'data') and info.data.get("status"):
            status = info.data.get("status")
        else:
            # Fallback for older pydantic versions
            status = getattr(info, 'values', {}).get("status")

        if status and "fail" in status.lower() and v is None:
            raise ValueError(
                "'error' field must be populated if status indicates failure."
            )
        if status and "success" in status.lower() and v is not None:
            # Allowing error to be populated even on success, for warnings or partial failures not yet fully specified.
            # Consider making this stricter if pure success should never have an error object.
            pass
        return v

    @field_validator("data")
    @classmethod
    def check_data_if_success(cls, v, info):
        """Check Data If Success.

            Args:
                v: The value of the data field
                info: Validation info containing field context

            Returns:
                The validated value
            """
        if hasattr(info, 'data') and info.data.get("status"):
            status = info.data.get("status")
        else:
            # Fallback for older pydantic versions
            status = getattr(info, 'values', {}).get("status")

        if status and "success" in status.lower() and v is None:
            # Data can be None even on success if the tool has no specific data output (e.g. a tool that only has side effects)
            pass
        if status and "fail" in status.lower() and v is not None:
            raise ValueError(
                "'data' field should be null or omitted if status indicates failure."
            )
        return v

    model_config = ConfigDict(extra="allow")  # Allow additional fields in data, specific validation is per-tool


class MCPMessage(BaseModel):
    """Represents a message in an MCP conversation."""

    role: str = Field(..., description="Role of the message sender (e.g., 'user', 'assistant', 'system', 'tool').")
    content: str | None = Field(None, description="Text content of the message.")
    tool_calls: list[MCPToolCall] | None = Field(None, description="Tool calls made in this message.")
    tool_results: list[MCPToolResult] | None = Field(None, description="Results from tool executions.")
    metadata: dict[str, Any] | None = Field(None, description="Additional metadata for the message.")

    model_config = ConfigDict(extra="allow")


class MCPToolRegistry:
    """Registry for managing available MCP tools."""

    def __init__(self) -> None:
        """Initialize the tool registry."""
        self._tools: dict[str, dict[str, Any]] = {}
        logger.info("MCPToolRegistry initialized")

    def register(self, tool_name: str, schema: dict[str, Any], handler: Callable[..., Any] | None = None) -> None:
        """
        Register a tool with the registry.

        Args:
            tool_name: Unique name for the tool
            schema: JSON Schema describing the tool's arguments
            handler: Optional callable to handle tool invocations
        """
        self._tools[tool_name] = {
            "name": tool_name,
            "schema": schema,
            "handler": handler,
        }
        logger.debug(f"Registered tool: {tool_name}")

    def unregister(self, tool_name: str) -> bool:
        """
        Remove a tool from the registry.

        Args:
            tool_name: Name of the tool to remove

        Returns:
            True if removed, False if not found
        """
        if tool_name in self._tools:
            del self._tools[tool_name]
            logger.debug(f"Unregistered tool: {tool_name}")
            return True
        return False

    def get(self, tool_name: str) -> dict[str, Any] | None:
        """
        Get a tool's metadata by name.

        Args:
            tool_name: Name of the tool

        Returns:
            Tool metadata dict or None
        """
        return self._tools.get(tool_name)

    # Alias for API coherence (mcp_bridge uses get_tool)
    get_tool = get

    def list_tools(self) -> list[str]:
        """
        List all registered tool names.

        Returns:
            List of tool names
        """
        return list(self._tools.keys())

    def validate_call(self, tool_call: MCPToolCall) -> tuple[bool, str | None]:
        """
        Validate a tool call against the registry.

        Args:
            tool_call: The tool call to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        tool = self._tools.get(tool_call.tool_name)
        if not tool:
            return False, f"Unknown tool: {tool_call.tool_name}"

        # Basic schema validation could be added here
        # For now, just check tool exists
        return True, None

    def execute(self, tool_call: MCPToolCall) -> MCPToolResult:
        """
        Execute a tool call using its registered handler.

        Args:
            tool_call: The tool call to execute

        Returns:
            MCPToolResult with execution outcome
        """
        tool = self._tools.get(tool_call.tool_name)
        if not tool:
            return MCPToolResult(
                status="failure",
                error=MCPErrorDetail(
                    error_type="ToolNotFound",
                    error_message=f"Tool '{tool_call.tool_name}' not registered"
                )
            )

        handler = tool.get("handler")
        if not handler:
            return MCPToolResult(
                status="failure",
                error=MCPErrorDetail(
                    error_type="NoHandler",
                    error_message=f"No handler registered for tool '{tool_call.tool_name}'"
                )
            )

        try:
            result = handler(**tool_call.arguments)
            return MCPToolResult(
                status="success",
                data={"result": result}
            )
        except Exception as e:
            logger.error(f"Tool execution failed: {e}")
            return MCPToolResult(
                status="failure",
                error=MCPErrorDetail(
                    error_type=type(e).__name__,
                    error_message=str(e)
                )
            )


# Example Usage (for testing or demonstration)
if __name__ == "__main__":
    # Example Tool Call
    mcp_call = MCPToolCall(
        tool_name="example.do_something",
        arguments={"param1": "value1", "param2": 123},
    )
    print(f"MCP Call: {mcp_call.model_dump_json(indent=2)}")

    # Example Successful Tool Result
    mcp_success_result = MCPToolResult(
        status="success",
        data={"output_value": "Task completed successfully.", "items_processed": 10},
        explanation="The example tool processed 10 items and finished.",
    )
    print(f"MCP Success Result: {mcp_success_result.model_dump_json(indent=2)}")

    # Example Failure Tool Result
    mcp_failure_result = MCPToolResult(
        status="failure",
        error=MCPErrorDetail(
            error_type="ResourceUnavailable",
            error_message="The required resource could not be accessed.",
            error_details={"resource_id": "res_abc123"},
        ),
    )
    print(f"MCP Failure Result: {mcp_failure_result.model_dump_json(indent=2)}")

    # Example Failure Tool Result (validation error)
    try:
        MCPToolResult(
            status="failure",
            data={"some": "data"},  # Data should be null on failure
        )
    except ValueError as e:
        print(f"Validation Error for invalid failure data: {e}")

    try:
        MCPToolResult(
            status="failure",  # Error must be populated
            error=None,
        )
    except ValueError as e:
        print(
            f"Validation Error for invalid success data (missing error on failure): {e}"
        )
