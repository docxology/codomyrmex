"""Real-component contracts for the strict Colony enforcement profile."""

from __future__ import annotations

import concurrent.futures
import multiprocessing
import time
from dataclasses import replace
from pathlib import Path
from typing import Any

import pytest
from cryptography.hazmat.primitives import serialization

from codomyrmex.colony_kernel import (
    ActionProposal,
    AgentRole,
    ColonyKernel,
    ColonyKernelConfig,
    Ed25519Authority,
    OutcomeEvidence,
)
from codomyrmex.colony_kernel.authorization import (
    AuthorizationError,
    AuthorizationLedger,
    canonical_json,
    deserialize_authorization,
    digest,
    serialize_authorization,
)
from codomyrmex.colony_kernel.models import (
    ColonySignal,
    DecayRate,
    GateDecision,
    ResourceCost,
    SignalSource,
    SignalType,
    SupervisedEvaluatorEvidence,
)
from codomyrmex.colony_kernel.pheromone_store import PheromoneStore
from codomyrmex.colony_kernel.resource_ledger import ResourceBudget, ResourceLedger


def _consume_authorization_process(
    db_path: str,
    token_json: str,
    raw_private_key: bytes,
    queue: Any,
) -> None:
    authority = Ed25519Authority.from_raw_private_bytes(raw_private_key)
    ledger = AuthorizationLedger(db_path, issuer=authority)
    token = deserialize_authorization(token_json)
    try:
        ledger.consume(
            token,
            agent_id=token.agent_id,
            action_type=token.action_type,
            target=token.target,
        )
    except AuthorizationError:
        queue.put(False)
    else:
        queue.put(True)
    finally:
        ledger.close()


def _proposal(*, target: str = "src/release_target.py", proposal_id: str = "p-1") -> ActionProposal:
    return ActionProposal(
        agent_id="release-agent",
        agent_type="contract-test",
        action_type="patch_file",
        target=target,
        rationale="contract test",
        expected_outcome="the declared change is applied",
        rollback_plan="restore the previous file content",
        evidence={"test": "release-contract"},
        proposal_id=proposal_id,
        budget_estimate=ResourceCost(llm_calls=1),
    )


def _strict_kernel(tmp_path: Path) -> ColonyKernel:
    key = Ed25519Authority.generate()
    kernel = ColonyKernel(
        ColonyKernelConfig(
            db_path=str(tmp_path / "kernel.sqlite"),
            enforcement_mode="strict",
            authorization_signer=key,
            executor_id="contract-executor",
            budget=ResourceBudget(max_llm_calls=10),
        )
    )
    profile = kernel.agent_profile("release-agent")
    profile.role = AgentRole.REPAIR_ANT
    profile.trust_score = 0.9
    profile.total_proposals = 3
    kernel.consequence_memory.save_profile(profile)
    return kernel


def test_signed_authorization_is_single_use_and_receipt_linked(tmp_path: Path) -> None:
    kernel = _strict_kernel(tmp_path)
    kernel.register_executor_handler(
        "patch_file", lambda target, payload: {"target": target, "changed": True}
    )
    proposal = _proposal()

    decision = kernel.propose_action(proposal)
    assert decision.decision is GateDecision.EXECUTE
    assert decision.authorization is not None

    run = kernel.execute_authorized(
        decision.authorization,
        agent_id=proposal.agent_id,
        action_type=proposal.action_type,
        target=proposal.target,
    )
    assert run.receipt.exit_code == 0
    record = kernel.record_attested_outcome(
        proposal,
        OutcomeEvidence(decision.authorization.authorization_id, run.receipt),
        {"summary": "changed"},
        True,
    )
    assert record.evidence_grade == "attested_execution"
    assert kernel.authorization_ledger is not None
    assert kernel.authorization_ledger.lifecycle_snapshot()["receipts"] == 1

    with pytest.raises(AuthorizationError, match="unknown or already consumed"):
        kernel.execute_authorized(
            decision.authorization,
            agent_id=proposal.agent_id,
            action_type=proposal.action_type,
            target=proposal.target,
        )
    kernel.close()


def test_unattested_report_is_quarantined_without_trust_or_failure_pressure(
    tmp_path: Path,
) -> None:
    kernel = _strict_kernel(tmp_path)
    proposal = _proposal(proposal_id="quarantined")
    before = kernel.agent_profile(proposal.agent_id).trust_score

    with pytest.raises(AuthorizationError, match="quarantined"):
        kernel.record_outcome(proposal, {"summary": "caller says passed"}, True)

    assert kernel.agent_profile(proposal.agent_id).trust_score == before
    assert kernel.consequence_memory.find_by_proposal_id(proposal.proposal_id) is None
    assert kernel.pheromone_store.sense(proposal.target, SignalType.FAILURE) == 0.0
    assert kernel.authorization_ledger is not None
    assert kernel.authorization_ledger.lifecycle_snapshot()["quarantined_reports"] == 1
    kernel.close()


def test_strict_scope_fails_closed_for_unregistered_target(tmp_path: Path) -> None:
    kernel = _strict_kernel(tmp_path)
    decision = kernel.propose_action(_proposal(target="README.md", proposal_id="outside"))
    assert decision.decision is GateDecision.REFUSE
    assert decision.authorization is None
    assert kernel.pheromone_store.sense("README.md", SignalType.FAILURE) == 0.0
    assert kernel.pheromone_store.sense("README.md", SignalType.POLICY_REJECTION) > 0.0
    kernel.close()


def test_scope_rejects_absolute_and_traversal_targets() -> None:
    from codomyrmex.colony_kernel.authorization import target_in_scope

    assert not target_in_scope("patch_file", "src/../README.md")
    assert not target_in_scope("patch_file", "/tmp/outside.py")
    assert target_in_scope("patch_file", "src/declared.py")


def test_tampered_cross_agent_and_expired_authorizations_are_rejected(
    tmp_path: Path,
) -> None:
    key = Ed25519Authority.generate()
    ledger = AuthorizationLedger(
        str(tmp_path / "authorization-edge.sqlite"), issuer=key, ttl_seconds=0.01
    )
    proposal = _proposal(proposal_id="edge")
    from codomyrmex.colony_kernel.models import GateResult

    token = ledger.issue(
        proposal,
        GateResult(GateDecision.EXECUTE, 1.0, "test", budget_approved=True),
    )
    tampered = replace(token, target="src/other.py")
    with pytest.raises(AuthorizationError, match="signature is invalid"):
        ledger.consume(
            tampered,
            agent_id=proposal.agent_id,
            action_type=proposal.action_type,
            target="src/other.py",
        )
    with pytest.raises(AuthorizationError, match="does not match executor"):
        ledger.consume(
            token,
            agent_id="other-agent",
            action_type=proposal.action_type,
            target=proposal.target,
        )
    time.sleep(0.02)
    with pytest.raises(AuthorizationError, match="expired"):
        ledger.consume(
            token,
            agent_id=proposal.agent_id,
            action_type=proposal.action_type,
            target=proposal.target,
        )
    ledger.close()


def test_supervised_evaluator_path_is_signed_and_read_only(tmp_path: Path) -> None:
    kernel = _strict_kernel(tmp_path)
    proposal = _proposal(proposal_id="supervised")
    evaluator = kernel._config.authorization_signer
    assert evaluator is not None
    payload = {
        "agent_id": proposal.agent_id,
        "proposal_id": proposal.proposal_id,
        "evaluator_id": "supervisor",
        "evaluator_key_id": evaluator.key_id,
        "assessment_digest": digest(proposal),
        "read_only": True,
    }
    evidence = SupervisedEvaluatorEvidence(
        agent_id=proposal.agent_id,
        proposal_id=proposal.proposal_id,
        evaluator_id="supervisor",
        evaluator_key_id=evaluator.key_id,
        assessment_digest=digest(proposal),
        signature=evaluator.sign(canonical_json(payload)),
    )
    result = kernel.supervised_read_only_evaluate(proposal, evidence)
    assert result.authorization is None
    assert kernel.authorization_ledger is not None
    assert kernel.authorization_ledger.lifecycle_snapshot().get("proposals", 0) == 0
    kernel.close()


def test_durable_signal_and_budget_state_survive_restart(tmp_path: Path) -> None:
    signal_db = tmp_path / "signals.sqlite"
    signal_store = PheromoneStore(db_path=str(signal_db))
    signal_store.deposit_signal(
        ColonySignal(
            location="src/persisted.py",
            signal_type=SignalType.RISK,
            strength=2.0,
            decay_rate=DecayRate.SLOW,
            source=SignalSource.TEST,
        )
    )
    signal_store.close()
    reopened_store = PheromoneStore(db_path=str(signal_db))
    assert reopened_store.sense("src/persisted.py", SignalType.RISK) == 2.0
    reopened_store.close()

    budget_db = tmp_path / "budget.sqlite"
    ledger = ResourceLedger(
        ResourceBudget(max_llm_calls=2), db_path=str(budget_db)
    )
    assert ledger.check_and_consume(ResourceCost(llm_calls=1), agent_id="worker") == (
        True,
        "consumed",
    )
    ledger.close()
    reopened_ledger = ResourceLedger(
        ResourceBudget(max_llm_calls=2), db_path=str(budget_db)
    )
    assert reopened_ledger.current_usage().llm_calls == 1
    assert reopened_ledger.check_budget(ResourceCost(llm_calls=2))[0] is False
    reopened_ledger.close()


def test_durable_budget_claim_is_atomic_across_threads(tmp_path: Path) -> None:
    ledger_path = str(tmp_path / "concurrent-budget.sqlite")
    budget = ResourceBudget(max_llm_calls=1)

    def claim() -> tuple[bool, str]:
        ledger = ResourceLedger(budget, db_path=ledger_path)
        result = ledger.check_and_consume(ResourceCost(llm_calls=1), agent_id="worker")
        ledger.close()
        return result

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: claim(), range(2)))
    assert sum(result[0] for result in results) == 1


def test_authorization_consumption_is_atomic_across_processes(tmp_path: Path) -> None:
    key = Ed25519Authority.generate()
    ledger_path = str(tmp_path / "authorization.sqlite")
    from codomyrmex.colony_kernel.models import GateResult

    ledger = AuthorizationLedger(ledger_path, issuer=key)
    proposal = _proposal(proposal_id="process-race")
    token = ledger.issue(
        proposal,
        GateResult(GateDecision.EXECUTE, 1.0, "test", budget_approved=True),
    )
    raw_key = key._private_key.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption(),
    )
    queue: Any = multiprocessing.get_context("fork").Queue()
    processes = [
        multiprocessing.get_context("fork").Process(
            target=_consume_authorization_process,
            args=(ledger_path, serialize_authorization(token), raw_key, queue),
        )
        for _ in range(2)
    ]
    for process in processes:
        process.start()
    for process in processes:
        process.join(timeout=10)
    results = [queue.get(timeout=2) for _ in processes]
    assert sum(results) == 1
    ledger.close()
