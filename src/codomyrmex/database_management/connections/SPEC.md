# Technical Specification - Connections

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

**Module**: `codomyrmex.database_management.connections`  
**Last Updated**: 2026-01-29

## 1. Purpose

Connection pooling, lifecycle management, and health checks

## 2. Architecture

### 2.1 Components

```
connections/
├── __init__.py          # Module exports
├── README.md            # Documentation
├── AGENTS.md            # Agent guidelines
├── SPEC.md              # This file
├── PAI.md               # Personal AI context
└── core.py              # Core implementation
```

### 2.2 Dependencies

- Python 3.10+
- Parent module: `database_management`

## 3. Interfaces

### 3.1 Public API

```python
# Primary exports from codomyrmex.database_management.connections
from codomyrmex.database_management.connections import (
    ConnectionState,            # Enum: IDLE, IN_USE, CLOSED, ERROR
    ConnectionStats,            # Dataclass: pool utilization statistics
    PoolConfig,                 # Dataclass: pool tuning parameters
    Connection,                 # ABC: base connection with execute/is_valid/close
    ConnectionFactory,          # ABC: factory for creating connections
    InMemoryConnection,         # Lightweight in-memory connection implementation
    InMemoryConnectionFactory,  # Factory for InMemoryConnection instances
    ConnectionPool,             # Thread-safe connection pool with acquire/release
    HealthChecker,              # Background health checker for pool connections
)

# Key class signatures:
class Connection(ABC, Generic[T]):
    def execute(self, query: str, params: tuple | None = None) -> Any: ...  # abstract
    def is_valid(self) -> bool: ...                                          # abstract
    def close(self) -> None: ...                                             # abstract
    def mark_used(self) -> None: ...
    def mark_idle(self) -> None: ...

class ConnectionPool(Generic[T]):
    def __init__(self, factory: ConnectionFactory[T],
                 config: PoolConfig | None = None) -> None: ...
    def acquire(self, timeout: float | None = None) -> Connection[T]: ...
    def release(self, conn: Connection[T]) -> None: ...
    def connection(self) -> Iterator[Connection[T]]: ...   # context manager
    def close(self) -> None: ...
    @property
    def stats(self) -> ConnectionStats: ...

class HealthChecker:
    def __init__(self, pool: ConnectionPool, check_interval: float = 60.0,
                 health_query: str = "SELECT 1") -> None: ...
    def check_health(self) -> bool: ...
    def start(self) -> None: ...
    def stop(self) -> None: ...
```

### 3.2 Configuration

Environment variables:
- `CODOMYRMEX_*`: Configuration options

## 4. Implementation Notes

### 4.1 Design Decisions

1. **Thread-safe pool with `queue.Queue`**: The pool uses a standard-library `Queue` for connection checkout, providing blocking acquire with timeout without external dependencies.
2. **Connection lifecycle management**: Connections are validated on checkout against both `max_lifetime_s` and the abstract `is_valid()` method, ensuring stale or broken connections are evicted automatically.
3. **Automatic pool replenishment**: When a connection is invalidated on release, the pool checks whether it has fallen below `min_connections` and creates replacements to maintain the floor.
4. **Generic type parameter**: `Connection[T]` and `ConnectionPool[T]` are generic over the result type, allowing type-safe specialization for different backends.

### 4.2 Limitations

- `HealthChecker.start()` uses a daemon thread with `time.sleep`; no async health checking
- Pool `stats.waiting_requests` is always 0 (approximate); accurate waiter counting is not implemented
- No connection warm-up or pre-ping on idle connections between validation intervals

## 5. Testing

```bash
# Run tests for this module
uv run pytest src/codomyrmex/tests/unit/database_management/connections/
```

## 6. Future Considerations

- Add async pool implementation using `asyncio.Queue`
- Implement accurate waiter counting for backpressure metrics
- Support connection pre-ping on checkout to catch stale-but-valid connections
