# Security Module - Index

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Table of Contents

### Top-Level Documentation
- [README.md](README.md) - Module overview, submodule summary, quick start
- [SPEC.md](SPEC.md) - Design specification, functional requirements, data models
- [AGENTS.md](AGENTS.md) - Agent integration, operating contracts, extensibility
- [technical_overview.md](technical_overview.md) - Architecture diagrams, conditional imports, enums, design decisions

### Submodule Documentation

#### Core Submodules (standalone, no external dependencies)
- [scanning/README.md](scanning/README.md) - Static application security testing (SAST) with extensible rules
- [secrets/README.md](secrets/README.md) - Secret detection, vault storage, helper utilities
- [audit/README.md](audit/README.md) - Audit logging with pluggable storage backends
- [compliance/README.md](compliance/README.md) - Compliance checking across 6 frameworks

#### Domain Submodules (may require optional dependencies)
- [digital/README.md](digital/README.md) - Digital security: vulnerability scanning, encryption, certificates, monitoring, reporting
- [physical/README.md](physical/README.md) - Physical security: access control, asset tracking, surveillance, perimeters
- [cognitive/README.md](cognitive/README.md) - Cognitive security: social engineering, phishing, awareness training, behavior analysis
- [theory/README.md](theory/README.md) - Security theory: principles, frameworks, threat modeling, risk assessment, patterns
- [ai_safety/README.md](ai_safety/README.md) - AI safety: jailbreak detection, prompt injection defense, adversarial containment, safety monitoring
- [governance/README.md](governance/README.md) - Governance: contract management, policy enforcement, dispute resolution

### Source Code
- [`src/codomyrmex/security/__init__.py`](../../../src/codomyrmex/security/__init__.py) - Master exports
- [`src/codomyrmex/security/scanning/__init__.py`](../../../src/codomyrmex/security/scanning/__init__.py) - Scanning implementation
- [`src/codomyrmex/security/secrets/__init__.py`](../../../src/codomyrmex/security/secrets/__init__.py) - Secrets implementation
- [`src/codomyrmex/security/audit/__init__.py`](../../../src/codomyrmex/security/audit/__init__.py) - Audit implementation
- [`src/codomyrmex/security/compliance/__init__.py`](../../../src/codomyrmex/security/compliance/__init__.py) - Compliance implementation
- [`src/codomyrmex/security/digital/__init__.py`](../../../src/codomyrmex/security/digital/__init__.py) - Digital security exports
- [`src/codomyrmex/security/physical/__init__.py`](../../../src/codomyrmex/security/physical/__init__.py) - Physical security exports
- [`src/codomyrmex/security/cognitive/__init__.py`](../../../src/codomyrmex/security/cognitive/__init__.py) - Cognitive security exports
- [`src/codomyrmex/security/theory/__init__.py`](../../../src/codomyrmex/security/theory/__init__.py) - Theory exports
- [`src/codomyrmex/security/ai_safety/__init__.py`](../../../src/codomyrmex/security/ai_safety/__init__.py) - AI safety exports
- [`src/codomyrmex/security/governance/__init__.py`](../../../src/codomyrmex/security/governance/__init__.py) - Governance exports

### Tests
- [`src/codomyrmex/tests/unit/security/scanning/test_scanning.py`](../../../src/codomyrmex/tests/unit/security/scanning/test_scanning.py)
- [`src/codomyrmex/tests/unit/security/secrets/test_secrets.py`](../../../src/codomyrmex/tests/unit/security/secrets/test_secrets.py)
- [`src/codomyrmex/tests/unit/security/audit/test_audit.py`](../../../src/codomyrmex/tests/unit/security/audit/test_audit.py)
- [`src/codomyrmex/tests/unit/security/compliance/test_compliance.py`](../../../src/codomyrmex/tests/unit/security/compliance/test_compliance.py)
- [`src/codomyrmex/tests/unit/security/test_security_digital.py`](../../../src/codomyrmex/tests/unit/security/test_security_digital.py)
- [`src/codomyrmex/tests/unit/security/test_security_physical.py`](../../../src/codomyrmex/tests/unit/security/test_security_physical.py)
- [`src/codomyrmex/tests/unit/security/test_security_cognitive.py`](../../../src/codomyrmex/tests/unit/security/test_security_cognitive.py)
- [`src/codomyrmex/tests/unit/security/test_security_theory.py`](../../../src/codomyrmex/tests/unit/security/test_security_theory.py)

## Navigation

- **Parent**: [README.md](README.md)
- **Source**: [`src/codomyrmex/security/`](../../../src/codomyrmex/security/)
- **Root**: [../../../README.md](../../../README.md)
