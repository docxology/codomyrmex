"""
Unit tests for the security.cognitive module.

Tests cognitive security operations including social engineering detection,
phishing analysis, awareness training, cognitive threat assessment, and behavior analysis.
"""

import pytest

from codomyrmex.security.cognitive import (
    detect_social_engineering,
    analyze_communication,
    SocialEngineeringDetector,
    analyze_email,
    detect_phishing_attempt,
    PhishingAnalyzer,
    create_training_module,
    assess_training_effectiveness,
    AwarenessTrainer,
    assess_cognitive_threats,
    evaluate_human_factors,
    CognitiveThreatAssessor,
    analyze_user_behavior,
    detect_anomalous_behavior,
    BehaviorAnalyzer,
)


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
            difficulty="beginner"
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


class TestCognitiveThreatAssessment:
    """Test cognitive threat assessment."""
    
    def test_cognitive_threat_assessor_initialization(self):
        """Test CognitiveThreatAssessor can be initialized."""
        assessor = CognitiveThreatAssessor()
        assert assessor is not None
    
    def test_assess_cognitive_threats(self):
        """Test assessing cognitive threats."""
        context = {
            "environment": "remote_work",
            "training_level": "low"
        }
        assessment = assess_cognitive_threats(context)
        assert isinstance(assessment, dict)
        assert "total_threats" in assessment
    
    def test_evaluate_human_factors(self):
        """Test evaluating human factors."""
        scenario = {
            "training_level": "intermediate",
            "experience": "high",
            "stress_level": "medium"
        }
        factors = evaluate_human_factors(scenario)
        assert isinstance(factors, dict)
        assert "training_level" in factors
        assert "experience" in factors


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
            "actions": ["sensitive_access"]
        }
        patterns = analyze_user_behavior("user123", behavior_data)
        assert isinstance(patterns, list)
    
    def test_detect_anomalous_behavior(self):
        """Test detecting anomalous behavior."""
        current_behavior = {
            "login_time": "02:00",
            "location": "unusual",
            "actions": ["sensitive_access"]
        }
        anomalies = detect_anomalous_behavior("user123", current_behavior)
        assert isinstance(anomalies, list)

