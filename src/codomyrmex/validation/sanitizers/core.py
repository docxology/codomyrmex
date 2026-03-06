"""Core sanitizers for cleaning and normalizing input data."""

import re
from typing import Any


def strip_whitespace(value: Any) -> Any:
    """Strip leading and trailing whitespace from a string."""
    if isinstance(value, str):
        return value.strip()
    return value


def to_lowercase(value: Any) -> Any:
    """Convert a string to lowercase."""
    if isinstance(value, str):
        return value.lower()
    return value


def to_uppercase(value: Any) -> Any:
    """Convert a string to uppercase."""
    if isinstance(value, str):
        return value.upper()
    return value


def remove_special_chars(value: Any) -> Any:
    """Remove special characters from a string, keeping alphanumeric and spaces."""
    if isinstance(value, str):
        return re.sub(r"[^a-zA-Z0-9\s]", "", value)
    return value


def sanitize_numeric(value: Any) -> int | float | None:
    """Attempt to convert a value to a number, return None if it fails."""
    try:
        if "." in str(value):
            return float(value)
        return int(value)
    except (ValueError, TypeError):
        return None
