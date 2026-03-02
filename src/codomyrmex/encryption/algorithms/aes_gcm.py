"""Authenticated encryption using AES-GCM."""

from __future__ import annotations

import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from codomyrmex.exceptions import EncryptionError
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class AESGCMEncryptor:
    """Encryptor using AES-GCM for authenticated encryption.

    Recommended for most use cases over AES-CBC.
    """

    def __init__(self, key: bytes | None = None):
        """Initialize AES-GCM encryptor.

        Args:
            key: 16, 24, or 32 byte key. If None, a 32-byte key is auto-generated.
        """
        if key and len(key) not in {16, 24, 32}:
            raise ValueError("AES-GCM key must be 16, 24, or 32 bytes.")
        self.key = key or os.urandom(32)
        self.aesgcm = AESGCM(self.key)

    def encrypt(self, data: bytes, associated_data: bytes | None = None) -> bytes:
        """Encrypt data with optional associated data (AAD).

        Args:
            data: Raw bytes to encrypt.
            associated_data: Optional authenticated but not encrypted data.

        Returns:
            Concatenated 12-byte nonce and ciphertext (including 16-byte tag).

        Raises:
            EncryptionError: If encryption fails.
        """
        try:
            nonce = os.urandom(12)
            ciphertext = self.aesgcm.encrypt(nonce, data, associated_data)
            return nonce + ciphertext
        except Exception as e:
            logger.error("AES-GCM encryption error: %s", e)
            raise EncryptionError(f"AES-GCM encryption failed: {e}") from e

    def decrypt(self, data: bytes, associated_data: bytes | None = None) -> bytes:
        """Decrypt data and verify authenticity.

        Args:
            data: Concatenated 12-byte nonce and ciphertext.
            associated_data: Associated data used during encryption.

        Returns:
            Decrypted raw bytes.

        Raises:
            EncryptionError: If decryption or authentication fails.
        """
        if len(data) < 28:  # 12 (nonce) + 16 (tag)
            raise EncryptionError("Data too short for AES-GCM decryption.")

        try:
            nonce = data[:12]
            ciphertext = data[12:]
            return self.aesgcm.decrypt(nonce, ciphertext, associated_data)
        except Exception as e:
            logger.error("AES-GCM decryption error: %s", e)
            raise EncryptionError(f"AES-GCM decryption/authentication failed: {e}") from e
