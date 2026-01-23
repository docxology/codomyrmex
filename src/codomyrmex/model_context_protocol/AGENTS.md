# Codomyrmex Agents — src/codomyrmex/model_context_protocol

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

Foundation Layer module defining Model Context Protocol (MCP) standards for AI tool communication. Provides schemas and utilities for creating MCP-compatible tool specifications across all Codomyrmex modules.

## Active Components

### MCP Schemas

- `mcp_schemas.py` - MCP schema definitions
  - Key Classes: `ToolSpecification`, `ParameterSchema`, `ResponseSchema`
  - Key Functions: `create_tool_spec()`, `validate_tool_spec()`, `generate_mcp_manifest()`

## Key Classes and Functions

| Class/Function | Purpose |
| :--- | :--- |
| `ToolSpecification` | Define an MCP tool with parameters and responses |
| `ParameterSchema` | Schema for tool parameters |
| `ResponseSchema` | Schema for tool responses |
| `create_tool_spec()` | Create a new tool specification |
| `validate_tool_spec()` | Validate tool specification format |
| `generate_mcp_manifest()` | Generate manifest for all module tools |

## Operating Contracts

1. **Foundation Status**: No dependencies on other Codomyrmex modules
2. **Standard Compliance**: All tools follow MCP specification
3. **Schema Validation**: Tool specs validated against JSON schema
4. **Documentation**: Each tool includes description and examples
5. **Versioning**: Tool specs include version information

## MCP Tool Pattern

```python
from codomyrmex.model_context_protocol import (
    ToolSpecification,
    ParameterSchema,
    create_tool_spec
)

# Define a tool
spec = create_tool_spec(
    name="analyze_code",
    description="Analyze code for quality issues",
    parameters=[
        ParameterSchema(
            name="code",
            type="string",
            description="Code to analyze",
            required=True
        ),
        ParameterSchema(
            name="language",
            type="string",
            description="Programming language",
            required=False,
            default="python"
        )
    ]
)
```

## Signposting

### Document Hierarchy

- **Self**: [AGENTS.md](AGENTS.md)
- **Parent**: [src/codomyrmex/AGENTS.md](../AGENTS.md)
- **Project Root**: [../../../AGENTS.md](../../../AGENTS.md)

### Sibling Modules (Foundation Layer)

| Module | AGENTS.md | Purpose |
| :--- | :--- | :--- |
| logging_monitoring | [../logging_monitoring/AGENTS.md](../logging_monitoring/AGENTS.md) | Logging infrastructure |
| environment_setup | [../environment_setup/AGENTS.md](../environment_setup/AGENTS.md) | Environment validation |
| terminal_interface | [../terminal_interface/AGENTS.md](../terminal_interface/AGENTS.md) | Terminal UI |

### Related Documentation

- [README.md](README.md) - User documentation
- [API_SPECIFICATION.md](API_SPECIFICATION.md) - API documentation
- [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md) - MCP tool definitions
- [SPEC.md](SPEC.md) - Functional specification
