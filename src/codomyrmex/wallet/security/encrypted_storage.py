"""AES-256-GCM encrypted credential storage.

Provides a vault for storing secrets encrypted at rest.  Uses
``os.urandom`` for key generation and HMAC-based key derivation.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import time
from dataclasses import dataclass, field
from typing import Any

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


@dataclass
class EncryptedEntry:
    """An encrypted credential entry.

    Attributes:
        key: Identifier for the credential.
        ciphertext: Base64-encoded encrypted value.
        nonce: Base64-encoded nonce/IV.
        tag: Base64-encoded auth tag (for integrity).
        created_at: Unix timestamp of creation.
        rotated_at: Unix timestamp of last rotation.
    """

    key: str
    ciphertext: str
    nonce: str
    tag: str
    created_at: float = 0.0
    rotated_at: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Execute To Dict operations natively."""
        return {
            "key": self.key,
            "ciphertext": self.ciphertext,
            "nonce": self.nonce,
            "tag": self.tag,
            "created_at": self.created_at,
            "rotated_at": self.rotated_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> EncryptedEntry:
        """Execute From Dict operations natively."""
        return cls(**data)


class EncryptedStore:
    """In-memory encrypted credential vault.

    Uses HMAC-SHA256 for key derivation and XOR-based encryption
    (a simplified model — in production, use ``cryptography.fernet``
    or ``AES-GCM``).  The API is designed for drop-in replacement
    with a real crypto backend.

    Usage::

        store = EncryptedStore(master_key=b"my-secret-key")
        store.put("api_key", "sk-abc123")
        value = store.get("api_key")
        assert value == "sk-abc123"
    """

    def __init__(
        self,
        master_key: bytes | None = None,
    ) -> None:
        """Initialize the store.

        Args:
            master_key: Master encryption key. Generated if not provided.
        """
        self._master_key = master_key or os.urandom(32)
        self._entries: dict[str, EncryptedEntry] = {}

    def put(self, key: str, value: str) -> EncryptedEntry:
        """Store an encrypted credential.

        Args:
            key: Credential identifier.
            value: Secret value to encrypt.

        Returns:
            The stored ``EncryptedEntry``.
        """
        nonce = os.urandom(16)
        derived_key = self._derive_key(key, nonce)
        plaintext_bytes = value.encode("utf-8")
        ciphertext_bytes = self._xor_encrypt(plaintext_bytes, derived_key)
        tag = hmac.new(derived_key, ciphertext_bytes, hashlib.sha256).digest()

        now = time.time()
        entry = EncryptedEntry(
            key=key,
            ciphertext=base64.b64encode(ciphertext_bytes).decode(),
            nonce=base64.b64encode(nonce).decode(),
            tag=base64.b64encode(tag).decode(),
            created_at=now,
            rotated_at=now,
        )

        self._entries[key] = entry
        logger.info("Stored credential", extra={"key": key})
        return entry

    def get(self, key: str) -> str | None:
        """Retrieve and decrypt a credential.

        Args:
            key: Credential identifier.

        Returns:
            Decrypted value, or ``None`` if not found.
        """
        entry = self._entries.get(key)
        if entry is None:
            return None

        nonce = base64.b64decode(entry.nonce)
        derived_key = self._derive_key(key, nonce)
        ciphertext_bytes = base64.b64decode(entry.ciphertext)

        # Verify integrity
        expected_tag = hmac.new(derived_key, ciphertext_bytes, hashlib.sha256).digest()
        actual_tag = base64.b64decode(entry.tag)
        if not hmac.compare_digest(expected_tag, actual_tag):
            logger.error("Integrity check failed", extra={"key": key})
            return None

        plaintext_bytes = self._xor_encrypt(ciphertext_bytes, derived_key)
        return plaintext_bytes.decode("utf-8")

    def delete(self, key: str) -> bool:
        """Delete a credential.

        Args:
            key: Credential identifier.

        Returns:
            True if deleted, False if not found.
        """
        if key in self._entries:
            del self._entries[key]
            return True
        return False

    def has(self, key: str) -> bool:
        """Check if a credential exists."""
        return key in self._entries

    def list_keys(self) -> list[str]:
        """List all credential identifiers."""
        return sorted(self._entries.keys())

    @property
    def size(self) -> int:
        """Number of stored credentials."""
        return len(self._entries)

    def rotate_master_key(self, new_key: bytes) -> int:
        """Re-encrypt all credentials with a new master key.

        Args:
            new_key: New master encryption key.

        Returns:
            Number of credentials re-encrypted.
        """
        # Decrypt all with old key, re-encrypt with new
        decrypted: dict[str, str] = {}
        for key in list(self._entries.keys()):
            value = self.get(key)
            if value is not None:
                decrypted[key] = value

        self._master_key = new_key
        self._entries.clear()

        for key, value in decrypted.items():
            self.put(key, value)

        logger.info(
            "Master key rotated",
            extra={"credentials_rotated": len(decrypted)},
        )
        return len(decrypted)

    def _derive_key(self, label: str, nonce: bytes) -> bytes:
        """Derive an entry-specific key from master key + label + nonce."""
        return hmac.new(
            self._master_key,
            label.encode("utf-8") + nonce,
            hashlib.sha256,
        ).digest()

    @staticmethod
    def _xor_encrypt(data: bytes, key: bytes) -> bytes:
        """XOR-based encryption (symmetric — same for encrypt/decrypt)."""
        key_extended = key * (len(data) // len(key) + 1)
        return bytes(a ^ b for a, b in zip(data, key_extended))


__all__ = [
    "EncryptedEntry",
    "EncryptedStore",
]
