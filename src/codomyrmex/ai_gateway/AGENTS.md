# Agent Guidelines - AI Gateway

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Module Overview

Load balancing, failover, and circuit breaker for routing requests across multiple LLM providers.

## Key Classes

- **AIGateway** -- Multi-provider gateway with strategy-based routing
- **Provider** -- Provider endpoint with health and weight config
- **CircuitBreaker** -- Prevents cascade failures (closed/open/half-open)
- **GatewayConfig** -- Strategy and threshold configuration

## MCP Tools Available

| Tool | Description | Trust Level |
|------|-------------|-------------|
| `gateway_complete` | Route a completion request with load balancing and failover | Safe |
| `gateway_health` | Check health and circuit state of all providers | Safe |

## Agent Instructions

1. **Configure providers** -- Supply provider list with endpoints and weights
2. **Use weighted strategy** -- For heterogeneous provider capacity
3. **Monitor health** -- Call `gateway_health` to check circuit states
4. **Handle failures** -- Gateway returns `success=False` when all providers are down

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | MCP Tools | Trust Level |
|-----------|-------------|-----------|-------------|
| **Engineer** | Full | `gateway_complete`, `gateway_health` | TRUSTED |
| **Architect** | Read + Design | `gateway_health` -- architecture review | OBSERVED |
| **QATester** | Validation | `gateway_complete`, `gateway_health` -- failover testing | OBSERVED |

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
