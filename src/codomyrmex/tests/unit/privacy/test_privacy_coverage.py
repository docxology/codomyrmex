"""Zero-mock tests for privacy.privacy module.

Covers PII detection, masking functions, differential privacy,
and the Privacy class with real data processing.
"""

import pytest

from codomyrmex.privacy.privacy import (
    PIIMatch,
    Privacy,
    PrivacyRule,
    add_laplace_noise,
    create_privacy,
    detect_pii,
    dp_count,
    dp_mean,
    laplace_noise,
    mask_email,
    mask_hash,
    mask_partial,
    mask_redact,
)


class TestDetectPii:
    """Tests for detect_pii function."""

    def test_detects_email(self):
        matches = detect_pii("Contact us at alice@example.com for help.")
        pii_types = {m.pii_type for m in matches}
        assert "email" in pii_types

    def test_detects_phone_number(self):
        matches = detect_pii("Call us at 555-867-5309.")
        pii_types = {m.pii_type for m in matches}
        assert "phone" in pii_types

    def test_detects_ssn(self):
        matches = detect_pii("SSN: 123-45-6789")
        pii_types = {m.pii_type for m in matches}
        assert "ssn" in pii_types

    def test_detects_ipv4(self):
        matches = detect_pii("Server at 192.168.1.100 is down.")
        pii_types = {m.pii_type for m in matches}
        assert "ipv4" in pii_types

    def test_no_pii_in_clean_text(self):
        matches = detect_pii("The quick brown fox jumps over the lazy dog.")
        assert len(matches) == 0

    def test_field_name_included_in_match(self):
        matches = detect_pii("alice@example.com", field_name="contact_email")
        assert matches[0].field == "contact_email"

    def test_match_contains_value(self):
        matches = detect_pii("Email: bob@test.org is here.")
        email_matches = [m for m in matches if m.pii_type == "email"]
        assert len(email_matches) >= 1
        assert "bob@test.org" in email_matches[0].value

    def test_match_positions(self):
        text = "Email: alice@example.com"
        matches = detect_pii(text)
        email_matches = [m for m in matches if m.pii_type == "email"]
        assert len(email_matches) >= 1
        m = email_matches[0]
        assert text[m.start : m.end] == m.value

    def test_multiple_pii_in_text(self):
        text = "Contact: alice@test.com, phone: 555-123-4567"
        matches = detect_pii(text)
        types = {m.pii_type for m in matches}
        assert "email" in types
        assert "phone" in types

    def test_empty_text_returns_no_matches(self):
        matches = detect_pii("")
        assert matches == []


class TestMaskHash:
    """Tests for mask_hash function."""

    def test_returns_hex_string(self):
        result = mask_hash("alice@example.com")
        assert all(c in "0123456789abcdef" for c in result)

    def test_sha256_length(self):
        result = mask_hash("test", algorithm="sha256")
        assert len(result) == 64

    def test_md5_length(self):
        result = mask_hash("test", algorithm="md5")
        assert len(result) == 32

    def test_sha1_length(self):
        result = mask_hash("test", algorithm="sha1")
        assert len(result) == 40

    def test_deterministic_for_same_input(self):
        r1 = mask_hash("same_input")
        r2 = mask_hash("same_input")
        assert r1 == r2

    def test_different_inputs_differ(self):
        r1 = mask_hash("input_a")
        r2 = mask_hash("input_b")
        assert r1 != r2

    def test_default_algorithm_is_sha256(self):
        result = mask_hash("test")
        assert len(result) == 64


class TestMaskRedact:
    """Tests for mask_redact function."""

    def test_default_replacement(self):
        result = mask_redact("sensitive_value")
        assert result == "***"

    def test_custom_replacement(self):
        result = mask_redact("value", replacement="REDACTED")
        assert result == "REDACTED"

    def test_empty_string(self):
        result = mask_redact("")
        assert result == "***"


class TestMaskPartial:
    """Tests for mask_partial function."""

    def test_standard_masking(self):
        result = mask_partial("1234567890", visible_chars=4)
        assert result == "******7890"
        assert len(result) == 10

    def test_value_shorter_than_visible_returned_as_is(self):
        result = mask_partial("123", visible_chars=4)
        assert result == "123"

    def test_value_exactly_visible_chars_returned_as_is(self):
        result = mask_partial("1234", visible_chars=4)
        assert result == "1234"

    def test_custom_mask_char(self):
        result = mask_partial("ABCDEFGH", visible_chars=3, mask_char="X")
        assert result == "XXXXXFGH"

    def test_single_visible_char(self):
        result = mask_partial("password", visible_chars=1)
        assert result.endswith("d")
        assert result.startswith("*")


class TestMaskEmail:
    """Tests for mask_email function."""

    def test_standard_email_masked(self):
        result = mask_email("alice@example.com")
        assert result.startswith("a")
        assert "@example.com" in result
        assert "****" in result

    def test_no_at_sign_redacted(self):
        result = mask_email("not_an_email")
        assert result == "***"

    def test_single_char_local_preserved(self):
        result = mask_email("a@example.com")
        assert "@example.com" in result
        assert result.startswith("a")

    def test_domain_always_preserved(self):
        result = mask_email("longusername@company.org")
        assert "@company.org" in result

    def test_masking_length_preserved(self):
        email = "alice@example.com"
        result = mask_email(email)
        # local part: "alice" -> "a****"
        local_original = "alice"
        local_result = result.split("@")[0]
        assert len(local_result) == len(local_original)


class TestLaplaceNoise:
    """Tests for laplace_noise function."""

    def test_returns_float(self):
        noise = laplace_noise(1.0)
        assert isinstance(noise, float)

    def test_invalid_epsilon_raises(self):
        with pytest.raises(ValueError, match="Epsilon must be positive"):
            laplace_noise(0.0)

    def test_negative_epsilon_raises(self):
        with pytest.raises(ValueError, match="Epsilon must be positive"):
            laplace_noise(-1.0)

    def test_returns_value_in_range(self):
        # Since implementation uses uniform approx: uniform(-0.5, 0.5)
        for _ in range(20):
            noise = laplace_noise(1.0)
            assert -0.5 <= noise <= 0.5


class TestAddLaplaceNoise:
    """Tests for add_laplace_noise function."""

    def test_returns_float(self):
        result = add_laplace_noise(100.0, epsilon=1.0)
        assert isinstance(result, float)

    def test_invalid_epsilon_raises(self):
        with pytest.raises(ValueError, match="Epsilon must be positive"):
            add_laplace_noise(10.0, epsilon=0.0)

    def test_noised_value_differs_from_true(self):
        # With probability ~1, noise will perturb the value
        results = [add_laplace_noise(50.0, epsilon=1.0) for _ in range(10)]
        assert not all(r == 50.0 for r in results)

    def test_large_epsilon_small_noise(self):
        # Very large epsilon -> tiny noise (high privacy budget = less noise)
        results = [add_laplace_noise(1000.0, epsilon=100.0) for _ in range(20)]
        for r in results:
            assert abs(r - 1000.0) < 100.0  # loose bound


class TestDpMean:
    """Tests for dp_mean function."""

    def test_empty_list_returns_zero(self):
        result = dp_mean([], epsilon=1.0, lower=0.0, upper=100.0)
        assert result == 0.0

    def test_returns_float(self):
        result = dp_mean([10.0, 20.0, 30.0], epsilon=1.0, lower=0.0, upper=100.0)
        assert isinstance(result, float)

    def test_noised_mean_is_reasonable(self):
        values = [50.0] * 100
        result = dp_mean(values, epsilon=1.0, lower=0.0, upper=100.0)
        # With large n, sensitivity is low, result should be close to 50
        assert 0.0 <= result <= 100.0


class TestDpCount:
    """Tests for dp_count function."""

    def test_returns_float(self):
        result = dp_count(100, epsilon=1.0)
        assert isinstance(result, float)

    def test_noised_count_is_reasonable(self):
        # With epsilon=10 (high), noise is small
        result = dp_count(100, epsilon=10.0)
        # Very loose bound to account for noise
        assert 50.0 <= result <= 150.0

    def test_zero_count(self):
        result = dp_count(0, epsilon=1.0)
        assert isinstance(result, float)


class TestPrivacyClass:
    """Tests for the Privacy class."""

    def test_init_no_config(self):
        p = Privacy()
        assert p.config == {}
        assert p._rules == {}

    def test_init_with_config(self):
        p = Privacy(config={"key": "value"})
        assert p.config == {"key": "value"}

    def test_add_rule(self):
        p = Privacy()
        p.add_rule(PrivacyRule("email", "email"))
        assert "email" in p._rules

    def test_process_hash_strategy(self):
        p = Privacy()
        p.add_rule(PrivacyRule("name", "hash"))
        result = p.process({"name": "Alice", "age": 30})
        assert result["name"] != "Alice"
        assert len(result["name"]) == 64  # sha256 hex
        assert result["age"] == 30

    def test_process_redact_strategy(self):
        p = Privacy()
        p.add_rule(PrivacyRule("ssn", "redact"))
        result = p.process({"ssn": "123-45-6789", "name": "Bob"})
        assert result["ssn"] == "***"
        assert result["name"] == "Bob"

    def test_process_redact_custom_replacement(self):
        p = Privacy()
        p.add_rule(PrivacyRule("secret", "redact", params={"replacement": "REDACTED"}))
        result = p.process({"secret": "my_secret_value"})
        assert result["secret"] == "REDACTED"

    def test_process_partial_strategy(self):
        p = Privacy()
        p.add_rule(PrivacyRule("card", "partial"))
        result = p.process({"card": "4111111111111111"})
        assert result["card"].endswith("1111")
        assert "*" in result["card"]

    def test_process_email_strategy(self):
        p = Privacy()
        p.add_rule(PrivacyRule("email", "email"))
        result = p.process({"email": "alice@example.com"})
        assert "@example.com" in result["email"]
        assert result["email"].startswith("a")

    def test_process_noise_strategy(self):
        p = Privacy()
        p.add_rule(PrivacyRule("salary", "noise", params={"epsilon": 1.0}))
        result = p.process({"salary": 75000})
        assert isinstance(result["salary"], float)

    def test_process_unknown_strategy_warning(self):
        p = Privacy()
        p.add_rule(PrivacyRule("field", "unknown_strategy"))
        # Should log a warning but not raise
        result = p.process({"field": "value"})
        # Field is unchanged since strategy unknown
        assert result["field"] == "value"

    def test_process_missing_field_skipped(self):
        p = Privacy()
        p.add_rule(PrivacyRule("email", "redact"))
        result = p.process({"name": "Alice"})
        # email rule applied but email field absent
        assert result == {"name": "Alice"}

    def test_process_returns_copy_not_mutation(self):
        p = Privacy()
        p.add_rule(PrivacyRule("name", "redact"))
        original = {"name": "Alice", "age": 30}
        result = p.process(original)
        assert original["name"] == "Alice"  # original unchanged
        assert result["name"] == "***"

    def test_process_multiple_rules(self):
        p = Privacy()
        p.add_rule(PrivacyRule("email", "email"))
        p.add_rule(PrivacyRule("ssn", "redact"))
        p.add_rule(PrivacyRule("name", "hash"))
        data = {"email": "bob@test.org", "ssn": "123-45-6789", "name": "Bob"}
        result = p.process(data)
        assert "@test.org" in result["email"]
        assert result["ssn"] == "***"
        assert len(result["name"]) == 64

    def test_scan_pii_finds_email(self):
        p = Privacy()
        data = {"contact": "Email me at user@example.com please"}
        matches = p.scan_pii(data)
        pii_types = {m.pii_type for m in matches}
        assert "email" in pii_types

    def test_scan_pii_skips_non_strings(self):
        p = Privacy()
        data = {"count": 42, "flag": True, "text": "Call 555-867-5309"}
        matches = p.scan_pii(data)
        # Only text field scanned
        pii_types = {m.pii_type for m in matches}
        assert "phone" in pii_types

    def test_scan_pii_empty_data(self):
        p = Privacy()
        matches = p.scan_pii({})
        assert matches == []

    def test_create_privacy_factory(self):
        p = create_privacy({"timeout": 30})
        assert isinstance(p, Privacy)
        assert p.config == {"timeout": 30}

    def test_create_privacy_no_config(self):
        p = create_privacy()
        assert isinstance(p, Privacy)
        assert p.config == {}


class TestPrivacyRule:
    """Tests for PrivacyRule dataclass."""

    def test_basic_construction(self):
        rule = PrivacyRule(field="email", strategy="redact")
        assert rule.field == "email"
        assert rule.strategy == "redact"
        assert rule.params == {}

    def test_with_params(self):
        rule = PrivacyRule(field="salary", strategy="noise", params={"epsilon": 0.5})
        assert rule.params["epsilon"] == 0.5


class TestPIIMatch:
    """Tests for PIIMatch dataclass."""

    def test_construction(self):
        match = PIIMatch(
            field="email", pii_type="email", value="a@b.com", start=0, end=7
        )
        assert match.field == "email"
        assert match.pii_type == "email"
        assert match.value == "a@b.com"
        assert match.start == 0
        assert match.end == 7
