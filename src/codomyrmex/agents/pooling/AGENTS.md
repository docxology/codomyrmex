# Codomyrmex Agents -- agents/pooling

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Multi-agent load balancing, failover, and intelligent routing with per-agent circuit breakers and health tracking.

## Key Components

| Component | Role |
|-----------|------|
| `LoadBalanceStrategy` | Enum: `ROUND_ROBIN`, `RANDOM`, `LEAST_LATENCY`, `LEAST_ERRORS`, `WEIGHTED`, `PRIORITY` |
| `AgentStatus` | Enum: `HEALTHY`, `DEGRADED`, `UNHEALTHY`, `CIRCUIT_OPEN` |
| `AgentHealth` | Dataclass: `avg_latency_ms`, `error_rate`, `consecutive_failures`, `total_requests`, `is_available` |
| `PooledAgent[T]` | Generic dataclass wrapping an agent with `weight`, `priority`, `health`, and `metadata` |
| `PoolConfig` | Dataclass: circuit breaker thresholds (`failure_threshold`, `reset_timeout_s`), retry settings (`max_retries`), health thresholds (`degraded_error_rate`, `unhealthy_error_rate`) |
| `CircuitBreaker` | Thread-safe state machine (closed/open/half-open) with `record_success()`, `record_failure()`, `reset()` |
| `AgentPool[T]` | Generic load-balanced pool: `add_agent()`, `remove_agent()`, `execute(func)` with retries and failover, `get_stats()` |
| `FallbackChain[T]` | Ordered chain trying agents sequentially until success; fluent `add()` API |

## Operating Contracts

- `AgentPool.execute(func, retries)` selects an agent using the configured strategy, calls `func(agent)`, records success/failure on the agent's circuit breaker, and retries with a different agent on failure.
- `CircuitBreaker` transitions: closed -> open (after `failure_threshold` consecutive failures), open -> half-open (after `reset_timeout_s` elapsed), half-open -> closed (on success) or open (on failure).
- `AgentPool._update_health_status()` derives `AgentStatus` from error-rate thresholds in `PoolConfig`; agents degrade and recover automatically.
- `FallbackChain.execute(func, on_fallback)` tries each agent in order; calls `on_fallback(name, exception)` when falling back to next agent.
- `AgentPool.get_stats()` returns per-agent health metrics dict keyed by agent ID.

## Integration Points

- Used by `agents` parent module for pooled agent execution.
- `AgentPool` is generic over any agent type `T`; consumers define the callable passed to `execute()`.

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
- Parent: [agents](../README.md)
