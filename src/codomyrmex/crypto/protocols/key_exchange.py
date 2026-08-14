"""Diffie-Hellman and Elliptic Curve Diffie-Hellman key exchange protocols.

Provides DH parameter generation, keypair generation, and shared secret
computation for both classical DH (RFC 3526) and X25519 ECDH (RFC 7748).
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import dh, x25519
from cryptography.utils import CryptographyDeprecationWarning

from codomyrmex.crypto.exceptions import ProtocolError
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)

# RFC 2409 group 2 and RFC 7919 ffdhe2048. Recent cryptography releases
# deprecate generating fresh finite-field DH parameters because parameter
# generation is slow and easy to get wrong. Using audited, standardized
# groups avoids that deprecated code path while keeping this legacy DH API
# interoperable. X25519 remains the preferred new-protocol choice below.
# Store the standardized groups as PKCS#3 parameter encodings. Constructing
# them through cryptography's DHParameterNumbers API also raises the same
# deprecation warning as generating new parameters.
_RFC_GROUP_PARAMETERS: dict[int, bytes] = {
    1024: (
        b"-----BEGIN DH PARAMETERS-----\n"
        b"MIGHAoGBAP//////////yQ/aoiFowjTExmKLgNwc0SkCTgiKZ8x0Agu+pjsTmyJR\n"
        b"Sgh5jjQE3e+VGbPNOkMbMCsKbfJfFDdP4TVtbVHCReSFtXZiXn7G9ExC6aY37WsL\n"
        b"/1y29Aa37e44a/taiZ+lrp8kEXxLH+ZJKGZR7OZTgf//////////AgEC\n"
        b"-----END DH PARAMETERS-----\n"
    ),
    2048: (
        b"-----BEGIN DH PARAMETERS-----\n"
        b"MIIBCAKCAQEA//////////+t+FRYortKmq/cViAnPTzx2LnFg84tNpWp4TZBFGQz\n"
        b"+8yTnc4kmz75fS/jY2MMddj2gbICrsRhetPfHtXV/WVhJDP1H18GbtCFY2VVPe0a\n"
        b"87VXE15/V8k1mE8McODmi3fipona8+/och3xWKE2rec1MKzKT0g6eXq8CrGCsyT7\n"
        b"YdEIqUuyyOP7uWrat2DX9GgdT0Kj3jlN9K5W7edjcrsZCwenyO4KbXCeAvzhzffi\n"
        b"7MA0BM0oNC9hkXL+nOmFg/+OTxIy7vKBg8P+OxtMb61zO7X8vC7CIAXFjvGDfRaD\n"
        b"ssbzSibBsu/6iGtCOGEoXJf//////////wIBAg==\n"
        b"-----END DH PARAMETERS-----\n"
    ),
}

_SUPPORTED_DH_SIZES = tuple(sorted(_RFC_GROUP_PARAMETERS))


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
    """Return standardized DH parameters meeting the requested minimum size.

    Args:
        key_size: Minimum bit length of the prime modulus. Must be >= 512.
            The next supported RFC group is selected when the request falls
            between standardized group sizes. Recommended: 2048.

    Returns:
        DH parameters suitable for generating keypairs.

    Raises:
        ProtocolError: If parameter generation fails or key_size is invalid.
    """
    if key_size < 512:
        raise ProtocolError(f"DH key_size must be >= 512, got {key_size}")
    group_size = next(
        (size for size in _SUPPORTED_DH_SIZES if size >= key_size),
        None,
    )
    if group_size is None:
        supported = ", ".join(str(size) for size in _SUPPORTED_DH_SIZES)
        raise ProtocolError(
            f"DH key_size {key_size} exceeds the largest supported RFC group; "
            f"supported minimums: {supported}"
        )
    try:
        logger.debug(
            "Loading RFC DH parameters for requested minimum key_size=%d "
            "(group_size=%d)",
            key_size,
            group_size,
        )
        # cryptography 50 warns when materializing any legacy DHParameters,
        # including audited RFC groups. Keep the compatibility suppression
        # narrow to this unavoidable boundary; new protocols should use
        # X25519 and never enter this path.
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", CryptographyDeprecationWarning)
            parameters = serialization.load_pem_parameters(
                _RFC_GROUP_PARAMETERS[group_size]
            )
        logger.info("DH parameters loaded successfully (group_size=%d)", group_size)
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
        logger.info("DH shared secret computed (%d bytes)", len(shared_secret))
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
        logger.info("X25519 ECDH shared secret computed (%d bytes)", len(shared_secret))
        return shared_secret
    except Exception as exc:
        raise ProtocolError(f"ECDH shared secret computation failed: {exc}") from exc
