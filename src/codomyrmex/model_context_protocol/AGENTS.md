# Codomyrmex Agents — src/codomyrmex/model_context_protocol

## Signposting
- **Parent**: [codomyrmex](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - [docs](docs/AGENTS.md)
    - [tests](tests/AGENTS.md)
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose
Defines the standard schemas (Model Context Protocol) for communication between AI agents and platform tools. Provides the syntax layer of the agent system with strict JSON schemas for `ToolCall` and `ToolResult`, ensuring interoperability and agnosticism to underlying LLM providers. Includes Pydantic models for validating and constructing MCP messages.

## Active Components
- `API_SPECIFICATION.md` – Detailed API specification
- `CHANGELOG.md` – Version history
- `MCP_TOOL_SPECIFICATION.md` – MCP tool specification (meta-specification)
- `README.md` – Project file
- `SECURITY.md` – Security considerations
- `SPEC.md` – Project file
- `USAGE_EXAMPLES.md` – Usage examples
- `__init__.py` – Module exports and public API
- `docs/` – Directory containing docs components
- `mcp_schemas.py` – Pydantic models for MCP message structures
- `requirements.txt` – Project file
- `tests/` – Directory containing tests components

## Key Classes and Functions

### MCPToolCall (`mcp_schemas.py`)
- `MCPToolCall` (Pydantic model) – Standard structure for tool call requests:
  - `tool_name: str` – Name of the tool to call
  - `parameters: dict[str, Any]` – Tool parameters
  - `request_id: Optional[str]` – Optional request identifier
  - `metadata: Optional[dict[str, Any]]` – Optional metadata

### MCPToolResult (`mcp_schemas.py`)
- `MCPToolResult` (Pydantic model) – Standard structure for tool call results:
  - `success: bool` – Whether the tool call succeeded
  - `result: Optional[Any]` – Tool execution result
  - `error: Optional[MCPErrorDetail]` – Error details if execution failed
  - `request_id: Optional[str]` – Request identifier (matches MCPToolCall)
  - `metadata: Optional[dict[str, Any]]` – Optional metadata

### MCPErrorDetail (`mcp_schemas.py`)
- `MCPErrorDetail` (Pydantic model) – Standard structure for detailed error information:
  - `error_type: str` – Machine-readable error code/type (e.g., "ValidationError", "FileNotFoundError")
  - `error_message: str` – Human-readable error message
  - `error_details: Optional[Union[Dict[str, Any], str]]` – Additional structured or unstructured error information

### Module Exports (`__init__.py`)
- `MCPToolCall` – Tool call request model
- `MCPToolResult` – Tool call result model
- `MCPErrorDetail` – Error detail model

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **📁 Parent Directory**: [codomyrmex](../README.md) - Parent directory documentation
- **🏠 Project Root**: [README](../../../README.md) - Main project documentation