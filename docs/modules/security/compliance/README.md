# Security Compliance Submodule

**Version**: v0.1.7 | **Source**: [`src/codomyrmex/security/compliance/__init__.py`](../../../../src/codomyrmex/security/compliance/__init__.py)

## Overview

Compliance checking and policy enforcement for 6 frameworks: SOC2, HIPAA, GDPR, PCI-DSS, ISO 27001, and custom. Provides control definitions, pluggable checkers via ABC, and scored compliance reports.

## Components

| Class | Description |
|-------|-------------|
| `ComplianceChecker` | Main compliance assessment engine. Manages controls and checkers, produces `ComplianceReport` |
| `Control` | Dataclass defining a compliance control (ID, title, description, framework, category) |
| `ControlResult` | Dataclass representing the result of checking a single control, with `passed` property |
| `ComplianceReport` | Dataclass aggregating results with `compliance_score` (0-100), `passed_controls`, `failed_controls` |
| `ControlChecker` | Abstract base class for control verification implementations |
| `PolicyChecker` | Concrete checker using a callable (lambda/function) for pass/fail determination |
| `SOC2_CONTROLS` | Pre-built list of 3 SOC2 controls: CC1.1 (Access Control Policy), CC6.1 (Encryption at Rest), CC6.7 (Encryption in Transit) |

## Enums

### ComplianceFramework (6 values)
`SOC2` | `HIPAA` | `GDPR` | `PCI_DSS` | `ISO27001` | `CUSTOM`

### ControlStatus (5 values)
`PASSED` | `FAILED` | `PARTIAL` | `NOT_APPLICABLE` | `UNKNOWN`

## Usage

```python
from codomyrmex.security.compliance import (
    ComplianceChecker, ComplianceFramework, Control, PolicyChecker, SOC2_CONTROLS,
)

# Create checker with pre-built controls
checker = ComplianceChecker(ComplianceFramework.SOC2)
for control in SOC2_CONTROLS:
    checker.add_control(control)

# Add policy checkers
checker.add_checker(PolicyChecker(
    control_id="CC1.1",
    check_fn=lambda ctx: ctx.get("has_access_policy", False),
    pass_message="Access control policy exists",
    fail_message="Missing access control policy",
    remediation="Define and document access control policy",
))

checker.add_checker(PolicyChecker(
    control_id="CC6.1",
    check_fn=lambda ctx: ctx.get("encryption_at_rest", False),
))

# Run assessment
report = checker.assess({
    "has_access_policy": True,
    "encryption_at_rest": False,
})

print(f"Score: {report.compliance_score}%")
print(f"Passed: {report.passed_controls}/{report.total_controls}")

# Check single control
result = checker.check_control("CC1.1", {"has_access_policy": True})
```

## Pre-built SOC2 Controls

| ID | Title | Category |
|----|-------|----------|
| `CC1.1` | Access Control Policy | Common Criteria |
| `CC6.1` | Encryption at Rest | Common Criteria |
| `CC6.7` | Encryption in Transit | Common Criteria |

## Thread Safety

`ComplianceChecker` uses `threading.Lock` for report ID generation.

## Dependencies

No external dependencies. Uses only Python standard library (`json`, `threading`, `dataclasses`, `enum`, `abc`).

## Tests

[`src/codomyrmex/tests/unit/security/compliance/test_compliance.py`](../../../../src/codomyrmex/tests/unit/security/compliance/test_compliance.py)

## Navigation

- **Parent**: [Security Module](../README.md)
- **Source**: [`src/codomyrmex/security/compliance/`](../../../../src/codomyrmex/security/compliance/)
