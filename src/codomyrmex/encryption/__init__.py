"""Encryption module for Codomyrmex.

Provides encryption, hashing, digital signatures, and key management:
- AES-256 symmetric encryption (CBC and GCM)
- RSA asymmetric encryption and digital signatures
- Key generation and key derivation (PBKDF2, HKDF)
- HMAC message authentication
- Secure hashing (SHA-256, SHA-384, SHA-512, MD5)
- Secure data containers for JSON objects
- Key management for secure key storage
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

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
from .signing import Signer

if TYPE_CHECKING:
    from pathlib import Path

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
                "  - PBKDF2: Key derivation from passwords\n"
                "  - HKDF: Key derivation from high-entropy material\n"
                "  - HMAC: Message authentication (SHA-256/384/512)\n"
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
                f"  Signer: {Signer.__name__} (available)\n"
                "  HMAC utils: available\n"
                "  KDF utils: available"
            ),
        },
    }


__all__ = [
    "AESGCMEncryptor",
    "EncryptionError",
    # Classes
    "Encryptor",
    "KeyManager",
    "SecureDataContainer",
    "Signer",
    # CLI
    "cli_commands",
    # HMAC
    "compute_hmac",
    "decrypt",
    "decrypt_data",
    "decrypt_file",
    # KDF
    "derive_key_hkdf",
    # Convenience functions
    "encrypt",
    "encrypt_data",
    "encrypt_file",
    "generate_aes_key",
    "generate_key",
    "get_encryptor",
    "hash_data",
    "verify_hmac",
]


__version__ = "0.2.0"


def encrypt(data: bytes, key: bytes, algorithm: str = "AES") -> bytes:
    """Encrypt bytes using specified algorithm."""
    return Encryptor(algorithm=algorithm).encrypt(data, key)


def decrypt(data: bytes, key: bytes, algorithm: str = "AES") -> bytes:
    """Decrypt bytes using specified algorithm."""
    return Encryptor(algorithm=algorithm).decrypt(data, key)


def generate_key(algorithm: str = "AES") -> bytes:
    """Generate an encryption key for specified algorithm."""
    return Encryptor(algorithm=algorithm).generate_key()


def get_encryptor(algorithm: str = "AES") -> Encryptor:
    """Get an Encryptor instance."""
    return Encryptor(algorithm=algorithm)


def encrypt_file(
    input_path: str | Path, output_path: str | Path, key: bytes, algorithm: str = "AES"
) -> bool:
    """Encrypt a file from input to output."""
    return Encryptor(algorithm=algorithm).encrypt_file(input_path, output_path, key)


def decrypt_file(
    input_path: str | Path, output_path: str | Path, key: bytes, algorithm: str = "AES"
) -> bool:
    """Decrypt a file from input to output."""
    return Encryptor(algorithm=algorithm).decrypt_file(input_path, output_path, key)


def hash_data(data: bytes, algorithm: str = "sha256") -> str:
    """Compute hexadecimal hash of data."""
    return Encryptor.hash_data(data, algorithm)
