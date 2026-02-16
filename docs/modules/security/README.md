# Security Module Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Security module provides comprehensive security capabilities for the Codomyrmex platform, organized into **8 specialized submodules** covering digital, physical, cognitive, and theoretical security domains, plus dedicated audit logging, compliance checking, static scanning, and secrets management.

All submodules use a **conditional import pattern** with graceful degradation: each submodule's exports are wrapped in `try/except ImportError` blocks with corresponding `*_AVAILABLE` flags, allowing the module to function even when optional dependencies are not installed.

## Submodule Summary

| Submodule | Description | Key Classes | Docs |
|-----------|-------------|-------------|------|
| **digital** | Digital security: vulnerability scanning, encryption, certificates, compliance, monitoring, reporting | `VulnerabilityScanner`, `EncryptionManager`, `CertificateValidator`, `SecurityMonitor`, `SecurityReportGenerator` | [digital/](digital/README.md) |
| **physical** | Physical security: access control, asset tracking, surveillance, perimeter management | `AccessControlSystem`, `AssetInventory`, `SurveillanceMonitor`, `PerimeterManager` | [physical/](physical/README.md) |
| **cognitive** | Cognitive security: social engineering detection, phishing analysis, awareness training | `SocialEngineeringDetector`, `PhishingAnalyzer`, `AwarenessTrainer`, `BehaviorAnalyzer` | [cognitive/](cognitive/README.md) |
| **theory** | Security theory: principles, frameworks, threat modeling, risk assessment, patterns, best practices | `SecurityPrinciple`, `SecurityFramework`, `ThreatModel`, `RiskAssessor`, `SecurityPattern` | [theory/](theory/README.md) |
| **audit** | Audit logging and event tracking with pluggable storage backends | `AuditLogger`, `AuditEvent`, `InMemoryAuditStore`, `FileAuditStore` | [audit/](audit/README.md) |
| **compliance** | Compliance checking and policy enforcement across frameworks (SOC2, HIPAA, GDPR, PCI-DSS, ISO 27001) | `ComplianceChecker`, `Control`, `ComplianceReport`, `PolicyChecker` | [compliance/](compliance/README.md) |
| **scanning** | Static application security testing with extensible rule engine | `SecurityScanner`, `SecurityFinding`, `ScanResult`, `PatternRule` | [scanning/](scanning/README.md) |
| **secrets** | Secret detection, scanning, vault storage, and helper utilities | `SecretScanner`, `SecretVault`, `DetectedSecret`, `SecretPatterns` | [secrets/](secrets/README.md) |

## Directory Contents

- `README.md` - This file (module overview)
- `SPEC.md` - Design specification and functional requirements
- `AGENTS.md` - Agent integration and operating contracts
- `index.md` - Table of contents with deep links
- `technical_overview.md` - Architecture, data models, and design decisions
- `digital/README.md` - Digital security submodule documentation
- `physical/README.md` - Physical security submodule documentation
- `cognitive/README.md` - Cognitive security submodule documentation
- `theory/README.md` - Security theory submodule documentation
- `audit/README.md` - Audit logging submodule documentation
- `compliance/README.md` - Compliance checking submodule documentation
- `scanning/README.md` - Security scanning submodule documentation
- `secrets/README.md` - Secrets management submodule documentation

## Quick Start

```python
# Scan code for security vulnerabilities
from codomyrmex.security.scanning import SecurityScanner

scanner = SecurityScanner()
result = scanner.scan_directory("src/")
for finding in result.findings:
    print(f"{finding.severity.value}: {finding.title} at {finding.file_path}:{finding.line_number}")

# Detect secrets in code
from codomyrmex.security.secrets import SecretScanner

secret_scanner = SecretScanner()
result = secret_scanner.scan_text('api_key = "AKIA1234567890ABCDEF"')
print(f"Found {len(result.secrets_found)} secrets")

# Audit logging
from codomyrmex.security.audit import AuditLogger, AuditEventType

audit = AuditLogger()
audit.log(event_type=AuditEventType.AUTH_LOGIN, action="user_login", actor="user@example.com")

# Compliance checking
from codomyrmex.security.compliance import ComplianceChecker, ComplianceFramework

checker = ComplianceChecker(ComplianceFramework.SOC2)
report = checker.assess({"has_access_policy": True})
print(f"Compliance score: {report.compliance_score}%")
```

## Dependencies

- **Required**: `logging_monitoring` (internal)
- **Optional**: `cryptography`, `pyOpenSSL` (for digital/encryption and certificate features), `jinja2` (for report generation)

When optional dependencies are missing, the corresponding submodule features are still importable but the availability flag will be `False`.

## Navigation

- **Source**: [`src/codomyrmex/security/`](../../../src/codomyrmex/security/)
- **Parent Directory**: [modules](../README.md)
- **Project Root**: [../../../README.md](../../../README.md)
- **Technical Overview**: [technical_overview.md](technical_overview.md)
- **Index**: [index.md](index.md)
