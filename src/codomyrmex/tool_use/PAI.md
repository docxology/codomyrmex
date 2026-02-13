# Personal AI Infrastructure -- Tool Use Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Tool Use Module provides meta-infrastructure for registering, validating, composing, and invoking tools. This is a **Core Layer** module that underpins how PAI agents discover and execute tools.

## PAI Capabilities

```python
from codomyrmex.tool_use import (
    ValidationResult, validate_input, validate_output,
    ToolEntry, ToolRegistry, tool,
    ChainStep, ChainResult, ToolChain,
)
```

## Key Exports

| Export | Type | Purpose |
|--------|------|---------|
| `ValidationResult` | Dataclass | Validation result with valid flag and error list |
| `validate_input` | Function | Validate tool input against JSON-schema-like spec |
| `validate_output` | Function | Validate tool output against JSON-schema-like spec |
| `ToolEntry` | Dataclass | Tool definition with handler, schemas, and tags |
| `ToolRegistry` | Class | Central registry for tool management and invocation |
| `tool` | Decorator | Mark functions as tools with schema metadata |
| `ChainStep` | Dataclass | Single step in a sequential tool pipeline |
| `ChainResult` | Dataclass | Result of chain execution with context and errors |
| `ToolChain` | Class | Sequential tool pipeline with context propagation |

## PAI Algorithm Phase Mapping

| Phase | Tool Use Contribution |
|-------|----------------------|
| **BUILD** | Tool registration via ToolRegistry and @tool decorator; defining tool schemas and handlers |
| **EXECUTE** | Tool invocation via registry.invoke(); chain execution via ToolChain.execute() |
| **VERIFY** | Input/output validation via validate_input/validate_output; chain pre-flight validation |
| **OBSERVE** | Tool search and discovery via registry.search(); listing registered tools |

## Architecture Role

**Core Layer** -- Tool Use is meta-infrastructure that other modules use to expose their functionality as discoverable, validated, composable tools. It bridges the gap between raw callable functions and structured, schema-validated tool interfaces that PAI agents can safely invoke.

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) -- Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) -- Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md) | [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md)
