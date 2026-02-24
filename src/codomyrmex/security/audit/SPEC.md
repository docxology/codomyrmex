# Technical Specification - Audit

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

**Module**: `codomyrmex.security.audit`  
**Last Updated**: 2026-01-29

## 1. Purpose

Security audit logging and forensic analysis

## 2. Architecture

### 2.1 Components

```
audit/
├── __init__.py          # Module exports
├── README.md            # Documentation
├── AGENTS.md            # Agent guidelines
├── SPEC.md              # This file
├── PAI.md               # Personal AI context
└── core.py              # Core implementation
```

### 2.2 Dependencies

- Python 3.10+
- Parent module: `security`

## 3. Interfaces

### 3.1 Public API

```python
# Primary exports from codomyrmex.security.audit
from codomyrmex.security.audit import (
    AuditEventType,      # Enum — event types (AUTH_LOGIN, AUTH_LOGOUT, AUTH_FAILED,
                         #   DATA_ACCESS, DATA_CREATE, DATA_UPDATE, DATA_DELETE,
                         #   PERMISSION_CHANGE, CONFIG_CHANGE, SYSTEM_ERROR, ADMIN_ACTION)
    AuditSeverity,       # Enum — DEBUG, INFO, WARNING, ERROR, CRITICAL
    AuditEvent,          # Dataclass — single audit record (id, event_type, action, actor,
                         #   resource, resource_id, severity, ip_address, user_agent,
                         #   details, timestamp); has .signature and .to_dict()/.to_json()
    AuditStore,          # ABC — base storage interface (store, query)
    InMemoryAuditStore,  # In-memory store (thread-safe, LRU eviction, max_events=10000)
    FileAuditStore,      # File-based store (JSONL append, thread-safe)
    AuditLogger,         # Main service — log(), query(), log_login(), log_data_access(),
                         #   log_admin_action()
)

# Key class signatures:

class AuditStore(ABC):
    def store(self, event: AuditEvent) -> None: ...
    def query(self, start: datetime | None, end: datetime | None,
              event_type: AuditEventType | None, actor: str | None) -> list[AuditEvent]: ...

class AuditLogger:
    def __init__(self, store: AuditStore | None = None): ...
    def log(self, event_type: AuditEventType, action: str, actor: str = "system",
            resource: str = "", resource_id: str = "",
            severity: AuditSeverity = AuditSeverity.INFO,
            ip_address: str = "", user_agent: str = "",
            details: dict[str, Any] | None = None) -> AuditEvent: ...
    def log_login(self, actor: str, ip_address: str = "", success: bool = True) -> AuditEvent: ...
    def log_data_access(self, actor: str, resource: str, resource_id: str = "") -> AuditEvent: ...
    def log_admin_action(self, actor: str, action: str,
                         details: dict[str, Any] | None = None) -> AuditEvent: ...
    def query(self, start: datetime | None = None, end: datetime | None = None,
              event_type: AuditEventType | None = None,
              actor: str | None = None) -> list[AuditEvent]: ...
```

### 3.2 Configuration

Environment variables:
- `CODOMYRMEX_*`: Configuration options

## 4. Implementation Notes

### 4.1 Design Decisions

1. **Thread-safe stores**: Both `InMemoryAuditStore` and `FileAuditStore` use `threading.Lock` to guarantee safe concurrent writes from multiple threads.
2. **LRU eviction in InMemoryAuditStore**: When events exceed `max_events` (default 10000), the oldest entries are discarded to bound memory usage.
3. **SHA-256 event signatures**: Each `AuditEvent` computes a truncated SHA-256 hash over its id, type, action, and timestamp for integrity verification.
4. **JSONL file format**: `FileAuditStore` appends one JSON line per event, enabling append-only writes and line-by-line streaming reads.

### 4.2 Limitations

- `FileAuditStore.query()` performs a full linear scan of the log file on every call; no indexing is available.
- The XOR-based integrity signature is informational only and does not protect against tampering (no HMAC or shared secret).

## 5. Testing

```bash
# Run tests for this module
uv run pytest src/codomyrmex/tests/unit/security/audit/
```

## 6. Future Considerations

- Add database-backed `AuditStore` implementation (e.g., SQLite or PostgreSQL) with indexed queries.
- Support HMAC-based event signatures using a configurable secret key for tamper detection.
- Add event retention policies and automatic log rotation for `FileAuditStore`.
