"""Tests for codomyrmex.crypto.graphy.asymmetric."""

from __future__ import annotations

import pytest
from cryptography.hazmat.primitives.asymmetric import ec, ed25519, rsa, x25519

from codomyrmex.crypto.exceptions import AsymmetricCipherError
from codomyrmex.crypto.graphy.asymmetric import (
    KeyPair,
    generate_ec_keypair,
    generate_ed25519_keypair,
    generate_rsa_keypair,
    generate_x25519_keypair,
    load_private_key,
    load_public_key,
    rsa_decrypt,
    rsa_encrypt,
    serialize_private_key,
    serialize_public_key,
)


@pytest.fixture(scope="module")
def rsa_keypair() -> KeyPair:
    """RSA-2048 for speed in tests."""
    return generate_rsa_keypair(key_size=2048)


@pytest.fixture(scope="module")
def ed25519_keypair() -> KeyPair:
    return generate_ed25519_keypair()


@pytest.fixture(scope="module")
def x25519_keypair() -> KeyPair:
    return generate_x25519_keypair()


@pytest.fixture(scope="module")
def ec_keypair() -> KeyPair:
    return generate_ec_keypair("secp256r1")


@pytest.mark.crypto
@pytest.mark.unit
class TestRSAKeypair:
    """Test suite for RSAKeypair."""
    def test_generate(self, rsa_keypair: KeyPair) -> None:
        """Test functionality: generate."""
        assert isinstance(rsa_keypair.private_key, rsa.RSAPrivateKey)
        assert isinstance(rsa_keypair.public_key, rsa.RSAPublicKey)

    def test_key_size(self, rsa_keypair: KeyPair) -> None:
        """Test functionality: key size."""
        assert rsa_keypair.private_key.key_size == 2048

    def test_encrypt_decrypt_roundtrip(self, rsa_keypair: KeyPair) -> None:
        """Test functionality: encrypt decrypt roundtrip."""
        plaintext = b"RSA roundtrip test"
        ct = rsa_encrypt(plaintext, rsa_keypair.public_key)
        assert ct != plaintext
        pt = rsa_decrypt(ct, rsa_keypair.private_key)
        assert pt == plaintext

    def test_encrypt_decrypt_empty(self, rsa_keypair: KeyPair) -> None:
        """Test functionality: encrypt decrypt empty."""
        plaintext = b""
        ct = rsa_encrypt(plaintext, rsa_keypair.public_key)
        pt = rsa_decrypt(ct, rsa_keypair.private_key)
        assert pt == plaintext

    def test_wrong_key_decrypt_fails(self, rsa_keypair: KeyPair) -> None:
        """Test functionality: wrong key decrypt fails."""
        other = generate_rsa_keypair(2048)
        ct = rsa_encrypt(b"secret", rsa_keypair.public_key)
        with pytest.raises(AsymmetricCipherError):
            rsa_decrypt(ct, other.private_key)


@pytest.mark.crypto
@pytest.mark.unit
class TestEd25519Keypair:
    """Test suite for Ed25519Keypair."""
    def test_generate(self, ed25519_keypair: KeyPair) -> None:
        """Test functionality: generate."""
        assert isinstance(ed25519_keypair.private_key, ed25519.Ed25519PrivateKey)
        assert isinstance(ed25519_keypair.public_key, ed25519.Ed25519PublicKey)


@pytest.mark.crypto
@pytest.mark.unit
class TestX25519Keypair:
    """Test suite for X25519Keypair."""
    def test_generate(self, x25519_keypair: KeyPair) -> None:
        """Test functionality: generate."""
        assert isinstance(x25519_keypair.private_key, x25519.X25519PrivateKey)
        assert isinstance(x25519_keypair.public_key, x25519.X25519PublicKey)

    def test_key_exchange(self) -> None:
        """Test functionality: key exchange."""
        alice = generate_x25519_keypair()
        bob = generate_x25519_keypair()
        shared_a = alice.private_key.exchange(bob.public_key)
        shared_b = bob.private_key.exchange(alice.public_key)
        assert shared_a == shared_b
        assert len(shared_a) == 32


@pytest.mark.crypto
@pytest.mark.unit
class TestECKeypair:
    """Test suite for ECKeypair."""
    def test_generate_secp256r1(self, ec_keypair: KeyPair) -> None:
        """Test functionality: generate secp256r1."""
        assert isinstance(ec_keypair.private_key, ec.EllipticCurvePrivateKey)
        assert isinstance(ec_keypair.public_key, ec.EllipticCurvePublicKey)

    def test_generate_secp384r1(self) -> None:
        """Test functionality: generate secp384r1."""
        kp = generate_ec_keypair("secp384r1")
        assert kp.private_key.key_size == 384

    def test_unsupported_curve(self) -> None:
        """Test functionality: unsupported curve."""
        with pytest.raises(AsymmetricCipherError, match="Unsupported curve"):
            generate_ec_keypair("brainpoolP256r1")


@pytest.mark.crypto
@pytest.mark.unit
class TestKeySerialization:
    """Test suite for KeySerialization."""
    def test_public_key_pem_roundtrip(self, rsa_keypair: KeyPair) -> None:
        """Test functionality: public key pem roundtrip."""
        pem = serialize_public_key(rsa_keypair.public_key, encoding="pem")
        assert pem.startswith(b"-----BEGIN PUBLIC KEY-----")
        loaded = load_public_key(pem)
        # Re-serialize to verify equality
        pem2 = serialize_public_key(loaded, encoding="pem")
        assert pem == pem2

    def test_public_key_der_roundtrip(self, rsa_keypair: KeyPair) -> None:
        """Test functionality: public key der roundtrip."""
        der = serialize_public_key(rsa_keypair.public_key, encoding="der")
        assert not der.startswith(b"-----")
        loaded = load_public_key(der)
        der2 = serialize_public_key(loaded, encoding="der")
        assert der == der2

    def test_private_key_pem_roundtrip(self, rsa_keypair: KeyPair) -> None:
        """Test functionality: private key pem roundtrip."""
        pem = serialize_private_key(rsa_keypair.private_key, encoding="pem")
        assert b"BEGIN PRIVATE KEY" in pem
        loaded = load_private_key(pem)
        pem2 = serialize_private_key(loaded, encoding="pem")
        assert pem == pem2

    def test_private_key_encrypted_roundtrip(self, rsa_keypair: KeyPair) -> None:
        """Test functionality: private key encrypted roundtrip."""
        password = b"test-password-123"
        pem = serialize_private_key(rsa_keypair.private_key, password=password)
        assert b"ENCRYPTED" in pem
        loaded = load_private_key(pem, password=password)
        # Verify loaded key works
        ct = rsa_encrypt(b"test", rsa_keypair.public_key)
        pt = rsa_decrypt(ct, loaded)
        assert pt == b"test"

    def test_ed25519_pem_roundtrip(self, ed25519_keypair: KeyPair) -> None:
        """Test functionality: ed25519 pem roundtrip."""
        pem = serialize_public_key(ed25519_keypair.public_key)
        loaded = load_public_key(pem)
        pem2 = serialize_public_key(loaded)
        assert pem == pem2

    def test_ec_pem_roundtrip(self, ec_keypair: KeyPair) -> None:
        """Test functionality: ec pem roundtrip."""
        pem = serialize_private_key(ec_keypair.private_key)
        loaded = load_private_key(pem)
        pem2 = serialize_private_key(loaded)
        assert pem == pem2

    def test_load_invalid_data(self) -> None:
        """Test functionality: load invalid data."""
        with pytest.raises(AsymmetricCipherError):
            load_public_key(b"not a key")

    def test_load_wrong_password(self, rsa_keypair: KeyPair) -> None:
        """Test functionality: load wrong password."""
        pem = serialize_private_key(rsa_keypair.private_key, password=b"correct")
        with pytest.raises(AsymmetricCipherError):
            load_private_key(pem, password=b"wrong")
