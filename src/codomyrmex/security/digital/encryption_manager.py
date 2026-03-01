"""Encryption manager for digital security.

Provides symmetric and asymmetric encryption capabilities, key management,
and secure data handling.
"""

import base64
import os

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False

from codomyrmex.exceptions import CodomyrmexError
from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)


class EncryptionError(CodomyrmexError):
    """Raised when encryption operations fail."""
    pass


class EncryptionManager:
    """Manages encryption keys and operations."""

    def __init__(self, key: bytes | None = None):
        """Initialize encryption manager.

        Args:
            key: Symmetric key (Fernet). If None, a new key is generated.
        """
        if not CRYPTOGRAPHY_AVAILABLE:
            raise ImportError("cryptography package not available. Install with: pip install cryptography")

        self.key = key or Fernet.generate_key()
        self.cipher = Fernet(self.key)

    def encrypt(self, data: str | bytes) -> bytes:
        """Encrypt data using symmetric key."""
        if isinstance(data, str):
            data = data.encode('utf-8')
        return self.cipher.encrypt(data)

    def decrypt(self, token: bytes) -> bytes:
        """Decrypt data using symmetric key."""
        try:
            return self.cipher.decrypt(token)
        except Exception as e:
            raise EncryptionError(f"Decryption failed: {e}") from e

    def decrypt_to_string(self, token: bytes) -> str:
        """Decrypt data and return as string."""
        return self.decrypt(token).decode('utf-8')

    @staticmethod
    def generate_key_pair(password: bytes | None = None) -> tuple[bytes, bytes]:
        """Generate RSA key pair.

        Args:
            password: Optional password to encrypt the private key PEM. When None,
                the private key is returned unencrypted — callers are responsible
                for protecting it (e.g. restrict file permissions, use secure storage).

        Returns:
            Tuple of (private_key_pem, public_key_pem)
        """
        if not CRYPTOGRAPHY_AVAILABLE:
             raise ImportError("cryptography package not available")

        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )

        encryption_algorithm = (
            serialization.BestAvailableEncryption(password)
            if password is not None
            else serialization.NoEncryption()
        )
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=encryption_algorithm,
        )

        public_key = private_key.public_key()
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        return private_pem, public_pem

    @staticmethod
    def derive_key(password: str, salt: bytes | None = None) -> tuple[bytes, bytes]:
        """Derive a key from a password using PBKDF2.

        Args:
            password: Password string
            salt: Optional salt. If None, random salt is generated.

        Returns:
            Tuple of (key, salt)
        """
        if not CRYPTOGRAPHY_AVAILABLE:
             raise ImportError("cryptography package not available")

        if salt is None:
            salt = os.urandom(16)

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )

        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key, salt


def encrypt_sensitive_data(data: str | bytes) -> dict[str, bytes]:
    """Encrypt sensitive data using a freshly generated symmetric key.

    Args:
        data: Plaintext string or bytes to encrypt.

    Returns:
        Dict with 'encrypted_data' (bytes) and 'key' (bytes, the Fernet key).
    """
    manager = EncryptionManager()
    encrypted = manager.encrypt(data)
    return {"encrypted_data": encrypted, "key": manager.key}


def decrypt_sensitive_data(encrypted_data: bytes, key: bytes) -> str:
    """Decrypt data that was encrypted with ``encrypt_sensitive_data``.

    Args:
        encrypted_data: Ciphertext bytes produced by ``encrypt_sensitive_data``.
        key: The Fernet key that was used during encryption.

    Returns:
        Decrypted plaintext string.
    """
    manager = EncryptionManager(key=key)
    return manager.decrypt_to_string(encrypted_data)
