"""Digital signature primitives: ECDSA, Ed25519, and RSA-PSS."""

from __future__ import annotations

from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec, ed25519, padding, utils

from codomyrmex.crypto.exceptions import SignatureError
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


def sign_ecdsa(message: bytes, private_key: Any) -> bytes:
    """Sign a message using ECDSA with SHA-256.

    Args:
        message: Data to sign.
        private_key: EC private key.

    Returns:
        DER-encoded ECDSA signature.

    Raises:
        SignatureError: On signing failure.
    """
    try:
        signature = private_key.sign(message, ec.ECDSA(hashes.SHA256()))
        logger.debug("ECDSA signature created, length=%d", len(signature))
        return signature
    except Exception as exc:
        raise SignatureError(f"ECDSA signing failed: {exc}") from exc


def verify_ecdsa(message: bytes, signature: bytes, public_key: Any) -> bool:
    """Verify an ECDSA signature.

    Args:
        message: Original signed data.
        signature: DER-encoded ECDSA signature.
        public_key: EC public key.

    Returns:
        True if signature is valid, False otherwise.
    """
    try:
        public_key.verify(signature, message, ec.ECDSA(hashes.SHA256()))
        logger.debug("ECDSA signature verified successfully")
        return True
    except InvalidSignature:
        logger.debug("ECDSA signature verification failed: invalid signature")
        return False
    except Exception as exc:
        raise SignatureError(f"ECDSA verification error: {exc}") from exc


def sign_ed25519(message: bytes, private_key: Any) -> bytes:
    """Sign a message using Ed25519.

    Args:
        message: Data to sign.
        private_key: Ed25519 private key.

    Returns:
        64-byte Ed25519 signature.

    Raises:
        SignatureError: On signing failure.
    """
    try:
        signature = private_key.sign(message)
        logger.debug("Ed25519 signature created, length=%d", len(signature))
        return signature
    except Exception as exc:
        raise SignatureError(f"Ed25519 signing failed: {exc}") from exc


def verify_ed25519(message: bytes, signature: bytes, public_key: Any) -> bool:
    """Verify an Ed25519 signature.

    Args:
        message: Original signed data.
        signature: 64-byte Ed25519 signature.
        public_key: Ed25519 public key.

    Returns:
        True if signature is valid, False otherwise.
    """
    try:
        public_key.verify(signature, message)
        logger.debug("Ed25519 signature verified successfully")
        return True
    except InvalidSignature:
        logger.debug("Ed25519 signature verification failed: invalid signature")
        return False
    except Exception as exc:
        raise SignatureError(f"Ed25519 verification error: {exc}") from exc


def sign_rsa_pss(message: bytes, private_key: Any) -> bytes:
    """Sign a message using RSA-PSS with SHA-256.

    Args:
        message: Data to sign.
        private_key: RSA private key.

    Returns:
        RSA-PSS signature bytes.

    Raises:
        SignatureError: On signing failure.
    """
    try:
        signature = private_key.sign(
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
            hashes.SHA256(),
        )
        logger.debug("RSA-PSS signature created, length=%d", len(signature))
        return signature
    except Exception as exc:
        raise SignatureError(f"RSA-PSS signing failed: {exc}") from exc


def verify_rsa_pss(message: bytes, signature: bytes, public_key: Any) -> bool:
    """Verify an RSA-PSS signature.

    Args:
        message: Original signed data.
        signature: RSA-PSS signature bytes.
        public_key: RSA public key.

    Returns:
        True if signature is valid, False otherwise.
    """
    try:
        public_key.verify(
            signature,
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
            hashes.SHA256(),
        )
        logger.debug("RSA-PSS signature verified successfully")
        return True
    except InvalidSignature:
        logger.debug("RSA-PSS signature verification failed: invalid signature")
        return False
    except Exception as exc:
        raise SignatureError(f"RSA-PSS verification error: {exc}") from exc
