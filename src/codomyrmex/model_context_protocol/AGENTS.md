# Codomyrmex Agents — src/codomyrmex/model_context_protocol

## Signposting
- **Parent**: [codomyrmex](../AGENTS.md)
- **Self**: [Model Context Protocol Agents](AGENTS.md)
- **Children**:
    - [docs](docs/AGENTS.md)
    - [tests](tests/AGENTS.md)
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

Foundation module defining the Model Context Protocol (MCP) for standardized AI communication within the Codomyrmex platform. This module establishes the schemas, interfaces, and standards that enable consistent interaction between AI agents, language models, and platform components.

The model_context_protocol module serves as the communication backbone, ensuring reliable and structured AI interactions across the entire platform.

## Module Overview

### Key Capabilities
- **Protocol Definition**: Comprehensive MCP specification documents
- **Schema Validation**: Pydantic models for message structure validation
- **Tool Specifications**: Standardized tool calling interfaces for AI agents
- **Error Handling**: Structured error reporting and recovery mechanisms
- **Type Safety**: Type-safe message construction and validation

### Key Features
- Complete MCP specification with examples and guidelines
- Pydantic-based schema validation for all MCP messages
- Tool call and result message structures
- Error detail specifications with context preservation
- Integration patterns for AI agent development

## Function Signatures

### Pydantic Schema Classes

```python
class MCPErrorDetail(BaseModel):
    """Standard structure for detailed error information in MCP responses."""

    error_type: str = Field(
        ...,
        description="Unique code or type for the error (e.g., ValidationError, FileNotFoundError)"
    )
    error_message: str = Field(
        ...,
        description="Descriptive message explaining the error"
    )
    error_details: Optional[Union[dict[str, Any], str]] = Field(
        None,
        description="Optional structured details or string with additional error info"
    )
```

Pydantic model for structured error reporting in MCP responses.

**Fields:**
- `error_type` (str, required): Error classification/code
- `error_message` (str, required): Human-readable error description
- `error_details` (Optional[Union[dict, str]]): Additional context (structured or text)

**Usage**: Include in `MCPToolResult` when `status` indicates failure

```python
class MCPToolCall(BaseModel):
    """Represents a call to an MCP tool."""

    tool_name: str = Field(
        ...,
        description="Unique invocation name of the tool"
    )
    arguments: dict[str, Any] = Field(
        ...,
        description="Arguments for the tool (schema defined by specific tool)"
    )

    model_config = ConfigDict(extra="allow")
```

Pydantic model for tool invocation requests.

**Fields:**
- `tool_name` (str, required): Name of tool to invoke
- `arguments` (dict[str, Any], required): Tool-specific parameters

**Configuration**: Allows extra fields (`extra="allow"`) for tool-specific validation

```python
class MCPToolResult(BaseModel):
    """Represents the result of an MCP tool execution."""

    status: str = Field(
        ...,
        description="Outcome of tool execution (success, failure, no_change_needed)"
    )
    data: Optional[dict[str, Any]] = Field(
        None,
        description="Output data from tool if successful (tool-specific schema)"
    )
    error: Optional[MCPErrorDetail] = Field(
        None,
        description="Error details if execution failed"
    )
    explanation: Optional[str] = Field(
        None,
        description="Human-readable explanation of the result"
    )

    model_config = ConfigDict(extra="allow")
```

Pydantic model for tool execution results with validation.

**Fields:**
- `status` (str, required): Execution outcome indicator
- `data` (Optional[dict], optional): Success data (None on failure)
- `error` (Optional[MCPErrorDetail], optional): Error details (required on failure)
- `explanation` (Optional[str], optional): Contextual explanation

**Validation Rules**:
- If `status` contains "fail", `error` must be populated
- If `status` contains "fail", `data` must be None
- If `status` contains "success", `data` may be None (for side-effect-only tools)

**Validators:**

```python
@field_validator("error")
@classmethod
def check_error_if_failed(cls, v, info) -> Optional[MCPErrorDetail]
```

Validates that `error` is populated when status indicates failure.

```python
@field_validator("data")
@classmethod
def check_data_if_success(cls, v, info) -> Optional[dict[str, Any]]
```

Validates that `data` is None when status indicates failure.

## Active Components

### Core Implementation
- `__init__.py` – Module initialization and public API exports
- `mcp_schemas.py` – Pydantic models for MCP message validation

### Documentation
- `README.md` – Module usage and overview
- `API_SPECIFICATION.md` – Complete API documentation for schemas
- `MCP_TOOL_SPECIFICATION.md` – Tool specification standards
- `USAGE_EXAMPLES.md` – Practical usage demonstrations
- `SECURITY.md` – Security considerations for AI communications
- `CHANGELOG.md` – Version history and updates

### Supporting Files
- `requirements.txt` – Module dependencies (pydantic)
- `docs/` – Additional documentation
- `tests/` – Comprehensive test suite


### Additional Files
- `SPEC.md` – Spec Md
- `__pycache__` –   Pycache  
- `docs` – Docs
- `tests` – Tests

## Operating Contracts

### Universal MCP Protocols

All AI communication within the Codomyrmex platform must:

1. **Follow MCP Standards** - Adhere to defined message schemas and structures
2. **Validate Messages** - Use provided schemas for message validation
3. **Handle Errors Properly** - Use structured error reporting with context
4. **Preserve Tool Interfaces** - Maintain compatibility with existing tool specifications
5. **Ensure Type Safety** - Use typed interfaces for reliable communication

### Module-Specific Guidelines

#### Schema Usage
- Import and use Pydantic models for all MCP message construction
- Validate messages before transmission to ensure compliance
- Handle validation errors gracefully with informative feedback
- Extend schemas carefully to maintain backward compatibility

#### Protocol Compliance
- Follow MCP specification for tool calling and result handling
- Include proper error details in failure responses
- Preserve message context across request/response cycles
- Support both synchronous and asynchronous communication patterns

#### Tool Specifications
- Document all tools using the standardized MCP format
- Include parameter schemas and return value specifications
- Provide usage examples and error scenarios
- Maintain tool interface stability across versions

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)

### Module Documentation
- **Module Overview**: [README.md](README.md) - Complete module documentation
- **API Reference**: [API_SPECIFICATION.md](API_SPECIFICATION.md) - Detailed API specification (if applicable)
- **Usage Examples**: [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md) - Practical usage demonstrations (if applicable)

### Platform Navigation
- **Parent Directory**: [codomyrmex](../README.md) - Package overview
- **Project Root**: [README](../../../README.md) - Main project documentation
- **Source Root**: [src](../../README.md) - Source code documentation