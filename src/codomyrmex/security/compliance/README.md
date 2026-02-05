# compliance

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Compliance checking and policy enforcement for the security module. Provides a framework for defining compliance controls against standard frameworks (SOC2, HIPAA, GDPR, PCI-DSS, ISO 27001), running automated assessments via pluggable checker functions, and generating compliance reports with pass/fail/partial status, remediation guidance, and a computed compliance score. Ships with pre-built SOC2 control definitions.

## Key Exports

- **`ComplianceFramework`** -- Enum of supported compliance frameworks: SOC2, HIPAA, GDPR, PCI_DSS, ISO27001, CUSTOM
- **`ControlStatus`** -- Enum of control check outcomes: PASSED, FAILED, PARTIAL, NOT_APPLICABLE, UNKNOWN
- **`Control`** -- Dataclass defining a compliance control with ID, title, description, framework, category, and requirements
- **`ControlResult`** -- Dataclass capturing a single control check outcome with status, message, evidence list, and remediation text
- **`ComplianceReport`** -- Dataclass representing a full assessment report with computed properties for total/passed/failed controls and a 0-100 compliance score
- **`ControlChecker`** -- Abstract base class for control checkers that implement a `check()` method against a context dict
- **`PolicyChecker`** -- Concrete checker that evaluates a callable predicate and returns pass/fail results with configurable messages and remediation
- **`ComplianceChecker`** -- Main compliance engine: registers controls and checkers, runs full assessments or single-control checks, and produces ComplianceReport instances
- **`SOC2_CONTROLS`** -- Pre-built list of SOC2 Common Criteria control definitions (CC1.1 Access Control Policy, CC6.1 Encryption at Rest, CC6.7 Encryption in Transit)

## Directory Contents

- `__init__.py` - All compliance classes, enums, dataclasses, and pre-built SOC2 controls
- `README.md` - This file
- `SPEC.md` - Module specification
- `AGENTS.md` - Agent integration notes
- `PAI.md` - PAI algorithm context
- `py.typed` - PEP 561 typing marker

## Navigation

- **Parent Module**: [security](../README.md)
- **Project Root**: [../../../../README.md](../../../../README.md)
