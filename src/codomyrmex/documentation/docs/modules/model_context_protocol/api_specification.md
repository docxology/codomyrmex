# Model Context Protocol - API Specification

## Introduction

The `model_context_protocol` module primarily defines the Model Context Protocol (MCP) itself through specification documents. However, it also provides a Python module, `model_context_protocol.mcp_schemas`, containing Pydantic models. These models serve as a reference implementation and utility for working with MCP message structures in Python-based Codomyrmex modules.

This API specification details these Pydantic models, which constitute the programmable interface of this module.

## Python Module: `codomyrmex.model_context_protocol.schemas.mcp_schemas`

This module provides Pydantic models for validating and constructing MCP messages.

To use these models, import them into your Python code:
```python
from codomyrmex.model_context_protocol import MCPToolCall, MCPToolResult, MCPErrorDetail
```

Or from the schemas submodule directly:
```python
from codomyrmex.model_context_protocol.schemas.mcp_schemas import MCPToolCall, MCPToolResult, MCPErrorDetail
```

### 1. Pydantic Model: `MCPErrorDetail`

-   **Description**: Represents the standard structure for detailed error information within an `MCPToolResult` when a tool execution fails.
-   **Source File**: `model_context_protocol/schemas/mcp_schemas.py`

-   **Fields**:
    -   `error_type` (str, required): A unique code or type for the error (e.g., `"ValidationError"`, `"FileNotFoundError"`).
        -   *Description*: Machine-readable identifier for the category of error.
    -   `error_message` (str, required): A descriptive message explaining the error.
        -   *Description*: Human-readable explanation of what went wrong.
    -   `error_details` (Optional[Union[Dict[str, Any], str]], optional): Provides additional, structured (as a dictionary) or unstructured (as a string) information about the error.
        -   *Description*: Can contain context-specific details, such as which parameter failed validation or the path of a missing file.
        -   *Default*: `None`

-   **Example Initialization**:
    ```python
    error_info = MCPErrorDetail(
        error_type="ResourceNotFound",
        error_message="The requested resource could not be located.",
        error_details={"resource_id": "xyz-123"}
    )
    ```

### 2. Pydantic Model: `MCPToolCall`

-   **Description**: Represents an MCP Tool Call message sent by an AI agent to invoke a specific tool.
-   **Source File**: `model_context_protocol/schemas/mcp_schemas.py`

-   **Fields**:
    -   `tool_name` (str, required): The unique invocation name of the tool to be called (e.g., `"ai_code_editing.generate_code_snippet"`).
        -   *Description*: Must match the `Invocation Name` defined in the tool's `MCP_TOOL_SPECIFICATION.md`.
    -   `arguments` (Dict[str, Any], required): A dictionary containing the parameters for the tool, as specified by the tool's `Input Schema`.
        -   *Description*: Keys are parameter names, values are the arguments. The structure of this dictionary is tool-specific and should be validated by the tool itself or a tool-specific argument model.

-   **Configuration**:
    -   `Config.extra = 'allow'`: Allows arbitrary fields within the `arguments` dictionary, as these are tool-specific. Further validation of `arguments` should be performed by the tool based on its own specification.

-   **Example Initialization**:
    ```python
    tool_call_msg = MCPToolCall(
        tool_name="file_utility.read_file_content",
        arguments={
            "file_path": "/path/to/file.txt",
            "max_chars": 1024
        }
    )
    ```

### 3. Pydantic Model: `MCPToolResult`

-   **Description**: Represents an MCP Tool Result message sent back by a tool to the AI agent after execution.
-   **Source File**: `model_context_protocol/schemas/mcp_schemas.py`

-   **Fields**:
    -   `status` (str, required): Indicates the outcome of the tool execution.
        -   *Description*: Common values include `"success"`, `"failure"`, `"no_change_needed"`. Refer to `docs/technical_overview.md` for more details.
    -   `data` (Optional[Dict[str, Any]], optional): If `status` indicates success, this dictionary contains the primary output of the tool, structured according to the tool's `Output Schema`.
        -   *Description*: Tool-specific payload on successful execution. Should be `None` or omitted if `status` is `"failure"`.
        -   *Default*: `None`
    -   `error` (Optional[`MCPErrorDetail`], optional): If `status` is `"failure"`, this field contains an `MCPErrorDetail` object with details about the error.
        -   *Description*: Should be populated if execution failed. Should be `None` or omitted if `status` is `"success"` (though warnings could theoretically be placed here if a more nuanced status system is developed).
        -   *Default*: `None`
    -   `explanation` (Optional[str], optional): A human-readable explanation of the results or changes made.
        -   *Description*: Often provided if the tool uses an LLM or if a summary is helpful.
        -   *Default*: `None`

-   **Validators**:
    -   `check_error_if_failed`: Ensures that the `error` field is populated if `status` indicates failure.
    -   `check_data_if_success`: Ensures that the `data` field is `None` or omitted if `status` indicates failure (data should not be present on failure).

-   **Configuration**:
    -   `Config.extra = 'allow'`: Allows additional fields within the `data` dictionary, as the `data` payload is tool-specific. Further validation of `data` should be performed by the consumer based on the tool's `Output Schema`.

-   **Example Initialization (Success)**:
    ```python
    success_result = MCPToolResult(
        status="success",
        data={"file_content": "Hello World"},
        explanation="Read file successfully."
    )
    ```

-   **Example Initialization (Failure)**:
    ```python
    failure_result = MCPToolResult(
        status="failure",
        error=MCPErrorDetail(
            error_type="FileNotFound",
            error_message="The target file was not found."
        )
    )
    ```

## Data Models

The Pydantic models (`MCPErrorDetail`, `MCPToolCall`, `MCPToolResult`, `MCPMessage`, `MCPToolRegistry`) described above are the primary data models provided by this module's API. Additionally, the module exports `MCPServer` and `MCPServerConfig` for running an MCP server, and the `mcp_tool` decorator from `decorators.py` for registering functions as MCP tools.

## Authentication & Authorization

Not applicable to these Pydantic models themselves. Authentication and authorization are concerns for the systems that *use* MCP to dispatch tool calls (see `SECURITY.md`).

## Rate Limiting

Not applicable to these Pydantic models.

## Versioning

-   The Pydantic models in `model_context_protocol.mcp_schemas` will be versioned according to the overall version of the `model_context_protocol` module (see `CHANGELOG.md`).
-   Changes to these models (e.g., adding required fields, removing fields, changing types in a non-backward-compatible way) would constitute a breaking change and necessitate a major version increment for the `model_context_protocol` module. 
## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../docs/README.md)
- **Home**: [Root README](../../../README.md)
