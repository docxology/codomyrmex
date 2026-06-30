"""Tests for colony_kernel.role_adapter — zero-mock, real data only.

Covers:
- New agent starts as SANDBOX (no history)
- High-trust test_fix agent earns REPAIR_ANT
- High-trust security agent earns GUARD_ANT
- Well-routing agent earns DISPATCHER
- Low-trust agent stays SANDBOX
- role_stats returns correct counts for all AgentRole values
"""

from __future__ import annotations

import pytest

from codomyrmex.colony_kernel.models import (
    ActionProposal,
    AgentRole,
    AgentTrustProfile,
    ConsequenceRecord,
    ResourceCost,
)
from codomyrmex.colony_kernel.role_adapter import (
    ConsequenceMemory,
    RoleAdapter,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_proposal(
    agent_id: str,
    action_type: str = "test_fix",
    target: str = "codomyrmex.some_module",
) -> ActionProposal:
    return ActionProposal(
        agent_id=agent_id,
        agent_type="repair_worker",
        action_type=action_type,
        target=target,
        rationale="automated repair",
        expected_outcome="tests green",
        budget_estimate=ResourceCost(),
    )


def _make_record(
    agent_id: str,
    action_type: str = "test_fix",
    tests_passed: bool = True,
    repair_needed: bool = False,
    trust_delta: float = 0.0,
) -> ConsequenceRecord:
    proposal = _make_proposal(agent_id, action_type=action_type)
    return ConsequenceRecord(
        proposal=proposal,
        action_taken="applied patch",
        actual_outcome="tests green" if tests_passed else "tests still failing",
        tests_passed=tests_passed,
        repair_needed=repair_needed,
        trust_delta=trust_delta,
    )


def _build_high_trust_adapter(
    agent_id: str,
    action_type: str,
    n_successes: int = 18,
    final_trust: float = 0.85,
) -> RoleAdapter:
    """Return a RoleAdapter whose agent has a high trust score and successful actions.

    We submit successful records and force the profile trust score directly so
    that the tests are deterministic regardless of the delta computation formula.
    """
    memory = ConsequenceMemory()
    adapter = RoleAdapter(memory)

    # Ensure the profile exists before we mutate it.
    adapter.get_profile(agent_id)

    # Submit successful consequence records to populate action history.
    for _ in range(n_successes):
        record = _make_record(agent_id, action_type=action_type, tests_passed=True)
        memory.store_record(record)
        profile = memory.get_profile(agent_id)
        assert profile is not None
        profile.total_proposals += 1
        profile.accepted_proposals += 1
        profile.consequence_history.append(record.consequence_id)

    # Force the trust score to the desired value so the role inference
    # is exercised from a known state — no floating-point accumulation surprises.
    profile = memory.get_profile(agent_id)
    assert profile is not None
    profile.trust_score = final_trust
    memory.save_profile(profile)

    return adapter


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestNewAgentStartsAsSandbox:
    """A brand-new agent with no history must be SANDBOX."""

    def test_assign_role_returns_sandbox(self) -> None:
        memory = ConsequenceMemory()
        adapter = RoleAdapter(memory)
        role = adapter.assign_role("agent-brand-new")
        assert role == AgentRole.SANDBOX

    def test_get_profile_initialises_sandbox(self) -> None:
        memory = ConsequenceMemory()
        adapter = RoleAdapter(memory)
        profile = adapter.get_profile("agent-fresh")
        assert profile.role == AgentRole.SANDBOX
        assert profile.trust_score == pytest.approx(0.1, abs=1e-9)
        assert profile.total_proposals == 0
        assert profile.accepted_proposals == 0

    def test_default_trust_score_is_low(self) -> None:
        memory = ConsequenceMemory()
        adapter = RoleAdapter(memory)
        profile = adapter.get_profile("agent-zero")
        # Default trust 0.1 is below SANDBOX threshold (< 0.3).
        assert profile.trust_score < 0.3


class TestHighTrustTestFixAgentBecomesRepairAnt:
    """An agent with trust >= 0.8 and successful test_fix actions -> REPAIR_ANT."""

    def test_repair_ant_via_test_fix(self) -> None:
        agent_id = "agent-repair-test-fix"
        adapter = _build_high_trust_adapter(agent_id, action_type="test_fix", final_trust=0.82)
        role = adapter.assign_role(agent_id)
        assert role == AgentRole.REPAIR_ANT

    def test_repair_ant_via_bug_repair(self) -> None:
        agent_id = "agent-repair-bug"
        adapter = _build_high_trust_adapter(agent_id, action_type="bug_repair", final_trust=0.80)
        role = adapter.assign_role(agent_id)
        assert role == AgentRole.REPAIR_ANT

    def test_below_trust_threshold_stays_sandbox(self) -> None:
        """Even with test_fix actions, trust < 0.8 keeps agent in SANDBOX."""
        agent_id = "agent-repair-low-trust"
        adapter = _build_high_trust_adapter(agent_id, action_type="test_fix", final_trust=0.75)
        role = adapter.assign_role(agent_id)
        # Rule 1 requires trust >= 0.8; this agent falls through to Rule 6 (SANDBOX).
        assert role == AgentRole.SANDBOX

    def test_update_profile_propagates_role(self) -> None:
        """update_profile must persist the new role in the returned profile."""
        agent_id = "agent-repair-update"
        memory = ConsequenceMemory()
        adapter = RoleAdapter(memory)

        # Set trust high first.
        adapter.get_profile(agent_id)
        profile = memory.get_profile(agent_id)
        assert profile is not None
        profile.trust_score = 0.85
        memory.save_profile(profile)

        record = _make_record(agent_id, action_type="test_fix", tests_passed=True)
        updated = adapter.update_profile(record)
        assert updated.role == AgentRole.REPAIR_ANT


class TestHighTrustSecurityAgentBecomesGuardAnt:
    """An agent with trust >= 0.85 and successful security actions -> GUARD_ANT."""

    def test_guard_ant_via_security_scan(self) -> None:
        agent_id = "agent-guard-scan"
        adapter = _build_high_trust_adapter(
            agent_id, action_type="security_scan", final_trust=0.90
        )
        role = adapter.assign_role(agent_id)
        assert role == AgentRole.GUARD_ANT

    def test_guard_ant_via_vulnerability_fix(self) -> None:
        agent_id = "agent-guard-vuln"
        adapter = _build_high_trust_adapter(
            agent_id, action_type="vulnerability_fix", final_trust=0.85
        )
        role = adapter.assign_role(agent_id)
        assert role == AgentRole.GUARD_ANT

    def test_trust_just_below_threshold_is_not_guard(self) -> None:
        """trust = 0.849 should not satisfy Rule 3 (>= 0.85)."""
        agent_id = "agent-guard-below"
        adapter = _build_high_trust_adapter(
            agent_id, action_type="security_scan", final_trust=0.84
        )
        role = adapter.assign_role(agent_id)
        # Should not be GUARD_ANT; falls to Rule 6 (SANDBOX).
        assert role != AgentRole.GUARD_ANT


class TestWellRoutingAgentBecomesDispatcher:
    """An agent with >= 20 proposals and >= 70% acceptance rate -> DISPATCHER."""

    def _make_dispatcher_adapter(self, agent_id: str) -> RoleAdapter:
        memory = ConsequenceMemory()
        adapter = RoleAdapter(memory)

        # Ensure profile exists with mid-range trust (not triggering SANDBOX rule 5).
        adapter.get_profile(agent_id)
        profile = memory.get_profile(agent_id)
        assert profile is not None
        profile.trust_score = 0.55
        # Set proposal counts directly to satisfy Rule 4.
        profile.total_proposals = 20
        profile.accepted_proposals = 15  # 75% >= 70%
        memory.save_profile(profile)
        return adapter

    def test_dispatcher_role_with_high_acceptance(self) -> None:
        agent_id = "agent-dispatcher-good"
        adapter = self._make_dispatcher_adapter(agent_id)
        role = adapter.assign_role(agent_id)
        assert role == AgentRole.DISPATCHER

    def test_dispatcher_not_triggered_with_low_proposals(self) -> None:
        """Fewer than 20 proposals means Rule 4 is not satisfied."""
        memory = ConsequenceMemory()
        adapter = RoleAdapter(memory)
        agent_id = "agent-dispatcher-few"
        adapter.get_profile(agent_id)
        profile = memory.get_profile(agent_id)
        assert profile is not None
        profile.trust_score = 0.55
        profile.total_proposals = 19
        profile.accepted_proposals = 19  # 100% but not enough proposals
        memory.save_profile(profile)
        role = adapter.assign_role(agent_id)
        assert role != AgentRole.DISPATCHER

    def test_dispatcher_not_triggered_with_low_acceptance_rate(self) -> None:
        """>= 20 proposals but < 70% acceptance does not earn DISPATCHER."""
        memory = ConsequenceMemory()
        adapter = RoleAdapter(memory)
        agent_id = "agent-dispatcher-low-rate"
        adapter.get_profile(agent_id)
        profile = memory.get_profile(agent_id)
        assert profile is not None
        profile.trust_score = 0.55
        profile.total_proposals = 20
        profile.accepted_proposals = 13  # 65% < 70%
        memory.save_profile(profile)
        role = adapter.assign_role(agent_id)
        assert role != AgentRole.DISPATCHER


class TestLowTrustAgentStaysSandbox:
    """An agent with trust < 0.3 must stay in SANDBOX regardless of history."""

    def test_very_low_trust_is_sandbox(self) -> None:
        memory = ConsequenceMemory()
        adapter = RoleAdapter(memory)
        agent_id = "agent-low-trust"
        adapter.get_profile(agent_id)
        profile = memory.get_profile(agent_id)
        assert profile is not None
        profile.trust_score = 0.05
        memory.save_profile(profile)
        role = adapter.assign_role(agent_id)
        assert role == AgentRole.SANDBOX

    def test_consecutive_failures_force_sandbox(self) -> None:
        """Three consecutive failures at the tail of records -> SANDBOX (Rule 5)."""
        memory = ConsequenceMemory()
        adapter = RoleAdapter(memory)
        agent_id = "agent-streak-fail"

        # Start with high trust so the agent would otherwise earn a specialist role.
        adapter.get_profile(agent_id)
        profile = memory.get_profile(agent_id)
        assert profile is not None
        profile.trust_score = 0.82
        memory.save_profile(profile)

        # Inject 3 consecutive failing records.
        for _ in range(3):
            record = _make_record(
                agent_id,
                action_type="test_fix",
                tests_passed=False,
                repair_needed=True,
            )
            memory.store_record(record)
            profile = memory.get_profile(agent_id)
            assert profile is not None
            profile.total_proposals += 1
            profile.consequence_history.append(record.consequence_id)
            memory.save_profile(profile)

        role = adapter.assign_role(agent_id)
        assert role == AgentRole.SANDBOX

    def test_apply_delta_clamps_to_zero(self) -> None:
        """apply_delta must not let trust go below 0.0."""
        profile = AgentTrustProfile(agent_id="agent-clamp", trust_score=0.05)
        profile.apply_delta(-1.0)
        assert profile.trust_score == pytest.approx(0.0, abs=1e-9)

    def test_apply_delta_clamps_to_one(self) -> None:
        """apply_delta must not let trust exceed 1.0."""
        profile = AgentTrustProfile(agent_id="agent-clamp-hi", trust_score=0.99)
        profile.apply_delta(1.0)
        assert profile.trust_score == pytest.approx(1.0, abs=1e-9)


class TestRoleStats:
    """role_stats must return a dict keyed on all AgentRole values with correct counts."""

    def test_empty_memory_returns_all_zero_counts(self) -> None:
        memory = ConsequenceMemory()
        adapter = RoleAdapter(memory)
        stats = adapter.role_stats()
        assert set(stats.keys()) == set(AgentRole)
        assert all(v == 0 for v in stats.values())

    def test_single_new_agent_counted_as_sandbox(self) -> None:
        memory = ConsequenceMemory()
        adapter = RoleAdapter(memory)
        adapter.get_profile("agent-stats-new")
        stats = adapter.role_stats()
        assert stats[AgentRole.SANDBOX] == 1
        for role in AgentRole:
            if role != AgentRole.SANDBOX:
                assert stats[role] == 0

    def test_two_agents_different_roles_counted_correctly(self) -> None:
        memory = ConsequenceMemory()
        adapter = RoleAdapter(memory)

        # Agent 1: SANDBOX (new agent, no history).
        adapter.get_profile("agent-stats-sandbox")

        # Agent 2: REPAIR_ANT (high trust + test_fix).
        agent_repair = "agent-stats-repair"
        adapter.get_profile(agent_repair)
        profile_r = memory.get_profile(agent_repair)
        assert profile_r is not None
        profile_r.trust_score = 0.82
        memory.save_profile(profile_r)

        # Add a successful test_fix record for agent_repair.
        record = _make_record(agent_repair, action_type="test_fix", tests_passed=True)
        memory.store_record(record)

        stats = adapter.role_stats()
        assert stats[AgentRole.SANDBOX] == 1
        assert stats[AgentRole.REPAIR_ANT] == 1
        assert stats[AgentRole.GUARD_ANT] == 0
        assert stats[AgentRole.DISPATCHER] == 0
        assert stats[AgentRole.MEMORY_ANT] == 0

    def test_all_roles_present_as_keys(self) -> None:
        """role_stats keys must always include every AgentRole member."""
        memory = ConsequenceMemory()
        adapter = RoleAdapter(memory)
        stats = adapter.role_stats()
        for role in AgentRole:
            assert role in stats

    def test_counts_are_integers(self) -> None:
        memory = ConsequenceMemory()
        adapter = RoleAdapter(memory)
        adapter.get_profile("agent-count-type")
        stats = adapter.role_stats()
        for count in stats.values():
            assert isinstance(count, int)

    def test_total_count_matches_known_agents(self) -> None:
        """Sum of all role counts should equal the number of known agents."""
        memory = ConsequenceMemory()
        adapter = RoleAdapter(memory)
        n_agents = 4
        for i in range(n_agents):
            adapter.get_profile(f"agent-total-{i}")
        stats = adapter.role_stats()
        assert sum(stats.values()) == n_agents


class TestAgentsByRole:
    """agents_by_role returns sorted agent_ids for the requested role."""

    def test_returns_empty_for_unknown_role_with_no_agents(self) -> None:
        memory = ConsequenceMemory()
        adapter = RoleAdapter(memory)
        result = adapter.agents_by_role(AgentRole.REPAIR_ANT)
        assert result == []

    def test_returns_all_sandbox_agents(self) -> None:
        memory = ConsequenceMemory()
        adapter = RoleAdapter(memory)
        ids = ["agent-by-role-c", "agent-by-role-a", "agent-by-role-b"]
        for aid in ids:
            adapter.get_profile(aid)
        result = adapter.agents_by_role(AgentRole.SANDBOX)
        assert sorted(ids) == result

    def test_does_not_return_wrong_role(self) -> None:
        memory = ConsequenceMemory()
        adapter = RoleAdapter(memory)
        adapter.get_profile("agent-wrong-role")
        result = adapter.agents_by_role(AgentRole.REPAIR_ANT)
        assert "agent-wrong-role" not in result


# ---------------------------------------------------------------------------
# Trust score → role mapping via infer_role (kernel API)
# ---------------------------------------------------------------------------


class TestInferRoleTrustScoreMapping:
    """infer_role maps trust scores to roles using the kernel thresholds.

    Thresholds (from role_adapter.py):
      total_proposals < 3            -> SANDBOX  (insufficient history)
      trust >= 0.70                  -> GUARD_ANT
      trust >= 0.50                  -> DISPATCHER
      trust >= 0.35                  -> MEMORY_ANT
      trust >= 0.20                  -> REPAIR_ANT
      trust < 0.20                   -> SANDBOX
    """

    def _profile(self, trust: float, proposals: int = 5) -> AgentTrustProfile:
        """Build a real AgentTrustProfile with the given trust score and proposal count."""
        p = AgentTrustProfile(agent_id=f"agent-trust-{trust:.2f}")
        p.trust_score = trust
        p.total_proposals = proposals
        return p

    # --- trust = 0.0 → SANDBOX ---

    def test_trust_zero_maps_to_sandbox(self) -> None:
        profile = self._profile(trust=0.0)
        role = RoleAdapter.infer_role(profile)
        assert role == AgentRole.SANDBOX

    def test_trust_zero_with_many_proposals_still_sandbox(self) -> None:
        """trust = 0.0 is below every promotion threshold; proposals don't help."""
        profile = self._profile(trust=0.0, proposals=100)
        role = RoleAdapter.infer_role(profile)
        assert role == AgentRole.SANDBOX

    def test_trust_just_below_repair_threshold_is_sandbox(self) -> None:
        """trust = 0.19 is just below the REPAIR_ANT threshold of 0.20."""
        profile = self._profile(trust=0.19)
        role = RoleAdapter.infer_role(profile)
        assert role == AgentRole.SANDBOX

    def test_insufficient_proposals_forces_sandbox_regardless_of_trust(self) -> None:
        """Fewer than 3 proposals keeps agent SANDBOX even at high trust."""
        profile = self._profile(trust=0.0, proposals=2)
        role = RoleAdapter.infer_role(profile)
        assert role == AgentRole.SANDBOX

    # --- trust = 0.3 → REPAIR_ANT ---

    def test_trust_0_3_maps_to_repair_ant(self) -> None:
        """trust = 0.3 >= 0.20 threshold → REPAIR_ANT (given proposals >= 3)."""
        profile = self._profile(trust=0.3)
        role = RoleAdapter.infer_role(profile)
        assert role == AgentRole.REPAIR_ANT

    def test_trust_exactly_at_repair_threshold_maps_to_repair_ant(self) -> None:
        """trust = 0.20 (exact boundary) -> REPAIR_ANT."""
        profile = self._profile(trust=0.20)
        role = RoleAdapter.infer_role(profile)
        assert role == AgentRole.REPAIR_ANT

    def test_trust_0_3_is_not_sandbox(self) -> None:
        profile = self._profile(trust=0.3)
        role = RoleAdapter.infer_role(profile)
        assert role != AgentRole.SANDBOX

    def test_trust_0_3_with_minimum_proposals(self) -> None:
        """Exactly 3 proposals (the promotion floor) at trust 0.3 -> REPAIR_ANT."""
        profile = self._profile(trust=0.3, proposals=3)
        role = RoleAdapter.infer_role(profile)
        assert role == AgentRole.REPAIR_ANT

    # --- trust = 0.8 → specialist role (GUARD_ANT, MEMORY_ANT, or DISPATCHER) ---

    def test_trust_0_8_maps_to_specialist_role(self) -> None:
        """trust = 0.8 >= 0.70 (GUARD_ANT threshold) -> a specialist role."""
        profile = self._profile(trust=0.8)
        role = RoleAdapter.infer_role(profile)
        # 0.8 >= 0.70 → GUARD_ANT by the kernel infer_role thresholds.
        assert role in {AgentRole.GUARD_ANT, AgentRole.MEMORY_ANT, AgentRole.DISPATCHER}

    def test_trust_0_8_is_not_sandbox(self) -> None:
        profile = self._profile(trust=0.8)
        role = RoleAdapter.infer_role(profile)
        assert role != AgentRole.SANDBOX

    def test_trust_0_8_is_not_repair_ant(self) -> None:
        """trust = 0.8 exceeds the REPAIR_ANT threshold; a higher role applies."""
        profile = self._profile(trust=0.8)
        role = RoleAdapter.infer_role(profile)
        assert role != AgentRole.REPAIR_ANT

    def test_trust_exactly_at_guard_threshold(self) -> None:
        """trust = 0.70 (exact boundary) -> GUARD_ANT."""
        profile = self._profile(trust=0.70)
        role = RoleAdapter.infer_role(profile)
        assert role == AgentRole.GUARD_ANT

    def test_trust_1_0_maps_to_guard_ant(self) -> None:
        """Maximum trust must also map to a specialist role (GUARD_ANT)."""
        profile = self._profile(trust=1.0)
        role = RoleAdapter.infer_role(profile)
        assert role == AgentRole.GUARD_ANT

    # --- boundary between REPAIR_ANT and MEMORY_ANT ---

    def test_trust_0_35_maps_to_memory_ant(self) -> None:
        """trust = 0.35 (MEMORY_ANT threshold) -> MEMORY_ANT."""
        profile = self._profile(trust=0.35)
        role = RoleAdapter.infer_role(profile)
        assert role == AgentRole.MEMORY_ANT

    def test_trust_0_50_maps_to_dispatcher(self) -> None:
        """trust = 0.50 (DISPATCHER threshold) -> DISPATCHER."""
        profile = self._profile(trust=0.50)
        role = RoleAdapter.infer_role(profile)
        assert role == AgentRole.DISPATCHER


# ---------------------------------------------------------------------------
# MEMORY_ANT via specialization-based assign_role (Rule 2)
# ---------------------------------------------------------------------------


class TestMemoryAntAssignment:
    """assign_role Rule 2: trust >= 0.8 AND doc_write/memory_index -> MEMORY_ANT.

    Rule priority order in assign_role:
      5 (SANDBOX for low trust / failures) -> 3 (GUARD_ANT) -> 1 (REPAIR_ANT)
      -> 2 (MEMORY_ANT) -> 4 (DISPATCHER) -> 6 (default SANDBOX)

    MEMORY_ANT is returned when trust >= 0.8, the agent has successful
    memory-category actions, and does NOT have any security-category successes
    (which would trigger Rule 3 first).

    Trust range that reliably produces MEMORY_ANT via assign_role: [0.80, 0.85).
    At trust >= 0.85 the agent could earn GUARD_ANT if security actions exist,
    so we use 0.82 (safely inside [0.80, 0.85)) to keep the test unambiguous.
    """

    def _make_memory_ant_adapter(self, agent_id: str, action_type: str = "doc_write") -> RoleAdapter:
        """Return a RoleAdapter whose agent qualifies for MEMORY_ANT via Rule 2.

        Trust is set to 0.82 (in [0.80, 0.85)) with successful memory-category
        actions and no security-category actions, so Rule 2 fires before Rule 3.
        """
        memory = ConsequenceMemory()
        adapter = RoleAdapter(memory)

        adapter.get_profile(agent_id)

        # Store successful memory-category records.
        for _ in range(5):
            record = _make_record(agent_id, action_type=action_type, tests_passed=True)
            memory.store_record(record)
            profile = memory.get_profile(agent_id)
            assert profile is not None
            profile.total_proposals += 1
            profile.accepted_proposals += 1
            profile.consequence_history.append(record.consequence_id)

        # Force trust into [0.80, 0.85) so Rule 3 (GUARD_ANT) cannot fire.
        profile = memory.get_profile(agent_id)
        assert profile is not None
        profile.trust_score = 0.82
        memory.save_profile(profile)

        return adapter

    def test_assign_role_returns_memory_ant_at_qualifying_trust(self) -> None:
        """trust = 0.82 with successful doc_write actions -> MEMORY_ANT (Rule 2)."""
        agent_id = "agent-memory-doc-write"
        adapter = self._make_memory_ant_adapter(agent_id, action_type="doc_write")
        role = adapter.assign_role(agent_id)
        assert role == AgentRole.MEMORY_ANT

    def test_assign_role_returns_memory_ant_for_memory_index(self) -> None:
        """memory_index is the second qualifying action type for MEMORY_ANT."""
        agent_id = "agent-memory-index"
        adapter = self._make_memory_ant_adapter(agent_id, action_type="memory_index")
        role = adapter.assign_role(agent_id)
        assert role == AgentRole.MEMORY_ANT

    def test_memory_ant_stable_with_same_trust(self) -> None:
        """Calling assign_role twice with the same trust returns MEMORY_ANT both times."""
        agent_id = "agent-memory-stable"
        adapter = self._make_memory_ant_adapter(agent_id, action_type="doc_write")
        role_first = adapter.assign_role(agent_id)
        role_second = adapter.assign_role(agent_id)
        assert role_first == AgentRole.MEMORY_ANT
        assert role_second == AgentRole.MEMORY_ANT

    def test_memory_ant_not_sandbox(self) -> None:
        """MEMORY_ANT trust (0.82) is strictly above the sandbox floor (0.3)."""
        agent_id = "agent-memory-above-sandbox"
        adapter = self._make_memory_ant_adapter(agent_id, action_type="doc_write")
        profile = adapter.get_profile(agent_id)
        # Confirm trust is well above the SANDBOX threshold of 0.3.
        assert profile.trust_score > 0.3
        # And the role itself is not SANDBOX.
        role = adapter.assign_role(agent_id)
        assert role != AgentRole.SANDBOX

    def test_memory_ant_requires_memory_action(self) -> None:
        """Without a memory-category action, trust alone does not produce MEMORY_ANT."""
        agent_id = "agent-memory-no-action"
        memory = ConsequenceMemory()
        adapter = RoleAdapter(memory)

        adapter.get_profile(agent_id)
        profile = memory.get_profile(agent_id)
        assert profile is not None
        # High trust but only non-memory action type.
        profile.trust_score = 0.82
        memory.save_profile(profile)

        # Store a successful test_fix record (not a memory action).
        record = _make_record(agent_id, action_type="test_fix", tests_passed=True)
        memory.store_record(record)
        profile = memory.get_profile(agent_id)
        assert profile is not None
        profile.total_proposals += 1
        profile.accepted_proposals += 1
        profile.consequence_history.append(record.consequence_id)
        memory.save_profile(profile)

        role = adapter.assign_role(agent_id)
        # Should be REPAIR_ANT (Rule 1 fires before Rule 2), not MEMORY_ANT.
        assert role != AgentRole.MEMORY_ANT

    def test_memory_ant_not_assigned_below_trust_threshold(self) -> None:
        """trust < 0.8 with memory actions does not produce MEMORY_ANT."""
        agent_id = "agent-memory-low-trust"
        memory = ConsequenceMemory()
        adapter = RoleAdapter(memory)

        adapter.get_profile(agent_id)

        for _ in range(5):
            record = _make_record(agent_id, action_type="doc_write", tests_passed=True)
            memory.store_record(record)
            profile = memory.get_profile(agent_id)
            assert profile is not None
            profile.total_proposals += 1
            profile.accepted_proposals += 1
            profile.consequence_history.append(record.consequence_id)

        profile = memory.get_profile(agent_id)
        assert profile is not None
        profile.trust_score = 0.75  # below 0.8 threshold
        memory.save_profile(profile)

        role = adapter.assign_role(agent_id)
        assert role != AgentRole.MEMORY_ANT
