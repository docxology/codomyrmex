"""Tests for crypto.analysis.strength module."""

from __future__ import annotations

import pytest

from codomyrmex.crypto.analysis.strength import (
    StrengthResult,
    assess_key_strength,
    assess_password_strength,
    check_common_passwords,
    estimate_crack_time,
)


@pytest.mark.unit
@pytest.mark.crypto
class TestAssessPasswordStrength:
    """Tests for assess_password_strength function."""

    def test_empty_password_is_very_weak(self):
        result = assess_password_strength("")
        assert result.score == 0
        assert result.level == "very_weak"
        assert result.entropy_bits == 0.0

    def test_common_password_is_very_weak(self):
        result = assess_password_strength("password")
        assert result.level == "very_weak"
        assert result.score <= 10

    def test_short_password_scores_low(self):
        result = assess_password_strength("abc")
        assert result.score < 40
        assert any("8 characters" in f for f in result.feedback)

    def test_strong_password_scores_high(self):
        result = assess_password_strength("C0mpl3x!P@ssw0rd#2024")
        assert result.score >= 60
        assert result.level in ("strong", "very_strong")

    def test_all_digits_lacks_diversity(self):
        result = assess_password_strength("12345678901234")
        assert any("uppercase" in f.lower() for f in result.feedback)

    def test_sequential_chars_penalized(self):
        result = assess_password_strength("abcdefgh")
        assert any("sequential" in f.lower() for f in result.feedback)

    def test_repeated_chars_penalized(self):
        result = assess_password_strength("aaabbbccc")
        assert any("repeated" in f.lower() for f in result.feedback)

    def test_result_has_correct_fields(self):
        result = assess_password_strength("test")
        assert isinstance(result, StrengthResult)
        assert isinstance(result.score, int)
        assert isinstance(result.level, str)
        assert isinstance(result.feedback, list)
        assert isinstance(result.entropy_bits, float)

    def test_score_within_bounds(self):
        for pw in ["", "a", "password", "Str0ng!Pass#2024xyz"]:
            result = assess_password_strength(pw)
            assert 0 <= result.score <= 100

    def test_levels_are_valid(self):
        valid_levels = {"very_weak", "weak", "fair", "strong", "very_strong"}
        for pw in ["", "ab", "abcdefgh", "P@ss12AB!", "C0mpl3x!P@ssw0rd#Long2024"]:
            result = assess_password_strength(pw)
            assert result.level in valid_levels


@pytest.mark.unit
@pytest.mark.crypto
class TestEstimateCrackTime:
    """Tests for estimate_crack_time function."""

    def test_empty_password_returns_zero(self):
        assert estimate_crack_time("") == 0.0

    def test_simple_password_fast_crack(self):
        # Short lowercase password should be crackable quickly
        seconds = estimate_crack_time("abc", guesses_per_second=1e10)
        # 26^3 / 1e10 = ~1.76e-6 seconds
        assert seconds < 1.0

    def test_long_password_slow_crack(self):
        # Long complex password should take a very long time
        seconds = estimate_crack_time("C0mpl3x!P@ss2024", guesses_per_second=1e10)
        # Should be many years
        assert seconds > 3600 * 24 * 365  # at least 1 year

    def test_positive_result_for_nonempty(self):
        seconds = estimate_crack_time("hello")
        assert seconds > 0.0

    def test_zero_guesses_per_second(self):
        assert estimate_crack_time("test", guesses_per_second=0) == 0.0


@pytest.mark.unit
@pytest.mark.crypto
class TestAssessKeyStrength:
    """Tests for assess_key_strength function."""

    def test_aes_128_valid(self):
        key = bytes(range(16))  # 128 bits
        result = assess_key_strength(key, "aes-128")
        assert result.score >= 70

    def test_aes_256_valid(self):
        import os

        key = os.urandom(32)  # 256 bits
        result = assess_key_strength(key, "aes-256")
        assert result.score >= 70

    def test_short_aes_key_weak(self):
        key = b"\x00" * 8  # Only 64 bits
        result = assess_key_strength(key, "aes")
        assert result.score < 40

    def test_all_zero_key_penalized(self):
        key = b"\x00" * 32
        result = assess_key_strength(key, "aes-256")
        # Should be penalized for low entropy
        assert any("entropy" in f.lower() for f in result.feedback)

    def test_unknown_algorithm(self):
        key = bytes(range(32))
        result = assess_key_strength(key, "custom-algo")
        assert any("unknown" in f.lower() for f in result.feedback)


@pytest.mark.unit
@pytest.mark.crypto
class TestCheckCommonPasswords:
    """Tests for check_common_passwords function."""

    def test_password_is_common(self):
        assert check_common_passwords("password") is True

    def test_123456_is_common(self):
        assert check_common_passwords("123456") is True

    def test_iloveyou_is_common(self):
        assert check_common_passwords("iloveyou") is True

    def test_case_insensitive(self):
        assert check_common_passwords("PASSWORD") is True
        assert check_common_passwords("Password") is True

    def test_uncommon_password_returns_false(self):
        assert check_common_passwords("xK9#mQ2$vL7@nP4") is False

    def test_empty_string_not_common(self):
        assert check_common_passwords("") is False
