"""
Security Module for Codomyrmex.

The Security module provides comprehensive security capabilities organized into nine
specialized submodules:
- physical: Physical security practices
- digital: Digital security
- cognitive: Cognitive security practices
- theory: Generic security considerations and theory
- ai_safety: AI-specific security monitoring and defense
- scanning: Static application security testing
- secrets: Secret detection and exposure auditing
- audit: Security audit logging
- compliance: Compliance standards checking
- governance: Consolidated governance capabilities

Integration:
- Uses `logging_monitoring` for all logging
- Relies on `environment_setup` for environment validation
- Integrates with `static_analysis` for code security analysis
"""

from . import audit, compliance, scanning, secrets

# Import AI safety
try:
    from .ai_safety import AISafetyMonitor
    AI_SAFETY_AVAILABLE = True
except ImportError:
    AISafetyMonitor = None
    AI_SAFETY_AVAILABLE = False

__version__ = "0.1.0"

# Import from digital security
try:
    from .digital import (
        # Certificates
        CertificateValidator,
        # Compliance
        ComplianceChecker,
        ComplianceCheckResult,
        ComplianceRequirement,
        ComplianceStandard,
        # Encryption
        EncryptionManager,
        # Secrets detection
        SecretsDetector,
        # Security analysis
        SecurityAnalyzer,
        SecurityEvent,
        SecurityFinding,
        SecurityIssue,
        # Monitoring
        SecurityMonitor,
        # Reporting
        SecurityReportGenerator,
        SecurityScanResult,
        SSLValidationResult,
        VulnerabilityReport,
        # Vulnerability scanning
        VulnerabilityScanner,
        analyze_directory_security,
        analyze_file_security,
        audit_access_logs,
        audit_code_security,
        audit_secrets_exposure,
        check_compliance,
        decrypt_sensitive_data,
        encrypt_sensitive_data,
        generate_security_report,
        monitor_security_events,
        scan_directory_for_secrets,
        scan_file_for_secrets,
        scan_vulnerabilities,
        validate_ssl_certificates,
    )
    DIGITAL_AVAILABLE = True
except ImportError:
    DIGITAL_AVAILABLE = False

# Import from physical security
try:
    from .physical import (
        AccessControlSystem,
        AssetInventory,
        PerimeterManager,
        PhysicalVulnerabilityScanner,
        SurveillanceMonitor,
        assess_physical_security,
        check_access_permission,
        check_perimeter_security,
        get_asset_status,
        grant_access,
        log_physical_event,
        manage_access_points,
        monitor_physical_access,
        register_asset,
        revoke_access,
        scan_physical_vulnerabilities,
        track_asset,
    )
    PHYSICAL_AVAILABLE = True
except ImportError:
    PHYSICAL_AVAILABLE = False

# Import from cognitive security
try:
    from .cognitive import (
        AwarenessTrainer,
        BehaviorAnalyzer,
        CognitiveThreatAssessor,
        PhishingAnalyzer,
        SocialEngineeringDetector,
        analyze_communication,
        analyze_email,
        analyze_user_behavior,
        assess_cognitive_threats,
        assess_training_effectiveness,
        create_training_module,
        detect_anomalous_behavior,
        detect_phishing_attempt,
        detect_social_engineering,
        evaluate_human_factors,
    )
    COGNITIVE_AVAILABLE = True
except ImportError:
    COGNITIVE_AVAILABLE = False

# Import from theory
try:
    from .theory import (
        RiskAssessment,
        SecurityBestPractice,
        SecurityFramework,
        SecurityPattern,
        SecurityPrinciple,
        ThreatModel,
        analyze_threats,
        apply_framework,
        apply_pattern,
        apply_principle,
        assess_risk,
        calculate_risk_score,
        check_compliance_with_practices,
        create_threat_model,
        get_best_practices,
        get_framework,
        get_security_patterns,
        get_security_principles,
    )
    THEORY_AVAILABLE = True
except ImportError:
    THEORY_AVAILABLE = False

# Build __all__ dynamically
from . import governance

__all__ = [
    "governance",
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

if AI_SAFETY_AVAILABLE:
    __all__.append("AISafetyMonitor")


# =============================================================================
# MCP Tools
# =============================================================================

from typing import Any, Dict, List

from codomyrmex.model_context_protocol.decorators import mcp_tool


@mcp_tool(category="security")
def scan_project_security(path: str = ".") -> dict[str, Any]:
    """
    Run a full security scan on the project (vulnerabilities + secrets).

    Args:
        path: Root path to scan (default: current directory)

    Returns:
        Structured security report.
    """
    results = {}

    if DIGITAL_AVAILABLE:
        # 1. Vulnerabilities
        try:
            vuln_report = scan_vulnerabilities(path)
            results["vulnerabilities"] = {
                "count": len(vuln_report.findings) if hasattr(vuln_report, "findings") else 0,
                "report": str(vuln_report)
            }
        except Exception as e:
            results["vulnerabilities"] = {"error": str(e)}

        # 2. Secrets
        try:
            secrets = scan_directory_for_secrets(path)
            results["secrets"] = {
                "count": len(secrets),
                "findings": [s.to_dict() for s in secrets] if secrets else []
            }
        except Exception as e:
            results["secrets"] = {"error": str(e)}

    else:
        return {"error": "Digital security module not available."}

    return results

@mcp_tool(category="security")
def security_audit_code(path: str) -> dict[str, Any]:
    """
    Audit code quality and security for a specific file or directory.

    Args:
        path: Path to file or directory

    Returns:
        Audit results.
    """
    if not DIGITAL_AVAILABLE:
        return {"error": "Digital security module not available."}

    try:
        return audit_code_security(path)
    except Exception as e:
        return {"error": str(e)}

