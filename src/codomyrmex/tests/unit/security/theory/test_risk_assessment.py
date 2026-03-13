"""Zero-mock tests for codomyrmex.security.theory.risk_assessment."""

import pytest

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
# RiskLevel enum
# ---------------------------------------------------------------------------


class TestRiskLevel:
    def test_member_count(self):
        assert len(RiskLevel) == 4

    def test_member_names(self):
        names = {m.name for m in RiskLevel}
        assert names == {"LOW", "MEDIUM", "HIGH", "CRITICAL"}

    def test_string_values(self):
        assert RiskLevel.LOW.value == "low"
        assert RiskLevel.MEDIUM.value == "medium"
        assert RiskLevel.HIGH.value == "high"
        assert RiskLevel.CRITICAL.value == "critical"


# ---------------------------------------------------------------------------
# LikelihoodLevel enum
# ---------------------------------------------------------------------------


class TestLikelihoodLevel:
    def test_member_count(self):
        assert len(LikelihoodLevel) == 3

    def test_member_names(self):
        names = {m.name for m in LikelihoodLevel}
        assert names == {"LOW", "MEDIUM", "HIGH"}

    def test_string_values(self):
        assert LikelihoodLevel.LOW.value == "low"
        assert LikelihoodLevel.MEDIUM.value == "medium"
        assert LikelihoodLevel.HIGH.value == "high"


# ---------------------------------------------------------------------------
# ImpactLevel enum
# ---------------------------------------------------------------------------


class TestImpactLevel:
    def test_member_count(self):
        assert len(ImpactLevel) == 4

    def test_member_names(self):
        names = {m.name for m in ImpactLevel}
        assert names == {"LOW", "MEDIUM", "HIGH", "CRITICAL"}

    def test_string_values(self):
        assert ImpactLevel.LOW.value == "low"
        assert ImpactLevel.MEDIUM.value == "medium"
        assert ImpactLevel.HIGH.value == "high"
        assert ImpactLevel.CRITICAL.value == "critical"


# ---------------------------------------------------------------------------
# calculate_risk_score function
# ---------------------------------------------------------------------------


class TestCalculateRiskScore:
    """Exhaustive tests for the likelihood * impact product formula."""

    # likelihood scores: low=0.25, medium=0.5, high=0.75
    # impact scores: low=0.25, medium=0.5, high=0.75, critical=1.0

    def test_low_likelihood_low_impact(self):
        score = calculate_risk_score("low", "low")
        assert score == pytest.approx(0.062, abs=1e-3)

    def test_low_likelihood_medium_impact(self):
        score = calculate_risk_score("low", "medium")
        assert score == pytest.approx(0.125, abs=1e-3)

    def test_low_likelihood_high_impact(self):
        score = calculate_risk_score("low", "high")
        assert score == pytest.approx(0.188, abs=1e-3)

    def test_low_likelihood_critical_impact(self):
        score = calculate_risk_score("low", "critical")
        assert score == pytest.approx(0.25, abs=1e-3)

    def test_medium_likelihood_low_impact(self):
        score = calculate_risk_score("medium", "low")
        assert score == pytest.approx(0.125, abs=1e-3)

    def test_medium_likelihood_medium_impact(self):
        score = calculate_risk_score("medium", "medium")
        assert score == pytest.approx(0.25, abs=1e-3)

    def test_medium_likelihood_high_impact(self):
        score = calculate_risk_score("medium", "high")
        assert score == pytest.approx(0.375, abs=1e-3)

    def test_medium_likelihood_critical_impact(self):
        score = calculate_risk_score("medium", "critical")
        assert score == pytest.approx(0.5, abs=1e-3)

    def test_high_likelihood_low_impact(self):
        score = calculate_risk_score("high", "low")
        assert score == pytest.approx(0.188, abs=1e-3)

    def test_high_likelihood_medium_impact(self):
        score = calculate_risk_score("high", "medium")
        assert score == pytest.approx(0.375, abs=1e-3)

    def test_high_likelihood_high_impact(self):
        score = calculate_risk_score("high", "high")
        assert score == pytest.approx(0.562, abs=1e-3)

    def test_high_likelihood_critical_impact(self):
        score = calculate_risk_score("high", "critical")
        assert score == pytest.approx(0.75, abs=1e-3)

    def test_unknown_likelihood_defaults_to_medium_score(self):
        # Unknown likelihood falls back to 0.5 (medium default)
        score = calculate_risk_score("unknown", "medium")
        assert score == pytest.approx(0.25, abs=1e-3)

    def test_unknown_impact_defaults_to_medium_score(self):
        score = calculate_risk_score("medium", "unknown")
        assert score == pytest.approx(0.25, abs=1e-3)

    def test_returns_float(self):
        assert isinstance(calculate_risk_score("medium", "high"), float)

    def test_score_is_bounded_0_to_1(self):
        for likelihood in ("low", "medium", "high"):
            for impact in ("low", "medium", "high", "critical"):
                score = calculate_risk_score(likelihood, impact)
                assert 0.0 <= score <= 1.0, (
                    f"Out of range for {likelihood}/{impact}: {score}"
                )

    def test_case_insensitive_lookup(self):
        """Source calls .lower() on inputs before lookup."""
        assert calculate_risk_score("HIGH", "CRITICAL") == calculate_risk_score(
            "high", "critical"
        )
        assert calculate_risk_score("Low", "Medium") == calculate_risk_score(
            "low", "medium"
        )


# ---------------------------------------------------------------------------
# Risk dataclass
# ---------------------------------------------------------------------------


class TestRiskDataclass:
    def _make_risk(self, **overrides):
        defaults = {
            "risk_id": "risk-001",
            "description": "Test risk",
            "likelihood": "medium",
            "impact": "high",
            "risk_score": 0.375,
        }
        defaults.update(overrides)
        return Risk(**defaults)

    def test_required_fields_instantiation(self):
        r = self._make_risk()
        assert r.risk_id == "risk-001"
        assert r.description == "Test risk"
        assert r.likelihood == "medium"
        assert r.impact == "high"
        assert r.risk_score == pytest.approx(0.375)

    def test_default_category(self):
        r = self._make_risk()
        assert r.category == "general"

    def test_default_threat_source(self):
        r = self._make_risk()
        assert r.threat_source == "unknown"

    def test_default_vulnerability_is_empty_string(self):
        r = self._make_risk()
        assert r.vulnerability == ""

    def test_default_mitigation_priority(self):
        r = self._make_risk()
        assert r.mitigation_priority == "medium"

    def test_default_residual_risk_is_none(self):
        r = self._make_risk()
        assert r.residual_risk is None

    def test_default_risk_owner_is_none(self):
        r = self._make_risk()
        assert r.risk_owner is None

    def test_default_list_fields_are_empty(self):
        r = self._make_risk()
        assert r.affected_assets == []
        assert r.existing_controls == []
        assert r.recommended_controls == []

    def test_list_fields_do_not_share_default(self):
        r1 = self._make_risk(risk_id="r1")
        r2 = self._make_risk(risk_id="r2")
        r1.affected_assets.append("server")
        assert r2.affected_assets == []


# ---------------------------------------------------------------------------
# RiskAssessment dataclass
# ---------------------------------------------------------------------------


class TestRiskAssessmentDataclass:
    def test_basic_instantiation(self):
        ra = RiskAssessment(
            assessment_id="a-001",
            risks=[],
            overall_risk_level="low",
            recommendations=[],
        )
        assert ra.assessment_id == "a-001"
        assert ra.risks == []
        assert ra.overall_risk_level == "low"

    def test_default_methodology(self):
        ra = RiskAssessment(
            assessment_id="a-001",
            risks=[],
            overall_risk_level="low",
            recommendations=[],
        )
        assert ra.assessment_methodology == "qualitative"

    def test_created_at_is_datetime(self):
        from datetime import datetime

        ra = RiskAssessment(
            assessment_id="a-001",
            risks=[],
            overall_risk_level="low",
            recommendations=[],
        )
        assert isinstance(ra.created_at, datetime)


# ---------------------------------------------------------------------------
# RiskAssessor class
# ---------------------------------------------------------------------------


class TestRiskAssessor:
    def test_default_methodology_is_qualitative(self):
        assessor = RiskAssessor()
        assert assessor.methodology == "qualitative"

    def test_custom_methodology(self):
        assessor = RiskAssessor(methodology="quantitative")
        assert assessor.methodology == "quantitative"

    def test_assess_returns_risk_assessment(self):
        assessor = RiskAssessor()
        result = assessor.assess({})
        assert isinstance(result, RiskAssessment)

    def test_assess_empty_context_returns_generic_risk(self):
        assessor = RiskAssessor()
        result = assessor.assess({})
        assert len(result.risks) == 1
        assert result.risks[0].category == "general"

    def test_assess_with_data_asset_triggers_data_protection_risk(self):
        assessor = RiskAssessor()
        result = assessor.assess({"assets": ["user_data_store"]})
        categories = [r.category for r in result.risks]
        assert "data_protection" in categories

    def test_assess_with_data_breach_in_threats_triggers_data_risk(self):
        assessor = RiskAssessor()
        result = assessor.assess({"threats": ["data_breach"]})
        categories = [r.category for r in result.risks]
        assert "data_protection" in categories

    def test_assess_with_authentication_context_triggers_access_control(self):
        assessor = RiskAssessor()
        result = assessor.assess({"system_type": "authentication_service"})
        categories = [r.category for r in result.risks]
        assert "access_control" in categories

    def test_assess_with_service_asset_triggers_availability_risk(self):
        assessor = RiskAssessor()
        result = assessor.assess({"assets": ["web_service"]})
        categories = [r.category for r in result.risks]
        assert "availability" in categories

    def test_assess_risk_scores_are_populated(self):
        assessor = RiskAssessor()
        result = assessor.assess({"assets": ["user_data"]})
        for risk in result.risks:
            assert risk.risk_score > 0.0

    def test_assess_assessment_id_has_prefix(self):
        assessor = RiskAssessor()
        result = assessor.assess({})
        assert result.assessment_id.startswith("assessment_")

    def test_assess_summary_is_string(self):
        assessor = RiskAssessor()
        result = assessor.assess({"assets": ["user_data"]})
        assert isinstance(result.summary, str)
        assert len(result.summary) > 0

    def test_assess_risk_matrix_is_dict_with_levels(self):
        assessor = RiskAssessor()
        result = assessor.assess({"assets": ["service"]})
        assert isinstance(result.risk_matrix, dict)
        for key in ("critical", "high", "medium", "low"):
            assert key in result.risk_matrix

    def test_calculate_residual_risk_zero_controls(self):
        assessor = RiskAssessor()
        risk = Risk(
            risk_id="r-test",
            description="test",
            likelihood="medium",
            impact="high",
            risk_score=0.375,
            existing_controls=[],
        )
        residual = assessor._calculate_residual_risk(risk)
        assert residual == pytest.approx(0.375)

    def test_calculate_residual_risk_one_control_reduces_by_0_1(self):
        assessor = RiskAssessor()
        risk = Risk(
            risk_id="r-test",
            description="test",
            likelihood="medium",
            impact="high",
            risk_score=0.375,
            existing_controls=["firewall"],
        )
        residual = assessor._calculate_residual_risk(risk)
        assert residual == pytest.approx(0.375 - 0.1, abs=1e-6)

    def test_calculate_residual_risk_max_reduction_is_0_5(self):
        assessor = RiskAssessor()
        risk = Risk(
            risk_id="r-test",
            description="test",
            likelihood="high",
            impact="critical",
            risk_score=0.75,
            existing_controls=["c1", "c2", "c3", "c4", "c5", "c6", "c7"],
        )
        residual = assessor._calculate_residual_risk(risk)
        # Max reduction is 0.5 regardless of how many controls
        assert residual == pytest.approx(0.75 - 0.5, abs=1e-6)

    def test_calculate_residual_risk_never_below_zero(self):
        assessor = RiskAssessor()
        risk = Risk(
            risk_id="r-test",
            description="test",
            likelihood="low",
            impact="low",
            risk_score=0.062,
            existing_controls=["c1", "c2", "c3", "c4", "c5", "c6"],
        )
        residual = assessor._calculate_residual_risk(risk)
        assert residual >= 0.0

    def test_calculate_overall_risk_above_0_75_is_critical(self):
        assessor = RiskAssessor()
        risks = [
            Risk(
                risk_id="r1",
                description="d",
                likelihood="high",
                impact="critical",
                risk_score=0.8,
            )
        ]
        level = assessor._calculate_overall_risk(risks)
        assert level == RiskLevel.CRITICAL.value

    def test_calculate_overall_risk_above_0_5_is_high(self):
        assessor = RiskAssessor()
        risks = [
            Risk(
                risk_id="r1",
                description="d",
                likelihood="high",
                impact="high",
                risk_score=0.562,
            )
        ]
        level = assessor._calculate_overall_risk(risks)
        assert level == RiskLevel.HIGH.value

    def test_calculate_overall_risk_above_0_25_is_medium(self):
        assessor = RiskAssessor()
        risks = [
            Risk(
                risk_id="r1",
                description="d",
                likelihood="medium",
                impact="high",
                risk_score=0.375,
            )
        ]
        level = assessor._calculate_overall_risk(risks)
        assert level == RiskLevel.MEDIUM.value

    def test_calculate_overall_risk_at_or_below_0_25_is_low(self):
        assessor = RiskAssessor()
        risks = [
            Risk(
                risk_id="r1",
                description="d",
                likelihood="low",
                impact="medium",
                risk_score=0.125,
            )
        ]
        level = assessor._calculate_overall_risk(risks)
        assert level == RiskLevel.LOW.value

    def test_calculate_overall_risk_empty_list_is_low(self):
        assessor = RiskAssessor()
        level = assessor._calculate_overall_risk([])
        assert level == RiskLevel.LOW.value

    def test_existing_controls_cause_residual_risk_to_be_set(self):
        assessor = RiskAssessor()
        result = assessor.assess(
            {
                "assets": ["data_store"],
                "existing_controls": ["encryption", "access_control"],
            }
        )
        for risk in result.risks:
            if risk.existing_controls:
                assert risk.residual_risk is not None


# ---------------------------------------------------------------------------
# prioritize_risks function
# ---------------------------------------------------------------------------


class TestPrioritizeRisks:
    def _make_risk(self, risk_id, risk_score, priority):
        return Risk(
            risk_id=risk_id,
            description="test",
            likelihood="medium",
            impact="high",
            risk_score=risk_score,
            mitigation_priority=priority,
        )

    def test_higher_risk_score_first(self):
        r_low = self._make_risk("low", 0.125, "low")
        r_high = self._make_risk("high", 0.75, "critical")
        result = prioritize_risks([r_low, r_high])
        assert result[0].risk_id == "high"

    def test_returns_same_length(self):
        risks = [self._make_risk(f"r{i}", 0.1 * i, "medium") for i in range(5)]
        result = prioritize_risks(risks)
        assert len(result) == 5

    def test_returns_list_of_risk_objects(self):
        risks = [self._make_risk("r1", 0.3, "medium")]
        result = prioritize_risks(risks)
        assert all(isinstance(r, Risk) for r in result)

    def test_empty_list_returns_empty(self):
        result = prioritize_risks([])
        assert result == []


# ---------------------------------------------------------------------------
# calculate_aggregate_risk function
# ---------------------------------------------------------------------------


class TestCalculateAggregateRisk:
    def test_empty_list_returns_zeroed_dict(self):
        result = calculate_aggregate_risk([])
        assert result["total_risks"] == 0
        assert result["average_risk_score"] == 0.0
        assert result["max_risk_score"] == 0.0
        assert result["risk_distribution"] == {}

    def test_total_risks_count(self):
        risks = [
            Risk(
                risk_id=f"r{i}",
                description="d",
                likelihood="medium",
                impact="high",
                risk_score=0.375,
            )
            for i in range(3)
        ]
        result = calculate_aggregate_risk(risks)
        assert result["total_risks"] == 3

    def test_average_risk_score_is_correct(self):
        risks = [
            Risk(
                risk_id="r1",
                description="d",
                likelihood="low",
                impact="low",
                risk_score=0.062,
            ),
            Risk(
                risk_id="r2",
                description="d",
                likelihood="high",
                impact="critical",
                risk_score=0.75,
            ),
        ]
        result = calculate_aggregate_risk(risks)
        expected_avg = round((0.062 + 0.75) / 2, 3)
        assert result["average_risk_score"] == pytest.approx(expected_avg, abs=1e-3)

    def test_max_risk_score_is_correct(self):
        risks = [
            Risk(
                risk_id="r1",
                description="d",
                likelihood="low",
                impact="low",
                risk_score=0.062,
            ),
            Risk(
                risk_id="r2",
                description="d",
                likelihood="high",
                impact="critical",
                risk_score=0.75,
            ),
        ]
        result = calculate_aggregate_risk(risks)
        assert result["max_risk_score"] == pytest.approx(0.75, abs=1e-3)

    def test_risk_distribution_counts_by_impact(self):
        risks = [
            Risk(
                risk_id="r1",
                description="d",
                likelihood="high",
                impact="critical",
                risk_score=0.75,
            ),
            Risk(
                risk_id="r2",
                description="d",
                likelihood="medium",
                impact="high",
                risk_score=0.375,
            ),
            Risk(
                risk_id="r3",
                description="d",
                likelihood="low",
                impact="medium",
                risk_score=0.125,
            ),
            Risk(
                risk_id="r4",
                description="d",
                likelihood="low",
                impact="low",
                risk_score=0.062,
            ),
        ]
        result = calculate_aggregate_risk(risks)
        dist = result["risk_distribution"]
        assert dist["critical"] == 1
        assert dist["high"] == 1
        assert dist["medium"] == 1
        assert dist["low"] == 1


# ---------------------------------------------------------------------------
# assess_risk convenience function
# ---------------------------------------------------------------------------


class TestAssessRisk:
    def test_returns_risk_assessment(self):
        result = assess_risk({})
        assert isinstance(result, RiskAssessment)

    def test_default_methodology_is_qualitative(self):
        result = assess_risk({})
        assert result.assessment_methodology == "qualitative"

    def test_custom_methodology_passed_through(self):
        result = assess_risk({}, methodology="quantitative")
        assert result.assessment_methodology == "quantitative"

    def test_custom_assessor_used(self):
        assessor = RiskAssessor(methodology="hybrid")
        result = assess_risk({}, assessor=assessor)
        assert result.assessment_methodology == "hybrid"

    def test_context_data_used_in_assessment(self):
        result = assess_risk({"assets": ["sensitive_data_store"]})
        categories = [r.category for r in result.risks]
        assert "data_protection" in categories
