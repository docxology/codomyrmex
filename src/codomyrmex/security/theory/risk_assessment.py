from datetime import datetime
from typing import List, Dict, Any, Optional

from dataclasses import dataclass, field
from enum import Enum
import uuid

from codomyrmex.logging_monitoring.logger_config import get_logger











































"""Risk assessment methodologies."""

"""Core functionality module

This module provides risk_assessment functionality including:
- 12 functions: assess_risk, calculate_risk_score, prioritize_risks...
- 6 classes: RiskLevel, LikelihoodLevel, ImpactLevel...

Usage:
    from risk_assessment import FunctionName, ClassName
    # Example usage here
"""
logger = get_logger(__name__)


class RiskLevel(Enum):
    """Risk levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class LikelihoodLevel(Enum):
    """Likelihood levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ImpactLevel(Enum):
    """Impact levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Risk:
    """Represents a security risk."""
    
    risk_id: str
    description: str
    likelihood: str  # low, medium, high
    impact: str  # low, medium, high, critical
    risk_score: float  # Calculated from likelihood and impact
    category: str = "general"
    affected_assets: List[str] = field(default_factory=list)
    threat_source: str = "unknown"
    vulnerability: str = ""
    existing_controls: List[str] = field(default_factory=list)
    recommended_controls: List[str] = field(default_factory=list)
    residual_risk: Optional[float] = None
    risk_owner: Optional[str] = None
    mitigation_priority: str = "medium"  # low, medium, high, critical


@dataclass
class RiskAssessment:
    """Results of a risk assessment."""
    
    assessment_id: str
    risks: List[Risk]
    overall_risk_level: str
    recommendations: List[str]
    created_at: datetime = field(default_factory=datetime.now)
    assessed_by: Optional[str] = None
    assessment_methodology: str = "qualitative"  # qualitative, quantitative, hybrid
    risk_matrix: Optional[Dict[str, Any]] = None
    summary: Optional[str] = None


class RiskAssessor:
    """Performs risk assessments using various methodologies."""
    
    def __init__(self, methodology: str = "qualitative"):
        """
        Initialize risk assessor.
        
        Args:
            methodology: Assessment methodology (qualitative, quantitative, hybrid)
        """
        self.methodology = methodology
        logger.info(f"RiskAssessor initialized with {methodology} methodology")
    
    def assess(self, context: Dict[str, Any]) -> RiskAssessment:
        """
        Perform a risk assessment.
        
        Args:
            context: Context dictionary with system information, threats, assets
            
        Returns:
            RiskAssessment with identified risks and recommendations
        """
        risks = self._identify_risks(context)
        
        # Calculate risk scores
        for risk in risks:
            risk.risk_score = calculate_risk_score(risk.likelihood, risk.impact)
            # Calculate residual risk if controls are present
            if risk.existing_controls:
                risk.residual_risk = self._calculate_residual_risk(risk)
        
        overall_risk = self._calculate_overall_risk(risks)
        recommendations = self._generate_recommendations(risks)
        
        # Create risk matrix
        risk_matrix = self._create_risk_matrix(risks)
        
        assessment = RiskAssessment(
            assessment_id=f"assessment_{uuid.uuid4().hex[:8]}",
            risks=risks,
            overall_risk_level=overall_risk,
            recommendations=recommendations,
            assessment_methodology=self.methodology,
            risk_matrix=risk_matrix,
            summary=self._generate_summary(risks, overall_risk)
        )
        
        logger.info(f"Completed risk assessment with {len(risks)} risks, overall level: {overall_risk}")
        return assessment
    
    def _identify_risks(self, context: Dict[str, Any]) -> List[Risk]:
        """
        Identify risks in context.
        
        Args:
            context: Context with system information
            
        Returns:
            List of identified risks
        """
        risks = []
        
        # Extract context information
        threats = context.get("threats", [])
        assets = context.get("assets", [])
        vulnerabilities = context.get("vulnerabilities", [])
        system_type = context.get("system_type", "general")
        
        # Identify risks based on common threat patterns
        if "data_breach" in str(threats).lower() or "data" in str(assets).lower():
            risks.append(Risk(
                risk_id=f"risk_{uuid.uuid4().hex[:8]}",
                description="Risk of unauthorized data access or disclosure",
                likelihood=LikelihoodLevel.MEDIUM.value,
                impact=ImpactLevel.CRITICAL.value,
                risk_score=calculate_risk_score(LikelihoodLevel.MEDIUM.value, ImpactLevel.CRITICAL.value),
                category="data_protection",
                affected_assets=[a for a in assets if "data" in str(a).lower()],
                threat_source="External attackers, malicious insiders",
                vulnerability="Insufficient access controls, weak encryption",
                existing_controls=context.get("existing_controls", []),
                recommended_controls=[
                    "Implement encryption at rest and in transit",
                    "Enforce strong access controls",
                    "Regular security audits"
                ],
                mitigation_priority="critical"
            ))
        
        if "unauthorized_access" in str(threats).lower() or "authentication" in str(context).lower():
            risks.append(Risk(
                risk_id=f"risk_{uuid.uuid4().hex[:8]}",
                description="Risk of unauthorized system access",
                likelihood=LikelihoodLevel.MEDIUM.value,
                impact=ImpactLevel.HIGH.value,
                risk_score=calculate_risk_score(LikelihoodLevel.MEDIUM.value, ImpactLevel.HIGH.value),
                category="access_control",
                affected_assets=assets,
                threat_source="External attackers, credential theft",
                vulnerability="Weak authentication, insufficient authorization",
                existing_controls=context.get("existing_controls", []),
                recommended_controls=[
                    "Implement multi-factor authentication",
                    "Enforce strong password policies",
                    "Regular access reviews"
                ],
                mitigation_priority="high"
            ))
        
        if "denial_of_service" in str(threats).lower() or "service" in str(assets).lower():
            risks.append(Risk(
                risk_id=f"risk_{uuid.uuid4().hex[:8]}",
                description="Risk of service unavailability due to attacks",
                likelihood=LikelihoodLevel.MEDIUM.value,
                impact=ImpactLevel.HIGH.value,
                risk_score=calculate_risk_score(LikelihoodLevel.MEDIUM.value, ImpactLevel.HIGH.value),
                category="availability",
                affected_assets=[a for a in assets if "service" in str(a).lower()],
                threat_source="DDoS attacks, resource exhaustion",
                vulnerability="Insufficient rate limiting, no DDoS protection",
                existing_controls=context.get("existing_controls", []),
                recommended_controls=[
                    "Implement rate limiting",
                    "DDoS protection services",
                    "Resource quotas and monitoring"
                ],
                mitigation_priority="high"
            ))
        
        # Generic risk if no specific risks identified
        if not risks:
            risks.append(Risk(
                risk_id=f"risk_{uuid.uuid4().hex[:8]}",
                description="General security risk in system",
                likelihood=LikelihoodLevel.LOW.value,
                impact=ImpactLevel.MEDIUM.value,
                risk_score=calculate_risk_score(LikelihoodLevel.LOW.value, ImpactLevel.MEDIUM.value),
                category="general",
                affected_assets=assets,
                threat_source="Various",
                vulnerability="Unknown vulnerabilities",
                existing_controls=context.get("existing_controls", []),
                recommended_controls=["Conduct security assessment", "Implement security controls"],
                mitigation_priority="medium"
            ))
        
        return risks
    
    def _calculate_residual_risk(self, risk: Risk) -> float:
        """
        Calculate residual risk after existing controls.
        
        Args:
            risk: Risk with existing controls
            
        Returns:
            Residual risk score (0.0 to 1.0)
        """
        # Simple reduction based on number of controls
        control_reduction = min(len(risk.existing_controls) * 0.1, 0.5)
        residual = max(risk.risk_score - control_reduction, 0.0)
        return residual
    
    def _calculate_overall_risk(self, risks: List[Risk]) -> str:
        """
        Calculate overall risk level from individual risks.
        
        Args:
            risks: List of risks
            
        Returns:
            Overall risk level (low, medium, high, critical)
        """
        if not risks:
            return RiskLevel.LOW.value
        
        # Use highest risk score
        max_risk_score = max(r.risk_score for r in risks)
        
        if max_risk_score > 0.75:
            return RiskLevel.CRITICAL.value
        elif max_risk_score > 0.5:
            return RiskLevel.HIGH.value
        elif max_risk_score > 0.25:
            return RiskLevel.MEDIUM.value
        else:
            return RiskLevel.LOW.value
    
    def _generate_recommendations(self, risks: List[Risk]) -> List[str]:
        """
        Generate risk mitigation recommendations.
        
        Args:
            risks: List of risks
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Prioritize by risk score
        sorted_risks = sorted(risks, key=lambda r: r.risk_score, reverse=True)
        
        for risk in sorted_risks[:5]:  # Top 5 risks
            if risk.recommended_controls:
                recommendations.extend(risk.recommended_controls)
        
        # Add general recommendations
        if any(r.risk_score > 0.7 for r in risks):
            recommendations.append("Immediate action required for high-risk items")
        
        if any(r.category == "data_protection" for r in risks):
            recommendations.append("Review data protection controls and encryption")
        
        if any(r.category == "access_control" for r in risks):
            recommendations.append("Strengthen authentication and authorization")
        
        return list(set(recommendations))  # Remove duplicates
    
    def _create_risk_matrix(self, risks: List[Risk]) -> Dict[str, Any]:
        """
        Create a risk matrix visualization data.
        
        Args:
            risks: List of risks
            
        Returns:
            Risk matrix data structure
        """
        matrix = {
            "critical": [],
            "high": [],
            "medium": [],
            "low": []
        }
        
        for risk in risks:
            level = risk.impact
            if level not in matrix:
                level = "medium"
            matrix[level].append({
                "risk_id": risk.risk_id,
                "description": risk.description,
                "likelihood": risk.likelihood,
                "impact": risk.impact,
                "risk_score": risk.risk_score
            })
        
        return matrix
    
    def _generate_summary(self, risks: List[Risk], overall_risk: str) -> str:
        """
        Generate assessment summary.
        
        Args:
            risks: List of risks
            overall_risk: Overall risk level
            
        Returns:
            Summary text
        """
        total_risks = len(risks)
        critical_count = sum(1 for r in risks if r.impact == ImpactLevel.CRITICAL.value)
        high_count = sum(1 for r in risks if r.impact == ImpactLevel.HIGH.value)
        
        summary = f"Risk assessment identified {total_risks} risks with overall risk level: {overall_risk}. "
        summary += f"Critical risks: {critical_count}, High risks: {high_count}. "
        summary += "Immediate attention required for high and critical risks."
        
        return summary


def assess_risk(
    context: Dict[str, Any],
    assessor: Optional[RiskAssessor] = None,
    methodology: str = "qualitative",
) -> RiskAssessment:
    """
    Perform a risk assessment.
    
    Args:
        context: Context information for assessment
        assessor: Optional RiskAssessor instance
        methodology: Assessment methodology (qualitative, quantitative, hybrid)
        
    Returns:
        RiskAssessment results
    """
    if assessor is None:
        assessor = RiskAssessor(methodology=methodology)
    return assessor.assess(context)


def calculate_risk_score(likelihood: str, impact: str) -> float:
    """
    Calculate risk score from likelihood and impact.
    
    Args:
        likelihood: Likelihood level (low, medium, high)
        impact: Impact level (low, medium, high, critical)
        
    Returns:
        Risk score (0.0 to 1.0)
    """
    likelihood_scores = {
        LikelihoodLevel.LOW.value: 0.25,
        LikelihoodLevel.MEDIUM.value: 0.5,
        LikelihoodLevel.HIGH.value: 0.75
    }
    
    impact_scores = {
        ImpactLevel.LOW.value: 0.25,
        ImpactLevel.MEDIUM.value: 0.5,
        ImpactLevel.HIGH.value: 0.75,
        ImpactLevel.CRITICAL.value: 1.0
    }
    
    likelihood_score = likelihood_scores.get(likelihood.lower(), 0.5)
    impact_score = impact_scores.get(impact.lower(), 0.5)
    
    # Risk score is the product of likelihood and impact
    risk_score = likelihood_score * impact_score
    
    return round(risk_score, 3)


def prioritize_risks(risks: List[Risk]) -> List[Risk]:
    """
    Prioritize risks by score and mitigation priority.
    
    Args:
        risks: List of risks
        
    Returns:
        Sorted list of risks (highest priority first)
    """
    priority_order = {
        "critical": 4,
        "high": 3,
        "medium": 2,
        "low": 1
    }
    
    return sorted(
        risks,
        key=lambda r: (r.risk_score, priority_order.get(r.mitigation_priority, 0)),
        reverse=True
    )


def calculate_aggregate_risk(risks: List[Risk]) -> Dict[str, Any]:
    """
    Calculate aggregate risk metrics.
    
    Args:
        risks: List of risks
        
    Returns:
        Aggregate risk metrics
    """
    if not risks:
        return {
            "total_risks": 0,
            "average_risk_score": 0.0,
            "max_risk_score": 0.0,
            "risk_distribution": {}
        }
    
    risk_scores = [r.risk_score for r in risks]
    avg_score = sum(risk_scores) / len(risk_scores)
    max_score = max(risk_scores)
    
    # Distribution by impact
    distribution = {
        "critical": sum(1 for r in risks if r.impact == ImpactLevel.CRITICAL.value),
        "high": sum(1 for r in risks if r.impact == ImpactLevel.HIGH.value),
        "medium": sum(1 for r in risks if r.impact == ImpactLevel.MEDIUM.value),
        "low": sum(1 for r in risks if r.impact == ImpactLevel.LOW.value)
    }
    
    return {
        "total_risks": len(risks),
        "average_risk_score": round(avg_score, 3),
        "max_risk_score": round(max_score, 3),
        "risk_distribution": distribution
    }
