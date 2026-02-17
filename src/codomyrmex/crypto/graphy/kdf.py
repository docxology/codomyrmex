"""Key derivation functions: PBKDF2, scrypt, Argon2id, HKDF."""

from __future__ import annotations

import os
from dataclasses import dataclass, field

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

from codomyrmex.crypto.exceptions import KDFError
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)

_DEFAULT_SALT_SIZE = 16  # 128-bit salt


@dataclass(frozen=True)
class DerivedKey:
    """Result of a key derivation operation."""

    key: bytes
    salt: bytes
    algorithm: str
    parameters: dict = field(default_factory=dict)


def derive_pbkdf2(
    password: bytes,
    salt: bytes | None = None,
    iterations: int = 600_000,
    key_length: int = 32,
) -> DerivedKey:
    """Derive a key using PBKDF2-HMAC-SHA256.

    Args:
        password: Password bytes.
        salt: Salt bytes. If None, a random 16-byte salt is generated.
        iterations: Number of iterations. OWASP recommends >= 600,000 for SHA-256.
        key_length: Desired key length in bytes.

    Returns:
        DerivedKey with the derived key, salt, and parameters.

    Raises:
        KDFError: On derivation failure.
    """
    if salt is None:
        salt = os.urandom(_DEFAULT_SALT_SIZE)
    try:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=key_length,
            salt=salt,
            iterations=iterations,
        )
        key = kdf.derive(password)
        logger.debug(
            "PBKDF2 derivation complete, iterations=%d, key_length=%d",
            iterations,
            key_length,
        )
        return DerivedKey(
            key=key,
            salt=salt,
            algorithm="pbkdf2_sha256",
            parameters={"iterations": iterations, "key_length": key_length},
        )
    except Exception as exc:
        raise KDFError(f"PBKDF2 derivation failed: {exc}") from exc


def derive_scrypt(
    password: bytes,
    salt: bytes | None = None,
    n: int = 2**20,
    r: int = 8,
    p: int = 1,
    key_length: int = 32,
) -> DerivedKey:
    """Derive a key using scrypt.

    Args:
        password: Password bytes.
        salt: Salt bytes. If None, a random 16-byte salt is generated.
        n: CPU/memory cost parameter. Must be a power of 2.
        r: Block size parameter.
        p: Parallelization parameter.
        key_length: Desired key length in bytes.

    Returns:
        DerivedKey with the derived key, salt, and parameters.

    Raises:
        KDFError: On derivation failure.
    """
    if salt is None:
        salt = os.urandom(_DEFAULT_SALT_SIZE)
    try:
        kdf = Scrypt(salt=salt, length=key_length, n=n, r=r, p=p)
        key = kdf.derive(password)
        logger.debug("scrypt derivation complete, n=%d, r=%d, p=%d", n, r, p)
        return DerivedKey(
            key=key,
            salt=salt,
            algorithm="scrypt",
            parameters={"n": n, "r": r, "p": p, "key_length": key_length},
        )
    except Exception as exc:
        raise KDFError(f"scrypt derivation failed: {exc}") from exc


def derive_argon2id(
    password: bytes,
    salt: bytes | None = None,
    time_cost: int = 3,
    memory_cost: int = 65536,
    parallelism: int = 4,
    key_length: int = 32,
) -> DerivedKey:
    """Derive a key using Argon2id.

    Attempts to use cryptography library's Argon2id (available in cryptography >= 44).
    Falls back to scrypt-based derivation if Argon2id is not available.

    Args:
        password: Password bytes.
        salt: Salt bytes. If None, a random 16-byte salt is generated.
        time_cost: Number of iterations.
        memory_cost: Memory usage in KiB.
        parallelism: Degree of parallelism.
        key_length: Desired key length in bytes.

    Returns:
        DerivedKey with the derived key, salt, and parameters.

    Raises:
        KDFError: On derivation failure.
    """
    if salt is None:
        salt = os.urandom(_DEFAULT_SALT_SIZE)

    # Try cryptography library's Argon2id first
    try:
        from cryptography.hazmat.primitives.kdf.argon2 import Argon2id as CryptoArgon2id

        kdf = CryptoArgon2id(
            salt=salt,
            length=key_length,
            iterations=time_cost,
            lanes=parallelism,
            memory_cost=memory_cost,
            ad=None,
            secret=None,
        )
        key = kdf.derive(password)
        logger.debug(
            "Argon2id derivation complete (cryptography backend), "
            "time_cost=%d, memory_cost=%d",
            time_cost,
            memory_cost,
        )
        return DerivedKey(
            key=key,
            salt=salt,
            algorithm="argon2id",
            parameters={
                "time_cost": time_cost,
                "memory_cost": memory_cost,
                "parallelism": parallelism,
                "key_length": key_length,
            },
        )
    except ImportError:
        pass
    except Exception as exc:
        raise KDFError(f"Argon2id derivation failed: {exc}") from exc

    # Fallback: scrypt-based derivation clearly labeled
    logger.warning(
        "Argon2id not available (requires cryptography >= 44). "
        "Falling back to scrypt-based derivation."
    )
    try:
        kdf = Scrypt(salt=salt, length=key_length, n=2**17, r=8, p=1)
        key = kdf.derive(password)
        return DerivedKey(
            key=key,
            salt=salt,
            algorithm="argon2id_fallback_scrypt",
            parameters={
                "note": "Argon2id unavailable, used scrypt fallback",
                "n": 2**17,
                "r": 8,
                "p": 1,
                "key_length": key_length,
            },
        )
    except Exception as exc:
        raise KDFError(f"Argon2id fallback (scrypt) derivation failed: {exc}") from exc


def derive_hkdf(
    input_key: bytes,
    info: bytes,
    salt: bytes | None = None,
    length: int = 32,
) -> bytes:
    """Derive a key using HKDF (HMAC-based Key Derivation Function).

    Suitable for deriving multiple keys from a single shared secret.

    Args:
        input_key: Input keying material.
        info: Context and application-specific information.
        salt: Optional salt. If None, HKDF uses a zero-filled salt.
        length: Desired output key length in bytes.

    Returns:
        Derived key bytes.

    Raises:
        KDFError: On derivation failure.
    """
    try:
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=length,
            salt=salt,
            info=info,
        )
        derived = hkdf.derive(input_key)
        logger.debug("HKDF derivation complete, output length=%d", length)
        return derived
    except Exception as exc:
        raise KDFError(f"HKDF derivation failed: {exc}") from exc
