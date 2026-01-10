from typing import Any, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator

from codomyrmex.logging_monitoring.logger_config import get_logger











































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
    error_details: Optional[Union[dict[str, Any], str]] = Field(
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
    data: Optional[dict[str, Any]] = Field(
        None,
        description="The output data from the tool if successful. Schema is tool-specific.",
    )
    error: Optional[MCPErrorDetail] = Field(
        None, description="Details of the error if execution failed."
    )
    explanation: Optional[str] = Field(
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
# AGGRESSIVE_REMOVAL_GARBAGE_DOC: # AGGRESSIVE_REMOVAL:             """
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
# AGGRESSIVE_REMOVAL_GARBAGE_DOC: # AGGRESSIVE_REMOVAL:             """
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


# Example Usage (for testing or demonstration)
if __name__ == "__main__":
    # Example Tool Call
    tool_call_data = {
        "tool_name": "example.do_something",
        "arguments": {"param1": "value1", "param2": 123},
    }
    mcp_call = MCPToolCall(**tool_call_data)
    print(f"MCP Call: {mcp_call.model_dump_json(indent=2)}")

    # Example Successful Tool Result
    success_result_data = {
        "status": "success",
        "data": {"output_value": "Task completed successfully.", "items_processed": 10},
        "explanation": "The example tool processed 10 items and finished.",
    }
    mcp_success_result = MCPToolResult(**success_result_data)
    print(f"MCP Success Result: {mcp_success_result.model_dump_json(indent=2)}")

    # Example Failure Tool Result
    failure_result_data = {
        "status": "failure",
        "error": {
            "error_type": "ResourceUnavailable",
            "error_message": "The required resource could not be accessed.",
            "error_details": {"resource_id": "res_abc123"},
        },
    }
    mcp_failure_result = MCPToolResult(**failure_result_data)
    print(f"MCP Failure Result: {mcp_failure_result.model_dump_json(indent=2)}")

    # Example Failure Tool Result (validation error)
    invalid_failure_data = {
        "status": "failure",
        "data": {"some": "data"},  # Data should be null on failure
    }
    try:
        MCPToolResult(**invalid_failure_data)
    except ValueError as e:
        print(f"Validation Error for invalid failure data: {e}")

    invalid_success_data = {
        "status": "failure",  # Error must be populated
        "error": None,
    }
    try:
        MCPToolResult(**invalid_success_data)
    except ValueError as e:
        print(
            f"Validation Error for invalid success data (missing error on failure): {e}"
        )
