"""Test task - Simple demonstration test."""


def test_simple_addition():
    """Test that basic addition works."""
    assert 1 + 1 == 2


def test_string_operations():
    """Test basic string operations."""
    text = "hello world"
    assert text.upper() == "HELLO WORLD"
    assert len(text) == 11


def test_list_operations():
    """Test basic list operations."""
    numbers = [1, 2, 3]
    assert sum(numbers) == 6
    assert len(numbers) == 3
    assert 2 in numbers
