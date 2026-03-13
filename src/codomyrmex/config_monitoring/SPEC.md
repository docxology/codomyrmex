# Config Monitoring — Functional Specification

**Version**: v1.2.2 | **Status**: Active | **Last Updated**: March 2026

## Purpose

The `config_monitoring` module provides runtime configuration change detection, drift analysis, compliance auditing, and hot-reload watching. It enables AI agents and operators to track configuration file mutations across environments, detect security anti-patterns (plaintext secrets, overly permissive permissions), and maintain point-in-time snapshots for infrastructure drift detection.

## Architecture

```
config_monitoring/
├── config_monitor.py   # Core monitoring engine (ConfigurationMonitor)
├── watcher.py          # Thread-safe hot-reload poller (ConfigWatcher)
└── mcp_tools.py        # MCP tool surface (3 tools)
```

### Data Model

#### `ConfigChange` (dataclass)

Record of a single configuration file mutation.

| Field | Type | Description |
| :--- | :--- | :--- |
| `change_id` | `str` | Unique ID (`chg_{timestamp_ms}`) |
| `config_path` | `str` | Absolute path to changed file |
| `change_type` | `str` | One of `created`, `modified`, `deleted` |
| `timestamp` | `datetime` | When the change was detected |
| `previous_hash` | `str \| None` | SHA-256 before change |
| `current_hash` | `str \| None` | SHA-256 after change |
| `changes` | `dict` | Additional change metadata |
| `source` | `str` | Origin of change (default `"unknown"`) |

#### `ConfigAudit` (dataclass)

Result of a compliance audit run.

| Field | Type | Description |
| :--- | :--- | :--- |
| `audit_id` | `str` | Unique ID (`audit_{env}_{timestamp}`) |
| `timestamp` | `datetime` | When the audit ran |
| `environment` | `str` | Target environment name |
| `compliance_status` | `str` | `"compliant"` or `"non_compliant"` |
| `issues_found` | `list[str]` | Human-readable issue descriptions |
| `recommendations` | `list[str]` | Remediation suggestions |
| `audit_scope` | `dict` | `files_audited` count and `config_dir` path |

#### `ConfigSnapshot` (dataclass)

Point-in-time capture of all file hashes in a directory for drift detection.

| Field | Type | Description |
| :--- | :--- | :--- |
| `snapshot_id` | `str` | Unique ID (`snap_{env}_{timestamp}`) |
| `timestamp` | `datetime` | When the snapshot was taken |
| `environment` | `str` | Environment name |
| `config_hashes` | `dict[str, str]` | Absolute path → SHA-256 mapping |
| `total_files` | `int` | Number of files captured |

### Core Engine: `ConfigurationMonitor`

Central service class orchestrating all monitoring operations.

**Initialization**: Accepts an optional `workspace_dir`. Creates three directories:

- `{workspace}/config_monitoring/` — monitoring state
- `{workspace}/config_monitoring/snapshots/` — JSON snapshot files
- `{workspace}/config_audits/` — JSON audit reports

**Key Methods**:

| Method | Signature | Description |
| :--- | :--- | :--- |
| `calculate_file_hash` | `(path) → str` | SHA-256 hash (8KB chunked reads) |
| `record_change` | `(path, type, prev, curr, source) → ConfigChange` | Create and store a change record (ring buffer: 1000 max) |
| `detect_config_changes` | `(paths) → list[ConfigChange]` | Compare current hashes to persisted baselines, emit deltas |
| `create_snapshot` | `(env, dir) → ConfigSnapshot` | Hash all files recursively, persist as JSON |
| `detect_drift` | `(snapshot_id, dir) → dict` | Compare current directory state against a snapshot |
| `audit_configuration` | `(env, dir, rules?) → ConfigAudit` | Scan for security issues (secrets, permissions) |
| `get_changes` | `(path?) → list[ConfigChange]` | Retrieve change history, optionally filtered |
| `get_recent_changes` | `(hours=24) → list[ConfigChange]` | Get changes from the last N hours |
| `get_audit_history` | `(env?) → list[ConfigAudit]` | Sorted audit history |
| `get_monitoring_summary` | `() → dict` | Aggregate counts and status |

### Hot-Reload Watcher: `ConfigWatcher`

Thread-safe filesystem poller that invokes a callback when a watched file changes.

| Method / Property | Description |
| :--- | :--- |
| `start()` | Launch daemon polling thread |
| `stop()` | Signal thread to stop, join with timeout |
| `is_alive` | Property: whether the watcher thread is running |

**Design**: Uses `threading.Event.wait(interval)` for responsive stop, not `time.sleep`. Detects file disappearance and logs a warning.

### Security Audit Patterns

The `audit_configuration` method scans files for 5 regex patterns:

1. Plaintext `password = "..."` assignments
2. Plaintext `api_key = "..."` assignments
3. Plaintext `secret = "..."` assignments
4. Plaintext `token = "..."` assignments
5. Unencrypted PEM private keys (`-----BEGIN ... PRIVATE KEY-----`)

Also checks Unix file permissions and flags files with group/other read access.

## Persistence

| File | Format | Contents |
| :--- | :--- | :--- |
| `config_monitoring/config_hashes.json` | JSON | `{absolute_path: sha256_hash}` |
| `config_monitoring/snapshots/*.json` | JSON | Full `ConfigSnapshot` serialization |
| `config_audits/*.json` | JSON | Full `ConfigAudit` serialization |

## Constraints

- **Zero-Mock**: Tests must use real filesystem operations
- **Polling**: Watcher uses mtime polling for maximum cross-platform portability (no OS-specific events)
- **Regex Audit**: Compliance checks use regex pattern matching; not a full secret scanner
- **Ring Buffer**: In-memory change history caps at 1000 entries

## Related Modules

| Module | Relationship |
| :--- | :--- |
| `config_management` | Parent: general configuration loading and management |
| `logging_monitoring` | Foundation: structured logging via `get_logger` |
| `security` | Sibling: deeper security scanning capabilities |
| `exceptions` | Foundation: `CodomyrmexError` base exception |

## Navigation

- **Self**: [SPEC.md](SPEC.md) — This document
- **Parent**: [README.md](README.md) — Module overview
- **Siblings**: [AGENTS.md](AGENTS.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md) | [PAI.md](PAI.md)
- **Parent Module**: [config_management/](../config_management/SPEC.md)
