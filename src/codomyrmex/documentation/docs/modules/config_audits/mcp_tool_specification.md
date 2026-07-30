# Config Audits MCP Tool Specification

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: June 2026

## Tools

### `config_audits_audit_file`

- **Purpose**: Audit one configuration file against the default rules.
- **Parameters**: `file_path: str`
- **Returns**: `status`, `audit_id`, `is_compliant`, `issue_count`, `issues`, and `summary`.

### `config_audits_audit_directory`

- **Purpose**: Audit every file matching a glob pattern in a directory.
- **Parameters**: `directory_path: str`, `pattern: str = "*.json"`
- **Returns**: `status`, `files_audited`, `total_issues`, and `results`.

### `config_audits_generate_report`

- **Purpose**: Audit a directory and produce a formatted report string.
- **Parameters**: `directory_path: str`, `pattern: str = "*.json"`
- **Returns**: `status` and `report`.

## Error Contract

All tools catch runtime failures and return `{"status": "error", "message": str(exc)}`.

## Navigation

- **Python API**: [API_SPECIFICATION.md](API_SPECIFICATION.md)
- **Module SPEC**: [SPEC.md](SPEC.md)
- **Agent guidance**: [AGENTS.md](AGENTS.md)
