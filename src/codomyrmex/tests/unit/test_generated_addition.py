"""Unit tests for generated addition functions."""

import pytest


def add(a, b):
    """A simple addition function."""
    return a + b


@pytest.mark.unit
class TestGeneratedAdditionFunctions:
    """Tests for the generated addition functions."""

    def test_add_positive_numbers(self):
        """Test adding two positive numbers."""
        result = add(2, 3)
        assert result == 5

    def test_add_negative_numbers(self):
        """Test adding two negative numbers."""
        result = add(-2, -3)
        assert result == -5

    def test_add_mixed_numbers(self):
        """Test adding a positive and a negative number."""
        result = add(2, -3)
        assert result == -1

    def test_add_with_zero(self):
        """Test adding zero."""
        result = add(5, 0)
        assert result == 5
