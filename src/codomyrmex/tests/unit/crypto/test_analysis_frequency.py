"""Tests for crypto.analysis.frequency module."""

from __future__ import annotations

import pytest

from codomyrmex.crypto.analysis.frequency import (
    bigram_frequency,
    character_frequency,
    expected_english_frequency,
    index_of_coincidence,
)


@pytest.mark.unit
@pytest.mark.crypto
class TestCharacterFrequency:
    """Tests for character_frequency function."""

    def test_empty_string(self):
        result = character_frequency("")
        assert result == {}

    def test_no_alpha_chars(self):
        result = character_frequency("12345!@#$%")
        assert result == {}

    def test_single_char(self):
        result = character_frequency("aaaa")
        assert len(result) == 1
        assert abs(result["a"] - 100.0) < 0.01

    def test_equal_distribution(self):
        result = character_frequency("abcabc")
        assert len(result) == 3
        for char in "abc":
            assert abs(result[char] - 33.33) < 0.1

    def test_case_insensitive(self):
        result = character_frequency("AaBb")
        assert "a" in result
        assert "b" in result
        assert abs(result["a"] - 50.0) < 0.01

    def test_ignores_non_alpha(self):
        result = character_frequency("a1b2c3")
        assert len(result) == 3
        for char in "abc":
            assert abs(result[char] - 33.33) < 0.1

    def test_known_text(self):
        text = "etaoins"
        result = character_frequency(text)
        assert abs(result["e"] - (1 / 7) * 100) < 0.1


@pytest.mark.unit
@pytest.mark.crypto
class TestBigramFrequency:
    """Tests for bigram_frequency function."""

    def test_empty_string(self):
        result = bigram_frequency("")
        assert result == {}

    def test_single_char(self):
        result = bigram_frequency("a")
        assert result == {}

    def test_two_chars(self):
        result = bigram_frequency("ab")
        assert len(result) == 1
        assert abs(result["ab"] - 100.0) < 0.01

    def test_repeated_text(self):
        result = bigram_frequency("ababab")
        # Bigrams: ab, ba, ab, ba, ab -> ab=3, ba=2 out of 5
        assert "ab" in result
        assert "ba" in result
        assert abs(result["ab"] - 60.0) < 0.1
        assert abs(result["ba"] - 40.0) < 0.1

    def test_case_insensitive(self):
        result = bigram_frequency("AB")
        assert "ab" in result


@pytest.mark.unit
@pytest.mark.crypto
class TestIndexOfCoincidence:
    """Tests for index_of_coincidence function."""

    def test_empty_string(self):
        assert index_of_coincidence("") == 0.0

    def test_single_char(self):
        assert index_of_coincidence("a") == 0.0

    def test_all_same_chars(self):
        # IC for all same chars = 1.0
        result = index_of_coincidence("aaaaaaaaaa")
        assert abs(result - 1.0) < 0.01

    def test_english_text_approximate(self):
        # A reasonably long English sample
        text = (
            "The quick brown fox jumps over the lazy dog. "
            "This sentence contains many different letters and "
            "demonstrates typical English letter distribution. "
            "We expect the index of coincidence to be around "
            "zero point zero six seven for English text samples "
            "that are sufficiently long to be statistically meaningful."
        )
        result = index_of_coincidence(text)
        # English IC should be roughly 0.060-0.075
        assert 0.055 < result < 0.080

    def test_random_text_lower_ic(self):
        # Uniformly distributed letters should have lower IC (~0.0385)
        import string

        # Create text with equal counts of all 26 letters
        text = string.ascii_lowercase * 100
        result = index_of_coincidence(text)
        # Should be close to 1/26 = 0.0385
        assert abs(result - (1.0 / 26.0)) < 0.005


@pytest.mark.unit
@pytest.mark.crypto
class TestExpectedEnglishFrequency:
    """Tests for expected_english_frequency function."""

    def test_returns_26_letters(self):
        freq = expected_english_frequency()
        assert len(freq) == 26

    def test_all_lowercase_letters_present(self):
        import string

        freq = expected_english_frequency()
        for letter in string.ascii_lowercase:
            assert letter in freq

    def test_frequencies_sum_near_100(self):
        freq = expected_english_frequency()
        total = sum(freq.values())
        assert abs(total - 100.0) < 1.0

    def test_e_is_most_frequent(self):
        freq = expected_english_frequency()
        assert freq["e"] > freq["t"]
        assert freq["e"] > 12.0

    def test_z_is_least_frequent(self):
        freq = expected_english_frequency()
        assert freq["z"] < freq["q"]
        assert freq["z"] < 0.1
