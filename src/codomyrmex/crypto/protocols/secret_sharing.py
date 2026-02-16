"""Shamir's Secret Sharing over a prime field.

Implements (k, n) threshold secret sharing where any k shares can
reconstruct the original secret, but k-1 shares reveal no information.
Uses Lagrange interpolation over GF(p) for reconstruction.
"""

from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass

from codomyrmex.crypto.exceptions import ProtocolError
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)

# A 256-bit prime suitable for the finite field.
# This is 2^256 - 189, a well-known 256-bit prime.
PRIME = (2**256) - 189


@dataclass
class Share:
    """A single share in a Shamir secret sharing scheme.

    Attributes:
        index: The x-coordinate (evaluation point), a positive integer.
        value: The y-coordinate (polynomial evaluation), an integer mod PRIME.
    """

    index: int
    value: int


def _int_from_bytes(data: bytes) -> int:
    """Convert bytes to a non-negative integer (big-endian)."""
    return int.from_bytes(data, byteorder="big")


def _int_to_bytes(n: int) -> bytes:
    """Convert a non-negative integer to bytes (big-endian).

    Returns at least 1 byte even for zero.
    """
    if n == 0:
        return b"\x00"
    byte_length = (n.bit_length() + 7) // 8
    return n.to_bytes(byte_length, byteorder="big")


def _evaluate_polynomial(coefficients: list[int], x: int, prime: int) -> int:
    """Evaluate a polynomial at point x modulo prime using Horner's method.

    Args:
        coefficients: [a_0, a_1, ..., a_{k-1}] where a_0 is the constant term.
        x: The evaluation point.
        prime: The field prime.

    Returns:
        The polynomial value at x, mod prime.
    """
    result = 0
    for coeff in reversed(coefficients):
        result = (result * x + coeff) % prime
    return result


def split_secret(secret: bytes, n: int, k: int) -> list[Share]:
    """Split a secret into n shares with a threshold of k.

    Any k shares can reconstruct the secret; fewer than k shares
    reveal no information about the secret (information-theoretic security).

    Args:
        secret: The secret bytes to split. Must be non-empty and
            represent a value less than PRIME.
        n: Total number of shares to generate. Must be >= k.
        k: Minimum number of shares required for reconstruction. Must be >= 2.

    Returns:
        A list of n Share objects.

    Raises:
        ProtocolError: If parameters are invalid or secret is too large.
    """
    if k < 2:
        raise ProtocolError(f"Threshold k must be >= 2, got {k}")
    if n < k:
        raise ProtocolError(
            f"Total shares n must be >= threshold k, got n={n}, k={k}"
        )
    if not secret:
        raise ProtocolError("Secret must not be empty")

    secret_int = _int_from_bytes(secret)
    if secret_int >= PRIME:
        raise ProtocolError(
            "Secret is too large for the field (must be < PRIME)"
        )

    logger.debug("Splitting secret into %d shares with threshold %d", n, k)

    # Build polynomial: f(x) = secret + a1*x + a2*x^2 + ... + a_{k-1}*x^{k-1}
    coefficients = [secret_int]
    for _ in range(k - 1):
        coefficients.append(secrets.randbelow(PRIME))

    shares = []
    for i in range(1, n + 1):
        y = _evaluate_polynomial(coefficients, i, PRIME)
        shares.append(Share(index=i, value=y))

    logger.info("Secret split into %d shares (threshold=%d)", n, k)
    return shares


def reconstruct_secret(shares: list[Share]) -> bytes:
    """Reconstruct a secret from k or more shares using Lagrange interpolation.

    The shares must be from the same split_secret invocation and there
    must be at least k shares (the original threshold).

    Args:
        shares: A list of Share objects. Must contain at least 2 shares
            with distinct indices.

    Returns:
        The reconstructed secret as bytes.

    Raises:
        ProtocolError: If shares are invalid or reconstruction fails.
    """
    if len(shares) < 2:
        raise ProtocolError("Need at least 2 shares for reconstruction")

    indices = [s.index for s in shares]
    if len(set(indices)) != len(indices):
        raise ProtocolError("All share indices must be distinct")

    logger.debug("Reconstructing secret from %d shares", len(shares))

    # Lagrange interpolation at x=0
    secret_int = 0
    for i, share_i in enumerate(shares):
        x_i = share_i.index
        y_i = share_i.value

        # Compute Lagrange basis polynomial L_i(0)
        numerator = 1
        denominator = 1
        for j, share_j in enumerate(shares):
            if i == j:
                continue
            x_j = share_j.index
            numerator = (numerator * (0 - x_j)) % PRIME
            denominator = (denominator * (x_i - x_j)) % PRIME

        # Modular inverse of denominator
        lagrange_coeff = (numerator * pow(denominator, -1, PRIME)) % PRIME
        secret_int = (secret_int + y_i * lagrange_coeff) % PRIME

    result = _int_to_bytes(secret_int)
    logger.info("Secret reconstructed successfully (%d bytes)", len(result))
    return result


def generate_share_commitment(share: Share) -> bytes:
    """Generate a commitment for a share (simplified Feldman-style).

    This creates a SHA-256 hash binding the share index to its value,
    which can later be used to verify the share has not been tampered with.

    Args:
        share: The share to commit to.

    Returns:
        A 32-byte SHA-256 commitment.
    """
    logger.debug("Generating commitment for share index=%d", share.index)
    h = hashlib.sha256()
    h.update(share.index.to_bytes(4, byteorder="big"))
    h.update(_int_to_bytes(share.value))
    return h.digest()


def verify_share(share: Share, commitment: bytes) -> bool:
    """Verify a share against a previously generated commitment.

    Args:
        share: The share to verify.
        commitment: The SHA-256 commitment from generate_share_commitment.

    Returns:
        True if the share matches the commitment, False otherwise.
    """
    logger.debug("Verifying share index=%d against commitment", share.index)
    expected = generate_share_commitment(share)
    is_valid = secrets.compare_digest(expected, commitment)
    if is_valid:
        logger.info("Share index=%d verified successfully", share.index)
    else:
        logger.warning("Share index=%d failed verification", share.index)
    return is_valid
