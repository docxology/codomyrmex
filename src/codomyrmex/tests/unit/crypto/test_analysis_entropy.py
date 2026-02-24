"""Tests for crypto.analysis.entropy module."""

from __future__ import annotations

import os

import pytest

from codomyrmex.crypto.analysis.entropy import (
    ChiSquaredResult,
    byte_entropy,
    chi_squared_test,
    serial_correlation,
    shannon_entropy,
)


@pytest.mark.unit
@pytest.mark.crypto
class TestShannonEntropy:
    """Tests for shannon_entropy function."""

    def test_empty_data_returns_zero(self):
        """Test functionality: empty data returns zero."""
        assert shannon_entropy(b"") == 0.0
        assert shannon_entropy("") == 0.0

    def test_single_byte_returns_zero(self):
        """Test functionality: single byte returns zero."""
        # All same bytes -> entropy = 0
        assert shannon_entropy(b"\x00" * 100) == 0.0

    def test_all_same_character_returns_zero(self):
        """Test functionality: all same character returns zero."""
        assert shannon_entropy("aaaaaaa") == 0.0

    def test_two_equally_likely_symbols(self):
        """Test functionality: two equally likely symbols."""
        # 50/50 split -> entropy = 1.0
        data = "ab" * 500
        result = shannon_entropy(data)
        assert abs(result - 1.0) < 0.01

    def test_four_equally_likely_symbols(self):
        """Test functionality: four equally likely symbols."""
        # 4 equal symbols -> entropy = 2.0
        data = "abcd" * 250
        result = shannon_entropy(data)
        assert abs(result - 2.0) < 0.01

    def test_string_input(self):
        """Test functionality: string input."""
        result = shannon_entropy("hello world")
        assert result > 0.0


@pytest.mark.unit
@pytest.mark.crypto
class TestByteEntropy:
    """Tests for byte_entropy function."""

    def test_empty_returns_zero(self):
        """Test functionality: empty returns zero."""
        assert byte_entropy(b"") == 0.0

    def test_single_value_returns_zero(self):
        """Test functionality: single value returns zero."""
        assert byte_entropy(bytes([42]) * 1000) == 0.0

    def test_uniform_random_near_eight(self):
        """Test functionality: uniform random near eight."""
        # All 256 byte values equally represented -> entropy ~8.0
        data = bytes(range(256)) * 100
        result = byte_entropy(data)
        assert abs(result - 8.0) < 0.01

    def test_maximum_is_eight(self):
        """Test functionality: maximum is eight."""
        data = bytes(range(256)) * 50
        result = byte_entropy(data)
        assert result <= 8.0 + 0.001

    def test_two_byte_values(self):
        """Test functionality: two byte values."""
        # Two equally likely bytes -> entropy = 1.0
        data = bytes([0, 255]) * 500
        result = byte_entropy(data)
        assert abs(result - 1.0) < 0.01


@pytest.mark.unit
@pytest.mark.crypto
class TestChiSquaredTest:
    """Tests for chi_squared_test function."""

    def test_empty_data_raises(self):
        """Test functionality: empty data raises."""
        with pytest.raises(ValueError):
            chi_squared_test(b"")

    def test_uniform_data_passes(self):
        """Test functionality: uniform data passes."""
        # Perfectly uniform data should have p_value close to 1
        data = bytes(range(256)) * 100
        result = chi_squared_test(data)
        assert isinstance(result, ChiSquaredResult)
        assert result.uniform is True
        assert result.p_value > 0.05
        # Chi-squared statistic should be 0 for perfectly uniform
        assert result.statistic < 1.0

    def test_biased_data_fails(self):
        """Test functionality: biased data fails."""
        # Heavily biased data should fail uniformity test
        data = b"\x00" * 5000 + b"\x01" * 100
        result = chi_squared_test(data)
        assert result.uniform is False
        assert result.p_value < 0.05

    def test_random_bytes_likely_passes(self):
        """Test functionality: random bytes likely passes."""
        # os.urandom should be uniform enough to pass
        data = os.urandom(10000)
        result = chi_squared_test(data)
        # Random data should usually pass, but not guaranteed
        # Use a generous check
        assert result.statistic > 0
        assert 0.0 <= result.p_value <= 1.0

    def test_result_dataclass_fields(self):
        """Test functionality: result dataclass fields."""
        data = bytes(range(256)) * 10
        result = chi_squared_test(data)
        assert hasattr(result, "statistic")
        assert hasattr(result, "p_value")
        assert hasattr(result, "uniform")


@pytest.mark.unit
@pytest.mark.crypto
class TestSerialCorrelation:
    """Tests for serial_correlation function."""

    def test_empty_returns_zero(self):
        """Test functionality: empty returns zero."""
        assert serial_correlation(b"") == 0.0

    def test_single_byte_returns_zero(self):
        """Test functionality: single byte returns zero."""
        assert serial_correlation(b"\x42") == 0.0

    def test_constant_bytes_returns_zero(self):
        """Test functionality: constant bytes returns zero."""
        # All same values -> correlation undefined / 0
        result = serial_correlation(b"\x80" * 100)
        assert result == 0.0

    def test_sequential_bytes_positive_correlation(self):
        """Test functionality: sequential bytes positive correlation."""
        # Sequentially increasing -> high positive correlation
        data = bytes(range(256))
        result = serial_correlation(data)
        assert result > 0.9

    def test_alternating_bytes_negative_correlation(self):
        """Test functionality: alternating bytes negative correlation."""
        # Alternating high/low -> negative correlation
        data = bytes([0, 255] * 500)
        result = serial_correlation(data)
        assert result < -0.9

    def test_range_is_bounded(self):
        """Test functionality: range is bounded."""
        data = os.urandom(1000)
        result = serial_correlation(data)
        assert -1.0 <= result <= 1.0
