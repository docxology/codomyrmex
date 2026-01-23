# Codomyrmex Agents — src/codomyrmex/security/digital

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

Provides comprehensive digital security capabilities including vulnerability scanning, secrets detection, security analysis, compliance checking, encryption management, SSL certificate validation, and real-time security monitoring.

## Active Components

- `vulnerability_scanner.py` - Vulnerability scanning with `VulnerabilityScanner`
- `secrets_detector.py` - Secrets detection with `SecretsDetector`
- `security_analyzer.py` - AST-based security analysis with `SecurityAnalyzer`
- `security_monitor.py` - Real-time monitoring with `SecurityMonitor`
- `compliance_checker.py` - Compliance validation with `ComplianceChecker`
- `encryption_manager.py` - Encryption utilities with `EncryptionManager`
- `certificate_validator.py` - SSL/TLS validation with `CertificateValidator`
- `security_reports.py` - Report generation utilities
- `__init__.py` - Module exports with conditional availability

## Key Classes and Functions

### vulnerability_scanner.py
- **`VulnerabilityScanner`** - Comprehensive vulnerability scanning:
  - `scan_vulnerabilities(target_path, scan_types)` - Full vulnerability scan.
  - `_scan_dependencies(target_path)` - Scan Python/Node.js dependencies.
  - `_scan_code_security(target_path)` - Code security analysis.
  - `_check_compliance(target_path)` - Compliance standard checks.
- **`VulnerabilityReport`** - Assessment report with `valid` property for Unified Streamline.
- **`SecurityScanResult`** - Individual scan operation results.
- **`ComplianceCheck`** - Compliance verification result.
- **Enums**: `SeverityLevel`, `ComplianceStandard` (OWASP_TOP_10, NIST_800_53, ISO_27001, PCI_DSS, GDPR, HIPAA).

### secrets_detector.py
- **`SecretsDetector`** - Detects secrets and credentials in code:
  - `scan_file(file_path)` - Scan single file for secrets.
  - `scan_directory(directory_path, recursive)` - Scan directory recursively.
  - Detects: AWS keys, private keys, GitHub tokens, Slack tokens, API keys, passwords.
  - Uses Shannon entropy analysis for high-entropy string detection.
- **`SecretFinding`** - Finding with file_path, line_number, secret_type, confidence.

### security_analyzer.py
- **`SecurityAnalyzer`** - AST and pattern-based security analysis:
  - `analyze_file(filepath)` - Analyze file for vulnerabilities.
  - `analyze_directory(directory, recursive)` - Analyze all supported files.
  - Detects: SQL injection, XSS, command injection, path traversal, insecure random, hardcoded secrets, weak crypto.
- **`SecurityFinding`** - Finding with issue_type, severity, CWE ID, recommendation.
- **`SecurityIssue`** - Enum of detectable issue types.
- **`ASTSecurityAnalyzer`** - AST visitor for Python security analysis.

### security_monitor.py
- **`SecurityMonitor`** - Real-time security event monitoring:
  - `start_monitoring()` / `stop_monitoring()` - Control monitoring loop.
  - `_collect_system_logs()` - Collect events from log files.
  - `_parse_log_line(line, source)` - Parse log lines for security events.
  - `_check_alert_rules(event)` - Evaluate events against alert rules.
- **`SecurityEvent`** - Event with type, timestamp, source_ip, user_id, severity.
- **`AlertRule`** - Rule with conditions, cooldown, alert level.
- **`SecurityEventType`** - Enum: AUTHENTICATION_FAILURE, AUTHORIZATION_FAILURE, SUSPICIOUS_ACTIVITY, etc.

### compliance_checker.py
- **`ComplianceChecker`** - Standards compliance validation:
  - `check_compliance(target_config, standards)` - Check against standards.
  - `get_compliance_score(results)` - Calculate compliance percentage.
- **`ComplianceControl`** - Security control definition.
- **`ComplianceResult`** - Check result with status and evidence.
- **`ComplianceStandard`** - Enum of supported standards.

### encryption_manager.py
- **`EncryptionManager`** - Encryption operations:
  - `encrypt(data)` / `decrypt(token)` - Symmetric encryption with Fernet.
  - `generate_key_pair()` - Generate RSA 2048-bit key pair.
  - `derive_key(password, salt)` - PBKDF2 key derivation.
- **Requires**: `cryptography` package.

### certificate_validator.py
- **`CertificateValidator`** - SSL/TLS certificate validation:
  - `validate_certificate(hostname, port)` - Validate server certificate.
  - Returns expiration days, issuer, subject, validation errors.
- **`SSLValidationResult`** - Validation result with certificate info.
- **Requires**: `OpenSSL` package.

## Operating Contracts

- All components are conditionally imported based on available dependencies.
- Vulnerability scans support multiple scan types: dependencies, code, compliance.
- Secrets detection skips binary files and common non-code files.
- Security monitoring runs in a background thread with configurable intervals.
- Alert rules have cooldown periods to prevent alert fatigue.
- Encryption uses strong defaults: Fernet (AES-128-CBC), RSA-2048, PBKDF2 with 100k iterations.

## Signposting

- **Dependencies**: Optional `cryptography`, `OpenSSL` packages.
- **Parent Directory**: [security](../README.md) - Parent module documentation.
- **Related Modules**:
  - `theory/` - Security frameworks and best practices.
  - `cognitive/` - Human factor security.
  - `physical/` - Physical security controls.
- **Project Root**: [../../../../README.md](../../../../README.md) - Main project documentation.
