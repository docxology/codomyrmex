"""Tests for FPF context builder."""

import pytest

from codomyrmex.fpf import ContextBuilder
from codomyrmex.fpf import FPFSpec, Pattern, PatternStatus, Concept, ConceptType


def test_context_builder_initialization():
    """Test context builder initialization."""
    spec = FPFSpec(patterns=[])
    builder = ContextBuilder(spec)
    assert builder is not None


def test_build_context_for_pattern():
    """Test building context for a pattern."""
    spec = FPFSpec(
        patterns=[
            Pattern(
                id="A.1",
                title="Test Pattern",
                status=PatternStatus.STABLE,
                keywords=["test"],
                dependencies={"builds_on": ["A.0"]},
                sections={"problem": "Test problem", "solution": "Test solution"},
                content="",
            )
        ]
    )
    builder = ContextBuilder(spec)
    context = builder.build_context_for_pattern("A.1")
    assert isinstance(context, str)
    assert "A.1" in context
    assert "Test Pattern" in context


def test_build_context_for_pattern_not_found():
    """Test building context for non-existent pattern."""
    spec = FPFSpec(patterns=[])
    builder = ContextBuilder(spec)
    context = builder.build_context_for_pattern("Z.999")
    assert "not found" in context.lower()


def test_build_context_for_concept():
    """Test building context for a concept."""
    spec = FPFSpec(
        patterns=[
            Pattern(
                id="A.1",
                title="Test Pattern",
                status=PatternStatus.STABLE,
                content="",
            )
        ],
        concepts=[
            Concept(
                name="U.Holon",
                definition="A holon is a system that is both a whole and a part.",
                pattern_id="A.1",
                type=ConceptType.U_TYPE,
            )
        ],
    )
    builder = ContextBuilder(spec)
    context = builder.build_context_for_concept("Holon")
    assert isinstance(context, str)
    assert "U.Holon" in context or "Holon" in context


def test_build_minimal_context():
    """Test building minimal context."""
    spec = FPFSpec(
        patterns=[
            Pattern(
                id="A.1",
                title="Pattern 1",
                status=PatternStatus.STABLE,
                keywords=["test"],
                content="",
                part="A",
            ),
            Pattern(
                id="B.1",
                title="Pattern 2",
                status=PatternStatus.DRAFT,
                keywords=["test"],
                content="",
                part="B",
            ),
        ]
    )
    builder = ContextBuilder(spec)
    context = builder.build_minimal_context(filters={"part": "A"})
    assert isinstance(context, str)
    assert "A.1" in context


def test_build_full_context():
    """Test building full context."""
    spec = FPFSpec(
        patterns=[
            Pattern(
                id="A.1",
                title="Test Pattern",
                status=PatternStatus.STABLE,
                content="",
            )
        ],
        concepts=[
            Concept(
                name="U.Holon",
                definition="Test definition",
                pattern_id="A.1",
                type=ConceptType.U_TYPE,
            )
        ],
    )
    builder = ContextBuilder(spec)
    context = builder.build_full_context()
    assert isinstance(context, str)
    assert "FPF Full Specification Context" in context


