# Config Audits API Specification

**Version**: v1.2.7 | **Status**: Active | **Last Updated**: June 2026

## Purpose

`codomyrmex.config_audits` audits configuration files for security,
compliance, and best-practice issues using real filesystem inputs and rule
objects.

## Python API

| Symbol | Type | Purpose |
|:---|:---|:---|
| `ConfigAuditor` | Class | Audits files/directories and produces audit results |
| `AuditRule` | Dataclass | Describes a rule id, pattern, severity, and recommendation |
| `AuditIssue` | Dataclass | Describes a single rule violation |
| `AuditResult` | Dataclass | Captures compliance status, issues, and summary |
| `DEFAULT_RULES` | Constant | Built-in rules used by the default auditor |

## MCP API

| Tool | Parameters | Returns |
|:---|:---|:---|
| `config_audits_audit_file` | `file_path: str` | Status, audit id, compliance flag, issue count, issues, and summary |
| `config_audits_audit_directory` | `directory_path: str`, `pattern: str = "*.json"` | Status, files audited, total issues, and per-file summaries |
| `config_audits_generate_report` | `directory_path: str`, `pattern: str = "*.json"` | Status and formatted report text |

## Error Shape

MCP tools return dictionaries with `status: "error"` and `message` when an
operation fails. Successful calls return `status: "success"` plus tool-specific
fields.

## Navigation

- **Module README**: [README.md](README.md)
- **Module SPEC**: [SPEC.md](SPEC.md)
- **MCP tools**: [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md)
- **Agent guidance**: [AGENTS.md](AGENTS.md)
- **PAI notes**: [PAI.md](PAI.md)
