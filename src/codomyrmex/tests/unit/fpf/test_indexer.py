"""Tests for FPF indexer."""

import pytest

from codomyrmex.fpf import FPFIndexer, FPFSpec, Pattern, PatternStatus


def test_indexer_initialization():
    """Test indexer initialization."""
    indexer = FPFIndexer()
    assert indexer is not None


def test_build_index():
    """Test index building."""
    indexer = FPFIndexer()
    spec = FPFSpec(
        patterns=[
            Pattern(
                id="A.1",
                title="Test Pattern",
                status=PatternStatus.STABLE,
                keywords=["test"],
                content="",
            )
        ]
    )
    index = indexer.build_index(spec)
    assert index is not None
    assert index.get_pattern("A.1") is not None


def test_search_patterns():
    """Test pattern search."""
    indexer = FPFIndexer()
    spec = FPFSpec(
        patterns=[
            Pattern(
                id="A.1",
                title="Test Pattern",
                status=PatternStatus.STABLE,
                keywords=["test"],
                content="This is a test pattern about holons.",
            )
        ]
    )
    indexer.build_index(spec)
    results = indexer.search_patterns("test")
    assert len(results) > 0


def test_get_pattern_by_id():
    """Test getting pattern by ID."""
    indexer = FPFIndexer()
    spec = FPFSpec(
        patterns=[
            Pattern(
                id="A.1",
                title="Test Pattern",
                status=PatternStatus.STABLE,
                content="",
            )
        ]
    )
    indexer.build_index(spec)
    pattern = indexer.get_pattern_by_id("A.1")
    assert pattern is not None
    assert pattern.id == "A.1"


def test_get_pattern_by_id_not_found():
    """Test getting non-existent pattern."""
    indexer = FPFIndexer()
    spec = FPFSpec(patterns=[])
    indexer.build_index(spec)
    pattern = indexer.get_pattern_by_id("Z.999")
    assert pattern is None


def test_search_patterns_with_filters():
    """Test search with filters."""
    indexer = FPFIndexer()
    spec = FPFSpec(
        patterns=[
            Pattern(
                id="A.1",
                title="Stable Pattern",
                status=PatternStatus.STABLE,
                keywords=["test"],
                content="",
                part="A",
            ),
            Pattern(
                id="B.1",
                title="Draft Pattern",
                status=PatternStatus.DRAFT,
                keywords=["test"],
                content="",
                part="B",
            ),
        ]
    )
    indexer.build_index(spec)
    results = indexer.search_patterns("test", filters={"status": "Stable"})
    assert len(results) == 1
    assert results[0].status == PatternStatus.STABLE


def test_get_related_patterns():
    """Test getting related patterns."""
    indexer = FPFIndexer()
    spec = FPFSpec(
        patterns=[
            Pattern(
                id="A.1",
                title="Pattern 1",
                status=PatternStatus.STABLE,
                dependencies={"builds_on": ["A.0"]},
                content="",
            ),
            Pattern(
                id="A.0",
                title="Pattern 0",
                status=PatternStatus.STABLE,
                content="",
            ),
        ]
    )
    indexer.build_index(spec)
    related = indexer.get_related_patterns("A.1", depth=1)
    assert len(related) > 0


def test_search_patterns_empty_query():
    """Test search with empty query."""
    indexer = FPFIndexer()
    spec = FPFSpec(patterns=[])
    indexer.build_index(spec)
    results = indexer.search_patterns("")
    assert isinstance(results, list)

