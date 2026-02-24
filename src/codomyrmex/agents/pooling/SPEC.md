# Technical Specification - Pooling

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

**Module**: `codomyrmex.agents.pooling`  
**Last Updated**: 2026-01-29

## 1. Purpose

Multi-agent load balancing, failover, and intelligent routing

## 2. Architecture

### 2.1 Components

```
pooling/
├── __init__.py          # Module exports
├── README.md            # Documentation
├── AGENTS.md            # Agent guidelines
├── SPEC.md              # This file
├── PAI.md               # Personal AI context
└── core.py              # Core implementation
```

### 2.2 Dependencies

- Python 3.10+
- Parent module: `agents`

## 3. Interfaces

### 3.1 Public API

```python
# Primary exports from codomyrmex.agents.pooling
from codomyrmex.agents.pooling import (
    LoadBalanceStrategy,   # Enum: ROUND_ROBIN, RANDOM, LEAST_LATENCY, LEAST_ERRORS, WEIGHTED, PRIORITY
    AgentStatus,           # Enum: HEALTHY, DEGRADED, UNHEALTHY, CIRCUIT_OPEN
    AgentHealth,           # Dataclass: health metrics (latency, error rate, consecutive failures)
    PooledAgent,           # Dataclass (Generic[T]): wraps an agent with weight, priority, and health
    PoolConfig,            # Dataclass: circuit breaker thresholds, retry settings, timeouts
    CircuitBreaker,        # Thread-safe circuit breaker (closed/open/half-open states)
    AgentPool,             # Generic[T]: load-balanced pool with failover and per-agent circuit breakers
    FallbackChain,         # Generic[T]: ordered chain that tries agents sequentially until success
)

# Key class signatures:
class AgentPool(Generic[T]):
    def __init__(self, strategy: LoadBalanceStrategy = LoadBalanceStrategy.ROUND_ROBIN, config: PoolConfig | None = None): ...
    def add_agent(self, agent_id: str, agent: T, weight: float = 1.0, priority: int = 0, metadata: dict[str, Any] | None = None) -> None: ...
    def remove_agent(self, agent_id: str) -> bool: ...
    def execute(self, func: Callable[[T], Any], retries: int | None = None) -> Any: ...
    def get_available_agents(self) -> list[PooledAgent[T]]: ...
    def get_stats(self) -> dict[str, dict[str, Any]]: ...
    def reset_agent(self, agent_id: str) -> bool: ...

class FallbackChain(Generic[T]):
    def add(self, name: str, agent: T) -> "FallbackChain[T]": ...
    def execute(self, func: Callable[[T], Any], on_fallback: Callable[[str, Exception], None] | None = None) -> Any: ...

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, reset_timeout_s: float = 30.0): ...
    def is_open(self) -> bool: ...  # property
    def record_success(self) -> None: ...
    def record_failure(self) -> None: ...
    def reset(self) -> None: ...
```

### 3.2 Configuration

Environment variables:
- `CODOMYRMEX_*`: Configuration options

## 4. Implementation Notes

### 4.1 Design Decisions

1. **Thread-safe circuit breaker**: `CircuitBreaker` uses `threading.Lock` for safe concurrent access; the closed/open/half-open state machine prevents cascading failures across pooled agents.
2. **Six load-balancing strategies**: Round-robin, random, least-latency, least-errors, weighted, and priority -- selectable via `LoadBalanceStrategy` enum without subclassing `AgentPool`.
3. **Automatic health status promotion**: `_update_health_status` derives `AgentStatus` from error-rate thresholds in `PoolConfig`, so agents degrade and recover without manual intervention.

### 4.2 Limitations

- Health checks are passive (triggered by request outcomes); no active probing or heartbeat mechanism
- `FallbackChain` does not track health metrics; it is a simple ordered-attempt pattern with no circuit breaking

## 5. Testing

```bash
# Run tests for this module
uv run pytest src/codomyrmex/tests/unit/agents/pooling/
```

## 6. Future Considerations

- Active health probes (periodic ping/heartbeat for proactive status updates)
- Async-native `AgentPool` variant for use with `asyncio` event loops
