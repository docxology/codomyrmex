"""
Unit tests for the security.cognitive module.

Tests cognitive security operations including social engineering detection,
phishing analysis, awareness training, cognitive threat assessment, and behavior analysis.
"""

import pytest

from codomyrmex.security.cognitive import (
    AwarenessTrainer,
    BehaviorAnalyzer,
    CognitiveThreatAssessor,
    PhishingAnalyzer,
    SocialEngineeringDetector,
    analyze_communication,
    analyze_email,
    analyze_user_behavior,
    assess_cognitive_threats,
    assess_training_effectiveness,
    create_training_module,
    detect_anomalous_behavior,
    detect_phishing_attempt,
    detect_social_engineering,
    evaluate_human_factors,
)


@pytest.mark.unit
class TestSocialEngineeringDetection:
    """Test social engineering detection."""

    def test_social_engineering_detector_initialization(self):
        """Test SocialEngineeringDetector can be initialized."""
        detector = SocialEngineeringDetector()
        assert detector is not None

    def test_detect_social_engineering(self):
        """Test detecting social engineering indicators."""
        communication = "URGENT: Your account will be closed. Click here immediately!"
        indicators = detect_social_engineering(communication)
        assert isinstance(indicators, list)

    def test_analyze_communication(self):
        """Test analyzing communication for social engineering."""
        communication = "This is an urgent request for your password..."
        analysis = analyze_communication(communication)
        assert isinstance(analysis, dict)
        assert "total_indicators" in analysis
        assert "risk_score" in analysis
        assert 0.0 <= analysis["risk_score"] <= 1.0


@pytest.mark.unit
class TestPhishingAnalysis:
    """Test phishing analysis."""

    def test_phishing_analyzer_initialization(self):
        """Test PhishingAnalyzer can be initialized."""
        analyzer = PhishingAnalyzer()
        assert analyzer is not None

    def test_analyze_email(self):
        """Test analyzing email for phishing."""
        email_content = "Click here to verify your account: http://fake-bank.com"
        analysis = analyze_email(email_content, sender="noreply@fake-bank.com")
        assert analysis is not None
        assert hasattr(analysis, "is_phishing")
        assert hasattr(analysis, "confidence")
        assert hasattr(analysis, "risk_level")
        assert 0.0 <= analysis.confidence <= 1.0

    def test_detect_phishing_attempt(self):
        """Test detecting phishing attempt."""
        email_content = "Click here to verify your account"
        is_phishing = detect_phishing_attempt(email_content)
        assert isinstance(is_phishing, bool)


@pytest.mark.unit
class TestAwarenessTraining:
    """Test awareness training."""

    def test_awareness_trainer_initialization(self):
        """Test AwarenessTrainer can be initialized."""
        trainer = AwarenessTrainer()
        assert trainer is not None
        assert trainer.modules == {}
        assert trainer.results == []

    def test_create_training_module(self):
        """Test creating a training module."""
        module = create_training_module(
            module_id="phishing-101",
            title="Phishing Awareness",
            description="Learn to identify phishing attempts",
            content="Phishing emails often contain...",
            difficulty="beginner",
        )
        assert module is not None
        assert module.module_id == "phishing-101"
        assert module.title == "Phishing Awareness"
        assert module.difficulty == "beginner"
        assert module.created_at is not None

    def test_assess_training_effectiveness(self):
        """Test assessing training effectiveness."""
        effectiveness = assess_training_effectiveness("user123")
        assert isinstance(effectiveness, dict)
        assert "user_id" in effectiveness
        assert "modules_completed" in effectiveness
        assert "average_score" in effectiveness
        assert "effectiveness" in effectiveness


@pytest.mark.unit
class TestCognitiveThreatAssessment:
    """Test cognitive threat assessment."""

    def test_cognitive_threat_assessor_initialization(self):
        """Test CognitiveThreatAssessor can be initialized."""
        assessor = CognitiveThreatAssessor()
        assert assessor is not None

    def test_assess_cognitive_threats(self):
        """Test assessing cognitive threats."""
        context = {"environment": "remote_work", "training_level": "low"}
        assessment = assess_cognitive_threats(context)
        assert isinstance(assessment, dict)
        assert "total_threats" in assessment

    def test_evaluate_human_factors(self):
        """Test evaluating human factors."""
        scenario = {
            "training_level": "intermediate",
            "experience": "high",
            "stress_level": "medium",
        }
        factors = evaluate_human_factors(scenario)
        assert isinstance(factors, dict)
        assert "training_level" in factors
        assert "experience" in factors


@pytest.mark.unit
class TestBehaviorAnalysis:
    """Test behavior analysis."""

    def test_behavior_analyzer_initialization(self):
        """Test BehaviorAnalyzer can be initialized."""
        analyzer = BehaviorAnalyzer()
        assert analyzer is not None
        assert analyzer.behavior_history == {}

    def test_analyze_user_behavior(self):
        """Test analyzing user behavior."""
        behavior_data = {
            "login_time": "02:00",
            "location": "unusual",
            "actions": ["sensitive_access"],
        }
        patterns = analyze_user_behavior("user123", behavior_data)
        assert isinstance(patterns, list)

    def test_detect_anomalous_behavior(self):
        """Test detecting anomalous behavior."""
        current_behavior = {
            "login_time": "02:00",
            "location": "unusual",
            "actions": ["sensitive_access"],
        }
        anomalies = detect_anomalous_behavior("user123", current_behavior)
        assert isinstance(anomalies, list)


# ---------------------------------------------------------------------------
# CognitiveThreatAssessor — branch coverage for assess_threats()
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestAssessThreatsAllBranches:
    """Cover every conditional branch in assess_threats()."""

    def _assessor(self):
        from codomyrmex.security.cognitive.cognitive_threat_assessment import (
            CognitiveThreatAssessor,
        )
        return CognitiveThreatAssessor()

    def test_admin_access_level_yields_high_privilege_target(self):
        # Arrange: admin access triggers the privileged branch
        assessor = self._assessor()
        context = {"access_level": "admin"}
        # Act
        threats = assessor.assess_threats(context)
        # Assert
        types = [t.threat_type for t in threats]
        assert "high_privilege_target" in types

    def test_privileged_access_level_yields_high_privilege_target(self):
        assessor = self._assessor()
        threats = assessor.assess_threats({"access_level": "privileged"})
        types = [t.threat_type for t in threats]
        assert "high_privilege_target" in types

    def test_high_privilege_target_severity_is_critical(self):
        assessor = self._assessor()
        threats = assessor.assess_threats({"access_level": "admin"})
        critical = [t for t in threats if t.threat_type == "high_privilege_target"]
        assert len(critical) == 1
        assert critical[0].severity == "critical"

    def test_remote_environment_yields_insecure_environment(self):
        assessor = self._assessor()
        threats = assessor.assess_threats({"environment": "remote"})
        types = [t.threat_type for t in threats]
        assert "insecure_environment" in types

    def test_public_wifi_environment_yields_insecure_environment(self):
        assessor = self._assessor()
        threats = assessor.assess_threats({"environment": "public_wifi"})
        types = [t.threat_type for t in threats]
        assert "insecure_environment" in types

    def test_recent_incidents_nonempty_yields_elevated_risk_period(self):
        assessor = self._assessor()
        threats = assessor.assess_threats({"recent_incidents": ["incident-1", "incident-2"]})
        types = [t.threat_type for t in threats]
        assert "elevated_risk_period" in types

    def test_recent_incidents_count_in_description(self):
        assessor = self._assessor()
        threats = assessor.assess_threats({"recent_incidents": ["a", "b", "c"]})
        elevated = [t for t in threats if t.threat_type == "elevated_risk_period"]
        assert len(elevated) == 1
        assert "3" in elevated[0].description

    def test_high_social_media_exposure_yields_osint_risk(self):
        assessor = self._assessor()
        threats = assessor.assess_threats({"social_media_exposure": "high"})
        types = [t.threat_type for t in threats]
        assert "osint_risk" in types

    def test_osint_risk_severity_is_medium(self):
        assessor = self._assessor()
        threats = assessor.assess_threats({"social_media_exposure": "high"})
        osint = [t for t in threats if t.threat_type == "osint_risk"]
        assert osint[0].severity == "medium"

    def test_all_five_conditions_yields_five_threats(self):
        assessor = self._assessor()
        context = {
            "training_level": "none",
            "access_level": "admin",
            "environment": "remote",
            "recent_incidents": ["inc-1"],
            "social_media_exposure": "high",
        }
        threats = assessor.assess_threats(context)
        assert len(threats) == 5

    def test_threat_ids_are_sequential(self):
        assessor = self._assessor()
        context = {
            "training_level": "low",
            "access_level": "admin",
        }
        threats = assessor.assess_threats(context)
        assert threats[0].threat_id == "CT-001"
        assert threats[1].threat_id == "CT-002"

    def test_empty_context_yields_no_threats(self):
        assessor = self._assessor()
        threats = assessor.assess_threats({})
        assert threats == []

    def test_module_level_assess_cognitive_threats_function(self):
        from codomyrmex.security.cognitive.cognitive_threat_assessment import (
            assess_cognitive_threats,
        )
        result = assess_cognitive_threats({"access_level": "admin"})
        assert result["critical_count"] == 1
        assert result["total_threats"] == 1


# ---------------------------------------------------------------------------
# CognitiveThreatAssessor — branch coverage for evaluate_human_factors()
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestEvaluateHumanFactorsBranches:
    """Cover risk score and recommendation branches in evaluate_human_factors()."""

    def _assessor(self):
        from codomyrmex.security.cognitive.cognitive_threat_assessment import (
            CognitiveThreatAssessor,
        )
        return CognitiveThreatAssessor()

    def test_high_stress_increases_risk_score(self):
        assessor = self._assessor()
        result = assessor.evaluate_human_factors({"stress_level": "high"})
        assert result["risk_score"] >= 0.2

    def test_very_high_stress_increases_risk_score(self):
        assessor = self._assessor()
        result = assessor.evaluate_human_factors({"stress_level": "very_high"})
        assert result["risk_score"] >= 0.2

    def test_high_risk_tolerance_increases_risk_score(self):
        assessor = self._assessor()
        result = assessor.evaluate_human_factors({"risk_tolerance": "high"})
        assert result["risk_score"] >= 0.2

    def test_privileged_access_increases_risk_score(self):
        assessor = self._assessor()
        result = assessor.evaluate_human_factors({"access_level": "admin"})
        assert result["risk_score"] >= 0.15

    def test_stress_recommendation_added(self):
        assessor = self._assessor()
        result = assessor.evaluate_human_factors({"stress_level": "high"})
        recs = result["recommendations"]
        assert any("workload" in r.lower() or "stress" in r.lower() for r in recs)

    def test_risk_tolerance_recommendation_added(self):
        assessor = self._assessor()
        result = assessor.evaluate_human_factors({"risk_tolerance": "high"})
        recs = result["recommendations"]
        assert any("risk" in r.lower() for r in recs)

    def test_privileged_recommendation_added(self):
        assessor = self._assessor()
        result = assessor.evaluate_human_factors({"access_level": "privileged"})
        recs = result["recommendations"]
        assert any("verification" in r.lower() or "privileged" in r.lower() for r in recs)

    def test_no_risk_factors_yields_default_recommendation(self):
        assessor = self._assessor()
        result = assessor.evaluate_human_factors({})
        recs = result["recommendations"]
        assert len(recs) >= 1
        assert any("awareness" in r.lower() or "refresher" in r.lower() for r in recs)

    def test_risk_score_capped_at_one(self):
        assessor = self._assessor()
        # All risk factors active
        result = assessor.evaluate_human_factors({
            "training_level": "none",
            "stress_level": "very_high",
            "risk_tolerance": "very_high",
            "access_level": "admin",
        })
        assert result["risk_score"] <= 1.0

    def test_module_level_evaluate_human_factors_function(self):
        from codomyrmex.security.cognitive.cognitive_threat_assessment import (
            evaluate_human_factors,
        )
        result = evaluate_human_factors({"stress_level": "high"})
        assert "risk_score" in result
        assert result["risk_score"] >= 0.2
