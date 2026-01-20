"""Authenticated encryption using AES-GCM."""

import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class AESGCMEncryptor:
    """Encryptor using AES-GCM for authenticated encryption."""
    
    def __init__(self, key: Optional[bytes] = None):
        if key and len(key) not in {16, 24, 32}:
            raise ValueError("Key must be 16, 24, or 32 bytes.")
        self.key = key or os.urandom(32)
        self.aesgcm = AESGCM(self.key)

    def encrypt(self, data: bytes, associated_data: Optional[bytes] = None) -> bytes:
        """Encrypt data with optional associated data (AAD)."""
        nonce = os.urandom(12)
        ciphertext = self.aesgcm.encrypt(nonce, data, associated_data)
        return nonce + ciphertext

    def decrypt(self, data: bytes, associated_data: Optional[bytes] = None) -> bytes:
        """Decrypt data and verify authenticity."""
        nonce = data[:12]
        ciphertext = data[12:]
        return self.aesgcm.decrypt(nonce, ciphertext, associated_data)
