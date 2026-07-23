from __future__ import annotations

import json

import pytest

from codomyrmex.colony_kernel.attestation import (
    AttestationLedger,
    Ed25519Signer,
    Ed25519Verifier,
    HMACSigner,
    LedgerError,
    LedgerEventType,
    LedgerValidationStatus,
)


def _ledger(tmp_path):
    return AttestationLedger(
        tmp_path / "ledger.sqlite",
        signer=HMACSigner(b"0123456789abcdef0123456789abcdef", key_id="test"),
        clock=lambda: 123.0,
    )


def _complete_run(ledger: AttestationLedger):
    proposal = ledger.record_proposal(
        "run-1", "agent-a", {"proposal_id": "proposal-1", "target": "safe.py"}
    )
    verdict = ledger.record_gate_verdict(
        "run-1", "gate", proposal, "execute", {"decision": "execute", "score": 0.8}
    )
    authorization = ledger.authorize_execution("run-1", "gate", verdict)
    execution = ledger.record_execution(
        "run-1",
        "executor",
        authorization,
        {"execution_id": "execution-1", "exit_code": 0, "artifact_hashes": []},
    )
    outcome = ledger.record_outcome(
        "run-1", "observer", execution, {"tests_passed": True, "summary": "clean"}
    )
    return proposal, verdict, authorization, execution, outcome


def test_complete_attested_lifecycle_is_valid(tmp_path):
    ledger = _ledger(tmp_path)
    _complete_run(ledger)

    result = ledger.validate("run-1")

    assert result.valid is True
    assert result.status == LedgerValidationStatus.VALID
    assert result.event_count == 5
    assert result.last_valid_sequence == 5


def test_outcome_requires_execution_receipt(tmp_path):
    ledger = _ledger(tmp_path)
    with pytest.raises(LedgerError, match="execution receipt"):
        ledger.record_outcome("run-1", "observer", object(), {"tests_passed": True})


def test_hold_cannot_become_execution_authorization(tmp_path):
    ledger = _ledger(tmp_path)
    proposal = ledger.record_proposal("run-1", "agent-a", {"proposal_id": "p"})
    verdict = ledger.record_gate_verdict("run-1", "gate", proposal, "hold", {})

    with pytest.raises(LedgerError, match="EXECUTE"):
        ledger.authorize_execution("run-1", "gate", verdict)


def test_tampering_is_detected_without_rewriting_the_artifact(tmp_path):
    ledger = _ledger(tmp_path)
    _complete_run(ledger)
    ledger._conn.execute(
        "UPDATE ledger_events SET payload_json=? WHERE sequence=3",
        (json.dumps({"gate_event_id": "forged", "proposal_id": "proposal-1"}),),
    )

    result = ledger.validate("run-1")

    assert result.valid is False
    assert result.status == LedgerValidationStatus.BAD_HASH


def test_nonce_reuse_is_rejected(tmp_path):
    ledger = _ledger(tmp_path)
    first = ledger.create_event(
        "run-1", LedgerEventType.PROPOSAL, "agent", {"proposal_id": "p1"}, nonce="fixed"
    )
    ledger.append(first)
    second = ledger.create_event(
        "run-1", LedgerEventType.REJECTION, "agent", {"reason": "retry"}, nonce="fixed"
    )

    with pytest.raises(LedgerError, match="duplicate"):
        ledger.append(second)


def test_event_serialization_is_stable(tmp_path):
    ledger = _ledger(tmp_path)
    event = ledger.record_proposal("run-1", "agent-a", {"proposal_id": "p"})

    encoded = json.dumps(event.to_dict(), sort_keys=True, separators=(",", ":"))
    assert encoded == json.dumps(event.to_dict(), sort_keys=True, separators=(",", ":"))
    assert event.event_hash == event.computed_hash()


def test_ed25519_public_verifier_is_independent_when_available():
    signer = Ed25519Signer.generate(key_id="research")
    verifier = Ed25519Verifier(signer.public_key_bytes(), key_id="research")
    signature = signer.sign(b"payload")
    assert verifier.verify(b"payload", signature)
    assert not verifier.verify(b"tampered", signature)


def test_rejection_and_error_are_terminal_evidence_events(tmp_path):
    ledger = _ledger(tmp_path)
    proposal = ledger.record_proposal("run-1", "agent-a", {"proposal_id": "p"})
    ledger.record_rejection("run-1", "gate", proposal, "risk pressure")
    ledger.record_error("run-1", "executor", proposal, "not executed")
    result = ledger.validate("run-1")
    assert result.valid
