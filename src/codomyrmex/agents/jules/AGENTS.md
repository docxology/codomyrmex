# Codomyrmex Agents — src/codomyrmex/agents/jules

## Signposting
- **Parent**: [agents](../AGENTS.md)
- **Self**: [Jules Agents](AGENTS.md)
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

Jules submodule providing integration with Jules CLI tool. This includes a client wrapper for executing jules commands and integration adapters for Codomyrmex modules.

## Function Signatures

### JulesClient

```python
def execute_jules_command(self, command: str, args: Optional[list[str]] = None) -> dict[str, Any]
```

Execute a jules command.

**Parameters:**
- `command` (str): Jules command name
- `args` (Optional[list[str]]): Command arguments

**Returns:** `dict` - Command result

```python
def get_jules_help(self) -> dict[str, Any]
```

Get jules help information.

**Returns:** `dict` - Help information

### JulesIntegrationAdapter

```python
def adapt_for_ai_code_editing(self, prompt: str, language: str = "python", **kwargs) -> str
```

Adapt Jules for AI code editing module.

**Parameters:**
- `prompt` (str): Code generation prompt
- `language` (str): Programming language
- `**kwargs`: Additional parameters

**Returns:** `str` - Generated code

## Navigation Links

- **Human Documentation**: [README.md](README.md)
- **Parent Module**: [agents](../AGENTS.md)



## Active Components
- `README.md` - Component file.
- `SPEC.md` - Component file.
- `__init__.py` - Component file.
- `jules_client.py` - Component file.
- `jules_integration.py` - Component file.

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
