# Codomyrmex Agents — src/codomyrmex/security/digital

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
Digital security including vulnerability scanning, encryption management, certificate validation, secrets detection, compliance checking, security analysis, monitoring, and reporting. Provides comprehensive digital security capabilities.

## Active Components
- `API_SPECIFICATION.md` – Detailed API specification
- `CHANGELOG.md` – Version history
- `README.md` – Project file
- `SECURITY.md` – Security considerations
- `SPEC.md` – Project file
- `__init__.py` – Module exports and public API
- `certificate_validator.py` – Certificate validation
- `compliance_checker.py` – Compliance checking
- `encryption_manager.py` – Encryption management
- `requirements.txt` – Project file
- `secrets_detector.py` – Secrets detection in code
- `security_analyzer.py` – Security analysis
- `security_monitor.py` – Security monitoring
- `security_reports.py` – Security reporting
- `vulnerability_scanner.py` – Vulnerability scanning

## Key Classes and Functions

### VulnerabilityScanner (`vulnerability_scanner.py`)
- `VulnerabilityScanner()` – Scan for vulnerabilities
- `scan_codebase(path: str) -> list[Vulnerability]` – Scan codebase for vulnerabilities
- `scan_dependencies(dependencies: dict) -> list[Vulnerability]` – Scan dependencies

### SecretsDetector (`secrets_detector.py`)
- `SecretsDetector()` – Detect secrets in code
- `detect_secrets(code: str) -> list[SecretFinding]` – Detect secrets in code
- `scan_file(file_path: str) -> list[SecretFinding]` – Scan file for secrets

### EncryptionManager (`encryption_manager.py`)
- `EncryptionManager()` – Manage encryption
- `encrypt_data(data: str, key: str) -> str` – Encrypt data
- `decrypt_data(encrypted_data: str, key: str) -> str` – Decrypt data

### CertificateValidator (`certificate_validator.py`)
- `CertificateValidator()` – Validate certificates
- `validate_certificate(cert_path: str) -> ValidationResult` – Validate certificate

### ComplianceChecker (`compliance_checker.py`)
- `ComplianceChecker()` – Check compliance
- `check_compliance(config: dict) -> ComplianceResult` – Check compliance with standards

### SecurityAnalyzer (`security_analyzer.py`)
- `SecurityAnalyzer()` – Analyze security posture
- `analyze_security(config: dict) -> SecurityAnalysis` – Analyze security

### SecurityMonitor (`security_monitor.py`)
- `SecurityMonitor()` – Monitor security events
- `monitor_events() -> Iterator[SecurityEvent]` – Monitor security events

### SecurityReports (`security_reports.py`)
- `SecurityReports()` – Generate security reports
- `generate_report(analysis: SecurityAnalysis) -> Report` – Generate security report

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **📁 Parent Directory**: [security](../README.md) - Parent directory documentation
- **🏠 Project Root**: [README](../../../../README.md) - Main project documentation