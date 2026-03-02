# Personal AI Infrastructure -- Config Audits Module

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Configuration auditing module that validates config files against defined rules and reports compliance issues. Provides `ConfigAuditor` for scanning individual files or entire directories against `DEFAULT_RULES` and custom `AuditRule` sets.

## PAI Capabilities

### Configuration Compliance Auditing

```python
from codomyrmex.config_audits import ConfigAuditor, DEFAULT_RULES

auditor = ConfigAuditor(rules=DEFAULT_RULES)

# Audit a single config file
result: AuditResult = auditor.audit_file("pyproject.toml")
for issue in result.issues:
    print(f"{issue.severity}: {issue.message}")

# Audit all configs in a directory
results: list[AuditResult] = auditor.audit_directory("configs/", pattern="*.toml")
```

## PAI Phase Mapping

| Phase   | Tool/Class    | Usage                                          |
|---------|---------------|-------------------------------------------------|
| OBSERVE | ConfigAuditor.audit_file      | Scan a config file for rule violations |
| OBSERVE | ConfigAuditor.audit_directory | Scan all matching configs in a directory |
| VERIFY  | AuditResult   | Inspect issues list and compliance status        |

## Key Exports

| Export        | Type      | Description                          |
|---------------|-----------|--------------------------------------|
| ConfigAuditor | Class     | Main auditing engine                 |
| AuditIssue    | Dataclass | Single audit finding                 |
| AuditResult   | Dataclass | Aggregated result from an audit pass |
| AuditRule     | Dataclass | Rule definition for audits           |
| DEFAULT_RULES | Constant  | Built-in rule set                    |

## Integration Notes

- No `mcp_tools.py` -- this module is not auto-discovered via MCP.
- Call directly from Python when PAI agents need config compliance checks.
- Pairs with `config_management` module for get/set and `validation` for schema checks.
