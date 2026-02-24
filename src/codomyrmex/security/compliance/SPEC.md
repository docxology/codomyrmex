# Technical Specification - Compliance

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

**Module**: `codomyrmex.security.compliance`  
**Last Updated**: 2026-01-29

## 1. Purpose

GDPR, SOC2, HIPAA compliance checking and reporting

## 2. Architecture

### 2.1 Components

```
compliance/
├── __init__.py          # Module exports
├── README.md            # Documentation
├── AGENTS.md            # Agent guidelines
├── SPEC.md              # This file
├── PAI.md               # Personal AI context
└── core.py              # Core implementation
```

### 2.2 Dependencies

- Python 3.10+
- Parent module: `security`

## 3. Interfaces

### 3.1 Public API

```python
# Primary exports from codomyrmex.security.compliance
from codomyrmex.security.compliance import (
    ComplianceFramework, # Enum — SOC2, HIPAA, GDPR, PCI_DSS, ISO27001, CUSTOM
    ControlStatus,       # Enum — PASSED, FAILED, PARTIAL, NOT_APPLICABLE, UNKNOWN
    Control,             # Dataclass — compliance control definition (id, title,
                         #   description, framework, category, requirements, metadata)
    ControlResult,       # Dataclass — result of a control check (control_id, status,
                         #   message, evidence, remediation, checked_at); has .passed
    ComplianceReport,    # Dataclass — assessment report (report_id, framework, results,
                         #   created_at, metadata); has .total_controls, .passed_controls,
                         #   .failed_controls, .compliance_score
    ControlChecker,      # ABC — base checker interface (control_id, check)
    PolicyChecker,       # Callable-based checker with pass/fail messages and remediation
    ComplianceChecker,   # Main engine — add_control(), add_checker(), get_control(),
                         #   list_controls(), assess(), check_control()
    SOC2_CONTROLS,       # list[Control] — 3 pre-built SOC2 controls (CC1.1, CC6.1, CC6.7)
)

# Key class signatures:

class ControlChecker(ABC):
    @property
    def control_id(self) -> str: ...
    def check(self, context: dict[str, Any]) -> ControlResult: ...

class ComplianceChecker:
    def __init__(self, framework: ComplianceFramework): ...
    def add_control(self, control: Control) -> "ComplianceChecker": ...
    def add_checker(self, checker: ControlChecker) -> "ComplianceChecker": ...
    def get_control(self, control_id: str) -> Control | None: ...
    def list_controls(self) -> list[Control]: ...
    def assess(self, context: dict[str, Any]) -> ComplianceReport: ...
    def check_control(self, control_id: str,
                      context: dict[str, Any]) -> ControlResult | None: ...
```

### 3.2 Configuration

Environment variables:
- `CODOMYRMEX_*`: Configuration options

## 4. Implementation Notes

### 4.1 Design Decisions

1. **Framework-agnostic engine**: `ComplianceChecker` accepts any `ComplianceFramework` enum value, allowing the same engine to drive SOC2, HIPAA, GDPR, PCI-DSS, ISO 27001, or custom assessments.
2. **Callable-based PolicyChecker**: `PolicyChecker` wraps a plain `Callable[[dict], bool]` so that simple boolean checks can be registered without subclassing `ControlChecker`.
3. **Pre-built SOC2 controls**: Three starter controls (`CC1.1` Access Control Policy, `CC6.1` Encryption at Rest, `CC6.7` Encryption in Transit) ship as `SOC2_CONTROLS` for quick bootstrapping.

### 4.2 Limitations

- Only 3 pre-built SOC2 controls are included; real-world frameworks require dozens to hundreds of controls.
- No persistent report storage; `ComplianceReport` objects are in-memory only.
- `PolicyChecker` swallows exceptions and returns `UNKNOWN` status, which may hide checker implementation bugs.

## 5. Testing

```bash
# Run tests for this module
uv run pytest src/codomyrmex/tests/unit/security/compliance/
```

## 6. Future Considerations

- Add full control libraries for HIPAA, GDPR, and PCI-DSS frameworks beyond the current SOC2 starters.
- Implement persistent report storage with historical trend tracking and compliance score over time.
- Add evidence collection automation that gathers system state snapshots during control checks.
