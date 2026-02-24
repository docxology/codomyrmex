"""Tests for codomyrmex.crypto.graphy.symmetric."""

from __future__ import annotations

import pytest

from codomyrmex.crypto.exceptions import SymmetricCipherError
from codomyrmex.crypto.graphy.symmetric import (
    CipherResult,
    decrypt_aes_gcm,
    decrypt_chacha20,
    encrypt_aes_gcm,
    encrypt_chacha20,
    generate_symmetric_key,
)


@pytest.fixture
def aes_key_128() -> bytes:
    return generate_symmetric_key(128)


@pytest.fixture
def aes_key_256() -> bytes:
    return generate_symmetric_key(256)


@pytest.fixture
def chacha_key() -> bytes:
    return generate_symmetric_key(256)


@pytest.mark.crypto
@pytest.mark.unit
class TestGenerateSymmetricKey:
    """Test suite for GenerateSymmetricKey."""
    def test_key_128(self) -> None:
        """Test functionality: key 128."""
        key = generate_symmetric_key(128)
        assert len(key) == 16

    def test_key_192(self) -> None:
        """Test functionality: key 192."""
        key = generate_symmetric_key(192)
        assert len(key) == 24

    def test_key_256(self) -> None:
        """Test functionality: key 256."""
        key = generate_symmetric_key(256)
        assert len(key) == 32

    def test_invalid_key_size(self) -> None:
        """Test functionality: invalid key size."""
        with pytest.raises(SymmetricCipherError, match="Invalid key size"):
            generate_symmetric_key(512)

    def test_keys_are_unique(self) -> None:
        """Test functionality: keys are unique."""
        k1 = generate_symmetric_key(256)
        k2 = generate_symmetric_key(256)
        assert k1 != k2


@pytest.mark.crypto
@pytest.mark.unit
class TestAESGCM:
    """Test suite for AESGCM."""
    def test_encrypt_decrypt_roundtrip(self, aes_key_256: bytes) -> None:
        """Test functionality: encrypt decrypt roundtrip."""
        plaintext = b"Hello, AES-GCM world!"
        result = encrypt_aes_gcm(plaintext, aes_key_256)
        assert isinstance(result, CipherResult)
        assert result.ciphertext != plaintext
        assert len(result.nonce) == 12
        assert len(result.tag) == 16

        decrypted = decrypt_aes_gcm(
            result.ciphertext, aes_key_256, result.nonce, result.tag
        )
        assert decrypted == plaintext

    def test_encrypt_decrypt_with_aad(self, aes_key_256: bytes) -> None:
        """Test functionality: encrypt decrypt with aad."""
        plaintext = b"Authenticated data test"
        aad = b"additional context"
        result = encrypt_aes_gcm(plaintext, aes_key_256, aad=aad)
        decrypted = decrypt_aes_gcm(
            result.ciphertext, aes_key_256, result.nonce, result.tag, aad=aad
        )
        assert decrypted == plaintext

    def test_wrong_aad_fails(self, aes_key_256: bytes) -> None:
        """Test functionality: wrong aad fails."""
        plaintext = b"AAD mismatch test"
        aad = b"correct aad"
        result = encrypt_aes_gcm(plaintext, aes_key_256, aad=aad)
        with pytest.raises(SymmetricCipherError):
            decrypt_aes_gcm(
                result.ciphertext, aes_key_256, result.nonce, result.tag, aad=b"wrong aad"
            )

    def test_wrong_key_fails(self, aes_key_256: bytes) -> None:
        """Test functionality: wrong key fails."""
        plaintext = b"Wrong key test"
        result = encrypt_aes_gcm(plaintext, aes_key_256)
        wrong_key = generate_symmetric_key(256)
        with pytest.raises(SymmetricCipherError):
            decrypt_aes_gcm(result.ciphertext, wrong_key, result.nonce, result.tag)

    def test_tampered_ciphertext_fails(self, aes_key_256: bytes) -> None:
        """Test functionality: tampered ciphertext fails."""
        plaintext = b"Tamper detection test"
        result = encrypt_aes_gcm(plaintext, aes_key_256)
        tampered = bytearray(result.ciphertext)
        if tampered:
            tampered[0] ^= 0xFF
        with pytest.raises(SymmetricCipherError):
            decrypt_aes_gcm(bytes(tampered), aes_key_256, result.nonce, result.tag)

    def test_128_bit_key(self, aes_key_128: bytes) -> None:
        """Test functionality: 128 bit key."""
        plaintext = b"128-bit key test"
        result = encrypt_aes_gcm(plaintext, aes_key_128)
        decrypted = decrypt_aes_gcm(
            result.ciphertext, aes_key_128, result.nonce, result.tag
        )
        assert decrypted == plaintext

    def test_empty_plaintext(self, aes_key_256: bytes) -> None:
        """Test functionality: empty plaintext."""
        plaintext = b""
        result = encrypt_aes_gcm(plaintext, aes_key_256)
        decrypted = decrypt_aes_gcm(
            result.ciphertext, aes_key_256, result.nonce, result.tag
        )
        assert decrypted == plaintext

    def test_large_plaintext(self, aes_key_256: bytes) -> None:
        """Test functionality: large plaintext."""
        plaintext = b"A" * 1_000_000
        result = encrypt_aes_gcm(plaintext, aes_key_256)
        decrypted = decrypt_aes_gcm(
            result.ciphertext, aes_key_256, result.nonce, result.tag
        )
        assert decrypted == plaintext


@pytest.mark.crypto
@pytest.mark.unit
class TestChaCha20:
    """Test suite for ChaCha20."""
    def test_encrypt_decrypt_roundtrip(self, chacha_key: bytes) -> None:
        """Test functionality: encrypt decrypt roundtrip."""
        plaintext = b"Hello, ChaCha20-Poly1305!"
        result = encrypt_chacha20(plaintext, chacha_key)
        assert isinstance(result, CipherResult)
        assert result.ciphertext != plaintext
        assert len(result.nonce) == 12
        assert len(result.tag) == 16

        decrypted = decrypt_chacha20(
            result.ciphertext, chacha_key, result.nonce, result.tag
        )
        assert decrypted == plaintext

    def test_encrypt_decrypt_with_aad(self, chacha_key: bytes) -> None:
        """Test functionality: encrypt decrypt with aad."""
        plaintext = b"ChaCha20 AAD test"
        aad = b"extra context"
        result = encrypt_chacha20(plaintext, chacha_key, aad=aad)
        decrypted = decrypt_chacha20(
            result.ciphertext, chacha_key, result.nonce, result.tag, aad=aad
        )
        assert decrypted == plaintext

    def test_wrong_key_fails(self, chacha_key: bytes) -> None:
        """Test functionality: wrong key fails."""
        plaintext = b"Wrong key test"
        result = encrypt_chacha20(plaintext, chacha_key)
        wrong_key = generate_symmetric_key(256)
        with pytest.raises(SymmetricCipherError):
            decrypt_chacha20(result.ciphertext, wrong_key, result.nonce, result.tag)

    def test_tampered_ciphertext_fails(self, chacha_key: bytes) -> None:
        """Test functionality: tampered ciphertext fails."""
        plaintext = b"Tamper detection"
        result = encrypt_chacha20(plaintext, chacha_key)
        tampered = bytearray(result.ciphertext)
        if tampered:
            tampered[0] ^= 0xFF
        with pytest.raises(SymmetricCipherError):
            decrypt_chacha20(bytes(tampered), chacha_key, result.nonce, result.tag)

    def test_empty_plaintext(self, chacha_key: bytes) -> None:
        """Test functionality: empty plaintext."""
        plaintext = b""
        result = encrypt_chacha20(plaintext, chacha_key)
        decrypted = decrypt_chacha20(
            result.ciphertext, chacha_key, result.nonce, result.tag
        )
        assert decrypted == plaintext
