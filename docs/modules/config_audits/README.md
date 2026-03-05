# Config Audits

Security, compliance, and best-practice auditing of configuration files.

> Source module: [`src/codomyrmex/config_audits/`](../../../src/codomyrmex/config_audits/)

## Key Capabilities

- **Secret Detection**: Identifies hardcoded passwords, API keys, and secrets in config files
- **Permission Auditing**: Verifies filesystem permissions on configuration files are appropriately restrictive
- **Syntax Validation**: Checks JSON and YAML configuration files for syntactic correctness
- **Environment Compliance**: Enforces environment-specific rules (e.g., debug mode disabled in production)
- **Report Generation**: Produces human-readable and machine-parsable audit reports

## Key Components

| Component | Purpose |
|-----------|---------|
| `ConfigAuditor` | Central orchestrator for running audits on files and directories |
| `AuditRule` | Pluggable rule definitions for specific audit checks |
| `AuditResult` | Structured results including identified issues and compliance status |

## Quick Start

```python
from codomyrmex.config_audits import ConfigAuditor

auditor = ConfigAuditor()
results = auditor.audit_directory("config/", pattern="*.json")
report = auditor.generate_report(results)
```

## MCP Tools

This module does not currently expose MCP tools. Use the Python API directly.

## References

- [Source README](../../../src/codomyrmex/config_audits/README.md)
- [AGENTS.md](../../../src/codomyrmex/config_audits/AGENTS.md)
- [PAI.md](../../../src/codomyrmex/config_audits/PAI.md)
