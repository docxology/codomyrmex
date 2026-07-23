"""Deterministic replay for the implemented paired-locality contract.

This module is deliberately narrower than a benchmark runner.  It replays the
checked-in caller-reported failure fixture with real Colony Kernel subsystems,
fixed proposal identities, and no wall-clock values in the semantic output.
The result is suitable for manuscript generation and for an independent,
machine-readable regression check.  It does not attest that the reported
outcome came from an executed action.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from codomyrmex.colony_kernel.kernel import ColonyKernel, ColonyKernelConfig
from codomyrmex.colony_kernel.models import (
    ActionProposal,
    AgentRole,
    AgentTrustProfile,
    GateResult,
    SignalType,
)
from codomyrmex.colony_kernel.role_adapter import RoleAdapter

REPLAY_SCHEMA_VERSION = "1.0"


def _proposal(
    *,
    agent_id: str,
    target: str,
    proposal_id: str,
    rationale: str,
    expected_outcome: str,
) -> ActionProposal:
    """Build a proposal with stable identity and timestamps for replay."""
    return ActionProposal(
        agent_id=agent_id,
        agent_type="dispatcher",
        action_type="patch_file",
        target=target,
        rationale=rationale,
        expected_outcome=expected_outcome,
        rollback_plan="revert the bounded paired fixture",
        evidence={"fixture": "paired-locality", "test": "contract"},
        proposal_id=proposal_id,
        created_at=0.0,
    )


def _result_payload(result: GateResult) -> dict[str, Any]:
    """Project a GateResult onto deterministic, public semantic fields."""
    return {
        "decision": result.decision.value,
        "gate_score": round(float(result.gate_score), 12),
        "budget_approved": bool(result.budget_approved),
        "falsification_severity": round(float(result.falsification_severity), 12),
        "required_evidence": list(result.required_evidence),
        "reason": result.reason,
    }


def _run_once(*, agent_trust: float, recovery_ticks: int) -> dict[str, Any]:
    """Execute one semantic replay without serialising volatile kernel state."""
    kernel = ColonyKernel(config=ColonyKernelConfig(db_path=":memory:"))
    try:
        agent_id = "replay-independent-reviewer"
        target = "codomyrmex.manuscript.paired_target"
        unrelated_target = "codomyrmex.manuscript.unrelated_target"
        profile = AgentTrustProfile(
            agent_id=agent_id,
            trust_score=agent_trust,
            total_proposals=3,
        )
        profile.role = RoleAdapter.infer_role(profile)
        if profile.role is AgentRole.SANDBOX:
            raise RuntimeError("Replay fixture requires a non-sandbox profile")

        same_target = _proposal(
            agent_id=agent_id,
            target=target,
            proposal_id="replay-same-target",
            rationale="Apply a bounded correction with a verified rollback path.",
            expected_outcome="targeted tests pass",
        )
        unrelated = _proposal(
            agent_id=agent_id,
            target=unrelated_target,
            proposal_id="replay-unrelated-target",
            rationale="Apply an independent bounded correction.",
            expected_outcome="independent tests pass",
        )
        reported = _proposal(
            agent_id="replay-outcome-reporter",
            target=target,
            proposal_id="replay-reported-failure",
            rationale="Record the fixture's caller-reported failed outcome.",
            expected_outcome="targeted tests fail",
        )

        before = kernel.actuation_gate.evaluate(same_target, profile, [], True)
        pressure_before = {
            "risk": round(kernel.pheromone_store.sense(target, SignalType.RISK), 12),
            "failure": round(
                kernel.pheromone_store.sense(target, SignalType.FAILURE), 12
            ),
        }
        kernel.record_outcome(
            reported,
            outcome={"summary": "targeted tests failed"},
            tests_passed=False,
        )
        after = kernel.actuation_gate.evaluate(same_target, profile, [], True)
        unaffected = kernel.actuation_gate.evaluate(unrelated, profile, [], True)
        pressure_unrelated = {
            "risk": round(
                kernel.pheromone_store.sense(unrelated_target, SignalType.RISK), 12
            ),
            "failure": round(
                kernel.pheromone_store.sense(unrelated_target, SignalType.FAILURE), 12
            ),
        }
        pressure_after = {
            "risk": round(kernel.pheromone_store.sense(target, SignalType.RISK), 12),
            "failure": round(
                kernel.pheromone_store.sense(target, SignalType.FAILURE), 12
            ),
        }

        for _ in range(recovery_ticks):
            kernel.tick()
        recovered = kernel.actuation_gate.evaluate(same_target, profile, [], True)
        pressure_recovered = {
            "risk": round(kernel.pheromone_store.sense(target, SignalType.RISK), 12),
            "failure": round(
                kernel.pheromone_store.sense(target, SignalType.FAILURE), 12
            ),
        }
        return {
            "profile": {
                "agent_id": profile.agent_id,
                "trust_score": round(float(profile.trust_score), 12),
                "role": profile.role.value,
                "total_proposals": profile.total_proposals,
            },
            "targets": {"same": target, "unrelated": unrelated_target},
            "results": {
                "before_failure": _result_payload(before),
                "after_failure_same_target": _result_payload(after),
                "after_failure_unrelated_target": _result_payload(unaffected),
                "after_recovery": _result_payload(recovered),
            },
            "pressure": {
                "before_failure": pressure_before,
                "after_failure_same_target": pressure_after,
                "after_failure_unrelated_target": pressure_unrelated,
                "after_recovery": pressure_recovered,
            },
            "recovery_ticks": recovery_ticks,
        }
    finally:
        kernel.consequence_memory.close()


def _canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def run_paired_locality_replay(
    *, agent_trust: float, recovery_ticks: int, seed: int = 0
) -> dict[str, Any]:
    """Return a repeatable, hashed replay record for the local contract.

    ``seed`` is recorded as an explicit protocol input even though this fixture
    uses no random draws.  That makes future stochastic extensions fail closed
    if they omit the declared seed from their artifact.
    """
    if not 0.0 <= agent_trust <= 1.0:
        raise ValueError("agent_trust must be in [0.0, 1.0]")
    if recovery_ticks < 0:
        raise ValueError("recovery_ticks must be non-negative")

    first = _run_once(agent_trust=agent_trust, recovery_ticks=recovery_ticks)
    repeat = _run_once(agent_trust=agent_trust, recovery_ticks=recovery_ticks)
    first_json = _canonical_json(first)
    repeat_json = _canonical_json(repeat)
    before = first["results"]["before_failure"]
    after = first["results"]["after_failure_same_target"]
    unrelated = first["results"]["after_failure_unrelated_target"]
    recovered = first["results"]["after_recovery"]
    assertions = {
        "repeatable_semantics": first_json == repeat_json,
        "same_target_score_decreases": after["gate_score"] < before["gate_score"],
        "same_target_decision_tightens": (
            before["decision"] == "execute" and after["decision"] == "hold"
        ),
        "unrelated_target_unchanged": unrelated == before,
        "recovery_restores_decision": recovered == before,
        "reported_outcome_is_explicitly_unattested": True,
    }
    record: dict[str, Any] = {
        "schema_version": REPLAY_SCHEMA_VERSION,
        "seed": seed,
        "inputs": {
            "agent_trust": round(agent_trust, 12),
            "recovery_ticks": recovery_ticks,
            "randomness": "none; seed reserved for protocol compatibility",
        },
        "runs": {"first": first, "repeat": repeat},
        "assertions": assertions,
        "semantic_digest": hashlib.sha256(first_json.encode("utf-8")).hexdigest(),
    }
    artifact_json = _canonical_json(record)
    record["record_sha256"] = hashlib.sha256(artifact_json.encode("utf-8")).hexdigest()
    return record


def write_replay_artifact(path: Path, record: dict[str, Any]) -> str:
    """Write a replay record atomically and return its byte-level SHA-256."""
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(record, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(payload, encoding="utf-8")
    temporary.replace(path)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


__all__ = [
    "REPLAY_SCHEMA_VERSION",
    "run_paired_locality_replay",
    "write_replay_artifact",
]
