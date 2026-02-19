# pooling

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Overview

Multi-agent load balancing, failover, and intelligent routing. Provides a generic `AgentPool` that distributes work across multiple agents using configurable strategies (round-robin, random, least-latency, least-errors, weighted, priority), integrated circuit breakers for fault tolerance, per-agent health tracking, and automatic retry with exponential backoff. Also includes a `FallbackChain` for simple ordered-failover patterns.

## Key Exports

- **`LoadBalanceStrategy`** -- Enum of load balancing strategies (round_robin, random, least_latency, least_errors, weighted, priority)
- **`AgentStatus`** -- Enum of agent health states (healthy, degraded, unhealthy, circuit_open)
- **`AgentHealth`** -- Dataclass tracking per-agent health metrics including success/failure counts, average latency, error rate, and availability
- **`PooledAgent`** -- Generic dataclass wrapping an agent instance with its ID, weight, priority, and health metrics
- **`PoolConfig`** -- Configuration dataclass for pool behavior: circuit breaker thresholds, health check intervals, retry settings, and request timeout
- **`CircuitBreaker`** -- Thread-safe circuit breaker with closed/open/half-open states, failure threshold, and configurable reset timeout
- **`AgentPool`** -- Generic agent pool with strategy-based selection, automatic failover across agents, circuit breaker integration, health status updates, and pool-wide stats reporting
- **`FallbackChain`** -- Generic ordered chain of agents that tries each in sequence until one succeeds, with optional fallback callback

## Directory Contents

- `__init__.py` - All pooling logic: load balancing strategies, circuit breaker, agent pool, fallback chain, health tracking
- `README.md` - This file
- `AGENTS.md` - Agent integration notes
- `PAI.md` - PAI-specific documentation
- `SPEC.md` - Module specification
- `py.typed` - PEP 561 type-checking marker

## Navigation

- **Parent Module**: [agents](../README.md)
- **Project Root**: [../../../../README.md](../../../../README.md)
