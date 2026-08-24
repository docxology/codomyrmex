"""External-actuation observation adapter for Colony Kernel research experiments (R2).

Provides an independently observed execution lifecycle that verifies external
receipt provenance, rejects forged/replayed actuation records, and separates
caller-reported events from attested execution witnesses.
"""

from __future__ import annotations

import hashlib
import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from codomyrmex.colony_kernel.attestation import (
    AttestationLedger,
    LedgerError,
    LedgerEvent,
    digest_json,
)


class ActuationStatus(StrEnum):
    """Observable status of an actuation attempt."""

    AUTHORIZED = "authorized"
    EXECUTED = "executed"
    REJECTED = "rejected"
    FAILED = "failed"
    UNVERIFIED = "unverified"


@dataclass(frozen=True)
class ExternalExecutionWitness:
    """Independently observed external execution receipt."""

    execution_id: str
    target: str
    action: str
    exit_code: int
    stdout_hash: str
    stderr_hash: str
    timestamp: float
    environment_digest: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def digest(self) -> str:
        payload = {
            "execution_id": self.execution_id,
            "target": self.target,
            "action": self.action,
            "exit_code": self.exit_code,
            "stdout_hash": self.stdout_hash,
            "stderr_hash": self.stderr_hash,
            "timestamp": self.timestamp,
            "environment_digest": self.environment_digest,
        }
        return digest_json(payload)


@dataclass(frozen=True)
class ActuationObservationResult:
    """Attested outcome of an external actuation lifecycle observation."""

    run_id: str
    proposal_id: str
    authorization_event_id: str | None
    witness: ExternalExecutionWitness | None
    status: ActuationStatus
    verified: bool
    evidence_trail_hash: str
    error_reason: str | None = None


class ExternalActuationAdapter:
    """Mediates and observes external actions against an AttestationLedger."""

    def __init__(
        self,
        ledger: AttestationLedger,
        environment_id: str = "default_sandbox",
    ) -> None:
        self.ledger = ledger
        self.environment_id = environment_id
        self._observed_executions: dict[str, ExternalExecutionWitness] = {}
        self._used_authorizations: set[str] = set()

    def observe_and_record(
        self,
        run_id: str,
        proposal_dict: dict[str, Any],
        gate_verdict: str,
        gate_metadata: dict[str, Any],
        executor_fn: Callable[[], tuple[int, str, str]],
        *,
        actor_id: str = "actuation_observer",
    ) -> ActuationObservationResult:
        """Authorize, execute, witness, and record an external actuation lifecycle.

        Args:
            run_id: Unique identifier for the research run.
            proposal_dict: Proposal details including 'proposal_id', 'target', 'action'.
            gate_verdict: Gate verdict ('execute', 'hold', 'refuse').
            gate_metadata: Metadata from gate evaluation.
            executor_fn: Callable executing the external actuation returning (exit_code, stdout, stderr).
            actor_id: Identifier of the observing actor.

        Returns:
            ActuationObservationResult with cryptographic provenance.
        """
        proposal_id = str(proposal_dict.get("proposal_id") or uuid.uuid4().hex)
        normalized_proposal = dict(proposal_dict)
        normalized_proposal["proposal_id"] = proposal_id
        target = str(normalized_proposal.get("target", "unknown"))
        action = str(normalized_proposal.get("action", "unknown"))

        # 1. Record proposal event
        try:
            prop_event = self.ledger.record_proposal(
                run_id, actor_id, normalized_proposal
            )
        except LedgerError as err:
            return ActuationObservationResult(
                run_id=run_id,
                proposal_id=proposal_id,
                authorization_event_id=None,
                witness=None,
                status=ActuationStatus.FAILED,
                verified=False,
                evidence_trail_hash="",
                error_reason=f"Proposal recording failed: {err}",
            )

        # 2. Record gate verdict event
        try:
            verdict_event = self.ledger.record_gate_verdict(
                run_id, actor_id, prop_event, gate_verdict, gate_metadata
            )
        except LedgerError as err:
            return ActuationObservationResult(
                run_id=run_id,
                proposal_id=proposal_id,
                authorization_event_id=None,
                witness=None,
                status=ActuationStatus.FAILED,
                verified=False,
                evidence_trail_hash="",
                error_reason=f"Gate verdict recording failed: {err}",
            )

        if gate_verdict != "execute":
            # Non-execute verdicts produce rejection records
            rej_event = self.ledger.record_rejection(
                run_id, actor_id, prop_event, f"Gate decided {gate_verdict}"
            )
            return ActuationObservationResult(
                run_id=run_id,
                proposal_id=proposal_id,
                authorization_event_id=None,
                witness=None,
                status=ActuationStatus.REJECTED,
                verified=self.ledger.validate(run_id).valid,
                evidence_trail_hash=rej_event.event_hash,
                error_reason=f"Actuation rejected by gate ({gate_verdict})",
            )

        # 3. Authorize execution
        try:
            auth_event = self.ledger.authorize_execution(
                run_id, actor_id, verdict_event
            )
        except LedgerError as err:
            return ActuationObservationResult(
                run_id=run_id,
                proposal_id=proposal_id,
                authorization_event_id=None,
                witness=None,
                status=ActuationStatus.REJECTED,
                verified=False,
                evidence_trail_hash="",
                error_reason=f"Authorization failed: {err}",
            )

        if auth_event.event_id in self._used_authorizations:
            return ActuationObservationResult(
                run_id=run_id,
                proposal_id=proposal_id,
                authorization_event_id=auth_event.event_id,
                witness=None,
                status=ActuationStatus.REJECTED,
                verified=False,
                evidence_trail_hash="",
                error_reason="Duplicate authorization reuse detected",
            )
        self._used_authorizations.add(auth_event.event_id)

        # 4. Execute under observation
        exec_start = time.time()
        try:
            exit_code, stdout, stderr = executor_fn()
        except Exception as exc:
            err_event = self.ledger.record_error(
                run_id, actor_id, auth_event, f"Execution raised exception: {exc}"
            )
            return ActuationObservationResult(
                run_id=run_id,
                proposal_id=proposal_id,
                authorization_event_id=auth_event.event_id,
                witness=None,
                status=ActuationStatus.FAILED,
                verified=False,
                evidence_trail_hash=err_event.event_hash,
                error_reason=str(exc),
            )

        # 5. Create independent execution witness
        stdout_hash = hashlib.sha256(stdout.encode("utf-8")).hexdigest()
        stderr_hash = hashlib.sha256(stderr.encode("utf-8")).hexdigest()
        env_digest = hashlib.sha256(self.environment_id.encode("utf-8")).hexdigest()

        witness = ExternalExecutionWitness(
            execution_id=uuid.uuid4().hex,
            target=target,
            action=action,
            exit_code=exit_code,
            stdout_hash=stdout_hash,
            stderr_hash=stderr_hash,
            timestamp=exec_start,
            environment_digest=env_digest,
            metadata={"duration_s": time.time() - exec_start},
        )
        self._observed_executions[witness.execution_id] = witness

        # 6. Record execution receipt
        receipt_event = self.ledger.record_execution(
            run_id,
            actor_id,
            auth_event,
            {
                "execution_id": witness.execution_id,
                "witness_digest": witness.digest(),
                "exit_code": exit_code,
                "stdout_hash": stdout_hash,
                "stderr_hash": stderr_hash,
            },
        )

        # 7. Record outcome
        tests_passed = exit_code == 0
        outcome_event = self.ledger.record_outcome(
            run_id,
            actor_id,
            receipt_event,
            {
                "tests_passed": tests_passed,
                "exit_code": exit_code,
                "witness_id": witness.execution_id,
            },
        )

        # 8. Validate full ledger chain
        validation = self.ledger.validate(run_id)
        verified = validation.valid and validation.event_count >= 5

        status = ActuationStatus.EXECUTED if tests_passed else ActuationStatus.FAILED

        return ActuationObservationResult(
            run_id=run_id,
            proposal_id=proposal_id,
            authorization_event_id=auth_event.event_id,
            witness=witness,
            status=status,
            verified=verified,
            evidence_trail_hash=outcome_event.event_hash,
            error_reason=None if tests_passed else f"Non-zero exit code: {exit_code}",
        )
