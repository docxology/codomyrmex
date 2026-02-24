"""Tests for crypto protocols key exchange (DH and ECDH).

Validates Diffie-Hellman and X25519 ECDH key generation,
shared secret agreement, and error handling.
"""

from __future__ import annotations

import pytest

from codomyrmex.crypto.exceptions import ProtocolError
from codomyrmex.crypto.protocols.key_exchange import (
    DHKeyPair,
    ECDHKeyPair,
    dh_compute_shared_secret,
    dh_generate_keypair,
    dh_generate_parameters,
    ecdh_compute_shared_secret,
    ecdh_generate_keypair,
)


# ---------------------------------------------------------------------------
# Diffie-Hellman
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.crypto
class TestDHKeyExchange:
    """Classical Diffie-Hellman key exchange tests."""

    @pytest.fixture(scope="class")
    def dh_params(self):
        """Generate DH parameters once for the entire test class (slow)."""
        return dh_generate_parameters(key_size=1024)

    def test_generate_parameters_returns_parameters(self, dh_params) -> None:
        """Test functionality: generate parameters returns parameters."""
        from cryptography.hazmat.primitives.asymmetric import dh

        assert isinstance(dh_params, dh.DHParameters)

    def test_generate_keypair_returns_dh_keypair(self, dh_params) -> None:
        """Test functionality: generate keypair returns dh keypair."""
        kp = dh_generate_keypair(dh_params)
        assert isinstance(kp, DHKeyPair)
        assert kp.parameters is dh_params

    def test_shared_secret_agreement(self, dh_params) -> None:
        """Two parties using the same parameters must derive the same shared secret."""
        alice = dh_generate_keypair(dh_params)
        bob = dh_generate_keypair(dh_params)

        secret_alice = dh_compute_shared_secret(alice.private_key, bob.public_key)
        secret_bob = dh_compute_shared_secret(bob.private_key, alice.public_key)

        assert secret_alice == secret_bob
        assert len(secret_alice) > 0

    def test_different_keypairs_yield_different_public_keys(self, dh_params) -> None:
        """Test functionality: different keypairs yield different public keys."""
        from cryptography.hazmat.primitives.serialization import (
            Encoding,
            PublicFormat,
        )

        kp1 = dh_generate_keypair(dh_params)
        kp2 = dh_generate_keypair(dh_params)
        pub1 = kp1.public_key.public_bytes(Encoding.DER, PublicFormat.SubjectPublicKeyInfo)
        pub2 = kp2.public_key.public_bytes(Encoding.DER, PublicFormat.SubjectPublicKeyInfo)
        assert pub1 != pub2

    def test_invalid_key_size_raises(self) -> None:
        """Test functionality: invalid key size raises."""
        with pytest.raises(ProtocolError, match="key_size must be >= 512"):
            dh_generate_parameters(key_size=128)


# ---------------------------------------------------------------------------
# ECDH (X25519)
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.crypto
class TestECDHKeyExchange:
    """X25519 Elliptic Curve Diffie-Hellman tests."""

    def test_generate_keypair_returns_ecdh_keypair(self) -> None:
        """Test functionality: generate keypair returns ecdh keypair."""
        kp = ecdh_generate_keypair()
        assert isinstance(kp, ECDHKeyPair)

    def test_shared_secret_agreement(self) -> None:
        """Two X25519 parties must derive the same 32-byte shared secret."""
        alice = ecdh_generate_keypair()
        bob = ecdh_generate_keypair()

        secret_alice = ecdh_compute_shared_secret(alice.private_key, bob.public_key)
        secret_bob = ecdh_compute_shared_secret(bob.private_key, alice.public_key)

        assert secret_alice == secret_bob
        assert len(secret_alice) == 32

    def test_shared_secret_is_32_bytes(self) -> None:
        """Test functionality: shared secret is 32 bytes."""
        alice = ecdh_generate_keypair()
        bob = ecdh_generate_keypair()
        secret = ecdh_compute_shared_secret(alice.private_key, bob.public_key)
        assert len(secret) == 32

    def test_different_keypairs_yield_different_secrets(self) -> None:
        """Test functionality: different keypairs yield different secrets."""
        alice = ecdh_generate_keypair()
        bob = ecdh_generate_keypair()
        carol = ecdh_generate_keypair()

        secret_ab = ecdh_compute_shared_secret(alice.private_key, bob.public_key)
        secret_ac = ecdh_compute_shared_secret(alice.private_key, carol.public_key)

        assert secret_ab != secret_ac
