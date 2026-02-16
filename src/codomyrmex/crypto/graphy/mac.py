"""Message Authentication Codes: HMAC-SHA256, Poly1305, CMAC-AES."""

from __future__ import annotations

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import cmac, hashes, hmac
from cryptography.hazmat.primitives.ciphers.algorithms import AES
from cryptography.hazmat.primitives.poly1305 import Poly1305

from codomyrmex.crypto.exceptions import CryptoError
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


def compute_hmac_sha256(data: bytes, key: bytes) -> bytes:
    """Compute HMAC-SHA256 of data.

    Args:
        data: Input data to authenticate.
        key: HMAC key (any length, but >= 32 bytes recommended).

    Returns:
        32-byte HMAC-SHA256 tag.

    Raises:
        CryptoError: On computation failure.
    """
    try:
        h = hmac.HMAC(key, hashes.SHA256())
        h.update(data)
        tag = h.finalize()
        logger.debug("HMAC-SHA256 computed, tag length=%d", len(tag))
        return tag
    except Exception as exc:
        raise CryptoError(f"HMAC-SHA256 computation failed: {exc}") from exc


def verify_hmac_sha256(data: bytes, key: bytes, expected_mac: bytes) -> bool:
    """Verify HMAC-SHA256 using constant-time comparison.

    Args:
        data: Input data to verify.
        key: HMAC key.
        expected_mac: Expected HMAC tag.

    Returns:
        True if MAC is valid, False otherwise.
    """
    try:
        h = hmac.HMAC(key, hashes.SHA256())
        h.update(data)
        h.verify(expected_mac)
        logger.debug("HMAC-SHA256 verification passed")
        return True
    except InvalidSignature:
        logger.debug("HMAC-SHA256 verification failed: invalid MAC")
        return False
    except Exception as exc:
        raise CryptoError(f"HMAC-SHA256 verification error: {exc}") from exc


def compute_poly1305(data: bytes, key: bytes) -> bytes:
    """Compute Poly1305 MAC.

    Args:
        data: Input data to authenticate.
        key: Exactly 32-byte key. Each key MUST be used only once.

    Returns:
        16-byte Poly1305 tag.

    Raises:
        CryptoError: On computation failure or invalid key size.
    """
    if len(key) != 32:
        raise CryptoError(f"Poly1305 requires exactly 32-byte key, got {len(key)} bytes")
    try:
        p = Poly1305(key)
        p.update(data)
        tag = p.finalize()
        logger.debug("Poly1305 computed, tag length=%d", len(tag))
        return tag
    except Exception as exc:
        raise CryptoError(f"Poly1305 computation failed: {exc}") from exc


def compute_cmac(data: bytes, key: bytes) -> bytes:
    """Compute CMAC-AES.

    Args:
        data: Input data to authenticate.
        key: AES key (16, 24, or 32 bytes).

    Returns:
        16-byte CMAC tag.

    Raises:
        CryptoError: On computation failure or invalid key size.
    """
    try:
        c = cmac.CMAC(AES(key))
        c.update(data)
        tag = c.finalize()
        logger.debug("CMAC-AES computed, tag length=%d", len(tag))
        return tag
    except Exception as exc:
        raise CryptoError(f"CMAC-AES computation failed: {exc}") from exc
