# Codomyrmex Agents — src/codomyrmex/security/theory

## Signposting
- **Parent**: [security](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose
Security theory including architecture patterns, best practices, security frameworks, security principles, risk assessment, and threat modeling. Provides theoretical foundations and methodologies for security analysis.

## Active Components
- `README.md` – Project file
- `SPEC.md` – Project file
- `__init__.py` – Module exports and public API
- `architecture_patterns.py` – Security architecture patterns
- `best_practices.py` – Security best practices
- `frameworks.py` – Security frameworks
- `principles.py` – Security principles
- `risk_assessment.py` – Risk assessment methodologies
- `threat_modeling.py` – Threat modeling techniques

## Key Classes and Functions

### ArchitecturePatterns (`architecture_patterns.py`)
- `ArchitecturePatterns()` – Security architecture patterns
- `get_pattern(pattern_name: str) -> Pattern` – Get architecture pattern

### BestPractices (`best_practices.py`)
- `BestPractices()` – Security best practices
- `get_practices(category: str) -> list[Practice]` – Get best practices

### SecurityFrameworks (`frameworks.py`)
- `SecurityFrameworks()` – Security frameworks
- `get_framework(framework_name: str) -> Framework` – Get security framework

### SecurityPrinciples (`principles.py`)
- `SecurityPrinciples()` – Security principles
- `get_principles() -> list[Principle]` – Get security principles

### RiskAssessment (`risk_assessment.py`)
- `RiskAssessment()` – Risk assessment methodologies
- `assess_risk(context: dict) -> RiskAssessment` – Assess risk

### ThreatModeling (`threat_modeling.py`)
- `ThreatModeling()` – Threat modeling techniques
- `model_threats(system: dict) -> ThreatModel` – Model threats

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **📁 Parent Directory**: [security](../README.md) - Parent directory documentation
- **🏠 Project Root**: [README](../../../../README.md) - Main project documentation