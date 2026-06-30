"""Unit tests for ResourceLedger and ResourceBudget.

Zero-mock policy: no unittest.mock, MagicMock, or pytest-mock.
All tests use real ResourceCost values and verify actual arithmetic.
"""

from __future__ import annotations

import pytest

from codomyrmex.colony_kernel.models import ResourceCost
from codomyrmex.colony_kernel.resource_ledger import ResourceBudget, ResourceLedger

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def ledger() -> ResourceLedger:
    """Fresh ResourceLedger with default budget for each test."""
    return ResourceLedger()


@pytest.fixture
def tight_budget() -> ResourceBudget:
    """A budget with very low caps to trigger violations easily."""
    return ResourceBudget(
        max_llm_calls_per_hour=5,
        max_runtime_seconds=10.0,
        max_risk_level=0.3,
        max_human_attention_minutes=5.0,
        max_merge_risk=0.2,
        total_doc_debt_allowed=1.0,
        max_security_exposure=0.1,
    )


def _cost(
    llm_calls: int = 0,
    runtime_seconds: float = 0.0,
    risk_level: float = 0.0,
    human_attention_minutes: float = 0.0,
    merge_risk: float = 0.0,
    doc_debt: float = 0.0,
    security_exposure: float = 0.0,
) -> ResourceCost:
    return ResourceCost(
        llm_calls=llm_calls,
        runtime_seconds=runtime_seconds,
        risk_level=risk_level,
        human_attention_minutes=human_attention_minutes,
        merge_risk=merge_risk,
        doc_debt=doc_debt,
        security_exposure=security_exposure,
    )


# ---------------------------------------------------------------------------
# can_afford — affordable cases
# ---------------------------------------------------------------------------


class TestCanAffordAffordable:
    def test_zero_cost_is_always_affordable(self, ledger: ResourceLedger) -> None:
        ok, reason = ledger.can_afford(_cost())
        assert ok is True
        assert reason is None

    def test_small_llm_calls_under_budget(self, ledger: ResourceLedger) -> None:
        ok, reason = ledger.can_afford(_cost(llm_calls=1))
        assert ok is True
        assert reason is None

    def test_accumulated_plus_new_still_under_budget(self, ledger: ResourceLedger) -> None:
        ledger.record_cost(_cost(llm_calls=50), agent_id="agent-a")
        ok, reason = ledger.can_afford(_cost(llm_calls=49))
        assert ok is True
        assert reason is None

    def test_all_dimensions_near_limit_is_affordable(self) -> None:
        budget = ResourceBudget(
            max_llm_calls_per_hour=10,
            max_runtime_seconds=100.0,
            max_risk_level=0.5,
            max_human_attention_minutes=20.0,
            max_merge_risk=0.4,
            total_doc_debt_allowed=5.0,
            max_security_exposure=0.3,
        )
        ledger = ResourceLedger(budget=budget)
        cost = _cost(
            llm_calls=10,
            runtime_seconds=100.0,
            risk_level=0.5,
            human_attention_minutes=20.0,
            merge_risk=0.4,
            doc_debt=5.0,
            security_exposure=0.3,
        )
        ok, reason = ledger.can_afford(cost)
        assert ok is True
        assert reason is None


# ---------------------------------------------------------------------------
# can_afford — budget exceeded cases
# ---------------------------------------------------------------------------


class TestCanAffordExceeded:
    def test_llm_calls_exceeded(self, tight_budget: ResourceBudget) -> None:
        ledger = ResourceLedger(budget=tight_budget)
        ok, reason = ledger.can_afford(_cost(llm_calls=6))
        assert ok is False
        assert reason is not None
        assert "llm_calls" in reason

    def test_runtime_seconds_exceeded(self, tight_budget: ResourceBudget) -> None:
        ledger = ResourceLedger(budget=tight_budget)
        ok, reason = ledger.can_afford(_cost(runtime_seconds=11.0))
        assert ok is False
        assert reason is not None
        assert "runtime_seconds" in reason

    def test_risk_level_exceeded(self, tight_budget: ResourceBudget) -> None:
        ledger = ResourceLedger(budget=tight_budget)
        ok, reason = ledger.can_afford(_cost(risk_level=0.31))
        assert ok is False
        assert reason is not None
        assert "risk_level" in reason

    def test_human_attention_minutes_exceeded(self, tight_budget: ResourceBudget) -> None:
        ledger = ResourceLedger(budget=tight_budget)
        ok, reason = ledger.can_afford(_cost(human_attention_minutes=6.0))
        assert ok is False
        assert reason is not None
        assert "human_attention_minutes" in reason

    def test_merge_risk_exceeded(self, tight_budget: ResourceBudget) -> None:
        ledger = ResourceLedger(budget=tight_budget)
        ok, reason = ledger.can_afford(_cost(merge_risk=0.21))
        assert ok is False
        assert reason is not None
        assert "merge_risk" in reason

    def test_doc_debt_exceeded(self, tight_budget: ResourceBudget) -> None:
        ledger = ResourceLedger(budget=tight_budget)
        ok, reason = ledger.can_afford(_cost(doc_debt=1.01))
        assert ok is False
        assert reason is not None
        assert "doc_debt" in reason

    def test_security_exposure_exceeded(self, tight_budget: ResourceBudget) -> None:
        ledger = ResourceLedger(budget=tight_budget)
        ok, reason = ledger.can_afford(_cost(security_exposure=0.11))
        assert ok is False
        assert reason is not None
        assert "security_exposure" in reason

    def test_accumulated_cost_pushes_over_budget(self, tight_budget: ResourceBudget) -> None:
        """Accumulated spend of 3 + new cost of 3 = 6 > max 5."""
        ledger = ResourceLedger(budget=tight_budget)
        ledger.record_cost(_cost(llm_calls=3), agent_id="agent-a")

        ok, reason = ledger.can_afford(_cost(llm_calls=3))

        assert ok is False
        assert reason is not None
        assert "llm_calls" in reason

    def test_reason_string_includes_projected_and_cap_values(
        self, tight_budget: ResourceBudget
    ) -> None:
        ledger = ResourceLedger(budget=tight_budget)
        ok, reason = ledger.can_afford(_cost(llm_calls=10))

        assert ok is False
        assert reason is not None
        assert "10" in reason
        assert "5" in reason


# ---------------------------------------------------------------------------
# record_cost
# ---------------------------------------------------------------------------


class TestRecordCost:
    def test_record_cost_empty_agent_id_raises(self, ledger: ResourceLedger) -> None:
        with pytest.raises(ValueError, match="agent_id"):
            ledger.record_cost(_cost(llm_calls=1), agent_id="")

    def test_record_cost_accumulates_llm_calls(self, ledger: ResourceLedger) -> None:
        ledger.record_cost(_cost(llm_calls=3), agent_id="a")
        ledger.record_cost(_cost(llm_calls=7), agent_id="a")

        usage = ledger.current_usage()
        assert usage.llm_calls == 10

    def test_record_cost_accumulates_runtime_seconds(self, ledger: ResourceLedger) -> None:
        ledger.record_cost(_cost(runtime_seconds=1.5), agent_id="a")
        ledger.record_cost(_cost(runtime_seconds=2.5), agent_id="a")

        usage = ledger.current_usage()
        assert usage.runtime_seconds == pytest.approx(4.0)

    def test_record_cost_accumulates_human_attention(self, ledger: ResourceLedger) -> None:
        ledger.record_cost(_cost(human_attention_minutes=5.0), agent_id="a")
        ledger.record_cost(_cost(human_attention_minutes=3.0), agent_id="a")

        usage = ledger.current_usage()
        assert usage.human_attention_minutes == pytest.approx(8.0)

    def test_record_cost_accumulates_doc_debt(self, ledger: ResourceLedger) -> None:
        ledger.record_cost(_cost(doc_debt=10.0), agent_id="a")
        ledger.record_cost(_cost(doc_debt=5.5), agent_id="a")

        usage = ledger.current_usage()
        assert usage.doc_debt == pytest.approx(15.5)

    def test_record_cost_risk_level_clamped_at_one(self, ledger: ResourceLedger) -> None:
        ledger.record_cost(_cost(risk_level=0.7), agent_id="a")
        ledger.record_cost(_cost(risk_level=0.8), agent_id="a")

        usage = ledger.current_usage()
        assert usage.risk_level == pytest.approx(1.0)

    def test_record_cost_appends_to_history(self, ledger: ResourceLedger) -> None:
        ledger.record_cost(_cost(llm_calls=1), agent_id="agent-x")
        ledger.record_cost(_cost(llm_calls=2), agent_id="agent-y")

        history = ledger.history()
        assert len(history) == 2

    def test_record_cost_history_entries_have_correct_agent_id(
        self, ledger: ResourceLedger
    ) -> None:
        ledger.record_cost(_cost(llm_calls=1), agent_id="agent-x")
        ledger.record_cost(_cost(llm_calls=2), agent_id="agent-y")

        history = ledger.history()
        assert history[0][0] == "agent-x"
        assert history[1][0] == "agent-y"

    def test_record_cost_history_entries_have_timestamp(self, ledger: ResourceLedger) -> None:
        import time as _time

        before = _time.time()
        ledger.record_cost(_cost(llm_calls=1), agent_id="a")
        after = _time.time()

        history = ledger.history()
        ts = history[0][2]
        assert before <= ts <= after

    def test_reset_clears_accumulated_but_preserves_history(
        self, ledger: ResourceLedger
    ) -> None:
        ledger.record_cost(_cost(llm_calls=5), agent_id="a")
        ledger.reset("hourly")

        assert ledger.current_usage().llm_calls == 0
        assert len(ledger.history()) == 1

    def test_can_afford_reflects_accumulated_after_reset(
        self, tight_budget: ResourceBudget
    ) -> None:
        """After reset, the budget window clears and previously exhausted cap is open again."""
        ledger = ResourceLedger(budget=tight_budget)
        ledger.record_cost(_cost(llm_calls=5), agent_id="a")

        ok_before, _ = ledger.can_afford(_cost(llm_calls=1))
        assert ok_before is False

        ledger.reset()

        ok_after, reason_after = ledger.can_afford(_cost(llm_calls=1))
        assert ok_after is True
        assert reason_after is None


# ---------------------------------------------------------------------------
# agent_spend
# ---------------------------------------------------------------------------


class TestAgentSpend:
    def test_agent_spend_zero_for_unknown_agent(self, ledger: ResourceLedger) -> None:
        spend = ledger.agent_spend("unknown-agent")
        assert spend.llm_calls == 0
        assert spend.runtime_seconds == 0.0

    def test_agent_spend_tracks_single_agent(self, ledger: ResourceLedger) -> None:
        ledger.record_cost(_cost(llm_calls=3), agent_id="bot-1")
        ledger.record_cost(_cost(llm_calls=7), agent_id="bot-1")

        spend = ledger.agent_spend("bot-1")
        assert spend.llm_calls == 10

    def test_agent_spend_isolates_agents(self, ledger: ResourceLedger) -> None:
        ledger.record_cost(_cost(llm_calls=5), agent_id="bot-1")
        ledger.record_cost(_cost(llm_calls=3), agent_id="bot-2")

        assert ledger.agent_spend("bot-1").llm_calls == 5
        assert ledger.agent_spend("bot-2").llm_calls == 3

    def test_agent_spend_sums_all_dimensions(self, ledger: ResourceLedger) -> None:
        ledger.record_cost(
            _cost(llm_calls=2, runtime_seconds=5.0, human_attention_minutes=1.0),
            agent_id="bot-3",
        )
        ledger.record_cost(
            _cost(llm_calls=1, runtime_seconds=3.0, human_attention_minutes=2.0),
            agent_id="bot-3",
        )

        spend = ledger.agent_spend("bot-3")
        assert spend.llm_calls == 3
        assert spend.runtime_seconds == pytest.approx(8.0)
        assert spend.human_attention_minutes == pytest.approx(3.0)

    def test_agent_spend_spans_across_resets(self, ledger: ResourceLedger) -> None:
        """History persists across reset; agent_spend uses full history."""
        ledger.record_cost(_cost(llm_calls=4), agent_id="bot-4")
        ledger.reset()
        ledger.record_cost(_cost(llm_calls=2), agent_id="bot-4")

        spend = ledger.agent_spend("bot-4")
        assert spend.llm_calls == 6


# ---------------------------------------------------------------------------
# most_expensive_agents
# ---------------------------------------------------------------------------


class TestMostExpensiveAgents:
    def test_most_expensive_agents_empty_ledger(self, ledger: ResourceLedger) -> None:
        ranked = ledger.most_expensive_agents(k=5)
        assert ranked == []

    def test_most_expensive_agents_ranked_by_llm_calls(self, ledger: ResourceLedger) -> None:
        ledger.record_cost(_cost(llm_calls=1), agent_id="cheap")
        ledger.record_cost(_cost(llm_calls=10), agent_id="expensive")
        ledger.record_cost(_cost(llm_calls=5), agent_id="medium")

        ranked = ledger.most_expensive_agents(k=3)

        assert ranked[0][0] == "expensive"
        assert ranked[1][0] == "medium"
        assert ranked[2][0] == "cheap"

    def test_most_expensive_agents_secondary_sort_by_human_attention(
        self, ledger: ResourceLedger
    ) -> None:
        """Two agents with equal LLM calls; more human_attention ranks higher."""
        ledger.record_cost(_cost(llm_calls=5, human_attention_minutes=1.0), agent_id="low-attn")
        ledger.record_cost(_cost(llm_calls=5, human_attention_minutes=9.0), agent_id="high-attn")

        ranked = ledger.most_expensive_agents(k=2)

        assert ranked[0][0] == "high-attn"
        assert ranked[1][0] == "low-attn"

    def test_most_expensive_agents_k_clamps_to_agent_count(
        self, ledger: ResourceLedger
    ) -> None:
        ledger.record_cost(_cost(llm_calls=1), agent_id="only-agent")

        ranked = ledger.most_expensive_agents(k=100)

        assert len(ranked) == 1

    def test_most_expensive_agents_returns_aggregated_totals(
        self, ledger: ResourceLedger
    ) -> None:
        ledger.record_cost(_cost(llm_calls=3), agent_id="bot")
        ledger.record_cost(_cost(llm_calls=4), agent_id="bot")

        ranked = ledger.most_expensive_agents(k=1)

        assert ranked[0][0] == "bot"
        assert ranked[0][1].llm_calls == 7

    def test_most_expensive_agents_returns_k_results(self, ledger: ResourceLedger) -> None:
        for i in range(10):
            ledger.record_cost(_cost(llm_calls=i + 1), agent_id=f"bot-{i}")

        ranked = ledger.most_expensive_agents(k=3)

        assert len(ranked) == 3

    def test_most_expensive_agents_result_is_most_expensive_first(
        self, ledger: ResourceLedger
    ) -> None:
        ledger.record_cost(_cost(llm_calls=1), agent_id="bot-a")
        ledger.record_cost(_cost(llm_calls=20), agent_id="bot-b")
        ledger.record_cost(_cost(llm_calls=10), agent_id="bot-c")

        ranked = ledger.most_expensive_agents(k=2)

        assert ranked[0][0] == "bot-b"
        assert ranked[1][0] == "bot-c"

    def test_most_expensive_agents_spans_resets(self, ledger: ResourceLedger) -> None:
        """most_expensive_agents uses full history, not just current period."""
        ledger.record_cost(_cost(llm_calls=8), agent_id="bot-x")
        ledger.reset()
        ledger.record_cost(_cost(llm_calls=1), agent_id="bot-x")
        ledger.record_cost(_cost(llm_calls=5), agent_id="bot-y")

        ranked = ledger.most_expensive_agents(k=2)

        # bot-x has 8+1=9 total, bot-y has 5
        assert ranked[0][0] == "bot-x"
        assert ranked[0][1].llm_calls == 9
