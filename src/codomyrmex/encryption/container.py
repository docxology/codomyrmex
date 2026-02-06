"""Secure data container for encrypted storage."""

import json
from typing import Any

from .aes_gcm import AESGCMEncryptor


class SecureDataContainer:
    """A container for storing and retrieving encrypted data objects."""

    def __init__(self, key: bytes):
        self.encryptor = AESGCMEncryptor(key)

    def pack(self, data: Any, metadata: dict[str, Any] | None = None) -> bytes:
        """Serialize and encrypt a data object."""
        payload = {
            "data": data,
            "metadata": metadata or {}
        }
        json_data = json.dumps(payload).encode()
        return self.encryptor.encrypt(json_data)

    def unpack(self, encrypted_data: bytes) -> dict[str, Any]:
        """Decrypt and deserialize a data object."""
        json_data = self.encryptor.decrypt(encrypted_data)
        return json.loads(json_data.decode())
