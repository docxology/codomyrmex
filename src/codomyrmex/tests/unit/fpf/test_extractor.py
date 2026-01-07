"""Tests for FPF extractor."""

import pytest

from codomyrmex.fpf.extractor import FPFExtractor
from codomyrmex.fpf.models import FPFSpec, Pattern, PatternStatus


def test_extractor_initialization():
    """Test extractor initialization."""
    extractor = FPFExtractor()
    assert extractor is not None


def test_extract_concepts():
    """Test concept extraction."""
    extractor = FPFExtractor()
    spec = FPFSpec(
        patterns=[
            Pattern(
                id="A.1",
                title="Test Pattern",
                status=PatternStatus.STABLE,
                content="This pattern defines `U.Holon` and `U.System`.",
            )
        ]
    )
    concepts = extractor.extract_concepts(spec)
    assert len(concepts) > 0


def test_extract_relationships():
    """Test relationship extraction."""
    extractor = FPFExtractor()
    spec = FPFSpec(
        patterns=[
            Pattern(
                id="A.1",
                title="Test Pattern",
                status=PatternStatus.STABLE,
                dependencies={"builds_on": ["A.0"]},
                content="",
            )
        ]
    )
    relationships = extractor.extract_relationships(spec)
    assert len(relationships) > 0
    assert relationships[0].source == "A.1"
    assert relationships[0].target == "A.0"


def test_extract_keywords():
    """Test keyword extraction."""
    extractor = FPFExtractor()
    spec = FPFSpec(
        patterns=[
            Pattern(
                id="A.1",
                title="Test Pattern",
                status=PatternStatus.STABLE,
                keywords=["holon", "system"],
                content="",
            )
        ]
    )
    keywords = extractor.extract_keywords(spec)
    assert "A.1" in keywords
    assert "holon" in keywords["A.1"]


def test_extract_concepts_empty_spec():
    """Test concept extraction from empty spec."""
    extractor = FPFExtractor()
    spec = FPFSpec(patterns=[])
    concepts = extractor.extract_concepts(spec)
    assert isinstance(concepts, list)
    assert len(concepts) == 0


def test_extract_relationships_empty_spec():
    """Test relationship extraction from empty spec."""
    extractor = FPFExtractor()
    spec = FPFSpec(patterns=[])
    relationships = extractor.extract_relationships(spec)
    assert isinstance(relationships, list)
    assert len(relationships) == 0


def test_extract_relationships_multiple_types():
    """Test extraction of multiple relationship types."""
    extractor = FPFExtractor()
    spec = FPFSpec(
        patterns=[
            Pattern(
                id="A.1",
                title="Test Pattern",
                status=PatternStatus.STABLE,
                dependencies={
                    "builds_on": ["A.0"],
                    "prerequisite_for": ["A.2"],
                    "coordinates_with": ["B.1"],
                },
                content="",
            )
        ]
    )
    relationships = extractor.extract_relationships(spec)
    assert len(relationships) >= 3
    rel_types = {r.type for r in relationships}
    assert "builds_on" in rel_types or "prerequisite_for" in rel_types


def test_extract_dependencies_empty():
    """Test dependency extraction from empty spec."""
    extractor = FPFExtractor()
    spec = FPFSpec(patterns=[])
    deps = extractor.extract_dependencies(spec)
    assert isinstance(deps, dict)
    assert len(deps) == 0


def test_extract_keywords_empty():
    """Test keyword extraction from empty spec."""
    extractor = FPFExtractor()
    spec = FPFSpec(patterns=[])
    keywords = extractor.extract_keywords(spec)
    assert isinstance(keywords, dict)
    assert len(keywords) == 0

