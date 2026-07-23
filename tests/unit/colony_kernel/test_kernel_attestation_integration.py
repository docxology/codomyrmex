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

    with pytest.raises(ValueError, match="execution receipt"):
        kernel.record_outcome(_proposal(), {"summary": "reported"}, tests_passed=True)
