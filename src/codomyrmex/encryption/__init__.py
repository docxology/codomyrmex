"""
Encryption module for Codomyrmex.

This module provides encryption/decryption utilities and key management.
"""

from typing import Optional

from codomyrmex.exceptions import CodomyrmexError

from .encryptor import Encryptor
from .key_manager import KeyManager

__all__ = [
    "Encryptor",
    "KeyManager",
    "encrypt",
    "decrypt",
    "generate_key",
    "get_encryptor",
]

__version__ = "0.1.0"


class EncryptionError(CodomyrmexError):
    """Raised when encryption operations fail."""

    pass


def encrypt(data: bytes, key: bytes, algorithm: str = "AES") -> bytes:
    """Encrypt data."""
    encryptor = Encryptor(algorithm=algorithm)
    return encryptor.encrypt(data, key)


def decrypt(data: bytes, key: bytes, algorithm: str = "AES") -> bytes:
    """Decrypt data."""
    encryptor = Encryptor(algorithm=algorithm)
    return encryptor.decrypt(data, key)


def generate_key(algorithm: str = "AES") -> bytes:
    """Generate an encryption key."""
    encryptor = Encryptor(algorithm=algorithm)
    return encryptor.generate_key()


def get_encryptor(algorithm: str = "AES") -> Encryptor:
    """Get an encryptor instance."""
    return Encryptor(algorithm=algorithm)

