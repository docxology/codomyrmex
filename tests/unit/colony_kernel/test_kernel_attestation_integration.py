from __future__ import annotations

import pytest

from codomyrmex.colony_kernel.kernel import ColonyKernel, ColonyKernelConfig
from codomyrmex.colony_kernel.models import ActionProposal


def _proposal() -> ActionProposal:
    return ActionProposal(
        agent_id="agent-a",
        agent_type="test",
        action_type="run_tests",
        target="tests/unit/example.py",
        rationale="verify the contract",
        expected_outcome="tests pass",
        rollback_plan="restore the previous state",
        evidence={"test": "tests/unit/example.py"},
    )


def test_optional_attestation_records_proposal_and_verdict_without_schema_change():
    kernel = ColonyKernel(
        ColonyKernelConfig(
            attestation_mode="optional",
            attestation_secret_key=b"0123456789abcdef0123456789abcdef",
        )
    )

    result = kernel.propose_action(_proposal())

    assert result.decision.value in {"execute", "hold", "refuse"}
    status = kernel.attestation_status()
    assert status is not None
    assert status.event_count == 2
    assert status.valid is True


def test_required_attestation_rejects_unlinked_caller_report():
    kernel = ColonyKernel(
        ColonyKernelConfig(
            attestation_mode="required",
            attestation_secret_key=b"0123456789abcdef0123456789abcdef",
        )
    )

    with pytest.raises(ValueError, match="record_attested_outcome"):
        kernel.record_outcome(_proposal(), {"summary": "reported"}, tests_passed=True)


def _prepare_attested_execution(kernel: ColonyKernel) -> ActionProposal:
    proposal = _proposal()
    profile = kernel.agent_profile(proposal.agent_id)
    profile.trust_score = 0.9
    profile.total_proposals = 10
    kernel.consequence_memory.save_profile(profile)
    result = kernel.propose_action(proposal)
    assert result.decision.value == "execute"
    kernel.authorize_execution(proposal.proposal_id, actor_id="gate")
    kernel.record_execution_receipt(
        proposal.proposal_id,
        {"executor": "sandbox-worker", "exit_code": 0},
    )
    return proposal


def test_required_attestation_rejects_direct_outcome_even_after_receipt():
    kernel = ColonyKernel(
        ColonyKernelConfig(
            attestation_mode="required",
            attestation_secret_key=b"0123456789abcdef0123456789abcdef",
        )
    )
    proposal = _prepare_attested_execution(kernel)

    with pytest.raises(ValueError, match="record_attested_outcome"):
        kernel.record_outcome(
            proposal,
            {"summary": "direct report"},
            tests_passed=True,
        )


def test_required_attestation_records_complete_linked_lifecycle():
    kernel = ColonyKernel(
        ColonyKernelConfig(
            attestation_mode="required",
            attestation_secret_key=b"0123456789abcdef0123456789abcdef",
        )
    )
    proposal = _prepare_attested_execution(kernel)

    record = kernel.record_attested_outcome(
        proposal,
        {"summary": "verified local receipt chain"},
        tests_passed=True,
    )

    assert record.proposal.proposal_id == proposal.proposal_id
    status = kernel.attestation_status()
    assert status is not None
    assert status.event_count == 5
    assert status.valid is True
