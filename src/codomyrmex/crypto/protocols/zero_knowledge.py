"""Zero-knowledge proof primitives: Schnorr protocol and Pedersen commitments.

Implements the Schnorr identification protocol (non-interactive via
Fiat-Shamir heuristic) and Pedersen commitment scheme for use in
privacy-preserving cryptographic protocols.
"""

from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass

from codomyrmex.crypto.exceptions import ProtocolError
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


@dataclass
class SchnorrProof:
    """A non-interactive Schnorr proof of knowledge of a discrete logarithm.

    Attributes:
        commitment: g^r mod p, the prover's commitment.
        challenge: Hash-derived challenge value.
        response: r + challenge * secret mod order, the prover's response.
    """

    commitment: int
    challenge: int
    response: int


def _hash_to_int(*values: int) -> int:
    """Hash a sequence of integers into a single integer via SHA-256.

    Each integer is encoded as a variable-length big-endian byte string
    prefixed with its 4-byte length, ensuring unambiguous concatenation.
    """
    h = hashlib.sha256()
    for v in values:
        v_bytes = v.to_bytes((v.bit_length() + 7) // 8 or 1, byteorder="big")
        h.update(len(v_bytes).to_bytes(4, byteorder="big"))
        h.update(v_bytes)
    return int.from_bytes(h.digest(), byteorder="big")


def schnorr_prove(secret: int, generator: int, prime: int) -> SchnorrProof:
    """Create a non-interactive Schnorr proof of knowledge of a discrete log.

    Proves knowledge of `secret` such that `public_value = generator^secret mod prime`
    without revealing `secret`, using the Fiat-Shamir heuristic.

    Args:
        secret: The secret exponent (discrete logarithm).
        generator: A generator of the multiplicative group mod prime.
        prime: A prime modulus defining the group.

    Returns:
        A SchnorrProof that can be verified with schnorr_verify.

    Raises:
        ProtocolError: If inputs are invalid.
    """
    if prime < 3:
        raise ProtocolError(f"Prime must be >= 3, got {prime}")
    if secret < 1:
        raise ProtocolError(f"Secret must be >= 1, got {secret}")
    if generator < 2:
        raise ProtocolError(f"Generator must be >= 2, got {generator}")

    order = prime - 1  # For a prime p, the group order is p-1

    logger.debug("Creating Schnorr proof (prime bit-length=%d)", prime.bit_length())

    # Public value: g^secret mod p
    public_value = pow(generator, secret, prime)

    # Random nonce r in [1, order-1]
    r = secrets.randbelow(order - 1) + 1

    # Commitment: g^r mod p
    commitment = pow(generator, r, prime)

    # Fiat-Shamir challenge: H(g || public_value || commitment) mod order
    challenge = _hash_to_int(generator, public_value, commitment) % order
    if challenge == 0:
        # Extremely unlikely but handle it: ensure non-zero challenge
        challenge = 1

    # Response: (r + challenge * secret) mod order
    response = (r + challenge * secret) % order

    logger.info("Schnorr proof created successfully")
    return SchnorrProof(
        commitment=commitment,
        challenge=challenge,
        response=response,
    )


def schnorr_verify(
    proof: SchnorrProof,
    public_value: int,
    generator: int,
    prime: int,
) -> bool:
    """Verify a non-interactive Schnorr proof.

    Checks that the prover knows the discrete logarithm of public_value
    with respect to generator in the group mod prime.

    Args:
        proof: The SchnorrProof to verify.
        public_value: g^secret mod prime (the public key).
        generator: The group generator used during proof creation.
        prime: The prime modulus defining the group.

    Returns:
        True if the proof is valid, False otherwise.
    """
    order = prime - 1

    logger.debug("Verifying Schnorr proof")

    # Recompute challenge from public parameters
    expected_challenge = _hash_to_int(generator, public_value, proof.commitment) % order
    if expected_challenge == 0:
        expected_challenge = 1

    if proof.challenge != expected_challenge:
        logger.warning("Schnorr verification failed: challenge mismatch")
        return False

    # Verify: g^response == commitment * public_value^challenge (mod p)
    lhs = pow(generator, proof.response, prime)
    rhs = (proof.commitment * pow(public_value, proof.challenge, prime)) % prime

    is_valid = lhs == rhs
    if is_valid:
        logger.info("Schnorr proof verified successfully")
    else:
        logger.warning("Schnorr verification failed: equation check failed")
    return is_valid


def pedersen_commit(
    value: int,
    randomness: int,
    g: int,
    h: int,
    p: int,
) -> int:
    """Create a Pedersen commitment.

    Computes C = g^value * h^randomness mod p. The commitment is:
    - Hiding: C reveals no information about value without knowing randomness.
    - Binding: Cannot find (value', randomness') != (value, randomness) with same C
      (under the discrete log assumption).

    Args:
        value: The value to commit to.
        randomness: Random blinding factor.
        g: First generator of the group.
        h: Second generator (must be chosen such that log_g(h) is unknown).
        p: Prime modulus.

    Returns:
        The commitment integer C = g^value * h^randomness mod p.

    Raises:
        ProtocolError: If inputs are invalid.
    """
    if p < 3:
        raise ProtocolError(f"Prime must be >= 3, got {p}")

    logger.debug("Creating Pedersen commitment")
    commitment = (pow(g, value, p) * pow(h, randomness, p)) % p
    logger.info("Pedersen commitment created")
    return commitment


def pedersen_verify(
    commitment: int,
    value: int,
    randomness: int,
    g: int,
    h: int,
    p: int,
) -> bool:
    """Verify a Pedersen commitment opening.

    Checks that commitment == g^value * h^randomness mod p.

    Args:
        commitment: The commitment to verify.
        value: The claimed committed value.
        randomness: The claimed blinding factor.
        g: First generator.
        h: Second generator.
        p: Prime modulus.

    Returns:
        True if the commitment is valid for the given value and randomness.
    """
    logger.debug("Verifying Pedersen commitment")
    expected = (pow(g, value, p) * pow(h, randomness, p)) % p
    is_valid = commitment == expected
    if is_valid:
        logger.info("Pedersen commitment verified successfully")
    else:
        logger.warning("Pedersen commitment verification failed")
    return is_valid
