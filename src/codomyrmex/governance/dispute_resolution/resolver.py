"""Dispute resolution workflow: filing, evidence collection, mediation, resolution.

Provides a structured process for handling disputes arising from contract
violations or policy disagreements.  Each dispute progresses through a defined
lifecycle: FILED -> UNDER_REVIEW -> MEDIATION -> RESOLVED (or DISMISSED).
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional

logger = logging.getLogger(__name__)


class DisputeStatus(Enum):
    """Lifecycle stages for a dispute."""

    FILED = "filed"
    UNDER_REVIEW = "under_review"
    MEDIATION = "mediation"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"


class DisputeError(Exception):
    """Raised on invalid dispute operations."""


@dataclass
class Evidence:
    """A piece of evidence submitted to a dispute.

    Attributes:
        id: Unique evidence identifier.
        submitted_by: Name of the submitting party.
        description: What this evidence demonstrates.
        content: The evidence payload (text, reference, etc.).
        submitted_at: Timestamp of submission.
    """

    id: str
    submitted_by: str
    description: str
    content: str
    submitted_at: datetime = field(default_factory=datetime.now)


@dataclass
class Dispute:
    """Internal representation of a dispute record."""

    id: str
    contract_id: str
    claimant: str
    issue: str
    status: DisputeStatus = DisputeStatus.FILED
    evidence: list[Evidence] = field(default_factory=list)
    mediation_notes: list[str] = field(default_factory=list)
    resolution: Optional[str] = None
    filed_at: datetime = field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None


class DisputeResolver:
    """Manages the dispute resolution lifecycle.

    Usage::

        resolver = DisputeResolver()
        dispute = resolver.file_dispute("contract-123", "Alice", "Late delivery")
        resolver.add_evidence(dispute["id"], {
            "submitted_by": "Alice",
            "description": "Delivery receipt showing 2-week delay",
            "content": "Receipt #4521 dated 2024-03-15",
        })
        result = resolver.mediate(dispute["id"])
        final = resolver.resolve(dispute["id"], "Partial refund of 25%")
    """

    def __init__(self) -> None:
        self._disputes: dict[str, Dispute] = {}

    def file_dispute(
        self,
        contract_id: str,
        claimant: str,
        issue: str,
    ) -> dict:
        """File a new dispute.

        Args:
            contract_id: Identifier of the related contract.
            claimant: The party filing the dispute.
            issue: Description of the grievance.

        Returns:
            A dict with ``id``, ``contract_id``, ``claimant``, ``issue``,
            ``status``, and ``filed_at``.
        """
        if not contract_id or not claimant or not issue:
            raise DisputeError("contract_id, claimant, and issue are required.")

        dispute = Dispute(
            id=str(uuid.uuid4()),
            contract_id=contract_id,
            claimant=claimant,
            issue=issue,
        )
        self._disputes[dispute.id] = dispute
        logger.info(
            "Dispute %s filed by %s for contract %s",
            dispute.id[:8],
            claimant,
            contract_id[:8] if len(contract_id) > 8 else contract_id,
        )

        return self._dispute_summary(dispute)

    def get_dispute_status(self, dispute_id: str) -> dict:
        """Return the current state of a dispute.

        Args:
            dispute_id: The dispute identifier.

        Returns:
            A dict with ``id``, ``status``, ``evidence_count``,
            ``mediation_notes_count``, and ``resolution``.

        Raises:
            DisputeError: If the dispute is not found.
        """
        dispute = self._get_dispute(dispute_id)
        return {
            "id": dispute.id,
            "contract_id": dispute.contract_id,
            "claimant": dispute.claimant,
            "issue": dispute.issue,
            "status": dispute.status.value,
            "evidence_count": len(dispute.evidence),
            "mediation_notes_count": len(dispute.mediation_notes),
            "resolution": dispute.resolution,
            "filed_at": dispute.filed_at.isoformat(),
            "resolved_at": dispute.resolved_at.isoformat() if dispute.resolved_at else None,
        }

    def add_evidence(self, dispute_id: str, evidence: dict) -> dict:
        """Submit evidence to an open dispute.

        The dispute must be in FILED or UNDER_REVIEW status.

        Args:
            dispute_id: Target dispute.
            evidence: Dict with ``submitted_by`` (str), ``description`` (str),
                and ``content`` (str).

        Returns:
            A dict describing the recorded evidence.

        Raises:
            DisputeError: If the dispute is closed or evidence is invalid.
        """
        dispute = self._get_dispute(dispute_id)
        if dispute.status in (DisputeStatus.RESOLVED, DisputeStatus.DISMISSED):
            raise DisputeError("Cannot add evidence to a closed dispute.")

        submitted_by = evidence.get("submitted_by", "")
        description = evidence.get("description", "")
        content = evidence.get("content", "")
        if not submitted_by or not description:
            raise DisputeError(
                "Evidence must include 'submitted_by' and 'description'."
            )

        ev = Evidence(
            id=str(uuid.uuid4()),
            submitted_by=submitted_by,
            description=description,
            content=content,
        )
        dispute.evidence.append(ev)

        # Automatically transition from FILED to UNDER_REVIEW on first evidence
        if dispute.status == DisputeStatus.FILED:
            dispute.status = DisputeStatus.UNDER_REVIEW

        logger.info(
            "Evidence %s added to dispute %s by %s",
            ev.id[:8],
            dispute_id[:8],
            submitted_by,
        )

        return {
            "evidence_id": ev.id,
            "dispute_id": dispute_id,
            "submitted_by": submitted_by,
            "description": description,
        }

    def mediate(self, dispute_id: str) -> dict:
        """Initiate or continue mediation on a dispute.

        Transitions the dispute to MEDIATION status and generates a summary
        of the evidence collected so far.

        Args:
            dispute_id: Target dispute.

        Returns:
            A dict with ``status``, ``evidence_summary``, and ``recommendation``.

        Raises:
            DisputeError: If the dispute is already resolved/dismissed or
                still in FILED status with no evidence.
        """
        dispute = self._get_dispute(dispute_id)
        if dispute.status in (DisputeStatus.RESOLVED, DisputeStatus.DISMISSED):
            raise DisputeError("Cannot mediate a closed dispute.")
        if dispute.status == DisputeStatus.FILED and not dispute.evidence:
            raise DisputeError(
                "Evidence must be submitted before mediation can begin."
            )

        dispute.status = DisputeStatus.MEDIATION

        # Build evidence summary for mediator
        evidence_summary = []
        for ev in dispute.evidence:
            evidence_summary.append({
                "submitted_by": ev.submitted_by,
                "description": ev.description,
            })

        # Simple heuristic recommendation based on evidence count
        ev_count = len(dispute.evidence)
        if ev_count >= 3:
            recommendation = "Sufficient evidence for ruling. Recommend resolution."
        elif ev_count >= 1:
            recommendation = "Limited evidence. Consider requesting additional documentation."
        else:
            recommendation = "No evidence available. Recommend dismissal."

        note = f"Mediation initiated with {ev_count} piece(s) of evidence."
        dispute.mediation_notes.append(note)

        logger.info("Mediation started for dispute %s", dispute_id[:8])

        return {
            "dispute_id": dispute_id,
            "status": dispute.status.value,
            "evidence_summary": evidence_summary,
            "recommendation": recommendation,
        }

    def resolve(self, dispute_id: str, resolution: str) -> dict:
        """Resolve a dispute with a final determination.

        Args:
            dispute_id: Target dispute.
            resolution: The resolution statement.

        Returns:
            A dict with ``dispute_id``, ``status``, ``resolution``, and
            ``resolved_at``.

        Raises:
            DisputeError: If the dispute is already closed or resolution
                is empty.
        """
        if not resolution:
            raise DisputeError("Resolution text is required.")

        dispute = self._get_dispute(dispute_id)
        if dispute.status in (DisputeStatus.RESOLVED, DisputeStatus.DISMISSED):
            raise DisputeError("Dispute is already closed.")

        dispute.status = DisputeStatus.RESOLVED
        dispute.resolution = resolution
        dispute.resolved_at = datetime.now()

        logger.info("Dispute %s resolved: %s", dispute_id[:8], resolution[:50])

        return {
            "dispute_id": dispute_id,
            "status": dispute.status.value,
            "resolution": resolution,
            "resolved_at": dispute.resolved_at.isoformat(),
        }

    def dismiss(self, dispute_id: str, reason: str = "Insufficient merit") -> dict:
        """Dismiss a dispute without a substantive resolution.

        Args:
            dispute_id: Target dispute.
            reason: Reason for dismissal.

        Returns:
            A dict with ``dispute_id``, ``status``, and ``reason``.
        """
        dispute = self._get_dispute(dispute_id)
        if dispute.status in (DisputeStatus.RESOLVED, DisputeStatus.DISMISSED):
            raise DisputeError("Dispute is already closed.")

        dispute.status = DisputeStatus.DISMISSED
        dispute.resolution = f"DISMISSED: {reason}"
        dispute.resolved_at = datetime.now()

        logger.info("Dispute %s dismissed: %s", dispute_id[:8], reason)

        return {
            "dispute_id": dispute_id,
            "status": dispute.status.value,
            "reason": reason,
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_dispute(self, dispute_id: str) -> Dispute:
        if dispute_id not in self._disputes:
            raise DisputeError(f"Dispute '{dispute_id}' not found.")
        return self._disputes[dispute_id]

    def _dispute_summary(self, dispute: Dispute) -> dict:
        return {
            "id": dispute.id,
            "contract_id": dispute.contract_id,
            "claimant": dispute.claimant,
            "issue": dispute.issue,
            "status": dispute.status.value,
            "filed_at": dispute.filed_at.isoformat(),
        }
