"""Cryptographically secure random generation utilities.

Uses ``os.urandom`` and the ``secrets`` module to ensure all randomness
is sourced from the operating system's CSPRNG.
"""

from __future__ import annotations

import os
import secrets
import string
import uuid

from codomyrmex.crypto.exceptions import RandomError
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


def secure_random_bytes(n: int) -> bytes:
    """Generate *n* cryptographically secure random bytes.

    Args:
        n: Number of bytes to generate. Must be non-negative.

    Returns:
        A bytes object of length *n*.

    Raises:
        RandomError: If *n* is negative or generation fails.
    """
    if n < 0:
        raise RandomError(f"Byte count must be non-negative, got {n}")
    try:
        return os.urandom(n)
    except Exception as exc:
        raise RandomError(f"Failed to generate random bytes: {exc}") from exc


def secure_random_int(min_val: int, max_val: int) -> int:
    """Generate a cryptographically secure random integer in [min_val, max_val].

    Args:
        min_val: Inclusive lower bound.
        max_val: Inclusive upper bound.

    Returns:
        A random integer *i* such that min_val <= i <= max_val.

    Raises:
        RandomError: If min_val > max_val or generation fails.
    """
    if min_val > max_val:
        raise RandomError(
            f"min_val ({min_val}) must be <= max_val ({max_val})"
        )
    try:
        # secrets.randbelow gives [0, exclusive_upper)
        return min_val + secrets.randbelow(max_val - min_val + 1)
    except Exception as exc:
        if isinstance(exc, RandomError):
            raise
        raise RandomError(f"Failed to generate random int: {exc}") from exc


def secure_random_string(
    length: int,
    charset: str | None = None,
) -> str:
    """Generate a cryptographically secure random string.

    Args:
        length: Desired string length. Must be non-negative.
        charset: Characters to choose from. Defaults to ASCII letters + digits.

    Returns:
        A random string of the specified length.

    Raises:
        RandomError: If length is negative, charset is empty, or generation fails.
    """
    if length < 0:
        raise RandomError(f"Length must be non-negative, got {length}")
    if charset is not None and len(charset) == 0:
        raise RandomError("Charset must not be empty")

    if charset is None:
        charset = string.ascii_letters + string.digits

    try:
        return "".join(secrets.choice(charset) for _ in range(length))
    except Exception as exc:
        if isinstance(exc, RandomError):
            raise
        raise RandomError(f"Failed to generate random string: {exc}") from exc


def generate_uuid4() -> str:
    """Generate a random UUID version 4.

    Returns:
        A UUID4 string in the standard 8-4-4-4-12 hexadecimal format.
    """
    return str(uuid.uuid4())


def generate_nonce(size: int = 16) -> bytes:
    """Generate a random nonce (number used once).

    Args:
        size: Number of bytes for the nonce. Defaults to 16 (128 bits).

    Returns:
        A bytes object of the requested size.

    Raises:
        RandomError: If size is non-positive or generation fails.
    """
    if size <= 0:
        raise RandomError(f"Nonce size must be positive, got {size}")
    try:
        return os.urandom(size)
    except Exception as exc:
        raise RandomError(f"Failed to generate nonce: {exc}") from exc
