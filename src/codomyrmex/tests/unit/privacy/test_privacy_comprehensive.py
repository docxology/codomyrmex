"""Comprehensive zero-mock tests for privacy.privacy module.

Covers: PIIMatch, detect_pii, mask_hash, mask_redact, mask_partial,
mask_email, laplace_noise, add_laplace_noise, dp_mean, dp_count,
PrivacyRule, Privacy, create_privacy.

Zero-mock policy: no unittest.mock, no MagicMock, no monkeypatch.
"""

import hashlib

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

# ==============================================================================
# PIIMatch Dataclass
# ==============================================================================


@pytest.mark.unit
class TestPIIMatch:
    """Tests for the PIIMatch dataclass."""

    def test_piimatch_creation(self):
        """PIIMatch stores all fields correctly."""
        m = PIIMatch(field="email_field", pii_type="email", value="a@b.com", start=5, end=12)
        assert m.field == "email_field"
        assert m.pii_type == "email"
        assert m.value == "a@b.com"
        assert m.start == 5
        assert m.end == 12

    def test_piimatch_equality(self):
        """Two PIIMatch with same data are equal (dataclass default)."""
        a = PIIMatch(field="f", pii_type="email", value="x@y.com", start=0, end=7)
        b = PIIMatch(field="f", pii_type="email", value="x@y.com", start=0, end=7)
        assert a == b

    def test_piimatch_inequality(self):
        """PIIMatch with different data are not equal."""
        a = PIIMatch(field="f", pii_type="email", value="x@y.com", start=0, end=7)
        b = PIIMatch(field="f", pii_type="phone", value="5551234567", start=0, end=10)
        assert a != b


# ==============================================================================
# detect_pii
# ==============================================================================


@pytest.mark.unit
class TestDetectPII:
    """Tests for the detect_pii function."""

    def test_detect_email(self):
        """Detects email addresses."""
        matches = detect_pii("Contact alice@example.com today")
        types = {m.pii_type for m in matches}
        assert "email" in types
        email_match = next(m for m in matches if m.pii_type == "email")
        assert email_match.value == "alice@example.com"

    def test_detect_phone_with_dashes(self):
        """Detects phone numbers with dashes."""
        matches = detect_pii("Call 555-123-4567")
        types = {m.pii_type for m in matches}
        assert "phone" in types

    def test_detect_phone_with_dots(self):
        """Detects phone numbers with dots."""
        matches = detect_pii("Call 555.123.4567")
        types = {m.pii_type for m in matches}
        assert "phone" in types

    def test_detect_phone_plain(self):
        """Detects phone numbers without separators."""
        matches = detect_pii("Call 5551234567")
        types = {m.pii_type for m in matches}
        assert "phone" in types

    def test_detect_ssn(self):
        """Detects social security numbers."""
        matches = detect_pii("SSN: 123-45-6789")
        types = {m.pii_type for m in matches}
        assert "ssn" in types
        ssn_match = next(m for m in matches if m.pii_type == "ssn")
        assert ssn_match.value == "123-45-6789"

    def test_detect_credit_card_plain(self):
        """Detects credit card numbers without separators."""
        matches = detect_pii("Card: 4111111111111111")
        types = {m.pii_type for m in matches}
        assert "credit_card" in types

    def test_detect_credit_card_with_dashes(self):
        """Detects credit card numbers with dashes."""
        matches = detect_pii("Card: 4111-1111-1111-1111")
        types = {m.pii_type for m in matches}
        assert "credit_card" in types

    def test_detect_credit_card_with_spaces(self):
        """Detects credit card numbers with spaces."""
        matches = detect_pii("Card: 4111 1111 1111 1111")
        types = {m.pii_type for m in matches}
        assert "credit_card" in types

    def test_detect_ipv4(self):
        """Detects IPv4 addresses."""
        matches = detect_pii("Server at 192.168.1.100")
        types = {m.pii_type for m in matches}
        assert "ipv4" in types
        ip_match = next(m for m in matches if m.pii_type == "ipv4")
        assert ip_match.value == "192.168.1.100"

    def test_detect_multiple_types(self):
        """Detects multiple PII types in the same string."""
        text = "Email alice@example.com, SSN 123-45-6789, IP 10.0.0.1"
        matches = detect_pii(text)
        types = {m.pii_type for m in matches}
        assert "email" in types
        assert "ssn" in types
        assert "ipv4" in types

    def test_detect_pii_with_field_name(self):
        """field_name is passed through to PIIMatch objects."""
        matches = detect_pii("alice@example.com", field_name="contact_email")
        assert len(matches) > 0
        assert all(m.field == "contact_email" for m in matches)

    def test_detect_pii_empty_string(self):
        """No PII detected in empty string."""
        assert detect_pii("") == []

    def test_detect_pii_no_pii(self):
        """No PII detected in clean text."""
        matches = detect_pii("The quick brown fox jumps over the lazy dog")
        assert len(matches) == 0

    def test_detect_pii_positions_are_correct(self):
        """start/end positions correctly index into the original text."""
        text = "Email: alice@example.com done"
        matches = detect_pii(text)
        email_match = next(m for m in matches if m.pii_type == "email")
        assert text[email_match.start:email_match.end] == "alice@example.com"

    def test_detect_pii_multiple_same_type(self):
        """Detects multiple occurrences of the same PII type."""
        text = "a@b.com and c@d.com"
        matches = detect_pii(text)
        email_matches = [m for m in matches if m.pii_type == "email"]
        assert len(email_matches) >= 2

    def test_detect_pii_default_field_name(self):
        """Default field_name is empty string."""
        matches = detect_pii("alice@example.com")
        assert all(m.field == "" for m in matches)


# ==============================================================================
# mask_hash
# ==============================================================================


@pytest.mark.unit
class TestMaskHash:
    """Tests for the mask_hash function."""

    def test_sha256_default(self):
        """Default algorithm is sha256."""
        result = mask_hash("hello")
        expected = hashlib.sha256(b"hello").hexdigest()
        assert result == expected

    def test_sha256_explicit(self):
        """Explicit sha256 matches hashlib."""
        result = mask_hash("test", algorithm="sha256")
        expected = hashlib.sha256(b"test").hexdigest()
        assert result == expected

    def test_md5(self):
        """md5 algorithm works correctly."""
        result = mask_hash("test", algorithm="md5")
        expected = hashlib.md5(b"test").hexdigest()
        assert result == expected

    def test_sha1(self):
        """sha1 algorithm works correctly."""
        result = mask_hash("test", algorithm="sha1")
        expected = hashlib.sha1(b"test").hexdigest()
        assert result == expected

    def test_deterministic(self):
        """Same input produces same output."""
        assert mask_hash("dummy_sec") == mask_hash("dummy_sec")

    def test_different_inputs_differ(self):
        """Different inputs produce different hashes."""
        assert mask_hash("a") != mask_hash("b")

    def test_empty_string(self):
        """Hashing empty string works."""
        result = mask_hash("")
        expected = hashlib.sha256(b"").hexdigest()
        assert result == expected

    def test_unicode_input(self):
        """Unicode characters are hashed correctly."""
        result = mask_hash("cafe\u0301")
        expected = hashlib.sha256("cafe\u0301".encode()).hexdigest()
        assert result == expected

    def test_invalid_algorithm_raises(self):
        """Invalid algorithm raises ValueError."""
        with pytest.raises(ValueError):
            mask_hash("test", algorithm="not_a_hash")


# ==============================================================================
# mask_redact
# ==============================================================================


@pytest.mark.unit
class TestMaskRedact:
    """Tests for the mask_redact function."""

    def test_default_replacement(self):
        """Default replacement is '***'."""
        assert mask_redact("sensitive") == "***"

    def test_custom_replacement(self):
        """Custom replacement string is used."""
        assert mask_redact("data", replacement="REDACTED") == "REDACTED"

    def test_empty_replacement(self):
        """Empty replacement string works."""
        assert mask_redact("data", replacement="") == ""

    def test_empty_input(self):
        """Redacting empty string returns replacement."""
        assert mask_redact("") == "***"

    def test_ignores_original_value(self):
        """Output is always the replacement, regardless of input."""
        assert mask_redact("short") == mask_redact("a very long string with lots of data")


# ==============================================================================
# mask_partial
# ==============================================================================


@pytest.mark.unit
class TestMaskPartial:
    """Tests for the mask_partial function."""

    def test_basic_partial_mask(self):
        """Last 4 characters visible, rest masked."""
        result = mask_partial("1234567890", 4)
        assert result == "******7890"

    def test_default_visible_chars(self):
        """Default visible_chars is 4."""
        result = mask_partial("1234567890")
        assert result == "******7890"

    def test_custom_mask_char(self):
        """Custom mask character works."""
        result = mask_partial("ABCDEF", visible_chars=2, mask_char="#")
        assert result == "####EF"

    def test_value_shorter_than_visible(self):
        """When value is shorter than visible_chars, return value unchanged."""
        result = mask_partial("AB", visible_chars=4)
        assert result == "AB"

    def test_value_equal_to_visible(self):
        """When value length equals visible_chars, return value unchanged."""
        result = mask_partial("ABCD", visible_chars=4)
        assert result == "ABCD"

    def test_value_one_more_than_visible(self):
        """One character is masked when value is one longer than visible."""
        result = mask_partial("ABCDE", visible_chars=4)
        assert result == "*BCDE"

    def test_single_visible_char(self):
        """Only last character visible."""
        result = mask_partial("HIDDEN", visible_chars=1)
        assert result == "*****N"

    def test_zero_visible_chars(self):
        """Zero visible chars: masks full length then appends value[-0:] which is full value.

        This is a quirk of Python slicing: value[-0:] == value.
        So mask_partial("ABC", 0) == "***" + "ABC" == "***ABC".
        """
        result = mask_partial("ABC", visible_chars=0)
        # value[-0:] in Python is the full string, so result is "***ABC"
        assert result == "***ABC"

    def test_empty_string(self):
        """Empty string returns empty (shorter than visible_chars)."""
        result = mask_partial("", visible_chars=4)
        assert result == ""


# ==============================================================================
# mask_email
# ==============================================================================


@pytest.mark.unit
class TestMaskEmail:
    """Tests for the mask_email function."""

    def test_basic_email_masking(self):
        """Standard email keeps first char and domain."""
        result = mask_email("alice@example.com")
        assert result.startswith("a")
        assert result.endswith("@example.com")
        assert "*" in result

    def test_preserves_domain(self):
        """Domain part is fully preserved."""
        result = mask_email("longusername@company.co.uk")
        assert result.endswith("@company.co.uk")

    def test_single_char_local_part(self):
        """Single char local part still has *** appended."""
        result = mask_email("a@b.com")
        assert result == "a***@b.com"

    def test_two_char_local_part(self):
        """Two char local part masks second char."""
        result = mask_email("ab@c.com")
        assert result == "a*@c.com"

    def test_no_at_sign(self):
        """Input without @ is fully redacted."""
        result = mask_email("not-an-email")
        assert result == "***"

    def test_multiple_at_signs(self):
        """Splits on last @ sign (rsplit behavior)."""
        result = mask_email("user@subdomain@domain.com")
        assert result.endswith("@domain.com")

    def test_empty_local_part(self):
        """Empty local part before @ results in *** prefix."""
        result = mask_email("@domain.com")
        # empty local, len <= 1 check: len("") == 0 <= 1
        assert result == "***@domain.com"


# ==============================================================================
# laplace_noise
# ==============================================================================


@pytest.mark.unit
class TestLaplaceNoise:
    """Tests for the laplace_noise function."""

    def test_returns_float(self):
        """Returns a float value."""
        result = laplace_noise(epsilon=1.0)
        assert isinstance(result, float)

    def test_bounded_range(self):
        """Result is between -0.5 and 0.5 (uniform approx)."""
        for _ in range(50):
            result = laplace_noise(epsilon=1.0)
            assert -0.5 <= result <= 0.5

    def test_zero_epsilon_raises(self):
        """Epsilon of 0 raises ValueError."""
        with pytest.raises(ValueError, match="Epsilon must be positive"):
            laplace_noise(epsilon=0.0)

    def test_negative_epsilon_raises(self):
        """Negative epsilon raises ValueError."""
        with pytest.raises(ValueError, match="Epsilon must be positive"):
            laplace_noise(epsilon=-1.0)

    def test_different_sensitivities_accepted(self):
        """Various sensitivity values do not raise."""
        # The function accepts sensitivity but the uniform approx doesn't
        # fully use it -- just verify no error.
        for s in [0.1, 1.0, 10.0, 100.0]:
            result = laplace_noise(epsilon=1.0, sensitivity=s)
            assert isinstance(result, float)


# ==============================================================================
# add_laplace_noise
# ==============================================================================


@pytest.mark.unit
class TestAddLaplaceNoise:
    """Tests for the add_laplace_noise function."""

    def test_returns_float(self):
        """Returns a float."""
        result = add_laplace_noise(100.0, epsilon=1.0)
        assert isinstance(result, float)

    def test_high_epsilon_low_noise(self):
        """High epsilon means low noise -- result close to original."""
        results = [add_laplace_noise(100.0, epsilon=100.0) for _ in range(50)]
        mean_result = sum(results) / len(results)
        assert 95.0 < mean_result < 105.0

    def test_zero_epsilon_raises(self):
        """Epsilon of 0 raises ValueError."""
        with pytest.raises(ValueError, match="Epsilon must be positive"):
            add_laplace_noise(50.0, epsilon=0.0)

    def test_negative_epsilon_raises(self):
        """Negative epsilon raises ValueError."""
        with pytest.raises(ValueError, match="Epsilon must be positive"):
            add_laplace_noise(50.0, epsilon=-0.5)

    def test_zero_value(self):
        """Adding noise to zero works."""
        result = add_laplace_noise(0.0, epsilon=1.0)
        assert isinstance(result, float)

    def test_negative_value(self):
        """Adding noise to negative value works."""
        result = add_laplace_noise(-50.0, epsilon=10.0)
        assert isinstance(result, float)

    def test_custom_sensitivity(self):
        """Custom sensitivity is accepted without error."""
        result = add_laplace_noise(100.0, epsilon=1.0, sensitivity=5.0)
        assert isinstance(result, float)


# ==============================================================================
# dp_mean
# ==============================================================================


@pytest.mark.unit
class TestDPMean:
    """Tests for the dp_mean function."""

    def test_empty_list_returns_zero(self):
        """Empty values list returns 0.0."""
        result = dp_mean([], epsilon=1.0, lower=0.0, upper=100.0)
        assert result == 0.0

    def test_single_value(self):
        """Single value list returns approximately that value (high epsilon)."""
        results = [dp_mean([50.0], epsilon=100.0, lower=0.0, upper=100.0) for _ in range(20)]
        mean_result = sum(results) / len(results)
        assert 40.0 < mean_result < 60.0

    def test_known_mean_high_epsilon(self):
        """With high epsilon, result is close to true mean."""
        values = [10.0, 20.0, 30.0, 40.0, 50.0]
        results = [dp_mean(values, epsilon=100.0, lower=0.0, upper=100.0) for _ in range(20)]
        mean_result = sum(results) / len(results)
        # True mean is 30.0
        assert 25.0 < mean_result < 35.0

    def test_returns_float(self):
        """Always returns a float."""
        result = dp_mean([1.0, 2.0], epsilon=1.0, lower=0.0, upper=10.0)
        assert isinstance(result, float)

    def test_large_list_stability(self):
        """Larger list has less noise (sensitivity decreases with n)."""
        values = [50.0] * 100
        results = [dp_mean(values, epsilon=1.0, lower=0.0, upper=100.0) for _ in range(20)]
        mean_result = sum(results) / len(results)
        # With 100 values, sensitivity = (100-0)/100 = 1.0, so noise is moderate
        assert 40.0 < mean_result < 60.0


# ==============================================================================
# dp_count
# ==============================================================================


@pytest.mark.unit
class TestDPCount:
    """Tests for the dp_count function."""

    def test_returns_float(self):
        """dp_count always returns a float."""
        result = dp_count(42, epsilon=1.0)
        assert isinstance(result, float)

    def test_high_epsilon_close_to_true(self):
        """High epsilon produces result close to true count."""
        results = [dp_count(100, epsilon=100.0) for _ in range(20)]
        mean_result = sum(results) / len(results)
        assert 95.0 < mean_result < 105.0

    def test_zero_count(self):
        """Zero count produces result near zero."""
        results = [dp_count(0, epsilon=10.0) for _ in range(20)]
        mean_result = sum(results) / len(results)
        assert -5.0 < mean_result < 5.0

    def test_negative_count(self):
        """Negative count is handled (noise added to negative)."""
        result = dp_count(-10, epsilon=1.0)
        assert isinstance(result, float)


# ==============================================================================
# PrivacyRule Dataclass
# ==============================================================================


@pytest.mark.unit
class TestPrivacyRule:
    """Tests for the PrivacyRule dataclass."""

    def test_basic_creation(self):
        """PrivacyRule stores field, strategy, and params."""
        rule = PrivacyRule(field="email", strategy="email", params={})
        assert rule.field == "email"
        assert rule.strategy == "email"
        assert rule.params == {}

    def test_default_params(self):
        """Default params is empty dict."""
        rule = PrivacyRule(field="ssn", strategy="redact")
        assert rule.params == {}

    def test_with_params(self):
        """Custom params are stored correctly."""
        rule = PrivacyRule(field="card", strategy="partial", params={"visible": 4})
        assert rule.params["visible"] == 4

    def test_equality(self):
        """Two rules with same data are equal."""
        a = PrivacyRule(field="f", strategy="hash", params={"algorithm": "md5"})
        b = PrivacyRule(field="f", strategy="hash", params={"algorithm": "md5"})
        assert a == b


# ==============================================================================
# Privacy Class
# ==============================================================================


@pytest.mark.unit
class TestPrivacyClass:
    """Tests for the Privacy class."""

    def test_init_default(self):
        """Default initialization works."""
        p = Privacy()
        assert p.config == {}
        assert p._rules == {}

    def test_init_with_config(self):
        """Config is stored when provided."""
        p = Privacy(config={"level": "strict"})
        assert p.config["level"] == "strict"

    def test_add_rule(self):
        """Adding a rule stores it keyed by field."""
        p = Privacy()
        rule = PrivacyRule("email", "email")
        p.add_rule(rule)
        assert "email" in p._rules
        assert p._rules["email"] is rule

    def test_add_rule_overwrites(self):
        """Adding a rule for the same field overwrites the previous one."""
        p = Privacy()
        rule1 = PrivacyRule("email", "redact")
        rule2 = PrivacyRule("email", "hash")
        p.add_rule(rule1)
        p.add_rule(rule2)
        assert p._rules["email"].strategy == "hash"

    def test_process_hash_strategy(self):
        """Hash strategy produces correct sha256 output."""
        p = Privacy()
        p.add_rule(PrivacyRule("dummy_sec", "hash"))
        result = p.process({"dummy_sec": "dummy_pass_word"})
        expected = hashlib.sha256(b"dummy_pass_word").hexdigest()
        assert result["dummy_sec"] == expected

    def test_process_hash_with_md5(self):
        """Hash strategy with md5 algorithm parameter."""
        p = Privacy()
        p.add_rule(PrivacyRule("dummy_sec", "hash", {"algorithm": "md5"}))
        result = p.process({"dummy_sec": "dummy_pass_word"})
        expected = hashlib.md5(b"dummy_pass_word").hexdigest()
        assert result["dummy_sec"] == expected

    def test_process_redact_strategy(self):
        """Redact strategy replaces with ***."""
        p = Privacy()
        p.add_rule(PrivacyRule("ssn", "redact"))
        result = p.process({"ssn": "123-45-6789"})
        assert result["ssn"] == "***"

    def test_process_redact_custom_replacement(self):
        """Redact strategy with custom replacement."""
        p = Privacy()
        p.add_rule(PrivacyRule("ssn", "redact", {"replacement": "[REMOVED]"}))
        result = p.process({"ssn": "123-45-6789"})
        assert result["ssn"] == "[REMOVED]"

    def test_process_partial_strategy(self):
        """Partial strategy shows last N characters."""
        p = Privacy()
        p.add_rule(PrivacyRule("card", "partial", {"visible": 4}))
        result = p.process({"card": "4111111111111111"})
        assert result["card"].endswith("1111")
        assert result["card"].startswith("*")

    def test_process_email_strategy(self):
        """Email strategy masks local part, preserves domain."""
        p = Privacy()
        p.add_rule(PrivacyRule("email", "email"))
        result = p.process({"email": "alice@example.com"})
        assert "@example.com" in result["email"]
        assert result["email"].startswith("a")

    def test_process_noise_strategy(self):
        """Noise strategy adds Laplace noise to numeric value."""
        p = Privacy()
        p.add_rule(PrivacyRule("salary", "noise", {"epsilon": 100.0}))
        results = [p.process({"salary": 50000})["salary"] for _ in range(20)]
        mean_result = sum(results) / len(results)
        # High epsilon = low noise
        assert 49000 < mean_result < 51000

    def test_process_noise_custom_sensitivity(self):
        """Noise strategy with custom sensitivity parameter."""
        p = Privacy()
        p.add_rule(PrivacyRule("score", "noise", {"epsilon": 10.0, "sensitivity": 0.1}))
        result = p.process({"score": 85.0})
        assert isinstance(result["score"], float)

    def test_process_unknown_strategy_leaves_value(self):
        """Unknown strategy logs warning but does not modify value."""
        p = Privacy()
        p.add_rule(PrivacyRule("field", "unknown_strategy"))
        result = p.process({"field": "original"})
        assert result["field"] == "original"

    def test_process_missing_field(self):
        """Rule for a field not in data is silently skipped."""
        p = Privacy()
        p.add_rule(PrivacyRule("missing", "redact"))
        result = p.process({"present": "value"})
        assert result == {"present": "value"}
        assert "missing" not in result

    def test_process_preserves_unruled_fields(self):
        """Fields without rules are left untouched."""
        p = Privacy()
        p.add_rule(PrivacyRule("ssn", "redact"))
        result = p.process({"ssn": "123-45-6789", "name": "Alice", "age": 30})
        assert result["name"] == "Alice"
        assert result["age"] == 30

    def test_process_returns_copy(self):
        """Process returns a new dict, not mutating the original."""
        p = Privacy()
        p.add_rule(PrivacyRule("ssn", "redact"))
        data = {"ssn": "123-45-6789"}
        result = p.process(data)
        assert data["ssn"] == "123-45-6789"  # Original unchanged
        assert result["ssn"] == "***"

    def test_process_empty_data(self):
        """Processing empty data returns empty dict."""
        p = Privacy()
        p.add_rule(PrivacyRule("ssn", "redact"))
        result = p.process({})
        assert result == {}

    def test_process_multiple_rules(self):
        """Multiple rules are all applied."""
        p = Privacy()
        p.add_rule(PrivacyRule("email", "email"))
        p.add_rule(PrivacyRule("ssn", "redact"))
        p.add_rule(PrivacyRule("dummy_sec", "hash"))
        data = {"email": "a@b.com", "ssn": "111-22-3333", "dummy_sec": "pwd"}
        result = p.process(data)
        assert "@b.com" in result["email"]
        assert result["ssn"] == "***"
        assert result["dummy_sec"] == hashlib.sha256(b"pwd").hexdigest()

    def test_process_converts_to_string_for_hash(self):
        """Numeric value is converted to string before hashing."""
        p = Privacy()
        p.add_rule(PrivacyRule("id", "hash"))
        result = p.process({"id": 12345})
        expected = hashlib.sha256(b"12345").hexdigest()
        assert result["id"] == expected

    def test_scan_pii_detects_email(self):
        """scan_pii finds email addresses in string fields."""
        p = Privacy()
        matches = p.scan_pii({"contact": "alice@example.com", "age": "25"})
        types = {m.pii_type for m in matches}
        assert "email" in types

    def test_scan_pii_skips_non_strings(self):
        """scan_pii only scans string values, not ints/floats."""
        p = Privacy()
        matches = p.scan_pii({"count": 42, "rate": 3.14, "flag": True})
        assert len(matches) == 0

    def test_scan_pii_field_names(self):
        """scan_pii populates field name on each match."""
        p = Privacy()
        matches = p.scan_pii({"bio": "Email: a@b.com"})
        assert all(m.field == "bio" for m in matches)

    def test_scan_pii_empty_data(self):
        """scan_pii on empty dict returns no matches."""
        p = Privacy()
        assert p.scan_pii({}) == []

    def test_scan_pii_multiple_fields(self):
        """scan_pii scans all string fields."""
        p = Privacy()
        matches = p.scan_pii({
            "email_field": "alice@example.com",
            "phone_field": "555-123-4567",
        })
        types = {m.pii_type for m in matches}
        assert "email" in types
        assert "phone" in types


# ==============================================================================
# create_privacy Factory
# ==============================================================================


@pytest.mark.unit
class TestCreatePrivacy:
    """Tests for the create_privacy factory function."""

    def test_creates_privacy_instance(self):
        """Returns a Privacy instance."""
        p = create_privacy()
        assert isinstance(p, Privacy)

    def test_passes_config(self):
        """Config is forwarded to Privacy."""
        p = create_privacy(config={"mode": "strict"})
        assert p.config["mode"] == "strict"

    def test_default_config_is_empty(self):
        """Default config is empty dict."""
        p = create_privacy()
        assert p.config == {}
