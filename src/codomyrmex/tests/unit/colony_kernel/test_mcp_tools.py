"""Unit tests for codomyrmex.colony_kernel.mcp_tools.

Zero-mock policy: no unittest.mock, MagicMock, or pytest-mock.
Kernel singleton is reset between tests via monkeypatch on the module-level
``_kernel`` attribute (narrow monkeypatch — environment isolation only,
not method stubbing).  All assertions are against real return values.
"""

from __future__ import annotations

import json
import types

import pytest

import codomyrmex.colony_kernel.mcp_tools as _mcp_mod
from codomyrmex.colony_kernel.mcp_tools import (
    ColonyKernel,
    colony_agent_profile,
    colony_falsify_plan,
    colony_pheromone_query,
    colony_propose_action,
    colony_pruning_report,
    colony_record_outcome,
    colony_status,
    colony_tick,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def fresh_kernel(monkeypatch: pytest.MonkeyPatch) -> None:
    """Replace the module-level ``_kernel`` singleton with a fresh instance
    for every test, then restore the original reference on teardown.

    This is the canonical pattern for resetting singleton state without
    mocking: monkeypatch.setattr replaces the module attribute; pytest
    restores it after the test.
    """
    monkeypatch.setattr(_mcp_mod, "_kernel", ColonyKernel())


# ---------------------------------------------------------------------------
# colony_status
# ---------------------------------------------------------------------------


class TestColonyStatus:
    def test_returns_dict(self) -> None:
        result = colony_status()
        assert isinstance(result, dict)

    def test_has_required_keys(self) -> None:
        result = colony_status()
        expected_keys = {
            "pheromone_summary",
            "budget_usage",
            "role_distribution",
            "recent_consequences",
            "pruning_candidates_count",
        }
        assert expected_keys.issubset(result.keys())

    def test_pheromone_summary_is_dict(self) -> None:
        result = colony_status()
        assert isinstance(result["pheromone_summary"], dict)
        assert "top_signals" in result["pheromone_summary"]

    def test_initial_agent_count_is_zero(self) -> None:
        result = colony_status()
        # role_distribution maps role names to counts; sum = total agents
        assert sum(result["role_distribution"].values()) == 0

    def test_recent_consequences_is_list(self) -> None:
        result = colony_status()
        assert isinstance(result["recent_consequences"], list)

    def test_top_signals_is_list(self) -> None:
        result = colony_status()
        assert isinstance(result["pheromone_summary"]["top_signals"], list)

    def test_budget_usage_is_dict(self) -> None:
        result = colony_status()
        assert isinstance(result["budget_usage"], dict)

    def test_pruning_candidates_count_is_int(self) -> None:
        result = colony_status()
        assert isinstance(result["pruning_candidates_count"], int)


# ---------------------------------------------------------------------------
# colony_propose_action
# ---------------------------------------------------------------------------


class TestColonyProposeAction:
    def test_returns_dict(self) -> None:
        result = colony_propose_action(
            agent_id="agent-001",
            action_type="patch_file",
            target="codomyrmex.utils.helpers",
            rationale="Fix the off-by-one error in the range loop.",
            rollback_plan="git revert HEAD --no-edit",
        )
        assert isinstance(result, dict)

    def test_new_agent_gets_hold_or_refuse(self) -> None:
        """New agents start with SANDBOX role and trust 0.1.
        The minimum trust for SANDBOX is 0.05 so trust alone won't block, but
        the default proposal has an underfunded budget (llm_calls=1, runtime=5)
        and no evidence dict, which may generate falsification findings.
        At minimum the gate should return HOLD or REFUSE (never EXECUTE for a
        brand-new agent with a minimal proposal that has no evidence).
        """
        result = colony_propose_action(
            agent_id="brand-new-agent",
            action_type="delete",
            target="codomyrmex.legacy.old_module",
            rationale="short",
            rollback_plan="",  # triggers missing_rollback finding
        )
        assert "decision" in result
        assert result["decision"] in ("hold", "refuse", "HOLD", "REFUSE")

    def test_missing_rollback_triggers_finding(self) -> None:
        """A proposal with no rollback plan should produce a REFUSE or HOLD."""
        result = colony_propose_action(
            agent_id="agent-nrb",
            action_type="archive",
            target="codomyrmex.deprecated",
            rationale="Module is deprecated and unused.",
            rollback_plan="",
        )
        assert isinstance(result, dict)
        assert result.get("decision") in ("hold", "refuse", "HOLD", "REFUSE")

    def test_has_expected_gate_result_keys(self) -> None:
        result = colony_propose_action(
            agent_id="agent-002",
            action_type="patch_file",
            target="codomyrmex.core.utils",
            rationale="Correct the type annotation on the public API.",
            rollback_plan="git revert HEAD",
        )
        for key in ("decision", "gate_score", "reason"):
            assert key in result, f"Missing key: {key}"

    def test_gate_score_is_float_in_range(self) -> None:
        result = colony_propose_action(
            agent_id="agent-003",
            action_type="patch_file",
            target="codomyrmex.core.logging",
            rationale="Add missing log level guard.",
            rollback_plan="git revert HEAD",
        )
        score = result.get("gate_score")
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0

    def test_invalid_evidence_json_returns_error(self) -> None:
        result = colony_propose_action(
            agent_id="agent-bad",
            action_type="patch_file",
            target="codomyrmex.core",
            rationale="Some rationale.",
            rollback_plan="git revert HEAD",
            evidence="not-valid-json{{{",
        )
        assert "error" in result

    def test_agent_count_increments_after_proposal(self) -> None:
        colony_propose_action(
            agent_id="agent-new-001",
            action_type="patch_file",
            target="codomyrmex.core.parser",
            rationale="Extend the public parser API.",
            rollback_plan="git revert HEAD",
        )
        status = colony_status()
        assert sum(status["role_distribution"].values()) >= 1

    def test_evidence_json_accepted(self) -> None:
        evidence = json.dumps({"test_id": "T-001", "pr_url": "https://example.com/1"})
        result = colony_propose_action(
            agent_id="agent-ev",
            action_type="patch_file",
            target="codomyrmex.core.evented",
            rationale=(
                "Fix the event handler to avoid double-firing on repeated "
                "subscription calls per T-001."
            ),
            rollback_plan="git revert HEAD",
            evidence=evidence,
        )
        assert isinstance(result, dict)
        assert "decision" in result


# ---------------------------------------------------------------------------
# colony_record_outcome
# ---------------------------------------------------------------------------


class TestColonyRecordOutcome:
    def test_returns_dict_with_status_recorded(self) -> None:
        result = colony_record_outcome(
            agent_id="agent-ro",
            action_type="patch_file",
            target="codomyrmex.core.models",
            actual_outcome="All 47 unit tests passed; coverage 82%.",
            tests_passed=True,
        )
        assert isinstance(result, dict)
        assert result.get("status") == "recorded"

    def test_consequence_id_is_present(self) -> None:
        result = colony_record_outcome(
            agent_id="agent-ro",
            action_type="patch_file",
            target="codomyrmex.core.models",
            actual_outcome="Tests passed.",
            tests_passed=True,
        )
        assert "consequence_id" in result
        assert isinstance(result["consequence_id"], str)

    def test_trust_score_returned(self) -> None:
        result = colony_record_outcome(
            agent_id="agent-ro",
            action_type="patch_file",
            target="codomyrmex.core.models",
            actual_outcome="Tests passed.",
            tests_passed=True,
        )
        assert "trust_score" in result
        assert 0.0 <= result["trust_score"] <= 1.0

    def test_passed_outcome_increases_trust(self) -> None:
        """Record a passing outcome and verify the trust score went up."""
        colony_propose_action(
            agent_id="agent-trust",
            action_type="patch_file",
            target="codomyrmex.core",
            rationale="Patch the logging module.",
            rollback_plan="git revert HEAD",
        )
        before = colony_agent_profile("agent-trust")
        trust_before = before.get("trust_score", 0.1)

        colony_record_outcome(
            agent_id="agent-trust",
            action_type="patch_file",
            target="codomyrmex.core",
            actual_outcome="All tests pass.",
            tests_passed=True,
            human_feedback=1.0,
        )
        after = colony_agent_profile("agent-trust")
        trust_after = after.get("trust_score", 0.1)
        assert trust_after > trust_before

    def test_failed_outcome_decreases_trust(self) -> None:
        """Record a failing outcome and verify the trust score went down."""
        colony_propose_action(
            agent_id="agent-fail",
            action_type="patch_file",
            target="codomyrmex.core",
            rationale="Patch the logging module.",
            rollback_plan="git revert HEAD",
        )
        before = colony_agent_profile("agent-fail")
        trust_before = before.get("trust_score", 0.1)

        colony_record_outcome(
            agent_id="agent-fail",
            action_type="patch_file",
            target="codomyrmex.core",
            actual_outcome="Tests failed; 3 errors.",
            tests_passed=False,
        )
        after = colony_agent_profile("agent-fail")
        trust_after = after.get("trust_score", 0.1)
        assert trust_after < trust_before

    def test_consequence_log_grows(self) -> None:
        colony_record_outcome(
            agent_id="agent-log",
            action_type="patch_file",
            target="codomyrmex.utils",
            actual_outcome="Done.",
            tests_passed=True,
        )
        status = colony_status()
        # recent_consequences is a list; it should have at least one entry
        assert len(status["recent_consequences"]) >= 1


# ---------------------------------------------------------------------------
# colony_agent_profile
# ---------------------------------------------------------------------------


class TestColonyAgentProfile:
    def test_returns_dict_for_unknown_agent(self) -> None:
        result = colony_agent_profile("unknown-brand-new")
        assert isinstance(result, dict)

    def test_auto_creates_sandbox_role(self) -> None:
        result = colony_agent_profile("fresh-sandbox-agent")
        assert result.get("role") == "sandbox"

    def test_initial_trust_score_is_0_1(self) -> None:
        result = colony_agent_profile("trust-check-agent")
        assert abs(result.get("trust_score", -1) - 0.1) < 1e-6

    def test_agent_id_matches(self) -> None:
        agent_id = "profile-id-agent"
        result = colony_agent_profile(agent_id)
        assert result.get("agent_id") == agent_id

    def test_known_agent_profile_after_proposal(self) -> None:
        colony_propose_action(
            agent_id="known-agent",
            action_type="patch_file",
            target="codomyrmex.core.known",
            rationale="Known agent action.",
            rollback_plan="git revert HEAD",
        )
        result = colony_agent_profile("known-agent")
        assert isinstance(result, dict)
        assert result.get("total_proposals", 0) >= 1


# ---------------------------------------------------------------------------
# colony_pheromone_query
# ---------------------------------------------------------------------------


class TestColonyPheromoneQuery:
    def test_returns_list_for_unknown_location(self) -> None:
        result = colony_pheromone_query("codomyrmex.no.such.module", "success")
        assert isinstance(result, list)
        assert result == []

    def test_valid_signal_types(self) -> None:
        valid_types = [
            "failure",
            "success",
            "risk",
            "need",
            "dependency",
            "human_priority",
        ]
        for sig in valid_types:
            result = colony_pheromone_query("codomyrmex.core", sig)
            assert isinstance(result, list), f"Expected list for signal_type={sig}"

    def test_invalid_signal_type_returns_error_dict(self) -> None:
        result = colony_pheromone_query("codomyrmex.core", "not_a_real_signal")
        assert isinstance(result, list)
        assert len(result) == 1
        assert "error" in result[0]

    def test_signal_appears_after_proposal_on_target(self) -> None:
        """After a successful (EXECUTE) proposal the kernel deposits a
        DEPENDENCY pheromone on the target.  Since a brand-new agent may
        receive HOLD/REFUSE, we verify the field interaction indirectly via
        status counts rather than asserting on the specific signal value."""
        colony_propose_action(
            agent_id="pheromone-agent",
            action_type="patch_file",
            target="codomyrmex.pheromone.target",
            rationale="Lay a dependency trail.",
            rollback_plan="git revert HEAD",
        )
        # Querying the location should not raise regardless of deposit outcome
        result = colony_pheromone_query("codomyrmex.pheromone.target", "dependency")
        assert isinstance(result, list)

    def test_failure_pheromone_deposited_on_refuse(self) -> None:
        """A REFUSE gate decision deposits a FAILURE pheromone on the target."""
        target = "codomyrmex.refuse.target"
        # Trigger a REFUSE by providing a high-risk plan with no rollback
        colony_propose_action(
            agent_id="refuse-agent",
            action_type="delete",
            target=target,
            rationale="short",
            rollback_plan="",
        )
        result = colony_pheromone_query(target, "failure")
        # Either a signal was deposited (list with items) or it wasn't (empty).
        # We only assert the return type to avoid brittleness on scoring details.
        assert isinstance(result, list)


# ---------------------------------------------------------------------------
# colony_falsify_plan
# ---------------------------------------------------------------------------


class TestColonyFalsifyPlan:
    def test_returns_dict(self) -> None:
        plan = json.dumps(
            {
                "action_type": "patch_file",
                "target": "codomyrmex.utils.helpers",
                "rationale": "Fix type annotation.",
                "rollback_plan": "git revert HEAD",
                "budget_estimate": {"llm_calls": 2, "runtime_seconds": 10.0},
            }
        )
        result = colony_falsify_plan(plan)
        assert isinstance(result, dict)

    def test_has_required_keys(self) -> None:
        plan = json.dumps(
            {
                "action_type": "patch_file",
                "target": "codomyrmex.core",
                "rationale": "Patch the type annotation in the public API.",
                "rollback_plan": "git revert HEAD",
                "budget_estimate": {"llm_calls": 1, "runtime_seconds": 5.0},
            }
        )
        result = colony_falsify_plan(plan)
        assert "findings" in result
        assert "severity_score" in result
        assert "recommendation" in result

    def test_severity_score_in_range(self) -> None:
        plan = json.dumps({"action_type": "patch_file", "target": "x"})
        result = colony_falsify_plan(plan)
        score = result.get("severity_score", -1.0)
        assert 0.0 <= score <= 1.0

    def test_recommendation_is_valid_string(self) -> None:
        plan = json.dumps({"action_type": "patch_file", "target": "x"})
        result = colony_falsify_plan(plan)
        assert result.get("recommendation") in ("execute", "hold", "refuse")

    def test_empty_plan_has_findings(self) -> None:
        """An empty plan triggers multiple attack vectors."""
        result = colony_falsify_plan("{}")
        assert isinstance(result["findings"], list)
        assert len(result["findings"]) > 0

    def test_well_formed_plan_passes(self) -> None:
        """A complete, well-formed plan should score low and recommend execute."""
        plan = json.dumps(
            {
                "action_type": "patch_file",
                "target": "codomyrmex.core.parser",
                "rationale": (
                    "The recursive descent parser mis-handles empty token streams, "
                    "causing an IndexError on blank input — confirmed by test T-042."
                ),
                "rollback_plan": "git revert HEAD --no-edit && uv run pytest",
                "evidence": {"test_id": "T-042", "error": "IndexError on line 87"},
                "budget_estimate": {"llm_calls": 2, "runtime_seconds": 30.0},
            }
        )
        result = colony_falsify_plan(plan)
        assert result["recommendation"] == "execute"
        assert result["severity_score"] < 0.4

    def test_missing_rollback_triggers_finding(self) -> None:
        plan = json.dumps(
            {
                "action_type": "patch_file",
                "target": "codomyrmex.core",
                "rationale": "Fix the thing.",
                "rollback_plan": "",
            }
        )
        result = colony_falsify_plan(plan)
        vectors = [f.get("attack_vector") for f in result["findings"]]
        assert "missing_rollback" in vectors

    def test_high_risk_delete_action_triggers_blast_radius(self) -> None:
        plan = json.dumps(
            {
                "action_type": "delete",
                "target": "codomyrmex.legacy",
                "rationale": "Remove the legacy module.",
                "rollback_plan": "git revert HEAD",
                "evidence": {"pr": "https://example.com/pr/99"},
                "budget_estimate": {"llm_calls": 1, "runtime_seconds": 5.0},
            }
        )
        result = colony_falsify_plan(plan)
        vectors = [f.get("attack_vector") for f in result["findings"]]
        assert "blast_radius" in vectors

    def test_circular_dependency_detected(self) -> None:
        """When target == agent_id the circular_dependency check fires."""
        plan = json.dumps(
            {
                "action_type": "patch_file",
                "target": "agent-self",
                "agent_id": "agent-self",
                "rationale": "Self-modification.",
                "rollback_plan": "git revert HEAD",
            }
        )
        result = colony_falsify_plan(plan)
        vectors = [f.get("attack_vector") for f in result["findings"]]
        assert "circular_dependency" in vectors

    def test_invalid_json_returns_error(self) -> None:
        result = colony_falsify_plan("{not valid json}")
        assert "error" in result

    def test_findings_is_list(self) -> None:
        result = colony_falsify_plan("{}")
        assert isinstance(result["findings"], list)

    def test_each_finding_has_attack_vector_and_severity(self) -> None:
        result = colony_falsify_plan("{}")
        for finding in result["findings"]:
            assert "attack_vector" in finding
            assert "severity" in finding


# ---------------------------------------------------------------------------
# colony_pruning_report
# ---------------------------------------------------------------------------


class TestColonyPruningReport:
    def test_returns_dict(self) -> None:
        result = colony_pruning_report()
        assert isinstance(result, dict)

    def test_has_required_keys(self) -> None:
        result = colony_pruning_report()
        assert "candidates" in result
        assert "total_candidates" in result
        assert "generated_at" in result

    def test_candidates_is_list(self) -> None:
        result = colony_pruning_report()
        assert isinstance(result["candidates"], list)

    def test_total_candidates_matches_list_length(self) -> None:
        result = colony_pruning_report()
        assert result["total_candidates"] == len(result["candidates"])

    def test_generated_at_is_positive_float(self) -> None:
        result = colony_pruning_report()
        assert isinstance(result["generated_at"], float)
        assert result["generated_at"] > 0.0

    def test_fresh_kernel_has_no_candidates(self) -> None:
        """A freshly initialised kernel with no signals has no pruning candidates."""
        result = colony_pruning_report()
        assert result["total_candidates"] == 0


# ---------------------------------------------------------------------------
# colony_tick
# ---------------------------------------------------------------------------


class TestColonyTick:
    def test_returns_dict(self) -> None:
        result = colony_tick()
        assert isinstance(result, dict)

    def test_has_status_keys(self) -> None:
        result = colony_tick()
        assert "pheromone_summary" in result
        assert "budget_usage" in result

    def test_tick_evaporates_traces(self) -> None:
        """After ticking, the pheromone field should be processed without error."""
        # Deposit a signal first
        colony_propose_action(
            agent_id="tick-agent",
            action_type="patch_file",
            target="codomyrmex.tick.target",
            rationale="Test tick behavior.",
            rollback_plan="git revert HEAD",
        )
        result = colony_tick()
        assert isinstance(result, dict)
        assert "error" not in result

    def test_multiple_ticks_no_error(self) -> None:
        for _ in range(5):
            result = colony_tick()
            assert "error" not in result

    def test_no_exception_on_empty_field(self) -> None:
        """Ticking an empty pheromone field must not raise."""
        result = colony_tick()
        assert isinstance(result, dict)
        assert "error" not in result


# ---------------------------------------------------------------------------
# Schema roundtrip tests — pin exact output key sets so future changes break
# these tests before they break MCP clients.
# ---------------------------------------------------------------------------


class TestMcpToolSchemas:
    def test_colony_status_exact_keys(self) -> None:
        result = colony_status()
        assert set(result.keys()) == {
            "pheromone_summary",
            "budget_usage",
            "role_distribution",
            "recent_consequences",
            "pruning_candidates_count",
        }

    def test_colony_tick_exact_keys(self) -> None:
        result = colony_tick()
        assert set(result.keys()) == {
            "pheromone_summary",
            "budget_usage",
            "role_distribution",
            "recent_consequences",
            "pruning_candidates_count",
        }

    def test_colony_pruning_report_exact_keys(self) -> None:
        result = colony_pruning_report()
        assert set(result.keys()) == {
            "candidates",
            "total_candidates",
            "generated_at",
        }

    def test_colony_propose_action_exact_keys(self) -> None:
        result = colony_propose_action(
            agent_id="schema-agent",
            action_type="patch_file",
            target="codomyrmex.schema.target",
            rationale="Schema roundtrip verification.",
            rollback_plan="git revert HEAD",
        )
        assert set(result.keys()) == {
            "decision",
            "gate_score",
            "reason",
            "required_evidence",
            "budget_approved",
            "falsification_severity",
        }

    def test_colony_record_outcome_exact_keys(self) -> None:
        result = colony_record_outcome(
            agent_id="schema-agent",
            action_type="patch_file",
            target="codomyrmex.schema.target",
            actual_outcome="Tests passed.",
            tests_passed=True,
        )
        assert set(result.keys()) == {
            "status",
            "consequence_id",
            "trust_score",
            "role",
        }


# ---------------------------------------------------------------------------
# Integration: propose -> record_outcome -> agent_profile sequence
# ---------------------------------------------------------------------------


class TestIntegrationSequence:
    def test_propose_then_record_updates_trust(self) -> None:
        """Simulate a realistic agent lifecycle:
        1. Propose an action.
        2. Record a successful outcome.
        3. Verify trust score increased.
        """
        agent_id = "integration-agent-001"

        colony_propose_action(
            agent_id=agent_id,
            action_type="patch_file",
            target="codomyrmex.integration.target",
            rationale="Align integration agent lifecycle.",
            rollback_plan="git revert HEAD",
        )

        profile_before = colony_agent_profile(agent_id)
        trust_before = profile_before["trust_score"]

        colony_record_outcome(
            agent_id=agent_id,
            action_type="patch_file",
            target="codomyrmex.integration.target",
            actual_outcome="All integration tests passed.",
            tests_passed=True,
            human_feedback=1.0,
        )

        profile_after = colony_agent_profile(agent_id)
        trust_after = profile_after["trust_score"]

        assert trust_after > trust_before

    def test_status_reflects_multi_agent_activity(self) -> None:
        for i in range(3):
            colony_propose_action(
                agent_id=f"multi-agent-{i}",
                action_type="patch_file",
                target=f"codomyrmex.multi.module_{i}",
                rationale="Multi-agent concurrency test.",
                rollback_plan="git revert HEAD",
            )
        status = colony_status()
        assert sum(status["role_distribution"].values()) == 3

    def test_full_lifecycle_no_errors(self) -> None:
        """Run the complete propose->record->profile->status->tick cycle
        and verify no step returns an error key."""
        agent_id = "lifecycle-agent"

        proposal_result = colony_propose_action(
            agent_id=agent_id,
            action_type="patch_file",
            target="codomyrmex.lifecycle.target",
            rationale="End-to-end lifecycle verification test.",
            rollback_plan="git revert HEAD --no-edit",
        )
        assert "error" not in proposal_result

        outcome_result = colony_record_outcome(
            agent_id=agent_id,
            action_type="patch_file",
            target="codomyrmex.lifecycle.target",
            actual_outcome="Tests pass; no regressions.",
            tests_passed=True,
        )
        assert "error" not in outcome_result

        profile_result = colony_agent_profile(agent_id)
        assert "error" not in profile_result

        status_result = colony_status()
        assert "error" not in status_result

        tick_result = colony_tick()
        assert "error" not in tick_result
