"""Comprehensive tests for security.theory.threat_modeling — zero-mock.

Covers: ThreatSeverity, ThreatCategory, Threat, ThreatModel, ThreatModelBuilder
(STRIDE + generic), create_threat_model, analyze_threats, prioritize_threats.
"""

import pytest

from codomyrmex.security.theory.threat_modeling import (
    Threat,
    ThreatCategory,
    ThreatModel,
    ThreatModelBuilder,
    ThreatSeverity,
    analyze_threats,
    create_threat_model,
    prioritize_threats,
)

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class TestThreatSeverity:
    def test_values(self):
        assert ThreatSeverity.LOW.value == "low"
        assert ThreatSeverity.MEDIUM.value == "medium"
        assert ThreatSeverity.HIGH.value == "high"
        assert ThreatSeverity.CRITICAL.value == "critical"


class TestThreatCategory:
    def test_values(self):
        assert ThreatCategory.AUTHENTICATION.value == "authentication"
        assert ThreatCategory.INJECTION.value == "injection"
        assert ThreatCategory.DATA_EXPOSURE.value == "data_exposure"
        assert ThreatCategory.NETWORK.value == "network"


# ---------------------------------------------------------------------------
# Threat dataclass
# ---------------------------------------------------------------------------


class TestThreat:
    def test_create_threat(self):
        t = Threat(
            threat_id="T-001",
            threat_type="spoofing",
            description="Identity spoofing via credential theft",
            severity="high",
            mitigation="Implement MFA",
        )
        assert t.threat_id == "T-001"
        assert t.severity == "high"

    def test_default_fields(self):
        t = Threat(
            threat_id="T-002",
            threat_type="tampering",
            description="Data tampering",
            severity="medium",
            mitigation="Use checksums",
        )
        assert t.category == "general"
        assert t.likelihood == "medium"
        assert t.attack_vectors == []
        assert t.detection_methods == []


# ---------------------------------------------------------------------------
# ThreatModel dataclass
# ---------------------------------------------------------------------------


class TestThreatModel:
    def test_create_model(self):
        model = ThreatModel(
            model_id="TM-001",
            system_name="Web API",
            threats=[],
            assets=["user_data", "api_keys"],
            attack_surface=["login_endpoint"],
        )
        assert model.system_name == "Web API"
        assert model.methodology == "STRIDE"

    def test_model_with_threats(self):
        threat = Threat(
            threat_id="T-001",
            threat_type="injection",
            description="SQL injection",
            severity="critical",
            mitigation="Use parameterized queries",
        )
        model = ThreatModel(
            model_id="TM-001",
            system_name="DB Layer",
            threats=[threat],
            assets=["database"],
            attack_surface=["query_endpoint"],
        )
        assert len(model.threats) == 1


# ---------------------------------------------------------------------------
# ThreatModelBuilder
# ---------------------------------------------------------------------------


class TestThreatModelBuilder:
    def test_init_default_stride(self):
        builder = ThreatModelBuilder()
        assert builder.methodology == "STRIDE"

    def test_init_custom_methodology(self):
        builder = ThreatModelBuilder(methodology="DREAD")
        assert builder.methodology == "DREAD"

    def test_create_model_stride(self):
        builder = ThreatModelBuilder(methodology="STRIDE")
        model = builder.create_model(
            system_name="Test System",
            assets=["user_data", "api_keys", "database"],
            attack_surface=["api_endpoint", "admin_panel"],
        )
        assert isinstance(model, ThreatModel)
        assert model.system_name == "Test System"
        assert len(model.threats) > 0  # STRIDE should generate threats

    def test_create_model_with_assumptions(self):
        builder = ThreatModelBuilder()
        model = builder.create_model(
            system_name="Secure App",
            assets=["credentials"],
            attack_surface=["login"],
            assumptions=["Internal network only"],
            constraints=["No cloud deployment"],
        )
        assert "Internal network only" in model.assumptions

    def test_create_model_generic(self):
        builder = ThreatModelBuilder(methodology="generic")
        model = builder.create_model(
            system_name="Generic System",
            assets=["data"],
            attack_surface=["endpoint"],
        )
        assert isinstance(model, ThreatModel)


# ---------------------------------------------------------------------------
# Convenience functions
# ---------------------------------------------------------------------------


class TestConvenienceFunctions:
    def test_create_threat_model_default(self):
        model = create_threat_model(
            system_name="My API",
            assets=["user_data"],
            attack_surface=["rest_api"],
        )
        assert isinstance(model, ThreatModel)
        assert model.system_name == "My API"

    def test_create_threat_model_with_builder(self):
        builder = ThreatModelBuilder(methodology="STRIDE")
        model = create_threat_model(
            system_name="Custom",
            assets=["db"],
            attack_surface=["web"],
            builder=builder,
        )
        assert isinstance(model, ThreatModel)

    def test_analyze_threats(self):
        model = create_threat_model(
            system_name="Test",
            assets=["data"],
            attack_surface=["api"],
        )
        analysis = analyze_threats(model)
        assert isinstance(analysis, dict)
        assert len(analysis) > 0

    def test_prioritize_threats(self):
        model = create_threat_model(
            system_name="Test",
            assets=["data", "keys"],
            attack_surface=["api", "admin"],
        )
        prioritized = prioritize_threats(model)
        assert isinstance(prioritized, list)
        # All returned items should be Threat objects
        for t in prioritized:
            assert isinstance(t, Threat)
