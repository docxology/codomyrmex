# Codomyrmex Agents — src/codomyrmex/agents/opencode

## Signposting
- **Parent**: [agents](../AGENTS.md)
- **Self**: [OpenCode Agents](AGENTS.md)
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

OpenCode submodule providing integration with OpenCode CLI tool. This includes a client for interacting with OpenCode CLI and integration adapters for Codomyrmex modules.

## Function Signatures

### OpenCodeClient

Implements `AgentInterface` with OpenCode CLI integration.

```python
def __init__(self, config: Optional[dict[str, Any]] = None)
```

Initialize OpenCode client.

**Parameters:**
- `config` (Optional[dict[str, Any]]): Optional configuration override

```python
def _execute_impl(self, request: AgentRequest) -> AgentResponse
```

Execute OpenCode command.

**Parameters:**
- `request` (AgentRequest): Agent request

**Returns:** `AgentResponse` - Agent response

```python
def _stream_impl(self, request: AgentRequest) -> Iterator[str]
```

Stream OpenCode command output.

**Parameters:**
- `request` (AgentRequest): Agent request

**Yields:** `str` - Chunks of output

```python
def initialize_project(self, project_path: Optional[Path] = None) -> dict[str, Any]
```

Initialize OpenCode for a project.

**Parameters:**
- `project_path` (Optional[Path]): Optional project path (uses working_dir if not provided)

**Returns:** `dict[str, Any]` - Initialization result dictionary

```python
def get_opencode_version(self) -> dict[str, Any]
```

Get OpenCode version information.

**Returns:** `dict[str, Any]` - Version information dictionary

### OpenCodeIntegrationAdapter

```python
def adapt_for_ai_code_editing(self, prompt: str, language: str = "python", **kwargs) -> str
```

Adapt OpenCode for AI code editing module.

**Parameters:**
- `prompt` (str): Code generation prompt
- `language` (str): Programming language
- `**kwargs`: Additional parameters

**Returns:** `str` - Generated code

```python
def adapt_for_llm(self, messages: list[dict], model: str = None, **kwargs) -> dict
```

Adapt OpenCode for LLM module.

**Parameters:**
- `messages` (list[dict]): Conversation messages
- `model` (str): Model name (not used for OpenCode)
- `**kwargs`: Additional parameters

**Returns:** `dict` - Completion result dictionary

```python
def adapt_for_code_execution(self, code: str, language: str = "python", **kwargs) -> dict[str, Any]
```

Adapt OpenCode for code execution sandbox.

**Parameters:**
- `code` (str): Code to execute
- `language` (str): Programming language
- `**kwargs`: Additional parameters

**Returns:** `dict[str, Any]` - Execution result dictionary

## Navigation Links

- **Human Documentation**: [README.md](README.md)
- **Parent Module**: [agents](../AGENTS.md)

## Active Components
- `README.md` - Component file.
- `SPEC.md` - Component file.
- `__init__.py` - Component file.
- `opencode_client.py` - Component file.
- `opencode_integration.py` - Component file.

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update task queues when necessary.

## Detailed Architecture and Implementation

The implementation of this component follows the core principles of the Codomyrmex ecosystem: modularity, performance, and reliability. By adhering to standardized interfaces, this module ensures seamless integration with the broader platform.

### Design Principles
1.  **Strict Modularity**: Each component is isolated and communicates via well-defined APIs.
2.  **Performance Optimization**: Implementation leverages lazy loading and intelligent caching to minimize resource overhead.
3.  **Error Resilience**: Robust exception handling ensures system stability even under unexpected conditions.
4.  **Extensibility**: The architecture is designed to accommodate future enhancements without breaking existing contracts.

### Technical Implementation
The codebase utilizes modern Python features (version 3.10+) to provide a clean, type-safe API. Interaction patterns are documented in the corresponding `AGENTS.md` and `SPEC.md` files, ensuring that both human developers and automated agents can effectively utilize these capabilities.

