"""Unit tests for PheromoneStore.

Zero-mock policy: no unittest.mock, MagicMock, or pytest-mock.
All tests use real ColonySignal objects and verify actual state mutations.
"""

from __future__ import annotations

import pytest

from codomyrmex.colony_kernel.models import (
    ColonySignal,
    DecayRate,
    SignalSource,
    SignalType,
)
from codomyrmex.colony_kernel.pheromone_store import PheromoneStore

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def store() -> PheromoneStore:
    """Fresh PheromoneStore for each test."""
    return PheromoneStore()


def _signal(
    location: str,
    signal_type: SignalType = SignalType.FAILURE,
    strength: float = 1.0,
    decay_rate: DecayRate = DecayRate.NORMAL,
    source: SignalSource = SignalSource.TEST,
    evidence: dict | None = None,
) -> ColonySignal:
    """Helper to build a ColonySignal with defaults."""
    return ColonySignal(
        location=location,
        signal_type=signal_type,
        strength=strength,
        decay_rate=decay_rate,
        source=source,
        evidence=evidence or {},
    )


# ---------------------------------------------------------------------------
# deposit_signal
# ---------------------------------------------------------------------------


class TestDepositSignal:
    def test_deposit_creates_signal_retrievable_by_query(
        self, store: PheromoneStore
    ) -> None:
        sig = _signal(
            "codomyrmex.git_operations.core", SignalType.FAILURE, strength=2.5
        )
        store.deposit_signal(sig)

        results = store.query_pressure(
            "codomyrmex.git_operations.core", SignalType.FAILURE
        )

        assert len(results) == 1
        result = results[0]
        assert result.location == "codomyrmex.git_operations.core"
        assert result.signal_type == SignalType.FAILURE
        assert result.strength == pytest.approx(2.5)

    def test_deposit_preserves_source(self, store: PheromoneStore) -> None:
        sig = _signal("mod.a", SignalType.SUCCESS, source=SignalSource.HUMAN)
        store.deposit_signal(sig)

        results = store.query_pressure("mod.a", SignalType.SUCCESS)

        assert results[0].source == SignalSource.HUMAN

    def test_deposit_preserves_decay_rate(self, store: PheromoneStore) -> None:
        sig = _signal("mod.b", decay_rate=DecayRate.SLOW)
        store.deposit_signal(sig)

        results = store.query_pressure("mod.b")

        assert results[0].decay_rate == DecayRate.SLOW

    def test_deposit_preserves_evidence(self, store: PheromoneStore) -> None:
        evidence = {"test_id": "test_push_fails", "run": 42}
        sig = _signal("mod.c", evidence=evidence)
        store.deposit_signal(sig)

        results = store.query_pressure("mod.c")

        assert results[0].evidence["test_id"] == "test_push_fails"
        assert results[0].evidence["run"] == 42

    def test_deposit_twice_accumulates_strength(self, store: PheromoneStore) -> None:
        """Depositing the same (type, location) key twice adds strength."""
        store.deposit_signal(_signal("mod.d", strength=1.0))
        store.deposit_signal(_signal("mod.d", strength=2.0))

        results = store.query_pressure("mod.d")

        assert results[0].strength == pytest.approx(3.0)

    def test_deposit_different_types_at_same_location_are_distinct(
        self, store: PheromoneStore
    ) -> None:
        store.deposit_signal(_signal("mod.e", SignalType.FAILURE, strength=1.0))
        store.deposit_signal(_signal("mod.e", SignalType.SUCCESS, strength=5.0))

        failures = store.query_pressure("mod.e", SignalType.FAILURE)
        successes = store.query_pressure("mod.e", SignalType.SUCCESS)

        assert len(failures) == 1
        assert len(successes) == 1
        assert failures[0].strength == pytest.approx(1.0)
        assert successes[0].strength == pytest.approx(5.0)

    def test_deposit_registers_key_evaporation_rate_fast(
        self, store: PheromoneStore
    ) -> None:
        """FAST decay key should be stored in _key_evaporation at 0.30."""
        sig = _signal("mod.fast", decay_rate=DecayRate.FAST)
        store.deposit_signal(sig)

        # Canonical key format: "{location}:{signal_type}" (location first)
        key = "mod.fast:failure"
        assert key in store._key_evaporation
        assert store._key_evaporation[key] == pytest.approx(0.30)

    def test_deposit_registers_key_evaporation_rate_slow(
        self, store: PheromoneStore
    ) -> None:
        """SLOW decay key should be stored in _key_evaporation at 0.02."""
        sig = _signal("mod.slow", decay_rate=DecayRate.SLOW)
        store.deposit_signal(sig)

        # Canonical key format: "{location}:{signal_type}" (location first)
        key = "mod.slow:failure"
        assert store._key_evaporation[key] == pytest.approx(0.02)


# ---------------------------------------------------------------------------
# reinforce_path
# ---------------------------------------------------------------------------


class TestReinforcePath:
    def test_reinforce_increases_strength(self, store: PheromoneStore) -> None:
        store.deposit_signal(_signal("pkg.x", SignalType.DEPENDENCY, strength=1.0))
        before = store.query_pressure("pkg.x", SignalType.DEPENDENCY)[0].strength

        store.reinforce_path("pkg.x", SignalType.DEPENDENCY)

        after = store.query_pressure("pkg.x", SignalType.DEPENDENCY)[0].strength
        assert after > before

    def test_reinforce_increases_by_default_delta(self, store: PheromoneStore) -> None:
        """Default reinforce_on_read_delta is 0.15 (StigmergyConfig default)."""
        store.deposit_signal(_signal("pkg.y", strength=2.0))
        store.reinforce_path("pkg.y", SignalType.FAILURE)

        results = store.query_pressure("pkg.y", SignalType.FAILURE)
        assert results[0].strength == pytest.approx(2.15)

    def test_reinforce_nonexistent_key_is_noop(self, store: PheromoneStore) -> None:
        """reinforce_path on a missing key must not raise and leave store empty."""
        store.reinforce_path("pkg.nonexistent", SignalType.FAILURE)

        assert len(store._field) == 0

    def test_reinforce_does_not_affect_other_signal_types_at_same_location(
        self, store: PheromoneStore
    ) -> None:
        store.deposit_signal(_signal("pkg.z", SignalType.FAILURE, strength=1.0))
        store.deposit_signal(_signal("pkg.z", SignalType.SUCCESS, strength=1.0))

        store.reinforce_path("pkg.z", SignalType.FAILURE)

        failures = store.query_pressure("pkg.z", SignalType.FAILURE)[0].strength
        successes = store.query_pressure("pkg.z", SignalType.SUCCESS)[0].strength

        assert failures == pytest.approx(1.15)
        assert successes == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# evaporate
# ---------------------------------------------------------------------------


class TestEvaporate:
    def test_evaporate_decreases_strength(self, store: PheromoneStore) -> None:
        store.deposit_signal(
            _signal("loc.a", strength=5.0, decay_rate=DecayRate.NORMAL)
        )
        store.evaporate()

        results = store.query_pressure("loc.a")
        assert results[0].strength == pytest.approx(5.0 - 0.10)

    def test_evaporate_fast_signal_decreases_more(self, store: PheromoneStore) -> None:
        store.deposit_signal(
            _signal("loc.fast", strength=5.0, decay_rate=DecayRate.FAST)
        )
        store.evaporate()

        results = store.query_pressure("loc.fast")
        assert results[0].strength == pytest.approx(5.0 - 0.30)

    def test_evaporate_slow_signal_decreases_less(self, store: PheromoneStore) -> None:
        store.deposit_signal(
            _signal("loc.slow", strength=5.0, decay_rate=DecayRate.SLOW)
        )
        store.evaporate()

        results = store.query_pressure("loc.slow")
        assert results[0].strength == pytest.approx(5.0 - 0.02)

    def test_evaporate_removes_signal_at_or_below_zero(
        self, store: PheromoneStore
    ) -> None:
        """A signal with strength exactly equal to one tick of NORMAL decay is pruned."""
        store.deposit_signal(
            _signal("loc.b", strength=0.10, decay_rate=DecayRate.NORMAL)
        )
        store.evaporate()

        results = store.query_pressure("loc.b")
        assert len(results) == 0

    def test_evaporate_removes_key_from_evaporation_map(
        self, store: PheromoneStore
    ) -> None:
        store.deposit_signal(
            _signal("loc.c", strength=0.10, decay_rate=DecayRate.NORMAL)
        )
        # Canonical key format: "{location}:{signal_type}" (location first)
        key = "loc.c:failure"
        assert key in store._key_evaporation

        store.evaporate()

        assert key not in store._key_evaporation

    def test_evaporate_multiple_ticks_converges_to_zero(
        self, store: PheromoneStore
    ) -> None:
        """After enough ticks, every signal is pruned."""
        store.deposit_signal(
            _signal("loc.d", strength=1.0, decay_rate=DecayRate.NORMAL)
        )

        for _ in range(15):
            store.evaporate()

        assert len(store._field) == 0

    def test_evaporate_leaves_strong_signal_alive(self, store: PheromoneStore) -> None:
        store.deposit_signal(
            _signal("loc.e", strength=10.0, decay_rate=DecayRate.NORMAL)
        )
        store.evaporate()

        results = store.query_pressure("loc.e")
        assert len(results) == 1

    def test_evaporate_applies_different_rates_to_different_keys(
        self, store: PheromoneStore
    ) -> None:
        store.deposit_signal(
            _signal(
                "loc.f", SignalType.FAILURE, strength=2.0, decay_rate=DecayRate.FAST
            )
        )
        store.deposit_signal(
            _signal(
                "loc.f", SignalType.SUCCESS, strength=2.0, decay_rate=DecayRate.SLOW
            )
        )

        store.evaporate()

        fast = store.query_pressure("loc.f", SignalType.FAILURE)[0].strength
        slow = store.query_pressure("loc.f", SignalType.SUCCESS)[0].strength

        assert fast == pytest.approx(2.0 - 0.30)
        assert slow == pytest.approx(2.0 - 0.02)
        assert fast < slow


# ---------------------------------------------------------------------------
# query_pressure
# ---------------------------------------------------------------------------


class TestQueryPressure:
    def test_query_pressure_exact_location_match(self, store: PheromoneStore) -> None:
        store.deposit_signal(_signal("pkg.core", strength=3.0))
        results = store.query_pressure("pkg.core")
        assert len(results) == 1
        assert results[0].location == "pkg.core"

    def test_query_pressure_prefix_match_returns_children(
        self, store: PheromoneStore
    ) -> None:
        store.deposit_signal(_signal("pkg.core"))
        store.deposit_signal(_signal("pkg.core.utils"))
        store.deposit_signal(_signal("pkg.core.models"))

        results = store.query_pressure("pkg.core")

        locations = {r.location for r in results}
        assert "pkg.core" in locations
        assert "pkg.core.utils" in locations
        assert "pkg.core.models" in locations

    def test_query_pressure_does_not_return_sibling_prefix(
        self, store: PheromoneStore
    ) -> None:
        """'pkg.coreutils' must not be returned when querying 'pkg.core'."""
        store.deposit_signal(_signal("pkg.core"))
        store.deposit_signal(_signal("pkg.coreutils"))

        results = store.query_pressure("pkg.core")

        locations = {r.location for r in results}
        assert "pkg.coreutils" not in locations

    def test_query_pressure_filters_by_signal_type(self, store: PheromoneStore) -> None:
        store.deposit_signal(_signal("mod.q", SignalType.FAILURE, strength=1.0))
        store.deposit_signal(_signal("mod.q", SignalType.SUCCESS, strength=2.0))

        failures = store.query_pressure("mod.q", SignalType.FAILURE)
        successes = store.query_pressure("mod.q", SignalType.SUCCESS)

        assert len(failures) == 1
        assert failures[0].signal_type == SignalType.FAILURE
        assert len(successes) == 1
        assert successes[0].signal_type == SignalType.SUCCESS

    def test_query_pressure_returns_sorted_by_descending_strength(
        self, store: PheromoneStore
    ) -> None:
        store.deposit_signal(_signal("grp.a", SignalType.FAILURE, strength=1.0))
        store.deposit_signal(_signal("grp.b", SignalType.FAILURE, strength=5.0))
        store.deposit_signal(_signal("grp.c", SignalType.FAILURE, strength=3.0))

        results = store.query_pressure("grp", SignalType.FAILURE)

        strengths = [r.strength for r in results]
        assert strengths == sorted(strengths, reverse=True)

    def test_query_pressure_returns_empty_for_unknown_location(
        self, store: PheromoneStore
    ) -> None:
        results = store.query_pressure("pkg.nonexistent")
        assert results == []

    def test_query_pressure_no_type_filter_returns_all_types(
        self, store: PheromoneStore
    ) -> None:
        store.deposit_signal(_signal("ns.x", SignalType.FAILURE))
        store.deposit_signal(_signal("ns.x", SignalType.SUCCESS))
        store.deposit_signal(_signal("ns.x", SignalType.RISK))

        results = store.query_pressure("ns.x")

        signal_types = {r.signal_type for r in results}
        assert SignalType.FAILURE in signal_types
        assert SignalType.SUCCESS in signal_types
        assert SignalType.RISK in signal_types

    def test_query_pressure_path_separator_slash_also_matches(
        self, store: PheromoneStore
    ) -> None:
        """Slash-based paths (file paths) should be prefix-matched via '/'."""
        store.deposit_signal(_signal("src/codomyrmex/core.py"))
        store.deposit_signal(_signal("src/codomyrmex/models.py"))

        results = store.query_pressure("src/codomyrmex")

        locations = {r.location for r in results}
        assert "src/codomyrmex/core.py" in locations
        assert "src/codomyrmex/models.py" in locations


# ---------------------------------------------------------------------------
# top_pressure
# ---------------------------------------------------------------------------


class TestTopPressure:
    def test_top_pressure_returns_highest_strength_first(
        self, store: PheromoneStore
    ) -> None:
        store.deposit_signal(_signal("a.a", strength=1.0))
        store.deposit_signal(_signal("a.b", strength=9.5))
        store.deposit_signal(_signal("a.c", strength=3.0))

        top = store.top_pressure(k=3)

        assert top[0].strength == pytest.approx(9.5)
        assert top[1].strength == pytest.approx(3.0)
        assert top[2].strength == pytest.approx(1.0)

    def test_top_pressure_respects_k_limit(self, store: PheromoneStore) -> None:
        for i in range(10):
            store.deposit_signal(_signal(f"b.{i}", strength=float(i + 1)))

        top = store.top_pressure(k=3)

        assert len(top) == 3

    def test_top_pressure_k_larger_than_count_returns_all(
        self, store: PheromoneStore
    ) -> None:
        store.deposit_signal(_signal("c.x", strength=2.0))
        store.deposit_signal(_signal("c.y", strength=1.0))

        top = store.top_pressure(k=100)

        assert len(top) == 2

    def test_top_pressure_returns_empty_on_empty_store(
        self, store: PheromoneStore
    ) -> None:
        top = store.top_pressure(k=10)
        assert top == []

    def test_top_pressure_returns_correct_signal_type_metadata(
        self, store: PheromoneStore
    ) -> None:
        store.deposit_signal(
            _signal(
                "d.mod",
                SignalType.HUMAN_PRIORITY,
                strength=8.0,
                source=SignalSource.HUMAN,
            )
        )
        store.deposit_signal(_signal("d.mod", SignalType.FAILURE, strength=1.0))

        top = store.top_pressure(k=1)

        assert top[0].signal_type == SignalType.HUMAN_PRIORITY
        assert top[0].source == SignalSource.HUMAN

    def test_top_pressure_reflects_state_after_evaporation(
        self, store: PheromoneStore
    ) -> None:
        """After evaporation the strongest signal should change accordingly."""
        store.deposit_signal(_signal("e.fast", strength=1.0, decay_rate=DecayRate.FAST))
        store.deposit_signal(_signal("e.slow", strength=1.0, decay_rate=DecayRate.SLOW))

        store.evaporate()

        top = store.top_pressure(k=2)
        assert top[0].location == "e.slow"


# ---------------------------------------------------------------------------
# summary
# ---------------------------------------------------------------------------


class TestSummary:
    def test_summary_total_signals(self, store: PheromoneStore) -> None:
        store.deposit_signal(_signal("s.a"))
        store.deposit_signal(_signal("s.b", SignalType.SUCCESS))

        summary = store.summary()

        assert summary["total_signals"] == 2

    def test_summary_empty_store(self, store: PheromoneStore) -> None:
        summary = store.summary()

        assert summary["total_signals"] == 0
        assert summary["max_strength"] == 0.0
        assert summary["min_strength"] == 0.0
        assert summary["mean_strength"] == 0.0

    def test_summary_by_signal_type_counts(self, store: PheromoneStore) -> None:
        store.deposit_signal(_signal("s.c", SignalType.FAILURE))
        store.deposit_signal(_signal("s.d", SignalType.FAILURE))
        store.deposit_signal(_signal("s.e", SignalType.SUCCESS))

        summary = store.summary()

        assert summary["by_signal_type"]["failure"] == 2
        assert summary["by_signal_type"]["success"] == 1

    def test_summary_mean_strength(self, store: PheromoneStore) -> None:
        store.deposit_signal(_signal("s.f", strength=2.0))
        store.deposit_signal(_signal("s.g", strength=4.0))

        summary = store.summary()

        assert summary["mean_strength"] == pytest.approx(3.0)
