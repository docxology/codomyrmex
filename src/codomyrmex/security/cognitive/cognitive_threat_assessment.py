from dataclasses import dataclass

from codomyrmex.logging_monitoring.logger_config import get_logger

"""Cognitive threat assessment."""

logger = get_logger(__name__)


@dataclass
class CognitiveThreat:
    """Represents a cognitive security threat."""

    threat_id: str
    threat_type: str
    severity: str  # low, medium, high, critical
    description: str
    human_factors: list[str]
    mitigation: str


class CognitiveThreatAssessor:
    """Assesses cognitive security threats."""

    def __init__(self):

        logger.info("CognitiveThreatAssessor initialized")

    def assess_threats(self, context: dict) -> list[CognitiveThreat]:
        """Assess cognitive threats in a given context."""
        threats = []
        threat_counter = 1

        # Check training level
        training_level = context.get("training_level", "").lower()
        if training_level in ("none", "low"):
            threats.append(CognitiveThreat(
                threat_id=f"CT-{threat_counter:03d}",
                threat_type="untrained_personnel",
                severity="high",
                description="Personnel with insufficient security awareness training are highly susceptible to social engineering attacks",
                human_factors=["lack_of_awareness", "susceptibility_to_manipulation", "poor_judgment"],
                mitigation="Implement mandatory security awareness training program with regular refresher courses",
            ))
            threat_counter += 1

        # Check access level
        access_level = context.get("access_level", "").lower()
        if access_level in ("admin", "privileged"):
            threats.append(CognitiveThreat(
                threat_id=f"CT-{threat_counter:03d}",
                threat_type="high_privilege_target",
                severity="critical",
                description="Users with elevated privileges are high-value targets for social engineering and credential theft",
                human_factors=["high_value_target", "authority_abuse_risk", "credential_exposure"],
                mitigation="Enforce principle of least privilege, require multi-factor authentication, and implement privileged access monitoring",
            ))
            threat_counter += 1

        # Check environment
        environment = context.get("environment", "").lower()
        if environment in ("remote", "public_wifi"):
            threats.append(CognitiveThreat(
                threat_id=f"CT-{threat_counter:03d}",
                threat_type="insecure_environment",
                severity="high",
                description="Working from insecure environments increases risk of shoulder surfing, eavesdropping, and network-based attacks",
                human_factors=["environmental_exposure", "reduced_vigilance", "network_vulnerability"],
                mitigation="Require VPN usage, enforce screen privacy filters, and provide secure remote work guidelines",
            ))
            threat_counter += 1

        # Check recent incidents
        recent_incidents = context.get("recent_incidents", [])
        if recent_incidents:
            threats.append(CognitiveThreat(
                threat_id=f"CT-{threat_counter:03d}",
                threat_type="elevated_risk_period",
                severity="high",
                description=f"Recent security incidents ({len(recent_incidents)} recorded) indicate an elevated threat environment",
                human_factors=["alert_fatigue", "complacency", "stress_response"],
                mitigation="Heighten monitoring, issue targeted security advisories, and conduct incident-specific awareness briefings",
            ))
            threat_counter += 1

        # Check social media exposure
        social_media_exposure = context.get("social_media_exposure", "").lower()
        if social_media_exposure == "high":
            threats.append(CognitiveThreat(
                threat_id=f"CT-{threat_counter:03d}",
                threat_type="osint_risk",
                severity="medium",
                description="High social media exposure provides attackers with personal information for targeted social engineering (spear phishing, pretexting)",
                human_factors=["information_leakage", "digital_footprint", "personal_data_exposure"],
                mitigation="Conduct OSINT assessments, educate on social media privacy settings, and limit publicly shared organizational information",
            ))
            threat_counter += 1

        logger.debug("Assessed cognitive threats")
        return threats

    def assess_cognitive_threats(self, context: dict) -> dict:
        """Comprehensive cognitive threat assessment."""
        threats = self.assess_threats(context)

        assessment = {
            "total_threats": len(threats),
            "critical_count": sum(1 for t in threats if t.severity == "critical"),
            "high_count": sum(1 for t in threats if t.severity == "high"),
            "threats": threats,
        }

        return assessment

    def evaluate_human_factors(self, scenario: dict) -> dict:
        """Evaluate human factors in security scenarios."""
        factors = {
            "training_level": scenario.get("training_level", "unknown"),
            "experience": scenario.get("experience", "unknown"),
            "stress_level": scenario.get("stress_level", "unknown"),
            "risk_tolerance": scenario.get("risk_tolerance", "unknown"),
        }

        # Calculate risk score
        risk_score = 0.0
        if factors["training_level"] in ("none", "low"):
            risk_score += 0.3
        if factors["stress_level"] in ("high", "very_high"):
            risk_score += 0.2
        if factors["risk_tolerance"] in ("high", "very_high"):
            risk_score += 0.2
        access_level = scenario.get("access_level", "").lower()
        if access_level in ("admin", "privileged"):
            risk_score += 0.15

        risk_score = min(risk_score, 1.0)

        # Generate recommendations
        recommendations = []
        if factors["training_level"] in ("none", "low"):
            recommendations.append("Enroll in mandatory security awareness training")
        if factors["stress_level"] in ("high", "very_high"):
            recommendations.append("Implement workload management to reduce stress-induced errors")
        if factors["risk_tolerance"] in ("high", "very_high"):
            recommendations.append("Provide targeted training on risk assessment and cautious behavior")
        if access_level in ("admin", "privileged"):
            recommendations.append("Apply additional verification steps for privileged operations")
        if not recommendations:
            recommendations.append("Continue regular security awareness refreshers")

        factors["risk_score"] = risk_score
        factors["recommendations"] = recommendations

        return factors


def assess_cognitive_threats(
    context: dict,
    assessor: CognitiveThreatAssessor | None = None,
) -> dict:
    """Assess cognitive threats."""
    if assessor is None:
        assessor = CognitiveThreatAssessor()
    return assessor.assess_cognitive_threats(context)


def evaluate_human_factors(
    scenario: dict,
    assessor: CognitiveThreatAssessor | None = None,
) -> dict:
    """Evaluate human factors."""
    if assessor is None:
        assessor = CognitiveThreatAssessor()
    return assessor.evaluate_human_factors(scenario)


