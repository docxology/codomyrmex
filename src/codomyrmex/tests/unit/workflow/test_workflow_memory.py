"""Tests for Sprint 23 (Workflow) and Sprint 24 (Agent Memory)."""

from __future__ import annotations

import time

import pytest

from codomyrmex.orchestrator.workflow_engine import (
    StepStatus, WorkflowResult, WorkflowRunner, WorkflowStep,
)
from codomyrmex.orchestrator.workflow_templates import (
    WorkflowTemplate, ci_cd_template, code_review_template, data_pipeline_template,
)
from codomyrmex.agents.memory.store import MemoryEntry, MemoryStore
from codomyrmex.agents.memory.conversation import ConversationHistory, Turn
from codomyrmex.agents.memory.journal import JournalEntry, LearningJournal


# ── WorkflowEngine ───────────────────────────────────────────────


class TestWorkflowStep:
    """Test suite for WorkflowStep."""
    def test_to_dict(self) -> None:
        """Test functionality: to dict."""
        s = WorkflowStep("build")
        d = s.to_dict()
        assert d["name"] == "build"
        assert d["status"] == "pending"


class TestWorkflowRunner:
    """Test suite for WorkflowRunner."""
    def test_linear_pipeline(self) -> None:
        """Test functionality: linear pipeline."""
        runner = WorkflowRunner()
        runner.add_step(WorkflowStep("a", action=lambda ctx: "done_a"))
        runner.add_step(WorkflowStep("b", action=lambda ctx: "done_b", depends_on=["a"]))
        result = runner.run()
        assert result.success
        assert result.completed_count == 2

    def test_failed_step_skips_dependents(self) -> None:
        """Test functionality: failed step skips dependents."""
        def fail(ctx):
            raise RuntimeError("boom")

        runner = WorkflowRunner()
        runner.add_step(WorkflowStep("a", action=fail))
        runner.add_step(WorkflowStep("b", action=lambda ctx: "ok", depends_on=["a"]))
        result = runner.run()
        assert not result.success
        assert result.failed_count == 1

    def test_parallel_roots(self) -> None:
        """Test functionality: parallel roots."""
        runner = WorkflowRunner()
        runner.add_step(WorkflowStep("a", action=lambda ctx: 1))
        runner.add_step(WorkflowStep("b", action=lambda ctx: 2))
        runner.add_step(WorkflowStep("c", action=lambda ctx: 3, depends_on=["a", "b"]))
        result = runner.run()
        assert result.success
        assert result.completed_count == 3

    def test_cycle_detection(self) -> None:
        """Test functionality: cycle detection."""
        runner = WorkflowRunner()
        runner.add_step(WorkflowStep("a", depends_on=["b"]))
        runner.add_step(WorkflowStep("b", depends_on=["a"]))
        with pytest.raises(ValueError):
            runner.run()

    def test_context_passing(self) -> None:
        """Test functionality: context passing."""
        def write_ctx(ctx):
            ctx["key"] = "value"

        def read_ctx(ctx):
            return ctx.get("key")

        runner = WorkflowRunner()
        runner.add_step(WorkflowStep("write", action=write_ctx))
        runner.add_step(WorkflowStep("read", action=read_ctx, depends_on=["write"]))
        result = runner.run()
        assert result.success

    def test_step_count(self) -> None:
        """Test functionality: step count."""
        runner = WorkflowRunner()
        runner.add_step(WorkflowStep("x"))
        assert runner.step_count == 1


class TestWorkflowTemplates:
    """Test suite for WorkflowTemplates."""
    def test_ci_cd(self) -> None:
        """Test functionality: ci cd."""
        t = ci_cd_template()
        assert len(t.steps) == 4
        runner = t.instantiate({
            "lint": lambda ctx: "ok",
            "build": lambda ctx: "ok",
            "test": lambda ctx: "ok",
            "deploy": lambda ctx: "ok",
        })
        assert runner.step_count == 4
        result = runner.run()
        assert result.success

    def test_code_review(self) -> None:
        """Test functionality: code review."""
        t = code_review_template()
        assert t.name == "code_review"
        assert len(t.steps) == 4

    def test_data_pipeline(self) -> None:
        """Test functionality: data pipeline."""
        t = data_pipeline_template()
        assert t.name == "data_pipeline"


# ── MemoryStore ──────────────────────────────────────────────────


class TestMemoryStore:
    """Test suite for MemoryStore."""
    def test_put_get(self) -> None:
        """Test functionality: put get."""
        store = MemoryStore()
        store.put("k", "v")
        assert store.get("k") == "v"

    def test_missing_key(self) -> None:
        """Test functionality: missing key."""
        store = MemoryStore()
        assert store.get("nope", "default") == "default"

    def test_delete(self) -> None:
        """Test functionality: delete."""
        store = MemoryStore()
        store.put("k", 1)
        assert store.delete("k")
        assert not store.has("k")

    def test_ttl_expiry(self) -> None:
        """Test functionality: ttl expiry."""
        store = MemoryStore()
        store.put("k", "v", ttl=0.001)
        time.sleep(0.01)
        assert store.get("k") is None

    def test_search_by_tag(self) -> None:
        """Test functionality: search by tag."""
        store = MemoryStore()
        store.put("a", 1, tags=["red"])
        store.put("b", 2, tags=["blue"])
        assert len(store.search_by_tag("red")) == 1

    def test_size(self) -> None:
        """Test functionality: size."""
        store = MemoryStore()
        store.put("a", 1)
        store.put("b", 2)
        assert store.size == 2


# ── ConversationHistory ──────────────────────────────────────────


class TestConversationHistory:
    """Test suite for ConversationHistory."""
    def test_add_and_count(self) -> None:
        """Test functionality: add and count."""
        h = ConversationHistory()
        h.add("user", "hello")
        h.add("assistant", "hi")
        assert h.turn_count == 2

    def test_by_role(self) -> None:
        """Test functionality: by role."""
        h = ConversationHistory()
        h.add("user", "a")
        h.add("assistant", "b")
        h.add("user", "c")
        assert len(h.by_role("user")) == 2

    def test_max_turns(self) -> None:
        """Test functionality: max turns."""
        h = ConversationHistory(max_turns=2)
        h.add("user", "1")
        h.add("user", "2")
        h.add("user", "3")
        assert h.turn_count == 2

    def test_to_messages(self) -> None:
        """Test functionality: to messages."""
        h = ConversationHistory()
        h.add("user", "hi")
        msgs = h.to_messages()
        assert msgs[0]["role"] == "user"

    def test_summary(self) -> None:
        """Test functionality: summary."""
        h = ConversationHistory()
        h.add("user", "one two three")
        s = h.summary()
        assert s["total_words"] == 3


# ── LearningJournal ──────────────────────────────────────────────


class TestLearningJournal:
    """Test suite for LearningJournal."""
    def test_record(self) -> None:
        """Test functionality: record."""
        j = LearningJournal()
        j.record("python", "use generators")
        assert j.size == 1

    def test_by_topic(self) -> None:
        """Test functionality: by topic."""
        j = LearningJournal()
        j.record("python", "a")
        j.record("rust", "b")
        assert len(j.by_topic("python")) == 1

    def test_detect_patterns(self) -> None:
        """Test functionality: detect patterns."""
        j = LearningJournal()
        j.record("python", "x", tags=["performance"])
        j.record("python", "y", tags=["performance"])
        j.record("rust", "z")
        patterns = j.detect_patterns()
        assert patterns["top_topics"][0][0] == "python"

    def test_high_confidence(self) -> None:
        """Test functionality: high confidence."""
        j = LearningJournal()
        j.record("a", confidence=0.9)
        j.record("b", confidence=0.3)
        assert len(j.high_confidence(0.8)) == 1
