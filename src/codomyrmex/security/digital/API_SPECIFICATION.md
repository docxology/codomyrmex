# Security Audit - API Specification

## Introduction

This API specification documents the programmatic interfaces for the Security Audit module of Codomyrmex. The module provides comprehensive security analysis, vulnerability scanning, compliance checking, and security monitoring capabilities for the Codomyrmex ecosystem.

## Functions

All functions below are importable from `codomyrmex.security.digital`.

### Function: `scan_vulnerabilities(target_path: str, scan_types: list[str] | None = None) -> VulnerabilityReport`

- **Description**: Scan a path for vulnerabilities with a new `VulnerabilityScanner`.
- **Parameters**:
    - `target_path`: File or directory to scan.
    - `scan_types`: Any of `"dependencies"`, `"code"` and `"compliance"` (default: the scanner's configured `scan_types`, `["dependencies", "code"]`).
- **Return Value**: A `VulnerabilityReport` with `vulnerabilities`, `compliance_checks` and scan metadata.

### Function: `audit_code_security(target_path: str) -> list[dict[str, Any]]`

- **Description**: Run only the `"code"` scan of `scan_vulnerabilities()`.
- **Parameters**:
    - `target_path`: File or directory of source code to audit.
- **Return Value**: The report's `vulnerabilities` list.

### Function: `check_compliance(target_path: str, standards: list[str] | None = None) -> list[dict[str, Any]]`

- **Description**: Run only the `"compliance"` scan of `scan_vulnerabilities()`.
- **Parameters**:
    - `target_path`: Path to the codebase or configuration to check.
    - `standards`: Compliance standards to check against (default: the scanner's configured `compliance_standards`).
- **Return Value**: The report's `compliance_checks` list.

### Function: `monitor_security_events(config_path: str | None = None) -> SecurityMonitor`

- **Description**: Create a `SecurityMonitor` and start its background monitoring thread. Call `stop_monitoring()` on the result to stop it.
- **Parameters**:
    - `config_path`: Path to a monitor configuration file (log files, interval, alert settings).
- **Return Value**: The running `SecurityMonitor`.

### Function: `generate_security_report(vulnerability_data: dict[str, Any], compliance_data: dict[str, Any], monitoring_data: dict[str, Any], output_path: str | None = None) -> SecurityReport`

- **Description**: Combine vulnerability, compliance and monitoring data into one report with `SecurityReportGenerator.generate_comprehensive_report()`.
- **Parameters**:
    - `vulnerability_data`: Vulnerability scan data.
    - `compliance_data`: Compliance check data.
    - `monitoring_data`: Security monitoring data.
    - `output_path`: When given, the report is also exported there as JSON.
- **Return Value**: A `SecurityReport` (`report_id`, `title`, `generated_at`, `target_system`, `executive_summary`, `risk_assessment`, `findings`, `recommendations`, `compliance_status`, `metrics`, `appendices`); `to_dict()` gives the JSON form.

### Function: `scan_secrets(target_path: str, recursive: bool = True) -> list[dict[str, Any]]`

- **Description**: Scan a file or directory for hard-coded secrets with a `SecretsDetector` (pattern matching plus entropy analysis). This replaces the former `audit_secrets_exposure()`, `scan_file_for_secrets()` and `scan_directory_for_secrets()`, which do not exist.
- **Parameters**:
    - `target_path`: File or directory to scan.
    - `recursive`: Scan subdirectories when `target_path` is a directory.
- **Return Value**: One dictionary per finding: `file_path`, `line_number`, `secret_type`, `confidence` (`HIGH`, `MEDIUM` or `LOW`), `description` and `snippet` (the line, truncated to 100 characters). Use `SecretsDetector().scan_file()` or `scan_directory()` for `SecretFinding` objects.

### Function: `analyze_file_security(filepath: str) -> List[SecurityFinding]`

- **Description**: Analyze a file for security vulnerabilities using AST and pattern matching.
- **Parameters**:
    - `filepath`: Path to file to analyze
- **Return Value**: List of security findings with severity, confidence, and recommendations
- **Errors**: Returns empty list if file cannot be analyzed

### Function: `analyze_directory_security(directory: str, recursive: bool = True) -> List[SecurityFinding]`

- **Description**: Analyze all files in a directory for security vulnerabilities.
- **Parameters**:
    - `directory`: Directory path to analyze
    - `recursive`: Whether to analyze subdirectories (default: True)
- **Return Value**: List of all security findings across all analyzed files
- **Errors**: Returns empty list if directory cannot be accessed

### Function: `encrypt_sensitive_data(data: str | bytes) -> dict[str, bytes]`

- **Description**: Encrypt data with a freshly generated Fernet (symmetric) key.
- **Parameters**:
    - `data`: Plaintext string or bytes.
- **Return Value**: `{"encrypted_data": <bytes>, "key": <bytes>}`; keep `key` to decrypt.

### Function: `decrypt_sensitive_data(encrypted_data: bytes, key: bytes) -> str`

- **Description**: Decrypt data produced by `encrypt_sensitive_data()`.
- **Parameters**:
    - `encrypted_data`: Ciphertext bytes from `encrypt_sensitive_data()`.
    - `key`: The Fernet key returned alongside the ciphertext.
- **Return Value**: The decrypted plaintext string.

### Function: `validate_ssl_certificates(hostname: str, port: int = 443, timeout: int = 10) -> dict[str, Any]`

- **Description**: Connect to a host and validate its TLS certificate with a `CertificateValidator`.
- **Parameters**:
    - `hostname`: Hostname or IP address to connect to.
    - `port`: TCP port (default: 443).
    - `timeout`: Connection timeout in seconds (default: 10).
- **Return Value**: The `SSLValidationResult` as a dictionary: `hostname`, `port`, `valid`, `certificate_info`, `validation_errors`, `expiration_days`, `issuer`, `subject`, `serial_number`.

### Function: `audit_access_logs(log_files: list[str] | None = None) -> list[SecurityEvent]`

- **Description**: Read the last 100 lines of each log file and extract security events (authentication failures, suspicious activity and similar) with a `SecurityMonitor`.
- **Parameters**:
    - `log_files`: Log files to read (default: the monitor's configured files, `/var/log/auth.log` and `/var/log/security.log`). Missing files are skipped.
- **Return Value**: The `SecurityEvent` objects found.

## Classes

### Class: `SecretsDetector`

- **Description**: Pattern- and entropy-based detection of hard-coded secrets.
- **Methods**:
    - `__init__(patterns: dict[str, str] | None = None)`: Use custom regex patterns instead of the built-in `PATTERNS`
    - `scan_file(file_path: str) -> list[SecretFinding]`: Scan a single file
    - `scan_directory(directory_path: str, recursive: bool = True) -> list[SecretFinding]`: Scan a directory

### Class: `SecurityAnalyzer`

- **Description**: Advanced security analyzer using AST and pattern matching.
- **Methods**:
    - `__init__()`: Initialize analyzer
    - `analyze_file(filepath: str) -> List[SecurityFinding]`: Analyze single file
    - `analyze_directory(directory: str, recursive: bool = True) -> List[SecurityFinding]`: Analyze directory

### Class: `ComplianceChecker`

- **Description**: Comprehensive compliance checker against multiple security standards.
- **Methods**:
    - `__init__(standards: Optional[List[str]] = None)`: Initialize with compliance standards
    - `check_compliance(target_path: str, standards: Optional[List[str]] = None) -> List[ComplianceCheckResult]`: Perform compliance checking

### Class: `ExecutionLimits`

- **Description**: Dataclass for configuring resource limits (belongs to code_execution_sandbox module).
- **Attributes**:
    - `time_limit`: Maximum execution time in seconds
    - `memory_limit`: Memory limit in MB
    - `cpu_limit`: CPU cores limit
    - `max_output_chars`: Maximum output characters

### Class: `ResourceMonitor`

- **Description**: Monitors resource usage during execution (belongs to code_execution_sandbox module).
- **Methods**:
    - `start_monitoring()`: Begin monitoring
    - `update_monitoring()`: Update usage metrics
    - `get_resource_usage()`: Get comprehensive usage statistics

## Data Structures

### VulnerabilityReport

Comprehensive vulnerability assessment results:

```python
{
    "scan_id": <str>,
    "target": <str>,
    "scan_timestamp": <timestamp>,
    "duration_seconds": <float>,
    "vulnerabilities": [
        {
            "cve_id": <str>,
            "severity": "critical|high|medium|low",
            "package": <str>,
            "version": <str>,
            "fixed_version": <str>,
            "description": <str>,
            "cvss_score": <float>,
            "exploit_available": <bool>
        }
    ],
    "summary": {
        "total_vulnerabilities": <int>,
        "critical_count": <int>,
        "high_count": <int>,
        "medium_count": <int>,
        "low_count": <int>,
        "risk_score": <float>
    },
    "recommendations": [<list_of_fix_recommendations>]
}
```

### SecurityScanResult

Results from security code scanning:

```python
{
    "scan_id": <str>,
    "target_path": <str>,
    "scan_type": <str>,
    "files_scanned": <int>,
    "lines_scanned": <int>,
    "findings": [
        {
            "file": <str>,
            "line": <int>,
            "rule_id": <str>,
            "severity": "critical|high|medium|low",
            "message": <str>,
            "code_snippet": <str>,
            "recommendation": <str>
        }
    ],
    "metrics": {
        "cyclomatic_complexity_avg": <float>,
        "duplicate_code_percentage": <float>,
        "security_score": <float>
    }
}
```

### ComplianceCheck

Compliance verification results:

```python
{
    "check_id": <str>,
    "standard": <str>,
    "target": <str>,
    "compliance_status": "compliant|non_compliant|partial",
    "score": <float>,
    "requirements_checked": <int>,
    "requirements_passed": <int>,
    "violations": [
        {
            "requirement_id": <str>,
            "severity": "high|medium|low",
            "description": <str>,
            "remediation": <str>
        }
    ],
    "evidence": [<list_of_compliance_evidence>],
    "next_audit_date": <timestamp>
}
```

### SecurityEvent

Security monitoring event data:

```python
{
    "event_id": <str>,
    "timestamp": <timestamp>,
    "event_type": <str>,
    "severity": "critical|high|medium|low|info",
    "source": <str>,
    "description": <str>,
    "user_id": <str>,
    "ip_address": <str>,
    "resource": <str>,
    "action": <str>,
    "metadata": {<event_specific_data>},
    "alert_triggered": <bool>
}
```

### SSLValidationResult

SSL certificate validation results:

```python
{
    "hostname": <str>,
    "port": <int>,
    "certificate_valid": <bool>,
    "certificate_info": {
        "subject": <str>,
        "issuer": <str>,
        "valid_from": <timestamp>,
        "valid_until": <timestamp>,
        "serial_number": <str>,
        "signature_algorithm": <str>
    },
    "validation_errors": [<list_of_validation_errors>],
    "chain_valid": <bool>,
    "revocation_status": <str>,
    "security_score": <float>,
    "recommendations": [<list_of_security_recommendations>]
}
```

## Error Handling

All functions follow consistent error handling patterns:

- **Scan Errors**: `SecurityScanError` for vulnerability scanning failures
- **Audit Errors**: `SecurityAuditError` for security audit execution failures
- **Compliance Errors**: `ComplianceError` for compliance checking failures
- **Monitoring Errors**: `MonitoringError` for security monitoring setup failures
- **Report Errors**: `ReportGenerationError` for security report creation failures
- **Encryption Errors**: `EncryptionError` for cryptographic operation failures
- **Decryption Errors**: `DecryptionError` for decryption operation failures
- **Certificate Errors**: `CertificateError` for SSL validation failures
- **Log Audit Errors**: `AuditError` for access log analysis failures

## Integration Patterns

### Comprehensive Security Assessment

```python
from codomyrmex.security.digital import (
    audit_code_security,
    check_compliance,
    generate_security_report,
    scan_vulnerabilities,
)

# Scan dependencies and code for vulnerabilities
vuln_report = scan_vulnerabilities("./", scan_types=["dependencies", "code"])

# Audit source code only
code_findings = audit_code_security("./src")

# Check compliance
compliance_checks = check_compliance("./", standards=["OWASP", "NIST"])

# Combine the results into one report (also written to JSON)
report = generate_security_report(
    vulnerability_data=vuln_report.to_dict(),
    compliance_data={"checks": compliance_checks},
    monitoring_data={},
    output_path="output/security_report.json",
)
```

### Real-time Security Monitoring

```python
from codomyrmex.security.digital import monitor_security_events

# Start the background monitoring thread
monitor = monitor_security_events()

# Inspect collected events
for event in monitor.events:
    if event.severity.value in ("CRITICAL", "HIGH"):
        print(event.to_dict())

monitor.stop_monitoring()
```

### Data Encryption Pipeline

```python
import json

from codomyrmex.security.digital import decrypt_sensitive_data, encrypt_sensitive_data

# Encrypt sensitive configuration with a fresh key
encrypted = encrypt_sensitive_data(json.dumps({"service_url": "https://example.com"}))

# Store encrypted["encrypted_data"]; keep encrypted["key"] in a secret store

# Later, decrypt when needed
config = json.loads(
    decrypt_sensitive_data(encrypted["encrypted_data"], encrypted["key"])
)
```

## Security Considerations

- **Zero Trust Architecture**: All security functions assume breach and validate thoroughly
- **Defense in Depth**: Multiple security layers protect against various attack vectors
- **Secure by Default**: Conservative security settings with opt-in flexibility
- **Audit Trail**: Comprehensive logging of all security operations
- **Compliance Focus**: Adherence to industry standards and regulatory requirements
- **Performance Security**: Security measures don't compromise system performance
- **Key Management**: Secure cryptographic key lifecycle management
- **Incident Response**: Automated alerting and incident response capabilities

## Performance Characteristics

- **Efficient Scanning**: Optimized vulnerability scanning with minimal false positives
- **Scalable Monitoring**: Real-time security monitoring with configurable performance
- **Fast Encryption**: High-performance cryptographic operations
- **Resource Aware**: Security operations respect system resource limits
- **Parallel Processing**: Concurrent security analysis for large codebases
- **Caching**: Security scan results caching for improved performance
- **Streaming Analysis**: Real-time security event processing and alerting

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../../docs/README.md)
- **Home**: [Root README](../../../README.md)
