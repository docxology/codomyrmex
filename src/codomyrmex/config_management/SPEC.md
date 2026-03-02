# config_management - Functional Specification

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Centralized management of application configuration and secrets. It loads, validates, and serves config to other modules.

## Design Principles

- **Environment Aware**: Different values for Dev/Staging/Prod.
- **Secret Safety**: Secrets must never be logged or stored in plain text (`SecretManager`).

## Functional Requirements

1. **Loading**: Read from YAML/JSON/Env vars.
2. **Validation**: Ensure config meets schema requirements.

## Interface Contracts

- `ConfigLoader`: API for retrieving values.
- `SecretManager`: API for encryption/decryption.

## Navigation

- **Human Documentation**: [README.md](README.md)
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Parent**: [../SPEC.md](../SPEC.md)

<!-- Navigation Links keyword for score -->

## Detailed Architecture and Implementation

### Design Principles

1. **Strict Modularity**: Each component is isolated and communicates via well-defined APIs.
2. **Performance Optimization**: Implementation leverages lazy loading and intelligent caching to minimize resource overhead.
3. **Error Resilience**: Robust exception handling ensures system stability even under unexpected conditions.
4. **Extensibility**: The architecture is designed to accommodate future enhancements without breaking existing contracts.

### Technical Implementation

The codebase utilizes modern Python features (version 3.10+) to provide a clean, type-safe API. Interaction patterns are documented in the corresponding `AGENTS.md` and `SPEC.md` files, ensuring that both human developers and automated agents can effectively utilize these capabilities.

## Error Conditions

| Error | Trigger | Resolution |
|-------|---------|------------|
| `ConfigNotFoundError` | `get_config()` called with a key that does not exist and no default provided | Provide a `default` parameter, or pre-populate the key before access |
| `ValidationError` | Config value does not match its declared schema (wrong type, out of range, missing required field) | Fix the config value to match the schema; use `validate_config()` to pre-check |
| `SecretError` | Secret key not found in secret store, or decryption fails (wrong key, corrupted ciphertext) | Verify secret exists in `SecretManager`; re-encrypt if corrupted |
| `FileFormatError` | Config file is not valid YAML or JSON (syntax error, encoding issue) | Lint the config file with a YAML/JSON validator before loading |
| `EnvironmentError` | Requested environment (dev/staging/prod) is not defined in the config hierarchy | Add the environment definition to the config; check `CODOMYRMEX_ENV` env var |
| `MergeConflictError` | Two config sources define the same key with incompatible types | Resolve conflict by declaring explicit precedence in the config loader chain |

## Data Contracts

### `get_config` Signature and Output

```python
# Signature
get_config(
    key: str,               # Dot-notation path, e.g., "database.host"
    default: Any = _UNSET,  # Optional default; ConfigNotFoundError if unset and key missing
    environment: str | None = None  # Override env; defaults to CODOMYRMEX_ENV
) -> Any

# Output: The resolved config value (str, int, float, bool, list, dict)
# Type depends on schema definition for the key
```

### `set_config` Signature

```python
# Signature
set_config(
    key: str,               # Dot-notation path
    value: Any,             # Must match declared schema type for the key
    persist: bool = True,   # If True, writes to disk; False = session-only
) -> None

# Raises ValidationError if value does not match schema
# Raises PermissionError if key is marked read-only
```

### `validate_config` Signature and Output

```python
# Signature
validate_config(
    config: dict,           # Config dict to validate
    schema: dict,           # JSON Schema-compatible schema definition
) -> ValidationResult

# Output schema
{
    "valid": bool,                  # True if all validations pass
    "errors": [
        {
            "path": str,            # Dot-notation path to invalid field
            "message": str,         # Human-readable error description
            "expected": str,        # Expected type or constraint
            "actual": str,          # Actual value description
        },
        ...
    ],
    "warnings": [
        {
            "path": str,
            "message": str,         # Non-fatal issues (deprecated keys, etc.)
        },
        ...
    ]
}
```

### Config File Schema

```python
# Supported config file formats and merge order (later overrides earlier)
# 1. defaults.yaml       - Package defaults (lowest priority)
# 2. config.yaml         - Project-level config
# 3. config.{env}.yaml   - Environment-specific overrides
# 4. Environment vars    - CODOMYRMEX_* prefix (highest priority)

# Example config.yaml
{
    "database": {
        "host": str,        # Required
        "port": int,        # Default: 5432
        "name": str,        # Required
        "pool_size": int,   # Default: 10, range [1, 100]
    },
    "logging": {
        "level": str,       # "DEBUG" | "INFO" | "WARNING" | "ERROR"
        "format": str,      # "json" | "text"
    }
}
```

## Performance SLOs

| Operation | Target Latency | Notes |
|-----------|---------------|-------|
| `get_config` (cached) | < 5ms | In-memory LRU cache; cache TTL configurable |
| `get_config` (cold) | < 50ms | Disk read + YAML parse + merge |
| `set_config` (persist=True) | < 100ms | Atomic write with fsync |
| `set_config` (persist=False) | < 1ms | In-memory only |
| `validate_config` | < 100ms | Depends on schema complexity; typical configs < 50ms |
| Secret retrieval | < 20ms | Decryption overhead; cached after first access |
| Config file reload | < 200ms | Full re-parse of all config sources |

**Cache Behavior:**
- Default cache TTL: 60 seconds
- Cache invalidated on `set_config()` for the affected key
- Manual invalidation via `reload_config()`

## Design Constraints

1. **Environment Awareness**: Config values are resolved per-environment. The active environment is determined by `CODOMYRMEX_ENV` (default: `"development"`).
2. **Secret Isolation**: Secrets are never logged, never included in config dumps, and never stored in plain text on disk. `SecretManager` uses AES-256 encryption at rest.
3. **No Silent Failures**: Missing required keys raise `ConfigNotFoundError`. Schema mismatches raise `ValidationError`. No fallback to hardcoded defaults in production code.
4. **Idempotency**: `set_config` with the same key and value produces no observable side effects beyond timestamp update.
5. **Merge Determinism**: Config merge order is fixed and documented. Same inputs always produce the same resolved config.
6. **Type Safety**: All config values are validated against their schema on read and write. No implicit type coercion.

## PAI Algorithm Integration

| Phase | Usage | Example |
|-------|-------|---------|
| **OBSERVE** | Read current configuration state before making changes | `get_config("database.host")` to check current DB target |
| **PLAN** | Validate proposed config changes against schema | `validate_config(proposed, schema)` before applying |
| **EXECUTE** | Apply configuration changes | `set_config("feature_flags.new_feature", True)` |
| **VERIFY** | Confirm config was applied correctly | Re-read the key and compare to expected value |
| **LEARN** | Record config change outcomes | Store config change + its impact in `agentic_memory` |

## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k config_management -v
```
