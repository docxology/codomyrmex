# Config Audits -- Agent Coordination

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

The config_audits module provides security and compliance auditing for configuration files. It enables AI agents to scan configuration files for hardcoded secrets, overly permissive file permissions, JSON syntax errors, and debug mode in production. The rule-based architecture supports custom rules and generates structured audit reports with severity-graded issues and actionable recommendations.

## Key Files

| File | Class/Function | Role |
|------|----------------|------|
| `__init__.py` | Exports `ConfigAuditor`, `AuditIssue`, `AuditResult`, `AuditRule`, `DEFAULT_RULES` | Module entry point |
| `auditor.py` | `ConfigAuditor` | Orchestrates auditing: `audit_file()`, `audit_directory()`, `generate_report()` |
| `models.py` | `Severity` (Enum) | Severity levels: `LOW`, `MEDIUM`, `HIGH`, `CRITICAL` |
| `models.py` | `AuditIssue` (dataclass) | A single issue: rule_id, message, severity, file_path, location, recommendation |
| `models.py` | `AuditResult` (dataclass) | Result of an audit: audit_id, timestamp, issues list, success flag, summary. Property `is_compliant` returns True when no HIGH/CRITICAL issues exist |
| `models.py` | `AuditRule` (dataclass) | Rule definition: rule_id, description, severity, check_func (callable) |
| `rules.py` | `check_secrets` | SEC001: Detects hardcoded passwords, API keys, secrets, tokens via regex |
| `rules.py` | `check_permissions` | SEC002: Flags world-readable file permissions (mode & 0o004) |
| `rules.py` | `check_json_syntax` | SYN001: Validates JSON syntax for .json files |
| `rules.py` | `check_debug_enabled` | OPS001: Detects debug=true in production config files (path contains "prod") |
| `rules.py` | `DEFAULT_RULES` | List of the 4 built-in AuditRule objects |

## MCP Tools Available

This module exposes no MCP tools. Agents interact with it by importing `ConfigAuditor` and related classes from `codomyrmex.config_audits`.

## Agent Instructions

1. **Initialize with default or custom rules** -- `ConfigAuditor()` uses `DEFAULT_RULES` (4 rules). Pass a custom `rules` list to override: `ConfigAuditor(rules=[my_rule1, my_rule2])`.
2. **Audit single files** -- Call `auditor.audit_file("config.json")`. Returns an `AuditResult` with all issues found. Check `result.is_compliant` for pass/fail (no HIGH or CRITICAL issues).
3. **Audit directories** -- Call `auditor.audit_directory("config/", pattern="*.json")`. Default pattern scans `*.json`, `*.yaml`, and `*.yml`. Returns a list of `AuditResult` objects.
4. **Generate human-readable reports** -- Call `auditor.generate_report(results)` to produce a formatted string with issue counts by severity, per-file breakdowns, and recommendations.
5. **Write custom rules** -- Create an `AuditRule` with a `check_func(content: str, file_path: str | None) -> list[AuditIssue]`. The function receives file content as a string and the file path.
6. **Handle missing files** -- `audit_file()` returns an `AuditResult` with `success=False` and a SYS001 issue if the file does not exist, or SYS002 if it cannot be read.
7. **Check compliance programmatically** -- Use `result.is_compliant` property, which returns `True` only when there are no HIGH or CRITICAL severity issues.

## Operating Contracts

- `audit_file()` never raises exceptions. File-not-found and read errors are returned as `AuditResult` objects with `success=False` and corresponding `AuditIssue` entries.
- Rule execution errors are caught and logged. A SYS003 issue is appended but auditing continues with remaining rules.
- `AuditResult.is_compliant` returns `True` when no issues have `Severity.HIGH` or `Severity.CRITICAL`. `LOW` and `MEDIUM` issues do not affect compliance status.
- `audit_directory()` returns an empty list for non-existent or non-directory paths (logs error, does not raise).
- `DEFAULT_RULES` contains 4 rules: SEC001 (secrets), SEC002 (permissions), SYN001 (JSON syntax), OPS001 (debug mode). All are applied in order.
- The `check_debug_enabled` rule only triggers when the file path contains "prod" (case-insensitive).
- Each `AuditResult` receives a unique `audit_id` via `uuid.uuid4()`.
- **Zero-Mock Policy**: Tests must use real files on the filesystem. Use `pytest`'s `tmp_path` fixture for creating temporary config files with known content.
- **Rule extensibility**: New rules should be added to `rules.py` and included in `DEFAULT_RULES` if they are universally applicable.

## Common Patterns

```python
from codomyrmex.config_audits import ConfigAuditor

# Audit a single config file
auditor = ConfigAuditor()
result = auditor.audit_file("config/production.json")

if not result.is_compliant:
    print(f"FAIL: {len(result.issues)} issues found")
    for issue in result.issues:
        print(f"  [{issue.severity.value}] {issue.rule_id}: {issue.message}")
        if issue.recommendation:
            print(f"    Fix: {issue.recommendation}")
else:
    print("PASS: Configuration is compliant")
```

```python
from codomyrmex.config_audits import ConfigAuditor

# Audit all config files in a directory
auditor = ConfigAuditor()
results = auditor.audit_directory("config/")

# Generate a summary report
report = auditor.generate_report(results)
print(report)
```

```python
from codomyrmex.config_audits import AuditRule, AuditIssue, ConfigAuditor
from codomyrmex.config_audits.models import Severity

# Create a custom audit rule
def check_max_nesting(content: str, file_path: str | None) -> list[AuditIssue]:
    depth = max(content.count("{"), content.count("["))
    issues = []
    if depth > 10:
        issues.append(AuditIssue(
            rule_id="CUSTOM001",
            message=f"Excessive nesting depth ({depth} levels)",
            severity=Severity.MEDIUM,
            file_path=file_path,
            recommendation="Flatten configuration structure."
        ))
    return issues

custom_rule = AuditRule(
    rule_id="CUSTOM001",
    description="Check nesting depth",
    severity=Severity.MEDIUM,
    check_func=check_max_nesting,
)

# Use custom rules alongside defaults
from codomyrmex.config_audits import DEFAULT_RULES
auditor = ConfigAuditor(rules=DEFAULT_RULES + [custom_rule])
```

## Testing Patterns

```python
from codomyrmex.config_audits import ConfigAuditor
from codomyrmex.config_audits.models import Severity

class TestConfigAuditor:
    def test_detects_hardcoded_secret(self, tmp_path):
        config_file = tmp_path / "config.json"
        config_file.write_text('{"password": "s3cret123"}')

        auditor = ConfigAuditor()
        result = auditor.audit_file(str(config_file))
        assert not result.is_compliant
        assert any(i.rule_id == "SEC001" for i in result.issues)

    def test_valid_config_is_compliant(self, tmp_path):
        config_file = tmp_path / "config.json"
        config_file.write_text('{"host": "localhost", "port": 8080}')

        auditor = ConfigAuditor()
        result = auditor.audit_file(str(config_file))
        assert result.is_compliant

    def test_missing_file_returns_failure(self):
        auditor = ConfigAuditor()
        result = auditor.audit_file("/nonexistent/config.json")
        assert not result.success
        assert any(i.rule_id == "SYS001" for i in result.issues)
```

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | Primary Use |
|-----------|-------------|-------------|
| **Engineer** | Full | Audit configs during BUILD, create custom rules for project-specific checks |
| **Architect** | Design | Review audit rule coverage and compliance thresholds during PLAN |
| **QATester** | Validation | Run full directory audits and verify compliance during VERIFY |
| **Researcher** | Read-only | Inspect audit reports and issue patterns during OBSERVE |

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
