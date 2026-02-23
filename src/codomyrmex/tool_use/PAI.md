# Personal AI Infrastructure — Tool Use Module

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Tool Use module provides a structured framework for tool validation, registration, and chaining. It enables PAI agents to register tools with schemas, validate inputs/outputs, and compose multi-step tool chains for complex workflows.

## PAI Capabilities

### Tool Registration

```python
from codomyrmex.tool_use import ToolRegistry, ToolEntry, tool

registry = ToolRegistry()

@tool(name="analyze", description="Analyze code")
def analyze_code(source: str) -> dict:
    return {"complexity": 5, "issues": []}

# Register manually
entry = ToolEntry(name="analyze", handler=analyze_code, schema={...})
registry.register(entry)
```

### Input/Output Validation

```python
from codomyrmex.tool_use import validate_input, validate_output, ValidationResult

# Validate tool inputs against schema
result: ValidationResult = validate_input(data={"source": "print('hi')"}, schema=tool_schema)

# Validate tool outputs
output_result = validate_output(data=response, schema=output_schema)
```

### Tool Chaining

```python
from codomyrmex.tool_use import ToolChain, ChainStep, ChainResult

chain = ToolChain()
chain.add_step(ChainStep(tool="read_file", args={"path": "main.py"}))
chain.add_step(ChainStep(tool="analyze", args={"source": "{prev.output}"}))
chain.add_step(ChainStep(tool="write_report", args={"findings": "{prev.output}"}))

result: ChainResult = chain.execute()
```

## Key Exports

| Export | Type | Purpose |
|--------|------|---------|
| `ToolRegistry` | Class | Tool registration and lookup |
| `ToolEntry` | Class | Tool metadata and handler binding |
| `tool` | Decorator | Register a function as a tool |
| `validate_input` | Function | Validate tool inputs against schema |
| `validate_output` | Function | Validate tool outputs against schema |
| `ValidationResult` | Class | Validation outcome data model |
| `ToolChain` | Class | Multi-step tool composition |
| `ChainStep` | Class | Individual step in a tool chain |
| `ChainResult` | Class | Chain execution result |

## PAI Algorithm Phase Mapping

| Phase | Tool Use Contribution |
|-------|------------------------|
| **THINK** | Registry provides available tool catalog for capability selection |
| **PLAN** | Tool chains define multi-step execution plans |
| **EXECUTE** | Validate inputs, execute tools, validate outputs |
| **VERIFY** | Validation framework ensures tool I/O conformance |

## Architecture Role

**Core Layer** — Foundational tool infrastructure consumed by `model_context_protocol/` (MCP tool registration), `agents/` (tool dispatch), and `orchestrator/` (workflow step execution).

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) — Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) — Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
