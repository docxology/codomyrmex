# PEFT -- PAI Integration

## Phase Mapping

| PAI Phase | Tool | Usage |
|-----------|------|-------|
| OBSERVE | `peft_compare_methods` | Survey PEFT options for model |
| THINK | `peft_compare_methods` | Compare parameter efficiency |
| BUILD | `peft_create_adapter` | Create adapter with specific config |
| VERIFY | `peft_create_adapter` | Verify reduction factor meets requirements |

## MCP Tools

| Tool Name | Category | Description |
|-----------|----------|-------------|
| `peft_create_adapter` | peft | Create adapter and return parameter stats |
| `peft_compare_methods` | peft | Compare all PEFT methods for a dimension |

## Agent Providers

This module does not provide agent types. It provides PEFT analysis tools that agents consume.

## Dependencies

- Foundation: `model_context_protocol` (for `@mcp_tool` decorator)
- External: `numpy`
