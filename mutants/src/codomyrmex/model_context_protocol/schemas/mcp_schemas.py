from typing import Any, Callable, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)
from inspect import signature as _mutmut_signature
from typing import Annotated
from typing import Callable
from typing import ClassVar


MutantDict = Annotated[dict[str, Callable], "Mutant"]


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg = None):
    """Forward call to original or mutated function, depending on the environment"""
    import os
    mutant_under_test = os.environ['MUTANT_UNDER_TEST']
    if mutant_under_test == 'fail':
        from mutmut.__main__ import MutmutProgrammaticFailException
        raise MutmutProgrammaticFailException('Failed programmatically')      
    elif mutant_under_test == 'stats':
        from mutmut.__main__ import record_trampoline_hit
        record_trampoline_hit(orig.__module__ + '.' + orig.__name__)
        result = orig(*call_args, **call_kwargs)
        return result
    prefix = orig.__module__ + '.' + orig.__name__ + '__mutmut_'
    if not mutant_under_test.startswith(prefix):
        result = orig(*call_args, **call_kwargs)
        return result
    mutant_name = mutant_under_test.rpartition('.')[-1]
    if self_arg is not None:
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs)
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs)
    return result

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

    def xǁMCPToolRegistryǁ__init____mutmut_orig(self) -> None:
        """Initialize the tool registry."""
        self._tools: dict[str, dict[str, Any]] = {}
        logger.info("MCPToolRegistry initialized")

    def xǁMCPToolRegistryǁ__init____mutmut_1(self) -> None:
        """Initialize the tool registry."""
        self._tools: dict[str, dict[str, Any]] = None
        logger.info("MCPToolRegistry initialized")

    def xǁMCPToolRegistryǁ__init____mutmut_2(self) -> None:
        """Initialize the tool registry."""
        self._tools: dict[str, dict[str, Any]] = {}
        logger.info(None)

    def xǁMCPToolRegistryǁ__init____mutmut_3(self) -> None:
        """Initialize the tool registry."""
        self._tools: dict[str, dict[str, Any]] = {}
        logger.info("XXMCPToolRegistry initializedXX")

    def xǁMCPToolRegistryǁ__init____mutmut_4(self) -> None:
        """Initialize the tool registry."""
        self._tools: dict[str, dict[str, Any]] = {}
        logger.info("mcptoolregistry initialized")

    def xǁMCPToolRegistryǁ__init____mutmut_5(self) -> None:
        """Initialize the tool registry."""
        self._tools: dict[str, dict[str, Any]] = {}
        logger.info("MCPTOOLREGISTRY INITIALIZED")
    
    xǁMCPToolRegistryǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMCPToolRegistryǁ__init____mutmut_1': xǁMCPToolRegistryǁ__init____mutmut_1, 
        'xǁMCPToolRegistryǁ__init____mutmut_2': xǁMCPToolRegistryǁ__init____mutmut_2, 
        'xǁMCPToolRegistryǁ__init____mutmut_3': xǁMCPToolRegistryǁ__init____mutmut_3, 
        'xǁMCPToolRegistryǁ__init____mutmut_4': xǁMCPToolRegistryǁ__init____mutmut_4, 
        'xǁMCPToolRegistryǁ__init____mutmut_5': xǁMCPToolRegistryǁ__init____mutmut_5
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMCPToolRegistryǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁMCPToolRegistryǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁMCPToolRegistryǁ__init____mutmut_orig)
    xǁMCPToolRegistryǁ__init____mutmut_orig.__name__ = 'xǁMCPToolRegistryǁ__init__'

    def xǁMCPToolRegistryǁregister__mutmut_orig(self, tool_name: str, schema: dict[str, Any], handler: Callable[..., Any] | None = None) -> None:
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

    def xǁMCPToolRegistryǁregister__mutmut_1(self, tool_name: str, schema: dict[str, Any], handler: Callable[..., Any] | None = None) -> None:
        """
        Register a tool with the registry.

        Args:
            tool_name: Unique name for the tool
            schema: JSON Schema describing the tool's arguments
            handler: Optional callable to handle tool invocations
        """
        self._tools[tool_name] = None
        logger.debug(f"Registered tool: {tool_name}")

    def xǁMCPToolRegistryǁregister__mutmut_2(self, tool_name: str, schema: dict[str, Any], handler: Callable[..., Any] | None = None) -> None:
        """
        Register a tool with the registry.

        Args:
            tool_name: Unique name for the tool
            schema: JSON Schema describing the tool's arguments
            handler: Optional callable to handle tool invocations
        """
        self._tools[tool_name] = {
            "XXnameXX": tool_name,
            "schema": schema,
            "handler": handler,
        }
        logger.debug(f"Registered tool: {tool_name}")

    def xǁMCPToolRegistryǁregister__mutmut_3(self, tool_name: str, schema: dict[str, Any], handler: Callable[..., Any] | None = None) -> None:
        """
        Register a tool with the registry.

        Args:
            tool_name: Unique name for the tool
            schema: JSON Schema describing the tool's arguments
            handler: Optional callable to handle tool invocations
        """
        self._tools[tool_name] = {
            "NAME": tool_name,
            "schema": schema,
            "handler": handler,
        }
        logger.debug(f"Registered tool: {tool_name}")

    def xǁMCPToolRegistryǁregister__mutmut_4(self, tool_name: str, schema: dict[str, Any], handler: Callable[..., Any] | None = None) -> None:
        """
        Register a tool with the registry.

        Args:
            tool_name: Unique name for the tool
            schema: JSON Schema describing the tool's arguments
            handler: Optional callable to handle tool invocations
        """
        self._tools[tool_name] = {
            "name": tool_name,
            "XXschemaXX": schema,
            "handler": handler,
        }
        logger.debug(f"Registered tool: {tool_name}")

    def xǁMCPToolRegistryǁregister__mutmut_5(self, tool_name: str, schema: dict[str, Any], handler: Callable[..., Any] | None = None) -> None:
        """
        Register a tool with the registry.

        Args:
            tool_name: Unique name for the tool
            schema: JSON Schema describing the tool's arguments
            handler: Optional callable to handle tool invocations
        """
        self._tools[tool_name] = {
            "name": tool_name,
            "SCHEMA": schema,
            "handler": handler,
        }
        logger.debug(f"Registered tool: {tool_name}")

    def xǁMCPToolRegistryǁregister__mutmut_6(self, tool_name: str, schema: dict[str, Any], handler: Callable[..., Any] | None = None) -> None:
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
            "XXhandlerXX": handler,
        }
        logger.debug(f"Registered tool: {tool_name}")

    def xǁMCPToolRegistryǁregister__mutmut_7(self, tool_name: str, schema: dict[str, Any], handler: Callable[..., Any] | None = None) -> None:
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
            "HANDLER": handler,
        }
        logger.debug(f"Registered tool: {tool_name}")

    def xǁMCPToolRegistryǁregister__mutmut_8(self, tool_name: str, schema: dict[str, Any], handler: Callable[..., Any] | None = None) -> None:
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
        logger.debug(None)
    
    xǁMCPToolRegistryǁregister__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMCPToolRegistryǁregister__mutmut_1': xǁMCPToolRegistryǁregister__mutmut_1, 
        'xǁMCPToolRegistryǁregister__mutmut_2': xǁMCPToolRegistryǁregister__mutmut_2, 
        'xǁMCPToolRegistryǁregister__mutmut_3': xǁMCPToolRegistryǁregister__mutmut_3, 
        'xǁMCPToolRegistryǁregister__mutmut_4': xǁMCPToolRegistryǁregister__mutmut_4, 
        'xǁMCPToolRegistryǁregister__mutmut_5': xǁMCPToolRegistryǁregister__mutmut_5, 
        'xǁMCPToolRegistryǁregister__mutmut_6': xǁMCPToolRegistryǁregister__mutmut_6, 
        'xǁMCPToolRegistryǁregister__mutmut_7': xǁMCPToolRegistryǁregister__mutmut_7, 
        'xǁMCPToolRegistryǁregister__mutmut_8': xǁMCPToolRegistryǁregister__mutmut_8
    }
    
    def register(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMCPToolRegistryǁregister__mutmut_orig"), object.__getattribute__(self, "xǁMCPToolRegistryǁregister__mutmut_mutants"), args, kwargs, self)
        return result 
    
    register.__signature__ = _mutmut_signature(xǁMCPToolRegistryǁregister__mutmut_orig)
    xǁMCPToolRegistryǁregister__mutmut_orig.__name__ = 'xǁMCPToolRegistryǁregister'

    def xǁMCPToolRegistryǁunregister__mutmut_orig(self, tool_name: str) -> bool:
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

    def xǁMCPToolRegistryǁunregister__mutmut_1(self, tool_name: str) -> bool:
        """
        Remove a tool from the registry.

        Args:
            tool_name: Name of the tool to remove

        Returns:
            True if removed, False if not found
        """
        if tool_name not in self._tools:
            del self._tools[tool_name]
            logger.debug(f"Unregistered tool: {tool_name}")
            return True
        return False

    def xǁMCPToolRegistryǁunregister__mutmut_2(self, tool_name: str) -> bool:
        """
        Remove a tool from the registry.

        Args:
            tool_name: Name of the tool to remove

        Returns:
            True if removed, False if not found
        """
        if tool_name in self._tools:
            del self._tools[tool_name]
            logger.debug(None)
            return True
        return False

    def xǁMCPToolRegistryǁunregister__mutmut_3(self, tool_name: str) -> bool:
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
            return False
        return False

    def xǁMCPToolRegistryǁunregister__mutmut_4(self, tool_name: str) -> bool:
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
        return True
    
    xǁMCPToolRegistryǁunregister__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMCPToolRegistryǁunregister__mutmut_1': xǁMCPToolRegistryǁunregister__mutmut_1, 
        'xǁMCPToolRegistryǁunregister__mutmut_2': xǁMCPToolRegistryǁunregister__mutmut_2, 
        'xǁMCPToolRegistryǁunregister__mutmut_3': xǁMCPToolRegistryǁunregister__mutmut_3, 
        'xǁMCPToolRegistryǁunregister__mutmut_4': xǁMCPToolRegistryǁunregister__mutmut_4
    }
    
    def unregister(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMCPToolRegistryǁunregister__mutmut_orig"), object.__getattribute__(self, "xǁMCPToolRegistryǁunregister__mutmut_mutants"), args, kwargs, self)
        return result 
    
    unregister.__signature__ = _mutmut_signature(xǁMCPToolRegistryǁunregister__mutmut_orig)
    xǁMCPToolRegistryǁunregister__mutmut_orig.__name__ = 'xǁMCPToolRegistryǁunregister'

    def xǁMCPToolRegistryǁget__mutmut_orig(self, tool_name: str) -> dict[str, Any] | None:
        """
        Get a tool's metadata by name.

        Args:
            tool_name: Name of the tool

        Returns:
            Tool metadata dict or None
        """
        return self._tools.get(tool_name)

    def xǁMCPToolRegistryǁget__mutmut_1(self, tool_name: str) -> dict[str, Any] | None:
        """
        Get a tool's metadata by name.

        Args:
            tool_name: Name of the tool

        Returns:
            Tool metadata dict or None
        """
        return self._tools.get(None)
    
    xǁMCPToolRegistryǁget__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMCPToolRegistryǁget__mutmut_1': xǁMCPToolRegistryǁget__mutmut_1
    }
    
    def get(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMCPToolRegistryǁget__mutmut_orig"), object.__getattribute__(self, "xǁMCPToolRegistryǁget__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get.__signature__ = _mutmut_signature(xǁMCPToolRegistryǁget__mutmut_orig)
    xǁMCPToolRegistryǁget__mutmut_orig.__name__ = 'xǁMCPToolRegistryǁget'

    # Alias for API coherence (mcp_bridge uses get_tool)
    get_tool = get

    def xǁMCPToolRegistryǁlist_tools__mutmut_orig(self) -> list[str]:
        """
        List all registered tool names.

        Returns:
            List of tool names
        """
        return list(self._tools.keys())

    def xǁMCPToolRegistryǁlist_tools__mutmut_1(self) -> list[str]:
        """
        List all registered tool names.

        Returns:
            List of tool names
        """
        return list(None)
    
    xǁMCPToolRegistryǁlist_tools__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMCPToolRegistryǁlist_tools__mutmut_1': xǁMCPToolRegistryǁlist_tools__mutmut_1
    }
    
    def list_tools(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMCPToolRegistryǁlist_tools__mutmut_orig"), object.__getattribute__(self, "xǁMCPToolRegistryǁlist_tools__mutmut_mutants"), args, kwargs, self)
        return result 
    
    list_tools.__signature__ = _mutmut_signature(xǁMCPToolRegistryǁlist_tools__mutmut_orig)
    xǁMCPToolRegistryǁlist_tools__mutmut_orig.__name__ = 'xǁMCPToolRegistryǁlist_tools'

    def xǁMCPToolRegistryǁvalidate_call__mutmut_orig(self, tool_call: MCPToolCall) -> tuple[bool, str | None]:
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

    def xǁMCPToolRegistryǁvalidate_call__mutmut_1(self, tool_call: MCPToolCall) -> tuple[bool, str | None]:
        """
        Validate a tool call against the registry.

        Args:
            tool_call: The tool call to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        tool = None
        if not tool:
            return False, f"Unknown tool: {tool_call.tool_name}"

        # Basic schema validation could be added here
        # For now, just check tool exists
        return True, None

    def xǁMCPToolRegistryǁvalidate_call__mutmut_2(self, tool_call: MCPToolCall) -> tuple[bool, str | None]:
        """
        Validate a tool call against the registry.

        Args:
            tool_call: The tool call to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        tool = self._tools.get(None)
        if not tool:
            return False, f"Unknown tool: {tool_call.tool_name}"

        # Basic schema validation could be added here
        # For now, just check tool exists
        return True, None

    def xǁMCPToolRegistryǁvalidate_call__mutmut_3(self, tool_call: MCPToolCall) -> tuple[bool, str | None]:
        """
        Validate a tool call against the registry.

        Args:
            tool_call: The tool call to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        tool = self._tools.get(tool_call.tool_name)
        if tool:
            return False, f"Unknown tool: {tool_call.tool_name}"

        # Basic schema validation could be added here
        # For now, just check tool exists
        return True, None

    def xǁMCPToolRegistryǁvalidate_call__mutmut_4(self, tool_call: MCPToolCall) -> tuple[bool, str | None]:
        """
        Validate a tool call against the registry.

        Args:
            tool_call: The tool call to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        tool = self._tools.get(tool_call.tool_name)
        if not tool:
            return True, f"Unknown tool: {tool_call.tool_name}"

        # Basic schema validation could be added here
        # For now, just check tool exists
        return True, None

    def xǁMCPToolRegistryǁvalidate_call__mutmut_5(self, tool_call: MCPToolCall) -> tuple[bool, str | None]:
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
        return False, None
    
    xǁMCPToolRegistryǁvalidate_call__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMCPToolRegistryǁvalidate_call__mutmut_1': xǁMCPToolRegistryǁvalidate_call__mutmut_1, 
        'xǁMCPToolRegistryǁvalidate_call__mutmut_2': xǁMCPToolRegistryǁvalidate_call__mutmut_2, 
        'xǁMCPToolRegistryǁvalidate_call__mutmut_3': xǁMCPToolRegistryǁvalidate_call__mutmut_3, 
        'xǁMCPToolRegistryǁvalidate_call__mutmut_4': xǁMCPToolRegistryǁvalidate_call__mutmut_4, 
        'xǁMCPToolRegistryǁvalidate_call__mutmut_5': xǁMCPToolRegistryǁvalidate_call__mutmut_5
    }
    
    def validate_call(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMCPToolRegistryǁvalidate_call__mutmut_orig"), object.__getattribute__(self, "xǁMCPToolRegistryǁvalidate_call__mutmut_mutants"), args, kwargs, self)
        return result 
    
    validate_call.__signature__ = _mutmut_signature(xǁMCPToolRegistryǁvalidate_call__mutmut_orig)
    xǁMCPToolRegistryǁvalidate_call__mutmut_orig.__name__ = 'xǁMCPToolRegistryǁvalidate_call'

    def xǁMCPToolRegistryǁexecute__mutmut_orig(self, tool_call: MCPToolCall) -> MCPToolResult:
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

    def xǁMCPToolRegistryǁexecute__mutmut_1(self, tool_call: MCPToolCall) -> MCPToolResult:
        """
        Execute a tool call using its registered handler.

        Args:
            tool_call: The tool call to execute

        Returns:
            MCPToolResult with execution outcome
        """
        tool = None
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

    def xǁMCPToolRegistryǁexecute__mutmut_2(self, tool_call: MCPToolCall) -> MCPToolResult:
        """
        Execute a tool call using its registered handler.

        Args:
            tool_call: The tool call to execute

        Returns:
            MCPToolResult with execution outcome
        """
        tool = self._tools.get(None)
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

    def xǁMCPToolRegistryǁexecute__mutmut_3(self, tool_call: MCPToolCall) -> MCPToolResult:
        """
        Execute a tool call using its registered handler.

        Args:
            tool_call: The tool call to execute

        Returns:
            MCPToolResult with execution outcome
        """
        tool = self._tools.get(tool_call.tool_name)
        if tool:
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

    def xǁMCPToolRegistryǁexecute__mutmut_4(self, tool_call: MCPToolCall) -> MCPToolResult:
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
                status=None,
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

    def xǁMCPToolRegistryǁexecute__mutmut_5(self, tool_call: MCPToolCall) -> MCPToolResult:
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
                error=None
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

    def xǁMCPToolRegistryǁexecute__mutmut_6(self, tool_call: MCPToolCall) -> MCPToolResult:
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

    def xǁMCPToolRegistryǁexecute__mutmut_7(self, tool_call: MCPToolCall) -> MCPToolResult:
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

    def xǁMCPToolRegistryǁexecute__mutmut_8(self, tool_call: MCPToolCall) -> MCPToolResult:
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
                status="XXfailureXX",
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

    def xǁMCPToolRegistryǁexecute__mutmut_9(self, tool_call: MCPToolCall) -> MCPToolResult:
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
                status="FAILURE",
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

    def xǁMCPToolRegistryǁexecute__mutmut_10(self, tool_call: MCPToolCall) -> MCPToolResult:
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
                    error_type=None,
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

    def xǁMCPToolRegistryǁexecute__mutmut_11(self, tool_call: MCPToolCall) -> MCPToolResult:
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
                    error_message=None
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

    def xǁMCPToolRegistryǁexecute__mutmut_12(self, tool_call: MCPToolCall) -> MCPToolResult:
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

    def xǁMCPToolRegistryǁexecute__mutmut_13(self, tool_call: MCPToolCall) -> MCPToolResult:
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

    def xǁMCPToolRegistryǁexecute__mutmut_14(self, tool_call: MCPToolCall) -> MCPToolResult:
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
                    error_type="XXToolNotFoundXX",
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

    def xǁMCPToolRegistryǁexecute__mutmut_15(self, tool_call: MCPToolCall) -> MCPToolResult:
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
                    error_type="toolnotfound",
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

    def xǁMCPToolRegistryǁexecute__mutmut_16(self, tool_call: MCPToolCall) -> MCPToolResult:
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
                    error_type="TOOLNOTFOUND",
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

    def xǁMCPToolRegistryǁexecute__mutmut_17(self, tool_call: MCPToolCall) -> MCPToolResult:
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

        handler = None
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

    def xǁMCPToolRegistryǁexecute__mutmut_18(self, tool_call: MCPToolCall) -> MCPToolResult:
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

        handler = tool.get(None)
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

    def xǁMCPToolRegistryǁexecute__mutmut_19(self, tool_call: MCPToolCall) -> MCPToolResult:
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

        handler = tool.get("XXhandlerXX")
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

    def xǁMCPToolRegistryǁexecute__mutmut_20(self, tool_call: MCPToolCall) -> MCPToolResult:
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

        handler = tool.get("HANDLER")
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

    def xǁMCPToolRegistryǁexecute__mutmut_21(self, tool_call: MCPToolCall) -> MCPToolResult:
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
        if handler:
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

    def xǁMCPToolRegistryǁexecute__mutmut_22(self, tool_call: MCPToolCall) -> MCPToolResult:
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
                status=None,
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

    def xǁMCPToolRegistryǁexecute__mutmut_23(self, tool_call: MCPToolCall) -> MCPToolResult:
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
                error=None
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

    def xǁMCPToolRegistryǁexecute__mutmut_24(self, tool_call: MCPToolCall) -> MCPToolResult:
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

    def xǁMCPToolRegistryǁexecute__mutmut_25(self, tool_call: MCPToolCall) -> MCPToolResult:
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

    def xǁMCPToolRegistryǁexecute__mutmut_26(self, tool_call: MCPToolCall) -> MCPToolResult:
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
                status="XXfailureXX",
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

    def xǁMCPToolRegistryǁexecute__mutmut_27(self, tool_call: MCPToolCall) -> MCPToolResult:
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
                status="FAILURE",
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

    def xǁMCPToolRegistryǁexecute__mutmut_28(self, tool_call: MCPToolCall) -> MCPToolResult:
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
                    error_type=None,
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

    def xǁMCPToolRegistryǁexecute__mutmut_29(self, tool_call: MCPToolCall) -> MCPToolResult:
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
                    error_message=None
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

    def xǁMCPToolRegistryǁexecute__mutmut_30(self, tool_call: MCPToolCall) -> MCPToolResult:
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

    def xǁMCPToolRegistryǁexecute__mutmut_31(self, tool_call: MCPToolCall) -> MCPToolResult:
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

    def xǁMCPToolRegistryǁexecute__mutmut_32(self, tool_call: MCPToolCall) -> MCPToolResult:
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
                    error_type="XXNoHandlerXX",
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

    def xǁMCPToolRegistryǁexecute__mutmut_33(self, tool_call: MCPToolCall) -> MCPToolResult:
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
                    error_type="nohandler",
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

    def xǁMCPToolRegistryǁexecute__mutmut_34(self, tool_call: MCPToolCall) -> MCPToolResult:
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
                    error_type="NOHANDLER",
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

    def xǁMCPToolRegistryǁexecute__mutmut_35(self, tool_call: MCPToolCall) -> MCPToolResult:
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
            result = None
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

    def xǁMCPToolRegistryǁexecute__mutmut_36(self, tool_call: MCPToolCall) -> MCPToolResult:
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
                status=None,
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

    def xǁMCPToolRegistryǁexecute__mutmut_37(self, tool_call: MCPToolCall) -> MCPToolResult:
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
                data=None
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

    def xǁMCPToolRegistryǁexecute__mutmut_38(self, tool_call: MCPToolCall) -> MCPToolResult:
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

    def xǁMCPToolRegistryǁexecute__mutmut_39(self, tool_call: MCPToolCall) -> MCPToolResult:
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

    def xǁMCPToolRegistryǁexecute__mutmut_40(self, tool_call: MCPToolCall) -> MCPToolResult:
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
                status="XXsuccessXX",
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

    def xǁMCPToolRegistryǁexecute__mutmut_41(self, tool_call: MCPToolCall) -> MCPToolResult:
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
                status="SUCCESS",
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

    def xǁMCPToolRegistryǁexecute__mutmut_42(self, tool_call: MCPToolCall) -> MCPToolResult:
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
                data={"XXresultXX": result}
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

    def xǁMCPToolRegistryǁexecute__mutmut_43(self, tool_call: MCPToolCall) -> MCPToolResult:
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
                data={"RESULT": result}
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

    def xǁMCPToolRegistryǁexecute__mutmut_44(self, tool_call: MCPToolCall) -> MCPToolResult:
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
            logger.error(None)
            return MCPToolResult(
                status="failure",
                error=MCPErrorDetail(
                    error_type=type(e).__name__,
                    error_message=str(e)
                )
            )

    def xǁMCPToolRegistryǁexecute__mutmut_45(self, tool_call: MCPToolCall) -> MCPToolResult:
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
                status=None,
                error=MCPErrorDetail(
                    error_type=type(e).__name__,
                    error_message=str(e)
                )
            )

    def xǁMCPToolRegistryǁexecute__mutmut_46(self, tool_call: MCPToolCall) -> MCPToolResult:
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
                error=None
            )

    def xǁMCPToolRegistryǁexecute__mutmut_47(self, tool_call: MCPToolCall) -> MCPToolResult:
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
                error=MCPErrorDetail(
                    error_type=type(e).__name__,
                    error_message=str(e)
                )
            )

    def xǁMCPToolRegistryǁexecute__mutmut_48(self, tool_call: MCPToolCall) -> MCPToolResult:
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
                )

    def xǁMCPToolRegistryǁexecute__mutmut_49(self, tool_call: MCPToolCall) -> MCPToolResult:
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
                status="XXfailureXX",
                error=MCPErrorDetail(
                    error_type=type(e).__name__,
                    error_message=str(e)
                )
            )

    def xǁMCPToolRegistryǁexecute__mutmut_50(self, tool_call: MCPToolCall) -> MCPToolResult:
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
                status="FAILURE",
                error=MCPErrorDetail(
                    error_type=type(e).__name__,
                    error_message=str(e)
                )
            )

    def xǁMCPToolRegistryǁexecute__mutmut_51(self, tool_call: MCPToolCall) -> MCPToolResult:
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
                    error_type=None,
                    error_message=str(e)
                )
            )

    def xǁMCPToolRegistryǁexecute__mutmut_52(self, tool_call: MCPToolCall) -> MCPToolResult:
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
                    error_message=None
                )
            )

    def xǁMCPToolRegistryǁexecute__mutmut_53(self, tool_call: MCPToolCall) -> MCPToolResult:
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
                    error_message=str(e)
                )
            )

    def xǁMCPToolRegistryǁexecute__mutmut_54(self, tool_call: MCPToolCall) -> MCPToolResult:
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
                    )
            )

    def xǁMCPToolRegistryǁexecute__mutmut_55(self, tool_call: MCPToolCall) -> MCPToolResult:
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
                    error_type=type(None).__name__,
                    error_message=str(e)
                )
            )

    def xǁMCPToolRegistryǁexecute__mutmut_56(self, tool_call: MCPToolCall) -> MCPToolResult:
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
                    error_message=str(None)
                )
            )
    
    xǁMCPToolRegistryǁexecute__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMCPToolRegistryǁexecute__mutmut_1': xǁMCPToolRegistryǁexecute__mutmut_1, 
        'xǁMCPToolRegistryǁexecute__mutmut_2': xǁMCPToolRegistryǁexecute__mutmut_2, 
        'xǁMCPToolRegistryǁexecute__mutmut_3': xǁMCPToolRegistryǁexecute__mutmut_3, 
        'xǁMCPToolRegistryǁexecute__mutmut_4': xǁMCPToolRegistryǁexecute__mutmut_4, 
        'xǁMCPToolRegistryǁexecute__mutmut_5': xǁMCPToolRegistryǁexecute__mutmut_5, 
        'xǁMCPToolRegistryǁexecute__mutmut_6': xǁMCPToolRegistryǁexecute__mutmut_6, 
        'xǁMCPToolRegistryǁexecute__mutmut_7': xǁMCPToolRegistryǁexecute__mutmut_7, 
        'xǁMCPToolRegistryǁexecute__mutmut_8': xǁMCPToolRegistryǁexecute__mutmut_8, 
        'xǁMCPToolRegistryǁexecute__mutmut_9': xǁMCPToolRegistryǁexecute__mutmut_9, 
        'xǁMCPToolRegistryǁexecute__mutmut_10': xǁMCPToolRegistryǁexecute__mutmut_10, 
        'xǁMCPToolRegistryǁexecute__mutmut_11': xǁMCPToolRegistryǁexecute__mutmut_11, 
        'xǁMCPToolRegistryǁexecute__mutmut_12': xǁMCPToolRegistryǁexecute__mutmut_12, 
        'xǁMCPToolRegistryǁexecute__mutmut_13': xǁMCPToolRegistryǁexecute__mutmut_13, 
        'xǁMCPToolRegistryǁexecute__mutmut_14': xǁMCPToolRegistryǁexecute__mutmut_14, 
        'xǁMCPToolRegistryǁexecute__mutmut_15': xǁMCPToolRegistryǁexecute__mutmut_15, 
        'xǁMCPToolRegistryǁexecute__mutmut_16': xǁMCPToolRegistryǁexecute__mutmut_16, 
        'xǁMCPToolRegistryǁexecute__mutmut_17': xǁMCPToolRegistryǁexecute__mutmut_17, 
        'xǁMCPToolRegistryǁexecute__mutmut_18': xǁMCPToolRegistryǁexecute__mutmut_18, 
        'xǁMCPToolRegistryǁexecute__mutmut_19': xǁMCPToolRegistryǁexecute__mutmut_19, 
        'xǁMCPToolRegistryǁexecute__mutmut_20': xǁMCPToolRegistryǁexecute__mutmut_20, 
        'xǁMCPToolRegistryǁexecute__mutmut_21': xǁMCPToolRegistryǁexecute__mutmut_21, 
        'xǁMCPToolRegistryǁexecute__mutmut_22': xǁMCPToolRegistryǁexecute__mutmut_22, 
        'xǁMCPToolRegistryǁexecute__mutmut_23': xǁMCPToolRegistryǁexecute__mutmut_23, 
        'xǁMCPToolRegistryǁexecute__mutmut_24': xǁMCPToolRegistryǁexecute__mutmut_24, 
        'xǁMCPToolRegistryǁexecute__mutmut_25': xǁMCPToolRegistryǁexecute__mutmut_25, 
        'xǁMCPToolRegistryǁexecute__mutmut_26': xǁMCPToolRegistryǁexecute__mutmut_26, 
        'xǁMCPToolRegistryǁexecute__mutmut_27': xǁMCPToolRegistryǁexecute__mutmut_27, 
        'xǁMCPToolRegistryǁexecute__mutmut_28': xǁMCPToolRegistryǁexecute__mutmut_28, 
        'xǁMCPToolRegistryǁexecute__mutmut_29': xǁMCPToolRegistryǁexecute__mutmut_29, 
        'xǁMCPToolRegistryǁexecute__mutmut_30': xǁMCPToolRegistryǁexecute__mutmut_30, 
        'xǁMCPToolRegistryǁexecute__mutmut_31': xǁMCPToolRegistryǁexecute__mutmut_31, 
        'xǁMCPToolRegistryǁexecute__mutmut_32': xǁMCPToolRegistryǁexecute__mutmut_32, 
        'xǁMCPToolRegistryǁexecute__mutmut_33': xǁMCPToolRegistryǁexecute__mutmut_33, 
        'xǁMCPToolRegistryǁexecute__mutmut_34': xǁMCPToolRegistryǁexecute__mutmut_34, 
        'xǁMCPToolRegistryǁexecute__mutmut_35': xǁMCPToolRegistryǁexecute__mutmut_35, 
        'xǁMCPToolRegistryǁexecute__mutmut_36': xǁMCPToolRegistryǁexecute__mutmut_36, 
        'xǁMCPToolRegistryǁexecute__mutmut_37': xǁMCPToolRegistryǁexecute__mutmut_37, 
        'xǁMCPToolRegistryǁexecute__mutmut_38': xǁMCPToolRegistryǁexecute__mutmut_38, 
        'xǁMCPToolRegistryǁexecute__mutmut_39': xǁMCPToolRegistryǁexecute__mutmut_39, 
        'xǁMCPToolRegistryǁexecute__mutmut_40': xǁMCPToolRegistryǁexecute__mutmut_40, 
        'xǁMCPToolRegistryǁexecute__mutmut_41': xǁMCPToolRegistryǁexecute__mutmut_41, 
        'xǁMCPToolRegistryǁexecute__mutmut_42': xǁMCPToolRegistryǁexecute__mutmut_42, 
        'xǁMCPToolRegistryǁexecute__mutmut_43': xǁMCPToolRegistryǁexecute__mutmut_43, 
        'xǁMCPToolRegistryǁexecute__mutmut_44': xǁMCPToolRegistryǁexecute__mutmut_44, 
        'xǁMCPToolRegistryǁexecute__mutmut_45': xǁMCPToolRegistryǁexecute__mutmut_45, 
        'xǁMCPToolRegistryǁexecute__mutmut_46': xǁMCPToolRegistryǁexecute__mutmut_46, 
        'xǁMCPToolRegistryǁexecute__mutmut_47': xǁMCPToolRegistryǁexecute__mutmut_47, 
        'xǁMCPToolRegistryǁexecute__mutmut_48': xǁMCPToolRegistryǁexecute__mutmut_48, 
        'xǁMCPToolRegistryǁexecute__mutmut_49': xǁMCPToolRegistryǁexecute__mutmut_49, 
        'xǁMCPToolRegistryǁexecute__mutmut_50': xǁMCPToolRegistryǁexecute__mutmut_50, 
        'xǁMCPToolRegistryǁexecute__mutmut_51': xǁMCPToolRegistryǁexecute__mutmut_51, 
        'xǁMCPToolRegistryǁexecute__mutmut_52': xǁMCPToolRegistryǁexecute__mutmut_52, 
        'xǁMCPToolRegistryǁexecute__mutmut_53': xǁMCPToolRegistryǁexecute__mutmut_53, 
        'xǁMCPToolRegistryǁexecute__mutmut_54': xǁMCPToolRegistryǁexecute__mutmut_54, 
        'xǁMCPToolRegistryǁexecute__mutmut_55': xǁMCPToolRegistryǁexecute__mutmut_55, 
        'xǁMCPToolRegistryǁexecute__mutmut_56': xǁMCPToolRegistryǁexecute__mutmut_56
    }
    
    def execute(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMCPToolRegistryǁexecute__mutmut_orig"), object.__getattribute__(self, "xǁMCPToolRegistryǁexecute__mutmut_mutants"), args, kwargs, self)
        return result 
    
    execute.__signature__ = _mutmut_signature(xǁMCPToolRegistryǁexecute__mutmut_orig)
    xǁMCPToolRegistryǁexecute__mutmut_orig.__name__ = 'xǁMCPToolRegistryǁexecute'


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
