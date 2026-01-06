"""
Unit tests for the security.theory module.

Tests security theory operations including principles, frameworks, threat modeling,
risk assessment, architecture patterns, and best practices.
"""

import pytest

from codomyrmex.security.theory import (
    get_security_principles,
    apply_principle,
    SecurityPrinciple,
    get_framework,
    apply_framework,
    SecurityFramework,
    create_threat_model,
    analyze_threats,
    ThreatModel,
    assess_risk,
    calculate_risk_score,
    RiskAssessment,
    get_security_patterns,
    apply_pattern,
    SecurityPattern,
    get_best_practices,
    check_compliance_with_practices,
    SecurityBestPractice,
)


class TestSecurityPrinciples:
    """Test security principles."""
    
    def test_get_security_principles(self):
        """Test getting all security principles."""
        principles = get_security_principles()
        assert isinstance(principles, list)
        assert len(principles) > 0
        assert all(isinstance(p, SecurityPrinciple) for p in principles)
    
    def test_apply_principle(self):
        """Test applying a security principle."""
        result = apply_principle("least_privilege", {"user": "admin", "resource": "database"})
        assert isinstance(result, dict)
        assert "applied" in result
    
    def test_apply_unknown_principle(self):
        """Test applying unknown principle returns error."""
        result = apply_principle("unknown_principle", {})
        assert result["applied"] is False
        assert "error" in result


class TestSecurityFrameworks:
    """Test security frameworks."""
    
    def test_get_framework(self):
        """Test getting a security framework."""
        framework = get_framework("owasp_top_10")
        assert framework is not None
        assert isinstance(framework, SecurityFramework)
        assert framework.name == "OWASP Top 10"
    
    def test_get_unknown_framework(self):
        """Test getting unknown framework returns None."""
        framework = get_framework("unknown_framework")
        assert framework is None
    
    def test_apply_framework(self):
        """Test applying a security framework."""
        result = apply_framework("owasp_top_10", {"system": "web_app"})
        assert isinstance(result, dict)
        assert "applied" in result
    
    def test_nist_csf_framework(self):
        """Test NIST CSF framework."""
        framework = get_framework("nist_csf")
        assert framework is not None
        assert framework.name == "NIST Cybersecurity Framework"
    
    def test_iso_27001_framework(self):
        """Test ISO 27001 framework."""
        framework = get_framework("iso_27001")
        assert framework is not None
        assert framework.name == "ISO 27001"


class TestThreatModeling:
    """Test threat modeling."""
    
    def test_create_threat_model(self):
        """Test creating a threat model."""
        threat_model = create_threat_model(
            system_name="web_application",
            assets=["user_data", "payment_info"],
            attack_surface=["web_interface", "api_endpoints"]
        )
        assert threat_model is not None
        assert isinstance(threat_model, ThreatModel)
        assert threat_model.system_name == "web_application"
        assert len(threat_model.assets) == 2
        assert len(threat_model.attack_surface) == 2
    
    def test_analyze_threats(self):
        """Test analyzing threats in a threat model."""
        threat_model = create_threat_model(
            system_name="test_system",
            assets=["asset1"],
            attack_surface=["surface1"]
        )
        analysis = analyze_threats(threat_model)
        assert isinstance(analysis, dict)
        assert "total_threats" in analysis
        assert "critical_count" in analysis


class TestRiskAssessment:
    """Test risk assessment."""
    
    def test_calculate_risk_score(self):
        """Test calculating risk score."""
        score = calculate_risk_score("high", "critical")
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0
        
        # Test different combinations
        score_low_low = calculate_risk_score("low", "low")
        score_high_high = calculate_risk_score("high", "high")
        assert score_high_high > score_low_low
    
    def test_assess_risk(self):
        """Test performing risk assessment."""
        context = {
            "system": "payment_processor",
            "threats": ["data_breach", "unauthorized_access"]
        }
        assessment = assess_risk(context)
        assert assessment is not None
        assert isinstance(assessment, RiskAssessment)
        assert assessment.risks is not None
        assert assessment.overall_risk_level in ["low", "medium", "high"]


class TestArchitecturePatterns:
    """Test security architecture patterns."""
    
    def test_get_security_patterns(self):
        """Test getting all security patterns."""
        patterns = get_security_patterns()
        assert isinstance(patterns, list)
        assert len(patterns) > 0
        assert all(isinstance(p, SecurityPattern) for p in patterns)
    
    def test_apply_pattern(self):
        """Test applying a security pattern."""
        result = apply_pattern("zero_trust", {"network": "internal"})
        assert isinstance(result, dict)
        assert "applied" in result
    
    def test_zero_trust_pattern(self):
        """Test zero trust pattern."""
        patterns = get_security_patterns()
        zero_trust = next((p for p in patterns if p.name == "Zero Trust"), None)
        assert zero_trust is not None
        assert "trust" in zero_trust.description.lower()


class TestBestPractices:
    """Test security best practices."""
    
    def test_get_best_practices(self):
        """Test getting all best practices."""
        practices = get_best_practices()
        assert isinstance(practices, list)
        assert len(practices) > 0
        assert all(isinstance(p, SecurityBestPractice) for p in practices)
    
    def test_get_best_practices_by_category(self):
        """Test getting best practices filtered by category."""
        practices = get_best_practices(category="authentication")
        assert isinstance(practices, list)
        assert all(p.category == "authentication" for p in practices)
    
    def test_check_compliance_with_practices(self):
        """Test checking compliance with best practices."""
        context = {"system": "web_app"}
        compliance = check_compliance_with_practices(context)
        assert isinstance(compliance, dict)
        assert "total_practices" in compliance
        assert "compliant" in compliance

