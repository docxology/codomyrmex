# Personal AI Infrastructure -- AI Gateway Module

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

The AI Gateway module provides load balancing, failover, and circuit breaking for routing
LLM requests across multiple providers. It prevents cascade failures and enables automatic
recovery when providers come back online.

## MCP Tools

| Tool | Description | Trust Level | Category |
|------|-------------|-------------|----------|
| `codomyrmex.gateway_complete` | Route completion request with load balancing | Safe | ai_gateway |
| `codomyrmex.gateway_health` | Check provider health and circuit states | Safe | ai_gateway |

## PAI Algorithm Phase Mapping

| Phase | Contribution | Key Functions |
|-------|-------------|---------------|
| **EXECUTE** (5/7) | Route LLM requests with failover | `AIGateway.complete()`, `gateway_complete` MCP |
| **OBSERVE** (1/7) | Monitor provider health | `AIGateway.health_check()`, `gateway_health` MCP |
| **VERIFY** (6/7) | Confirm provider availability | `gateway_health` MCP |

## Architecture Role

**Application Layer** -- Routes LLM requests from agent workflows through healthy providers.
Consumed by `agents/` for multi-provider LLM access.

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
- **MCP Tools**: [mcp_tools.py](mcp_tools.py)
