"""Zero-width character text steganography.

Hides secret messages in plain text using invisible zero-width Unicode
characters. The cover text appears visually unchanged to human readers.
"""

from __future__ import annotations

from codomyrmex.crypto.exceptions import SteganographyError
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)

# Zero-width encoding characters
ZERO_WIDTH_SPACE = "\u200b"  # represents binary 0
ZERO_WIDTH_NON_JOINER = "\u200c"  # represents binary 1

# Delimiters to mark start and end of hidden data
_START_DELIMITER = "\u200d"  # Zero-width joiner
_END_DELIMITER = "\u2060"  # Word joiner (invisible)


def _bytes_to_zw(data: bytes) -> str:
    """Convert bytes to a zero-width character string."""
    zw_chars = []
    for byte in data:
        for i in range(7, -1, -1):
            bit = (byte >> i) & 1
            if bit == 0:
                zw_chars.append(ZERO_WIDTH_SPACE)
            else:
                zw_chars.append(ZERO_WIDTH_NON_JOINER)
    return "".join(zw_chars)


def _zw_to_bytes(zw_string: str) -> bytes:
    """Convert a zero-width character string back to bytes."""
    bits = []
    for ch in zw_string:
        if ch == ZERO_WIDTH_SPACE:
            bits.append(0)
        elif ch == ZERO_WIDTH_NON_JOINER:
            bits.append(1)
        # Skip any other characters (delimiters, etc.)

    # Convert bits to bytes
    result = bytearray()
    for i in range(0, len(bits) - 7, 8):
        byte = 0
        for j in range(8):
            byte = (byte << 1) | bits[i + j]
        result.append(byte)

    return bytes(result)


def _find_insertion_point(cover_text: str) -> int:
    """Find a natural position to insert zero-width characters.

    Prefers: after the first word, between sentences, or at the
    first space. Falls back to the end of the text.

    Args:
        cover_text: The cover text to analyze.

    Returns:
        Index position for insertion.
    """
    # Try to find first space (after first word)
    first_space = cover_text.find(" ")
    if first_space > 0:
        return first_space

    # Try after first period
    first_period = cover_text.find(".")
    if first_period > 0:
        return first_period + 1

    # Fall back to end of text
    return len(cover_text)


def embed_in_text(cover_text: str, secret_message: str) -> str:
    """Embed a secret message in text using zero-width characters.

    The secret message is encoded as UTF-8 bytes, converted to binary,
    mapped to zero-width characters, and inserted at a natural position
    in the cover text. Delimiters mark the start and end of the hidden
    data.

    Args:
        cover_text: The visible text that will carry the hidden message.
        secret_message: The message to hide.

    Returns:
        The stego text containing the hidden message.

    Raises:
        SteganographyError: If the cover text is empty.
    """
    if not cover_text:
        raise SteganographyError("Cover text cannot be empty")

    message_bytes = secret_message.encode("utf-8")
    zw_payload = _START_DELIMITER + _bytes_to_zw(message_bytes) + _END_DELIMITER

    insert_pos = _find_insertion_point(cover_text)
    stego_text = cover_text[:insert_pos] + zw_payload + cover_text[insert_pos:]

    logger.info(
        "Embedded %d bytes (%d zero-width chars) in text at position %d",
        len(message_bytes), len(zw_payload), insert_pos,
    )
    return stego_text


def extract_from_text(stego_text: str) -> str:
    """Extract a hidden message from stego text.

    Finds zero-width characters between the start and end delimiters,
    converts them from binary representation back to UTF-8 text.

    Args:
        stego_text: Text potentially containing a hidden message.

    Returns:
        The extracted secret message.

    Raises:
        SteganographyError: If no hidden message is found or the
            extracted data is invalid.
    """
    # Find delimiters
    start_idx = stego_text.find(_START_DELIMITER)
    end_idx = stego_text.find(_END_DELIMITER)

    if start_idx == -1 or end_idx == -1 or end_idx <= start_idx:
        raise SteganographyError("No hidden message found in text")

    # Extract zero-width characters between delimiters
    zw_section = stego_text[start_idx + 1 : end_idx]
    message_bytes = _zw_to_bytes(zw_section)

    try:
        message = message_bytes.decode("utf-8")
    except UnicodeDecodeError as e:
        raise SteganographyError(f"Extracted data is not valid UTF-8: {e}") from e

    logger.info("Extracted %d bytes from stego text", len(message_bytes))
    return message
