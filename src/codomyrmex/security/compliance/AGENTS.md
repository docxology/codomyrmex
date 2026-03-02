# Codomyrmex Agents — src/codomyrmex/security/compliance

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Framework-agnostic compliance checking engine supporting SOC2, HIPAA, GDPR, PCI-DSS, ISO 27001, and custom frameworks. Provides pluggable control checkers, assessment reports with compliance scoring, and pre-built SOC2 starter controls.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `__init__.py` | `ComplianceFramework` | Enum: `SOC2`, `HIPAA`, `GDPR`, `PCI_DSS`, `ISO27001`, `CUSTOM` |
| `__init__.py` | `ControlStatus` | Enum: `PASSED`, `FAILED`, `PARTIAL`, `NOT_APPLICABLE`, `UNKNOWN` |
| `__init__.py` | `Control` | Dataclass defining a compliance control with `id`, `title`, `description`, `framework`, `category`, `requirements` |
| `__init__.py` | `ControlResult` | Dataclass with `status`, `message`, `evidence`, `remediation`; `.passed` property |
| `__init__.py` | `ComplianceReport` | Dataclass with computed properties: `.total_controls`, `.passed_controls`, `.failed_controls`, `.compliance_score` (0-100) |
| `__init__.py` | `ControlChecker` (ABC) | Abstract base with `control_id` property and `check(context)` method |
| `__init__.py` | `PolicyChecker` | Callable-based checker wrapping `Callable[[dict], bool]` with pass/fail messages |
| `__init__.py` | `ComplianceChecker` | Main engine: `add_control()`, `add_checker()`, `assess()`, `check_control()`, `list_controls()` |
| `__init__.py` | `SOC2_CONTROLS` | Pre-built list of 3 SOC2 controls: CC1.1 (Access Control Policy), CC6.1 (Encryption at Rest), CC6.7 (Encryption in Transit) |

## Operating Contracts

- `ComplianceChecker` supports fluent chaining: `add_control()` and `add_checker()` return `self`.
- `PolicyChecker` catches exceptions during check and returns `UNKNOWN` status rather than raising.
- `ComplianceReport.compliance_score` returns 0.0 when no controls are checked.
- Report IDs are auto-generated via a thread-safe counter.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: Standard library only (no external codomyrmex module imports)
- **Used by**: Security dashboards, governance audits, CI/CD compliance gates

## Navigation

- **Parent**: [security](../README.md)
- **Root**: [Root](../../../../README.md)
