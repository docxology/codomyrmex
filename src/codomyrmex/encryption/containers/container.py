"""Secure data container for encrypted object storage."""

from __future__ import annotations

import json
from typing import Any

from codomyrmex.encryption.algorithms.aes_gcm import AESGCMEncryptor


class SecureDataContainer:
    """A container for storing and retrieving encrypted Python objects.

    Uses AES-GCM authenticated encryption for storage and retrieval.
    """

    def __init__(self, key: bytes):
        """Initialize secure data container.

        Args:
            key: 16, 24, or 32 byte AES key.
        """
        self.encryptor = AESGCMEncryptor(key)

    def pack(self, data: Any, metadata: dict[str, Any] | None = None) -> bytes:
        """Serialize and encrypt a data object.

        Args:
            data: JSON-serializable Python object.
            metadata: Optional dictionary of metadata.

        Returns:
            Encrypted byte payload.

        Raises:
            TypeError: If data or metadata is not JSON serializable.
            EncryptionError: If encryption fails.
        """
        payload = {"data": data, "metadata": metadata or {}}
        json_data = json.dumps(payload).encode("utf-8")
        return self.encryptor.encrypt(json_data)

    def unpack(self, encrypted_data: bytes) -> dict[str, Any]:
        """Decrypt and deserialize a data object.

        Args:
            encrypted_data: Encrypted byte payload.

        Returns:
            Unpacked data and metadata dictionary.

        Raises:
            EncryptionError: If decryption/authentication fails.
            json.JSONDecodeError: If deserialization fails.
        """
        json_data = self.encryptor.decrypt(encrypted_data)
        return json.loads(json_data.decode("utf-8"))
