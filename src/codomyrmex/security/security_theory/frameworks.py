"""Security frameworks (OWASP, NIST, etc.)."""

from dataclasses import dataclass
from typing import List, Optional

from codomyrmex.logging_monitoring.logger_config import get_logger

logger = get_logger(__name__)


@dataclass
class SecurityFramework:
    """Represents a security framework."""
    
    name: str
    description: str
    version: str
    categories: List[str]
    standards: List[str]


# Common security frameworks
FRAMEWORKS = {
    "owasp_top_10": SecurityFramework(
        name="OWASP Top 10",
        description="Top 10 web application security risks",
        version="2021",
        categories=["web_security", "application_security"],
        standards=["A01:2021-Broken Access Control", "A02:2021-Cryptographic Failures"],
    ),
    "nist_csf": SecurityFramework(
        name="NIST Cybersecurity Framework",
        description="Framework for improving cybersecurity",
        version="1.1",
        categories=["governance", "risk_management"],
        standards=["Identify", "Protect", "Detect", "Respond", "Recover"],
    ),
    "iso_27001": SecurityFramework(
        name="ISO 27001",
        description="Information security management",
        version="2022",
        categories=["information_security", "compliance"],
        standards=["ISMS", "Risk management", "Controls"],
    ),
}


def get_framework(framework_name: str) -> Optional[SecurityFramework]:
    """Get a security framework by name."""
    return FRAMEWORKS.get(framework_name)


def apply_framework(framework_name: str, context: dict) -> dict:
    """Apply a security framework to a context."""
    framework = get_framework(framework_name)
    if not framework:
        logger.warning(f"Unknown framework: {framework_name}")
        return {"applied": False, "error": "Unknown framework"}
    
    # Placeholder for actual application logic
    return {
        "applied": True,
        "framework": framework_name,
        "context": context,
    }


