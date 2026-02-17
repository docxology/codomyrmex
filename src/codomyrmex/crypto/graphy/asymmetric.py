"""Asymmetric encryption primitives: RSA, Ed25519, X25519, and elliptic curves."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, ed25519, padding, rsa, x25519

from codomyrmex.crypto.exceptions import AsymmetricCipherError
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)

_CURVE_MAP: dict[str, ec.EllipticCurve] = {
    "secp256r1": ec.SECP256R1(),
    "secp384r1": ec.SECP384R1(),
    "secp521r1": ec.SECP521R1(),
    "secp256k1": ec.SECP256K1(),
}


@dataclass
class KeyPair:
    """A public/private key pair."""

    private_key: Any
    public_key: Any


def generate_rsa_keypair(key_size: int = 4096) -> KeyPair:
    """Generate an RSA key pair.

    Args:
        key_size: RSA key size in bits. Minimum 2048 recommended.

    Returns:
        KeyPair with RSA private and public keys.

    Raises:
        AsymmetricCipherError: On key generation failure.
    """
    try:
        logger.debug("Generating RSA-%d key pair", key_size)
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
        )
        return KeyPair(private_key=private_key, public_key=private_key.public_key())
    except Exception as exc:
        raise AsymmetricCipherError(f"RSA key generation failed: {exc}") from exc


def rsa_encrypt(plaintext: bytes, public_key: Any) -> bytes:
    """Encrypt data with RSA-OAEP (SHA-256).

    Args:
        plaintext: Data to encrypt. Max size depends on key size.
        public_key: RSA public key.

    Returns:
        Encrypted ciphertext bytes.

    Raises:
        AsymmetricCipherError: On encryption failure.
    """
    try:
        ciphertext = public_key.encrypt(
            plaintext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
        logger.debug("RSA-OAEP encryption complete, ciphertext length=%d", len(ciphertext))
        return ciphertext
    except Exception as exc:
        raise AsymmetricCipherError(f"RSA encryption failed: {exc}") from exc


def rsa_decrypt(ciphertext: bytes, private_key: Any) -> bytes:
    """Decrypt data with RSA-OAEP (SHA-256).

    Args:
        ciphertext: RSA-encrypted data.
        private_key: RSA private key matching the public key used for encryption.

    Returns:
        Decrypted plaintext bytes.

    Raises:
        AsymmetricCipherError: On decryption failure.
    """
    try:
        plaintext = private_key.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
        logger.debug("RSA-OAEP decryption complete, plaintext length=%d", len(plaintext))
        return plaintext
    except Exception as exc:
        raise AsymmetricCipherError(f"RSA decryption failed: {exc}") from exc


def generate_ed25519_keypair() -> KeyPair:
    """Generate an Ed25519 signing key pair.

    Returns:
        KeyPair with Ed25519 private and public keys.

    Raises:
        AsymmetricCipherError: On key generation failure.
    """
    try:
        logger.debug("Generating Ed25519 key pair")
        private_key = ed25519.Ed25519PrivateKey.generate()
        return KeyPair(private_key=private_key, public_key=private_key.public_key())
    except Exception as exc:
        raise AsymmetricCipherError(f"Ed25519 key generation failed: {exc}") from exc


def generate_x25519_keypair() -> KeyPair:
    """Generate an X25519 key exchange key pair.

    Returns:
        KeyPair with X25519 private and public keys.

    Raises:
        AsymmetricCipherError: On key generation failure.
    """
    try:
        logger.debug("Generating X25519 key pair")
        private_key = x25519.X25519PrivateKey.generate()
        return KeyPair(private_key=private_key, public_key=private_key.public_key())
    except Exception as exc:
        raise AsymmetricCipherError(f"X25519 key generation failed: {exc}") from exc


def generate_ec_keypair(curve: str = "secp256r1") -> KeyPair:
    """Generate an elliptic curve key pair.

    Args:
        curve: Curve name. Supported: secp256r1, secp384r1, secp521r1, secp256k1.

    Returns:
        KeyPair with EC private and public keys.

    Raises:
        AsymmetricCipherError: If curve is unsupported or generation fails.
    """
    ec_curve = _CURVE_MAP.get(curve)
    if ec_curve is None:
        raise AsymmetricCipherError(
            f"Unsupported curve: {curve}. Supported: {', '.join(_CURVE_MAP)}"
        )
    try:
        logger.debug("Generating EC key pair on curve %s", curve)
        private_key = ec.generate_private_key(ec_curve)
        return KeyPair(private_key=private_key, public_key=private_key.public_key())
    except Exception as exc:
        raise AsymmetricCipherError(f"EC key generation failed: {exc}") from exc


def serialize_public_key(key: Any, encoding: str = "pem") -> bytes:
    """Serialize a public key to PEM or DER format.

    Args:
        key: Public key object.
        encoding: "pem" or "der".

    Returns:
        Serialized key bytes.

    Raises:
        AsymmetricCipherError: On serialization failure.
    """
    try:
        enc = serialization.Encoding.PEM if encoding == "pem" else serialization.Encoding.DER
        data = key.public_bytes(
            encoding=enc,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        logger.debug("Public key serialized to %s, length=%d", encoding.upper(), len(data))
        return data
    except Exception as exc:
        raise AsymmetricCipherError(f"Public key serialization failed: {exc}") from exc


def serialize_private_key(
    key: Any,
    password: bytes | None = None,
    encoding: str = "pem",
) -> bytes:
    """Serialize a private key to PEM or DER format.

    Args:
        key: Private key object.
        password: Optional password for encryption. If None, key is unencrypted.
        encoding: "pem" or "der".

    Returns:
        Serialized key bytes.

    Raises:
        AsymmetricCipherError: On serialization failure.
    """
    try:
        enc = serialization.Encoding.PEM if encoding == "pem" else serialization.Encoding.DER
        encryption: serialization.KeySerializationEncryption
        if password is not None:
            encryption = serialization.BestAvailableEncryption(password)
        else:
            encryption = serialization.NoEncryption()
        data = key.private_bytes(
            encoding=enc,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=encryption,
        )
        logger.debug("Private key serialized to %s, length=%d", encoding.upper(), len(data))
        return data
    except Exception as exc:
        raise AsymmetricCipherError(f"Private key serialization failed: {exc}") from exc


def load_public_key(data: bytes) -> Any:
    """Load a public key from PEM or DER encoded data.

    Args:
        data: PEM or DER encoded public key.

    Returns:
        Public key object.

    Raises:
        AsymmetricCipherError: On loading failure.
    """
    try:
        if data.startswith(b"-----"):
            key = serialization.load_pem_public_key(data)
        else:
            key = serialization.load_der_public_key(data)
        logger.debug("Public key loaded successfully")
        return key
    except Exception as exc:
        raise AsymmetricCipherError(f"Failed to load public key: {exc}") from exc


def load_private_key(data: bytes, password: bytes | None = None) -> Any:
    """Load a private key from PEM or DER encoded data.

    Args:
        data: PEM or DER encoded private key.
        password: Password if key is encrypted, else None.

    Returns:
        Private key object.

    Raises:
        AsymmetricCipherError: On loading failure.
    """
    try:
        if data.startswith(b"-----"):
            key = serialization.load_pem_private_key(data, password=password)
        else:
            key = serialization.load_der_private_key(data, password=password)
        logger.debug("Private key loaded successfully")
        return key
    except Exception as exc:
        raise AsymmetricCipherError(f"Failed to load private key: {exc}") from exc
