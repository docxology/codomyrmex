"""Unit tests for a generated example function."""

import pytest


def add(a, b):
    """A simple addition function."""
    return a + b


@pytest.mark.unit
class TestGeneratedExample:
    """Tests for the generated example function."""

    def test_add_positive_numbers(self):
        """Test adding two positive numbers."""
        result = add(1, 2)
        assert result == 3

    def test_add_negative_numbers(self):
        """Test adding two negative numbers."""
        result = add(-1, -2)
        assert result == -3

    def test_add_mixed_numbers(self):
        """Test adding a positive and a negative number."""
        result = add(1, -2)
        assert result == -1
