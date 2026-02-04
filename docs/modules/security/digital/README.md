# Security Digital Submodule

**Version**: v0.1.0 | **Source**: [`src/codomyrmex/security/digital/`](../../../../src/codomyrmex/security/digital/)

## Overview

Comprehensive digital security capabilities including vulnerability scanning, secrets detection, security analysis, compliance checking, encryption, certificate validation, security monitoring, and report generation. Organized across 8 component files, each conditionally imported with availability flags.

## Components

| Source File | Classes / Functions | Availability Flag |
|-------------|--------------------|--------------------|
| `vulnerability_scanner.py` | `VulnerabilityScanner`, `VulnerabilityReport`, `SecurityScanResult`, `ComplianceCheck`, `scan_vulnerabilities()`, `audit_code_security()`, `check_compliance()` | `VULNERABILITY_SCANNING_AVAILABLE` |
| `secrets_detector.py` | `SecretsDetector`, `scan_file_for_secrets()`, `scan_directory_for_secrets()`, `audit_secrets_exposure()` | `SECRETS_DETECTION_AVAILABLE` |
| `security_analyzer.py` | `SecurityAnalyzer`, `SecurityFinding`, `SecurityIssue`, `analyze_file_security()`, `analyze_directory_security()` | `SECURITY_ANALYSIS_AVAILABLE` |
| `compliance_checker.py` | `ComplianceChecker`, `ComplianceCheckResult`, `ComplianceRequirement`, `ComplianceStandard` | `COMPLIANCE_CHECKING_AVAILABLE` |
| `encryption_manager.py` | `EncryptionManager`, `encrypt_sensitive_data()`, `decrypt_sensitive_data()` | `ENCRYPTION_AVAILABLE` |
| `certificate_validator.py` | `CertificateValidator`, `SSLValidationResult`, `validate_ssl_certificates()` | `CERTIFICATE_VALIDATION_AVAILABLE` |
| `security_monitor.py` | `SecurityMonitor`, `SecurityEvent`, `monitor_security_events()`, `audit_access_logs()` | `SECURITY_MONITORING_AVAILABLE` |
| `security_reports.py` | `SecurityReportGenerator`, `generate_security_report()` | `SECURITY_REPORTING_AVAILABLE` |

## Exports (via top-level `security/__init__.py`)

When `DIGITAL_AVAILABLE` is `True`, the following are re-exported at the `codomyrmex.security` level:

- `VulnerabilityScanner`, `scan_vulnerabilities`, `audit_code_security`, `VulnerabilityReport`, `SecurityScanResult`
- `SecretsDetector`, `audit_secrets_exposure`, `scan_file_for_secrets`, `scan_directory_for_secrets`
- `SecurityAnalyzer`, `SecurityFinding`, `SecurityIssue`, `analyze_file_security`, `analyze_directory_security`
- `ComplianceChecker`, `ComplianceCheckResult`, `ComplianceRequirement`, `ComplianceStandard`, `check_compliance`
- `SecurityMonitor`, `monitor_security_events`, `audit_access_logs`, `SecurityEvent`
- `EncryptionManager`, `encrypt_sensitive_data`, `decrypt_sensitive_data`
- `CertificateValidator`, `validate_ssl_certificates`, `SSLValidationResult`
- `SecurityReportGenerator`, `generate_security_report`

## Conditional Import Pattern

Each component file is imported independently:
```python
try:
    from .encryption_manager import EncryptionManager, encrypt_sensitive_data, decrypt_sensitive_data
    ENCRYPTION_AVAILABLE = True
except ImportError:
    EncryptionManager = None
    ENCRYPTION_AVAILABLE = False
```

This allows partial functionality when some optional dependencies (e.g., `cryptography`, `pyOpenSSL`, `jinja2`) are not installed.

## Optional Dependencies

- `cryptography` - Required by `encryption_manager.py` and `certificate_validator.py`
- `pyOpenSSL` - Required by `certificate_validator.py`
- `jinja2` - Required by `security_reports.py`

## Tests

[`src/codomyrmex/tests/unit/security/test_security_digital.py`](../../../../src/codomyrmex/tests/unit/security/test_security_digital.py)

## Navigation

- **Parent**: [Security Module](../README.md)
- **Source**: [`src/codomyrmex/security/digital/`](../../../../src/codomyrmex/security/digital/)
