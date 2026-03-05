"""Example unit test demonstrating pytest usage in Codomyrmex."""

import pytest


@pytest.mark.unit
def test_example_function():
    """Test a basic arithmetic operation to verify pytest setup."""
    # Arrange
    a = 1
    b = 2
    expected = 3

    # Act
    result = a + b

    # Assert
    assert result == expected
