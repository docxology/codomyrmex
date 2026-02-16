"""Core encryption engine.

Provides the main ``Encryptor`` class that supports AES-256-CBC (legacy),
RSA encryption, key generation, digital signatures, and file encryption
utilities.  Module-level convenience functions ``encrypt_data``,
``decrypt_data``, and ``generate_aes_key`` are also re-exported here.
"""

from .encryptor import (
    Encryptor,
    decrypt_data,
    encrypt_data,
    generate_aes_key,
)

__all__ = [
    "Encryptor",
    "decrypt_data",
    "encrypt_data",
    "generate_aes_key",
]
