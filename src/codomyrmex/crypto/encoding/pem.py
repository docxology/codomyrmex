"""PEM (Privacy-Enhanced Mail) encoding and decoding.

Handles the standard PEM format used for certificates, keys, and other
cryptographic material: Base64 content wrapped between typed header and
footer lines with 64-character line wrapping.
"""

from __future__ import annotations

import base64
import re
import textwrap

from codomyrmex.crypto.exceptions import EncodingError
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)

_PEM_HEADER_RE = re.compile(r"-----BEGIN ([A-Z0-9 ]+)-----")
_PEM_FOOTER_RE = re.compile(r"-----END ([A-Z0-9 ]+)-----")


def encode_pem(data: bytes, label: str) -> str:
    """Encode binary data into PEM format.

    Args:
        data: Raw bytes to encode (e.g. DER-encoded key or certificate).
        label: The PEM type label (e.g. "RSA PRIVATE KEY", "CERTIFICATE").

    Returns:
        A PEM-formatted string with BEGIN/END markers and Base64 content
        wrapped at 64 characters per line.

    Raises:
        EncodingError: If encoding fails.
    """
    try:
        b64 = base64.b64encode(data).decode("ascii")
        wrapped = textwrap.fill(b64, width=64)
        return f"-----BEGIN {label}-----\n{wrapped}\n-----END {label}-----\n"
    except Exception as exc:
        raise EncodingError(f"PEM encoding failed: {exc}") from exc


def decode_pem(pem_string: str) -> bytes:
    """Decode PEM-formatted data back to raw bytes.

    Extracts the Base64 content between the BEGIN and END markers,
    ignoring whitespace, and decodes it.

    Args:
        pem_string: A PEM-formatted string.

    Returns:
        The decoded binary data.

    Raises:
        EncodingError: If the PEM structure is invalid or decoding fails.
    """
    try:
        header_match = _PEM_HEADER_RE.search(pem_string)
        footer_match = _PEM_FOOTER_RE.search(pem_string)

        if not header_match or not footer_match:
            raise EncodingError("Invalid PEM: missing BEGIN or END marker")

        header_label = header_match.group(1)
        footer_label = footer_match.group(1)

        if header_label != footer_label:
            raise EncodingError(
                f"PEM label mismatch: BEGIN {header_label} vs END {footer_label}"
            )

        # Extract content between header and footer
        start = header_match.end()
        end = footer_match.start()
        b64_content = pem_string[start:end].strip()

        # Remove all whitespace from the Base64 content
        b64_clean = "".join(b64_content.split())

        return base64.b64decode(b64_clean)
    except EncodingError:
        raise
    except Exception as exc:
        raise EncodingError(f"PEM decoding failed: {exc}") from exc


def identify_pem_type(pem_string: str) -> str:
    """Extract the type label from a PEM-formatted string.

    Args:
        pem_string: A PEM-formatted string.

    Returns:
        The label string (e.g. "RSA PRIVATE KEY", "CERTIFICATE").

    Raises:
        EncodingError: If no valid PEM header is found.
    """
    match = _PEM_HEADER_RE.search(pem_string)
    if not match:
        raise EncodingError("No PEM header found in input")
    return match.group(1)
