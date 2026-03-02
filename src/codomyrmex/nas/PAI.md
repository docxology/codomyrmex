# NAS -- PAI Integration

## Phase Mapping

| PAI Phase | Tool | Usage |
|-----------|------|-------|
| OBSERVE | `nas_sample_architecture` | Explore architecture space |
| THINK | `nas_random_search` | Search for optimal configurations |
| PLAN | `nas_random_search` | Plan model architecture before build |
| BUILD | `nas_sample_architecture` | Generate concrete architecture configs |

## MCP Tools

| Tool Name | Category | Description |
|-----------|----------|-------------|
| `nas_sample_architecture` | nas | Sample random architecture from search space |
| `nas_random_search` | nas | Run random NAS with size heuristic |

## Agent Providers

This module does not provide agent types. It provides architecture search tools that agents consume.

## Dependencies

- Foundation: `model_context_protocol` (for `@mcp_tool` decorator)
- External: `numpy`
