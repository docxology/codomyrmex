"""LSB image steganography for hiding messages in PNG images.

Embeds secret messages into the least significant bits of pixel
color channel values. Supports PNG images with RGB or RGBA color modes.
"""

from __future__ import annotations

import struct

from PIL import Image

from codomyrmex.crypto.exceptions import SteganographyError
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


def _message_to_bits(data: bytes) -> list[int]:
    """Convert bytes to a list of individual bits."""
    bits = []
    for byte in data:
        for i in range(7, -1, -1):
            bits.append((byte >> i) & 1)
    return bits


def _bits_to_bytes(bits: list[int]) -> bytes:
    """Convert a list of bits back to bytes."""
    result = bytearray()
    for i in range(0, len(bits) - 7, 8):
        byte = 0
        for j in range(8):
            byte = (byte << 1) | bits[i + j]
        result.append(byte)
    return bytes(result)


def calculate_capacity(image_path: str) -> int:
    """Calculate the maximum message size an image can hold.

    The capacity is based on the number of color channel values
    available for LSB embedding, minus 4 bytes reserved for the
    message length header.

    Args:
        image_path: Path to the PNG image file.

    Returns:
        Maximum number of message bytes that can be embedded.

    Raises:
        SteganographyError: If the image cannot be opened.
    """
    try:
        img = Image.open(image_path)
    except Exception as e:
        raise SteganographyError(f"Cannot open image: {e}") from e

    width, height = img.size
    # 3 channels (R, G, B) per pixel, each channel stores 1 bit
    total_bits = width * height * 3
    # 4 bytes (32 bits) reserved for length header
    capacity = (total_bits // 8) - 4

    logger.debug(
        "Image capacity: %d bytes (%dx%d, %d usable bits)",
        capacity, width, height, total_bits,
    )
    return max(0, capacity)


def embed_in_image(image_path: str, message: str, output_path: str) -> bool:
    """Embed a secret message into a PNG image using LSB steganography.

    The message is encoded as UTF-8, prepended with a 4-byte big-endian
    length header, and the resulting bits are embedded into the least
    significant bit of each R, G, B channel value.

    Args:
        image_path: Path to the source PNG image.
        message: The secret message to embed.
        output_path: Path where the stego image will be saved (PNG).

    Returns:
        True on success.

    Raises:
        SteganographyError: If the message is too large for the image,
            or if the image cannot be processed.
    """
    try:
        img = Image.open(image_path)
    except Exception as e:
        raise SteganographyError(f"Cannot open image: {e}") from e

    # Convert to RGB if necessary (strip alpha, handle palette modes)
    if img.mode != "RGB":
        img = img.convert("RGB")

    width, height = img.size
    pixels = img.load()

    # Prepare payload: 4-byte length header + message bytes
    message_bytes = message.encode("utf-8")
    length_header = struct.pack(">I", len(message_bytes))
    payload = length_header + message_bytes
    payload_bits = _message_to_bits(payload)

    # Check capacity
    max_bits = width * height * 3
    if len(payload_bits) > max_bits:
        raise SteganographyError(
            f"Message too large: needs {len(payload_bits)} bits, "
            f"image has {max_bits} bits available"
        )

    # Embed bits into LSBs
    bit_idx = 0
    total_bits = len(payload_bits)

    for y in range(height):
        for x in range(width):
            if bit_idx >= total_bits:
                break

            r, g, b = pixels[x, y]

            if bit_idx < total_bits:
                r = (r & 0xFE) | payload_bits[bit_idx]
                bit_idx += 1
            if bit_idx < total_bits:
                g = (g & 0xFE) | payload_bits[bit_idx]
                bit_idx += 1
            if bit_idx < total_bits:
                b = (b & 0xFE) | payload_bits[bit_idx]
                bit_idx += 1

            pixels[x, y] = (r, g, b)

        if bit_idx >= total_bits:
            break

    img.save(output_path, "PNG")

    logger.info(
        "Embedded %d bytes in image (%dx%d), saved to %s",
        len(message_bytes), width, height, output_path,
    )
    return True


def extract_from_image(image_path: str) -> str:
    """Extract a hidden message from a PNG image.

    Reads the LSBs of R, G, B channel values. The first 32 bits
    are interpreted as a big-endian message length, then that many
    bytes of message data are read and decoded as UTF-8.

    Args:
        image_path: Path to the stego PNG image.

    Returns:
        The extracted secret message.

    Raises:
        SteganographyError: If the image cannot be read or the
            extracted data is invalid.
    """
    try:
        img = Image.open(image_path)
    except Exception as e:
        raise SteganographyError(f"Cannot open image: {e}") from e

    if img.mode != "RGB":
        img = img.convert("RGB")

    width, height = img.size
    pixels = img.load()

    # Extract all LSBs
    bits: list[int] = []
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            bits.append(r & 1)
            bits.append(g & 1)
            bits.append(b & 1)

    # Read length header (first 32 bits = 4 bytes)
    if len(bits) < 32:
        raise SteganographyError("Image too small to contain a message")

    length_bytes = _bits_to_bytes(bits[:32])
    message_length = struct.unpack(">I", length_bytes)[0]

    # Validate length
    total_available = (len(bits) - 32) // 8
    if message_length > total_available:
        raise SteganographyError(
            f"Invalid message length {message_length} (only {total_available} bytes available)"
        )

    # Read message bytes
    message_bits = bits[32 : 32 + message_length * 8]
    message_bytes = _bits_to_bytes(message_bits)

    try:
        message = message_bytes.decode("utf-8")
    except UnicodeDecodeError as e:
        raise SteganographyError(f"Extracted data is not valid UTF-8: {e}") from e

    logger.info("Extracted %d bytes from image (%dx%d)", message_length, width, height)
    return message
