"""
Security Audit Module for Codomyrmex.

The Security Audit module provides comprehensive security analysis, vulnerability scanning,
compliance checking, and security monitoring capabilities for the Codomyrmex ecosystem.

Integration:
- Uses `logging_monitoring` for all logging (ensure `setup_logging()` is called in your main app).
- Relies on `environment_setup` for environment and dependency checks.
- Integrates with `static_analysis` for code security analysis.

Available functions:
- scan_vulnerabilities: Scan for security vulnerabilities in dependencies and code
- audit_code_security: Perform comprehensive code security analysis
- check_compliance: Verify compliance with security standards and policies
- monitor_security_events: Real-time security monitoring and alerting
- generate_security_report: Generate detailed security assessment reports
- encrypt_sensitive_data: Handle encryption of sensitive data
- validate_ssl_certificates: SSL/TLS certificate validation
- audit_access_logs: Security audit logging and analysis

Data structures:
- VulnerabilityReport: Detailed vulnerability assessment results
- SecurityScanResult: Results from security scans
- ComplianceCheck: Compliance verification results
- SecurityEvent: Security monitoring events
- EncryptionManager: Sensitive data encryption/decryption
- CertificateValidator: SSL certificate validation results
"""

from .vulnerability_scanner import (
    VulnerabilityScanner,
    scan_vulnerabilities,
    audit_code_security,
    check_compliance,
    VulnerabilityReport,
    SecurityScanResult,
    ComplianceCheck,
)

from .security_monitor import (
    SecurityMonitor,
    monitor_security_events,
    audit_access_logs,
    SecurityEvent,
)

from .encryption_manager import (
    EncryptionManager,
    encrypt_sensitive_data,
    decrypt_sensitive_data,
)

from .certificate_validator import (
    CertificateValidator,
    validate_ssl_certificates,
    SSLValidationResult,
)

from .security_reports import (
    generate_security_report,
    SecurityReportGenerator,
)

__all__ = [
    # Core security scanning
    "VulnerabilityScanner",
    "scan_vulnerabilities",
    "audit_code_security",
    "check_compliance",
    "VulnerabilityReport",
    "SecurityScanResult",
    "ComplianceCheck",
    # Security monitoring
    "SecurityMonitor",
    "monitor_security_events",
    "audit_access_logs",
    "SecurityEvent",
    # Encryption and certificates
    "EncryptionManager",
    "encrypt_sensitive_data",
    "decrypt_sensitive_data",
    "CertificateValidator",
    "validate_ssl_certificates",
    "SSLValidationResult",
    # Reporting
    "generate_security_report",
    "SecurityReportGenerator",
]
