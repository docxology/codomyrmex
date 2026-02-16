"""Symmetric encryption primitives: AES-GCM and ChaCha20-Poly1305."""

from __future__ import annotations

import os
from dataclasses import dataclass

from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305

from codomyrmex.crypto.exceptions import SymmetricCipherError
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)

_NONCE_SIZE = 12  # 96-bit nonce for both AES-GCM and ChaCha20-Poly1305


@dataclass(frozen=True)
class CipherResult:
    """Result of a symmetric encryption operation."""

    ciphertext: bytes
    nonce: bytes
    tag: bytes


def generate_symmetric_key(key_size: int = 256) -> bytes:
    """Generate a cryptographically secure random symmetric key.

    Args:
        key_size: Key size in bits. Must be 128, 192, or 256.

    Returns:
        Random key bytes.

    Raises:
        SymmetricCipherError: If key_size is invalid.
    """
    if key_size not in (128, 192, 256):
        raise SymmetricCipherError(f"Invalid key size: {key_size}. Must be 128, 192, or 256.")
    logger.debug("Generating %d-bit symmetric key", key_size)
    return os.urandom(key_size // 8)


def encrypt_aes_gcm(
    plaintext: bytes,
    key: bytes,
    aad: bytes | None = None,
) -> CipherResult:
    """Encrypt data using AES-GCM.

    Args:
        plaintext: Data to encrypt.
        key: AES key (16, 24, or 32 bytes).
        aad: Optional additional authenticated data.

    Returns:
        CipherResult containing ciphertext, nonce, and authentication tag.

    Raises:
        SymmetricCipherError: On encryption failure.
    """
    try:
        nonce = os.urandom(_NONCE_SIZE)
        aesgcm = AESGCM(key)
        # AESGCM.encrypt returns ciphertext || tag (tag is last 16 bytes)
        ct_with_tag = aesgcm.encrypt(nonce, plaintext, aad)
        ciphertext = ct_with_tag[:-16]
        tag = ct_with_tag[-16:]
        logger.debug("AES-GCM encryption complete, ciphertext length=%d", len(ciphertext))
        return CipherResult(ciphertext=ciphertext, nonce=nonce, tag=tag)
    except Exception as exc:
        raise SymmetricCipherError(f"AES-GCM encryption failed: {exc}") from exc


def decrypt_aes_gcm(
    ciphertext: bytes,
    key: bytes,
    nonce: bytes,
    tag: bytes,
    aad: bytes | None = None,
) -> bytes:
    """Decrypt data using AES-GCM.

    Args:
        ciphertext: Encrypted data (without tag).
        key: AES key matching the one used for encryption.
        nonce: Nonce used during encryption.
        tag: Authentication tag from encryption.
        aad: Optional additional authenticated data (must match encryption).

    Returns:
        Decrypted plaintext bytes.

    Raises:
        SymmetricCipherError: On decryption or authentication failure.
    """
    try:
        aesgcm = AESGCM(key)
        # AESGCM.decrypt expects ciphertext || tag
        ct_with_tag = ciphertext + tag
        plaintext = aesgcm.decrypt(nonce, ct_with_tag, aad)
        logger.debug("AES-GCM decryption complete, plaintext length=%d", len(plaintext))
        return plaintext
    except Exception as exc:
        raise SymmetricCipherError(f"AES-GCM decryption failed: {exc}") from exc


def encrypt_chacha20(
    plaintext: bytes,
    key: bytes,
    aad: bytes | None = None,
) -> CipherResult:
    """Encrypt data using ChaCha20-Poly1305.

    Args:
        plaintext: Data to encrypt.
        key: 32-byte key.
        aad: Optional additional authenticated data.

    Returns:
        CipherResult containing ciphertext, nonce, and authentication tag.

    Raises:
        SymmetricCipherError: On encryption failure.
    """
    try:
        nonce = os.urandom(_NONCE_SIZE)
        chacha = ChaCha20Poly1305(key)
        ct_with_tag = chacha.encrypt(nonce, plaintext, aad)
        ciphertext = ct_with_tag[:-16]
        tag = ct_with_tag[-16:]
        logger.debug("ChaCha20-Poly1305 encryption complete, ciphertext length=%d", len(ciphertext))
        return CipherResult(ciphertext=ciphertext, nonce=nonce, tag=tag)
    except Exception as exc:
        raise SymmetricCipherError(f"ChaCha20-Poly1305 encryption failed: {exc}") from exc


def decrypt_chacha20(
    ciphertext: bytes,
    key: bytes,
    nonce: bytes,
    tag: bytes,
    aad: bytes | None = None,
) -> bytes:
    """Decrypt data using ChaCha20-Poly1305.

    Args:
        ciphertext: Encrypted data (without tag).
        key: 32-byte key matching the one used for encryption.
        nonce: Nonce used during encryption.
        tag: Authentication tag from encryption.
        aad: Optional additional authenticated data (must match encryption).

    Returns:
        Decrypted plaintext bytes.

    Raises:
        SymmetricCipherError: On decryption or authentication failure.
    """
    try:
        chacha = ChaCha20Poly1305(key)
        ct_with_tag = ciphertext + tag
        plaintext = chacha.decrypt(nonce, ct_with_tag, aad)
        logger.debug("ChaCha20-Poly1305 decryption complete, plaintext length=%d", len(plaintext))
        return plaintext
    except Exception as exc:
        raise SymmetricCipherError(f"ChaCha20-Poly1305 decryption failed: {exc}") from exc
