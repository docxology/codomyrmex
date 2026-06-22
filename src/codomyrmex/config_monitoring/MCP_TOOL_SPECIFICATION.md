# Config Monitoring MCP Tool Specification

**Version**: v1.2.7 | **Status**: Active | **Last Updated**: June 2026

## Tools

### `config_monitoring_detect_changes`

- **Purpose**: Detect changed configuration files by comparing hashes to stored baselines.
- **Parameters**: `config_paths: list[str]`, `workspace_dir: str | None = None`
- **Returns**: `status`, `paths_checked`, `changes_detected`, and `changes`.

### `config_monitoring_summary`

- **Purpose**: Return aggregate monitoring state for the workspace.
- **Parameters**: `workspace_dir: str | None = None`
- **Returns**: `status` and `summary`.

### `config_monitoring_hash_file`

- **Purpose**: Calculate a SHA-256 hash for a configuration file.
- **Parameters**: `file_path: str`
- **Returns**: `status`, `file_path`, and `sha256`.

## Error Contract

All tools catch runtime failures and return `{"status": "error", "message": str(exc)}`.

## Navigation

- **Python API**: [API_SPECIFICATION.md](API_SPECIFICATION.md)
- **Module SPEC**: [SPEC.md](SPEC.md)
- **Agent guidance**: [AGENTS.md](AGENTS.md)
