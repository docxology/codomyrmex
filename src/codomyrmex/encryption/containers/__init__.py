"""Secure data containers for encrypted object storage.

Provides ``SecureDataContainer`` which serializes Python objects to JSON
and encrypts them using AES-GCM authenticated encryption.
"""

from .container import SecureDataContainer

__all__ = [
    "SecureDataContainer",
]
