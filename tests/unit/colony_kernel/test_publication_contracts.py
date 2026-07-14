"""Publication-readiness contracts exercised with production components."""

from __future__ import annotations

import importlib.util
from dataclasses import fields
from os import utime
from pathlib import Path

import pytest

from codomyrmex.colony_kernel.consequence_memory import ConsequenceMemory
from codomyrmex.colony_kernel.falsification.worker import (
    FalsificationWorker,
    proposal_to_falsification_plan,
)
from codomyrmex.colony_kernel.kernel import ColonyKernel
from codomyrmex.colony_kernel.models import (
    ActionProposal,
    AgentRole,
    AgentTrustProfile,
    ConsequenceRecord,
    FalsificationFinding,
    FalsificationSeverity,
    GateDecision,
    ResourceCost,
    SignalType,
    maximum_severity,
    recommendation_for_severity,
)
from codomyrmex.colony_kernel.resource_ledger import ResourceBudget, ResourceLedger
from codomyrmex.manuscript.variables import _parse_junit_status


def _artifact_freshness(artifacts: list[Path], source_files: list[Path], root: Path) -> dict[str, bool]:
    spec = importlib.util.spec_from_file_location(
        "release_manifest", Path("scripts/generate_release_manifest.py")
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module._artifact_freshness(artifacts, source_files, root)

pytestmark = pytest.mark.unit


def _proposal(
    *,
    agent_id: str = "publication-agent",
    target: str = "codomyrmex.publication.target",
    proposal_id: str | None = None,
    evidence: dict[str, object] | None = None,
) -> ActionProposal:
    values: dict[str, object] = {
        "agent_id": agent_id,
        "agent_type": "dispatcher",
        "action_type": "patch_file",
        "target": target,
        "rationale": "Apply one bounded correction with a measured rollback path.",
        "expected_outcome": "targeted tests pass and coverage remains stable",
        "rollback_plan": "revert the bounded correction",
        "evidence": evidence
        or {
            "tests": ["tests/unit/colony_kernel/test_publication_contracts.py"],
            "metrics": "coverage >= 60%",
            "scope": target,
            "dependencies": [],
        },
    }
    if proposal_id is not None:
        values["proposal_id"] = proposal_id
    return ActionProposal(**values)


def test_locality_control_and_decay_recovery_use_real_kernel() -> None:
    kernel = ColonyKernel()
    try:
        profile = AgentTrustProfile(
            agent_id="locality-reviewer",
            role=AgentRole.DISPATCHER,
            trust_score=0.50,
            total_proposals=3,
        )
        same = _proposal(agent_id=profile.agent_id)
        unrelated = _proposal(
            agent_id=profile.agent_id,
            target="codomyrmex.publication.unrelated",
        )
        before = kernel.actuation_gate.evaluate(same, profile, [], True)
        kernel.record_outcome(
            _proposal(agent_id="reporter", target=same.target),
            {"summary": "the targeted check failed"},
            tests_passed=False,
        )
        after = kernel.actuation_gate.evaluate(same, profile, [], True)
        control = kernel.actuation_gate.evaluate(unrelated, profile, [], True)
        assert before.decision == GateDecision.EXECUTE
        assert after.decision == GateDecision.HOLD
        assert after.gate_score < before.gate_score
        assert control.gate_score == pytest.approx(before.gate_score)

        for _ in range(20):
            kernel.tick()
        recovered = kernel.actuation_gate.evaluate(same, profile, [], True)
        assert recovered.gate_score == pytest.approx(before.gate_score)
    finally:
        kernel.consequence_memory.close()


def test_policy_rejection_and_falsification_never_create_failure() -> None:
    kernel = ColonyKernel()
    try:
        proposal = _proposal(agent_id="new-policy-agent")
        result = kernel.propose_action(proposal)
        assert result.decision == GateDecision.REFUSE
        assert kernel.pheromone_store.sense(proposal.target, SignalType.FAILURE) == 0.0
        assert (
            kernel.pheromone_store.sense(proposal.target, SignalType.POLICY_REJECTION)
            > 0.0
        )

        worker = FalsificationWorker(pheromone_store=kernel.pheromone_store)
        report = worker.evaluate_plan(
            {
                "action_type": "patch_file",
                "target": "codomyrmex.publication.falsification",
                "rationale": "Bounded patch with a measured test and rollback.",
                "expected_outcome": "targeted test passes",
                "rollback_plan": "revert patch",
                "tests": ["T-1"],
                "metrics": "coverage >= 60%",
                "scope": "codomyrmex.publication.falsification",
                "dependencies": [],
            }
        )
        assert report.findings
        assert kernel.pheromone_store.sense(
            "codomyrmex.publication.falsification", SignalType.RISK
        ) > 0.0
        assert kernel.pheromone_store.sense(
            "codomyrmex.publication.falsification", SignalType.FAILURE
        ) == 0.0
    finally:
        kernel.consequence_memory.close()


def test_typed_proposal_conversion_preserves_every_falsification_input() -> None:
    proposal = _proposal(
        evidence={
            "tests": ["T-1"],
            "metrics": "coverage >= 60%",
            "scope": "pkg.mod",
            "dependencies": ["stdlib"],
            "repo_root": ".",
            "supporting": "evidence",
        }
    )
    plan = proposal_to_falsification_plan(proposal)
    assert set(plan) == {
        "agent_id",
        "action_type",
        "target",
        "rationale",
        "expected_outcome",
        "rollback_plan",
        "tests",
        "metrics",
        "scope",
        "dependencies",
        "evidence",
        "budget_estimate",
        "repo_root",
    }
    assert plan["tests"] == ["T-1"]
    assert plan["metrics"] == "coverage >= 60%"
    assert plan["scope"] == "pkg.mod"
    assert plan["dependencies"] == ["stdlib"]


@pytest.mark.parametrize(
    ("field_name", "cost", "budget"),
    [
        ("llm_calls", ResourceCost(llm_calls=1), ResourceBudget(max_llm_calls=0)),
        (
            "runtime_seconds",
            ResourceCost(runtime_seconds=1.0),
            ResourceBudget(max_runtime_seconds=0.0),
        ),
        ("risk_level", ResourceCost(risk_level=1.0), ResourceBudget(max_risk_level=0.0)),
        (
            "human_attention_minutes",
            ResourceCost(human_attention_minutes=1.0),
            ResourceBudget(max_human_attention_minutes=0.0),
        ),
        ("merge_risk", ResourceCost(merge_risk=1.0), ResourceBudget(max_merge_risk=0.0)),
        ("doc_debt", ResourceCost(doc_debt=1.0), ResourceBudget(max_doc_debt=0.0)),
        (
            "security_exposure",
            ResourceCost(security_exposure=1.0),
            ResourceBudget(max_security_exposure=0.0),
        ),
    ],
)
def test_every_budget_dimension_is_enforced(
    field_name: str, cost: ResourceCost, budget: ResourceBudget
) -> None:
    assert field_name in {field.name for field in fields(ResourceCost)}
    affordable, reason = ResourceLedger(budget=budget).can_afford(cost)
    assert affordable is False
    assert field_name in (reason or "")


@pytest.mark.parametrize("db_path", [None, ":memory:"])
def test_trust_initialization_and_updates_match_backends(db_path: str | None) -> None:
    memory = ConsequenceMemory(db_path=db_path)
    try:
        before = memory.get_profile("backend-agent")
        assert before.trust_score == pytest.approx(0.1)
        memory.record(
            ConsequenceRecord(
                proposal=_proposal(agent_id="backend-agent"),
                action_taken="patch",
                actual_outcome="tests pass",
                tests_passed=True,
            )
        )
        assert memory.get_profile("backend-agent").trust_score == pytest.approx(0.14)
    finally:
        memory.close()


def test_outcome_grade_and_duplicate_reports_are_bounded() -> None:
    kernel = ColonyKernel()
    try:
        proposal = _proposal(proposal_id="stable-publication-lifecycle")
        first = kernel.record_outcome(proposal, {"summary": "reported"}, True)
        second = kernel.record_outcome(proposal, {"summary": "reported again"}, True)
        assert first.consequence_id == second.consequence_id
        assert first.evidence_grade == "caller_reported_unattested"
        assert kernel.agent_profile(proposal.agent_id).accepted_proposals == 1
    finally:
        kernel.consequence_memory.close()


def test_proposal_lifecycle_is_counted_once() -> None:
    kernel = ColonyKernel()
    try:
        proposal = _proposal(proposal_id="one-lifecycle")
        kernel.propose_action(proposal)
        kernel.propose_action(proposal)
        assert kernel.agent_profile(proposal.agent_id).total_proposals == 1
    finally:
        kernel.consequence_memory.close()


def test_mixed_severity_uses_numeric_maximum_and_unified_policy() -> None:
    findings = [
        FalsificationFinding("low", "low", FalsificationSeverity.LOW),
        FalsificationFinding("high", "high", FalsificationSeverity.HIGH),
        FalsificationFinding("critical", "critical", FalsificationSeverity.CRITICAL),
    ]
    strongest = maximum_severity(findings)
    assert strongest is FalsificationSeverity.CRITICAL
    assert recommendation_for_severity(strongest) == "refuse"


def test_junit_status_parser_separates_all_outcomes(tmp_path: Path) -> None:
    report = tmp_path / "junit.xml"
    report.write_text(
        """<testsuite tests=\"5\"><testcase name=\"p1\"/>\n"
        "<testcase name=\"p2\"><skipped/></testcase>\n"
        "<testcase name=\"f1\"><failure/></testcase>\n"
        "<testcase name=\"e1\"><error/></testcase>\n"
        "<testcase name=\"p3\"/></testsuite>""",
        encoding="utf-8",
    )
    assert _parse_junit_status(report) == {
        "collected": 5,
        "passed": 2,
        "skipped": 1,
        "failed": 1,
        "errors": 1,
    }


def test_junit_status_parser_rejects_stale_or_missing_artifact(tmp_path: Path) -> None:
    with pytest.raises(RuntimeError, match="missing"):
        _parse_junit_status(tmp_path / "stale.xml")


def test_release_manifest_rejects_stale_generated_artifact(tmp_path: Path) -> None:
    source = tmp_path / "source.md"
    artifact = tmp_path / "paper.pdf"
    source.write_text("source", encoding="utf-8")
    artifact.write_text("artifact", encoding="utf-8")
    artifact_mtime = source.stat().st_mtime_ns - 1_000_000
    utime(artifact, ns=(artifact_mtime, artifact_mtime))

    assert _artifact_freshness([artifact], [source], tmp_path) == {
        "paper.pdf": False
    }


def test_release_manifest_rejects_equal_mtime_as_fresh(tmp_path: Path) -> None:
    source = tmp_path / "source.md"
    artifact = tmp_path / "paper.pdf"
    source.write_text("source", encoding="utf-8")
    artifact.write_text("artifact", encoding="utf-8")
    source_mtime = source.stat().st_mtime_ns
    utime(artifact, ns=(source_mtime, source_mtime))

    assert _artifact_freshness([artifact], [source], tmp_path) == {
        "paper.pdf": False
    }
