# Semantic Router -- PAI Integration

## Phase Mapping

| PAI Phase | Tool | Usage |
|-----------|------|-------|
| OBSERVE | `semantic_router_route` | Classify incoming request intent |
| THINK | `semantic_router_route` | Test routing with different phrasings |
| PLAN | `semantic_router_route` | Determine which agent/capability to invoke |
| EXECUTE | `semantic_router_route` | Real-time intent routing during conversation |

## MCP Tools

| Tool Name | Category | Description |
|-----------|----------|-------------|
| `semantic_router_route` | semantic_router | Route input text to best matching semantic route |

## Agent Providers

This module does not provide agent types. It provides a routing tool that agents consume for intent classification.

## Dependencies

- Foundation: `model_context_protocol` (for `@mcp_tool` decorator)
- External: `numpy`
