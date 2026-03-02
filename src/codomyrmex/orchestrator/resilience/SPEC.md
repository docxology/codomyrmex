# Resilience — Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Fault-tolerance toolkit for the orchestrator providing error classification, retry policies, circuit breakers, self-healing diagnosis, and healing event journaling.

## Architecture

Layered resilience pattern:

1. **Classification** (`failure_taxonomy.py`) -- Errors are classified by keyword heuristics into `FailureCategory` with associated `RecoveryStrategy` lists.
2. **Retry** (`retry_engine.py`, `retry_policy.py`) -- Two retry implementations: `RetryEngine` with config adjusters and `PipelineRetryExecutor` with dead-letter routing and jitter.
3. **Circuit Breaking** (`agent_circuit_breaker.py`) -- Per-agent fault isolation using standard closed/open/half-open state machine.
4. **Self-Healing** (`self_healing.py`) -- `Diagnoser` produces structured `Diagnosis` with root cause, impact assessment, and ordered `RecoveryStep` plans.
5. **Auditing** (`healing_log.py`) -- Append-only `HealingLog` records diagnosis-recovery-outcome triples for pattern analysis.

## Key Classes

### `CircuitBreaker`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `register` | `agent_id: str` | `None` | Register an agent for health tracking |
| `allow` | `agent_id: str` | `bool` | Check if agent may receive work (checks cooldown for open circuits) |
| `record_success` | `agent_id: str` | `None` | Record success; resets consecutive failures and closes circuit |
| `record_failure` | `agent_id: str` | `None` | Record failure; opens circuit if threshold exceeded |
| `get_health` | `agent_id: str` | `AgentHealth \| None` | Retrieve health record |
| `reset` | `agent_id: str` | `None` | Force circuit back to closed state |

Constructor: `failure_threshold: int = 3`, `cooldown_seconds: float = 30.0`

### `Diagnoser`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `diagnose` | `error: Exception \| str, context: dict \| None` | `Diagnosis` | Classify error, identify root cause, assess impact, build recovery plan |

### `RetryEngine`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `execute` | `operation: Callable, *args, adjusters, config, **kwargs` | `RetryResult` | Retry with exponential backoff; adjusters modify config per failure category |

Constructor: `max_retries=3`, `base_delay=0.01`, `max_delay=1.0`, `backoff_factor=2.0`

### `PipelineRetryExecutor`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `execute` | `step_name: str, func: Callable, *args, **kwargs` | `RetryResult` | Sync retry with per-step policy |
| `execute_async` | `step_name: str, func: Callable, *args, **kwargs` | `RetryResult` | Async retry with `asyncio.sleep` delays |
| `set_policy` | `step_name: str, policy: RetryPolicy` | `None` | Assign custom policy per pipeline step |

### `HealingLog`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `record` | `event: HealingEvent` | `None` | Append a healing event |
| `success_rate` | none | `float` | Fraction of successful recoveries |
| `summary` | none | `dict` | Aggregate statistics by category and outcome |
| `to_jsonl` | none | `str` | Export all events as JSONL |

## Dependencies

- **Internal**: `codomyrmex.logging_monitoring`
- **External**: Standard library only (`time`, `random`, `asyncio`, `dataclasses`, `enum`)

## Constraints

- `classify_error` is heuristic-based; returns `confidence=0.5` for unknown categories.
- `RetryPolicy.compute_delay` applies jitter (0.5x-1.5x) by default to prevent thundering herd.
- `with_retry` decorator works with both sync and async functions automatically.
- Zero-mock: real execution only, `NotImplementedError` for unimplemented paths.

## Error Handling

- `CircuitBreaker` logs `WARNING` when circuit opens and `INFO` when recovering.
- `RetryEngine` logs each failed attempt with category classification.
- `PipelineRetryExecutor` invokes `on_retry` and `on_exhausted` callbacks if configured.
- All errors logged before propagation.
