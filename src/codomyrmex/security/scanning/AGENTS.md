# Codomyrmex Agents — src/codomyrmex/security/scanning

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Automated CVE scanning against installed Python dependencies using pip-audit and safety as backends. Produces structured `ScanReport` objects with vulnerability details and generates fix commands.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `vulnerability_scanner.py` | `Vulnerability` | Dataclass with `package`, `installed_version`, `vulnerability_id`, `description`, `fix_versions`, `severity`, `url`; has `.to_dict()` |
| `vulnerability_scanner.py` | `ScanReport` | Dataclass with `vulnerabilities`, `packages_scanned`, `scan_tool`, `success`, `error`; computed `.critical_count`, `.high_count` |
| `vulnerability_scanner.py` | `VulnerabilityScanner` | Main scanner: `scan_pip_audit()` (primary), `scan_safety()` (fallback), `scan()` (best available), `generate_fix_commands()` |

## Operating Contracts

- `scan()` tries `scan_pip_audit()` first; falls back to `scan_safety()` only if pip-audit fails.
- Both scan methods use `subprocess.run()` with a 120-second timeout.
- `scan_pip_audit()` returns `ScanReport(success=False)` with error message when pip-audit is not installed (no exception raised to caller).
- `generate_fix_commands()` produces deduplicated `pip install` commands targeting the latest fix version for each vulnerable package.
- External tool output parsing failures (JSON decode, missing keys) are caught and return empty results.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: Standard library (`subprocess`, `json`, `logging`)
- **External tools**: `pip-audit` (primary), `safety` (fallback) -- both optional
- **Used by**: CI/CD security gates, `security` parent module MCP tool `scan_vulnerabilities`

## Navigation

- **Parent**: [security](../README.md)
- **Root**: [Root](../../../../README.md)
