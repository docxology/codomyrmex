# Codomyrmex Agents — src/codomyrmex/security

## Signposting
- **Parent**: [codomyrmex](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - [cognitive](cognitive/AGENTS.md)
    - [digital](digital/AGENTS.md)
    - [docs](docs/AGENTS.md)
    - [physical](physical/AGENTS.md)
    - [security_theory](security_theory/AGENTS.md)
    - [tests](tests/AGENTS.md)
    - [theory](theory/AGENTS.md)
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose
Security scanning and threat assessment across cognitive, digital, and physical domains. Provides comprehensive security analysis including vulnerability scanning, compliance checking, threat modeling, and security monitoring. Integrates cognitive security (phishing, social engineering), digital security (vulnerabilities, encryption, certificates), and physical security assessments.

## Active Components
- `README.md` – Project file
- `SPEC.md` – Project file
- `__init__.py` – Module exports and public API
- `cognitive/` – Directory containing cognitive security components (phishing analysis, social engineering detection, awareness training)
- `digital/` – Directory containing digital security components (vulnerability scanning, encryption, certificates, compliance)
- `docs/` – Directory containing docs components
- `physical/` – Directory containing physical security components
- `security_theory/` – Directory containing security theory components
- `tests/` – Directory containing tests components
- `theory/` – Directory containing security theory components

## Key Classes and Functions

### SecurityScanner (`__init__.py`)
- `SecurityScanner()` – Main security scanner
- `scan_codebase(path: str) -> dict` – Scan codebase for security issues

### VulnerabilityDetector (`__init__.py`)
- `VulnerabilityDetector()` – Detect security vulnerabilities
- `check_vulnerabilities(dependencies: dict) -> list` – Check dependencies for vulnerabilities

### ComplianceChecker (`__init__.py`)
- `ComplianceChecker()` – Check compliance with security standards
- `check_compliance(config: dict) -> ComplianceResult` – Check compliance

### ThreatModeler (`__init__.py`)
- `ThreatModeler()` – Model security threats
- `assess_threats(system: dict) -> ThreatAssessment` – Assess threats

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **📁 Parent Directory**: [codomyrmex](../README.md) - Parent directory documentation
- **🏠 Project Root**: [README](../../../README.md) - Main project documentation