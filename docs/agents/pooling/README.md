# Agent Pooling

**Module**: `codomyrmex.agents.pooling` | **Category**: Infrastructure | **Last Updated**: March 2026

## Overview

Agent pooling with load balancing and circuit breakers. Distributes work across multiple agent backends with health monitoring, fallback chains, and configurable load balancing strategies.

## Key Classes

| Class | Purpose |
|:---|:---|
| `AgentPool` | Pool of agents with health-aware routing |
| `CircuitBreaker` | Circuit breaker for failing backends |
| `FallbackChain` | Ordered fallback sequence of agents |
| `PoolConfig` | Pool configuration (size, strategy, timeouts) |
| `PooledAgent` | Individual agent within the pool |
| `AgentHealth` | Health status for a pooled agent |
| `AgentStatus` | Status enum (healthy, degraded, failed) |
| `LoadBalanceStrategy` | Strategy enum (round-robin, least-loaded, random) |

## Usage

```python
from codomyrmex.agents.pooling import AgentPool

client = AgentPool()
```

## Source Module

Source: [`src/codomyrmex/agents/pooling/`](../../../../src/codomyrmex/agents/pooling/)

## Navigation

- **Parent**: [docs/agents/](../README.md)
- **Source**: [src/codomyrmex/agents/pooling/](../../../../src/codomyrmex/agents/pooling/)
- **Project Root**: [README.md](../../../README.md)
