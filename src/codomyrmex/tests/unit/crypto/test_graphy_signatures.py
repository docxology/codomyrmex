"""Tests for codomyrmex.crypto.graphy.signatures."""

from __future__ import annotations

import pytest

from codomyrmex.crypto.graphy.asymmetric import (
    KeyPair,
    generate_ec_keypair,
    generate_ed25519_keypair,
    generate_rsa_keypair,
)
from codomyrmex.crypto.graphy.signatures import (
    sign_ecdsa,
    sign_ed25519,
    sign_rsa_pss,
    verify_ecdsa,
    verify_ed25519,
    verify_rsa_pss,
)


@pytest.fixture(scope="module")
def ec_keypair() -> KeyPair:
    return generate_ec_keypair("secp256r1")


@pytest.fixture(scope="module")
def ed25519_keypair() -> KeyPair:
    return generate_ed25519_keypair()


@pytest.fixture(scope="module")
def rsa_keypair() -> KeyPair:
    return generate_rsa_keypair(2048)


MESSAGE = b"The quick brown fox jumps over the lazy dog"


@pytest.mark.crypto
@pytest.mark.unit
class TestECDSA:
    def test_sign_and_verify(self, ec_keypair: KeyPair) -> None:
        sig = sign_ecdsa(MESSAGE, ec_keypair.private_key)
        assert isinstance(sig, bytes)
        assert len(sig) > 0
        assert verify_ecdsa(MESSAGE, sig, ec_keypair.public_key) is True

    def test_tampered_message_fails(self, ec_keypair: KeyPair) -> None:
        sig = sign_ecdsa(MESSAGE, ec_keypair.private_key)
        assert verify_ecdsa(b"tampered message", sig, ec_keypair.public_key) is False

    def test_tampered_signature_fails(self, ec_keypair: KeyPair) -> None:
        sig = sign_ecdsa(MESSAGE, ec_keypair.private_key)
        tampered = bytearray(sig)
        tampered[-1] ^= 0xFF
        assert verify_ecdsa(MESSAGE, bytes(tampered), ec_keypair.public_key) is False

    def test_wrong_key_fails(self, ec_keypair: KeyPair) -> None:
        other = generate_ec_keypair("secp256r1")
        sig = sign_ecdsa(MESSAGE, ec_keypair.private_key)
        assert verify_ecdsa(MESSAGE, sig, other.public_key) is False

    def test_empty_message(self, ec_keypair: KeyPair) -> None:
        sig = sign_ecdsa(b"", ec_keypair.private_key)
        assert verify_ecdsa(b"", sig, ec_keypair.public_key) is True


@pytest.mark.crypto
@pytest.mark.unit
class TestEd25519:
    def test_sign_and_verify(self, ed25519_keypair: KeyPair) -> None:
        sig = sign_ed25519(MESSAGE, ed25519_keypair.private_key)
        assert isinstance(sig, bytes)
        assert len(sig) == 64
        assert verify_ed25519(MESSAGE, sig, ed25519_keypair.public_key) is True

    def test_tampered_message_fails(self, ed25519_keypair: KeyPair) -> None:
        sig = sign_ed25519(MESSAGE, ed25519_keypair.private_key)
        assert verify_ed25519(b"tampered", sig, ed25519_keypair.public_key) is False

    def test_tampered_signature_fails(self, ed25519_keypair: KeyPair) -> None:
        sig = sign_ed25519(MESSAGE, ed25519_keypair.private_key)
        tampered = bytearray(sig)
        tampered[0] ^= 0xFF
        assert verify_ed25519(MESSAGE, bytes(tampered), ed25519_keypair.public_key) is False

    def test_wrong_key_fails(self, ed25519_keypair: KeyPair) -> None:
        other = generate_ed25519_keypair()
        sig = sign_ed25519(MESSAGE, ed25519_keypair.private_key)
        assert verify_ed25519(MESSAGE, sig, other.public_key) is False


@pytest.mark.crypto
@pytest.mark.unit
class TestRSAPSS:
    def test_sign_and_verify(self, rsa_keypair: KeyPair) -> None:
        sig = sign_rsa_pss(MESSAGE, rsa_keypair.private_key)
        assert isinstance(sig, bytes)
        assert len(sig) == 256  # 2048-bit key -> 256-byte signature
        assert verify_rsa_pss(MESSAGE, sig, rsa_keypair.public_key) is True

    def test_tampered_message_fails(self, rsa_keypair: KeyPair) -> None:
        sig = sign_rsa_pss(MESSAGE, rsa_keypair.private_key)
        assert verify_rsa_pss(b"tampered", sig, rsa_keypair.public_key) is False

    def test_tampered_signature_fails(self, rsa_keypair: KeyPair) -> None:
        sig = sign_rsa_pss(MESSAGE, rsa_keypair.private_key)
        tampered = bytearray(sig)
        tampered[-1] ^= 0xFF
        assert verify_rsa_pss(MESSAGE, bytes(tampered), rsa_keypair.public_key) is False

    def test_wrong_key_fails(self, rsa_keypair: KeyPair) -> None:
        other = generate_rsa_keypair(2048)
        sig = sign_rsa_pss(MESSAGE, rsa_keypair.private_key)
        assert verify_rsa_pss(MESSAGE, sig, other.public_key) is False

    def test_different_messages_different_sigs(self, rsa_keypair: KeyPair) -> None:
        sig1 = sign_rsa_pss(b"message one", rsa_keypair.private_key)
        sig2 = sign_rsa_pss(b"message two", rsa_keypair.private_key)
        assert sig1 != sig2
