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
        signature = deserializer.sign(data, key="secret")
        if not deserializer.verify(data, key="secret", signature=signature):
            raise IntegrityError("Tampered!")
    """

    def __init__(self) -> None:
        self._serializer = AgentSerializer()

    def deserialize(self, data: bytes) -> AgentSnapshot:
        """Deserialize bytes to an AgentSnapshot.

        Args:
            data: UTF-8 JSON bytes.

        Returns:
            Reconstructed AgentSnapshot.
        """
        return self._serializer.deserialize_snapshot(data)

    def verify(
        self,
        data: bytes,
        key: str,
        signature: str | None = None,
    ) -> bool:
        """Verify HMAC-SHA256 integrity of serialized data.

        Args:
            data: The serialized payload bytes.
            key: Secret key used for signing.
            signature: Expected HMAC digest.  It is required; omitting it
                fails closed because a digest computed from the same payload
                cannot establish integrity.

        Returns:
            True if the signature matches.
        """
        if not signature:
            return False
        computed = self._compute_hmac(data, key)
        return hmac.compare_digest(computed, signature)

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
        self,
        data: bytes,
        signature: str,
        key: str,
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
            key.encode("utf-8"),
            data,
            hashlib.sha256,
        ).hexdigest()


__all__ = ["AgentDeserializer", "IntegrityError"]
