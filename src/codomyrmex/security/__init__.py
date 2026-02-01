"""
Security Module for Codomyrmex.

The Security module provides comprehensive security capabilities organized into four
specialized submodules:
- physical: Physical security practices
- digital: Digital security
- cognitive: Cognitive security practices
- theory: Generic security considerations and theory

Integration:
- Uses `logging_monitoring` for all logging
- Relies on `environment_setup` for environment validation
- Integrates with `static_analysis` for code security analysis
"""

from . import scanning
from . import secrets
from . import compliance
from . import audit
__version__ = "0.1.0"

# Import from digital security
try:
    from .digital import (
        # Vulnerability scanning
        VulnerabilityScanner,
        scan_vulnerabilities,
        audit_code_security,
        VulnerabilityReport,
        SecurityScanResult,
        # Secrets detection
        SecretsDetector,
        audit_secrets_exposure,
        scan_file_for_secrets,
        scan_directory_for_secrets,
        # Security analysis
        SecurityAnalyzer,
        SecurityFinding,
        SecurityIssue,
        analyze_file_security,
        analyze_directory_security,
        # Compliance
        ComplianceChecker,
        ComplianceCheckResult,
        ComplianceRequirement,
        ComplianceStandard,
        check_compliance,
        # Monitoring
        SecurityMonitor,
        monitor_security_events,
        audit_access_logs,
        SecurityEvent,
        # Encryption
        EncryptionManager,
        encrypt_sensitive_data,
        decrypt_sensitive_data,
        # Certificates
        CertificateValidator,
        validate_ssl_certificates,
        SSLValidationResult,
        # Reporting
        SecurityReportGenerator,
        generate_security_report,
    )
    DIGITAL_AVAILABLE = True
except ImportError:
    DIGITAL_AVAILABLE = False

# Import from physical security
try:
    from .physical import (
        AccessControlSystem,
        check_access_permission,
        grant_access,
        revoke_access,
        AssetInventory,
        register_asset,
        track_asset,
        get_asset_status,
        SurveillanceMonitor,
        monitor_physical_access,
        log_physical_event,
        PhysicalVulnerabilityScanner,
        assess_physical_security,
        scan_physical_vulnerabilities,
        PerimeterManager,
        check_perimeter_security,
        manage_access_points,
    )
    PHYSICAL_AVAILABLE = True
except ImportError:
    PHYSICAL_AVAILABLE = False

# Import from cognitive security
try:
    from .cognitive import (
        SocialEngineeringDetector,
        detect_social_engineering,
        analyze_communication,
        PhishingAnalyzer,
        analyze_email,
        detect_phishing_attempt,
        AwarenessTrainer,
        create_training_module,
        assess_training_effectiveness,
        CognitiveThreatAssessor,
        assess_cognitive_threats,
        evaluate_human_factors,
        BehaviorAnalyzer,
        analyze_user_behavior,
        detect_anomalous_behavior,
    )
    COGNITIVE_AVAILABLE = True
except ImportError:
    COGNITIVE_AVAILABLE = False

# Import from theory
try:
    from .theory import (
        SecurityPrinciple,
        get_security_principles,
        apply_principle,
        SecurityFramework,
        get_framework,
        apply_framework,
        ThreatModel,
        create_threat_model,
        analyze_threats,
        RiskAssessment,
        assess_risk,
        calculate_risk_score,
        SecurityPattern,
        get_security_patterns,
        apply_pattern,
        SecurityBestPractice,
        get_best_practices,
        check_compliance_with_practices,
    )
    THEORY_AVAILABLE = True
except ImportError:
    THEORY_AVAILABLE = False

# Build __all__ dynamically
__all__ = [
    'audit',
    'compliance',
    'secrets',
    'scanning',]

if DIGITAL_AVAILABLE:
    __all__.extend([
        "VulnerabilityScanner",
        "scan_vulnerabilities",
        "audit_code_security",
        "VulnerabilityReport",
        "SecurityScanResult",
        "SecretsDetector",
        "audit_secrets_exposure",
        "scan_file_for_secrets",
        "scan_directory_for_secrets",
        "SecurityAnalyzer",
        "SecurityFinding",
        "SecurityIssue",
        "analyze_file_security",
        "analyze_directory_security",
        "ComplianceChecker",
        "ComplianceCheckResult",
        "ComplianceRequirement",
        "ComplianceStandard",
        "check_compliance",
        "SecurityMonitor",
        "monitor_security_events",
        "audit_access_logs",
        "SecurityEvent",
        "EncryptionManager",
        "encrypt_sensitive_data",
        "decrypt_sensitive_data",
        "CertificateValidator",
        "validate_ssl_certificates",
        "SSLValidationResult",
        "SecurityReportGenerator",
        "generate_security_report",
    ])

if PHYSICAL_AVAILABLE:
    __all__.extend([
        "AccessControlSystem",
        "check_access_permission",
        "grant_access",
        "revoke_access",
        "AssetInventory",
        "register_asset",
        "track_asset",
        "get_asset_status",
        "SurveillanceMonitor",
        "monitor_physical_access",
        "log_physical_event",
        "PhysicalVulnerabilityScanner",
        "assess_physical_security",
        "scan_physical_vulnerabilities",
        "PerimeterManager",
        "check_perimeter_security",
        "manage_access_points",
    ])

if COGNITIVE_AVAILABLE:
    __all__.extend([
        "SocialEngineeringDetector",
        "detect_social_engineering",
        "analyze_communication",
        "PhishingAnalyzer",
        "analyze_email",
        "detect_phishing_attempt",
        "AwarenessTrainer",
        "create_training_module",
        "assess_training_effectiveness",
        "CognitiveThreatAssessor",
        "assess_cognitive_threats",
        "evaluate_human_factors",
        "BehaviorAnalyzer",
        "analyze_user_behavior",
        "detect_anomalous_behavior",
    ])

if THEORY_AVAILABLE:
    __all__.extend([
        "SecurityPrinciple",
        "get_security_principles",
        "apply_principle",
        "SecurityFramework",
        "get_framework",
        "apply_framework",
        "ThreatModel",
        "create_threat_model",
        "analyze_threats",
        "RiskAssessment",
        "assess_risk",
        "calculate_risk_score",
        "SecurityPattern",
        "get_security_patterns",
        "apply_pattern",
        "SecurityBestPractice",
        "get_best_practices",
        "check_compliance_with_practices",
    ])

