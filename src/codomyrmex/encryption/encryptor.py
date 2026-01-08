from typing import Optional
import os

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding as asym_padding
from cryptography.hazmat.primitives.asymmetric import padding as asym_padding
from cryptography.hazmat.primitives.asymmetric import padding as asym_padding
from cryptography.hazmat.primitives.asymmetric import padding as asym_padding
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import hashlib

from codomyrmex.exceptions import CodomyrmexError
from codomyrmex.logging_monitoring.logger_config import get_logger




























































"""
"""Core functionality module

This module provides encryptor functionality including:
- 11 functions: __init__, encrypt, decrypt...
- 2 classes: EncryptionError, Encryptor

Usage:
    # Example usage here
"""
Encryption utilities.
"""



logger = get_logger(__name__)

try:
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False


class EncryptionError(CodomyrmexError):
    """Raised when encryption operations fail."""

    pass


class Encryptor:
    """Encryptor for various algorithms."""

    def __init__(self, algorithm: str = "AES"):
        """Initialize encryptor.

        Args:
            algorithm: Encryption algorithm (AES, RSA)
        """
        if not CRYPTOGRAPHY_AVAILABLE:
            raise ImportError("cryptography package not available. Install with: pip install cryptography")

        self.algorithm = algorithm

    def encrypt(self, data: bytes, key: bytes) -> bytes:
        """Encrypt data using the configured algorithm.

        Args:
            data: Data to encrypt
            key: Encryption key

        Returns:
            Encrypted data

        Raises:
            EncryptionError: If encryption fails
        """
        try:
            if self.algorithm == "AES":
                return self._encrypt_aes(data, key)
            elif self.algorithm == "RSA":
                return self._encrypt_rsa(data, key)
            else:
                raise ValueError(f"Unknown algorithm: {self.algorithm}")
        except Exception as e:
            logger.error(f"Encryption error: {e}")
            raise EncryptionError(f"Failed to encrypt: {str(e)}") from e

    def decrypt(self, data: bytes, key: bytes) -> bytes:
        """Decrypt data using the configured algorithm.

        Args:
            data: Encrypted data
            key: Decryption key

        Returns:
            Decrypted data

        Raises:
            EncryptionError: If decryption fails
        """
        try:
            if self.algorithm == "AES":
                return self._decrypt_aes(data, key)
            elif self.algorithm == "RSA":
                return self._decrypt_rsa(data, key)
            else:
                raise ValueError(f"Unknown algorithm: {self.algorithm}")
        except Exception as e:
            logger.error(f"Decryption error: {e}")
            raise EncryptionError(f"Failed to decrypt: {str(e)}") from e

    def generate_key(self) -> bytes:
        """Generate a new encryption key.

        Returns:
            Generated key
        """
        if self.algorithm == "AES":
            return os.urandom(32)  # 256-bit key
        elif self.algorithm == "RSA":
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=default_backend()
            )
            return private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
        else:
            raise ValueError(f"Unknown algorithm: {self.algorithm}")

    def derive_key(self, password: str, salt: bytes) -> bytes:
        """Derive an encryption key from a password.

        Args:
            password: Password to derive key from
            salt: Salt for key derivation

        Returns:
            Derived key
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        return kdf.derive(password.encode())

    def sign(self, data: bytes, private_key: bytes) -> bytes:
        """Create a digital signature for data.

        Args:
            data: Data to sign
            private_key: Private key for signing

        Returns:
            Digital signature
        """

        private_key_obj = serialization.load_pem_private_key(private_key, password=None, backend=default_backend())
        signature = private_key_obj.sign(
            data,
            asym_padding.PSS(
                mgf=asym_padding.MGF1(hashes.SHA256()),
                salt_length=asym_padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return signature

    def verify(self, data: bytes, signature: bytes, public_key: bytes) -> bool:
        """Verify a digital signature.

        Args:
            data: Original data
            signature: Digital signature
            public_key: Public key for verification

        Returns:
            True if signature is valid
        """

        try:
            public_key_obj = serialization.load_pem_public_key(public_key, backend=default_backend())
            public_key_obj.verify(
                signature,
                data,
                asym_padding.PSS(
                    mgf=asym_padding.MGF1(hashes.SHA256()),
                    salt_length=asym_padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception:
            return False

    def _encrypt_aes(self, data: bytes, key: bytes) -> bytes:
        """Encrypt using AES."""
        # Ensure key is correct length
        if len(key) != 32:
            key = hashlib.sha256(key).digest()

        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()

        # Pad data
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(data) + padder.finalize()

        encrypted = encryptor.update(padded_data) + encryptor.finalize()
        return iv + encrypted

    def _decrypt_aes(self, data: bytes, key: bytes) -> bytes:
        """Decrypt using AES."""
        # Ensure key is correct length
        if len(key) != 32:
            key = hashlib.sha256(key).digest()

        iv = data[:16]
        encrypted = data[16:]

        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()

        decrypted = decryptor.update(encrypted) + decryptor.finalize()

        # Unpad data
        unpadder = padding.PKCS7(128).unpadder()
        unpadded = unpadder.update(decrypted) + unpadder.finalize()

        return unpadded

    def _encrypt_rsa(self, data: bytes, key: bytes) -> bytes:
        """Encrypt using RSA."""

        public_key = serialization.load_pem_public_key(key, backend=default_backend())
        return public_key.encrypt(
            data,
            asym_padding.OAEP(
                mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

    def _decrypt_rsa(self, data: bytes, key: bytes) -> bytes:
        """Decrypt using RSA."""

        private_key = serialization.load_pem_private_key(key, password=None, backend=default_backend())
        return private_key.decrypt(
            data,
            asym_padding.OAEP(
                mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

