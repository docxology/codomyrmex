"""Diffie-Hellman and Elliptic Curve Diffie-Hellman key exchange protocols.

Provides DH parameter generation, keypair generation, and shared secret
computation for both classical DH (RFC 3526) and X25519 ECDH (RFC 7748).
"""

from __future__ import annotations

from dataclasses import dataclass

from cryptography.hazmat.primitives.asymmetric import dh, x25519

from codomyrmex.crypto.exceptions import ProtocolError
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


@dataclass
class DHKeyPair:
    """A Diffie-Hellman keypair with its associated parameters."""

    private_key: dh.DHPrivateKey
    public_key: dh.DHPublicKey
    parameters: dh.DHParameters


@dataclass
class ECDHKeyPair:
    """An X25519 Elliptic Curve Diffie-Hellman keypair."""

    private_key: x25519.X25519PrivateKey
    public_key: x25519.X25519PublicKey


def dh_generate_parameters(key_size: int = 2048) -> dh.DHParameters:
    """Generate DH parameters with the specified key size.

    Args:
        key_size: Bit length of the prime modulus. Must be >= 512.
            Recommended: 2048 or higher for production use.

    Returns:
        DH parameters suitable for generating keypairs.

    Raises:
        ProtocolError: If parameter generation fails or key_size is invalid.
    """
    if key_size < 512:
        raise ProtocolError(f"DH key_size must be >= 512, got {key_size}")
    try:
        logger.debug("Generating DH parameters with key_size=%d", key_size)
        parameters = dh.generate_parameters(generator=2, key_size=key_size)
        logger.info("DH parameters generated successfully (key_size=%d)", key_size)
        return parameters
    except Exception as exc:
        raise ProtocolError(f"DH parameter generation failed: {exc}") from exc


def dh_generate_keypair(parameters: dh.DHParameters) -> DHKeyPair:
    """Generate a DH keypair from existing parameters.

    Args:
        parameters: Pre-generated DH parameters.

    Returns:
        A DHKeyPair containing private key, public key, and parameters.

    Raises:
        ProtocolError: If keypair generation fails.
    """
    try:
        logger.debug("Generating DH keypair")
        private_key = parameters.generate_private_key()
        public_key = private_key.public_key()
        logger.info("DH keypair generated successfully")
        return DHKeyPair(
            private_key=private_key,
            public_key=public_key,
            parameters=parameters,
        )
    except Exception as exc:
        raise ProtocolError(f"DH keypair generation failed: {exc}") from exc


def dh_compute_shared_secret(
    private_key: dh.DHPrivateKey,
    peer_public_key: dh.DHPublicKey,
) -> bytes:
    """Compute a shared secret from a private key and a peer's public key.

    Args:
        private_key: The local party's DH private key.
        peer_public_key: The remote party's DH public key.

    Returns:
        The raw shared secret bytes.

    Raises:
        ProtocolError: If the key exchange computation fails.
    """
    try:
        logger.debug("Computing DH shared secret")
        shared_secret = private_key.exchange(peer_public_key)
        logger.info(
            "DH shared secret computed (%d bytes)", len(shared_secret)
        )
        return shared_secret
    except Exception as exc:
        raise ProtocolError(f"DH shared secret computation failed: {exc}") from exc


def ecdh_generate_keypair() -> ECDHKeyPair:
    """Generate an X25519 ECDH keypair.

    Returns:
        An ECDHKeyPair containing the private and public keys.

    Raises:
        ProtocolError: If keypair generation fails.
    """
    try:
        logger.debug("Generating X25519 ECDH keypair")
        private_key = x25519.X25519PrivateKey.generate()
        public_key = private_key.public_key()
        logger.info("X25519 ECDH keypair generated successfully")
        return ECDHKeyPair(private_key=private_key, public_key=public_key)
    except Exception as exc:
        raise ProtocolError(f"ECDH keypair generation failed: {exc}") from exc


def ecdh_compute_shared_secret(
    private_key: x25519.X25519PrivateKey,
    peer_public_key: x25519.X25519PublicKey,
) -> bytes:
    """Compute a shared secret using X25519 ECDH.

    Args:
        private_key: The local party's X25519 private key.
        peer_public_key: The remote party's X25519 public key.

    Returns:
        The 32-byte shared secret.

    Raises:
        ProtocolError: If the key exchange computation fails.
    """
    try:
        logger.debug("Computing X25519 ECDH shared secret")
        shared_secret = private_key.exchange(peer_public_key)
        logger.info(
            "X25519 ECDH shared secret computed (%d bytes)", len(shared_secret)
        )
        return shared_secret
    except Exception as exc:
        raise ProtocolError(
            f"ECDH shared secret computation failed: {exc}"
        ) from exc
