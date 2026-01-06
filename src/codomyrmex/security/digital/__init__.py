"""
Digital Security Submodule for Codomyrmex Security Module.

The Digital Security submodule provides security analysis, vulnerability scanning,
compliance checking, and security monitoring capabilities for the Codomyrmex ecosystem.

This submodule provides digital security capabilities as part of the comprehensive security module.

Integration:
- Uses `logging_monitoring` for all logging
- Relies on `environment_setup` for environment and dependency checks
- Integrates with `static_analysis` for code security analysis
"""

# Import components conditionally based on available dependencies
try:
    from .certificate_validator import (
        CertificateValidator,
        SSLValidationResult,
        validate_ssl_certificates,
    )
    CERTIFICATE_VALIDATION_AVAILABLE = True
except ImportError:
    CertificateValidator = None
    SSLValidationResult = None
    validate_ssl_certificates = None
    CERTIFICATE_VALIDATION_AVAILABLE = False

try:
    from .encryption_manager import (
        EncryptionManager,
        decrypt_sensitive_data,
        encrypt_sensitive_data,
    )
    ENCRYPTION_AVAILABLE = True
except ImportError:
    EncryptionManager = None
    decrypt_sensitive_data = None
    encrypt_sensitive_data = None
    ENCRYPTION_AVAILABLE = False

try:
    from .security_monitor import (
        SecurityEvent,
        SecurityMonitor,
        audit_access_logs,
        monitor_security_events,
    )
    SECURITY_MONITORING_AVAILABLE = True
except ImportError:
    SecurityEvent = None
    SecurityMonitor = None
    audit_access_logs = None
    monitor_security_events = None
    SECURITY_MONITORING_AVAILABLE = False

try:
    from .security_reports import (
        SecurityReportGenerator,
        generate_security_report,
    )
    SECURITY_REPORTING_AVAILABLE = True
except ImportError:
    SecurityReportGenerator = None
    generate_security_report = None
    SECURITY_REPORTING_AVAILABLE = False

try:
    from .vulnerability_scanner import (
        ComplianceCheck,
        SecurityScanResult,
        VulnerabilityReport,
        VulnerabilityScanner,
        audit_code_security,
        check_compliance,
        scan_vulnerabilities,
    )
    VULNERABILITY_SCANNING_AVAILABLE = True
except ImportError:
    ComplianceCheck = None
    SecurityScanResult = None
    VulnerabilityReport = None
    VulnerabilityScanner = None
    audit_code_security = None
    check_compliance = None
    scan_vulnerabilities = None
    VULNERABILITY_SCANNING_AVAILABLE = False

try:
    from .secrets_detector import (
        SecretsDetector,
        audit_secrets_exposure,
        scan_file_for_secrets,
        scan_directory_for_secrets,
    )
    SECRETS_DETECTION_AVAILABLE = True
except ImportError:
    SecretsDetector = None
    audit_secrets_exposure = None
    scan_file_for_secrets = None
    scan_directory_for_secrets = None
    SECRETS_DETECTION_AVAILABLE = False

try:
    from .security_analyzer import (
        SecurityAnalyzer,
        SecurityFinding,
        SecurityIssue,
        analyze_file_security,
        analyze_directory_security,
    )
    SECURITY_ANALYSIS_AVAILABLE = True
except ImportError:
    SecurityAnalyzer = None
    SecurityFinding = None
    SecurityIssue = None
    analyze_file_security = None
    analyze_directory_security = None
    SECURITY_ANALYSIS_AVAILABLE = False

try:
    from .compliance_checker import (
        ComplianceChecker,
        ComplianceCheckResult,
        ComplianceRequirement,
        ComplianceStandard,
        check_compliance as check_compliance_new,
    )
    COMPLIANCE_CHECKING_AVAILABLE = True
except ImportError:
    ComplianceChecker = None
    ComplianceCheckResult = None
    ComplianceRequirement = None
    ComplianceStandard = None
    check_compliance_new = None
    COMPLIANCE_CHECKING_AVAILABLE = False

# Build __all__ dynamically based on available components
__all__ = []

# Core security scanning
if VULNERABILITY_SCANNING_AVAILABLE:
    __all__.extend([
        "VulnerabilityScanner",
        "scan_vulnerabilities",
        "audit_code_security",
        "check_compliance",
        "VulnerabilityReport",
        "SecurityScanResult",
        "ComplianceCheck",
    ])

# Enhanced security features
if SECRETS_DETECTION_AVAILABLE:
    __all__.extend([
        "SecretsDetector",
        "audit_secrets_exposure",
        "scan_file_for_secrets",
        "scan_directory_for_secrets",
    ])

if SECURITY_ANALYSIS_AVAILABLE:
    __all__.extend([
        "SecurityAnalyzer",
        "SecurityFinding",
        "SecurityIssue",
        "analyze_file_security",
        "analyze_directory_security",
    ])

if COMPLIANCE_CHECKING_AVAILABLE:
    __all__.extend([
        "ComplianceChecker",
        "ComplianceCheckResult",
        "ComplianceRequirement",
        "ComplianceStandard",
        "check_compliance_new",
    ])

# Security monitoring
if SECURITY_MONITORING_AVAILABLE:
    __all__.extend([
        "SecurityMonitor",
        "monitor_security_events",
        "audit_access_logs",
        "SecurityEvent",
    ])

# Encryption and certificates
if ENCRYPTION_AVAILABLE:
    __all__.extend([
        "EncryptionManager",
        "encrypt_sensitive_data",
        "decrypt_sensitive_data",
    ])

if CERTIFICATE_VALIDATION_AVAILABLE:
    __all__.extend([
        "CertificateValidator",
        "validate_ssl_certificates",
        "SSLValidationResult",
    ])

# Reporting
if SECURITY_REPORTING_AVAILABLE:
    __all__.extend([
        "generate_security_report",
        "SecurityReportGenerator",
    ])
