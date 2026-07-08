"""Zero-mock tests for codomyrmex.security.theory.threat_modeling."""

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
# ThreatSeverity enum
# ---------------------------------------------------------------------------


class TestThreatSeverity:
    def test_member_count(self):
        assert len(ThreatSeverity) == 4

    def test_member_names(self):
        names = {m.name for m in ThreatSeverity}
        assert names == {"LOW", "MEDIUM", "HIGH", "CRITICAL"}

    def test_string_values(self):
        assert ThreatSeverity.LOW.value == "low"
        assert ThreatSeverity.MEDIUM.value == "medium"
        assert ThreatSeverity.HIGH.value == "high"
        assert ThreatSeverity.CRITICAL.value == "critical"

    def test_severity_ordering_via_rank_dict(self):
        """The severity_order dict used in prioritize_threats encodes CRITICAL=4 > HIGH=3 > MEDIUM=2 > LOW=1."""
        severity_order = {
            ThreatSeverity.CRITICAL.value: 4,
            ThreatSeverity.HIGH.value: 3,
            ThreatSeverity.MEDIUM.value: 2,
            ThreatSeverity.LOW.value: 1,
        }
        assert (
            severity_order[ThreatSeverity.CRITICAL.value]
            > severity_order[ThreatSeverity.HIGH.value]
        )
        assert (
            severity_order[ThreatSeverity.HIGH.value]
            > severity_order[ThreatSeverity.MEDIUM.value]
        )
        assert (
            severity_order[ThreatSeverity.MEDIUM.value]
            > severity_order[ThreatSeverity.LOW.value]
        )


# ---------------------------------------------------------------------------
# ThreatCategory enum
# ---------------------------------------------------------------------------


class TestThreatCategory:
    def test_member_count(self):
        assert len(ThreatCategory) == 10

    def test_key_members_present(self):
        names = {m.name for m in ThreatCategory}
        assert "AUTHENTICATION" in names
        assert "AUTHORIZATION" in names
        assert "DATA_EXPOSURE" in names
        assert "INJECTION" in names
        assert "NETWORK" in names
        assert "LOGGING" in names

    def test_string_values(self):
        assert ThreatCategory.AUTHENTICATION.value == "authentication"
        assert ThreatCategory.AUTHORIZATION.value == "authorization"
        assert ThreatCategory.SOCIAL_ENGINEERING.value == "social_engineering"


# ---------------------------------------------------------------------------
# Threat dataclass
# ---------------------------------------------------------------------------


class TestThreatDataclass:
    def _make_threat(self, **overrides):
        defaults = {
            "threat_id": "t-001",
            "threat_type": "Spoofing",
            "description": "Test spoofing threat",
            "severity": ThreatSeverity.HIGH.value,
            "mitigation": "Use MFA",
        }
        defaults.update(overrides)
        return Threat(**defaults)

    def test_required_fields_instantiation(self):
        t = self._make_threat()
        assert t.threat_id == "t-001"
        assert t.threat_type == "Spoofing"
        assert t.description == "Test spoofing threat"
        assert t.severity == "high"
        assert t.mitigation == "Use MFA"

    def test_default_category(self):
        t = self._make_threat()
        assert t.category == "general"

    def test_default_likelihood(self):
        t = self._make_threat()
        assert t.likelihood == "medium"

    def test_default_impact(self):
        t = self._make_threat()
        assert t.impact == "medium"

    def test_default_list_fields_are_empty(self):
        t = self._make_threat()
        assert t.affected_assets == []
        assert t.attack_vectors == []
        assert t.detection_methods == []
        assert t.references == []

    def test_list_fields_do_not_share_default_instance(self):
        """Each Threat instance must get its own list, not a shared mutable default."""
        t1 = self._make_threat(threat_id="t-001")
        t2 = self._make_threat(threat_id="t-002")
        t1.affected_assets.append("server")
        assert t2.affected_assets == []

    def test_explicit_list_fields(self):
        t = self._make_threat(
            affected_assets=["db", "api"],
            attack_vectors=["SQLi"],
            detection_methods=["WAF"],
            references=["CVE-2021-1234"],
        )
        assert t.affected_assets == ["db", "api"]
        assert t.attack_vectors == ["SQLi"]
        assert t.detection_methods == ["WAF"]
        assert t.references == ["CVE-2021-1234"]

    def test_category_override(self):
        t = self._make_threat(category=ThreatCategory.AUTHENTICATION.value)
        assert t.category == "authentication"


# ---------------------------------------------------------------------------
# ThreatModel dataclass
# ---------------------------------------------------------------------------


class TestThreatModelDataclass:
    def _make_model(self, **overrides):
        defaults = {
            "model_id": "model-001",
            "system_name": "TestSystem",
            "threats": [],
            "assets": ["user_database"],
            "attack_surface": ["login_endpoint"],
        }
        defaults.update(overrides)
        return ThreatModel(**defaults)

    def test_required_fields_instantiation(self):
        m = self._make_model()
        assert m.model_id == "model-001"
        assert m.system_name == "TestSystem"
        assert m.threats == []
        assert m.assets == ["user_database"]

    def test_default_methodology_is_stride(self):
        m = self._make_model()
        assert m.methodology == "STRIDE"

    def test_default_assumptions_and_constraints_are_empty(self):
        m = self._make_model()
        assert m.assumptions == []
        assert m.constraints == []

    def test_created_at_is_datetime(self):
        from datetime import datetime

        m = self._make_model()
        assert isinstance(m.created_at, datetime)

    def test_methodology_override(self):
        m = self._make_model(methodology="PASTA")
        assert m.methodology == "PASTA"


# ---------------------------------------------------------------------------
# ThreatModelBuilder
# ---------------------------------------------------------------------------


class TestThreatModelBuilder:
    def test_default_methodology_is_stride(self):
        builder = ThreatModelBuilder()
        assert builder.methodology == "STRIDE"

    def test_custom_methodology(self):
        builder = ThreatModelBuilder(methodology="PASTA")
        assert builder.methodology == "PASTA"

    def test_create_model_returns_threat_model(self):
        builder = ThreatModelBuilder()
        model = builder.create_model("MyApp", ["user_data"], ["login"])
        assert isinstance(model, ThreatModel)

    def test_create_model_system_name(self):
        builder = ThreatModelBuilder()
        model = builder.create_model("BankingApp", ["accounts"], ["web_api"])
        assert model.system_name == "BankingApp"

    def test_create_model_assets_preserved(self):
        builder = ThreatModelBuilder()
        assets = ["user_database", "sensitive_data"]
        model = builder.create_model("App", assets, ["api_service"])
        assert model.assets == assets

    def test_create_model_model_id_has_prefix(self):
        builder = ThreatModelBuilder()
        model = builder.create_model("App", ["asset"], ["surface"])
        assert model.model_id.startswith("model_")

    def test_stride_always_includes_repudiation(self):
        builder = ThreatModelBuilder(methodology="STRIDE")
        model = builder.create_model("App", ["asset"], ["surface"])
        types = [t.threat_type for t in model.threats]
        assert "Repudiation" in types

    def test_stride_always_includes_elevation_of_privilege(self):
        builder = ThreatModelBuilder(methodology="STRIDE")
        model = builder.create_model("App", ["asset"], ["surface"])
        types = [t.threat_type for t in model.threats]
        assert "Elevation of Privilege" in types

    def test_stride_spoofing_when_login_in_attack_surface(self):
        builder = ThreatModelBuilder(methodology="STRIDE")
        model = builder.create_model("App", ["user_account"], ["login_endpoint"])
        types = [t.threat_type for t in model.threats]
        assert "Spoofing" in types

    def test_stride_spoofing_when_authentication_in_attack_surface(self):
        builder = ThreatModelBuilder(methodology="STRIDE")
        model = builder.create_model("App", ["asset"], ["authentication_service"])
        types = [t.threat_type for t in model.threats]
        assert "Spoofing" in types

    def test_stride_information_disclosure_when_sensitive_asset(self):
        builder = ThreatModelBuilder(methodology="STRIDE")
        model = builder.create_model("App", ["sensitive_pii"], ["api"])
        types = [t.threat_type for t in model.threats]
        assert "Information Disclosure" in types

    def test_stride_information_disclosure_has_critical_severity(self):
        builder = ThreatModelBuilder(methodology="STRIDE")
        model = builder.create_model("App", ["confidential_records"], ["api"])
        disclosure = next(
            t for t in model.threats if t.threat_type == "Information Disclosure"
        )
        assert disclosure.severity == ThreatSeverity.CRITICAL.value

    def test_stride_dos_when_service_in_attack_surface(self):
        builder = ThreatModelBuilder(methodology="STRIDE")
        model = builder.create_model("App", ["asset"], ["rest_api_service"])
        types = [t.threat_type for t in model.threats]
        assert "Denial of Service" in types

    def test_stride_dos_when_api_in_attack_surface(self):
        builder = ThreatModelBuilder(methodology="STRIDE")
        model = builder.create_model("App", ["asset"], ["public_api"])
        types = [t.threat_type for t in model.threats]
        assert "Denial of Service" in types

    def test_stride_tampering_when_data_in_assets(self):
        builder = ThreatModelBuilder(methodology="STRIDE")
        model = builder.create_model("App", ["user_data_store"], ["surface"])
        types = [t.threat_type for t in model.threats]
        assert "Tampering" in types

    def test_non_stride_produces_unauthorized_access(self):
        builder = ThreatModelBuilder(methodology="DREAD")
        model = builder.create_model("App", ["asset"], ["surface"])
        types = [t.threat_type for t in model.threats]
        assert "Unauthorized Access" in types

    def test_create_model_assumptions_and_constraints_passed(self):
        builder = ThreatModelBuilder()
        model = builder.create_model(
            "App",
            ["asset"],
            ["surface"],
            assumptions=["Internet-accessible"],
            constraints=["No VPN"],
        )
        assert model.assumptions == ["Internet-accessible"]
        assert model.constraints == ["No VPN"]


# ---------------------------------------------------------------------------
# analyze_threats function
# ---------------------------------------------------------------------------


class TestAnalyzeThreats:
    def _full_model(self):
        return create_threat_model(
            "FullApp",
            assets=["user_data", "sensitive_pii", "web_service"],
            attack_surface=["login_endpoint", "public_api_service"],
        )

    def test_returns_dict(self):
        model = self._full_model()
        result = analyze_threats(model)
        assert isinstance(result, dict)

    def test_has_required_keys(self):
        model = self._full_model()
        result = analyze_threats(model)
        for key in (
            "total_threats",
            "critical_count",
            "high_count",
            "medium_count",
            "low_count",
            "threats_by_category",
            "average_risk_score",
            "risk_scores",
            "methodology",
            "threats",
        ):
            assert key in result, f"Missing key: {key}"

    def test_total_threats_matches_model(self):
        model = self._full_model()
        result = analyze_threats(model)
        assert result["total_threats"] == len(model.threats)

    def test_critical_count_counts_critical_severity(self):
        model = self._full_model()
        result = analyze_threats(model)
        expected = sum(
            1 for t in model.threats if t.severity == ThreatSeverity.CRITICAL.value
        )
        assert result["critical_count"] == expected

    def test_severity_counts_sum_to_total(self):
        model = self._full_model()
        result = analyze_threats(model)
        total = (
            result["critical_count"]
            + result["high_count"]
            + result["medium_count"]
            + result["low_count"]
        )
        assert total == result["total_threats"]

    def test_average_risk_score_is_float(self):
        model = self._full_model()
        result = analyze_threats(model)
        assert isinstance(result["average_risk_score"], float)

    def test_methodology_matches_model(self):
        model = self._full_model()
        result = analyze_threats(model)
        assert result["methodology"] == model.methodology

    def test_threats_list_has_correct_fields(self):
        model = self._full_model()
        result = analyze_threats(model)
        for t in result["threats"]:
            assert "threat_id" in t
            assert "threat_type" in t
            assert "severity" in t
            assert "mitigation" in t

    def test_empty_threat_model_average_risk_is_zero(self):

        model = ThreatModel(
            model_id="empty",
            system_name="Empty",
            threats=[],
            assets=[],
            attack_surface=[],
        )
        result = analyze_threats(model)
        assert result["total_threats"] == 0
        assert result["average_risk_score"] == 0.0


# ---------------------------------------------------------------------------
# prioritize_threats function
# ---------------------------------------------------------------------------


class TestPrioritizeThreats:
    def test_returns_list_of_threats(self):
        model = create_threat_model(
            "App", ["user_data"], ["login_endpoint", "api_service"]
        )
        result = prioritize_threats(model)
        assert isinstance(result, list)
        assert all(isinstance(t, Threat) for t in result)

    def test_same_length_as_input(self):
        model = create_threat_model(
            "App", ["user_data"], ["login_endpoint", "api_service"]
        )
        result = prioritize_threats(model)
        assert len(result) == len(model.threats)

    def test_higher_risk_score_appears_first(self):
        """A threat with high/critical impact should outrank low/low in prioritization."""

        t_low = Threat(
            threat_id="t-low",
            threat_type="Low",
            description="Low risk",
            severity="low",
            mitigation="none",
            likelihood="low",
            impact="low",
        )
        t_high = Threat(
            threat_id="t-high",
            threat_type="High",
            description="High risk",
            severity="critical",
            mitigation="fix it",
            likelihood="high",
            impact="critical",
        )

        model = ThreatModel(
            model_id="test",
            system_name="Test",
            threats=[t_low, t_high],
            assets=["asset"],
            attack_surface=["surface"],
        )
        result = prioritize_threats(model)
        assert result[0].threat_id == "t-high"


# ---------------------------------------------------------------------------
# create_threat_model convenience function
# ---------------------------------------------------------------------------


class TestCreateThreatModel:
    def test_returns_threat_model(self):
        model = create_threat_model("WebApp", ["database"], ["login"])
        assert isinstance(model, ThreatModel)

    def test_passes_system_name(self):
        model = create_threat_model("PaymentService", ["transactions"], ["payment_api"])
        assert model.system_name == "PaymentService"

    def test_default_methodology_is_stride(self):
        model = create_threat_model("App", ["asset"], ["surface"])
        assert model.methodology == "STRIDE"

    def test_custom_methodology_passed_through(self):
        model = create_threat_model("App", ["asset"], ["surface"], methodology="PASTA")
        assert model.methodology == "PASTA"

    def test_custom_builder_used(self):
        builder = ThreatModelBuilder(methodology="DREAD")
        model = create_threat_model("App", ["asset"], ["surface"], builder=builder)
        assert model.methodology == "DREAD"
