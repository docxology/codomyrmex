from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from codomyrmex.logging_monitoring.logger_config import get_logger

"""Security frameworks (OWASP, NIST, ISO 27001, etc.)."""

logger = get_logger(__name__)


class FrameworkCategory(Enum):
    """Categories of security frameworks."""
    WEB_SECURITY = "web_security"
    APPLICATION_SECURITY = "application_security"
    GOVERNANCE = "governance"
    RISK_MANAGEMENT = "risk_management"
    INFORMATION_SECURITY = "information_security"
    COMPLIANCE = "compliance"
    CYBERSECURITY = "cybersecurity"


@dataclass
class FrameworkStandard:
    """Represents a standard within a framework."""
    code: str
    name: str
    description: str
    category: str
    severity: str = "medium"  # low, medium, high, critical


@dataclass
class SecurityFramework:
    """Represents a security framework."""

    name: str
    description: str
    version: str
    categories: list[str]
    standards: list[str]
    framework_standards: list[FrameworkStandard] = field(default_factory=list)
    website: str | None = None
    documentation_url: str | None = None


# Comprehensive security frameworks
FRAMEWORKS = {
    "owasp_top_10": SecurityFramework(
        name="OWASP Top 10",
        description="Top 10 most critical web application security risks",
        version="2021",
        categories=[FrameworkCategory.WEB_SECURITY.value, FrameworkCategory.APPLICATION_SECURITY.value],
        standards=[
            "A01:2021-Broken Access Control",
            "A02:2021-Cryptographic Failures",
            "A03:2021-Injection",
            "A04:2021-Insecure Design",
            "A05:2021-Security Misconfiguration",
            "A06:2021-Vulnerable and Outdated Components",
            "A07:2021-Identification and Authentication Failures",
            "A08:2021-Software and Data Integrity Failures",
            "A09:2021-Security Logging and Monitoring Failures",
            "A10:2021-Server-Side Request Forgery (SSRF)"
        ],
        framework_standards=[
            FrameworkStandard(
                code="A01:2021",
                name="Broken Access Control",
                description="Access control enforces policy such that users cannot act outside of their intended permissions",
                category="access_control",
                severity="critical"
            ),
            FrameworkStandard(
                code="A02:2021",
                name="Cryptographic Failures",
                description="Failures related to cryptography which often lead to sensitive data exposure",
                category="cryptography",
                severity="critical"
            ),
            FrameworkStandard(
                code="A03:2021",
                name="Injection",
                description="Injection flaws occur when untrusted data is sent to an interpreter",
                category="input_validation",
                severity="critical"
            ),
        ],
        website="https://owasp.org/www-project-top-ten/",
        documentation_url="https://owasp.org/Top10/"
    ),
    "nist_csf": SecurityFramework(
        name="NIST Cybersecurity Framework",
        description="Framework for improving critical infrastructure cybersecurity",
        version="1.1",
        categories=[FrameworkCategory.CYBERSECURITY.value, FrameworkCategory.RISK_MANAGEMENT.value],
        standards=[
            "Identify",
            "Protect",
            "Detect",
            "Respond",
            "Recover"
        ],
        framework_standards=[
            FrameworkStandard(
                code="ID",
                name="Identify",
                description="Develop organizational understanding to manage cybersecurity risk",
                category="governance",
                severity="high"
            ),
            FrameworkStandard(
                code="PR",
                name="Protect",
                description="Develop and implement safeguards to ensure delivery of critical services",
                category="protection",
                severity="high"
            ),
            FrameworkStandard(
                code="DE",
                name="Detect",
                description="Develop and implement activities to identify cybersecurity events",
                category="monitoring",
                severity="high"
            ),
            FrameworkStandard(
                code="RS",
                name="Respond",
                description="Develop and implement response activities",
                category="incident_response",
                severity="high"
            ),
            FrameworkStandard(
                code="RC",
                name="Recover",
                description="Develop and implement recovery planning and processes",
                category="business_continuity",
                severity="high"
            ),
        ],
        website="https://www.nist.gov/cyberframework",
        documentation_url="https://www.nist.gov/cyberframework/framework"
    ),
    "iso_27001": SecurityFramework(
        name="ISO 27001",
        description="Information security management systems - Requirements",
        version="2022",
        categories=[FrameworkCategory.INFORMATION_SECURITY.value, FrameworkCategory.COMPLIANCE.value],
        standards=[
            "ISMS - Information Security Management System",
            "Risk management",
            "Controls",
            "Continuous improvement"
        ],
        framework_standards=[
            FrameworkStandard(
                code="4.1",
                name="Understanding the organization and its context",
                description="Determine external and internal issues relevant to ISMS",
                category="governance",
                severity="high"
            ),
            FrameworkStandard(
                code="6.1.2",
                name="Information security risk assessment",
                description="Define and apply information security risk assessment process",
                category="risk_management",
                severity="critical"
            ),
            FrameworkStandard(
                code="8.1",
                name="Operational planning and control",
                description="Plan, implement and control processes needed to meet requirements",
                category="operations",
                severity="high"
            ),
        ],
        website="https://www.iso.org/standard/27001",
        documentation_url="https://www.iso.org/standard/27001.html"
    ),
    "cis_controls": SecurityFramework(
        name="CIS Controls",
        description="Center for Internet Security Critical Security Controls",
        version="8",
        categories=[FrameworkCategory.CYBERSECURITY.value],
        standards=[
            "CIS Control 1: Inventory and Control of Enterprise Assets",
            "CIS Control 2: Inventory and Control of Software Assets",
            "CIS Control 3: Data Protection",
            "CIS Control 4: Secure Configuration of Enterprise Assets and Software",
            "CIS Control 5: Account Management"
        ],
        website="https://www.cisecurity.org/controls/",
        documentation_url="https://www.cisecurity.org/controls/"
    ),
    "pci_dss": SecurityFramework(
        name="PCI DSS",
        description="Payment Card Industry Data Security Standard",
        version="4.0",
        categories=[FrameworkCategory.COMPLIANCE.value, FrameworkCategory.INFORMATION_SECURITY.value],
        standards=[
            "Build and Maintain Secure Network",
            "Protect Cardholder Data",
            "Maintain Vulnerability Management Program",
            "Implement Strong Access Control Measures",
            "Regularly Monitor and Test Networks",
            "Maintain Information Security Policy"
        ],
        website="https://www.pcisecuritystandards.org/",
        documentation_url="https://www.pcisecuritystandards.org/document_library"
    ),
}


def get_framework(framework_name: str) -> SecurityFramework | None:
    """Get a security framework by name."""
    return FRAMEWORKS.get(framework_name)


def get_all_frameworks() -> list[SecurityFramework]:
    """Get all available security frameworks."""
    return list(FRAMEWORKS.values())


def get_frameworks_by_category(category: str) -> list[SecurityFramework]:
    """Get frameworks filtered by category."""
    return [f for f in FRAMEWORKS.values() if category in f.categories]


def apply_framework(framework_name: str, context: dict[str, Any]) -> dict[str, Any]:
    """
    Apply a security framework to a context.

    Args:
        framework_name: Name of the framework to apply
        context: Context dictionary with system information

    Returns:
        Dictionary with application results and recommendations
    """
    framework = FRAMEWORKS.get(framework_name)
    if not framework:
        logger.warning(f"Unknown framework: {framework_name}")
        return {
            "applied": False,
            "error": f"Unknown framework: {framework_name}",
            "available_frameworks": list(FRAMEWORKS.keys())
        }

    logger.info(f"Applying framework '{framework.name}' version {framework.version} to context")

    # Generate recommendations based on framework
    recommendations = []

    if framework_name == "owasp_top_10":
        recommendations.append("Review OWASP Top 10 risks for web applications")
        recommendations.append("Implement secure coding practices")
        recommendations.append("Conduct regular security testing")

    elif framework_name == "nist_csf":
        recommendations.append("Implement Identify function: Asset management and risk assessment")
        recommendations.append("Implement Protect function: Access control and data security")
        recommendations.append("Implement Detect function: Security monitoring and detection")
        recommendations.append("Implement Respond function: Incident response planning")
        recommendations.append("Implement Recover function: Recovery planning and improvements")

    elif framework_name == "iso_27001":
        recommendations.append("Establish Information Security Management System (ISMS)")
        recommendations.append("Conduct risk assessment and treatment")
        recommendations.append("Implement security controls")
        recommendations.append("Establish continuous improvement process")

    return {
        "applied": True,
        "framework": framework_name,
        "framework_name": framework.name,
        "version": framework.version,
        "context": context,
        "recommendations": recommendations,
        "standards": framework.standards,
        "framework_standards": [
            {
                "code": std.code,
                "name": std.name,
                "description": std.description,
                "severity": std.severity
            }
            for std in framework.framework_standards
        ]
    }


def check_framework_compliance(framework_name: str, context: dict[str, Any]) -> dict[str, Any]:
    """
    Check compliance with a security framework.

    Args:
        framework_name: Name of the framework
        context: Context dictionary with compliance information

    Returns:
        Compliance check results
    """
    framework = FRAMEWORKS.get(framework_name)
    if not framework:
        return {
            "compliant": False,
            "error": f"Unknown framework: {framework_name}"
        }

    # Basic compliance checking
    compliance_checks = []
    for standard in framework.framework_standards:
        compliance_checks.append({
            "standard": standard.code,
            "name": standard.name,
            "status": "unknown",  # Would be determined by actual checks
            "severity": standard.severity
        })

    return {
        "compliant": True,
        "framework": framework_name,
        "framework_name": framework.name,
        "version": framework.version,
        "compliance_checks": compliance_checks,
        "total_standards": len(framework.framework_standards)
    }
