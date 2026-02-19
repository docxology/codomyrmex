# Security Theory Submodule

**Version**: v0.1.7 | **Source**: [`src/codomyrmex/security/theory/`](../../../../src/codomyrmex/security/theory/)

## Overview

Generic security considerations, principles, frameworks, threat modeling, risk assessment, architecture patterns, and best practices. Organized across 6 component files, each conditionally imported.

## Components

| Source File | Classes / Functions | Availability Flag |
|-------------|--------------------|--------------------|
| `principles.py` | `SecurityPrinciple`, `PrincipleCategory`, `get_security_principles()`, `get_principle()`, `get_principles_by_category()`, `apply_principle()`, `validate_principle_application()` | `PRINCIPLES_AVAILABLE` |
| `frameworks.py` | `SecurityFramework`, `FrameworkStandard`, `FrameworkCategory`, `get_framework()`, `get_all_frameworks()`, `get_frameworks_by_category()`, `apply_framework()`, `check_framework_compliance()` | `FRAMEWORKS_AVAILABLE` |
| `threat_modeling.py` | `Threat`, `ThreatModel`, `ThreatSeverity`, `ThreatCategory`, `ThreatModelBuilder`, `create_threat_model()`, `analyze_threats()`, `prioritize_threats()` | `THREAT_MODELING_AVAILABLE` |
| `risk_assessment.py` | `Risk`, `RiskAssessment`, `RiskLevel`, `LikelihoodLevel`, `ImpactLevel`, `RiskAssessor`, `assess_risk()`, `calculate_risk_score()`, `prioritize_risks()`, `calculate_aggregate_risk()` | `RISK_ASSESSMENT_AVAILABLE` |
| `architecture_patterns.py` | `SecurityPattern`, `PatternCategory`, `get_security_patterns()`, `get_pattern()`, `get_patterns_by_category()`, `apply_pattern()`, `validate_pattern_application()` | `ARCHITECTURE_PATTERNS_AVAILABLE` |
| `best_practices.py` | `SecurityBestPractice`, `PracticeCategory`, `PracticePriority`, `get_best_practices()`, `get_practice()`, `get_practices_by_priority()`, `get_practices_for_category()`, `check_compliance_with_practices()`, `prioritize_practices()` | `BEST_PRACTICES_AVAILABLE` |

## Exports (via top-level `security/__init__.py`)

When `THEORY_AVAILABLE` is `True`, the following key symbols are re-exported:
- `SecurityPrinciple`, `get_security_principles`, `apply_principle`
- `SecurityFramework`, `get_framework`, `apply_framework`
- `ThreatModel`, `create_threat_model`, `analyze_threats`
- `RiskAssessment`, `assess_risk`, `calculate_risk_score`
- `SecurityPattern`, `get_security_patterns`, `apply_pattern`
- `SecurityBestPractice`, `get_best_practices`, `check_compliance_with_practices`

## Key Classes

### SecurityPrinciple
Security principles organized by `PrincipleCategory`. Supports retrieval, application, and validation.

### SecurityFramework
Framework definitions (e.g., NIST, ISO) with standards, categories, compliance checking, and application methods.

### ThreatModel / ThreatModelBuilder
Threat modeling with `Threat` objects, `ThreatSeverity` and `ThreatCategory` enums. `ThreatModelBuilder` provides a fluent API for model construction.

### RiskAssessment / RiskAssessor
Risk assessment with `Risk` objects, `RiskLevel`, `LikelihoodLevel`, and `ImpactLevel` enums. Supports scoring, prioritization, and aggregate risk calculation.

### SecurityPattern
Security architecture patterns organized by `PatternCategory`. Supports retrieval, application, and validation.

### SecurityBestPractice
Best practices organized by `PracticeCategory` and `PracticePriority`. Supports compliance checking and prioritization.

## Tests

[`src/codomyrmex/tests/unit/security/test_security_theory.py`](../../../../src/codomyrmex/tests/unit/security/test_security_theory.py)

## Navigation

- **Parent**: [Security Module](../README.md)
- **Source**: [`src/codomyrmex/security/theory/`](../../../../src/codomyrmex/security/theory/)
