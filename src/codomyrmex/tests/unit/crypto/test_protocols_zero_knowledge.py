"""Tests for crypto protocols zero-knowledge proofs.

Validates Schnorr identification protocol (Fiat-Shamir) and
Pedersen commitment scheme round-trips and failure cases.
"""

from __future__ import annotations

import pytest

from codomyrmex.crypto.exceptions import ProtocolError
from codomyrmex.crypto.protocols.zero_knowledge import (
    SchnorrProof,
    pedersen_commit,
    pedersen_verify,
    schnorr_prove,
    schnorr_verify,
)

# A small safe prime for fast testing: p=23, generator g=5
# Order of g=5 in Z*_23 is 22 (primitive root).
SMALL_PRIME = 23
SMALL_GEN = 5

# A larger prime for more realistic testing: p=7919 (prime), g=7 (primitive root)
MEDIUM_PRIME = 7919
MEDIUM_GEN = 7


# ---------------------------------------------------------------------------
# Schnorr Protocol
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.crypto
class TestSchnorrProtocol:
    """Schnorr identification protocol tests."""

    def test_prove_verify_small_prime(self) -> None:
        """Valid proof with a small prime verifies correctly."""
        secret = 7
        public_value = pow(SMALL_GEN, secret, SMALL_PRIME)

        proof = schnorr_prove(secret, SMALL_GEN, SMALL_PRIME)
        assert schnorr_verify(proof, public_value, SMALL_GEN, SMALL_PRIME)

    def test_prove_verify_medium_prime(self) -> None:
        """Valid proof with a medium prime verifies correctly."""
        secret = 1234
        public_value = pow(MEDIUM_GEN, secret, MEDIUM_PRIME)

        proof = schnorr_prove(secret, MEDIUM_GEN, MEDIUM_PRIME)
        assert schnorr_verify(proof, public_value, MEDIUM_GEN, MEDIUM_PRIME)

    def test_multiple_secrets(self) -> None:
        """Different secrets all produce valid proofs."""
        for secret in [1, 3, 10, 21]:
            public_value = pow(SMALL_GEN, secret, SMALL_PRIME)
            proof = schnorr_prove(secret, SMALL_GEN, SMALL_PRIME)
            assert schnorr_verify(proof, public_value, SMALL_GEN, SMALL_PRIME)

    def test_tampered_commitment_fails(self) -> None:
        """A proof with a tampered commitment must fail."""
        secret = 7
        public_value = pow(SMALL_GEN, secret, SMALL_PRIME)
        proof = schnorr_prove(secret, SMALL_GEN, SMALL_PRIME)

        tampered = SchnorrProof(
            commitment=(proof.commitment + 1) % SMALL_PRIME,
            challenge=proof.challenge,
            response=proof.response,
        )
        assert not schnorr_verify(tampered, public_value, SMALL_GEN, SMALL_PRIME)

    def test_tampered_response_fails(self) -> None:
        """A proof with a tampered response must fail."""
        secret = 7
        public_value = pow(SMALL_GEN, secret, SMALL_PRIME)
        proof = schnorr_prove(secret, SMALL_GEN, SMALL_PRIME)

        tampered = SchnorrProof(
            commitment=proof.commitment,
            challenge=proof.challenge,
            response=(proof.response + 1) % (SMALL_PRIME - 1),
        )
        assert not schnorr_verify(tampered, public_value, SMALL_GEN, SMALL_PRIME)

    def test_wrong_public_value_fails(self) -> None:
        """Verification with a wrong public value must fail."""
        secret = 7
        # Compute the real public value, then use a different one
        real_pv = pow(SMALL_GEN, secret, SMALL_PRIME)
        wrong_pv = pow(SMALL_GEN, secret + 1, SMALL_PRIME)
        assert real_pv != wrong_pv

        proof = schnorr_prove(secret, SMALL_GEN, SMALL_PRIME)
        assert not schnorr_verify(proof, wrong_pv, SMALL_GEN, SMALL_PRIME)

    def test_invalid_inputs_raise(self) -> None:
        with pytest.raises(ProtocolError, match="Prime must be >= 3"):
            schnorr_prove(secret=5, generator=2, prime=2)
        with pytest.raises(ProtocolError, match="Secret must be >= 1"):
            schnorr_prove(secret=0, generator=2, prime=23)
        with pytest.raises(ProtocolError, match="Generator must be >= 2"):
            schnorr_prove(secret=5, generator=1, prime=23)


# ---------------------------------------------------------------------------
# Pedersen Commitments
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.crypto
class TestPedersenCommitment:
    """Pedersen commitment scheme tests."""

    # For Pedersen we need two generators g, h where log_g(h) is unknown.
    # For testing, any two distinct generators work since we are verifying
    # the math, not the security assumption.
    P_G = SMALL_GEN   # g = 5
    P_H = 4           # h = 4 (another element in Z*_23)
    P_P = SMALL_PRIME  # p = 23

    def test_commit_verify_roundtrip(self) -> None:
        """A valid commitment verifies correctly."""
        value = 10
        randomness = 13
        c = pedersen_commit(value, randomness, self.P_G, self.P_H, self.P_P)
        assert pedersen_verify(c, value, randomness, self.P_G, self.P_H, self.P_P)

    def test_different_values_different_commitments(self) -> None:
        """Different values with the same randomness yield different commitments."""
        r = 7
        c1 = pedersen_commit(3, r, self.P_G, self.P_H, self.P_P)
        c2 = pedersen_commit(5, r, self.P_G, self.P_H, self.P_P)
        assert c1 != c2

    def test_different_randomness_different_commitments(self) -> None:
        """Same value with different randomness yields different commitments."""
        v = 3
        c1 = pedersen_commit(v, 7, self.P_G, self.P_H, self.P_P)
        c2 = pedersen_commit(v, 11, self.P_G, self.P_H, self.P_P)
        assert c1 != c2

    def test_wrong_value_fails(self) -> None:
        """Verification with the wrong value must fail."""
        value = 10
        randomness = 13
        c = pedersen_commit(value, randomness, self.P_G, self.P_H, self.P_P)
        assert not pedersen_verify(c, value + 1, randomness, self.P_G, self.P_H, self.P_P)

    def test_wrong_randomness_fails(self) -> None:
        """Verification with the wrong randomness must fail."""
        value = 10
        randomness = 13
        c = pedersen_commit(value, randomness, self.P_G, self.P_H, self.P_P)
        assert not pedersen_verify(c, value, randomness + 1, self.P_G, self.P_H, self.P_P)

    def test_medium_prime(self) -> None:
        """Pedersen commitment with a larger prime."""
        g, h, p = MEDIUM_GEN, 11, MEDIUM_PRIME
        value, randomness = 500, 3000
        c = pedersen_commit(value, randomness, g, h, p)
        assert pedersen_verify(c, value, randomness, g, h, p)
        assert not pedersen_verify(c, value + 1, randomness, g, h, p)

    def test_zero_value(self) -> None:
        """Committing to zero should work (C = h^randomness mod p)."""
        randomness = 7
        c = pedersen_commit(0, randomness, self.P_G, self.P_H, self.P_P)
        expected = pow(self.P_H, randomness, self.P_P)
        assert c == expected
        assert pedersen_verify(c, 0, randomness, self.P_G, self.P_H, self.P_P)

    def test_invalid_prime_raises(self) -> None:
        with pytest.raises(ProtocolError, match="Prime must be >= 3"):
            pedersen_commit(1, 1, 2, 3, 2)
