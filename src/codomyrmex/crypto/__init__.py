"""Codomyrmex Crypto Module — comprehensive cryptographic operations.

Submodules:
    graphy      — Cryptography primitives (symmetric, asymmetric, hashing, signatures, KDF, MAC, certificates)
    currency    — Cryptocurrency (wallets, blockchain, transactions, addresses, tokens)
    analysis    — Cryptanalysis (entropy, frequency, strength, classical cipher breaking)
    steganography — Data hiding (image LSB, text zero-width chars, detection)
    encoding    — Crypto-related encoding (Base64, Base58, Base32, hex, PEM)
    random      — Cryptographic randomness (CSPRNG, NIST SP 800-22 tests)
    protocols   — Cryptographic protocols (key exchange, secret sharing, zero-knowledge proofs)
"""

__version__ = "0.1.0"

from . import (
    analysis,
    currency,
    encoding,
    graphy,
    protocols,
    random,
    steganography,
)
from .exceptions import (
    AsymmetricCipherError,
    BlockchainError,
    CertificateError,
    CryptoError,
    EncodingError,
    HashError,
    KDFError,
    ProtocolError,
    RandomError,
    SignatureError,
    SteganographyError,
    SymmetricCipherError,
    WalletError,
)

__all__ = [
    "__version__",
    "graphy",
    "currency",
    "analysis",
    "steganography",
    "encoding",
    "random",
    "protocols",
    "CryptoError",
    "SymmetricCipherError",
    "AsymmetricCipherError",
    "HashError",
    "SignatureError",
    "KDFError",
    "CertificateError",
    "WalletError",
    "BlockchainError",
    "SteganographyError",
    "EncodingError",
    "ProtocolError",
    "RandomError",
]


def cli_commands():
    """Return CLI commands for the crypto module."""
    return {
        "crypto:status": _cmd_status,
        "crypto:algorithms": _cmd_algorithms,
        "crypto:hash": _cmd_hash,
    }


def _cmd_status(**kwargs):
    """Show availability of each crypto submodule."""
    results = {}
    for name in ["graphy", "currency", "analysis", "steganography", "encoding", "random", "protocols"]:
        try:
            __import__(f"codomyrmex.crypto.{name}")
            results[name] = "available"
        except ImportError as e:
            results[name] = f"unavailable: {e}"
    return results


def _cmd_algorithms(**kwargs):
    """List available crypto algorithms across all submodules."""
    return {
        "symmetric": ["AES-256-GCM", "ChaCha20-Poly1305"],
        "asymmetric": ["RSA-4096", "Ed25519", "X25519", "SECP256R1"],
        "hashing": ["SHA-256", "SHA-3-256", "SHA-512", "BLAKE2b", "MD5"],
        "signatures": ["ECDSA", "EdDSA", "RSA-PSS"],
        "kdf": ["PBKDF2", "scrypt", "Argon2id", "HKDF"],
        "mac": ["HMAC-SHA256", "Poly1305", "CMAC"],
        "encoding": ["Base64", "Base58", "Base32", "Hex", "PEM"],
        "protocols": ["DH", "ECDH (X25519)", "Shamir Secret Sharing", "Schnorr ZKP", "Pedersen Commitment"],
    }


def _cmd_hash(data: str = "", algorithm: str = "sha256", **kwargs):
    """Quick hash computation."""
    from .graphy.hashing import hash_data
    return hash_data(data.encode() if isinstance(data, str) else data, algorithm)
