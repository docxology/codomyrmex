"""HMAC utilities for message authentication.

Provides HMAC computation and constant-time verification using the
standard library ``hmac`` module.
"""

import hashlib
import hmac as _hmac

_ALGORITHMS = {
    "sha256": hashlib.sha256,
    "sha384": hashlib.sha384,
    "sha512": hashlib.sha512,
}


def compute_hmac(
    data: bytes | str,
    key: bytes | str,
    algorithm: str = "sha256",
) -> bytes:
    """Compute an HMAC digest.

    Args:
        data: Message data (str will be UTF-8 encoded)
        key: Secret key (str will be UTF-8 encoded)
        algorithm: Hash algorithm name (sha256, sha384, sha512)

    Returns:
        Raw HMAC digest bytes

    Raises:
        ValueError: If algorithm is not supported
    """
    if algorithm not in _ALGORITHMS:
        raise ValueError(
            f"Unsupported algorithm: {algorithm}. "
            f"Choose from: {', '.join(sorted(_ALGORITHMS))}"
        )
    if isinstance(data, str):
        data = data.encode("utf-8")
    if isinstance(key, str):
        key = key.encode("utf-8")

    return _hmac.new(key, data, _ALGORITHMS[algorithm]).digest()


def verify_hmac(
    data: bytes | str,
    key: bytes | str,
    expected_mac: bytes,
    algorithm: str = "sha256",
) -> bool:
    """Verify an HMAC using constant-time comparison.

    Args:
        data: Original message data
        key: Secret key
        expected_mac: The HMAC to verify against
        algorithm: Hash algorithm name

    Returns:
        True if the HMAC matches
    """
    actual_mac = compute_hmac(data, key, algorithm)
    return _hmac.compare_digest(actual_mac, expected_mac)
