"""Encryption algorithm implementations.

Provides authenticated encryption via AES-GCM, the recommended symmetric
cipher for new code.
"""

from .aes_gcm import AESGCMEncryptor

__all__ = [
    "AESGCMEncryptor",
]
