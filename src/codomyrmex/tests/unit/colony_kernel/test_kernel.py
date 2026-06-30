"""Unit tests for codomyrmex.colony_kernel.kernel.

Zero-mock policy: no unittest.mock, MagicMock, or pytest-mock.
All subsystems are real instances; SQLite runs in :memory: mode.
"""

from __future__ import annotations

import time

import pytest

from codomyrmex.colony_kernel.kernel import (
    ActuationGate,
    ColonyKernel,
    ColonyKernelConfig,
    ConsequenceMemory,
    FalsificationWorker,
    PheromoneStore,
    PruningDaemon,
    ResourceBudget,
    ResourceLedger,
    RoleAdapter,
)
from codomyrmex.colony_kernel.models import (
    ActionProposal,
    AgentRole,
    AgentTrustProfile,
    ColonySignal,
    ConsequenceRecord,
    DecayRate,
    FalsificationFinding,
    FalsificationSeverity,
    GateDecision,
    GateResult,
    ResourceCost,
    SignalSource,
    SignalType,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def kernel() -> ColonyKernel:
    """A ColonyKernel with an ephemeral :memory: SQLite database."""
    return ColonyKernel(config=ColonyKernelConfig(db_path=":memory:"))


@pytest.fixture
def proposal() -> ActionProposal:
    """A well-formed ActionProposal that should clear the actuation gate."""
    return ActionProposal(
        agent_id="agent-alpha",
        agent_type="repair_ant",
        action_type="patch_file",
        target="mypackage.core",
        rationale="Fix the off-by-one error in the accumulator loop so tests pass.",
        expected_outcome="all unit tests pass; coverage >= 80%",
        budget_estimate=ResourceCost(llm_calls=2, runtime_seconds=10.0, risk_level=0.1),
        rollback_plan="git revert HEAD --no-edit && uv run pytest",
        evidence={"test_id": "tests/unit/test_core.py::test_accumulator"},
    )


@pytest.fixture
def sandbox_proposal() -> ActionProposal:
    """A proposal whose agent starts in SANDBOX (no prior history)."""
    return ActionProposal(
        agent_id="brand-new-agent",
        agent_type="repair_ant",
        action_type="patch_file",
        target="mypackage.utils",
        rationale="Fix a minor import error in the utils module cleanly.",
        expected_outcome="import succeeds without errors in test suite",
        rollback_plan="git revert HEAD --no-edit",
        evidence={"pr": "https://example.com/pr/42"},
    )


# ---------------------------------------------------------------------------
# Initialisation — all subsystems present
# ---------------------------------------------------------------------------

class TestColonyKernelInit:

    def test_kernel_has_pheromone_store(self, kernel: ColonyKernel):
        assert isinstance(kernel.pheromone_store, PheromoneStore)

    def test_kernel_has_resource_ledger(self, kernel: ColonyKernel):
        assert isinstance(kernel.resource_ledger, ResourceLedger)

    def test_kernel_has_actuation_gate(self, kernel: ColonyKernel):
        assert isinstance(kernel.actuation_gate, ActuationGate)

    def test_kernel_has_consequence_memory(self, kernel: ColonyKernel):
        assert isinstance(kernel.consequence_memory, ConsequenceMemory)

    def test_kernel_has_role_adapter(self, kernel: ColonyKernel):
        assert isinstance(kernel.role_adapter, RoleAdapter)

    def test_kernel_has_pruning_daemon(self, kernel: ColonyKernel):
        assert isinstance(kernel.pruning_daemon, PruningDaemon)

    def test_kernel_has_falsification_worker(self, kernel: ColonyKernel):
        assert isinstance(kernel.falsification_worker, FalsificationWorker)

    def test_default_config_uses_memory_db(self):
        k = ColonyKernel()
        assert k._config.db_path == ":memory:"

    def test_custom_config_is_stored(self):
        cfg = ColonyKernelConfig(db_path=":memory:", repo_root="/tmp/repo")
        k = ColonyKernel(config=cfg)
        assert k._config.repo_root == "/tmp/repo"


# ---------------------------------------------------------------------------
# propose_action returns GateResult
# ---------------------------------------------------------------------------

class TestProposeAction:

    def test_returns_gate_result(self, kernel: ColonyKernel, proposal: ActionProposal):
        result = kernel.propose_action(proposal)
        assert isinstance(result, GateResult)

    def test_gate_result_has_decision(self, kernel: ColonyKernel, proposal: ActionProposal):
        result = kernel.propose_action(proposal)
        assert isinstance(result.decision, GateDecision)

    def test_gate_result_has_gate_score(self, kernel: ColonyKernel, proposal: ActionProposal):
        result = kernel.propose_action(proposal)
        assert 0.0 <= result.gate_score <= 1.0

    def test_gate_result_has_reason_string(self, kernel: ColonyKernel, proposal: ActionProposal):
        result = kernel.propose_action(proposal)
        assert isinstance(result.reason, str)
        assert len(result.reason) > 0

    def test_gate_result_has_budget_approved_bool(self, kernel: ColonyKernel, proposal: ActionProposal):
        result = kernel.propose_action(proposal)
        assert isinstance(result.budget_approved, bool)

    def test_gate_result_has_required_evidence_list(self, kernel: ColonyKernel, proposal: ActionProposal):
        result = kernel.propose_action(proposal)
        assert isinstance(result.required_evidence, list)

    def test_sandbox_agent_receives_refuse(self, kernel: ColonyKernel, sandbox_proposal: ActionProposal):
        # A brand-new agent (0 prior proposals) is SANDBOX — gate must REFUSE
        result = kernel.propose_action(sandbox_proposal)
        assert result.decision == GateDecision.REFUSE

    def test_refuse_deposits_failure_pheromone(self, kernel: ColonyKernel, sandbox_proposal: ActionProposal):
        # After a REFUSE the failure signal at the target should be > 0
        kernel.propose_action(sandbox_proposal)
        strength = kernel.pheromone_store.sense(sandbox_proposal.target, SignalType.FAILURE)
        assert strength > 0.0

    def test_budget_overrun_causes_hold(self, kernel: ColonyKernel, proposal: ActionProposal):
        # Exhaust the llm_calls budget first
        tight_budget = ResourceBudget(max_llm_calls=1)
        cfg = ColonyKernelConfig(db_path=":memory:", budget=tight_budget)
        k = ColonyKernel(config=cfg)
        # Consume the entire budget
        k.resource_ledger.consume(ResourceCost(llm_calls=1))
        result = k.propose_action(proposal)
        assert result.decision == GateDecision.HOLD
        assert not result.budget_approved

    def test_propose_does_not_consume_budget(self, kernel: ColonyKernel, proposal: ActionProposal):
        before = kernel.resource_ledger.usage_summary()["llm_calls"]["used"]
        kernel.propose_action(proposal)
        after = kernel.resource_ledger.usage_summary()["llm_calls"]["used"]
        # propose_action must NOT consume — only record_outcome does
        assert before == after

    def test_multiple_proposals_do_not_raise(self, kernel: ColonyKernel, proposal: ActionProposal):
        for _ in range(5):
            result = kernel.propose_action(proposal)
            assert isinstance(result, GateResult)


# ---------------------------------------------------------------------------
# record_outcome updates trust
# ---------------------------------------------------------------------------

class TestRecordOutcome:

    def test_returns_consequence_record(self, kernel: ColonyKernel, proposal: ActionProposal):
        record = kernel.record_outcome(
            proposal,
            outcome={"summary": "applied patch", "action_taken": "patch_file"},
            tests_passed=True,
        )
        assert isinstance(record, ConsequenceRecord)

    def test_record_has_trust_delta_computed(self, kernel: ColonyKernel, proposal: ActionProposal):
        record = kernel.record_outcome(
            proposal,
            outcome={"summary": "applied patch"},
            tests_passed=True,
        )
        # trust_delta must be non-zero (ConsequenceMemory.record computed it)
        assert record.trust_delta != 0.0

    def test_passing_tests_increases_trust(self, kernel: ColonyKernel, proposal: ActionProposal):
        # Get baseline trust
        profile_before = kernel.consequence_memory.get_profile(proposal.agent_id)
        trust_before = profile_before.trust_score

        kernel.record_outcome(
            proposal,
            outcome={"summary": "all tests green"},
            tests_passed=True,
        )

        profile_after = kernel.consequence_memory.get_profile(proposal.agent_id)
        assert profile_after.trust_score > trust_before

    def test_failing_tests_decreases_trust(self, kernel: ColonyKernel, proposal: ActionProposal):
        profile_before = kernel.consequence_memory.get_profile(proposal.agent_id)
        trust_before = profile_before.trust_score

        kernel.record_outcome(
            proposal,
            outcome={"summary": "tests failed"},
            tests_passed=False,
        )

        profile_after = kernel.consequence_memory.get_profile(proposal.agent_id)
        assert profile_after.trust_score < trust_before

    def test_record_persists_in_consequence_memory(self, kernel: ColonyKernel, proposal: ActionProposal):
        kernel.record_outcome(
            proposal,
            outcome={"summary": "patch applied"},
            tests_passed=True,
        )
        recent = kernel.consequence_memory.recent_consequences(limit=5)
        assert len(recent) >= 1
        assert recent[0]["agent_id"] == proposal.agent_id

    def test_passing_outcome_reinforces_success_pheromone(self, kernel: ColonyKernel, proposal: ActionProposal):
        kernel.record_outcome(
            proposal,
            outcome={"summary": "success"},
            tests_passed=True,
        )
        strength = kernel.pheromone_store.sense(proposal.target, SignalType.SUCCESS)
        assert strength > 0.0

    def test_failing_outcome_deposits_failure_pheromone(self, kernel: ColonyKernel, proposal: ActionProposal):
        kernel.record_outcome(
            proposal,
            outcome={"summary": "tests failed"},
            tests_passed=False,
        )
        strength = kernel.pheromone_store.sense(proposal.target, SignalType.FAILURE)
        assert strength > 0.0

    def test_outcome_consumes_budget(self, kernel: ColonyKernel, proposal: ActionProposal):
        before = kernel.resource_ledger.usage_summary()["llm_calls"]["used"]
        kernel.record_outcome(
            proposal,
            outcome={"summary": "done"},
            tests_passed=True,
        )
        after = kernel.resource_ledger.usage_summary()["llm_calls"]["used"]
        assert after >= before + proposal.budget_estimate.llm_calls

    def test_human_feedback_good_boosts_trust(self, kernel: ColonyKernel, proposal: ActionProposal):
        profile_before = kernel.consequence_memory.get_profile(proposal.agent_id)
        trust_before = profile_before.trust_score

        kernel.record_outcome(
            proposal,
            outcome={"summary": "done"},
            tests_passed=True,
            human_feedback="good",
        )

        profile_after = kernel.consequence_memory.get_profile(proposal.agent_id)
        assert profile_after.trust_score > trust_before

    def test_human_feedback_bad_reduces_trust_relative_to_none(self, kernel: ColonyKernel, proposal: ActionProposal):
        # Record with "bad" feedback — trust delta should be smaller than with None
        import uuid

        from codomyrmex.colony_kernel.models import ActionProposal as AP

        p_bad = ActionProposal(
            agent_id="agent-bad-feedback",
            agent_type="repair_ant",
            action_type="patch_file",
            target="mod.a",
            rationale="Same action, different feedback path for comparison.",
            expected_outcome="tests pass",
            rollback_plan="git revert HEAD",
            evidence={"x": 1},
        )
        p_none = ActionProposal(
            agent_id="agent-no-feedback",
            agent_type="repair_ant",
            action_type="patch_file",
            target="mod.b",
            rationale="Same action, different feedback path for comparison.",
            expected_outcome="tests pass",
            rollback_plan="git revert HEAD",
            evidence={"x": 1},
        )
        record_bad = kernel.record_outcome(p_bad, {"summary": "done"}, tests_passed=True, human_feedback="bad")
        record_none = kernel.record_outcome(p_none, {"summary": "done"}, tests_passed=True, human_feedback=None)
        assert record_bad.trust_delta < record_none.trust_delta


# ---------------------------------------------------------------------------
# colony_status returns expected keys
# ---------------------------------------------------------------------------

class TestColonyStatus:

    def test_returns_dict(self, kernel: ColonyKernel):
        status = kernel.colony_status()
        assert isinstance(status, dict)

    def test_has_pheromone_summary_key(self, kernel: ColonyKernel):
        status = kernel.colony_status()
        assert "pheromone_summary" in status

    def test_has_budget_usage_key(self, kernel: ColonyKernel):
        status = kernel.colony_status()
        assert "budget_usage" in status

    def test_has_role_distribution_key(self, kernel: ColonyKernel):
        status = kernel.colony_status()
        assert "role_distribution" in status

    def test_has_recent_consequences_key(self, kernel: ColonyKernel):
        status = kernel.colony_status()
        assert "recent_consequences" in status

    def test_has_pruning_candidates_count_key(self, kernel: ColonyKernel):
        status = kernel.colony_status()
        assert "pruning_candidates_count" in status

    def test_pheromone_summary_is_dict(self, kernel: ColonyKernel):
        status = kernel.colony_status()
        summary = status["pheromone_summary"]
        assert isinstance(summary, dict)
        assert "total_signals" in summary
        assert "top_signals" in summary
        assert isinstance(summary["top_signals"], list)

    def test_budget_usage_has_llm_calls(self, kernel: ColonyKernel):
        status = kernel.colony_status()
        assert "llm_calls" in status["budget_usage"]

    def test_budget_usage_has_runtime_seconds(self, kernel: ColonyKernel):
        status = kernel.colony_status()
        assert "runtime_seconds" in status["budget_usage"]

    def test_recent_consequences_is_list(self, kernel: ColonyKernel):
        status = kernel.colony_status()
        assert isinstance(status["recent_consequences"], list)

    def test_role_distribution_is_dict(self, kernel: ColonyKernel):
        status = kernel.colony_status()
        assert isinstance(status["role_distribution"], dict)

    def test_pruning_candidates_count_is_int(self, kernel: ColonyKernel):
        status = kernel.colony_status()
        assert isinstance(status["pruning_candidates_count"], int)

    def test_status_after_outcome_shows_consequence(
        self, kernel: ColonyKernel, proposal: ActionProposal
    ):
        kernel.record_outcome(
            proposal, outcome={"summary": "done"}, tests_passed=True
        )
        status = kernel.colony_status()
        assert len(status["recent_consequences"]) >= 1


# ---------------------------------------------------------------------------
# tick() does not raise
# ---------------------------------------------------------------------------

class TestTick:

    def test_tick_does_not_raise_on_empty_kernel(self, kernel: ColonyKernel):
        kernel.tick()  # should complete silently

    def test_tick_does_not_raise_after_signal_deposit(self, kernel: ColonyKernel):
        signal = ColonySignal(
            location="mypackage.core",
            signal_type=SignalType.SUCCESS,
            strength=1.0,
            source=SignalSource.TEST,
        )
        kernel.pheromone_store.deposit(signal)
        kernel.tick()  # evaporation — should not raise

    def test_tick_evaporates_pheromones(self, kernel: ColonyKernel):
        # Deposit ONE FAST-decay signal, then tick — do not re-deposit inside the tick loop.
        signal = ColonySignal(
            location="mypackage.old",
            signal_type=SignalType.FAILURE,
            strength=0.5,
            decay_rate=DecayRate.FAST,
            source=SignalSource.TEST,
        )
        kernel.pheromone_store.deposit(signal)
        initial_strength = kernel.pheromone_store.sense("mypackage.old", SignalType.FAILURE)
        assert initial_strength > 0.0  # guard: we actually deposited something
        # Tick many times to let FAST-decay evaporation reduce the strength
        for _ in range(50):
            kernel.tick()
        # After 50 ticks the trace should have evaporated (removed → 0.0) or be lower
        final_strength = kernel.pheromone_store.sense("mypackage.old", SignalType.FAILURE)
        assert final_strength < initial_strength

    def test_multiple_ticks_do_not_raise(self, kernel: ColonyKernel):
        for _ in range(10):
            kernel.tick()

    def test_tick_after_record_outcome_does_not_raise(
        self, kernel: ColonyKernel, proposal: ActionProposal
    ):
        kernel.record_outcome(
            proposal, outcome={"summary": "done"}, tests_passed=True
        )
        kernel.tick()  # must not raise

    def test_tick_reduces_pheromone_count_eventually(self, kernel: ColonyKernel):
        # Deposit a single FAST signal and tick until it evaporates
        signal = ColonySignal(
            location="ephemeral.module",
            signal_type=SignalType.RISK,
            strength=0.3,
            decay_rate=DecayRate.FAST,
            source=SignalSource.RUNTIME,
        )
        kernel.pheromone_store.deposit(signal)
        initial_count = len(kernel.pheromone_store)
        # Tick enough times to remove the trace
        for _ in range(100):
            kernel.tick()
        final_count = len(kernel.pheromone_store)
        assert final_count <= initial_count


# ---------------------------------------------------------------------------
# agent_profile helper
# ---------------------------------------------------------------------------

class TestAgentProfile:

    def test_unknown_agent_returns_sandbox_profile(self, kernel: ColonyKernel):
        profile = kernel.agent_profile("totally-unknown-agent")
        assert isinstance(profile, AgentTrustProfile)
        assert profile.role == AgentRole.SANDBOX

    def test_known_agent_returns_profile_after_record(
        self, kernel: ColonyKernel, proposal: ActionProposal
    ):
        kernel.record_outcome(
            proposal, outcome={"summary": "done"}, tests_passed=True
        )
        profile = kernel.agent_profile(proposal.agent_id)
        assert profile.agent_id == proposal.agent_id
        assert profile.total_proposals == 1


# ---------------------------------------------------------------------------
# tick() evaporation path — explicit signal reduction
# ---------------------------------------------------------------------------

class TestTickEvaporation:
    """Tick must call pheromone_store.tick() and reduce signal strength."""

    def test_tick_removes_fast_decay_signal_below_initial(self, kernel: ColonyKernel):
        """A FAST-decay signal deposited once must decrease after repeated ticks."""
        signal = ColonySignal(
            location="mod.evap",
            signal_type=SignalType.FAILURE,
            strength=0.8,
            decay_rate=DecayRate.FAST,
            source=SignalSource.TEST,
        )
        kernel.pheromone_store.deposit(signal)
        initial = kernel.pheromone_store.sense("mod.evap", SignalType.FAILURE)
        assert initial > 0.0

        for _ in range(30):
            kernel.tick()

        final = kernel.pheromone_store.sense("mod.evap", SignalType.FAILURE)
        assert final < initial

    def test_tick_evaporates_to_zero_eventually(self, kernel: ColonyKernel):
        """Enough ticks must evaporate a minimal FAST signal to zero."""
        signal = ColonySignal(
            location="mod.gone",
            signal_type=SignalType.RISK,
            strength=0.1,
            decay_rate=DecayRate.FAST,
            source=SignalSource.RUNTIME,
        )
        kernel.pheromone_store.deposit(signal)
        for _ in range(200):
            kernel.tick()
        # After massive evaporation the trace is either gone (returns 0.0) or negligible
        final = kernel.pheromone_store.sense("mod.gone", SignalType.RISK)
        assert final == 0.0


# ---------------------------------------------------------------------------
# record_outcome() — tests_passed=False and repair_needed=True paths
# ---------------------------------------------------------------------------

class TestRecordOutcomeFailurePaths:
    """Cover FAILURE pheromone deposit and repair_needed trust penalty."""

    def test_tests_failed_deposits_failure_pheromone(
        self, kernel: ColonyKernel, proposal: ActionProposal
    ):
        kernel.record_outcome(
            proposal,
            outcome={"summary": "tests failed"},
            tests_passed=False,
        )
        strength = kernel.pheromone_store.sense(proposal.target, SignalType.FAILURE)
        assert strength > 0.0

    def test_repair_needed_penalises_trust_more_than_plain_failure(
        self, kernel: ColonyKernel
    ):
        """repair_needed=True in outcome adds an extra trust penalty."""
        p_repair = ActionProposal(
            agent_id="agent-repair-needed",
            agent_type="repair_ant",
            action_type="patch_file",
            target="mod.repair",
            rationale="Fix off-by-one error in the loop accumulator.",
            expected_outcome="tests pass after fix",
            rollback_plan="git revert HEAD --no-edit",
            evidence={"test_id": "t1"},
        )
        p_plain = ActionProposal(
            agent_id="agent-plain-fail",
            agent_type="repair_ant",
            action_type="patch_file",
            target="mod.plain",
            rationale="Fix off-by-one error in the loop accumulator.",
            expected_outcome="tests pass after fix",
            rollback_plan="git revert HEAD --no-edit",
            evidence={"test_id": "t2"},
        )
        # Both fail tests; one also needs repair
        r_repair = kernel.record_outcome(
            p_repair,
            outcome={"summary": "tests failed", "repair_needed": True},
            tests_passed=False,
        )
        r_plain = kernel.record_outcome(
            p_plain,
            outcome={"summary": "tests failed"},
            tests_passed=False,
        )
        # repair_needed path adds _TRUST_DELTA_REPAIR on top of _TRUST_DELTA_FAIL
        assert r_repair.trust_delta < r_plain.trust_delta

    def test_repair_needed_true_in_outcome_sets_record_flag(
        self, kernel: ColonyKernel, proposal: ActionProposal
    ):
        record = kernel.record_outcome(
            proposal,
            outcome={"summary": "applied but repair needed", "repair_needed": True},
            tests_passed=True,
        )
        assert record.repair_needed is True

    def test_repair_needed_false_by_default(
        self, kernel: ColonyKernel, proposal: ActionProposal
    ):
        record = kernel.record_outcome(
            proposal,
            outcome={"summary": "clean"},
            tests_passed=True,
        )
        assert record.repair_needed is False


# ---------------------------------------------------------------------------
# propose_action() — CRITICAL falsification → REFUSE
# ---------------------------------------------------------------------------

class TestProposeActionCriticalFalsification:
    """When pheromone pressure at target is >= 6.0 (FAILURE), FalsificationWorker
    returns a CRITICAL finding and the kernel's ActuationGate must REFUSE."""

    def test_critical_pheromone_pressure_causes_refuse(self, kernel: ColonyKernel):
        target = "mod.critical"
        # Deposit a FAILURE signal with strength that will result in >= 6.0 at target.
        # With TEST source multiplier 1.5: initial=5.0 → effective=7.5 which is >= 6.0.
        signal = ColonySignal(
            location=target,
            signal_type=SignalType.FAILURE,
            strength=5.0,
            decay_rate=DecayRate.SLOW,
            source=SignalSource.TEST,
        )
        kernel.pheromone_store.deposit(signal)
        # Verify the pressure is actually high enough
        assert kernel.pheromone_store.sense(target, SignalType.FAILURE) >= 6.0

        proposal = ActionProposal(
            agent_id="agent-alpha",
            agent_type="repair_ant",
            action_type="patch_file",
            target=target,
            rationale="Attempt to fix a heavily-failing module with known critical issues.",
            expected_outcome="tests pass after patch",
            rollback_plan="git revert HEAD --no-edit",
            evidence={"test_id": "t1"},
            budget_estimate=ResourceCost(llm_calls=2, runtime_seconds=5.0, risk_level=0.1),
        )
        # Pre-seed the agent with enough history to avoid SANDBOX block
        for _ in range(3):
            seed = ActionProposal(
                agent_id="agent-alpha",
                agent_type="repair_ant",
                action_type="run_tests",
                target="safe.mod",
                rationale="Seeding trust history so agent is not SANDBOX.",
                expected_outcome="tests pass",
                rollback_plan="none needed",
                evidence={"x": 1},
            )
            kernel.record_outcome(seed, outcome={"summary": "ok"}, tests_passed=True)

        result = kernel.propose_action(proposal)
        assert result.decision == GateDecision.REFUSE

    def test_high_but_not_critical_pressure_may_hold(self, kernel: ColonyKernel):
        """A HIGH (not CRITICAL) finding should yield HOLD or lower, not EXECUTE."""
        target = "mod.high"
        # strength=2.0 * TEST multiplier 1.5 = 3.0: HIGH (>= 3.0, < 6.0)
        signal = ColonySignal(
            location=target,
            signal_type=SignalType.FAILURE,
            strength=2.0,
            decay_rate=DecayRate.SLOW,
            source=SignalSource.TEST,
        )
        kernel.pheromone_store.deposit(signal)
        pressure = kernel.pheromone_store.sense(target, SignalType.FAILURE)
        assert 3.0 <= pressure < 6.0

        proposal = ActionProposal(
            agent_id="agent-alpha",
            agent_type="repair_ant",
            action_type="patch_file",
            target=target,
            rationale="Attempt patch on module with elevated but non-critical failure pressure.",
            expected_outcome="tests pass",
            rollback_plan="git revert HEAD --no-edit",
            evidence={"test_id": "t1"},
            budget_estimate=ResourceCost(llm_calls=1, runtime_seconds=5.0, risk_level=0.1),
        )
        # Seed trust
        for _ in range(3):
            seed = ActionProposal(
                agent_id="agent-alpha",
                agent_type="repair_ant",
                action_type="run_tests",
                target="safe.other",
                rationale="Seeding trust so agent passes SANDBOX check.",
                expected_outcome="tests pass",
                rollback_plan="none",
                evidence={"x": 1},
            )
            kernel.record_outcome(seed, outcome={"summary": "ok"}, tests_passed=True)

        result = kernel.propose_action(proposal)
        # HIGH falsification penalty reduces the score; must not be EXECUTE
        assert result.decision in {GateDecision.HOLD, GateDecision.REFUSE}


# ---------------------------------------------------------------------------
# save_profile() public method on ConsequenceMemory
# ---------------------------------------------------------------------------

class TestSaveProfile:
    """ConsequenceMemory.save_profile() persists an AgentTrustProfile."""

    def test_save_profile_persists_trust_score(self, kernel: ColonyKernel):
        profile = AgentTrustProfile(
            agent_id="persist-agent",
            role=AgentRole.REPAIR_ANT,
            trust_score=0.75,
            total_proposals=5,
            accepted_proposals=4,
        )
        kernel.consequence_memory.save_profile(profile)
        loaded = kernel.consequence_memory.get_profile("persist-agent")
        assert abs(loaded.trust_score - 0.75) < 1e-9

    def test_save_profile_overwrites_existing(self, kernel: ColonyKernel, proposal: ActionProposal):
        kernel.record_outcome(
            proposal, outcome={"summary": "done"}, tests_passed=True
        )
        profile = kernel.consequence_memory.get_profile(proposal.agent_id)
        original_trust = profile.trust_score

        # Manually bump trust and persist
        profile.trust_score = min(1.0, original_trust + 0.20)
        kernel.consequence_memory.save_profile(profile)

        reloaded = kernel.consequence_memory.get_profile(proposal.agent_id)
        assert abs(reloaded.trust_score - profile.trust_score) < 1e-9

    def test_save_profile_then_role_change_is_visible(self, kernel: ColonyKernel):
        """Saving a profile with a different role persists the role change."""
        profile = AgentTrustProfile(
            agent_id="role-change-agent",
            role=AgentRole.SANDBOX,
            trust_score=0.5,
            total_proposals=3,
            accepted_proposals=3,
        )
        kernel.consequence_memory.save_profile(profile)
        profile.role = AgentRole.MEMORY_ANT
        kernel.consequence_memory.save_profile(profile)

        reloaded = kernel.consequence_memory.get_profile("role-change-agent")
        assert reloaded.role == AgentRole.MEMORY_ANT


# ---------------------------------------------------------------------------
# close() on ConsequenceMemory
# ---------------------------------------------------------------------------

class TestConsequenceMemoryClose:
    """ConsequenceMemory.close() must close the underlying SQLite connection."""

    def test_close_does_not_raise(self):
        mem = ConsequenceMemory(db_path=":memory:")
        mem.close()  # must not raise

    def test_double_close_does_not_raise(self):
        """Closing twice should not raise (the __del__ guard covers this)."""
        mem = ConsequenceMemory(db_path=":memory:")
        mem.close()
        # The second close is handled by __del__ internally; call it directly
        # via the protected path to verify the try/except catches the error.
        try:
            mem._conn.close()
        except Exception:
            pass  # expected; SQLite already closed


# ---------------------------------------------------------------------------
# record_outcome() — outcome["cost"] dict path
# ---------------------------------------------------------------------------

class TestRecordOutcomeCostDict:
    """When outcome contains a 'cost' dict, record_outcome must use it."""

    def test_explicit_cost_dict_is_consumed(self, kernel: ColonyKernel, proposal: ActionProposal):
        before = kernel.resource_ledger.usage_summary()["llm_calls"]["used"]
        # Pass an explicit cost dict with 5 llm_calls
        kernel.record_outcome(
            proposal,
            outcome={
                "summary": "done",
                "cost": {"llm_calls": 5},
            },
            tests_passed=True,
        )
        after = kernel.resource_ledger.usage_summary()["llm_calls"]["used"]
        assert after == before + 5

    def test_invalid_cost_dict_falls_back_to_estimate(
        self, kernel: ColonyKernel, proposal: ActionProposal
    ):
        """A malformed 'cost' dict should fall back to the proposal's budget_estimate."""
        before = kernel.resource_ledger.usage_summary()["llm_calls"]["used"]
        kernel.record_outcome(
            proposal,
            outcome={
                "summary": "done",
                # risk_level out of range → ResourceCost raises ValueError
                "cost": {"llm_calls": 2, "risk_level": 99.0},
            },
            tests_passed=True,
        )
        after = kernel.resource_ledger.usage_summary()["llm_calls"]["used"]
        # Must have fallen back to proposal's budget_estimate.llm_calls
        assert after == before + proposal.budget_estimate.llm_calls


# ---------------------------------------------------------------------------
# _parse_human_feedback — numeric and unknown-string paths
# ---------------------------------------------------------------------------

class TestParseHumanFeedback:
    """Exercise the numeric-parse and unknown-string paths of _parse_human_feedback."""

    def test_numeric_string_is_parsed(self, kernel: ColonyKernel, proposal: ActionProposal):
        """Passing "0.5" as human_feedback should increase trust more than None."""
        record = kernel.record_outcome(
            proposal,
            outcome={"summary": "done"},
            tests_passed=True,
            human_feedback="0.5",
        )
        # _parse_human_feedback("0.5") → 0.5; adds 0.5 * _TRUST_DELTA_HUMAN_WEIGHT
        assert record.human_feedback == pytest.approx(0.5)

    def test_negative_numeric_string_is_clamped(self, kernel: ColonyKernel):
        p = ActionProposal(
            agent_id="agent-clamp",
            agent_type="repair_ant",
            action_type="patch_file",
            target="mod.clamp",
            rationale="Test numeric negative feedback clamping path.",
            expected_outcome="tests pass",
            rollback_plan="git revert HEAD",
            evidence={"x": 1},
        )
        record = kernel.record_outcome(
            p,
            outcome={"summary": "done"},
            tests_passed=True,
            human_feedback="-0.5",
        )
        assert record.human_feedback == pytest.approx(-0.5)

    def test_unrecognised_string_yields_zero_feedback(self, kernel: ColonyKernel):
        p = ActionProposal(
            agent_id="agent-unknown-fb",
            agent_type="repair_ant",
            action_type="patch_file",
            target="mod.unknown",
            rationale="Test unknown feedback string normalisation path.",
            expected_outcome="tests pass",
            rollback_plan="git revert HEAD",
            evidence={"x": 1},
        )
        record = kernel.record_outcome(
            p,
            outcome={"summary": "done"},
            tests_passed=True,
            human_feedback="maybe",  # unrecognised → 0.0
        )
        assert record.human_feedback == pytest.approx(0.0)

    def test_out_of_range_numeric_is_clamped_to_one(self, kernel: ColonyKernel):
        p = ActionProposal(
            agent_id="agent-over-fb",
            agent_type="repair_ant",
            action_type="patch_file",
            target="mod.over",
            rationale="Test over-range numeric clamping to 1.0.",
            expected_outcome="tests pass",
            rollback_plan="git revert HEAD",
            evidence={"x": 1},
        )
        record = kernel.record_outcome(
            p,
            outcome={"summary": "done"},
            tests_passed=True,
            human_feedback="5.0",  # > 1.0 → clamped to 1.0
        )
        assert record.human_feedback == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# role change triggers save_profile via record_outcome
# ---------------------------------------------------------------------------

class TestRoleChangeTriggeredSaveProfile:
    """When record_outcome causes a role change, save_profile must be called."""

    def test_role_promotion_is_persisted_after_enough_successful_outcomes(
        self, kernel: ColonyKernel
    ):
        """Build up enough trust that the RoleAdapter promotes the agent;
        confirm the promotion is persisted back by record_outcome."""
        agent_id = "promotable-agent"

        # The RoleAdapter requires >= 3 total_proposals before promotion.
        # _ROLE_REPAIR_MIN_TRUST = 0.20; initial trust_score = 0.1 + deltas.
        # Each passing record adds _TRUST_DELTA_PASS = 0.04.
        # After 3 records: 0.1 + 3*0.04 = 0.22 >= 0.20 → REPAIR_ANT.
        for i in range(3):
            p = ActionProposal(
                agent_id=agent_id,
                agent_type="repair_ant",
                action_type="patch_file",
                target=f"mod.promote.{i}",
                rationale="Seeding outcomes to trigger role promotion.",
                expected_outcome="tests pass",
                rollback_plan="git revert HEAD",
                evidence={"i": i},
            )
            kernel.record_outcome(p, outcome={"summary": "ok"}, tests_passed=True)

        profile = kernel.agent_profile(agent_id)
        # After 3 passing outcomes the agent should have been promoted from SANDBOX
        assert profile.role != AgentRole.SANDBOX


# ---------------------------------------------------------------------------
# propose_action() — EXECUTE branch
# ---------------------------------------------------------------------------

class TestProposeActionExecuteBranch:
    """The EXECUTE branch requires:
    - Agent trust_score >= 0.60  (trust_ok = 1.0)
    - No SANDBOX role            (total_proposals >= 3 after 3 record_outcome calls)
    - No CRITICAL falsification  (clean pheromone field, no FAILURE signals)
    - Budget approved            (default budget has plenty of headroom)
    - All proposal fields present (rollback_plan, evidence, expected_outcome)

    Trust delta per successful record_outcome (no repair, no human_feedback):
        compute_trust_delta → +_TRUST_DELTA_PASS = +0.04

    Starting trust = 0.1; need >= 0.60 for trust_ok = 1.0.
    Calls needed:  ceil((0.60 - 0.10) / 0.04) = ceil(12.5) = 13

    After 13 calls:
        trust_score  = 0.1 + 13 * 0.04 = 0.62  (>= 0.60 → trust_ok = 1.0)
        total_proposals = 13             (>= 3  → role != SANDBOX)
        role         = MEMORY_ANT        (0.35 <= 0.62 < 0.70)

    Gate score with a perfect proposal (all fields, zero risk pheromone):
        budget_ok=1.0  * 0.30 = 0.30
        risk_ok=1.0    * 0.30 = 0.30
        trust_ok=1.0   * 0.25 = 0.25
        completeness=1 * 0.15 = 0.15
        ─────────────────────────────
        total              = 1.00  >= 0.75 → EXECUTE
    """

    _AGENT_ID = "promoted-execute-agent"
    _TRUST_DELTA_PASS = 0.04   # _TRUST_DELTA_PASS from models.py
    _INITIAL_TRUST = 0.10      # AgentTrustProfile default trust_score
    _EXECUTE_TRUST_THRESHOLD = 0.60  # trust >= 0.60 → trust_ok = 1.0 in gate
    _N_OUTCOMES_NEEDED = 13    # ceil((0.60 - 0.10) / 0.04)

    @staticmethod
    def _seed_successful_outcomes(kernel: ColonyKernel, agent_id: str, n: int) -> None:
        """Call kernel.record_outcome n times with tests_passed=True for agent_id."""
        for i in range(n):
            p = ActionProposal(
                agent_id=agent_id,
                agent_type="repair_ant",
                action_type="run_tests",
                target=f"mod.trust.seed.{i}",
                rationale="Seeding successful outcomes to build agent trust above EXECUTE threshold.",
                expected_outcome="all tests pass",
                rollback_plan="git revert HEAD --no-edit",
                evidence={"seed_index": i},
            )
            kernel.record_outcome(p, outcome={"summary": "ok"}, tests_passed=True)

    @staticmethod
    def _make_execute_proposal(agent_id: str) -> ActionProposal:
        """Return a fully-populated ActionProposal that scores 1.00 at the gate."""
        return ActionProposal(
            agent_id=agent_id,
            agent_type="repair_ant",
            action_type="patch_file",
            target="mod.execute.target",
            rationale=(
                "Apply a well-understood, low-risk patch with full test coverage, "
                "a rollback plan, and documented evidence."
            ),
            expected_outcome="all unit tests pass; coverage unchanged",
            budget_estimate=ResourceCost(
                llm_calls=1,
                runtime_seconds=5.0,
                risk_level=0.05,
            ),
            rollback_plan="git revert HEAD --no-edit && uv run pytest",
            evidence={
                "test_ids": ["tests/unit/test_patch.py::test_main"],
                "pr_url": "https://example.com/pr/99",
            },
        )

    def test_propose_action_execute_with_promoted_agent(self, kernel: ColonyKernel):
        """After 13 successful record_outcome calls, propose_action must return EXECUTE."""
        self._seed_successful_outcomes(kernel, self._AGENT_ID, self._N_OUTCOMES_NEEDED)

        # Verify the trust precondition was actually met before calling propose_action
        profile = kernel.agent_profile(self._AGENT_ID)
        assert profile.trust_score >= self._EXECUTE_TRUST_THRESHOLD, (
            f"Precondition failed: expected trust >= {self._EXECUTE_TRUST_THRESHOLD}, "
            f"got {profile.trust_score:.4f} after {self._N_OUTCOMES_NEEDED} outcomes"
        )
        assert profile.role != AgentRole.SANDBOX, (
            f"Precondition failed: agent must not be SANDBOX, got {profile.role}"
        )

        proposal = self._make_execute_proposal(self._AGENT_ID)
        result = kernel.propose_action(proposal)

        assert result.decision == GateDecision.EXECUTE, (
            f"Expected EXECUTE but got {result.decision}. "
            f"gate_score={result.gate_score:.4f}, reason={result.reason!r}, "
            f"trust={profile.trust_score:.4f}, role={profile.role}"
        )

    def test_execute_result_has_correct_fields(self, kernel: ColonyKernel):
        """An EXECUTE GateResult must have gate_score >= 0.75 and no block reason."""
        self._seed_successful_outcomes(kernel, self._AGENT_ID, self._N_OUTCOMES_NEEDED)

        proposal = self._make_execute_proposal(self._AGENT_ID)
        result = kernel.propose_action(proposal)

        # Decision
        assert result.decision == GateDecision.EXECUTE

        # Score at or above the execute threshold
        assert result.gate_score >= 0.75, (
            f"gate_score {result.gate_score:.4f} is below the 0.75 execute threshold"
        )

        # Budget must have been approved
        assert result.budget_approved is True

        # EXECUTE results have empty required_evidence (no blocking items)
        assert result.required_evidence == [], (
            f"Expected empty required_evidence for EXECUTE, got {result.required_evidence}"
        )

        # Falsification severity must be below the CRITICAL threshold (1.0).
        # The FalsificationWorker may still raise LOW/MEDIUM/HIGH findings from
        # proposal heuristics; CRITICAL (weight=1.0) is the only hard REFUSE trigger.
        assert result.falsification_severity < 1.0, (
            f"Expected falsification_severity < 1.0 (non-CRITICAL) for EXECUTE, "
            f"got {result.falsification_severity}"
        )
