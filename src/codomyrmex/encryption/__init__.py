"""
Encryption module for Codomyrmex.

This module provides encryption/decryption utilities and key management:
- AES-256 symmetric encryption (CBC mode, with deprecation warning)
- AES-GCM authenticated encryption (recommended)
- RSA asymmetric encryption
- Key generation and derivation (PBKDF2, HKDF)
- HMAC message authentication
- Digital signatures
- File encryption utilities
- Secure hashing functions
- Secure data container
"""

from typing import Optional

from codomyrmex.exceptions import EncryptionError

from .algorithms import AESGCMEncryptor
from .containers import SecureDataContainer
from .core import (
    Encryptor,
    decrypt_data,
    encrypt_data,
    generate_aes_key,
)
from .keys import KeyManager, compute_hmac, derive_key_hkdf, verify_hmac

# Shared schemas for cross-module interop
try:
    from codomyrmex.validation.schemas import Result, ResultStatus
except ImportError:
    Result = None
    ResultStatus = None


def cli_commands():
    """Return CLI commands for the encryption module."""
    return {
        "algorithms": {
            "help": "List available encryption algorithms",
            "handler": lambda **kwargs: print(
                "Encryption Algorithms:\n"
                "  - AES-256-CBC: Symmetric (legacy, deprecated)\n"
                "  - AES-256-GCM: Authenticated symmetric (recommended)\n"
                "  - RSA: Asymmetric encryption\n"
                "  - PBKDF2: Key derivation\n"
                "  - HKDF: Key derivation\n"
                "  - HMAC: Message authentication\n"
                "  - SHA-256/SHA-512: Secure hashing"
            ),
        },
        "status": {
            "help": "Show encryption module status",
            "handler": lambda **kwargs: print(
                "Encryption Status:\n"
                f"  Encryptor: {Encryptor.__name__} (available)\n"
                f"  AES-GCM: {AESGCMEncryptor.__name__} (available)\n"
                f"  Key Manager: {KeyManager.__name__} (available)\n"
                f"  Secure Container: {SecureDataContainer.__name__} (available)\n"
                "  HMAC utils: available\n"
                "  KDF utils: available"
            ),
        },
    }


__all__ = [
    # Classes
    "Encryptor",
    "KeyManager",
    "AESGCMEncryptor",
    "SecureDataContainer",
    "EncryptionError",
    # Convenience functions
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
    # HMAC
    "compute_hmac",
    "verify_hmac",
    # KDF
    "derive_key_hkdf",
    # CLI
    "cli_commands",
]


__version__ = "0.1.0"


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
