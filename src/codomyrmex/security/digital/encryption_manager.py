from datetime import datetime, timezone
from typing import Any, Optional, Union
import logging
import os
import sys

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from dataclasses import dataclass
import base64
import hashlib
import secrets

from codomyrmex.logging_monitoring.logger_config import get_logger




























"""
Encryption Manager for Codomyrmex Security Audit Module.

Provides secure encryption and decryption capabilities for sensitive data,
passwords, and configuration files.
"""



# Add project root to Python path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
if PROJECT_ROOT not in sys.path:
    pass
#     sys.path.insert(0, PROJECT_ROOT)  # Removed sys.path manipulation

try:

    logger = get_logger(__name__)
except ImportError:

    logger = logging.getLogger(__name__)


@dataclass
class EncryptionResult:
    """Result of an encryption or decryption operation."""

    success: bool
    data: Optional[bytes] = None
    error: Optional[str] = None
    metadata: dict[str, Any] = None


class EncryptionManager:
    """
    Secure encryption/decryption manager for sensitive data.

    Features:
    - AES-256 encryption using Fernet
    - Password-based key derivation
    - Secure key generation and storage
    - Salt generation for additional security
    - Metadata tracking for encrypted data
    """

    def __init__(self, key_file: Optional[str] = None, password: Optional[str] = None):
        """
        Initialize the encryption manager.

        Args:
            key_file: Path to encryption key file
            password: Password for key derivation (alternative to key file)
        """
        self.key_file = key_file or os.path.join(os.getcwd(), ".encryption_key")
        self.password = password
        self._fernet: Optional[Fernet] = None
        self._salt: Optional[bytes] = None

        # Initialize encryption
        self._initialize_encryption()

    def _initialize_encryption(self):
        """Initialize encryption with key or password."""
        try:
            if self.password:
                # Derive key from password
                self._initialize_from_password()
            else:
                # Load or generate key from file
                self._initialize_from_key_file()

            logger.info("Encryption manager initialized successfully")

        except (OSError, PermissionError, ValueError, TypeError, AttributeError) as e:
            logger.error(f"Failed to initialize encryption: {e}")
            raise

    def _initialize_from_key_file(self):
        """Initialize encryption using a key file."""
        if os.path.exists(self.key_file):
            # Load existing key
            try:
                with open(self.key_file, "rb") as f:
                    key = f.read()
                self._fernet = Fernet(key)
                logger.info("Loaded existing encryption key")

            except (FileNotFoundError, PermissionError, ValueError, TypeError) as e:
                logger.error(f"Failed to load encryption key: {e}")
                raise
        else:
            # Generate new key
            logger.info("Generating new encryption key")
            key = Fernet.generate_key()
            self._fernet = Fernet(key)

            # Save key securely
            try:
                os.makedirs(os.path.dirname(self.key_file), exist_ok=True)
                with open(self.key_file, "wb") as f:
                    f.write(key)
                # Set restrictive permissions
                os.chmod(self.key_file, 0o600)
                logger.info(f"New encryption key saved to {self.key_file}")

            except (OSError, PermissionError, IOError) as e:
                logger.error(f"Failed to save encryption key: {e}")
                raise

    def _initialize_from_password(self):
        """Initialize encryption using password-based key derivation."""
        if not self.password:
            raise ValueError("Password is required for password-based encryption")

        # Generate salt if not exists
        salt_file = self.key_file + ".salt"
        if os.path.exists(salt_file):
            with open(salt_file, "rb") as f:
                self._salt = f.read()
        else:
            self._salt = os.urandom(16)
            try:
                with open(salt_file, "wb") as f:
                    f.write(self._salt)
                os.chmod(salt_file, 0o600)
            except (OSError, PermissionError, IOError) as e:
                logger.error(f"Failed to save salt: {e}")
                raise

        # Derive key from password and salt
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self._salt,
            iterations=100000,
            backend=default_backend(),
        )

        key = base64.urlsafe_b64encode(kdf.derive(self.password.encode()))
        self._fernet = Fernet(key)
        logger.info("Initialized password-based encryption")

    def encrypt_data(
        self, data: Union[str, bytes], metadata: Optional[dict[str, Any]] = None
    ) -> EncryptionResult:
        """
        Encrypt data using configured encryption method.

        Args:
            data: Data to encrypt (string or bytes)
            metadata: Optional metadata to store with encrypted data

        Returns:
            EncryptionResult: Encryption result with encrypted data and metadata
        """
        try:
            if not self._fernet:
                raise RuntimeError("Encryption not initialized")

            # Convert string to bytes if needed
            if isinstance(data, str):
                data = data.encode("utf-8")

            # Encrypt data
            encrypted_data = self._fernet.encrypt(data)

            # Prepare metadata
            full_metadata = {
                "encryption_timestamp": datetime.now(timezone.utc).isoformat(),
                "data_size": len(data),
                "encrypted_size": len(encrypted_data),
                "encryption_method": "Fernet_AES256",
            }

            if metadata:
                full_metadata.update(metadata)

            return EncryptionResult(
                success=True, data=encrypted_data, metadata=full_metadata
            )

        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            return EncryptionResult(success=False, error=str(e))

    def decrypt_data(self, encrypted_data: bytes) -> EncryptionResult:
        """
        Decrypt data using configured decryption method.

        Args:
            encrypted_data: Encrypted data to decrypt

        Returns:
            EncryptionResult: Decryption result with decrypted data
        """
        try:
            if not self._fernet:
                raise RuntimeError("Encryption not initialized")

            # Decrypt data
            decrypted_data = self._fernet.decrypt(encrypted_data)

            return EncryptionResult(success=True, data=decrypted_data)

        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            return EncryptionResult(success=False, error=str(e))

    def encrypt_file(
        self,
        input_file: str,
        output_file: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> EncryptionResult:
        """
        Encrypt a file.

        Args:
            input_file: Path to file to encrypt
            output_file: Path for encrypted output (optional)
            metadata: Optional metadata

        Returns:
            EncryptionResult: Encryption result
        """
        try:
            if not os.path.exists(input_file):
                raise FileNotFoundError(f"Input file not found: {input_file}")

            # Read input file
            with open(input_file, "rb") as f:
                data = f.read()

            # Encrypt data
            result = self.encrypt_data(data, metadata)
            if not result.success:
                return result

            # Determine output file path
            if not output_file:
                output_file = input_file + ".encrypted"

            # Write encrypted data
            with open(output_file, "wb") as f:
                f.write(result.data)

            # Set restrictive permissions
            os.chmod(output_file, 0o600)

            logger.info(f"File encrypted: {input_file} -> {output_file}")
            return result

        except Exception as e:
            logger.error(f"File encryption failed: {e}")
            return EncryptionResult(success=False, error=str(e))

    def decrypt_file(
        self, input_file: str, output_file: Optional[str] = None
    ) -> EncryptionResult:
        """
        Decrypt a file.

        Args:
            input_file: Path to encrypted file
            output_file: Path for decrypted output (optional)

        Returns:
            EncryptionResult: Decryption result
        """
        try:
            if not os.path.exists(input_file):
                raise FileNotFoundError(f"Input file not found: {input_file}")

            # Read encrypted file
            with open(input_file, "rb") as f:
                encrypted_data = f.read()

            # Decrypt data
            result = self.decrypt_data(encrypted_data)
            if not result.success:
                return result

            # Determine output file path
            if not output_file:
                if input_file.endswith(".encrypted"):
                    output_file = input_file[:-10]  # Remove .encrypted extension
                else:
                    output_file = input_file + ".decrypted"

            # Write decrypted data
            with open(output_file, "wb") as f:
                f.write(result.data)

            logger.info(f"File decrypted: {input_file} -> {output_file}")
            return result

        except Exception as e:
            logger.error(f"File decryption failed: {e}")
            return EncryptionResult(success=False, error=str(e))

    def rotate_key(self, new_password: Optional[str] = None) -> bool:
        """
        Rotate encryption key for enhanced security.

        Args:
            new_password: New password for key derivation (if using password-based encryption)

        Returns:
            bool: True if rotation successful
        """
        try:
            logger.info("Starting key rotation")

            # Generate new key
            if new_password:
                self.password = new_password
                self._initialize_from_password()
            else:
                new_key = Fernet.generate_key()
                self._fernet = Fernet(new_key)

                # Save new key
                with open(self.key_file, "wb") as f:
                    f.write(new_key)
                os.chmod(self.key_file, 0o600)

            logger.info("Key rotation completed successfully")
            return True

        except Exception as e:
            logger.error(f"Key rotation failed: {e}")
            return False

    def get_key_info(self) -> dict[str, Any]:
        """Get information about current encryption key."""
        info = {
            "key_file": self.key_file,
            "using_password": self.password is not None,
            "salt_available": self._salt is not None,
            "encryption_initialized": self._fernet is not None,
        }

        if self._salt:
            info["salt_hash"] = hashlib.sha256(self._salt).hexdigest()

        return info

    @staticmethod
    def generate_secure_password(length: int = 32) -> str:
        """
        Generate a secure random password.

        Args:
            length: Length of password to generate

        Returns:
            str: Secure random password
        """
        alphabet = (
            "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
        )
        return "".join(secrets.choice(alphabet) for _ in range(length))

    @staticmethod
    def hash_password(password: str, salt: Optional[bytes] = None) -> dict[str, str]:
        """
        Hash a password for secure storage.

        Args:
            password: Password to hash
            salt: Salt to use (generated if not provided)

        Returns:
            Dict containing hash and salt
        """
        if not salt:
            salt = os.urandom(16)

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend(),
        )

        hash_bytes = kdf.derive(password.encode())
        hash_str = base64.b64encode(hash_bytes).decode()

        return {
            "hash": hash_str,
            "salt": base64.b64encode(salt).decode(),
            "iterations": 100000,
            "algorithm": "PBKDF2_SHA256",
        }

    @staticmethod
    def verify_password(password: str, hash_data: dict[str, str]) -> bool:
        """
        Verify a password against its hash.

        Args:
            password: Password to verify
            hash_data: Hash data from hash_password()

        Returns:
            bool: True if password matches
        """
        try:
            salt = base64.b64decode(hash_data["salt"])
            stored_hash = base64.b64decode(hash_data["hash"])

            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=hash_data.get("iterations", 100000),
                backend=default_backend(),
            )

            computed_hash = kdf.derive(password.encode())
            return computed_hash == stored_hash

        except Exception as e:
            logger.error(f"Password verification failed: {e}")
            return False


# Convenience functions
def encrypt_sensitive_data(
    data: Union[str, bytes],
    key_file: Optional[str] = None,
    password: Optional[str] = None,
) -> EncryptionResult:
    """
    Convenience function to encrypt sensitive data.

    Args:
        data: Data to encrypt
        key_file: Path to encryption key file
        password: Password for encryption

    Returns:
        EncryptionResult: Encryption result
    """
    manager = EncryptionManager(key_file, password)
    return manager.encrypt_data(data)


def decrypt_sensitive_data(
    encrypted_data: bytes,
    key_file: Optional[str] = None,
    password: Optional[str] = None,
) -> EncryptionResult:
    """
    Convenience function to decrypt sensitive data.

    Args:
        encrypted_data: Encrypted data to decrypt
        key_file: Path to encryption key file
        password: Password for decryption

    Returns:
        EncryptionResult: Decryption result
    """
    manager = EncryptionManager(key_file, password)
    return manager.decrypt_data(encrypted_data)
