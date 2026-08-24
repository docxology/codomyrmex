"""Tests for the Colony Kernel external-actuation observation adapter (R2)."""

from __future__ import annotations

import pytest

from codomyrmex.colony_kernel.attestation import (
    AttestationLedger,
    HMACSigner,
)
from codomyrmex.colony_kernel.research.actuation_adapter import (
    ActuationObservationResult,
    ActuationStatus,
    ExternalActuationAdapter,
    ExternalExecutionWitness,
)


def test_successful_external_actuation_lifecycle(tmp_path) -> None:
    db_file = tmp_path / "attestation.db"
    signer = HMACSigner(secret_key=b"test_secret_key_16bytes_min")
    ledger = AttestationLedger(db_file, signer=signer)
    adapter = ExternalActuationAdapter(ledger, environment_id="test_env_1")

    proposal = {
        "proposal_id": "prop-001",
        "target": "src/codomyrmex/core.py",
        "action": "patch_file",
    }
    gate_metadata = {"score": 0.88, "decision": "execute"}

    def sample_executor() -> tuple[int, str, str]:
        return (0, "patch applied cleanly", "")

    result = adapter.observe_and_record(
        run_id="run-001",
        proposal_dict=proposal,
        gate_verdict="execute",
        gate_metadata=gate_metadata,
        executor_fn=sample_executor,
    )

    assert result.status == ActuationStatus.EXECUTED
    assert result.verified is True
    assert result.witness is not None
    assert result.witness.exit_code == 0
    assert result.witness.target == "src/codomyrmex/core.py"
    assert result.witness.action == "patch_file"
    assert result.authorization_event_id is not None
    assert result.error_reason is None


def test_failed_external_execution_witnessed_and_recorded(tmp_path) -> None:
    db_file = tmp_path / "attestation.db"
    signer = HMACSigner(secret_key=b"test_secret_key_16bytes_min")
    ledger = AttestationLedger(db_file, signer=signer)
    adapter = ExternalActuationAdapter(ledger, environment_id="test_env_2")

    proposal = {
        "proposal_id": "prop-002",
        "target": "src/codomyrmex/bad.py",
        "action": "delete_file",
    }

    def failing_executor() -> tuple[int, str, str]:
        return (1, "", "permission denied")

    result = adapter.observe_and_record(
        run_id="run-002",
        proposal_dict=proposal,
        gate_verdict="execute",
        gate_metadata={"score": 0.80},
        executor_fn=failing_executor,
    )

    assert result.status == ActuationStatus.FAILED
    assert result.verified is True
    assert result.witness is not None
    assert result.witness.exit_code == 1
    assert "Non-zero exit code: 1" in (result.error_reason or "")


def test_gate_refusal_prevents_actuation_execution(tmp_path) -> None:
    db_file = tmp_path / "attestation.db"
    signer = HMACSigner(secret_key=b"test_secret_key_16bytes_min")
    ledger = AttestationLedger(db_file, signer=signer)
    adapter = ExternalActuationAdapter(ledger)

    executed = False

    def executor_should_not_run() -> tuple[int, str, str]:
        nonlocal executed
        executed = True
        return (0, "ok", "")

    result = adapter.observe_and_record(
        run_id="run-003",
        proposal_dict={"proposal_id": "prop-003", "target": "sys/", "action": "rm"},
        gate_verdict="refuse",
        gate_metadata={"score": 0.20},
        executor_fn=executor_should_not_run,
    )

    assert result.status == ActuationStatus.REJECTED
    assert result.witness is None
    assert executed is False
    assert result.verified is True


def test_missing_proposal_id_is_generated_and_attested(tmp_path) -> None:
    ledger = AttestationLedger(
        tmp_path / "attestation.db",
        signer=HMACSigner(secret_key=b"test_secret_key_16bytes_min"),
    )
    adapter = ExternalActuationAdapter(ledger)

    result = adapter.observe_and_record(
        run_id="run-generated-id",
        proposal_dict={"target": "src/example.py", "action": "inspect"},
        gate_verdict="refuse",
        gate_metadata={"score": 0.1},
        executor_fn=lambda: (0, "", ""),
    )

    proposal_event = ledger.events("run-generated-id")[0]
    assert result.proposal_id
    assert proposal_event.payload["proposal_id"] == result.proposal_id
    assert result.verified is True
