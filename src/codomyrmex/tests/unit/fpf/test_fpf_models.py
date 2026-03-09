"""Tests for fpf.core.models."""

from datetime import datetime

from codomyrmex.fpf.core.models import (
    Concept,
    ConceptType,
    FPFIndex,
    FPFSpec,
    Pattern,
    PatternStatus,
    Relationship,
    RelationshipType,
)


class TestPatternStatus:
    def test_all_values(self):
        values = {s.value for s in PatternStatus}
        assert "Stable" in values
        assert "Draft" in values
        assert "Stub" in values
        assert "New" in values

    def test_str_enum(self):
        assert PatternStatus.STABLE == "Stable"


class TestRelationshipType:
    def test_all_values(self):
        values = {t.value for t in RelationshipType}
        assert "builds_on" in values
        assert "prerequisite_for" in values
        assert "coordinates_with" in values
        assert "constrains" in values
        assert "refines" in values

    def test_used_by(self):
        assert RelationshipType.USED_BY == "used_by"


class TestConceptType:
    def test_all_values(self):
        values = {t.value for t in ConceptType}
        assert "Mechanism" in values
        assert "Pattern" in values
        assert "Term" in values
        assert "Principle" in values

    def test_u_type(self):
        assert ConceptType.U_TYPE == "U.Type"


class TestPattern:
    def _make_pattern(self, **kwargs) -> Pattern:
        defaults = {
            "id": "A.1",
            "title": "Test Pattern",
            "status": PatternStatus.STABLE,
            "content": "# Test\nSome content here.",
        }
        defaults.update(kwargs)
        return Pattern(**defaults)

    def test_construction(self):
        p = self._make_pattern()
        assert p.id == "A.1"
        assert p.title == "Test Pattern"
        assert p.content == "# Test\nSome content here."

    def test_use_enum_values_status(self):
        p = self._make_pattern(status=PatternStatus.DRAFT)
        # With use_enum_values=True, stored as string value
        assert p.status == "Draft"

    def test_defaults(self):
        p = self._make_pattern()
        assert p.keywords == []
        assert p.search_queries == []
        assert p.dependencies == {}
        assert p.sections == {}
        assert p.metadata == {}
        assert p.part is None
        assert p.cluster is None

    def test_with_keywords(self):
        p = self._make_pattern(keywords=["abstraction", "system"])
        assert "abstraction" in p.keywords

    def test_with_part(self):
        p = self._make_pattern(part="A")
        assert p.part == "A"

    def test_with_cluster(self):
        p = self._make_pattern(cluster="C1")
        assert p.cluster == "C1"

    def test_with_sections(self):
        p = self._make_pattern(sections={"Problem": "No ordering.", "Solution": "Use layers."})
        assert p.sections["Problem"] == "No ordering."


class TestConcept:
    def _make_concept(self, **kwargs) -> Concept:
        defaults = {
            "name": "Modularity",
            "definition": "The degree to which components can be separated.",
            "pattern_id": "A.1",
            "type": ConceptType.PRINCIPLE,
        }
        defaults.update(kwargs)
        return Concept(**defaults)

    def test_construction(self):
        c = self._make_concept()
        assert c.name == "Modularity"
        assert c.pattern_id == "A.1"

    def test_use_enum_values_type(self):
        c = self._make_concept(type=ConceptType.MECHANISM)
        assert c.type == "Mechanism"

    def test_defaults(self):
        c = self._make_concept()
        assert c.references == []
        assert c.aliases == []
        assert c.metadata == {}

    def test_with_aliases(self):
        c = self._make_concept(aliases=["modular design"])
        assert "modular design" in c.aliases


class TestRelationship:
    def _make_rel(self, **kwargs) -> Relationship:
        defaults = {
            "source": "A.1",
            "target": "A.2",
            "type": RelationshipType.BUILDS_ON,
        }
        defaults.update(kwargs)
        return Relationship(**defaults)

    def test_construction(self):
        r = self._make_rel()
        assert r.source == "A.1"
        assert r.target == "A.2"

    def test_use_enum_values_type(self):
        r = self._make_rel(type=RelationshipType.CONSTRAINS)
        assert r.type == "constrains"

    def test_optional_fields(self):
        r = self._make_rel()
        assert r.strength is None
        assert r.description is None
        assert r.metadata == {}

    def test_with_description(self):
        r = self._make_rel(description="A.1 is the foundation for A.2")
        assert "foundation" in r.description


class TestFPFSpec:
    def _make_pattern(self, pid: str) -> Pattern:
        return Pattern(id=pid, title=f"Pattern {pid}", status=PatternStatus.STABLE, content="c")

    def _make_concept(self, name: str, pid: str) -> Concept:
        return Concept(name=name, definition="d", pattern_id=pid, type=ConceptType.TERM)

    def _make_rel(self, src: str, tgt: str) -> Relationship:
        return Relationship(source=src, target=tgt, type=RelationshipType.BUILDS_ON)

    def test_empty_spec(self):
        spec = FPFSpec()
        assert spec.patterns == []
        assert spec.concepts == []
        assert spec.relationships == []

    def test_get_pattern_by_id_found(self):
        p = self._make_pattern("A.1")
        spec = FPFSpec(patterns=[p])
        found = spec.get_pattern_by_id("A.1")
        assert found is not None
        assert found.id == "A.1"

    def test_get_pattern_by_id_not_found(self):
        spec = FPFSpec()
        assert spec.get_pattern_by_id("X.99") is None

    def test_get_concepts_by_pattern(self):
        c1 = self._make_concept("Foo", "A.1")
        c2 = self._make_concept("Bar", "A.2")
        spec = FPFSpec(concepts=[c1, c2])
        result = spec.get_concepts_by_pattern("A.1")
        assert len(result) == 1
        assert result[0].name == "Foo"

    def test_get_concepts_by_pattern_none(self):
        spec = FPFSpec()
        assert spec.get_concepts_by_pattern("Z.99") == []

    def test_get_relationships_by_source(self):
        r1 = self._make_rel("A.1", "A.2")
        r2 = self._make_rel("A.2", "A.3")
        spec = FPFSpec(relationships=[r1, r2])
        result = spec.get_relationships_by_source("A.1")
        assert len(result) == 1
        assert result[0].target == "A.2"

    def test_get_relationships_by_target(self):
        r1 = self._make_rel("A.1", "A.2")
        r2 = self._make_rel("A.3", "A.2")
        spec = FPFSpec(relationships=[r1, r2])
        result = spec.get_relationships_by_target("A.2")
        assert len(result) == 2

    def test_last_updated_str_parsed(self):
        spec = FPFSpec(last_updated="2024-01-15T10:00:00")
        assert isinstance(spec.last_updated, datetime)

    def test_last_updated_invalid_str_returns_none(self):
        spec = FPFSpec(last_updated="not-a-date")
        assert spec.last_updated is None

    def test_last_updated_datetime_passthrough(self):
        dt = datetime(2024, 6, 1, 12, 0, 0)
        spec = FPFSpec(last_updated=dt)
        assert spec.last_updated == dt

    def test_last_updated_none(self):
        spec = FPFSpec()
        assert spec.last_updated is None

    def test_version_and_source(self):
        spec = FPFSpec(version="3.0", source_url="https://example.com")
        assert spec.version == "3.0"
        assert spec.source_url == "https://example.com"


class TestFPFIndex:
    def _make_pattern(self, pid: str, title: str = "Test", content: str = "content") -> Pattern:
        return Pattern(id=pid, title=title, status=PatternStatus.STABLE, content=content)

    def test_empty_index(self):
        idx = FPFIndex()
        assert idx.get_pattern("A.1") is None

    def test_get_pattern_found(self):
        p = self._make_pattern("A.1")
        idx = FPFIndex(pattern_index={"A.1": p})
        assert idx.get_pattern("A.1") is p

    def test_search_patterns_by_title(self):
        p = self._make_pattern("A.1", title="Layered Architecture")
        idx = FPFIndex(pattern_index={"A.1": p})
        results = idx.search_patterns("layered")
        assert any(r.id == "A.1" for r in results)

    def test_search_patterns_by_keyword(self):
        p = self._make_pattern("A.2", title="Other")
        idx = FPFIndex(
            pattern_index={"A.2": p},
            keyword_index={"architecture": ["A.2"]},
        )
        results = idx.search_patterns("architecture")
        assert any(r.id == "A.2" for r in results)

    def test_search_patterns_by_content(self):
        p = self._make_pattern("A.3", content="This pattern describes dependency inversion.")
        idx = FPFIndex(pattern_index={"A.3": p})
        results = idx.search_patterns("dependency inversion")
        assert any(r.id == "A.3" for r in results)

    def test_search_with_status_filter(self):
        p_stable = self._make_pattern("A.1", title="query")
        p_draft = Pattern(id="A.2", title="query pattern", status=PatternStatus.DRAFT, content="c")
        idx = FPFIndex(pattern_index={"A.1": p_stable, "A.2": p_draft})
        results = idx.search_patterns("query", filters={"status": "Stable"})
        ids = [r.id for r in results]
        assert "A.1" in ids
        assert "A.2" not in ids

    def test_get_related_patterns_depth_1(self):
        p1 = self._make_pattern("A.1")
        p2 = self._make_pattern("A.2")
        idx = FPFIndex(
            pattern_index={"A.1": p1, "A.2": p2},
            relationship_graph={"A.1": ["A.2"]},
        )
        related = idx.get_related_patterns("A.1", depth=1)
        assert any(r.id == "A.2" for r in related)

    def test_get_related_patterns_excludes_self(self):
        p = self._make_pattern("A.1")
        idx = FPFIndex(
            pattern_index={"A.1": p},
            relationship_graph={"A.1": []},
        )
        related = idx.get_related_patterns("A.1")
        assert not any(r.id == "A.1" for r in related)

    def test_get_related_patterns_missing_node(self):
        idx = FPFIndex()
        related = idx.get_related_patterns("MISSING")
        assert related == []
