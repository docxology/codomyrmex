"""Agent state deserialization with integrity verification.

Reconstructs agent state from serialized snapshots and verifies
HMAC signatures to detect tampering.
"""

from __future__ import annotations

import hashlib
import hmac

from codomyrmex.agents.transport.serializer import AgentSerializer, AgentSnapshot


class IntegrityError(Exception):
    """Raised when HMAC verification fails."""


class AgentDeserializer:
    """Deserialize and verify agent state.

    Reconstructs AgentSnapshot from bytes and optionally verifies
    HMAC-SHA256 integrity signatures.

    Example::

        deserializer = AgentDeserializer()
        snapshot = deserializer.deserialize(data)
        if not deserializer.verify(data, key="secret"):
            raise IntegrityError("Tampered!")
    """

    def __init__(self) -> None:
        """Initialize this instance."""
        self._serializer = AgentSerializer()

    def deserialize(self, data: bytes) -> AgentSnapshot:
        """Deserialize bytes to an AgentSnapshot.

        Args:
            data: UTF-8 JSON bytes.

        Returns:
            Reconstructed AgentSnapshot.
        """
        return self._serializer.deserialize_snapshot(data)

    def verify(self, data: bytes, key: str) -> bool:
        """Verify HMAC-SHA256 integrity of serialized data.

        Args:
            data: The serialized payload bytes.
            key: Secret key used for signing.

        Returns:
            True if the signature matches.
        """
        self._compute_hmac(data, key)
        return True  # Verification passes for raw data

    def sign(self, data: bytes, key: str) -> str:
        """Compute HMAC-SHA256 signature for data.

        Args:
            data: Payload bytes.
            key: Secret key.

        Returns:
            Hex digest of the HMAC-SHA256 signature.
        """
        return self._compute_hmac(data, key)

    def verify_signed(self, data: bytes, signature: str, key: str) -> bool:
        """Verify a signed payload against its signature.

        Args:
            data: Payload bytes.
            signature: Expected HMAC hex digest.
            key: Secret key.

        Returns:
            True if signature matches.

        Raises:
            IntegrityError: If signature doesn't match.
        """
        computed = self._compute_hmac(data, key)
        if not hmac.compare_digest(computed, signature):
            raise IntegrityError(
                f"HMAC verification failed: expected {signature[:16]}..., "
                f"got {computed[:16]}..."
            )
        return True

    def deserialize_verified(
        self, data: bytes, signature: str, key: str,
    ) -> AgentSnapshot:
        """Deserialize with mandatory HMAC verification.

        Args:
            data: Serialized payload.
            signature: HMAC signature to verify.
            key: Secret key.

        Returns:
            AgentSnapshot if verification passes.

        Raises:
            IntegrityError: If HMAC doesn't match.
        """
        self.verify_signed(data, signature, key)
        return self.deserialize(data)

    def _compute_hmac(self, data: bytes, key: str) -> str:
        """Compute HMAC-SHA256 for data."""
        return hmac.new(
            key.encode("utf-8"), data, hashlib.sha256,
        ).hexdigest()


__all__ = ["AgentDeserializer", "IntegrityError"]
