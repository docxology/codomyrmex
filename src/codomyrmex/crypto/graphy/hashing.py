"""Cryptographic hash functions: SHA-256, SHA-3, SHA-512, BLAKE2b, MD5."""

from __future__ import annotations

import enum
import warnings

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.hashes import HashAlgorithm as _CryptoHashAlgorithm

from codomyrmex.crypto.exceptions import HashError
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class HashAlgorithm(enum.Enum):
    """Supported hash algorithms."""

    SHA256 = "sha256"
    SHA3_256 = "sha3_256"
    SHA512 = "sha512"
    BLAKE2B = "blake2b"
    MD5 = "md5"


def _compute_hash(data: bytes, algorithm: _CryptoHashAlgorithm) -> str:
    """Compute a hash digest and return hex string."""
    from cryptography.hazmat.backends import default_backend

    digest = hashes.Hash(algorithm, backend=default_backend())
    digest.update(data)
    return digest.finalize().hex()


def hash_sha256(data: bytes) -> str:
    """Compute SHA-256 hash.

    Args:
        data: Input bytes to hash.

    Returns:
        Hex-encoded digest string.

    Raises:
        HashError: On hashing failure.
    """
    try:
        result = _compute_hash(data, hashes.SHA256())
        logger.debug("SHA-256 hash computed, digest length=%d", len(result))
        return result
    except Exception as exc:
        raise HashError(f"SHA-256 hashing failed: {exc}") from exc


def hash_sha3_256(data: bytes) -> str:
    """Compute SHA-3-256 hash.

    Args:
        data: Input bytes to hash.

    Returns:
        Hex-encoded digest string.

    Raises:
        HashError: On hashing failure.
    """
    try:
        result = _compute_hash(data, hashes.SHA3_256())
        logger.debug("SHA-3-256 hash computed, digest length=%d", len(result))
        return result
    except Exception as exc:
        raise HashError(f"SHA-3-256 hashing failed: {exc}") from exc


def hash_sha512(data: bytes) -> str:
    """Compute SHA-512 hash.

    Args:
        data: Input bytes to hash.

    Returns:
        Hex-encoded digest string.

    Raises:
        HashError: On hashing failure.
    """
    try:
        result = _compute_hash(data, hashes.SHA512())
        logger.debug("SHA-512 hash computed, digest length=%d", len(result))
        return result
    except Exception as exc:
        raise HashError(f"SHA-512 hashing failed: {exc}") from exc


def hash_blake2b(data: bytes, digest_size: int = 32) -> str:
    """Compute BLAKE2b hash.

    Uses hashlib.blake2b which supports variable digest sizes (1-64 bytes),
    unlike the cryptography library's BLAKE2b which only supports 64.

    Args:
        data: Input bytes to hash.
        digest_size: Output digest size in bytes (1-64). Default 32.

    Returns:
        Hex-encoded digest string.

    Raises:
        HashError: On hashing failure or invalid digest size.
    """
    import hashlib

    if not 1 <= digest_size <= 64:
        raise HashError(f"BLAKE2b digest_size must be 1-64, got {digest_size}")
    try:
        h = hashlib.blake2b(data, digest_size=digest_size)
        result = h.hexdigest()
        logger.debug("BLAKE2b hash computed, digest_size=%d", digest_size)
        return result
    except Exception as exc:
        raise HashError(f"BLAKE2b hashing failed: {exc}") from exc


def hash_md5(data: bytes) -> str:
    """Compute MD5 hash.

    .. deprecated::
        MD5 is cryptographically broken. Use SHA-256 or better for security.

    Args:
        data: Input bytes to hash.

    Returns:
        Hex-encoded digest string.

    Raises:
        HashError: On hashing failure.
    """
    warnings.warn(
        "MD5 is cryptographically broken and should not be used for security purposes. "
        "Use hash_sha256() or hash_sha3_256() instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    try:
        result = _compute_hash(data, hashes.MD5())
        logger.debug("MD5 hash computed (DEPRECATED)")
        return result
    except Exception as exc:
        raise HashError(f"MD5 hashing failed: {exc}") from exc


_DISPATCH: dict[str, object] = {
    "sha256": hash_sha256,
    "sha3_256": hash_sha3_256,
    "sha512": hash_sha512,
    "blake2b": hash_blake2b,
    "md5": hash_md5,
}


def hash_data(data: bytes, algorithm: str = "sha256") -> str:
    """Compute hash using the specified algorithm.

    Args:
        data: Input bytes to hash.
        algorithm: Algorithm name (sha256, sha3_256, sha512, blake2b, md5).

    Returns:
        Hex-encoded digest string.

    Raises:
        HashError: If algorithm is unknown or hashing fails.
    """
    func = _DISPATCH.get(algorithm)
    if func is None:
        raise HashError(
            f"Unknown hash algorithm: {algorithm}. "
            f"Supported: {', '.join(_DISPATCH)}"
        )
    return func(data)  # type: ignore[operator]


def verify_hash(data: bytes, expected_hash: str, algorithm: str = "sha256") -> bool:
    """Verify that data matches an expected hash.

    Uses constant-time comparison to prevent timing attacks.

    Args:
        data: Input bytes to verify.
        expected_hash: Expected hex-encoded digest.
        algorithm: Algorithm name.

    Returns:
        True if hashes match, False otherwise.
    """
    import hmac as _hmac

    computed = hash_data(data, algorithm)
    result = _hmac.compare_digest(computed, expected_hash)
    logger.debug("Hash verification %s for algorithm %s", "passed" if result else "failed", algorithm)
    return result
