"""Unit tests for generated math functions."""

import pytest


def multiply(a, b):
    """A simple multiplication function."""
    return a * b


@pytest.mark.unit
class TestGeneratedMathFunctions:
    """Tests for the generated math functions."""

    def test_multiply_positive_numbers(self):
        """Test multiplying two positive numbers."""
        result = multiply(2, 3)
        assert result == 6

    def test_multiply_negative_numbers(self):
        """Test multiplying two negative numbers."""
        result = multiply(-2, -3)
        assert result == 6

    def test_multiply_mixed_numbers(self):
        """Test multiplying a positive and a negative number."""
        result = multiply(2, -3)
        assert result == -6

    def test_multiply_by_zero(self):
        """Test multiplying by zero."""
        result = multiply(5, 0)
        assert result == 0

    def test_multiply_identity(self):
        """Test multiplying by one."""
        result = multiply(5, 1)
        assert result == 5
