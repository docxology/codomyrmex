# AI Gateway -- Agent Coordination

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Overview

Provides load balancing, failover, and circuit breaker patterns for LLM provider management. Routes completion requests across multiple AI providers with configurable strategies.

## MCP Tools

| Tool | Description | Trust Level | Category |
|------|-------------|-------------|----------|
| `gateway_complete` | Route a completion request through the AI Gateway with load balancing and failover | Standard | ai_gateway |
| `gateway_health` | Check the health status of all configured AI Gateway providers | Standard | ai_gateway |


## PAI Integration

| Algorithm Phase | Agent Role | Primary Operations |
|----------------|-----------|-------------------|
| EXECUTE | Infrastructure Agent | Route LLM completions through load-balanced gateway |
| OBSERVE | Monitoring Agent | Check provider health and circuit breaker states |


## Agent Instructions

1. Provide a list of provider configurations (name, endpoint, weight) before calling gateway_complete
2. Use gateway_health to verify provider availability before routing requests


## Navigation

- [Source README](../../src/codomyrmex/ai_gateway/README.md) | [SPEC.md](SPEC.md)
