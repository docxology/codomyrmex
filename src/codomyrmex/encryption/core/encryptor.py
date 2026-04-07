"""Core encryption engine.

Provides the main Encryptor class that supports AES-256-CBC (legacy) and
RSA encryption with OAEP padding, as well as key generation, digital
signatures, and file encryption utilities.
"""

from __future__ import annotations

import base64
import hashlib
import os
import warnings
from typing import TYPE_CHECKING

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, padding, serialization
from cryptography.hazmat.primitives.asymmetric import padding as asym_padding
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from codomyrmex.exceptions import EncryptionError
from codomyrmex.logging_monitoring import get_logger

if TYPE_CHECKING:
    from pathlib import Path

logger = get_logger(__name__)


class Encryptor:
    """Encryptor for various algorithms (AES-CBC and RSA).

    Note:
        For authenticated symmetric encryption, use AESGCMEncryptor instead.
    """

    def __init__(self, algorithm: str = "AES"):
        """Initialize encryptor.

        Args:
            algorithm: Encryption algorithm ("AES" for CBC or "RSA").
        """
        self.algorithm = algorithm.upper()
        if self.algorithm not in {"AES", "RSA"}:
            raise ValueError(f"Unsupported algorithm: {algorithm}. Use 'AES' or 'RSA'.")

    def encrypt(self, data: bytes, key: bytes) -> bytes:
        """Encrypt data using the configured algorithm.

        Args:
            data: Raw bytes to encrypt.
            key: Encryption key (AES key or RSA public key PEM).

        Returns:
            Encrypted data bytes.

        Raises:
            EncryptionError: If encryption fails.
        """
        try:
            if self.algorithm == "AES":
                return self._encrypt_aes_cbc(data, key)
            if self.algorithm == "RSA":
                return self._encrypt_rsa_oaep(data, key)
            raise ValueError(f"Unknown algorithm: {self.algorithm}")
        except Exception as e:
            logger.error("Encryption error: %s", e)
            raise EncryptionError(f"Failed to encrypt: {e}") from e

    def decrypt(self, data: bytes, key: bytes) -> bytes:
        """Decrypt data using the configured algorithm.

        Args:
            data: Encrypted data bytes.
            key: Decryption key (AES key or RSA private key PEM).

        Returns:
            Decrypted data bytes.

        Raises:
            EncryptionError: If decryption fails.
        """
        try:
            if self.algorithm == "AES":
                return self._decrypt_aes_cbc(data, key)
            if self.algorithm == "RSA":
                return self._decrypt_rsa_oaep(data, key)
            raise ValueError(f"Unknown algorithm: {self.algorithm}")
        except Exception as e:
            logger.error("Decryption error: %s", e)
            raise EncryptionError(f"Failed to decrypt: {e}") from e

    def generate_key(self) -> bytes:
        """Generate a new encryption key for the configured algorithm.

        Returns:
            Generated key (32-byte AES key or RSA private key PEM).
        """
        if self.algorithm == "AES":
            return os.urandom(32)  # 256-bit key
        if self.algorithm == "RSA":
            private_key = rsa.generate_private_key(
                public_exponent=65537, key_size=2048, backend=default_backend()
            )
            return private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            )
        raise ValueError(f"Unknown algorithm: {self.algorithm}")

    def derive_key(self, password: str, salt: bytes, iterations: int = 100000) -> bytes:
        """Derive a 32-byte AES key from a password using PBKDF2.

        Args:
            password: Password to derive key from.
            salt: Random salt bytes (should be at least 16 bytes).
            iterations: Number of PBKDF2 iterations (default: 100,000).

        Returns:
            32-byte derived key.
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=iterations,
            backend=default_backend(),
        )
        return kdf.derive(password.encode())

    def sign(self, data: bytes, private_key: bytes) -> bytes:
        """Create a digital signature for data using RSA-PSS.

        Args:
            data: Data to sign.
            private_key: RSA private key in PEM format.

        Returns:
            Digital signature bytes.

        Raises:
            EncryptionError: If signing fails.
        """
        try:
            private_key_obj = serialization.load_pem_private_key(
                private_key, password=None, backend=default_backend()
            )
            if not isinstance(private_key_obj, rsa.RSAPrivateKey):
                raise ValueError("Provided key is not an RSA private key.")

            signature = private_key_obj.sign(
                data,
                asym_padding.PSS(
                    mgf=asym_padding.MGF1(hashes.SHA256()),
                    salt_length=asym_padding.PSS.MAX_LENGTH,
                ),
                hashes.SHA256(),
            )
            return signature
        except Exception as e:
            logger.error("Signing error: %s", e)
            raise EncryptionError(f"Failed to sign data: {e}") from e

    def verify(self, data: bytes, signature: bytes, public_key: bytes) -> bool:
        """Verify an RSA-PSS digital signature.

        Args:
            data: Original data.
            signature: Digital signature to verify.
            public_key: RSA public key in PEM format.

        Returns:
            True if signature is valid, False otherwise.
        """
        try:
            public_key_obj = serialization.load_pem_public_key(
                public_key, backend=default_backend()
            )
            if not isinstance(public_key_obj, rsa.RSAPublicKey):
                return False

            public_key_obj.verify(
                signature,
                data,
                asym_padding.PSS(
                    mgf=asym_padding.MGF1(hashes.SHA256()),
                    salt_length=asym_padding.PSS.MAX_LENGTH,
                ),
                hashes.SHA256(),
            )
            return True
        except Exception as e:
            logger.debug("Signature verification failed: %s", e)
            return False

    def _encrypt_aes_cbc(self, data: bytes, key: bytes) -> bytes:
        """Encrypt using AES-256-CBC."""
        warnings.warn(
            "AES-CBC mode does not provide authentication. "
            "Consider using AESGCMEncryptor for authenticated encryption.",
            DeprecationWarning,
            stacklevel=3,
        )
        # Ensure key is 32 bytes
        if len(key) != 32:
            key = hashlib.sha256(key).digest()

        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()

        # Pad data to 128-bit blocks (16 bytes)
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(data) + padder.finalize()

        encrypted = encryptor.update(padded_data) + encryptor.finalize()
        return iv + encrypted

    def _decrypt_aes_cbc(self, data: bytes, key: bytes) -> bytes:
        """Decrypt using AES-256-CBC."""
        if len(data) < 16:
            raise ValueError("Ciphertext too short for AES-CBC (missing IV).")

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

    def _encrypt_rsa_oaep(self, data: bytes, key: bytes) -> bytes:
        """Encrypt using RSA-OAEP."""
        public_key = serialization.load_pem_public_key(key, backend=default_backend())
        if not isinstance(public_key, rsa.RSAPublicKey):
            raise ValueError("Provided key is not an RSA public key.")

        return public_key.encrypt(
            data,
            asym_padding.OAEP(
                mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )

    def _decrypt_rsa_oaep(self, data: bytes, key: bytes) -> bytes:
        """Decrypt using RSA-OAEP."""
        private_key = serialization.load_pem_private_key(
            key, password=None, backend=default_backend()
        )
        if not isinstance(private_key, rsa.RSAPrivateKey):
            raise ValueError("Provided key is not an RSA private key.")

        return private_key.decrypt(
            data,
            asym_padding.OAEP(
                mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )

    # --- Utility Methods ---

    def encrypt_string(
        self, plaintext: str, key: bytes, encoding: str = "utf-8"
    ) -> str:
        """Encrypt a string and return base64-encoded ciphertext.

        Args:
            plaintext: String to encrypt.
            key: Encryption key.
            encoding: String encoding (default: "utf-8").

        Returns:
            Base64-encoded encrypted string.
        """
        encrypted = self.encrypt(plaintext.encode(encoding), key)
        return base64.b64encode(encrypted).decode("ascii")

    def decrypt_string(
        self, ciphertext: str, key: bytes, encoding: str = "utf-8"
    ) -> str:
        """Decrypt a base64-encoded ciphertext to string.

        Args:
            ciphertext: Base64-encoded encrypted string.
            key: Decryption key.
            encoding: String encoding (default: "utf-8").

        Returns:
            Decrypted string.
        """
        encrypted = base64.b64decode(ciphertext.encode("ascii"))
        return self.decrypt(encrypted, key).decode(encoding)

    def encrypt_file(
        self, input_path: str | Path, output_path: str | Path, key: bytes
    ) -> bool:
        """Encrypt a file.

        Args:
            input_path: Path to input file.
            output_path: Path to output encrypted file.
            key: Encryption key.

        Returns:
            True if successful.

        Raises:
            EncryptionError: If encryption fails.
        """
        try:
            with open(input_path, "rb") as f:
                plaintext = f.read()

            ciphertext = self.encrypt(plaintext, key)

            with open(output_path, "wb") as f:
                f.write(ciphertext)

            logger.info("Encrypted file: %s -> %s", input_path, output_path)
            return True
        except Exception as e:
            logger.error("File encryption error: %s", e)
            raise EncryptionError(f"Failed to encrypt file: {e}") from e

    def decrypt_file(
        self, input_path: str | Path, output_path: str | Path, key: bytes
    ) -> bool:
        """Decrypt a file.

        Args:
            input_path: Path to encrypted file.
            output_path: Path to output decrypted file.
            key: Decryption key.

        Returns:
            True if successful.

        Raises:
            EncryptionError: If decryption fails.
        """
        try:
            with open(input_path, "rb") as f:
                ciphertext = f.read()

            plaintext = self.decrypt(ciphertext, key)

            with open(output_path, "wb") as f:
                f.write(plaintext)

            logger.info("Decrypted file: %s -> %s", input_path, output_path)
            return True
        except Exception as e:
            logger.error("File decryption error: %s", e)
            raise EncryptionError(f"Failed to decrypt file: {e}") from e

    @staticmethod
    def hash_data(data: bytes, algorithm: str = "sha256") -> str:
        """Compute hexadecimal hash of data.

        Args:
            data: Data to hash.
            algorithm: Hash algorithm ("sha256", "sha384", "sha512", or "md5").

        Returns:
            Hexadecimal hash string.
        """
        alg = algorithm.lower()
        if alg == "sha256":
            return hashlib.sha256(data).hexdigest()
        if alg == "sha384":
            return hashlib.sha384(data).hexdigest()
        if alg == "sha512":
            return hashlib.sha512(data).hexdigest()
        if alg == "md5":
            return hashlib.md5(data, usedforsecurity=False).hexdigest()
        raise ValueError(f"Unknown hash algorithm: {algorithm}")

    @staticmethod
    def generate_salt(length: int = 16) -> bytes:
        """Generate cryptographically secure random salt.

        Args:
            length: Salt length in bytes (default: 16).

        Returns:
            Random salt bytes.
        """
        return os.urandom(length)

    def generate_key_pair(self, key_size: int = 2048) -> tuple[bytes, bytes]:
        """Generate RSA key pair.

        Args:
            key_size: RSA key size in bits (default: 2048).

        Returns:
            tuple of (private_key_pem, public_key_pem).
        """
        private_key = rsa.generate_private_key(
            public_exponent=65537, key_size=key_size, backend=default_backend()
        )

        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )

        public_pem = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

        return private_pem, public_pem


# --- Convenience Functions ---


def encrypt_data(data: bytes, key: bytes, algorithm: str = "AES") -> bytes:
    """Encrypt data using specified algorithm."""
    return Encryptor(algorithm).encrypt(data, key)


def decrypt_data(data: bytes, key: bytes, algorithm: str = "AES") -> bytes:
    """Decrypt data using specified algorithm."""
    return Encryptor(algorithm).decrypt(data, key)


def generate_aes_key() -> bytes:
    """Generate a random 32-byte AES key."""
    return os.urandom(32)
