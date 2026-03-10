"""Comprehensive tests for security.theory.risk_assessment — zero-mock.

Covers: RiskLevel, LikelihoodLevel, ImpactLevel, Risk, RiskAssessment,
RiskAssessor (qualitative methodology), assess_risk, calculate_risk_score,
prioritize_risks, calculate_aggregate_risk.
"""


from codomyrmex.security.theory.risk_assessment import (
    ImpactLevel,
    LikelihoodLevel,
    Risk,
    RiskAssessment,
    RiskAssessor,
    RiskLevel,
    assess_risk,
    calculate_aggregate_risk,
    calculate_risk_score,
    prioritize_risks,
)

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class TestRiskLevel:
    def test_values(self):
        assert RiskLevel.LOW.value == "low"
        assert RiskLevel.CRITICAL.value == "critical"


class TestLikelihoodLevel:
    def test_values(self):
        assert LikelihoodLevel.LOW.value == "low"
        assert LikelihoodLevel.HIGH.value == "high"


class TestImpactLevel:
    def test_values(self):
        assert ImpactLevel.LOW.value == "low"
        assert ImpactLevel.CRITICAL.value == "critical"


# ---------------------------------------------------------------------------
# Risk dataclass
# ---------------------------------------------------------------------------


class TestRisk:
    def test_create_risk(self):
        r = Risk(
            risk_id="R-001",
            description="Data breach via exposed API",
            likelihood="high",
            impact="critical",
            risk_score=0.9,
        )
        assert r.risk_id == "R-001"
        assert r.risk_score == 0.9

    def test_default_fields(self):
        r = Risk(
            risk_id="R-002",
            description="Minor config leak",
            likelihood="low",
            impact="low",
            risk_score=0.1,
        )
        assert r.category == "general"
        assert r.affected_assets == []
        assert r.residual_risk is None


# ---------------------------------------------------------------------------
# RiskAssessment dataclass
# ---------------------------------------------------------------------------


class TestRiskAssessment:
    def test_create_assessment(self):
        a = RiskAssessment(
            assessment_id="RA-001",
            risks=[],
            overall_risk_level="low",
            recommendations=["Implement MFA"],
        )
        assert a.assessment_id == "RA-001"
        assert a.assessment_methodology == "qualitative"

    def test_assessment_with_risks(self):
        risk = Risk(
            risk_id="R-001",
            description="Test risk",
            likelihood="medium",
            impact="high",
            risk_score=0.7,
        )
        a = RiskAssessment(
            assessment_id="RA-002",
            risks=[risk],
            overall_risk_level="high",
            recommendations=["Fix it"],
        )
        assert len(a.risks) == 1


# ---------------------------------------------------------------------------
# RiskAssessor
# ---------------------------------------------------------------------------


class TestRiskAssessor:
    def test_init(self):
        assessor = RiskAssessor()
        assert assessor.methodology == "qualitative"

    def test_init_custom(self):
        assessor = RiskAssessor(methodology="quantitative")
        assert assessor.methodology == "quantitative"

    def test_assess_basic_context(self):
        assessor = RiskAssessor()
        context = {
            "system_name": "Web App",
            "assets": ["user_data", "credentials"],
            "threats": ["sql_injection", "xss"],
        }
        result = assessor.assess(context)
        assert isinstance(result, RiskAssessment)
        assert len(result.risks) > 0

    def test_assess_empty_context(self):
        assessor = RiskAssessor()
        result = assessor.assess({})
        assert isinstance(result, RiskAssessment)


# ---------------------------------------------------------------------------
# Convenience functions
# ---------------------------------------------------------------------------


class TestAssessRisk:
    def test_assess_risk_default(self):
        result = assess_risk({"system_name": "Test", "assets": ["data"]})
        assert isinstance(result, RiskAssessment)

    def test_assess_risk_with_assessor(self):
        assessor = RiskAssessor(methodology="qualitative")
        result = assess_risk(
            {"system_name": "API", "assets": ["keys"]},
            assessor=assessor,
        )
        assert isinstance(result, RiskAssessment)


class TestCalculateRiskScore:
    def test_low_low(self):
        score = calculate_risk_score("low", "low")
        assert 0.0 <= score <= 0.3

    def test_high_critical(self):
        score = calculate_risk_score("high", "critical")
        assert score >= 0.7

    def test_medium_medium(self):
        score = calculate_risk_score("medium", "medium")
        assert 0.2 <= score <= 0.7


class TestPrioritizeRisks:
    def test_prioritize_empty(self):
        result = prioritize_risks([])
        assert result == []

    def test_prioritize_sorts_by_score(self):
        risks = [
            Risk(risk_id="R-1", description="Low", likelihood="low", impact="low", risk_score=0.1),
            Risk(risk_id="R-2", description="High", likelihood="high", impact="high", risk_score=0.9),
            Risk(risk_id="R-3", description="Med", likelihood="medium", impact="medium", risk_score=0.5),
        ]
        sorted_risks = prioritize_risks(risks)
        assert sorted_risks[0].risk_score >= sorted_risks[-1].risk_score


class TestCalculateAggregateRisk:
    def test_aggregate_empty(self):
        result = calculate_aggregate_risk([])
        assert isinstance(result, dict)

    def test_aggregate_with_risks(self):
        risks = [
            Risk(risk_id="R-1", description="A", likelihood="high", impact="high", risk_score=0.8),
            Risk(risk_id="R-2", description="B", likelihood="low", impact="low", risk_score=0.2),
        ]
        result = calculate_aggregate_risk(risks)
        assert isinstance(result, dict)
        assert len(result) > 0
