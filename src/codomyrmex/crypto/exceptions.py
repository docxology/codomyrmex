"""Crypto module exception hierarchy.

All crypto exceptions inherit from CodomyrmexError for consistency
with the broader Codomyrmex exception handling patterns.
"""

from __future__ import annotations

from codomyrmex.exceptions.base import CodomyrmexError


class CryptoError(CodomyrmexError):
    """Base exception for all crypto module errors."""


class SymmetricCipherError(CryptoError):
    """Error in symmetric encryption/decryption operations."""


class AsymmetricCipherError(CryptoError):
    """Error in asymmetric encryption/decryption operations."""


class HashError(CryptoError):
    """Error in hashing operations."""


class SignatureError(CryptoError):
    """Error in digital signature operations."""


class KDFError(CryptoError):
    """Error in key derivation operations."""


class CertificateError(CryptoError):
    """Error in certificate operations."""


class WalletError(CryptoError):
    """Error in cryptocurrency wallet operations."""


class BlockchainError(CryptoError):
    """Error in blockchain operations."""


class SteganographyError(CryptoError):
    """Error in steganography operations."""


class EncodingError(CryptoError):
    """Error in encoding/decoding operations."""


class ProtocolError(CryptoError):
    """Error in cryptographic protocol operations."""


class RandomError(CryptoError):
    """Error in random number generation operations."""
