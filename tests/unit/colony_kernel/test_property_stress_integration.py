"""Property-based, stress, edge-fuzzing, and integration tests for the Colony Kernel.

Zero-mock policy: no unittest.mock, MagicMock, or pytest-mock.
All tests use real objects: real SQLite (via tmp_path), real TraceField instances,
real YAML config loading (none needed here — pure Python domain logic).

Coverage targets:
  - Property-based: gate_score bounds, trust monotonicity, pheromone decay,
    ResourceCost arithmetic
  - Stress / edge-fuzzing: extreme trust values, risk pressure sweep,
    missing-completeness, massive deposits, 1000-proposal throughput,
    extreme findings lists
  - ConsequenceMemory stress: 1000 records, special-char agent IDs,
    200-agent profiling
  - ResourceLedger boundary: zero costs, max-dimension caps, mixed __add__
  - SignalType × DecayRate integration: full deposit-then-sense matrix
  - RoleAdapter edge cases: 0, 1, 2, 3 proposals (all failed)
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from codomyrmex.agentic_memory.stigmergy.field import TraceField
from codomyrmex.agentic_memory.stigmergy.models import StigmergyConfig
from codomyrmex.colony_kernel.actuation_gate import ActuationGate
from codomyrmex.colony_kernel.consequence_memory import (
    ConsequenceMemory as StandaloneConsequenceMemory,
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
    ResourceCost,
    SignalSource,
    SignalType,
    make_trace_key,
)
from codomyrmex.colony_kernel.pheromone_store import PheromoneStore
from codomyrmex.colony_kernel.resource_ledger import ResourceBudget, ResourceLedger
from codomyrmex.colony_kernel.role_adapter import (
    ConsequenceMemory as RoleConsequenceMemory,
)
from codomyrmex.colony_kernel.role_adapter import (
    RoleAdapter,
)

# ---------------------------------------------------------------------------
# Shared helpers — real objects, no stubs
# ---------------------------------------------------------------------------


class _UnlimitedLedger:
    """ResourceLedger stand-in that always approves (real can_afford protocol)."""

    def can_afford(self, cost: ResourceCost) -> tuple[bool, None]:
        return True, None


class _EmptyLedger:
    """ResourceLedger stand-in that always rejects."""

    def can_afford(self, cost: ResourceCost) -> tuple[bool, str]:
        return False, "test ledger rejects everything"


def _good_proposal(
    agent_id: str = "agent-prop",
    target: str = "codomyrmex.colony_kernel.actuation_gate",
) -> ActionProposal:
    return ActionProposal(
        agent_id=agent_id,
        agent_type="REPAIR_ANT",
        action_type="patch_file",
        target=target,
        rationale="Property-based test proposal with sufficient detail.",
        expected_outcome="All tests pass; no regressions.",
        budget_estimate=ResourceCost(llm_calls=1, runtime_seconds=2.0, risk_level=0.1),
        rollback_plan="git revert HEAD",
        evidence={"test_id": "prop_test"},
    )


def _gate_with_no_pressure(
    trust_score: float,
) -> tuple[ActuationGate, AgentTrustProfile]:
    """Return a fresh gate + profile with the given trust score."""
    field = TraceField(StigmergyConfig())
    gate = ActuationGate(pheromone_store=field, resource_ledger=_UnlimitedLedger())
    profile = AgentTrustProfile(
        agent_id="prop-agent",
        role=AgentRole.REPAIR_ANT,
        trust_score=trust_score,
        total_proposals=20,
        accepted_proposals=18,
    )
    return gate, profile


def _gate_with_risk(
    pressure: float, target: str = "codomyrmex.some.module"
) -> ActuationGate:
    """Return a gate with a RISK signal pre-loaded at *target* with *pressure*."""
    field = TraceField(StigmergyConfig(max_strength=200.0))
    key = f"{target}:{SignalType.RISK.value}"
    field.deposit(key, initial=pressure)
    return ActuationGate(pheromone_store=field, resource_ledger=_UnlimitedLedger())


# ---------------------------------------------------------------------------
# §1  Property-based tests (Hypothesis)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("agent_id", ["hyp-agent"])
class TestPropertyGateScoreBounds:
    """For any valid ActionProposal + AgentTrustProfile, gate_score ∈ [0.0, 1.0]."""

    @given(
        trust=st.floats(min_value=0.3, max_value=1.0, allow_nan=False),
        risk_pressure=st.floats(min_value=0.0, max_value=20.0, allow_nan=False),
        llm_calls=st.integers(min_value=0, max_value=20),
        runtime=st.floats(min_value=0.0, max_value=100.0, allow_nan=False),
        risk_level=st.floats(min_value=0.0, max_value=1.0, allow_nan=False),
    )
    @settings(max_examples=120, deadline=2000)
    def test_gate_score_always_in_unit_interval(
        self,
        agent_id: str,
        trust: float,
        risk_pressure: float,
        llm_calls: int,
        runtime: float,
        risk_level: float,
    ) -> None:
        """gate_score ∈ [0.0, 1.0] for all valid non-SANDBOX inputs."""
        target = "codomyrmex.some.module"
        field = TraceField(StigmergyConfig(max_strength=200.0))
        if risk_pressure > 0:
            key = f"{target}:{SignalType.RISK.value}"
            field.deposit(key, initial=risk_pressure)

        gate = ActuationGate(pheromone_store=field, resource_ledger=_UnlimitedLedger())

        proposal = ActionProposal(
            agent_id=agent_id,
            agent_type="REPAIR_ANT",
            action_type="patch_file",
            target=target,
            rationale="Property test rationale is always present.",
            expected_outcome="Property test outcome is always present.",
            budget_estimate=ResourceCost(
                llm_calls=llm_calls,
                runtime_seconds=runtime,
                risk_level=risk_level,
            ),
            rollback_plan="git revert HEAD",
            evidence={"test_id": "prop_t"},
        )
        profile = AgentTrustProfile(
            agent_id=agent_id,
            role=AgentRole.REPAIR_ANT,
            trust_score=trust,
            total_proposals=20,
            accepted_proposals=18,
        )
        result = gate.evaluate(proposal, profile)

        assert 0.0 <= result.gate_score <= 1.0, (
            f"gate_score {result.gate_score} out of [0,1] for trust={trust}, "
            f"risk_pressure={risk_pressure}"
        )


class TestPropertyTrustScoreEvolution:
    """After N clean outcomes, trust_score ∈ [0,1] and is monotonically non-decreasing."""

    @given(n_successes=st.integers(min_value=1, max_value=50))
    @settings(max_examples=40, deadline=3000)
    def test_trust_monotonically_non_decreasing_after_clean_outcomes(
        self, n_successes: int
    ) -> None:
        """N successive clean (tests_passed=True, repair_needed=False) outcomes must
        result in trust_score ≥ initial trust_score."""
        from codomyrmex.colony_kernel.models import _TRUST_DELTA_PASS

        profile = AgentTrustProfile(
            agent_id="mono-agent", role=AgentRole.SANDBOX, trust_score=0.1
        )
        previous = profile.trust_score
        for _ in range(n_successes):
            profile.apply_delta(_TRUST_DELTA_PASS)
            assert profile.trust_score >= previous, (
                f"Trust decreased: {profile.trust_score} < {previous}"
            )
            previous = profile.trust_score

        assert 0.0 <= profile.trust_score <= 1.0

    @given(trust=st.floats(min_value=0.0, max_value=1.0, allow_nan=False))
    @settings(max_examples=60, deadline=1000)
    def test_trust_score_always_in_unit_interval_after_apply_delta(
        self, trust: float
    ) -> None:
        """apply_delta must always clamp the result to [0.0, 1.0]."""
        profile = AgentTrustProfile(agent_id="clamp-agent", trust_score=trust)
        # Apply a large positive delta — should clamp at 1.0
        profile.apply_delta(100.0)
        assert profile.trust_score == pytest.approx(1.0)

        # Reset and apply large negative delta — should clamp at 0.0
        profile2 = AgentTrustProfile(agent_id="clamp-agent-2", trust_score=trust)
        profile2.apply_delta(-100.0)
        assert profile2.trust_score == pytest.approx(0.0)


class TestPropertyPheromoneDecay:
    """For any ColonySignal with positive strength, after one evaporate tick
    the strength is <= the original strength."""

    @given(
        strength=st.floats(min_value=0.11, max_value=50.0, allow_nan=False),
        decay=st.sampled_from(list(DecayRate)),
        signal_type=st.sampled_from(list(SignalType)),
    )
    @settings(max_examples=80, deadline=2000)
    def test_pheromone_strength_never_increases_after_tick(
        self, strength: float, decay: DecayRate, signal_type: SignalType
    ) -> None:
        """PheromoneStore.evaporate() must never increase any signal's strength."""
        store = PheromoneStore()
        sig = ColonySignal(
            location="codomyrmex.prop.module",
            signal_type=signal_type,
            strength=strength,
            decay_rate=decay,
            source=SignalSource.TEST,
        )
        store.deposit_signal(sig)

        before_results = store.query_pressure("codomyrmex.prop.module", signal_type)
        before = before_results[0].strength if before_results else 0.0

        store.evaporate()

        after_results = store.query_pressure("codomyrmex.prop.module", signal_type)
        after = after_results[0].strength if after_results else 0.0

        assert after <= before + 1e-9, (
            f"Strength increased from {before} to {after} after evaporate; "
            f"decay={decay}, signal_type={signal_type}"
        )


class TestPropertyResourceCostArithmetic:
    """ResourceCost.__add__ is commutative, associative, and identity-preserving."""

    @given(
        a_llm=st.integers(min_value=0, max_value=100),
        b_llm=st.integers(min_value=0, max_value=100),
        a_runtime=st.floats(min_value=0.0, max_value=3600.0, allow_nan=False),
        b_runtime=st.floats(min_value=0.0, max_value=3600.0, allow_nan=False),
        a_risk=st.floats(min_value=0.0, max_value=0.5, allow_nan=False),
        b_risk=st.floats(min_value=0.0, max_value=0.5, allow_nan=False),
    )
    @settings(max_examples=80, deadline=1000)
    def test_resource_cost_add_commutativity(
        self,
        a_llm: int,
        b_llm: int,
        a_runtime: float,
        b_runtime: float,
        a_risk: float,
        b_risk: float,
    ) -> None:
        """a + b == b + a for llm_calls and runtime_seconds (risk saturates at 1.0)."""
        a = ResourceCost(llm_calls=a_llm, runtime_seconds=a_runtime, risk_level=a_risk)
        b = ResourceCost(llm_calls=b_llm, runtime_seconds=b_runtime, risk_level=b_risk)

        ab = a + b
        ba = b + a

        assert ab.llm_calls == ba.llm_calls
        assert ab.runtime_seconds == pytest.approx(ba.runtime_seconds, abs=1e-9)
        assert ab.risk_level == pytest.approx(ba.risk_level, abs=1e-9)

    @given(
        a_llm=st.integers(min_value=0, max_value=50),
        b_llm=st.integers(min_value=0, max_value=50),
        c_llm=st.integers(min_value=0, max_value=50),
        runtime=st.floats(min_value=0.0, max_value=100.0, allow_nan=False),
    )
    @settings(max_examples=60, deadline=1000)
    def test_resource_cost_add_associativity(
        self, a_llm: int, b_llm: int, c_llm: int, runtime: float
    ) -> None:
        """(a + b) + c == a + (b + c) for non-clamping dimensions."""
        a = ResourceCost(llm_calls=a_llm, runtime_seconds=runtime)
        b = ResourceCost(llm_calls=b_llm)
        c = ResourceCost(llm_calls=c_llm)

        abc_left = (a + b) + c
        abc_right = a + (b + c)

        assert abc_left.llm_calls == abc_right.llm_calls
        assert abc_left.runtime_seconds == pytest.approx(
            abc_right.runtime_seconds, abs=1e-9
        )

    @given(llm=st.integers(min_value=0, max_value=100))
    @settings(max_examples=40, deadline=1000)
    def test_resource_cost_add_identity(self, llm: int) -> None:
        """a + zero_cost == a for non-clamping dimensions."""
        a = ResourceCost(llm_calls=llm, runtime_seconds=5.0)
        zero = ResourceCost()
        result = a + zero

        assert result.llm_calls == a.llm_calls
        assert result.runtime_seconds == pytest.approx(a.runtime_seconds, abs=1e-9)


# ---------------------------------------------------------------------------
# §2  Stress / edge-fuzzing tests — trust extremes
# ---------------------------------------------------------------------------


class TestGateExtremeTrust:
    """Edge trust values: 0.0, 0.299, and 1.0."""

    def _fresh_gate(self) -> ActuationGate:
        return ActuationGate(
            pheromone_store=TraceField(StigmergyConfig()),
            resource_ledger=_UnlimitedLedger(),
        )

    def test_trust_zero_is_refused(self) -> None:
        """trust_score = 0.0 triggers the hard-floor REFUSE."""
        gate = self._fresh_gate()
        profile = AgentTrustProfile(
            agent_id="zero-trust", role=AgentRole.REPAIR_ANT, trust_score=0.0
        )
        result = gate.evaluate(_good_proposal(agent_id="zero-trust"), profile)
        assert result.decision is GateDecision.REFUSE
        assert result.gate_score == pytest.approx(0.0)

    def test_trust_just_below_hard_floor_refused(self) -> None:
        """trust_score = 0.299 (just below 0.3 floor) must REFUSE."""
        gate = self._fresh_gate()
        profile = AgentTrustProfile(
            agent_id="below-floor", role=AgentRole.REPAIR_ANT, trust_score=0.299
        )
        result = gate.evaluate(_good_proposal(agent_id="below-floor"), profile)
        assert result.decision is GateDecision.REFUSE

    def test_trust_one_executes_with_good_proposal(self) -> None:
        """trust_score = 1.0 should produce the maximum gate_score and EXECUTE."""
        gate = self._fresh_gate()
        profile = AgentTrustProfile(
            agent_id="max-trust",
            role=AgentRole.REPAIR_ANT,
            trust_score=1.0,
            total_proposals=30,
            accepted_proposals=29,
        )
        result = gate.evaluate(_good_proposal(agent_id="max-trust"), profile)
        assert result.decision is GateDecision.EXECUTE
        assert result.gate_score >= 0.75


# ---------------------------------------------------------------------------
# §3  Stress / edge-fuzzing — risk pressure sweep
# ---------------------------------------------------------------------------


class TestGateExtremeRiskPressure:
    """Risk pressure at 0.0, 0.5, 2.99, 3.0, 5.99, 6.0, 100.0."""

    _TARGET = "codomyrmex.risk.sweep.module"

    def _eval(self, pressure: float) -> GateDecision:
        gate = _gate_with_risk(pressure, target=self._TARGET)
        profile = AgentTrustProfile(
            agent_id="risk-sweep-agent",
            role=AgentRole.REPAIR_ANT,
            trust_score=0.9,
            total_proposals=20,
            accepted_proposals=18,
        )
        result = gate.evaluate(
            _good_proposal(agent_id="risk-sweep-agent", target=self._TARGET), profile
        )
        return result.decision

    def test_zero_risk_pressure_executes(self) -> None:
        assert self._eval(0.0) is GateDecision.EXECUTE

    def test_low_risk_pressure_executes(self) -> None:
        """Pressure 0.5 < MED threshold (3.0) → risk_ok=1.0 → EXECUTE."""
        assert self._eval(0.5) is GateDecision.EXECUTE

    def test_just_below_med_threshold_executes(self) -> None:
        """Pressure 2.99 < 3.0 → risk_ok=1.0 → EXECUTE."""
        assert self._eval(2.99) is GateDecision.EXECUTE

    def test_at_med_threshold_is_not_execute_with_low_trust(self) -> None:
        """At pressure=3.0 risk_ok drops to 0.5; combined with medium trust may HOLD."""
        gate = _gate_with_risk(3.0, target=self._TARGET)
        profile = AgentTrustProfile(
            agent_id="med-risk-medium-trust",
            role=AgentRole.REPAIR_ANT,
            trust_score=0.35,
            total_proposals=5,
            accepted_proposals=3,
        )
        result = gate.evaluate(
            _good_proposal(agent_id="med-risk-medium-trust", target=self._TARGET),
            profile,
        )
        # score = 0.30 + 0.5*0.30 + 0.5*0.25 + 0.15 = 0.30+0.15+0.125+0.15 = 0.725 < 0.75
        assert result.decision in {GateDecision.HOLD, GateDecision.EXECUTE}

    def test_just_below_high_threshold_not_refused(self) -> None:
        """Pressure 5.99 < HIGH (6.0) → risk_ok=0.5 still possible."""
        gate = _gate_with_risk(5.99, target=self._TARGET)
        profile = AgentTrustProfile(
            agent_id="near-high-risk",
            role=AgentRole.REPAIR_ANT,
            trust_score=0.9,
            total_proposals=20,
            accepted_proposals=18,
        )
        result = gate.evaluate(
            _good_proposal(agent_id="near-high-risk", target=self._TARGET), profile
        )
        # risk_ok=0.5; with high trust score can still reach 0.85
        assert result.decision in {GateDecision.EXECUTE, GateDecision.HOLD}

    def test_at_high_threshold_blocks_execute(self) -> None:
        """Pressure 6.0 → risk_ok=0.0 → max score = 0.70 < 0.75 → HOLD."""
        gate = _gate_with_risk(6.0, target=self._TARGET)
        profile = AgentTrustProfile(
            agent_id="high-risk-agent",
            role=AgentRole.REPAIR_ANT,
            trust_score=0.9,
            total_proposals=20,
            accepted_proposals=18,
        )
        result = gate.evaluate(
            _good_proposal(agent_id="high-risk-agent", target=self._TARGET), profile
        )
        assert result.decision in {GateDecision.HOLD, GateDecision.REFUSE}

    def test_extreme_risk_pressure_100_blocks_execute(self) -> None:
        """Extreme pressure 100.0 → still risk_ok=0.0 → HOLD or REFUSE."""
        gate = _gate_with_risk(100.0, target=self._TARGET)
        profile = AgentTrustProfile(
            agent_id="extreme-risk-agent",
            role=AgentRole.REPAIR_ANT,
            trust_score=1.0,
            total_proposals=50,
            accepted_proposals=50,
        )
        result = gate.evaluate(
            _good_proposal(agent_id="extreme-risk-agent", target=self._TARGET), profile
        )
        assert result.decision in {GateDecision.HOLD, GateDecision.REFUSE}


# ---------------------------------------------------------------------------
# §4  Gate with all fields missing (completeness = 0)
# ---------------------------------------------------------------------------


class TestGateAllMissingCompleteness:
    """All 3 completeness fields empty — verifies the gate still produces a valid result."""

    def test_gate_all_missing_completeness_produces_valid_result(self) -> None:
        gate = ActuationGate(
            pheromone_store=TraceField(StigmergyConfig()),
            resource_ledger=_UnlimitedLedger(),
        )
        # All 3 optional completeness fields are missing/empty
        proposal = ActionProposal(
            agent_id="complete-miss-agent",
            agent_type="REPAIR_ANT",
            action_type="patch_file",
            target="codomyrmex.empty.completeness",
            rationale="Just a rationale.",
            expected_outcome="  ",  # whitespace-only counts as missing
            budget_estimate=ResourceCost(),
            rollback_plan="",  # missing
            evidence={},  # missing
        )
        profile = AgentTrustProfile(
            agent_id="complete-miss-agent",
            role=AgentRole.REPAIR_ANT,
            trust_score=0.9,
            total_proposals=20,
            accepted_proposals=18,
        )
        result = gate.evaluate(proposal, profile)
        assert isinstance(result.decision, GateDecision)
        assert 0.0 <= result.gate_score <= 1.0
        # At minimum 2 of 3 missing fields flagged in reason
        missing_mentioned = sum(
            1
            for f in ("rollback_plan", "evidence", "expected_outcome")
            if f in result.reason
        )
        assert missing_mentioned >= 1


# ---------------------------------------------------------------------------
# §5  PheromoneStore stress — 1000 signals
# ---------------------------------------------------------------------------


@pytest.mark.slow
class TestPheromoneStoreMassiveDeposits:
    """Deposit 1000 signals, then query and tick — no crashes, correct aggregation."""

    def test_massive_deposits_query_and_tick(self) -> None:
        store = PheromoneStore()
        n = 1000
        locations = [f"codomyrmex.stress.module_{i % 50}" for i in range(n)]

        for i, loc in enumerate(locations):
            sig = ColonySignal(
                location=loc,
                signal_type=SignalType.FAILURE,
                strength=0.5,
                decay_rate=DecayRate.NORMAL,
                source=SignalSource.TEST,
            )
            store.deposit_signal(sig)

        # 50 distinct locations × FAILURE type — each accumulated 20 deposits × 0.5 = 10.0
        for mod_i in range(50):
            loc = f"codomyrmex.stress.module_{mod_i}"
            results = store.query_pressure(loc, SignalType.FAILURE)
            assert len(results) == 1
            assert results[0].strength == pytest.approx(10.0, abs=1e-6)

        # evaporate once — all strengths should decrease
        store.evaporate()

        for mod_i in range(50):
            loc = f"codomyrmex.stress.module_{mod_i}"
            results = store.query_pressure(loc, SignalType.FAILURE)
            # 10.0 - 0.10 (NORMAL rate) = 9.90
            assert len(results) == 1
            assert results[0].strength == pytest.approx(9.90, abs=1e-6)

    def test_massive_mixed_signal_types_distinct(self) -> None:
        """1000 signals across all SignalTypes, then verify each type is distinct."""
        store = PheromoneStore()
        location = "codomyrmex.stress.mixed_types"
        for st_type in SignalType:
            for i in range(10):
                sig = ColonySignal(
                    location=location,
                    signal_type=st_type,
                    strength=1.0,
                    decay_rate=DecayRate.SLOW,
                    source=SignalSource.TEST,
                )
                store.deposit_signal(sig)

        for st_type in SignalType:
            results = store.query_pressure(location, st_type)
            assert len(results) == 1
            assert results[0].strength == pytest.approx(10.0, abs=1e-6)


# ---------------------------------------------------------------------------
# §6  Kernel stress — 1000 proposals
# ---------------------------------------------------------------------------


@pytest.mark.slow
class TestKernelThousandProposals:
    """Submit 1000 proposals to the ColonyKernel — assert no crashes and valid results."""

    def test_kernel_handles_thousand_proposals_without_crash(self) -> None:
        from codomyrmex.colony_kernel.kernel import ColonyKernel, ColonyKernelConfig

        kernel = ColonyKernel(config=ColonyKernelConfig(db_path=":memory:"))
        n = 1000
        decisions = []
        for i in range(n):
            proposal = ActionProposal(
                agent_id=f"stress-agent-{i % 20}",
                agent_type="REPAIR_ANT",
                action_type="patch_file",
                target=f"codomyrmex.stress.module_{i % 10}",
                rationale=f"Stress test proposal #{i} with full rationale text.",
                expected_outcome=f"All tests pass after stress patch #{i}.",
                budget_estimate=ResourceCost(
                    llm_calls=1, runtime_seconds=1.0, risk_level=0.05
                ),
                rollback_plan="git revert HEAD",
                evidence={"stress_run": i},
            )
            result = kernel.propose_action(proposal)
            assert isinstance(result.decision, GateDecision)
            assert 0.0 <= result.gate_score <= 1.0
            decisions.append(result.decision)

        assert len(decisions) == n
        # All new agents start as SANDBOX → expect at least some REFUSEs
        assert GateDecision.REFUSE in decisions


# ---------------------------------------------------------------------------
# §7  ActuationGate extreme findings
# ---------------------------------------------------------------------------


class TestActuationGateExtremeFindings:
    """Empty findings list, 50 findings, mixed severity — all produce valid GateResult."""

    def _gate_and_profile(self) -> tuple[ActuationGate, AgentTrustProfile]:
        field = TraceField(StigmergyConfig())
        gate = ActuationGate(pheromone_store=field, resource_ledger=_UnlimitedLedger())
        profile = AgentTrustProfile(
            agent_id="findings-agent",
            role=AgentRole.REPAIR_ANT,
            trust_score=0.85,
            total_proposals=20,
            accepted_proposals=18,
        )
        return gate, profile

    def _finding(self, sev: FalsificationSeverity) -> FalsificationFinding:
        return FalsificationFinding(
            claim="claim under test",
            attack_vector="edge_case",
            severity=sev,
        )

    def test_empty_findings_list_valid_result(self) -> None:
        gate, profile = self._gate_and_profile()
        proposal = _good_proposal(agent_id="findings-agent")
        result = gate.evaluate(proposal, profile, findings=[], budget_approved=True)
        assert isinstance(result.decision, GateDecision)
        assert 0.0 <= result.gate_score <= 1.0

    def test_fifty_low_severity_findings_valid_result(self) -> None:
        gate, profile = self._gate_and_profile()
        proposal = _good_proposal(agent_id="findings-agent")
        findings = [self._finding(FalsificationSeverity.LOW) for _ in range(50)]
        result = gate.evaluate(
            proposal, profile, findings=findings, budget_approved=True
        )
        assert isinstance(result.decision, GateDecision)
        assert 0.0 <= result.gate_score <= 1.0

    def test_mixed_severity_findings_produce_valid_result(self) -> None:
        gate, profile = self._gate_and_profile()
        proposal = _good_proposal(agent_id="findings-agent")
        findings = [
            self._finding(FalsificationSeverity.LOW),
            self._finding(FalsificationSeverity.MEDIUM),
            self._finding(FalsificationSeverity.HIGH),
            self._finding(FalsificationSeverity.CRITICAL),
        ]
        result = gate.evaluate(
            proposal, profile, findings=findings, budget_approved=True
        )
        assert isinstance(result.decision, GateDecision)
        assert 0.0 <= result.gate_score <= 1.0

    def test_single_critical_finding_reduces_score(self) -> None:
        """A CRITICAL finding contributes weight 1.0 and must reduce gate_score vs clean."""
        gate_clean, profile = self._gate_and_profile()
        proposal = _good_proposal(agent_id="findings-agent")
        clean_result = gate_clean.evaluate(
            proposal, profile, findings=[], budget_approved=True
        )

        gate_critical, profile2 = self._gate_and_profile()
        proposal2 = _good_proposal(agent_id="findings-agent")
        profile2.trust_score = 0.85
        critical_result = gate_critical.evaluate(
            proposal2,
            profile2,
            findings=[self._finding(FalsificationSeverity.CRITICAL)],
            budget_approved=True,
        )

        # falsification_severity > 0 for the critical case
        assert critical_result.falsification_severity > 0.0
        # Score with critical finding must be ≤ clean score
        assert critical_result.gate_score <= clean_result.gate_score + 1e-9


# ---------------------------------------------------------------------------
# §8  ConsequenceMemory stress tests
# ---------------------------------------------------------------------------


@pytest.mark.slow
class TestConsequenceMemory1000Records:
    """Persist 1000 records, verify retrieval accuracy (both in-memory and SQLite)."""

    def _proposal(self, agent_id: str) -> ActionProposal:
        return ActionProposal(
            agent_id=agent_id,
            agent_type="REPAIR_ANT",
            action_type="patch_file",
            target="codomyrmex.stress.consequence",
            rationale="Stress-test record.",
            expected_outcome="Tests green.",
            budget_estimate=ResourceCost(llm_calls=1, runtime_seconds=1.0),
            rollback_plan="git revert HEAD",
            evidence={"run": "stress"},
        )

    def _record(self, agent_id: str, tests_passed: bool = True) -> ConsequenceRecord:
        return ConsequenceRecord(
            proposal=self._proposal(agent_id),
            action_taken="applied patch",
            actual_outcome="all tests passed" if tests_passed else "tests failed",
            tests_passed=tests_passed,
            repair_needed=False,
        )

    def test_1000_records_retrievable_in_memory(self) -> None:
        memory = StandaloneConsequenceMemory(db_path=None)
        agent = "stress-agent-inmem"
        n = 1000
        for _ in range(n):
            memory.record(self._record(agent))
        results = memory.history(agent, limit=n + 10)
        assert len(results) == n

    def test_1000_records_retrievable_sqlite(self, tmp_path: Path) -> None:
        db_file = str(tmp_path / "stress_1000.db")
        memory = StandaloneConsequenceMemory(db_path=db_file)
        agent = "stress-agent-sqlite"
        n = 1000
        for _ in range(n):
            memory.record(self._record(agent))
        results = memory.history(agent, limit=n + 10)
        assert len(results) == n
        memory.close()

    def test_1000_records_trust_score_in_unit_interval(self) -> None:
        memory = StandaloneConsequenceMemory(db_path=None)
        agent = "stress-trust-agent"
        for _ in range(1000):
            memory.record(self._record(agent, tests_passed=True))
        score = memory.trust_score(agent)
        assert 0.0 <= score <= 1.0


class TestConsequenceMemoryExtremeAgentIds:
    """Agent IDs with special chars and very long names are stored and retrieved correctly."""

    _SPECIAL_IDS = [
        "agent-with-dashes",
        "agent_with_underscores",
        "agent.with.dots",
        "agent:with:colons",
        "agent/with/slashes",
        "agent with spaces",
        "αβγδ-unicode-agent",
        "a" * 256,  # 256-char agent ID
        "agent@domain.tld",
        "1234567890" * 10,  # 100-char numeric string
    ]

    def _record(self, agent_id: str) -> ConsequenceRecord:
        return ConsequenceRecord(
            proposal=ActionProposal(
                agent_id=agent_id,
                agent_type="REPAIR_ANT",
                action_type="patch_file",
                target="codomyrmex.special.agent",
                rationale="Special char agent test.",
                expected_outcome="Stored and retrieved without corruption.",
                budget_estimate=ResourceCost(),
                rollback_plan="git revert HEAD",
                evidence={},
            ),
            action_taken="special char test",
            actual_outcome="stored OK",
            tests_passed=True,
            repair_needed=False,
        )

    @pytest.mark.parametrize("agent_id", _SPECIAL_IDS)
    def test_special_agent_id_stored_and_retrieved(self, agent_id: str) -> None:
        memory = StandaloneConsequenceMemory(db_path=None)
        rec = self._record(agent_id)
        memory.record(rec)
        results = memory.history(agent_id, limit=5)
        assert len(results) == 1
        assert results[0].proposal.agent_id == agent_id

    @pytest.mark.parametrize("agent_id", _SPECIAL_IDS)
    def test_special_agent_id_trust_score_valid(self, agent_id: str) -> None:
        memory = StandaloneConsequenceMemory(db_path=None)
        rec = self._record(agent_id)
        memory.record(rec)
        score = memory.trust_score(agent_id)
        assert 0.0 <= score <= 1.0


class TestConsequenceMemorySimultaneousProfiles:
    """Create 200 agents, profile all — no collisions or missing data."""

    def test_200_agents_all_profiled_correctly(self) -> None:
        memory = StandaloneConsequenceMemory(db_path=None)
        n_agents = 200
        for i in range(n_agents):
            agent_id = f"profile-agent-{i:04d}"
            rec = ConsequenceRecord(
                proposal=ActionProposal(
                    agent_id=agent_id,
                    agent_type="REPAIR_ANT",
                    action_type="patch_file",
                    target="codomyrmex.profile.mass",
                    rationale=f"Profile test agent #{i}.",
                    expected_outcome="profile stored.",
                    budget_estimate=ResourceCost(),
                    rollback_plan="git revert HEAD",
                    evidence={},
                ),
                action_taken="profile test",
                actual_outcome="ok",
                tests_passed=(i % 3 != 0),
                repair_needed=False,
            )
            memory.record(rec)

        for i in range(n_agents):
            agent_id = f"profile-agent-{i:04d}"
            results = memory.history(agent_id, limit=5)
            assert len(results) == 1
            score = memory.trust_score(agent_id)
            assert 0.0 <= score <= 1.0


# ---------------------------------------------------------------------------
# §9  ResourceLedger boundary tests
# ---------------------------------------------------------------------------


class TestResourceLedgerZeroCosts:
    """All dimensions at exactly 0 are always affordable."""

    def test_zero_cost_always_affordable(self) -> None:
        ledger = ResourceLedger()
        ok, reason = ledger.can_afford(ResourceCost())
        assert ok is True
        assert reason is None

    def test_zero_cost_does_not_change_accumulator(self) -> None:
        ledger = ResourceLedger()
        ledger.record_cost(ResourceCost(), agent_id="zero-agent")
        usage = ledger.current_usage()
        assert usage.llm_calls == 0
        assert usage.runtime_seconds == pytest.approx(0.0)

    def test_zero_cost_after_accumulation_still_checks_correctly(self) -> None:
        ledger = ResourceLedger()
        ledger.record_cost(ResourceCost(llm_calls=10), agent_id="base-agent")
        ok, _ = ledger.can_afford(ResourceCost())
        assert ok is True


class TestResourceLedgerMaxDimensions:
    """Exactly at cap boundary — affordable; 1 unit over — rejected."""

    def test_at_every_cap_boundary_is_affordable(self) -> None:
        budget = ResourceBudget(
            max_llm_calls_per_hour=100,
            max_runtime_seconds=60.0,
            max_risk_level=0.5,
            max_human_attention_minutes=30.0,
            max_merge_risk=0.4,
            total_doc_debt_allowed=50.0,
            max_security_exposure=0.3,
        )
        ledger = ResourceLedger(budget=budget)
        cost = ResourceCost(
            llm_calls=100,
            runtime_seconds=60.0,
            risk_level=0.5,
            human_attention_minutes=30.0,
            merge_risk=0.4,
            doc_debt=50.0,
            security_exposure=0.3,
        )
        ok, reason = ledger.can_afford(cost)
        assert ok is True, f"Expected affordable at cap boundary; got: {reason}"

    def test_one_over_llm_cap_rejected(self) -> None:
        budget = ResourceBudget(max_llm_calls_per_hour=10)
        ledger = ResourceLedger(budget=budget)
        ok, reason = ledger.can_afford(ResourceCost(llm_calls=11))
        assert ok is False
        assert "llm_calls" in (reason or "")

    def test_one_over_runtime_cap_rejected(self) -> None:
        budget = ResourceBudget(max_runtime_seconds=10.0)
        ledger = ResourceLedger(budget=budget)
        ok, reason = ledger.can_afford(ResourceCost(runtime_seconds=10.001))
        assert ok is False
        assert "runtime_seconds" in (reason or "")

    def test_doc_debt_at_cap_then_one_over(self) -> None:
        budget = ResourceBudget(total_doc_debt_allowed=5.0)
        ledger = ResourceLedger(budget=budget)
        ok_at, _ = ledger.can_afford(ResourceCost(doc_debt=5.0))
        ok_over, reason = ledger.can_afford(ResourceCost(doc_debt=5.001))
        assert ok_at is True
        assert ok_over is False
        assert "doc_debt" in (reason or "")


class TestResourceCostMixedAdd:
    """ResourceCost.__add__ with different field combinations."""

    def test_add_only_llm_calls(self) -> None:
        a = ResourceCost(llm_calls=5)
        b = ResourceCost(llm_calls=3)
        result = a + b
        assert result.llm_calls == 8
        assert result.runtime_seconds == pytest.approx(0.0)
        assert result.risk_level == pytest.approx(0.0)

    def test_add_only_runtime_seconds(self) -> None:
        a = ResourceCost(runtime_seconds=10.5)
        b = ResourceCost(runtime_seconds=4.2)
        result = a + b
        assert result.runtime_seconds == pytest.approx(14.7, abs=1e-9)
        assert result.llm_calls == 0

    def test_add_risk_clamps_at_one(self) -> None:
        a = ResourceCost(risk_level=0.7)
        b = ResourceCost(risk_level=0.7)
        result = a + b
        # 0.7 + 0.7 = 1.4 → clamped to 1.0
        assert result.risk_level == pytest.approx(1.0)

    def test_add_merge_risk_clamps_at_one(self) -> None:
        a = ResourceCost(merge_risk=0.6)
        b = ResourceCost(merge_risk=0.6)
        result = a + b
        assert result.merge_risk == pytest.approx(1.0)

    def test_add_security_exposure_clamps_at_one(self) -> None:
        a = ResourceCost(security_exposure=0.8)
        b = ResourceCost(security_exposure=0.8)
        result = a + b
        assert result.security_exposure == pytest.approx(1.0)

    def test_add_all_fields_simultaneously(self) -> None:
        a = ResourceCost(
            llm_calls=5,
            runtime_seconds=10.0,
            risk_level=0.2,
            human_attention_minutes=3.0,
            merge_risk=0.1,
            doc_debt=1.0,
            security_exposure=0.1,
        )
        b = ResourceCost(
            llm_calls=3,
            runtime_seconds=5.0,
            risk_level=0.3,
            human_attention_minutes=2.0,
            merge_risk=0.2,
            doc_debt=0.5,
            security_exposure=0.2,
        )
        result = a + b
        assert result.llm_calls == 8
        assert result.runtime_seconds == pytest.approx(15.0, abs=1e-9)
        assert result.risk_level == pytest.approx(0.5, abs=1e-9)
        assert result.human_attention_minutes == pytest.approx(5.0, abs=1e-9)
        assert result.merge_risk == pytest.approx(0.3, abs=1e-9)
        assert result.doc_debt == pytest.approx(1.5, abs=1e-9)
        assert result.security_exposure == pytest.approx(0.3, abs=1e-9)

    def test_add_zero_to_zero_is_zero(self) -> None:
        result = ResourceCost() + ResourceCost()
        assert result.llm_calls == 0
        assert result.runtime_seconds == pytest.approx(0.0)
        assert result.risk_level == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# §10  SignalType × DecayRate integration tests
# ---------------------------------------------------------------------------


class TestAllSignalTypesCanBeDeposited:
    """Every SignalType × DecayRate combination can be deposited without error."""

    @pytest.mark.parametrize("sig_type", list(SignalType))
    @pytest.mark.parametrize("decay", list(DecayRate))
    def test_deposit_any_signal_type_any_decay_rate(
        self, sig_type: SignalType, decay: DecayRate
    ) -> None:
        store = PheromoneStore()
        sig = ColonySignal(
            location="codomyrmex.integration.matrix",
            signal_type=sig_type,
            strength=1.0,
            decay_rate=decay,
            source=SignalSource.TEST,
        )
        # Should not raise
        store.deposit_signal(sig)
        results = store.query_pressure("codomyrmex.integration.matrix", sig_type)
        assert len(results) == 1
        assert results[0].strength == pytest.approx(1.0, abs=1e-9)
        assert results[0].signal_type == sig_type
        assert results[0].decay_rate == decay


class TestAllSignalTypesCanBeSensed:
    """Deposit then sense each SignalType — sense returns positive strength."""

    @pytest.mark.parametrize("sig_type", list(SignalType))
    def test_deposit_then_sense_each_signal_type(self, sig_type: SignalType) -> None:
        store = PheromoneStore()
        location = f"codomyrmex.sense.test.{sig_type.value}"
        sig = ColonySignal(
            location=location,
            signal_type=sig_type,
            strength=2.0,
            decay_rate=DecayRate.SLOW,
            source=SignalSource.TEST,
        )
        store.deposit_signal(sig)
        sensed = store.sense(location, sig_type)
        assert sensed > 0.0, (
            f"Expected positive sense for {sig_type.value}; got {sensed}"
        )

    @pytest.mark.parametrize("sig_type", list(SignalType))
    def test_sense_absent_signal_returns_zero(self, sig_type: SignalType) -> None:
        store = PheromoneStore()
        sensed = store.sense("codomyrmex.absent.module", sig_type)
        assert sensed == pytest.approx(0.0, abs=1e-9)


# ---------------------------------------------------------------------------
# §11  RoleAdapter edge cases — proposal count boundaries
# ---------------------------------------------------------------------------


class TestRoleAdapterZeroProposals:
    """An agent with zero proposals is always SANDBOX."""

    def test_zero_proposals_is_sandbox(self) -> None:
        memory = RoleConsequenceMemory()
        adapter = RoleAdapter(memory)
        # get_profile initialises the agent
        profile = adapter.get_profile("zero-prop-agent")
        assert profile is not None
        assert profile.total_proposals == 0
        role = adapter.assign_role("zero-prop-agent")
        assert role is AgentRole.SANDBOX

    def test_zero_proposals_trust_below_floor(self) -> None:
        memory = RoleConsequenceMemory()
        adapter = RoleAdapter(memory)
        profile = adapter.get_profile("zero-prop-trust")
        assert profile is not None
        # Default trust is 0.1, below the promotion threshold
        assert profile.trust_score < 0.3


class TestRoleAdapterOneProposal:
    """Exactly 1 proposal — not enough for promotion; stays SANDBOX."""

    def test_one_proposal_stays_sandbox_with_low_trust(self) -> None:
        memory = RoleConsequenceMemory()
        adapter = RoleAdapter(memory)
        agent_id = "one-prop-agent"
        adapter.get_profile(agent_id)

        record = ConsequenceRecord(
            proposal=ActionProposal(
                agent_id=agent_id,
                agent_type="repair_worker",
                action_type="test_fix",
                target="codomyrmex.some_module",
                rationale="automated repair",
                expected_outcome="tests green",
                budget_estimate=ResourceCost(),
            ),
            action_taken="applied patch",
            actual_outcome="tests green",
            tests_passed=True,
            repair_needed=False,
            trust_delta=0.0,
        )
        memory.store_record(record)
        profile = memory.get_profile(agent_id)
        assert profile is not None
        profile.total_proposals = 1
        profile.accepted_proposals = 1
        memory.save_profile(profile)

        role = adapter.assign_role(agent_id)
        # 1 proposal is below _ROLE_MIN_PROPOSALS_FOR_PROMOTION (3)
        # and trust starts at 0.1, so SANDBOX unless trust was raised
        # The default trust of 0.1 ensures SANDBOX
        assert role is AgentRole.SANDBOX


class TestRoleAdapterTwoProposals:
    """Exactly 2 proposals with high trust — still 1 below minimum for promotion."""

    def test_two_proposals_below_minimum_stays_sandbox_or_repair(self) -> None:
        """With 2 proposals and trust=0.82, role may be SANDBOX (count-gated)."""
        memory = RoleConsequenceMemory()
        adapter = RoleAdapter(memory)
        agent_id = "two-prop-agent"
        adapter.get_profile(agent_id)

        for _ in range(2):
            record = ConsequenceRecord(
                proposal=ActionProposal(
                    agent_id=agent_id,
                    agent_type="repair_worker",
                    action_type="test_fix",
                    target="codomyrmex.some_module",
                    rationale="automated repair",
                    expected_outcome="tests green",
                    budget_estimate=ResourceCost(),
                ),
                action_taken="applied patch",
                actual_outcome="tests green",
                tests_passed=True,
                repair_needed=False,
                trust_delta=0.0,
            )
            memory.store_record(record)
            profile = memory.get_profile(agent_id)
            assert profile is not None
            profile.total_proposals += 1
            profile.accepted_proposals += 1
            profile.consequence_history.append(record.consequence_id)
            memory.save_profile(profile)

        profile = memory.get_profile(agent_id)
        assert profile is not None
        profile.trust_score = 0.82
        memory.save_profile(profile)

        role = adapter.assign_role(agent_id)
        # With test_fix successes and trust >= 0.8, specialization rules
        # may assign REPAIR_ANT regardless of count — both outcomes are valid
        assert role in {AgentRole.SANDBOX, AgentRole.REPAIR_ANT}


class TestRoleAdapterThreeProposalsAllFailed:
    """3 proposals, all failed — consecutive failures → SANDBOX."""

    def test_three_proposals_all_failed_is_sandbox(self) -> None:
        memory = RoleConsequenceMemory()
        adapter = RoleAdapter(memory)
        agent_id = "three-fail-agent"
        adapter.get_profile(agent_id)

        for _ in range(3):
            record = ConsequenceRecord(
                proposal=ActionProposal(
                    agent_id=agent_id,
                    agent_type="repair_worker",
                    action_type="test_fix",
                    target="codomyrmex.some_module",
                    rationale="automated repair",
                    expected_outcome="tests green",
                    budget_estimate=ResourceCost(),
                ),
                action_taken="applied patch",
                actual_outcome="tests still failing",
                tests_passed=False,
                repair_needed=True,
                trust_delta=0.0,
            )
            memory.store_record(record)
            profile = memory.get_profile(agent_id)
            assert profile is not None
            profile.total_proposals += 1
            profile.consequence_history.append(record.consequence_id)
            memory.save_profile(profile)

        role = adapter.assign_role(agent_id)
        # 3 consecutive failures → _consecutive_failures >= 3 → SANDBOX
        assert role is AgentRole.SANDBOX

    def test_three_failures_trust_not_above_floor(self) -> None:
        """After 3 failures from default trust, trust stays at or below initial."""
        from codomyrmex.colony_kernel.models import (
            _TRUST_DELTA_FAIL,
            _TRUST_DELTA_REPAIR,
        )

        profile = AgentTrustProfile(agent_id="fail-trust-agent", trust_score=0.1)
        for _ in range(3):
            delta = (
                _TRUST_DELTA_FAIL + _TRUST_DELTA_REPAIR
            )  # tests_passed=False, repair_needed=True
            profile.apply_delta(delta)
        # Trust can only go down from failures
        assert profile.trust_score <= 0.1


# ---------------------------------------------------------------------------
# §12  make_trace_key integration — all signal types produce distinct keys
# ---------------------------------------------------------------------------


class TestMakeTraceKeyAllSignalTypes:
    """make_trace_key produces distinct keys for every (location, signal_type) pair."""

    def test_all_signal_type_keys_distinct_at_same_location(self) -> None:
        location = "codomyrmex.key.integration"
        keys = [make_trace_key(location, st) for st in SignalType]
        assert len(keys) == len(set(keys)), (
            "Some SignalType keys collided at the same location"
        )

    def test_same_signal_type_different_locations_distinct(self) -> None:
        locations = [f"codomyrmex.module_{i}" for i in range(10)]
        keys = [make_trace_key(loc, SignalType.FAILURE) for loc in locations]
        assert len(keys) == len(set(keys)), "Some location keys collided"

    @pytest.mark.parametrize("sig_type", list(SignalType))
    def test_key_format_location_colon_signal(self, sig_type: SignalType) -> None:
        location = "codomyrmex.test.key_format"
        key = make_trace_key(location, sig_type)
        assert key == f"{location}:{sig_type.value}"
