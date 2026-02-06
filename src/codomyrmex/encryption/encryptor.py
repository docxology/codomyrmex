"""Encryption utilities.

This module provides cryptographic operations including:
- AES-256 symmetric encryption with CBC mode
- RSA asymmetric encryption with OAEP padding
- Key generation and password-based key derivation (PBKDF2)
- Digital signatures with PSS padding
- File encryption utilities
- Secure hashing functions
"""
import base64
import hashlib
import os
import warnings

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, padding, serialization
from cryptography.hazmat.primitives.asymmetric import padding as asym_padding
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from codomyrmex.exceptions import EncryptionError
from codomyrmex.logging_monitoring.logger_config import get_logger

logger = get_logger(__name__)


class Encryptor:
    """Encryptor for various algorithms."""

    def __init__(self, algorithm: str = "AES"):
        """Initialize encryptor.

        Args:
            algorithm: Encryption algorithm (AES, RSA)
        """
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
        warnings.warn(
            "AES-CBC mode does not provide authentication. "
            "Consider using AESGCMEncryptor for authenticated encryption.",
            DeprecationWarning,
            stacklevel=3,
        )
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

    # --- Utility Methods ---

    def encrypt_string(self, plaintext: str, key: bytes, encoding: str = "utf-8") -> str:
        """Encrypt a string and return base64-encoded ciphertext.

        Args:
            plaintext: String to encrypt
            key: Encryption key
            encoding: String encoding (default: utf-8)

        Returns:
            Base64-encoded encrypted string
        """
        encrypted = self.encrypt(plaintext.encode(encoding), key)
        return base64.b64encode(encrypted).decode("ascii")

    def decrypt_string(self, ciphertext: str, key: bytes, encoding: str = "utf-8") -> str:
        """Decrypt a base64-encoded ciphertext to string.

        Args:
            ciphertext: Base64-encoded encrypted string
            key: Decryption key
            encoding: String encoding (default: utf-8)

        Returns:
            Decrypted string
        """
        encrypted = base64.b64decode(ciphertext.encode("ascii"))
        return self.decrypt(encrypted, key).decode(encoding)

    def encrypt_file(self, input_path: str, output_path: str, key: bytes) -> bool:
        """Encrypt a file.

        Args:
            input_path: Path to input file
            output_path: Path to output encrypted file
            key: Encryption key

        Returns:
            True if successful

        Raises:
            EncryptionError: If encryption fails
        """
        try:
            with open(input_path, "rb") as f:
                plaintext = f.read()

            ciphertext = self.encrypt(plaintext, key)

            with open(output_path, "wb") as f:
                f.write(ciphertext)

            logger.info(f"Encrypted file: {input_path} -> {output_path}")
            return True
        except Exception as e:
            logger.error(f"File encryption error: {e}")
            raise EncryptionError(f"Failed to encrypt file: {str(e)}") from e

    def decrypt_file(self, input_path: str, output_path: str, key: bytes) -> bool:
        """Decrypt a file.

        Args:
            input_path: Path to encrypted file
            output_path: Path to output decrypted file
            key: Decryption key

        Returns:
            True if successful

        Raises:
            EncryptionError: If decryption fails
        """
        try:
            with open(input_path, "rb") as f:
                ciphertext = f.read()

            plaintext = self.decrypt(ciphertext, key)

            with open(output_path, "wb") as f:
                f.write(plaintext)

            logger.info(f"Decrypted file: {input_path} -> {output_path}")
            return True
        except Exception as e:
            logger.error(f"File decryption error: {e}")
            raise EncryptionError(f"Failed to decrypt file: {str(e)}") from e

    @staticmethod
    def hash_data(data: bytes, algorithm: str = "sha256") -> str:
        """Compute hash of data.

        Args:
            data: Data to hash
            algorithm: Hash algorithm (sha256, sha512, sha384, md5)

        Returns:
            Hexadecimal hash string
        """
        if algorithm == "sha256":
            return hashlib.sha256(data).hexdigest()
        elif algorithm == "sha512":
            return hashlib.sha512(data).hexdigest()
        elif algorithm == "sha384":
            return hashlib.sha384(data).hexdigest()
        elif algorithm == "md5":
            return hashlib.md5(data).hexdigest()
        else:
            raise ValueError(f"Unknown hash algorithm: {algorithm}")

    @staticmethod
    def generate_salt(length: int = 16) -> bytes:
        """Generate cryptographically secure random salt.

        Args:
            length: Salt length in bytes (default: 16)

        Returns:
            Random salt bytes
        """
        return os.urandom(length)

    def generate_key_pair(self, key_size: int = 2048) -> tuple[bytes, bytes]:
        """Generate RSA key pair.

        Args:
            key_size: RSA key size in bits (default: 2048)

        Returns:
            Tuple of (private_key_pem, public_key_pem)
        """
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
            backend=default_backend()
        )

        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

        public_pem = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        return private_pem, public_pem


# Convenience functions for module-level access
def encrypt_data(data: bytes, key: bytes, algorithm: str = "AES") -> bytes:
    """Encrypt data using specified algorithm.

    Args:
        data: Data to encrypt
        key: Encryption key
        algorithm: Algorithm (AES or RSA)

    Returns:
        Encrypted data
    """
    return Encryptor(algorithm).encrypt(data, key)


def decrypt_data(data: bytes, key: bytes, algorithm: str = "AES") -> bytes:
    """Decrypt data using specified algorithm.

    Args:
        data: Encrypted data
        key: Decryption key
        algorithm: Algorithm (AES or RSA)

    Returns:
        Decrypted data
    """
    return Encryptor(algorithm).decrypt(data, key)


def generate_aes_key() -> bytes:
    """Generate a random AES-256 key.

    Returns:
        32-byte AES key
    """
    return os.urandom(32)
