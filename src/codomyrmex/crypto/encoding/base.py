"""Base encoding implementations: Base64, Base58 (Bitcoin), Base32.

Provides encode/decode functions for common binary-to-text encoding schemes.
Base64 and Base32 use Python's stdlib base64 module. Base58 uses the Bitcoin
alphabet with a custom implementation.
"""

from __future__ import annotations

import base64

from codomyrmex.crypto.exceptions import EncodingError
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)

# Bitcoin Base58 alphabet (no 0, O, I, l to avoid visual ambiguity)
_BASE58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
_BASE58_MAP = {c: i for i, c in enumerate(_BASE58_ALPHABET)}


def encode_base64(data: bytes) -> str:
    """Encode bytes to a Base64 string.

    Args:
        data: Raw bytes to encode.

    Returns:
        Base64-encoded ASCII string.

    Raises:
        EncodingError: If encoding fails.
    """
    try:
        return base64.b64encode(data).decode("ascii")
    except Exception as exc:
        raise EncodingError(f"Base64 encoding failed: {exc}") from exc


def decode_base64(encoded: str) -> bytes:
    """Decode a Base64 string to bytes.

    Args:
        encoded: Base64-encoded string.

    Returns:
        Decoded bytes.

    Raises:
        EncodingError: If the input is not valid Base64.
    """
    try:
        return base64.b64decode(encoded)
    except Exception as exc:
        raise EncodingError(f"Base64 decoding failed: {exc}") from exc


def encode_base58(data: bytes) -> str:
    """Encode bytes using the Bitcoin Base58 alphabet.

    Converts bytes to a big integer, repeatedly divides by 58, and maps
    remainders to the Base58 alphabet. Leading zero bytes are preserved
    as '1' characters.

    Args:
        data: Raw bytes to encode.

    Returns:
        Base58-encoded string.

    Raises:
        EncodingError: If encoding fails.
    """
    try:
        # Count leading zero bytes
        leading_zeros = 0
        for byte in data:
            if byte == 0:
                leading_zeros += 1
            else:
                break

        # Convert bytes to integer
        num = int.from_bytes(data, "big")

        # Divide repeatedly by 58
        chars: list[str] = []
        while num > 0:
            num, remainder = divmod(num, 58)
            chars.append(_BASE58_ALPHABET[remainder])

        # Reverse (most significant first) and prepend leading '1's
        return "1" * leading_zeros + "".join(reversed(chars))
    except Exception as exc:
        if isinstance(exc, EncodingError):
            raise
        raise EncodingError(f"Base58 encoding failed: {exc}") from exc


def decode_base58(encoded: str) -> bytes:
    """Decode a Base58-encoded string to bytes.

    Args:
        encoded: Base58-encoded string.

    Returns:
        Decoded bytes.

    Raises:
        EncodingError: If the input contains invalid Base58 characters.
    """
    try:
        # Count leading '1' characters (they represent 0x00 bytes)
        leading_ones = 0
        for ch in encoded:
            if ch == "1":
                leading_ones += 1
            else:
                break

        # Convert Base58 string to integer
        num = 0
        for ch in encoded:
            if ch not in _BASE58_MAP:
                raise EncodingError(
                    f"Invalid Base58 character: {ch!r}"
                )
            num = num * 58 + _BASE58_MAP[ch]

        # Convert integer to bytes
        if num == 0:
            result_bytes = b""
        else:
            byte_length = (num.bit_length() + 7) // 8
            result_bytes = num.to_bytes(byte_length, "big")

        return b"\x00" * leading_ones + result_bytes
    except Exception as exc:
        if isinstance(exc, EncodingError):
            raise
        raise EncodingError(f"Base58 decoding failed: {exc}") from exc


def encode_base32(data: bytes) -> str:
    """Encode bytes to a Base32 string.

    Args:
        data: Raw bytes to encode.

    Returns:
        Base32-encoded ASCII string.

    Raises:
        EncodingError: If encoding fails.
    """
    try:
        return base64.b32encode(data).decode("ascii")
    except Exception as exc:
        raise EncodingError(f"Base32 encoding failed: {exc}") from exc


def decode_base32(encoded: str) -> bytes:
    """Decode a Base32 string to bytes.

    Args:
        encoded: Base32-encoded string.

    Returns:
        Decoded bytes.

    Raises:
        EncodingError: If the input is not valid Base32.
    """
    try:
        return base64.b32decode(encoded)
    except Exception as exc:
        raise EncodingError(f"Base32 decoding failed: {exc}") from exc
