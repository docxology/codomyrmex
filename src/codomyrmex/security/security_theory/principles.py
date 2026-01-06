"""Security principles and fundamentals."""

from dataclasses import dataclass
from typing import List

from codomyrmex.logging_monitoring.logger_config import get_logger

logger = get_logger(__name__)


@dataclass
class SecurityPrinciple:
    """Represents a security principle."""
    
    name: str
    description: str
    category: str  # confidentiality, integrity, availability, etc.
    examples: List[str]


# Common security principles
PRINCIPLES = {
    "defense_in_depth": SecurityPrinciple(
        name="Defense in Depth",
        description="Multiple layers of security controls",
        category="architecture",
        examples=["Network firewalls", "Application security", "Data encryption"],
    ),
    "least_privilege": SecurityPrinciple(
        name="Least Privilege",
        description="Grant minimum necessary permissions",
        category="access_control",
        examples=["User permissions", "Service accounts", "API access"],
    ),
    "separation_of_duties": SecurityPrinciple(
        name="Separation of Duties",
        description="Divide responsibilities to prevent conflicts",
        category="governance",
        examples=["Development and deployment", "Approval processes"],
    ),
    "fail_secure": SecurityPrinciple(
        name="Fail Secure",
        description="System should fail in a secure state",
        category="design",
        examples=["Access denied on error", "Encryption on failure"],
    ),
    "secure_by_default": SecurityPrinciple(
        name="Secure by Default",
        description="Default configuration should be secure",
        category="configuration",
        examples=["Disabled features", "Strong passwords", "Encryption enabled"],
    ),
}


def get_security_principles() -> List[SecurityPrinciple]:
    """Get all security principles."""
    return list(PRINCIPLES.values())


def apply_principle(principle_name: str, context: dict) -> dict:
    """Apply a security principle to a context."""
    principle = PRINCIPLES.get(principle_name)
    if not principle:
        logger.warning(f"Unknown principle: {principle_name}")
        return {"applied": False, "error": "Unknown principle"}
    
    # Placeholder for actual application logic
    return {
        "applied": True,
        "principle": principle_name,
        "context": context,
    }


