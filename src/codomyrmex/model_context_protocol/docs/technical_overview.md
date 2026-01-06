# Model Context Protocol - Technical Overview

## 1. Introduction

This document provides a detailed technical overview of the Model Context Protocol (MCP) within the Codomyrmex project. MCP is designed as a standardized communication interface facilitating interaction between AI models/agents and various software tools. Its primary goals are to ensure interoperability, enable robust tool usage by AI, and provide a clear framework for context and data exchange.

This overview elaborates on the concepts introduced in the main `README.md` and the `MCP_TOOL_SPECIFICATION.md` (meta-specification).

## 2. Core Purpose and Design Philosophy

MCP is built on the following core principles:

-   **Simplicity and Clarity**: Protocol messages and tool specifications should be easy to understand and implement.
-   **Flexibility and Extensibility**: The protocol should accommodate a wide variety of tools and allow for future evolution without breaking existing implementations unnecessarily.
-   **Machine Readability**: Tool specifications and message schemas should be structured to allow for automated parsing, validation, and potentially code generation for client/server interactions. JSON Schema is the recommended standard for this.
-   **Discoverability**: While full dynamic discovery is a more advanced feature, the standardized specification format aids in understanding available tools.
-   **Robustness**: Clear error reporting and versioning are essential for building reliable systems.

## 3. Formal Data Structure Definitions

### 3.1. MCP Tool Call Schema

**Python Implementation**: `MCPToolCall` (Pydantic model in `mcp_schemas.py`)

**JSON Schema**:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "MCP Tool Call",
  "description": "Standard structure for an AI agent to call a tool.",
  "type": "object",
  "properties": {
    "tool_name": {
      "type": "string",
      "description": "The unique invocation name of the tool (e.g., 'module_name.tool_name').",
      "pattern": "^[a-z0-9_]+(\\.[a-z0-9_]+)+$"
    },
    "arguments": {
      "type": "object",
      "description": "An object containing the arguments for the tool. The schema for this object is defined by the specific tool being called.",
      "additionalProperties": true
    }
  },
  "required": ["tool_name", "arguments"],
  "additionalProperties": false
}
```

**Pydantic Model**:
```python
from codomyrmex.model_context_protocol.mcp_schemas import MCPToolCall

# Fields:
# - tool_name: str (required) - Unique invocation name
# - arguments: dict[str, Any] (required) - Tool-specific parameters
```

**Serialization Format**: JSON (UTF-8 encoded)

**Example**:
```json
{
  "tool_name": "ai_code_editing.generate_code",
  "arguments": {
    "prompt": "Create a Python function to sum a list of numbers.",
    "language": "python",
    "context_code": "# This is where the function should be placed"
  }
}
```

### 3.2. MCP Tool Result Schema

**Python Implementation**: `MCPToolResult` (Pydantic model in `mcp_schemas.py`)

**JSON Schema**:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "MCP Tool Result",
  "description": "Standard structure for a tool to return results to an AI agent.",
  "type": "object",
  "properties": {
    "status": {
      "type": "string",
      "description": "The outcome of the tool execution.",
      "enum": ["success", "failure", "no_change_needed", "partial_success"],
      "default": "success"
    },
    "data": {
      "type": ["object", "null"],
      "description": "The output data from the tool if successful. Schema is tool-specific.",
      "additionalProperties": true
    },
    "error": {
      "$ref": "#/definitions/MCPErrorDetail",
      "description": "Details of the error if execution failed."
    },
    "explanation": {
      "type": ["string", "null"],
      "description": "Optional human-readable explanation of the result."
    }
  },
  "required": ["status"],
  "definitions": {
    "MCPErrorDetail": {
      "type": "object",
      "properties": {
        "error_type": {
          "type": "string",
          "description": "A unique code or type for the error (e.g., ValidationError, FileNotFoundError)."
        },
        "error_message": {
          "type": "string",
          "description": "A descriptive message explaining the error."
        },
        "error_details": {
          "oneOf": [
            {"type": "object", "additionalProperties": true},
            {"type": "string"},
            {"type": "null"}
          ],
          "description": "Optional structured details or a string containing more info about the error."
        }
      },
      "required": ["error_type", "error_message"]
    }
  }
}
```

**Pydantic Model**:
```python
from codomyrmex.model_context_protocol.mcp_schemas import MCPToolResult, MCPErrorDetail

# Fields:
# - status: str (required) - Execution outcome
# - data: Optional[dict[str, Any]] - Tool-specific output data
# - error: Optional[MCPErrorDetail] - Error information if failed
# - explanation: Optional[str] - Human-readable explanation
```

**Validation Rules**:
- If `status` contains "failure", `error` field must be populated
- If `status` contains "failure", `data` field should be null or omitted
- If `status` is "success", `data` may be null for tools with no specific output

**Example Success**:
```json
{
  "status": "success",
  "data": {
    "generated_code": "def sum_numbers(numbers):
    return sum(numbers)",
    "language": "python",
    "lines_generated": 2
  },
  "explanation": "Generated Python function to sum a list of numbers.",
  "error": null
}
```

**Example Failure**:
```json
{
  "status": "failure",
  "data": null,
  "error": {
    "error_type": "ValidationError",
    "error_message": "Invalid prompt: prompt cannot be empty",
    "error_details": {
      "parameter": "prompt",
      "provided_value": "",
      "constraint": "non-empty string"
    }
  },
  "explanation": "The tool call failed due to invalid input parameters."
}
```

### 3.3. MCP Error Detail Schema

**Python Implementation**: `MCPErrorDetail` (Pydantic model in `mcp_schemas.py`)

**JSON Schema**:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "MCP Error Detail",
  "description": "Standard structure for detailed error information in MCP responses.",
  "type": "object",
  "properties": {
    "error_type": {
      "type": "string",
      "description": "A unique code or type for the error.",
      "examples": ["ValidationError", "FileNotFoundError", "AuthenticationError", "ResourceNotFound", "ToolExecutionError", "ApiLimitExceeded"]
    },
    "error_message": {
      "type": "string",
      "description": "A descriptive message explaining the error."
    },
    "error_details": {
      "oneOf": [
        {"type": "object", "additionalProperties": true},
        {"type": "string"},
        {"type": "null"}
      ],
      "description": "Optional structured details or a string containing more info about the error."
    }
  },
  "required": ["error_type", "error_message"]
}
```

**Standard Error Types**:
- `ValidationError`: Input validation failed
- `FileNotFoundError`: Required file not found
- `AuthenticationError`: Authentication/authorization failure
- `ResourceNotFound`: Requested resource does not exist
- `ToolExecutionError`: Tool execution failed (generic)
- `ApiLimitExceeded`: API rate limit reached
- `TimeoutError`: Operation timed out
- `PermissionError`: Insufficient permissions

## 4. Tool Specification Format

### 4.1. Canonical Template Structure

Every `MCP_TOOL_SPECIFICATION.md` file must follow this structure:

1. **Tool Purpose and Description**
   - Clear explanation of what the tool does
   - Use cases and operational notes
   - Version number (semantic versioning)

2. **Invocation Name**
   - Unique, machine-readable identifier
   - Format: `module_name.tool_name`
   - Example: `ai_code_editing.generate_code`

3. **Input Schema (Parameters)**
   - Markdown table with parameter details
   - JSON Schema definition for `arguments` object
   - Required vs optional parameters clearly marked

4. **Output Schema (Return Value)**
   - Markdown table with field details
   - JSON Schema definition for `data` object (on success)
   - Example output structures

5. **Error Handling**
   - List of possible error conditions
   - Error types and messages
   - Error details structure

6. **Idempotency**
   - Clear statement on idempotency
   - Behavior on repeated calls

7. **Usage Examples**
   - Complete JSON examples of tool calls
   - Example tool results (success and failure)
   - Integration examples

8. **Security Considerations**
   - Security risks and mitigations
   - Input validation requirements
   - Access control considerations

### 4.2. JSON Schema Requirements

All tools **must** provide JSON Schema definitions for:
- Input parameters (`arguments` object)
- Output data (`data` object in success results)

**Minimum Schema Elements**:
- `type`: Data type (object, string, integer, boolean, array, null)
- `description`: Human-readable description
- `required`: Array of required property names (for objects)
- `properties`: Property definitions (for objects)
- `items`: Schema for array elements
- `examples`: Example values (recommended)

## 5. Versioning Strategy

### 5.1. Protocol Versioning

The Model Context Protocol itself follows semantic versioning:

- **Major Version (X.0.0)**: Breaking changes to protocol structure
- **Minor Version (0.X.0)**: New features, backward-compatible
- **Patch Version (0.0.X)**: Bug fixes, backward-compatible

**Current Protocol Version**: `1.0.0`

**Version Components**:
- Core message structures (Tool Call, Tool Result)
- Error reporting format
- Meta-specification requirements

### 5.2. Tool Versioning

Each individual tool has its own version, independent of the protocol version:

**Version Format**: `X.Y.Z` (semantic versioning)

**Breaking Changes** (Major version increment):
- Adding required parameters
- Removing parameters
- Changing parameter types
- Incompatible changes to output schema

**Non-Breaking Changes** (Minor/Patch increment):
- Adding optional parameters
- Adding new fields to output (without removing existing ones)
- Bug fixes
- Documentation improvements

**Version Declaration**:
Tools must declare their version in their `MCP_TOOL_SPECIFICATION.md`:
```markdown
## Tool: `module_name.tool_name`

**Version**: 1.2.3
```

### 5.3. Version Compatibility

- **Protocol Compatibility**: Tools written for MCP v1.0.0 should work with MCP v1.x.x
- **Tool Versioning**: Agents should be aware of tool versions and handle compatibility
- **Migration Strategy**: Breaking changes should include migration guides

## 6. Serialization Guidelines

### 6.1. JSON Encoding

- **Encoding**: UTF-8
- **Formatting**: Pretty-print for documentation, compact for transmission
- **Date/Time**: ISO 8601 format (e.g., `2024-01-15T10:30:00Z`)
- **Numbers**: Use JSON number type (no leading zeros, no octal/hex)

### 6.2. Data Type Mapping

| Python Type | JSON Type | Notes |
|------------|-----------|-------|
| `str` | `string` | UTF-8 encoded |
| `int` | `number` | Integer |
| `float` | `number` | Floating point |
| `bool` | `boolean` | true/false |
| `list` | `array` | Ordered sequence |
| `dict` | `object` | Key-value pairs |
| `None` | `null` | Null value |
| `datetime` | `string` | ISO 8601 format |
| `Path` | `string` | String representation |

### 6.3. Pydantic Serialization

The MCP schemas use Pydantic for validation and serialization:

```python
from codomyrmex.model_context_protocol.mcp_schemas import MCPToolCall, MCPToolResult

# Serialize to JSON
tool_call = MCPToolCall(tool_name="example.tool", arguments={"param": "value"})
json_str = tool_call.model_dump_json(indent=2)

# Deserialize from JSON
tool_call = MCPToolCall.model_validate_json(json_str)

# Serialize to dict
tool_dict = tool_call.model_dump()
```

## 7. Interaction Patterns

### 7.1. Synchronous Request-Response

The primary interaction pattern is synchronous:

1. Agent constructs `MCPToolCall`
2. Agent sends call to tool (via function call, HTTP, etc.)
3. Tool executes operation
4. Tool constructs `MCPToolResult`
5. Tool returns result to agent

**Flow Diagram**:
```
Agent -> [MCPToolCall] -> Tool -> [Execution] -> [MCPToolResult] -> Agent
```

### 7.2. Error Handling Flow

```
Agent -> [MCPToolCall] -> Tool
                        |
                        v
                   [Validation]
                        |
                        v
              [Valid?] -> No -> [MCPToolResult(status="failure", error={...})]
                        |
                       Yes
                        |
                        v
                   [Execution]
                        |
                        v
              [Success?] -> No -> [MCPToolResult(status="failure", error={...})]
                        |
                       Yes
                        |
                        v
              [MCPToolResult(status="success", data={...})]
```

## 8. Standard MCP Message Structures

### 8.1. Tool Call Message

This is the message an AI agent sends to invoke a specific tool.

**Format**: JSON Object

**Key Fields**:
- `tool_name` (string, required): The unique invocation name of the tool to be called (e.g., `"ai_code_editing.generate_code_snippet"`). This name must match the `Invocation Name` defined in the tool's `MCP_TOOL_SPECIFICATION.md`.
- `arguments` (object, required): A JSON object containing the parameters for the tool, as specified by the tool's `Input Schema`. The keys in this object are the parameter names, and the values are the arguments provided by the agent.

**Conceptual JSON Schema for a Tool Call Message**:

See Section 3.1 for the complete JSON Schema definition.

**Example Tool Call Message**:

```json
{
  "tool_name": "ai_code_editing.generate_code",
  "arguments": {
    "prompt": "Create a Python function to sum a list of numbers.",
    "language": "python",
    "context_code": "# This is where the function should be placed"
  }
}
```

### 8.2. Tool Result Message

This is the message a tool sends back to the AI agent after processing a tool call.

**Format**: JSON Object

**Key Fields**:
- `status` (string, required): Indicates the outcome of the tool execution (e.g., "success", "failure", "no_change_needed").
- `data` (object | null, optional): The output data from the tool if successful. The structure of this object is tool-specific and should match the tool's `Output Schema`.
- `error` (object | null, optional): Details of the error if execution failed. Should be an `MCPErrorDetail` object.
- `explanation` (string | null, optional): Optional human-readable explanation of the result.

**Conceptual JSON Schema for a Tool Result Message**:

See Section 3.2 for the complete JSON Schema definition.

**Example Successful Tool Result Message**:

```json
{
  "status": "success",
  "data": {
    "generated_code": "def sum_numbers(numbers):
    return sum(numbers)",
    "language": "python"
  },
  "explanation": "Generated Python function to sum a list of numbers.",
  "error": null
}
```

**Example Failure Tool Result Message**:

```json
{
  "status": "failure",
  "data": null,
  "error": {
    "error_type": "ValidationError",
    "error_message": "Invalid prompt: prompt cannot be empty",
    "error_details": {
      "parameter": "prompt",
      "provided_value": ""
    }
  },
  "explanation": "The tool call failed due to invalid input parameters."
}
```

### 8.3. Standard Error Object Structure

As referenced in the Tool Result schema, a standard error object is recommended when `status` is `"failure"`:

-   **`error_type`** (string, required): A machine-readable string identifying the general category of the error (e.g., `"ValidationError"`, `"AuthenticationError"`, `"ResourceNotFound"`, `"ToolExecutionError"`, `"ApiLimitExceeded"`). Tools should try to use a consistent set of error types.
-   **`error_message`** (string, required): A human-readable message describing the error.
-   **`error_details`** (object | string, optional): Provides additional, structured (or string) information about the error. For a `ValidationError`, this might include which parameter failed validation and why. For a `FileNotFoundError`, it might include the path that was not found.

## 9. Design Rationale for Key Decisions

-   **JSON as Primary Data Format**: Chosen for its ubiquity, human readability, and wide support across programming languages and platforms.
-   **JSON Schema for Definitions**: Provides a standardized and robust way to define and validate the structure of `arguments` and `data` objects, enabling clear contracts and automated checks.
-   **Pydantic Models for Python**: Provides runtime validation, type safety, and automatic serialization/deserialization.
-   **Emphasis on Module-Owned Tool Specifications**: Each module is responsible for defining and versioning its own tools. This decentralized approach scales better and aligns with the modular architecture of Codomyrmex. The `model_context_protocol` module provides the *template* and *rules* for these specifications.
-   **Explicit `status` Field**: Ensures that the success or failure of a tool call is always clearly and immediately communicated.
-   **Separate Error Object**: Allows for structured error information while keeping the main result structure clean.

## 10. Future Considerations

-   **Asynchronous Operations**: Defining patterns for long-running tools, including how to initiate them, check status, and retrieve results later.
-   **Streaming**: Support for tools that can stream partial results or logs back to the agent.
-   **Tool Discovery**: Mechanisms for agents to dynamically discover available tools and their specifications (e.g., via a central registry or by querying modules).
-   **More Complex Data Types**: Guidelines for handling binary data or other complex data types in tool arguments or results.
-   **Standardized Context Object**: Defining a more formal schema for common contextual information that might be passed to tools or agents.
-   **Batch Tool Calls**: Support for invoking multiple tools in a single request.

## 11. Implementation Guidelines

### 11.1. Tool Implementation Checklist

When implementing an MCP tool:

- [ ] Create `MCP_TOOL_SPECIFICATION.md` following the canonical template
- [ ] Define JSON Schema for input parameters
- [ ] Define JSON Schema for output data
- [ ] Implement tool function with proper error handling
- [ ] Create MCP wrapper function that accepts `MCPToolCall` and returns `MCPToolResult`
- [ ] Add comprehensive error handling with specific error types
- [ ] Document idempotency behavior
- [ ] Include security considerations
- [ ] Provide usage examples
- [ ] Version the tool appropriately

### 11.2. Validation Best Practices

- Use Pydantic models for runtime validation
- Validate tool-specific `arguments` against JSON Schema
- Return structured errors with `MCPErrorDetail`
- Log all tool invocations for audit purposes
- Implement rate limiting for tools that call external APIs

## 12. References

- [MCP Tool Specification Meta-Specification](../MCP_TOOL_SPECIFICATION.md) - Authoritative rules for tool specifications
- [Canonical Tool Template](../../module_template/MCP_TOOL_SPECIFICATION.md) - Starting point for new tools
- [API Specification](../API_SPECIFICATION.md) - Python API for MCP utilities
- [Usage Examples](../USAGE_EXAMPLES.md) - Practical implementation examples
- [JSON Schema Specification](https://json-schema.org/) - Standard for schema definitions
- [Pydantic Documentation](https://docs.pydantic.dev/) - Python data validation library

This technical overview provides the current state and foundational principles of the Model Context Protocol. It will evolve as the Codomyrmex project matures.

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../docs/README.md)
- **Home**: [Root README](../../../README.md)
