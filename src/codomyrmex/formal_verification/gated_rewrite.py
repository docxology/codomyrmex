"""Gated self-rewrite pipeline.

Agent proposes a code change → ``CodeChangeVerifier`` gates the change →
on approval an ``AttestationAuthority`` signs the result.

Builds on:
- :class:`~codomyrmex.formal_verification.code_change_verifier.CodeChangeVerifier`
- :class:`~codomyrmex.collaboration.coordination.attestation.AttestationAuthority`
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, timezone
from typing import TYPE_CHECKING, Any

from codomyrmex.collaboration.coordination.attestation import (
    AttestationAuthority,
    TaskAttestation,
)
from codomyrmex.formal_verification.code_change_verifier import (
    ChangeProposal,
    CodeChangeVerifier,
    VerificationResult,
)
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


@dataclass
class RewriteProposal:
    """A proposed self-rewrite from an agent.

    Attributes:
        agent_id: Identifier of the proposing agent.
        file_path: Path to the file being rewritten.
        original_source: Original Python source.
        modified_source: Proposed new source.
        rationale: Why the change was proposed.
        timestamp: When the proposal was created.
    """

    agent_id: str
    file_path: str
    original_source: str
    modified_source: str
    rationale: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now(tz=UTC).isoformat())

    def to_change_proposal(self) -> ChangeProposal:
        """Convert to a ``ChangeProposal`` for the verifier."""
        return ChangeProposal(
            file_path=self.file_path,
            original_source=self.original_source,
            modified_source=self.modified_source,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "file_path": self.file_path,
            "rationale": self.rationale,
            "timestamp": self.timestamp,
        }


@dataclass
class GateDecision:
    """Result of the rewrite gate evaluation.

    Attributes:
        approved: Whether the rewrite passed all verification rules.
        verification_result: Detailed per-rule results.
        attestation: Cryptographic attestation (only present on approval).
        proposal: The original rewrite proposal.
    """

    approved: bool
    verification_result: VerificationResult
    attestation: TaskAttestation | None = None
    proposal: RewriteProposal | None = None

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "approved": self.approved,
            "summary": self.verification_result.summary,
            "rule_results": [
                {
                    "rule_name": r.rule_name,
                    "passed": r.passed,
                    "message": r.message,
                }
                for r in self.verification_result.rule_results
            ],
        }
        if self.attestation:
            d["attestation"] = self.attestation.to_dict()
        if self.proposal:
            d["proposal"] = self.proposal.to_dict()
        return d


# ---------------------------------------------------------------------------
# Gate
# ---------------------------------------------------------------------------


class RewriteGate:
    """Evaluates a rewrite proposal against structural invariant rules.

    Wraps :class:`CodeChangeVerifier` and optionally signs approved
    changes via :class:`AttestationAuthority`.
    """

    def __init__(
        self,
        verifier: CodeChangeVerifier | None = None,
        authority: AttestationAuthority | None = None,
    ) -> None:
        self._verifier = verifier or CodeChangeVerifier()
        self._authority = authority or AttestationAuthority()

    def evaluate(self, proposal: RewriteProposal) -> GateDecision:
        """Run the verification pipeline on *proposal*.

        Returns a :class:`GateDecision` with approval status and, if
        approved, a signed :class:`TaskAttestation`.
        """
        change = proposal.to_change_proposal()
        result = self._verifier.verify(change)

        attestation: TaskAttestation | None = None
        if result.passed:
            attestation = self._authority.attest(
                task_id=f"rewrite:{proposal.file_path}",
                agent_id=proposal.agent_id,
                result_data=proposal.modified_source.encode(),
            )
            logger.info(
                "Rewrite APPROVED for %s by %s",
                proposal.file_path,
                proposal.agent_id,
            )
        else:
            logger.warning(
                "Rewrite REJECTED for %s: %s",
                proposal.file_path,
                result.summary,
            )

        return GateDecision(
            approved=result.passed,
            verification_result=result,
            attestation=attestation,
            proposal=proposal,
        )


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------


class GatedRewriter:
    """High-level orchestrator: propose → verify → attest.

    Usage::

        rewriter = GatedRewriter()
        decision = rewriter.propose(
            agent_id="agent-1",
            file_path="module.py",
            original="def foo(x): ...",
            modified="def foo(x, y): ...",
            rationale="Added parameter y",
        )
        if decision.approved:
            print(decision.attestation)
    """

    def __init__(
        self,
        verifier: CodeChangeVerifier | None = None,
        authority: AttestationAuthority | None = None,
    ) -> None:
        self._gate = RewriteGate(verifier=verifier, authority=authority)

    def propose(
        self,
        agent_id: str,
        file_path: str,
        original: str,
        modified: str,
        rationale: str = "",
    ) -> GateDecision:
        """Submit a rewrite proposal and get a gate decision.

        Args:
            agent_id: Who is proposing.
            file_path: File being changed.
            original: Original source code.
            modified: Proposed new source code.
            rationale: Human-readable explanation.

        Returns:
            :class:`GateDecision` with approval status and optional attestation.
        """
        proposal = RewriteProposal(
            agent_id=agent_id,
            file_path=file_path,
            original_source=original,
            modified_source=modified,
            rationale=rationale,
        )
        return self._gate.evaluate(proposal)


__all__ = [
    "GateDecision",
    "GatedRewriter",
    "RewriteGate",
    "RewriteProposal",
]
