"""Tests for agentic_memory/consolidation.py."""

from __future__ import annotations

from codomyrmex.agentic_memory.consolidation import (
    ConsolidationConfig,
    MemoryConsolidator,
)
from codomyrmex.agentic_memory.models import (
    Memory,
    MemoryImportance,
    MemoryType,
)


def _make_memory(
    content: str = "This is a substantial memory for testing purposes",
    importance: MemoryImportance = MemoryImportance.MEDIUM,
    memory_type: MemoryType = MemoryType.EPISODIC,
    memory_id: str | None = None,
) -> Memory:
    """Create a test memory."""
    return Memory(
        id=memory_id or f"mem-{id(content)}",
        content=content,
        memory_type=memory_type,
        importance=importance,
    )


class TestConsolidationConfig:
    """Test suite for ConsolidationConfig."""
    def test_defaults(self) -> None:
        """Test functionality: defaults."""
        cfg = ConsolidationConfig()
        assert cfg.min_importance == MemoryImportance.MEDIUM
        assert cfg.min_content_length == 20
        assert cfg.batch_size == 50


class TestMemoryConsolidator:
    """Test suite for MemoryConsolidator."""
    def test_consolidate_basic(self) -> None:
        """Test functionality: consolidate basic."""
        consolidator = MemoryConsolidator()
        memories = [_make_memory(memory_id="m1")]
        cases = consolidator.consolidate(memories)
        assert len(cases) == 1
        assert cases[0].case_id == "memory-m1"

    def test_features_populated(self) -> None:
        """Test functionality: features populated."""
        consolidator = MemoryConsolidator()
        memories = [_make_memory(memory_id="m1")]
        cases = consolidator.consolidate(memories)
        case = cases[0]
        assert "content_summary" in case.features
        assert "memory_type" in case.features
        assert "importance" in case.features

    def test_context_populated(self) -> None:
        """Test functionality: context populated."""
        consolidator = MemoryConsolidator()
        memories = [_make_memory(memory_id="m1")]
        cases = consolidator.consolidate(memories)
        assert "full_content" in cases[0].context

    def test_skip_low_importance(self) -> None:
        """Test functionality: skip low importance."""
        consolidator = MemoryConsolidator(
            config=ConsolidationConfig(min_importance=MemoryImportance.HIGH)
        )
        memories = [_make_memory(importance=MemoryImportance.LOW, memory_id="low")]
        cases = consolidator.consolidate(memories)
        assert len(cases) == 0

    def test_skip_short_content(self) -> None:
        """Test functionality: skip short content."""
        consolidator = MemoryConsolidator(
            config=ConsolidationConfig(min_content_length=100)
        )
        memories = [_make_memory(content="short", memory_id="short")]
        cases = consolidator.consolidate(memories)
        assert len(cases) == 0

    def test_no_duplicate_consolidation(self) -> None:
        """Test functionality: no duplicate consolidation."""
        consolidator = MemoryConsolidator()
        m = _make_memory(memory_id="dup-1")
        consolidator.consolidate([m])
        cases = consolidator.consolidate([m])  # Same memory again
        assert len(cases) == 0

    def test_batch_size_respected(self) -> None:
        """Test functionality: batch size respected."""
        consolidator = MemoryConsolidator(
            config=ConsolidationConfig(batch_size=3)
        )
        memories = [_make_memory(memory_id=f"m{i}") for i in range(10)]
        cases = consolidator.consolidate(memories)
        assert len(cases) == 3

    def test_metadata_source(self) -> None:
        """Test functionality: metadata source."""
        consolidator = MemoryConsolidator()
        cases = consolidator.consolidate([_make_memory(memory_id="src")])
        assert cases[0].metadata["source"] == "consolidation"
        assert cases[0].metadata["memory_id"] == "src"

    def test_mixed_importance(self) -> None:
        """Test functionality: mixed importance."""
        consolidator = MemoryConsolidator()
        memories = [
            _make_memory(importance=MemoryImportance.HIGH, memory_id="high"),
            _make_memory(importance=MemoryImportance.LOW, memory_id="low"),
            _make_memory(importance=MemoryImportance.MEDIUM, memory_id="med"),
        ]
        cases = consolidator.consolidate(memories)
        # LOW (1) < MEDIUM (2), so only HIGH and MEDIUM pass
        assert len(cases) == 2
        ids = {c.case_id for c in cases}
        assert "memory-high" in ids
        assert "memory-med" in ids
