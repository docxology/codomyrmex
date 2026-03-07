"""Core validation rules for common data types and patterns."""

import re
from typing import Any


def is_email(value: Any) -> bool:
    """Check if a value is a valid email address."""
    if not isinstance(value, str):
        return False
    # Simple regex for email validation
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return bool(re.match(pattern, value))


def is_url(value: Any) -> bool:
    """Check if a value is a valid URL."""
    if not isinstance(value, str):
        return False
    # Simple regex for URL validation
    pattern = r"^https?://[^\s/$.?#].[^\s]*$"
    return bool(re.match(pattern, value))


def is_alphanumeric(value: Any) -> bool:
    """Check if a value contains only alphanumeric characters."""
    if not isinstance(value, str):
        return False
    return value.isalnum()


def is_in_range(
    value: Any, min_val: float | None = None, max_val: float | None = None
) -> bool:
    """Check if a numeric value is within a specified range."""
    try:
        num = float(value)
        if min_val is not None and num < min_val:
            return False
        if max_val is not None and num > max_val:
            return False
        return True
    except (ValueError, TypeError):
        return False
