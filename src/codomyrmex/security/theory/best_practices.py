from typing import List, Dict, Any, Optional

from dataclasses import dataclass, field
from enum import Enum

from codomyrmex.logging_monitoring.logger_config import get_logger




























































"""Security best practices."""



"""Core functionality module

This module provides best_practices functionality including:
- 6 functions: get_best_practices, get_practice, get_practices_by_priority...
- 3 classes: PracticeCategory, PracticePriority, SecurityBestPractice

Usage:
    # Example usage here
"""
logger = get_logger(__name__)


class PracticeCategory(Enum):
    """Categories of security best practices."""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATA_PROTECTION = "data_protection"
    CODING = "coding"
    CONFIGURATION = "configuration"
    OPERATIONS = "operations"
    NETWORK = "network"
    CRYPTOGRAPHY = "cryptography"
    INCIDENT_RESPONSE = "incident_response"
    COMPLIANCE = "compliance"


class PracticePriority(Enum):
    """Priority levels for best practices."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SecurityBestPractice:
    """Represents a security best practice."""
    
    name: str
    description: str
    category: str  # coding, configuration, operations, etc.
    priority: str  # low, medium, high, critical
    implementation: str
    rationale: Optional[str] = None
    examples: List[str] = field(default_factory=list)
    related_practices: List[str] = field(default_factory=list)
    compliance_requirements: List[str] = field(default_factory=list)
    tools: List[str] = field(default_factory=list)


# Comprehensive security best practices
BEST_PRACTICES = {
    "strong_passwords": SecurityBestPractice(
        name="Strong Passwords",
        description="Use complex, unique passwords with sufficient length and complexity",
        category=PracticeCategory.AUTHENTICATION.value,
        priority=PracticePriority.HIGH.value,
        implementation="Enforce password complexity requirements: minimum length (12+), mix of character types, no common passwords",
        rationale="Weak passwords are easily compromised through brute force or credential stuffing attacks",
        examples=[
            "Password policy: 12+ characters, uppercase, lowercase, numbers, symbols",
            "Password history: prevent reuse of last 5 passwords",
            "Password expiration: 90 days for standard users, 30 days for privileged users"
        ],
        related_practices=["multi_factor_authentication", "password_manager"],
        compliance_requirements=["NIST 800-63B", "PCI DSS 8.2"],
        tools=["Password policy enforcement", "Password strength meters"]
    ),
    "multi_factor_authentication": SecurityBestPractice(
        name="Multi-Factor Authentication",
        description="Require multiple authentication factors for access",
        category=PracticeCategory.AUTHENTICATION.value,
        priority=PracticePriority.CRITICAL.value,
        implementation="Require at least two factors: something you know (password), something you have (token), something you are (biometric)",
        rationale="Significantly reduces risk of unauthorized access even if password is compromised",
        examples=[
            "SMS-based OTP",
            "Authenticator app (TOTP)",
            "Hardware security keys",
            "Biometric authentication"
        ],
        related_practices=["strong_passwords", "single_sign_on"],
        compliance_requirements=["NIST 800-63B", "PCI DSS 8.3"],
        tools=["MFA providers", "Authenticator apps", "Hardware tokens"]
    ),
    "encryption_at_rest": SecurityBestPractice(
        name="Encryption at Rest",
        description="Encrypt sensitive data when stored on disk or in databases",
        category=PracticeCategory.DATA_PROTECTION.value,
        priority=PracticePriority.CRITICAL.value,
        implementation="Use encryption for stored data, manage encryption keys securely, use strong algorithms (AES-256)",
        rationale="Protects data even if storage is compromised or stolen",
        examples=[
            "Database transparent encryption",
            "File system encryption",
            "Cloud storage encryption",
            "Backup encryption"
        ],
        related_practices=["encryption_in_transit", "key_management"],
        compliance_requirements=["PCI DSS 3.4", "HIPAA", "GDPR"],
        tools=["Database encryption", "File system encryption", "Cloud encryption services"]
    ),
    "encryption_in_transit": SecurityBestPractice(
        name="Encryption in Transit",
        description="Encrypt data during transmission over networks",
        category=PracticeCategory.DATA_PROTECTION.value,
        priority=PracticePriority.CRITICAL.value,
        implementation="Use TLS/SSL for all communications, enforce strong cipher suites (TLS 1.2+), implement certificate pinning",
        rationale="Prevents interception and man-in-the-middle attacks",
        examples=[
            "HTTPS for web traffic",
            "TLS for database connections",
            "VPN for remote access",
            "mTLS for service-to-service communication"
        ],
        related_practices=["encryption_at_rest", "certificate_management"],
        compliance_requirements=["PCI DSS 4.1", "HIPAA"],
        tools=["TLS/SSL", "VPN", "Certificate management"]
    ),
    "regular_updates": SecurityBestPractice(
        name="Regular Updates",
        description="Keep systems, applications, and dependencies updated with security patches",
        category=PracticeCategory.OPERATIONS.value,
        priority=PracticePriority.HIGH.value,
        implementation="Establish patch management process, test patches, apply critical patches promptly, maintain update schedule",
        rationale="Unpatched systems are vulnerable to known exploits",
        examples=[
            "Monthly security updates",
            "Critical patches within 48 hours",
            "Automated dependency updates",
            "Vulnerability scanning"
        ],
        related_practices=["vulnerability_management", "dependency_scanning"],
        compliance_requirements=["PCI DSS 6.2", "ISO 27001 A.12.6"],
        tools=["Patch management systems", "Vulnerability scanners", "Dependency checkers"]
    ),
    "input_validation": SecurityBestPractice(
        name="Input Validation",
        description="Validate and sanitize all user input to prevent injection attacks",
        category=PracticeCategory.CODING.value,
        priority=PracticePriority.CRITICAL.value,
        implementation="Validate input type, length, format, and content; sanitize before processing; use parameterized queries",
        rationale="Prevents injection attacks (SQL, XSS, command injection) and data corruption",
        examples=[
            "Input type validation",
            "Length restrictions",
            "Whitelist validation",
            "Parameterized queries",
            "Output encoding"
        ],
        related_practices=["output_encoding", "secure_coding"],
        compliance_requirements=["OWASP Top 10 A03", "PCI DSS 6.5"],
        tools=["Input validation libraries", "Static analysis tools", "WAF"]
    ),
    "least_privilege_access": SecurityBestPractice(
        name="Least Privilege Access",
        description="Grant users and processes minimum necessary permissions",
        category=PracticeCategory.AUTHORIZATION.value,
        priority=PracticePriority.CRITICAL.value,
        implementation="Review permissions regularly, grant minimum required access, use role-based access control (RBAC)",
        rationale="Limits damage from compromised accounts and reduces attack surface",
        examples=[
            "Role-based access control",
            "Regular access reviews",
            "Just-in-time access",
            "Privileged access management"
        ],
        related_practices=["separation_of_duties", "access_reviews"],
        compliance_requirements=["ISO 27001 A.9.2", "NIST CSF PR.AC-4"],
        tools=["IAM systems", "PAM solutions", "Access review tools"]
    ),
    "secure_coding": SecurityBestPractice(
        name="Secure Coding",
        description="Follow secure coding practices and standards",
        category=PracticeCategory.CODING.value,
        priority=PracticePriority.HIGH.value,
        implementation="Use secure coding guidelines, conduct code reviews, use static analysis, follow OWASP guidelines",
        rationale="Prevents security vulnerabilities at the source",
        examples=[
            "OWASP Secure Coding Practices",
            "Code review processes",
            "Static analysis tools",
            "Security training for developers"
        ],
        related_practices=["input_validation", "code_review", "security_testing"],
        compliance_requirements=["OWASP Top 10", "PCI DSS 6.5"],
        tools=["Static analysis tools", "Code review tools", "Security linters"]
    ),
    "security_monitoring": SecurityBestPractice(
        name="Security Monitoring",
        description="Continuously monitor systems for security events and anomalies",
        category=PracticeCategory.OPERATIONS.value,
        priority=PracticePriority.HIGH.value,
        implementation="Implement SIEM, log aggregation, real-time alerting, security event correlation",
        rationale="Enables early detection of security incidents and threats",
        examples=[
            "SIEM implementation",
            "Log aggregation",
            "Real-time alerting",
            "Security event correlation",
            "Threat intelligence integration"
        ],
        related_practices=["incident_response", "audit_logging"],
        compliance_requirements=["ISO 27001 A.12.4", "PCI DSS 10"],
        tools=["SIEM", "Log management", "Security analytics"]
    ),
    "incident_response": SecurityBestPractice(
        name="Incident Response",
        description="Establish and maintain incident response procedures",
        category=PracticeCategory.INCIDENT_RESPONSE.value,
        priority=PracticePriority.HIGH.value,
        implementation="Develop incident response plan, establish response team, conduct drills, maintain playbooks",
        rationale="Enables rapid and effective response to security incidents",
        examples=[
            "Incident response plan",
            "Response team roles",
            "Incident playbooks",
            "Regular drills and exercises",
            "Post-incident reviews"
        ],
        related_practices=["security_monitoring", "backup_recovery"],
        compliance_requirements=["ISO 27001 A.16", "NIST CSF RS"],
        tools=["Incident management systems", "Forensic tools", "Communication tools"]
    ),
    "backup_recovery": SecurityBestPractice(
        name="Backup and Recovery",
        description="Maintain regular backups and test recovery procedures",
        category=PracticeCategory.OPERATIONS.value,
        priority=PracticePriority.HIGH.value,
        implementation="Regular automated backups, off-site storage, encryption, regular recovery testing",
        rationale="Enables recovery from data loss, ransomware, and disasters",
        examples=[
            "Daily automated backups",
            "Off-site backup storage",
            "Encrypted backups",
            "Regular recovery testing",
            "Backup retention policies"
        ],
        related_practices=["disaster_recovery", "encryption_at_rest"],
        compliance_requirements=["ISO 27001 A.12.3", "PCI DSS 12.10"],
        tools=["Backup systems", "Recovery tools", "Backup verification"]
    ),
    "vulnerability_management": SecurityBestPractice(
        name="Vulnerability Management",
        description="Regularly scan for and remediate security vulnerabilities",
        category=PracticeCategory.OPERATIONS.value,
        priority=PracticePriority.HIGH.value,
        implementation="Regular vulnerability scanning, prioritization, remediation tracking, patch management",
        rationale="Identifies and addresses security weaknesses before exploitation",
        examples=[
            "Weekly vulnerability scans",
            "Automated scanning",
            "Risk-based prioritization",
            "Remediation tracking",
            "Vulnerability reporting"
        ],
        related_practices=["regular_updates", "security_testing"],
        compliance_requirements=["ISO 27001 A.12.6", "PCI DSS 11.2"],
        tools=["Vulnerability scanners", "Patch management", "Vulnerability databases"]
    ),
    "secure_configuration": SecurityBestPractice(
        name="Secure Configuration",
        description="Configure systems securely and maintain secure configurations",
        category=PracticeCategory.CONFIGURATION.value,
        priority=PracticePriority.HIGH.value,
        implementation="Use secure defaults, disable unnecessary services, harden configurations, regular configuration reviews",
        rationale="Prevents misconfigurations that create security vulnerabilities",
        examples=[
            "Secure default configurations",
            "Configuration hardening guides",
            "Regular configuration audits",
            "Change management",
            "Configuration baselines"
        ],
        related_practices=["secure_by_default", "configuration_management"],
        compliance_requirements=["ISO 27001 A.12.1", "CIS Controls"],
        tools=["Configuration management", "Hardening guides", "Compliance scanners"]
    ),
    "access_reviews": SecurityBestPractice(
        name="Access Reviews",
        description="Regularly review and audit user access permissions",
        category=PracticeCategory.AUTHORIZATION.value,
        priority=PracticePriority.MEDIUM.value,
        implementation="Quarterly access reviews, automated access certification, remove unused accounts",
        rationale="Ensures access permissions remain appropriate and removes unnecessary access",
        examples=[
            "Quarterly access reviews",
            "Automated access certification",
            "Privileged access reviews",
            "Account cleanup processes"
        ],
        related_practices=["least_privilege_access", "separation_of_duties"],
        compliance_requirements=["ISO 27001 A.9.2", "SOX"],
        tools=["Access review tools", "IAM systems", "Certification platforms"]
    ),
    "secure_development_lifecycle": SecurityBestPractice(
        name="Secure Development Lifecycle",
        description="Integrate security throughout the software development lifecycle",
        category=PracticeCategory.CODING.value,
        priority=PracticePriority.HIGH.value,
        implementation="Security requirements, threat modeling, secure coding, security testing, security reviews",
        rationale="Prevents security vulnerabilities and reduces cost of remediation",
        examples=[
            "Security requirements analysis",
            "Threat modeling",
            "Secure coding practices",
            "Security testing",
            "Security code reviews"
        ],
        related_practices=["secure_coding", "security_testing", "threat_modeling"],
        compliance_requirements=["OWASP SAMM", "BSIMM"],
        tools=["SDLC tools", "Security testing tools", "Threat modeling tools"]
    ),
}


def get_best_practices(category: Optional[str] = None) -> List[SecurityBestPractice]:
    """
    Get security best practices, optionally filtered by category.
    
    Args:
        category: Optional category filter (authentication, data_protection, operations, coding)
        
    Returns:
        List of security best practices
    """
    practices = list(BEST_PRACTICES.values())
    if category:
        practices = [p for p in practices if p.category == category]
    return practices


def get_practice(practice_name: str) -> Optional[SecurityBestPractice]:
    """Get a specific security best practice by name."""
    return BEST_PRACTICES.get(practice_name)


def get_practices_by_priority(priority: str) -> List[SecurityBestPractice]:
    """Get security best practices filtered by priority."""
    return [p for p in BEST_PRACTICES.values() if p.priority == priority]


def check_compliance_with_practices(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Check compliance with security best practices.
    
    Args:
        context: Context dictionary with system information and compliance data
        
    Returns:
        Compliance check results with pass/fail status and recommendations
    """
    total_practices = len(BEST_PRACTICES)
    compliance_checks = []
    compliant_count = 0
    non_compliant_count = 0
    not_applicable_count = 0
    
    # Check each practice
    for practice_name, practice in BEST_PRACTICES.items():
        check_result = {
            "practice": practice_name,
            "practice_name": practice.name,
            "category": practice.category,
            "priority": practice.priority,
            "status": "unknown",  # Would be determined by actual checks
            "recommendations": []
        }
        
        # Basic compliance logic based on practice type
        if practice.category == PracticeCategory.AUTHENTICATION.value:
            if "authentication" in str(context).lower():
                check_result["status"] = "compliant"
                compliant_count += 1
            else:
                check_result["status"] = "non_compliant"
                check_result["recommendations"].append(f"Implement {practice.name}")
                non_compliant_count += 1
        
        elif practice.category == PracticeCategory.DATA_PROTECTION.value:
            if "encryption" in str(context).lower():
                check_result["status"] = "compliant"
                compliant_count += 1
            else:
                check_result["status"] = "non_compliant"
                check_result["recommendations"].append(f"Implement {practice.name}")
                non_compliant_count += 1
        
        else:
            check_result["status"] = "not_applicable"
            not_applicable_count += 1
        
        compliance_checks.append(check_result)
    
    # Calculate compliance percentage
    applicable_practices = total_practices - not_applicable_count
    compliance_percentage = (compliant_count / applicable_practices * 100) if applicable_practices > 0 else 0
    
    # Generate recommendations for non-compliant practices
    recommendations = []
    for check in compliance_checks:
        if check["status"] == "non_compliant" and check["priority"] in ["high", "critical"]:
            recommendations.extend(check["recommendations"])
    
    return {
        "total_practices": total_practices,
        "applicable_practices": applicable_practices,
        "compliant": compliant_count,
        "non_compliant": non_compliant_count,
        "not_applicable": not_applicable_count,
        "compliance_percentage": round(compliance_percentage, 2),
        "compliance_checks": compliance_checks,
        "recommendations": list(set(recommendations)),  # Remove duplicates
        "critical_recommendations": [
            r for r in recommendations
            if any(c["priority"] == "critical" and r in c["recommendations"]
                   for c in compliance_checks)
        ]
    }


def get_practices_for_category(category: str) -> List[SecurityBestPractice]:
    """
    Get all best practices for a specific category.
    
    Args:
        category: Practice category
        
    Returns:
        List of practices in the category
    """
    return [p for p in BEST_PRACTICES.values() if p.category == category]


def prioritize_practices(practices: List[SecurityBestPractice]) -> List[SecurityBestPractice]:
    """
    Prioritize practices by priority level.
    
    Args:
        practices: List of practices
        
    Returns:
        Sorted list (critical first)
    """
    priority_order = {
        PracticePriority.CRITICAL.value: 4,
        PracticePriority.HIGH.value: 3,
        PracticePriority.MEDIUM.value: 2,
        PracticePriority.LOW.value: 1
    }
    
    return sorted(
        practices,
        key=lambda p: priority_order.get(p.priority, 0),
        reverse=True
    )
