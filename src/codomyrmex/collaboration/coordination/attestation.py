"""Cryptographic task attestation for multi-agent collaboration.

Provides HMAC-SHA256 signed attestations that agents use to prove
task completion. The AttestationAuthority manages key material and
supports individual and batch verification.
"""

from __future__ import annotations

import hashlib
import hmac
import os
import time
from dataclasses import dataclass
from typing import Any

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


@dataclass(frozen=True)
class TaskAttestation:
    """A signed attestation proving an agent completed a task.

    Attributes:
        task_id: Identifier of the completed task.
        agent_id: Identifier of the agent that completed the task.
        result_hash: SHA-256 hex digest of the result data.
        timestamp: Unix epoch timestamp of attestation creation.
        signature: HMAC-SHA256 hex digest binding all fields to the key.
    """

    task_id: str
    agent_id: str
    result_hash: str
    timestamp: float
    signature: str

    def to_dict(self) -> dict[str, Any]:
        """Serialize to JSON-compatible dict."""
        return {
            "task_id": self.task_id,
            "agent_id": self.agent_id,
            "result_hash": self.result_hash,
            "timestamp": self.timestamp,
            "signature": self.signature,
        }


class AttestationAuthority:
    """Issues and verifies HMAC-SHA256 task attestations.

    The authority holds a secret key and produces signatures over
    (task_id, agent_id, result_hash, timestamp). Attestations can be
    verified individually or in batch.

    Example::

        authority = AttestationAuthority()
        attestation = authority.attest("task-42", "agent-1", b"result data")
        assert authority.verify(attestation, b"result data")
    """

    def __init__(self, secret_key: bytes | None = None) -> None:
        """Initialize with an HMAC key.

        Args:
            secret_key: 32-byte key. If None, a cryptographically random
                key is generated automatically.
        """
        self._key = secret_key or os.urandom(32)
        logger.info("AttestationAuthority initialized (key_len=%d)", len(self._key))

    def _compute_result_hash(self, result_data: bytes) -> str:
        """Compute SHA-256 digest of result data.

        Args:
            result_data: Raw bytes to hash.

        Returns:
            Hex-encoded SHA-256 digest.
        """
        return hashlib.sha256(result_data).hexdigest()

    def _compute_signature(
        self,
        task_id: str,
        agent_id: str,
        result_hash: str,
        timestamp: float,
    ) -> str:
        """Compute HMAC-SHA256 signature over attestation fields.

        Args:
            task_id: Task identifier.
            agent_id: Agent identifier.
            result_hash: SHA-256 of result data.
            timestamp: Attestation timestamp.

        Returns:
            Hex-encoded HMAC-SHA256 signature.
        """
        message = f"{task_id}:{agent_id}:{result_hash}:{timestamp}".encode()
        return hmac.new(self._key, message, hashlib.sha256).hexdigest()

    def attest(
        self,
        task_id: str,
        agent_id: str,
        result_data: bytes,
        timestamp: float | None = None,
    ) -> TaskAttestation:
        """Create a signed attestation for a completed task.

        Args:
            task_id: Identifier of the completed task.
            agent_id: Identifier of the attesting agent.
            result_data: Raw result data to bind into the attestation.
            timestamp: Optional explicit timestamp (defaults to now).

        Returns:
            Signed TaskAttestation.
        """
        ts = timestamp or time.time()
        result_hash = self._compute_result_hash(result_data)
        signature = self._compute_signature(task_id, agent_id, result_hash, ts)

        attestation = TaskAttestation(
            task_id=task_id,
            agent_id=agent_id,
            result_hash=result_hash,
            timestamp=ts,
            signature=signature,
        )

        logger.debug(
            "Attested task=%s agent=%s hash=%s...",
            task_id,
            agent_id,
            result_hash[:12],
        )
        return attestation

    def verify(self, attestation: TaskAttestation, result_data: bytes) -> bool:
        """Verify an attestation against result data.

        Checks that:
        1. The result_hash matches SHA-256(result_data).
        2. The HMAC signature is valid for the attestation fields.

        Args:
            attestation: The attestation to verify.
            result_data: The original result data.

        Returns:
            True if the attestation is valid.
        """
        # Verify result hash
        expected_hash = self._compute_result_hash(result_data)
        if not hmac.compare_digest(attestation.result_hash, expected_hash):
            logger.warning(
                "Attestation result_hash mismatch for task=%s",
                attestation.task_id,
            )
            return False

        # Verify signature
        expected_sig = self._compute_signature(
            attestation.task_id,
            attestation.agent_id,
            attestation.result_hash,
            attestation.timestamp,
        )
        valid = hmac.compare_digest(attestation.signature, expected_sig)

        if not valid:
            logger.warning(
                "Attestation signature mismatch for task=%s",
                attestation.task_id,
            )

        return valid

    def batch_verify(
        self,
        attestations: list[TaskAttestation],
        results: list[bytes],
    ) -> dict[str, bool]:
        """Verify multiple attestations in batch.

        Args:
            attestations: List of attestations to verify.
            results: Corresponding result data for each attestation.

        Returns:
            Dict mapping task_id to verification result.

        Raises:
            ValueError: If attestations and results have different lengths.
        """
        if len(attestations) != len(results):
            raise ValueError(
                f"Attestation count ({len(attestations)}) != "
                f"result count ({len(results)})"
            )

        return {
            att.task_id: self.verify(att, data)
            for att, data in zip(attestations, results, strict=True)
        }


__all__ = [
    "AttestationAuthority",
    "TaskAttestation",
]
