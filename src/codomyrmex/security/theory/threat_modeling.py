"""Threat modeling methodologies."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from codomyrmex.logging_monitoring.logger_config import get_logger

logger = get_logger(__name__)


class ThreatSeverity(Enum):
    """Threat severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ThreatCategory(Enum):
    """Categories of threats."""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATA_EXPOSURE = "data_exposure"
    INJECTION = "injection"
    CONFIGURATION = "configuration"
    CRYPTOGRAPHY = "cryptography"
    LOGGING = "logging"
    NETWORK = "network"
    PHYSICAL = "physical"
    SOCIAL_ENGINEERING = "social_engineering"


@dataclass
class Threat:
    """Represents a security threat."""

    threat_id: str
    threat_type: str
    description: str
    severity: str  # low, medium, high, critical
    mitigation: str
    category: str = "general"
    likelihood: str = "medium"  # low, medium, high
    impact: str = "medium"  # low, medium, high, critical
    affected_assets: list[str] = field(default_factory=list)
    attack_vectors: list[str] = field(default_factory=list)
    detection_methods: list[str] = field(default_factory=list)
    references: list[str] = field(default_factory=list)


@dataclass
class ThreatModel:
    """Represents a threat model."""

    model_id: str
    system_name: str
    threats: list[Threat]
    assets: list[str]
    attack_surface: list[str]
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    methodology: str = "STRIDE"  # STRIDE, DREAD, PASTA, etc.
    assumptions: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)


class ThreatModelBuilder:
    """Builds threat models using various methodologies."""

    def __init__(self, methodology: str = "STRIDE"):
        """
        Initialize threat model builder.

        Args:
            methodology: Threat modeling methodology (STRIDE, DREAD, PASTA, etc.)
        """
        self.methodology = methodology
        logger.info(f"ThreatModelBuilder initialized with {methodology} methodology")

    def create_model(
        self,
        system_name: str,
        assets: list[str],
        attack_surface: list[str],
        assumptions: list[str] | None = None,
        constraints: list[str] | None = None,
    ) -> ThreatModel:
        """
        Create a threat model for a system.

        Args:
            system_name: Name of the system to model
            assets: List of assets to protect
            attack_surface: List of attack surface elements
            assumptions: Optional list of assumptions
            constraints: Optional list of constraints

        Returns:
            ThreatModel object with identified threats
        """
        if assumptions is None:
            assumptions = []
        if constraints is None:
            constraints = []

        threats = self._identify_threats(assets, attack_surface)

        model = ThreatModel(
            model_id=f"model_{uuid.uuid4().hex[:8]}",
            system_name=system_name,
            threats=threats,
            assets=assets,
            attack_surface=attack_surface,
            methodology=self.methodology,
            assumptions=assumptions,
            constraints=constraints,
        )

        logger.info(f"Created threat model for {system_name} with {len(threats)} threats")
        return model

    def _identify_threats(self, assets: list[str], attack_surface: list[str]) -> list[Threat]:
        """
        Identify threats based on assets and attack surface.

        Uses STRIDE methodology by default:
        - Spoofing
        - Tampering
        - Repudiation
        - Information Disclosure
        - Denial of Service
        - Elevation of Privilege
        """
        threats = []

        if self.methodology == "STRIDE":
            threats.extend(self._identify_stride_threats(assets, attack_surface))
        else:
            # Generic threat identification
            threats.extend(self._identify_generic_threats(assets, attack_surface))

        return threats

    def _identify_stride_threats(self, assets: list[str], attack_surface: list[str]) -> list[Threat]:
        """Identify threats using STRIDE methodology."""
        threats = []

        # Spoofing threats
        if any("authentication" in surface.lower() or "login" in surface.lower() for surface in attack_surface):
            threats.append(Threat(
                threat_id=f"threat_{uuid.uuid4().hex[:8]}",
                threat_type="Spoofing",
                description="Unauthorized user may spoof identity to gain access",
                severity=ThreatSeverity.HIGH.value,
                mitigation="Implement strong authentication mechanisms (MFA, certificates)",
                category=ThreatCategory.AUTHENTICATION.value,
                likelihood="medium",
                impact="high",
                affected_assets=[a for a in assets if "user" in a.lower() or "account" in a.lower()],
                attack_vectors=["Credential theft", "Session hijacking", "Identity impersonation"],
                detection_methods=["Authentication logs", "Failed login monitoring", "Anomaly detection"]
            ))

        # Tampering threats
        if any("data" in asset.lower() or "storage" in asset.lower() for asset in assets):
            threats.append(Threat(
                threat_id=f"threat_{uuid.uuid4().hex[:8]}",
                threat_type="Tampering",
                description="Data may be modified by unauthorized parties",
                severity=ThreatSeverity.HIGH.value,
                mitigation="Implement data integrity controls (checksums, digital signatures, access controls)",
                category=ThreatCategory.DATA_EXPOSURE.value,
                likelihood="medium",
                impact="high",
                affected_assets=[a for a in assets if "data" in a.lower()],
                attack_vectors=["Unauthorized access", "Man-in-the-middle", "Malicious insiders"],
                detection_methods=["Integrity checks", "Change monitoring", "Audit logs"]
            ))

        # Repudiation threats
        threats.append(Threat(
            threat_id=f"threat_{uuid.uuid4().hex[:8]}",
            threat_type="Repudiation",
            description="Users may deny performing actions",
            severity=ThreatSeverity.MEDIUM.value,
            mitigation="Implement comprehensive logging and audit trails",
            category=ThreatCategory.LOGGING.value,
            likelihood="low",
            impact="medium",
            affected_assets=assets,
            attack_vectors=["Lack of logging", "Insufficient audit trails"],
            detection_methods=["Audit log review", "Transaction monitoring"]
        ))

        # Information Disclosure
        if any("sensitive" in asset.lower() or "confidential" in asset.lower() for asset in assets):
            threats.append(Threat(
                threat_id=f"threat_{uuid.uuid4().hex[:8]}",
                threat_type="Information Disclosure",
                description="Sensitive information may be exposed",
                severity=ThreatSeverity.CRITICAL.value,
                mitigation="Encrypt sensitive data at rest and in transit, implement access controls",
                category=ThreatCategory.DATA_EXPOSURE.value,
                likelihood="medium",
                impact="critical",
                affected_assets=[a for a in assets if "sensitive" in a.lower() or "confidential" in a.lower()],
                attack_vectors=["Unauthorized access", "Data breaches", "Insufficient encryption"],
                detection_methods=["Access monitoring", "Data loss prevention", "Anomaly detection"]
            ))

        # Denial of Service
        if any("service" in surface.lower() or "api" in surface.lower() for surface in attack_surface):
            threats.append(Threat(
                threat_id=f"threat_{uuid.uuid4().hex[:8]}",
                threat_type="Denial of Service",
                description="Services may be unavailable due to attacks",
                severity=ThreatSeverity.HIGH.value,
                mitigation="Implement rate limiting, resource quotas, and DDoS protection",
                category=ThreatCategory.NETWORK.value,
                likelihood="medium",
                impact="high",
                affected_assets=[a for a in assets if "service" in a.lower()],
                attack_vectors=["DDoS attacks", "Resource exhaustion", "Network flooding"],
                detection_methods=["Traffic monitoring", "Resource usage alerts", "Availability monitoring"]
            ))

        # Elevation of Privilege
        threats.append(Threat(
            threat_id=f"threat_{uuid.uuid4().hex[:8]}",
            threat_type="Elevation of Privilege",
            description="Unauthorized users may gain elevated privileges",
            severity=ThreatSeverity.CRITICAL.value,
            mitigation="Implement least privilege access controls and privilege separation",
            category=ThreatCategory.AUTHORIZATION.value,
            likelihood="low",
            impact="critical",
            affected_assets=assets,
            attack_vectors=["Privilege escalation exploits", "Configuration errors", "Insufficient access controls"],
            detection_methods=["Privilege change monitoring", "Access control audits", "Anomaly detection"]
        ))

        return threats

    def _identify_generic_threats(self, assets: list[str], attack_surface: list[str]) -> list[Threat]:
        """Identify generic threats when methodology is not STRIDE."""
        threats = []

        # Generic threat: Unauthorized access
        threats.append(Threat(
            threat_id=f"threat_{uuid.uuid4().hex[:8]}",
            threat_type="Unauthorized Access",
            description="Unauthorized parties may gain access to system resources",
            severity=ThreatSeverity.HIGH.value,
            mitigation="Implement strong authentication and authorization controls",
            category=ThreatCategory.AUTHORIZATION.value,
            likelihood="medium",
            impact="high",
            affected_assets=assets,
            attack_vectors=["Weak authentication", "Insufficient authorization"],
            detection_methods=["Access logs", "Failed authentication monitoring"]
        ))

        return threats


def create_threat_model(
    system_name: str,
    assets: list[str],
    attack_surface: list[str],
    builder: ThreatModelBuilder | None = None,
    methodology: str = "STRIDE",
) -> ThreatModel:
    """
    Create a threat model for a system.

    Args:
        system_name: Name of the system
        assets: List of system assets
        attack_surface: List of attack surface elements
        builder: Optional ThreatModelBuilder instance
        methodology: Threat modeling methodology (STRIDE, DREAD, PASTA)

    Returns:
        ThreatModel object
    """
    if builder is None:
        builder = ThreatModelBuilder(methodology=methodology)
    return builder.create_model(system_name, assets, attack_surface)


def analyze_threats(threat_model: ThreatModel) -> dict[str, Any]:
    """
    Analyze threats in a threat model.

    Args:
        threat_model: ThreatModel to analyze

    Returns:
        Analysis results with threat counts and details
    """
    total_threats = len(threat_model.threats)
    critical_count = sum(1 for t in threat_model.threats if t.severity == ThreatSeverity.CRITICAL.value)
    high_count = sum(1 for t in threat_model.threats if t.severity == ThreatSeverity.HIGH.value)
    medium_count = sum(1 for t in threat_model.threats if t.severity == ThreatSeverity.MEDIUM.value)
    low_count = sum(1 for t in threat_model.threats if t.severity == ThreatSeverity.LOW.value)

    # Group by category
    threats_by_category = {}
    for threat in threat_model.threats:
        category = threat.category
        if category not in threats_by_category:
            threats_by_category[category] = []
        threats_by_category[category].append({
            "threat_id": threat.threat_id,
            "threat_type": threat.threat_type,
            "severity": threat.severity,
            "description": threat.description
        })

    # Calculate risk scores
    risk_scores = []
    for threat in threat_model.threats:
        from .risk_assessment import calculate_risk_score
        risk_score = calculate_risk_score(threat.likelihood, threat.impact)
        risk_scores.append({
            "threat_id": threat.threat_id,
            "risk_score": risk_score,
            "severity": threat.severity
        })

    avg_risk_score = sum(r["risk_score"] for r in risk_scores) / len(risk_scores) if risk_scores else 0.0

    return {
        "total_threats": total_threats,
        "critical_count": critical_count,
        "high_count": high_count,
        "medium_count": medium_count,
        "low_count": low_count,
        "threats_by_category": threats_by_category,
        "average_risk_score": avg_risk_score,
        "risk_scores": risk_scores,
        "methodology": threat_model.methodology,
        "threats": [
            {
                "threat_id": t.threat_id,
                "threat_type": t.threat_type,
                "description": t.description,
                "severity": t.severity,
                "mitigation": t.mitigation,
                "category": t.category,
                "likelihood": t.likelihood,
                "impact": t.impact
            }
            for t in threat_model.threats
        ]
    }


def prioritize_threats(threat_model: ThreatModel) -> list[Threat]:
    """
    Prioritize threats by severity and risk.

    Args:
        threat_model: ThreatModel to prioritize

    Returns:
        List of threats sorted by priority (highest first)
    """
    from .risk_assessment import calculate_risk_score

    # Calculate risk scores for all threats
    threats_with_scores = []
    for threat in threat_model.threats:
        risk_score = calculate_risk_score(threat.likelihood, threat.impact)
        threats_with_scores.append((threat, risk_score))

    # Sort by risk score (descending), then by severity
    severity_order = {
        ThreatSeverity.CRITICAL.value: 4,
        ThreatSeverity.HIGH.value: 3,
        ThreatSeverity.MEDIUM.value: 2,
        ThreatSeverity.LOW.value: 1
    }

    threats_with_scores.sort(
        key=lambda x: (x[1], severity_order.get(x[0].severity, 0)),
        reverse=True
    )

    return [threat for threat, _ in threats_with_scores]
