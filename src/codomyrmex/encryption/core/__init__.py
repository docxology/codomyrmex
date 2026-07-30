"""Core encryption engine.

Provides the main ``Encryptor`` class that supports AES-256-CBC,
RSA encryption, key generation, digital signatures, and file encryption
utilities.  ``generate_aes_key`` is available from this package for key generation.
"""

from .encryptor import Encryptor, generate_aes_key

__all__ = [
    "Encryptor",
    "generate_aes_key",
]
