"""Hexadecimal encoding and decoding utilities."""

from __future__ import annotations

from codomyrmex.crypto.exceptions import EncodingError
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


def encode_hex(data: bytes) -> str:
    """Encode bytes to a lowercase hexadecimal string.

    Args:
        data: Raw bytes to encode.

    Returns:
        Hex-encoded string (lowercase).

    Raises:
        EncodingError: If encoding fails.
    """
    try:
        return data.hex()
    except Exception as exc:
        raise EncodingError(f"Hex encoding failed: {exc}") from exc


def decode_hex(hex_string: str) -> bytes:
    """Decode a hexadecimal string to bytes.

    Args:
        hex_string: Hex-encoded string (case-insensitive).

    Returns:
        Decoded bytes.

    Raises:
        EncodingError: If the input is not valid hexadecimal.
    """
    try:
        return bytes.fromhex(hex_string)
    except ValueError as exc:
        raise EncodingError(f"Hex decoding failed: {exc}") from exc


def is_valid_hex(string: str) -> bool:
    """Check whether a string is valid hexadecimal.

    Args:
        string: The string to validate.

    Returns:
        True if the string can be decoded as hex, False otherwise.
    """
    try:
        bytes.fromhex(string)
        return True
    except (ValueError, TypeError) as e:
        logger.warning("Hex validation failed for input: %s", e)
        return False
