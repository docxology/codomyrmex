# Codomyrmex Agents — src/codomyrmex/orchestrator/resilience

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Provides fault-tolerance primitives for the orchestrator: error classification into a taxonomy of failure categories, automated retry with exponential backoff, per-agent circuit breaker for fault isolation, self-healing diagnosis with recovery plans, pipeline retry policies with dead-letter routing, and an append-only healing event log for learning from past recoveries.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `failure_taxonomy.py` | `FailureCategory` | Enum of failure categories: config, resource, dependency, logic, timeout, permission, unknown |
| `failure_taxonomy.py` | `RecoveryStrategy` | Enum of recovery actions: retry, adjust_config, fallback, escalate, skip, restart |
| `failure_taxonomy.py` | `classify_error` | Keyword-heuristic classifier mapping error messages to `ClassifiedError` with strategies |
| `failure_taxonomy.py` | `RECOVERY_MAP` | Static mapping from `FailureCategory` to ordered `RecoveryStrategy` lists |
| `agent_circuit_breaker.py` | `CircuitBreaker` | Per-agent circuit breaker (closed/open/half-open) with configurable threshold and cooldown |
| `agent_circuit_breaker.py` | `AgentHealth` | Health record dataclass tracking consecutive failures, lifetime counts, and state |
| `self_healing.py` | `Diagnoser` | Diagnoses errors and generates `Diagnosis` with root cause, impact, and `RecoveryStep` plan |
| `retry_engine.py` | `RetryEngine` | Config-aware retry with exponential backoff and per-category config adjusters |
| `retry_policy.py` | `RetryPolicy` / `PipelineRetryExecutor` | Pipeline-step retry with jitter, dead-letter routing, sync and async execution |
| `retry_policy.py` | `with_retry` | Decorator for retrying sync/async functions with exponential backoff |
| `healing_log.py` | `HealingLog` / `HealingEvent` | Append-only log of diagnosis-recovery-outcome triples with JSONL export |

## Operating Contracts

- `classify_error` uses keyword heuristics; confidence is 0.5 for unclassified errors.
- `CircuitBreaker` transitions: CLOSED -> OPEN (after threshold) -> HALF_OPEN (after cooldown) -> CLOSED (on success).
- `RetryEngine` sleeps between attempts; first retry delay is `base_delay * backoff_factor`.
- `PipelineRetryExecutor` routes exhausted retries to `RetryOutcome.DEAD_LETTER`.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: `codomyrmex.logging_monitoring` (structured logging)
- **Used by**: `orchestrator.process_orchestrator`, `orchestrator.workflows`, `orchestrator.execution`

## Navigation

- **Parent**: [orchestrator](../README.md)
- **Root**: [Root](../../../../README.md)
