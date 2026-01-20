"""
Encryption module for Codomyrmex.

This module provides encryption/decryption utilities and key management:
- AES-256 symmetric encryption
- RSA asymmetric encryption
- Key generation and derivation
- Digital signatures
- File encryption utilities
- Secure hashing functions
"""

from typing import Optional

from codomyrmex.exceptions import CodomyrmexError

from .encryptor import (
    Encryptor,
    EncryptionError,
    encrypt_data,
    decrypt_data,
    generate_aes_key,
)
from .key_manager import KeyManager
from .aes_gcm import AESGCMEncryptor
from .container import SecureDataContainer

__all__ = [
    # Classes
    "Encryptor",
    "KeyManager",
    "AESGCMEncryptor",
    "SecureDataContainer",
    "EncryptionError",
    # Functions
    "encrypt",
    "decrypt",
    "generate_key",
    "get_encryptor",
    "encrypt_data",
    "decrypt_data",
    "generate_aes_key",
    "encrypt_file",
    "decrypt_file",
    "hash_data",
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


def encrypt_file(input_path: str, output_path: str, key: bytes, algorithm: str = "AES") -> bool:
    """Encrypt a file."""
    return Encryptor(algorithm=algorithm).encrypt_file(input_path, output_path, key)


def decrypt_file(input_path: str, output_path: str, key: bytes, algorithm: str = "AES") -> bool:
    """Decrypt a file."""
    return Encryptor(algorithm=algorithm).decrypt_file(input_path, output_path, key)


def hash_data(data: bytes, algorithm: str = "sha256") -> str:
    """Compute hash of data."""
    return Encryptor.hash_data(data, algorithm)


