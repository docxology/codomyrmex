"""Tests for the FPF (First Principles Framework) module.

Complements test_e2e.py (integration workflows) and test_fetcher.py (network I/O).
These tests focus on:
- Module imports
- Data model construction and validation (Pattern, Concept, Relationship, FPFSpec)
- Enum values (PatternStatus, ConceptType, RelationshipType)
- FPFParser parsing logic with synthetic markdown
- FPFExtractor concept and relationship extraction
- ContextBuilder context generation
- FPFClient state management without network
"""

import pytest

from codomyrmex import fpf
from codomyrmex.fpf import (
    FPFParser,
    FPFExtractor,
    ContextBuilder,
    FPFClient,
    FPFSpec,
    Pattern,
    Concept,
    Relationship,
    FPFIndex,
    PatternStatus,
    ConceptType,
    RelationshipType,
)


@pytest.mark.unit
def test_fpf_module_import():
    """Verify that the fpf module can be imported successfully."""
    assert fpf is not None
    assert hasattr(fpf, "__path__")


@pytest.mark.unit
def test_fpf_module_structure():
    """Verify basic structure of fpf module."""
    assert hasattr(fpf, "__file__")


# --- Enum Tests ---


@pytest.mark.unit
def test_pattern_status_values():
    """PatternStatus contains all expected status values."""
    assert PatternStatus.STABLE.value == "Stable"
    assert PatternStatus.DRAFT.value == "Draft"
    assert PatternStatus.STUB.value == "Stub"
    assert PatternStatus.NEW.value == "New"


@pytest.mark.unit
def test_concept_type_values():
    """ConceptType contains expected concept categories."""
    assert ConceptType.U_TYPE.value == "U.Type"
    assert ConceptType.MECHANISM.value == "Mechanism"
    assert ConceptType.PATTERN.value == "Pattern"


@pytest.mark.unit
def test_relationship_type_values():
    """RelationshipType covers all dependency kinds."""
    assert RelationshipType.BUILDS_ON.value == "builds_on"
    assert RelationshipType.CONSTRAINS.value == "constrains"
    assert RelationshipType.COORDINATES_WITH.value == "coordinates_with"


# --- Data Model Tests ---


@pytest.mark.unit
def test_pattern_construction():
    """Pattern can be constructed with required fields."""
    pattern = Pattern(
        id="A.1",
        title="Test Pattern",
        status=PatternStatus.STABLE,
        content="## A.1 - Test Pattern\nSome content here.",
    )
    assert pattern.id == "A.1"
    assert pattern.title == "Test Pattern"
    assert pattern.keywords == []
    assert pattern.sections == {}


@pytest.mark.unit
def test_fpf_spec_get_pattern_by_id():
    """FPFSpec.get_pattern_by_id locates patterns correctly."""
    p1 = Pattern(id="A.1", title="First", status=PatternStatus.STABLE, content="c1")
    p2 = Pattern(id="B.2", title="Second", status=PatternStatus.DRAFT, content="c2")
    spec = FPFSpec(patterns=[p1, p2])

    assert spec.get_pattern_by_id("A.1") is p1
    assert spec.get_pattern_by_id("B.2") is p2
    assert spec.get_pattern_by_id("C.3") is None


@pytest.mark.unit
def test_relationship_construction():
    """Relationship model stores source, target, and type."""
    rel = Relationship(
        source="A.1",
        target="A.2",
        type=RelationshipType.BUILDS_ON,
        description="A.1 builds on A.2",
    )
    assert rel.source == "A.1"
    assert rel.target == "A.2"


# --- FPFParser Tests ---


@pytest.mark.unit
def test_parser_initialization():
    """FPFParser initializes with regex patterns."""
    parser = FPFParser()
    assert parser.pattern_regex is not None
    assert parser.section_regex is not None


@pytest.mark.unit
def test_parser_extracts_patterns_from_markdown():
    """FPFParser extracts patterns from synthetic markdown content."""
    markdown = """# FPF Specification

## A.1 - Holonic Architecture
| Stable |
### Problem
How to structure complex systems?
### Solution
Use holons.

## A.2 - Composability
| Draft |
### Problem
How to compose modules?
"""
    parser = FPFParser()
    spec = parser.parse_spec(markdown, source_path="test.md")

    assert isinstance(spec, FPFSpec)
    assert len(spec.patterns) == 2
    assert spec.patterns[0].id == "A.1"
    assert spec.patterns[0].title == "Holonic Architecture"
    assert spec.patterns[1].id == "A.2"


@pytest.mark.unit
def test_parser_extract_sections():
    """FPFParser.extract_sections splits content into named sections."""
    parser = FPFParser()
    content = """### Problem
This is the problem.
### Solution
This is the solution.
### Rationale
Why this works.
"""
    sections = parser.extract_sections(content)
    assert "problem" in sections
    assert "solution" in sections
    assert "rationale" in sections


# --- FPFExtractor Tests ---


@pytest.mark.unit
def test_extractor_extracts_relationships():
    """FPFExtractor builds relationships from pattern dependencies."""
    p1 = Pattern(
        id="A.1",
        title="First",
        status=PatternStatus.STABLE,
        content="content",
        dependencies={"builds_on": ["A.2"], "coordinates_with": ["B.1"]},
    )
    spec = FPFSpec(patterns=[p1])
    extractor = FPFExtractor()
    relationships = extractor.extract_relationships(spec)

    assert len(relationships) == 2
    types = [r.type for r in relationships]
    assert RelationshipType.BUILDS_ON in types
    assert RelationshipType.COORDINATES_WITH in types


@pytest.mark.unit
def test_extractor_extract_keywords():
    """FPFExtractor returns keyword index keyed by pattern ID."""
    p1 = Pattern(
        id="A.1",
        title="Test",
        status=PatternStatus.STABLE,
        content="test",
        keywords=["holon", "system"],
    )
    spec = FPFSpec(patterns=[p1])
    extractor = FPFExtractor()
    kw = extractor.extract_keywords(spec)
    assert kw["A.1"] == ["holon", "system"]


# --- ContextBuilder Tests ---


@pytest.mark.unit
def test_context_builder_pattern_not_found():
    """ContextBuilder returns informative string for missing pattern."""
    spec = FPFSpec(patterns=[])
    builder = ContextBuilder(spec)
    ctx = builder.build_context_for_pattern("Z.99")
    assert "Z.99" in ctx
    assert "not found" in ctx.lower()


@pytest.mark.unit
def test_context_builder_minimal_context():
    """ContextBuilder.build_minimal_context returns filtered summary."""
    p1 = Pattern(id="A.1", title="First", status=PatternStatus.STABLE, content="c", part="A")
    p2 = Pattern(id="B.1", title="Second", status=PatternStatus.DRAFT, content="c", part="B")
    spec = FPFSpec(patterns=[p1, p2])
    builder = ContextBuilder(spec)
    ctx = builder.build_minimal_context(filters={"part": "A"})
    assert "A.1" in ctx
    assert "B.1" not in ctx


# --- FPFClient Tests ---


@pytest.mark.unit
def test_client_raises_before_loading():
    """FPFClient raises ValueError when searching without loaded spec."""
    client = FPFClient()
    with pytest.raises(ValueError, match="No specification loaded"):
        client.search("test")


@pytest.mark.unit
def test_client_raises_on_export_before_loading():
    """FPFClient raises ValueError when exporting without loaded spec."""
    client = FPFClient()
    with pytest.raises(ValueError, match="No specification loaded"):
        client.export_json("/tmp/out.json")


@pytest.mark.unit
def test_client_raises_on_context_before_loading():
    """FPFClient raises ValueError when building context without loaded spec."""
    client = FPFClient()
    with pytest.raises(ValueError, match="No specification loaded"):
        client.build_context()
