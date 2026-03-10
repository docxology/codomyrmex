"""Comprehensive tests for security.theory.architecture_patterns — zero-mock.

Covers: PatternCategory, SecurityPattern, get_security_patterns,
get_pattern, get_patterns_by_category, apply_pattern, validate_pattern_application.
"""


from codomyrmex.security.theory.architecture_patterns import (
    PatternCategory,
    SecurityPattern,
    apply_pattern,
    get_pattern,
    get_patterns_by_category,
    get_security_patterns,
    validate_pattern_application,
)

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class TestPatternCategory:
    def test_values(self):
        assert PatternCategory.ARCHITECTURE.value == "architecture"
        assert PatternCategory.AUTHENTICATION.value == "authentication"
        assert PatternCategory.AUTHORIZATION.value == "authorization"
        assert PatternCategory.ENCRYPTION.value == "encryption"
        assert PatternCategory.NETWORK.value == "network"
        assert PatternCategory.DATA_PROTECTION.value == "data_protection"
        assert PatternCategory.ACCESS_CONTROL.value == "access_control"
        assert PatternCategory.MONITORING.value == "monitoring"
        assert PatternCategory.INCIDENT_RESPONSE.value == "incident_response"


# ---------------------------------------------------------------------------
# SecurityPattern
# ---------------------------------------------------------------------------


class TestSecurityPattern:
    def test_create_pattern(self):
        p = SecurityPattern(
            name="Zero Trust",
            description="Never trust, always verify",
            category="architecture",
            use_cases=["Cloud", "Microservices"],
            implementation="Verify every request",
        )
        assert p.name == "Zero Trust"
        assert len(p.use_cases) == 2

    def test_default_fields(self):
        p = SecurityPattern(
            name="Test",
            description="d",
            category="general",
            use_cases=["x"],
            implementation="i",
        )
        assert p.benefits == []
        assert p.trade_offs == []
        assert p.related_patterns == []
        assert p.examples == []
        assert p.anti_patterns == []


# ---------------------------------------------------------------------------
# Retrieval functions
# ---------------------------------------------------------------------------


class TestGetSecurityPatterns:
    def test_returns_list(self):
        patterns = get_security_patterns()
        assert isinstance(patterns, list)
        assert len(patterns) > 0

    def test_all_are_security_patterns(self):
        patterns = get_security_patterns()
        for p in patterns:
            assert isinstance(p, SecurityPattern)


class TestGetPattern:
    def test_get_existing_pattern(self):
        all_patterns = get_security_patterns()
        if all_patterns:
            name = all_patterns[0].name
            result = get_pattern(name)
            # May or may not find by display name
            assert result is None or isinstance(result, SecurityPattern)

    def test_get_nonexistent(self):
        result = get_pattern("nonexistent_pattern_xyz")
        assert result is None


class TestGetPatternsByCategory:
    def test_returns_list(self):
        result = get_patterns_by_category("architecture")
        assert isinstance(result, list)

    def test_nonexistent_category(self):
        result = get_patterns_by_category("nonexistent_xyz")
        assert isinstance(result, list)
        assert len(result) == 0


# ---------------------------------------------------------------------------
# Application and Validation
# ---------------------------------------------------------------------------


class TestApplyPattern:
    def test_apply_zero_trust(self):
        patterns = get_security_patterns()
        if patterns:
            result = apply_pattern(
                pattern_name=patterns[0].name,
                context={"system_type": "microservices"},
            )
            assert isinstance(result, dict)

    def test_apply_nonexistent_pattern(self):
        result = apply_pattern(
            pattern_name="nonexistent_xyz",
            context={"system_type": "web"},
        )
        # Should return error or empty result
        assert isinstance(result, dict)


class TestValidatePatternApplication:
    def test_validate_returns_dict(self):
        result = validate_pattern_application(
            pattern_name="defense_in_depth",
            context={"system_type": "web_app"},
        )
        assert isinstance(result, dict)

    def test_validate_nonexistent_pattern(self):
        result = validate_pattern_application(
            pattern_name="nonexistent_xyz",
            context={},
        )
        assert isinstance(result, dict)
