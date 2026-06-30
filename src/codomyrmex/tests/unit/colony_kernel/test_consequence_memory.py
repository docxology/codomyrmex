"""Tests for ConsequenceMemory — Colony Kernel outcome accountability store.

Zero-mock policy: no unittest.mock, MagicMock, or pytest-mock.
Both in-memory mode (db_path=None) and SQLite mode (tmp_path) are exercised.
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

import pytest

from codomyrmex.colony_kernel.consequence_memory import (
    _DELTA_FEEDBACK_ACCEPTED,
    _DELTA_FEEDBACK_REJECTED,
    _DELTA_REPAIR_NEEDED,
    _DELTA_TESTS_PASSED,
    _TRUST_BASE,
    ConsequenceMemory,
    _delta_for_record,
)
from codomyrmex.colony_kernel.models import (
    ActionProposal,
    ConsequenceRecord,
    ResourceCost,
)

if TYPE_CHECKING:
    from pathlib import Path

# ---------------------------------------------------------------------------
# Helpers — build real objects, no stubs
# ---------------------------------------------------------------------------


def _proposal(
    agent_id: str = "agent-a",
    action_type: str = "patch_file",
    target: str = "codomyrmex.git_operations.core",
) -> ActionProposal:
    return ActionProposal(
        agent_id=agent_id,
        agent_type="REPAIR_ANT",
        action_type=action_type,
        target=target,
        rationale="Fix failing test.",
        expected_outcome="All tests green.",
        budget_estimate=ResourceCost(llm_calls=1, runtime_seconds=3.0),
        rollback_plan="git revert HEAD",
        evidence={"test_id": "t1"},
    )


def _success_record(
    agent_id: str = "agent-a",
    action_type: str = "patch_file",
    human_feedback: float = 0.0,
) -> ConsequenceRecord:
    return ConsequenceRecord(
        proposal=_proposal(agent_id=agent_id, action_type=action_type),
        action_taken="Applied patch to git_operations/core.py.",
        actual_outcome="All 42 tests passed; no regressions.",
        tests_passed=True,
        repair_needed=False,
        human_feedback=human_feedback,
    )


def _failure_record(
    agent_id: str = "agent-a",
    action_type: str = "patch_file",
    human_feedback: float = 0.0,
) -> ConsequenceRecord:
    return ConsequenceRecord(
        proposal=_proposal(agent_id=agent_id, action_type=action_type),
        action_taken="Applied patch — but broke downstream module.",
        actual_outcome="3 tests failed after patch.",
        tests_passed=False,
        repair_needed=True,
        human_feedback=human_feedback,
    )


# ---------------------------------------------------------------------------
# Parametrize over both storage backends
# ---------------------------------------------------------------------------


@pytest.fixture(params=["in_memory", "sqlite"])
def memory(request: pytest.FixtureRequest, tmp_path: Path):
    """Parametrized fixture: in-memory and SQLite-backed ConsequenceMemory instances."""
    if request.param == "in_memory":
        mem = ConsequenceMemory(db_path=None)
        yield mem
        # in-memory close is a no-op; call for coverage
        mem.close()
    else:
        db_file = str(tmp_path / "colony.db")
        mem = ConsequenceMemory(db_path=db_file)
        yield mem
        mem.close()


# ---------------------------------------------------------------------------
# Test 1 — record increases accepted count (indirectly via history length)
# ---------------------------------------------------------------------------


def test_record_stored_and_retrievable(memory: ConsequenceMemory) -> None:
    """A recorded consequence is returned by history()."""
    rec = _success_record()
    memory.record(rec)
    results = memory.history("agent-a", limit=10)
    assert len(results) == 1
    assert results[0].consequence_id == rec.consequence_id


def test_multiple_records_all_stored(memory: ConsequenceMemory) -> None:
    """Recording N consequences results in N items in history."""
    count = 5
    records = [_success_record() for _ in range(count)]
    for r in records:
        memory.record(r)
    results = memory.history("agent-a", limit=20)
    assert len(results) == count


def test_record_auto_fills_trust_delta(memory: ConsequenceMemory) -> None:
    """When trust_delta is left at 0.0, record() fills it from outcome fields."""
    rec = _success_record()  # tests_passed=True, repair_needed=False, feedback=0.0
    assert rec.trust_delta == 0.0  # default before recording
    memory.record(rec)
    results = memory.history("agent-a", limit=1)
    stored = results[0]
    expected_delta = _DELTA_TESTS_PASSED  # only tests_passed=True contributes here
    assert abs(stored.trust_delta - expected_delta) < 1e-9


# ---------------------------------------------------------------------------
# Test 2 — multiple successes raise trust_score above baseline
# ---------------------------------------------------------------------------


def test_successes_raise_trust_score(memory: ConsequenceMemory) -> None:
    """Repeated test-passing records push trust above _TRUST_BASE."""
    for _ in range(5):
        memory.record(_success_record())
    score = memory.trust_score("agent-a")
    assert score > _TRUST_BASE


def test_trust_score_reflects_all_successes(memory: ConsequenceMemory) -> None:
    """Trust score increases linearly with test-passing records (within window)."""
    for i in range(3):
        memory.record(_success_record())
    score_3 = memory.trust_score("agent-a")

    for i in range(3):
        memory.record(_success_record())
    score_6 = memory.trust_score("agent-a")

    assert score_6 > score_3


# ---------------------------------------------------------------------------
# Test 3 — failures lower trust_score
# ---------------------------------------------------------------------------


def test_failures_lower_trust_score(memory: ConsequenceMemory) -> None:
    """Repair-needed records reduce trust below _TRUST_BASE."""
    for _ in range(3):
        memory.record(_failure_record())
    score = memory.trust_score("agent-a")
    assert score < _TRUST_BASE


def test_failures_outweigh_successes_when_many(memory: ConsequenceMemory) -> None:
    """Many failures after a few successes drive trust below baseline."""
    # Two successes
    for _ in range(2):
        memory.record(_success_record())
    # Eight failures
    for _ in range(8):
        memory.record(_failure_record())
    score = memory.trust_score("agent-a")
    assert score < _TRUST_BASE


# ---------------------------------------------------------------------------
# Test 4 — trust score clamped to [0.0, 1.0]
# ---------------------------------------------------------------------------


def test_trust_score_never_exceeds_one(memory: ConsequenceMemory) -> None:
    """Accumulating many successes cannot push trust above 1.0."""
    for _ in range(100):
        memory.record(_success_record(human_feedback=0.9))
    score = memory.trust_score("agent-a")
    assert score <= 1.0


def test_trust_score_never_below_zero(memory: ConsequenceMemory) -> None:
    """Accumulating many failures cannot push trust below 0.0."""
    for _ in range(100):
        memory.record(_failure_record(human_feedback=-0.9))
    score = memory.trust_score("agent-a")
    assert score >= 0.0


def test_trust_score_unknown_agent_returns_base(memory: ConsequenceMemory) -> None:
    """Querying an agent with no records returns _TRUST_BASE."""
    score = memory.trust_score("ghost-agent")
    assert score == _TRUST_BASE


# ---------------------------------------------------------------------------
# Test 5 — history() returns ordered records (newest first)
# ---------------------------------------------------------------------------


def test_history_newest_first(memory: ConsequenceMemory) -> None:
    """history() returns records in descending recorded_at order."""
    # Record with artificial timestamps to guarantee ordering
    now = time.time()
    r1 = ConsequenceRecord(
        proposal=_proposal(),
        action_taken="first",
        actual_outcome="ok",
        tests_passed=True,
        recorded_at=now - 10.0,
    )
    r2 = ConsequenceRecord(
        proposal=_proposal(),
        action_taken="second",
        actual_outcome="ok",
        tests_passed=True,
        recorded_at=now - 5.0,
    )
    r3 = ConsequenceRecord(
        proposal=_proposal(),
        action_taken="third",
        actual_outcome="ok",
        tests_passed=True,
        recorded_at=now,
    )
    # Insert in random order
    for r in [r2, r3, r1]:
        memory.record(r)

    results = memory.history("agent-a", limit=10)
    assert len(results) == 3
    timestamps = [r.recorded_at for r in results]
    assert timestamps == sorted(timestamps, reverse=True)


def test_history_limit_respected(memory: ConsequenceMemory) -> None:
    """history() returns at most *limit* records."""
    for _ in range(10):
        memory.record(_success_record())
    results = memory.history("agent-a", limit=3)
    assert len(results) == 3


def test_history_returns_empty_for_unknown_agent(memory: ConsequenceMemory) -> None:
    """history() returns [] for an agent with no records."""
    memory.record(_success_record(agent_id="other-agent"))
    results = memory.history("nobody", limit=10)
    assert results == []


def test_history_isolated_by_agent(memory: ConsequenceMemory) -> None:
    """Records for agent-a do not appear in agent-b's history."""
    memory.record(_success_record(agent_id="agent-a"))
    memory.record(_success_record(agent_id="agent-b"))
    a_hist = memory.history("agent-a", limit=10)
    b_hist = memory.history("agent-b", limit=10)
    assert all(r.proposal.agent_id == "agent-a" for r in a_hist)
    assert all(r.proposal.agent_id == "agent-b" for r in b_hist)


# ---------------------------------------------------------------------------
# Test 6 — pattern_success_rate computed correctly
# ---------------------------------------------------------------------------


def test_pattern_success_rate_all_success(memory: ConsequenceMemory) -> None:
    """All-success records for an action type -> rate == 1.0."""
    for _ in range(4):
        memory.record(_success_record(action_type="run_tests"))
    rate = memory.pattern_success_rate("run_tests")
    assert rate == 1.0


def test_pattern_success_rate_all_failure(memory: ConsequenceMemory) -> None:
    """All-failure records -> rate == 0.0."""
    for _ in range(3):
        memory.record(_failure_record(action_type="archive_module"))
    rate = memory.pattern_success_rate("archive_module")
    assert rate == 0.0


def test_pattern_success_rate_mixed(memory: ConsequenceMemory) -> None:
    """2 successes + 2 failures -> rate == 0.5."""
    for _ in range(2):
        memory.record(_success_record(action_type="patch_and_test"))
    for _ in range(2):
        memory.record(_failure_record(action_type="patch_and_test"))
    rate = memory.pattern_success_rate("patch_and_test")
    assert abs(rate - 0.5) < 1e-9


def test_pattern_success_rate_no_records(memory: ConsequenceMemory) -> None:
    """No records for an action type -> rate == 0.0 (not an error)."""
    rate = memory.pattern_success_rate("nonexistent_action")
    assert rate == 0.0


def test_pattern_success_rate_repair_needed_counts_as_failure(
    memory: ConsequenceMemory,
) -> None:
    """A record with tests_passed=True but repair_needed=True is NOT a success."""
    # Success definition: tests_passed AND NOT repair_needed
    mixed = ConsequenceRecord(
        proposal=_proposal(action_type="tricky_patch"),
        action_taken="Patched but left a loose end.",
        actual_outcome="Tests green but manual cleanup needed.",
        tests_passed=True,
        repair_needed=True,   # disqualifies from 'successful'
    )
    memory.record(mixed)
    rate = memory.pattern_success_rate("tricky_patch")
    assert rate == 0.0


def test_pattern_success_rate_spans_multiple_agents(memory: ConsequenceMemory) -> None:
    """pattern_success_rate aggregates across all agents for the action type."""
    memory.record(_success_record(agent_id="agent-x", action_type="deploy"))
    memory.record(_success_record(agent_id="agent-y", action_type="deploy"))
    memory.record(_failure_record(agent_id="agent-z", action_type="deploy"))
    rate = memory.pattern_success_rate("deploy")
    assert abs(rate - 2 / 3) < 1e-9


# ---------------------------------------------------------------------------
# Test 7 — successful_patterns ordering
# ---------------------------------------------------------------------------


def test_successful_patterns_returns_most_frequent_first(
    memory: ConsequenceMemory,
) -> None:
    """successful_patterns ranks action types by success count descending."""
    # patch_file: 3 successes
    for _ in range(3):
        memory.record(_success_record(action_type="patch_file"))
    # run_tests: 5 successes
    for _ in range(5):
        memory.record(_success_record(action_type="run_tests"))
    patterns = memory.successful_patterns("agent-a")
    assert patterns[0] == "run_tests"
    assert patterns[1] == "patch_file"


def test_successful_patterns_empty_for_unknown_agent(
    memory: ConsequenceMemory,
) -> None:
    """No records -> successful_patterns returns empty list."""
    memory.record(_success_record(agent_id="agent-a"))
    assert memory.successful_patterns("ghost") == []


# ---------------------------------------------------------------------------
# Test 8 — worst_performing_agents / best_performing_agents
# ---------------------------------------------------------------------------


def test_worst_and_best_performing_agents(memory: ConsequenceMemory) -> None:
    """Agents are ranked correctly by trust score in both directions."""
    # Good agent: 5 successes
    for _ in range(5):
        memory.record(_success_record(agent_id="good-agent"))
    # Bad agent: 5 failures
    for _ in range(5):
        memory.record(_failure_record(agent_id="bad-agent"))

    worst = memory.worst_performing_agents(k=1)
    best = memory.best_performing_agents(k=1)

    assert len(worst) == 1
    assert len(best) == 1
    worst_id, worst_score = worst[0]
    best_id, best_score = best[0]

    assert worst_id == "bad-agent"
    assert best_id == "good-agent"
    assert worst_score < best_score


# ---------------------------------------------------------------------------
# Test 9 — _delta_for_record unit tests (pure function)
# ---------------------------------------------------------------------------


def test_delta_tests_passed_only() -> None:
    rec = ConsequenceRecord(
        proposal=_proposal(),
        action_taken="done",
        actual_outcome="ok",
        tests_passed=True,
        repair_needed=False,
        human_feedback=0.0,
    )
    assert _delta_for_record(rec) == pytest.approx(_DELTA_TESTS_PASSED)


def test_delta_repair_needed_only() -> None:
    rec = ConsequenceRecord(
        proposal=_proposal(),
        action_taken="done",
        actual_outcome="partial",
        tests_passed=False,
        repair_needed=True,
        human_feedback=0.0,
    )
    assert _delta_for_record(rec) == pytest.approx(_DELTA_REPAIR_NEEDED)


def test_delta_feedback_accepted() -> None:
    rec = ConsequenceRecord(
        proposal=_proposal(),
        action_taken="done",
        actual_outcome="ok",
        tests_passed=False,
        repair_needed=False,
        human_feedback=0.8,
    )
    assert _delta_for_record(rec) == pytest.approx(_DELTA_FEEDBACK_ACCEPTED)


def test_delta_feedback_rejected() -> None:
    rec = ConsequenceRecord(
        proposal=_proposal(),
        action_taken="done",
        actual_outcome="bad",
        tests_passed=False,
        repair_needed=False,
        human_feedback=-0.9,
    )
    assert _delta_for_record(rec) == pytest.approx(_DELTA_FEEDBACK_REJECTED)


def test_delta_all_positive_additive() -> None:
    """tests_passed + positive human_feedback sum correctly."""
    rec = ConsequenceRecord(
        proposal=_proposal(),
        action_taken="done",
        actual_outcome="great",
        tests_passed=True,
        repair_needed=False,
        human_feedback=0.7,
    )
    expected = _DELTA_TESTS_PASSED + _DELTA_FEEDBACK_ACCEPTED
    assert _delta_for_record(rec) == pytest.approx(expected)


def test_delta_all_negative_additive() -> None:
    """repair_needed + rejected human_feedback sum correctly."""
    rec = ConsequenceRecord(
        proposal=_proposal(),
        action_taken="done",
        actual_outcome="disaster",
        tests_passed=False,
        repair_needed=True,
        human_feedback=-0.9,
    )
    expected = _DELTA_REPAIR_NEEDED + _DELTA_FEEDBACK_REJECTED
    assert _delta_for_record(rec) == pytest.approx(expected)


def test_delta_neutral_feedback_ignored() -> None:
    """human_feedback in (-0.5, 0.5) contributes 0 delta."""
    rec = ConsequenceRecord(
        proposal=_proposal(),
        action_taken="done",
        actual_outcome="ok",
        tests_passed=False,
        repair_needed=False,
        human_feedback=0.0,
    )
    assert _delta_for_record(rec) == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# Test 10 — ConsequenceMemory context manager / close
# ---------------------------------------------------------------------------


def test_context_manager_closes_cleanly(tmp_path: Path) -> None:
    """Using ConsequenceMemory as a context manager does not raise on exit."""
    db_path = str(tmp_path / "test_cm.db")
    with ConsequenceMemory(db_path=db_path) as mem:
        mem.record(_success_record())
        results = mem.history("agent-a", limit=5)
        assert len(results) == 1


def test_in_memory_close_is_noop() -> None:
    """Calling close() on an in-memory instance does not raise."""
    mem = ConsequenceMemory(db_path=None)
    mem.record(_success_record())
    mem.close()  # must not raise


# ---------------------------------------------------------------------------
# Test 11 — SQLite persistence across instances
# ---------------------------------------------------------------------------


def test_sqlite_data_persists_across_instances(tmp_path: Path) -> None:
    """Records written by one ConsequenceMemory instance are readable by another."""
    db_path = str(tmp_path / "persist.db")

    with ConsequenceMemory(db_path=db_path) as mem1:
        mem1.record(_success_record(agent_id="persisted-agent"))

    with ConsequenceMemory(db_path=db_path) as mem2:
        results = mem2.history("persisted-agent", limit=5)
        assert len(results) == 1
        assert results[0].proposal.agent_id == "persisted-agent"


def test_sqlite_trust_score_consistent_across_instances(tmp_path: Path) -> None:
    """Trust score computed by a fresh instance matches the original session."""
    db_path = str(tmp_path / "trust.db")

    with ConsequenceMemory(db_path=db_path) as mem1:
        for _ in range(4):
            mem1.record(_success_record(agent_id="stable-agent"))
        score_original = mem1.trust_score("stable-agent")

    with ConsequenceMemory(db_path=db_path) as mem2:
        score_reload = mem2.trust_score("stable-agent")

    assert abs(score_original - score_reload) < 1e-9
