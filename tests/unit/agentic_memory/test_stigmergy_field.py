"""Tests for stigmergy in-memory TraceField."""

from __future__ import annotations

import pytest

from codomyrmex.agentic_memory.core.consolidation import (
    ConsolidationConfig,
    MemoryConsolidator,
)
from codomyrmex.agentic_memory.core.models import Memory, MemoryImportance, MemoryType
from codomyrmex.agentic_memory.stigmergy import StigmergyConfig, TraceField


def test_deposit_and_sense() -> None:
    cfg = StigmergyConfig(max_strength=5.0)
    field = TraceField(cfg)
    m = field.deposit("task-a", initial=2.0, metadata={"src": "test"})
    assert m.key == "task-a"
    assert m.strength == 2.0
    read = field.sense("task-a")
    assert read is not None
    assert read.strength == 2.0


def test_reinforce_and_top_k() -> None:
    field = TraceField()
    field.deposit("x", 1.0)
    field.deposit("y", 3.0)
    field.reinforce("x")
    top = field.top_k(2)
    assert [t.key for t in top] == ["y", "x"]


def test_tick_evaporation_removes_weak() -> None:
    cfg = StigmergyConfig(evaporation_per_tick=0.5, min_strength=0.0)
    field = TraceField(cfg)
    field.deposit("fleeting", initial=0.4)
    removed = field.tick()
    assert removed == 1
    assert field.sense("fleeting") is None


def test_stigmergy_config_validation() -> None:
    with pytest.raises(ValueError, match="evaporation"):
        StigmergyConfig(evaporation_per_tick=-0.1)


def test_consolidation_trace_field_boost() -> None:
    field = TraceField()
    field.deposit("mem-1", initial=2.5)

    mem = Memory(
        id="mem-1",
        content="x" * 25,
        memory_type=MemoryType.SEMANTIC,
        importance=MemoryImportance.LOW,
    )
    cfg = ConsolidationConfig(
        min_importance=MemoryImportance.MEDIUM,
        trace_field=field,
    )
    cons = MemoryConsolidator(cfg)
    cases = cons.consolidate([mem])
    assert len(cases) == 1
    assert cases[0].case_id == "memory-mem-1"
