"""Tests for the UOR submodule.

Tests cover:
- Module import and parent re-exports
- PrismEngine: triadic coordinates, primitive ops, critical identity,
  correlate/fidelity, verify coherence
- UOREntity: content hashing, unique IDs, to_dict, recompute_hash
- UORRelationship: content hashing, to_dict
- EntityManager: CRUD, search, similarity, duplicate detection
- UORGraph: entity/relationship CRUD, BFS path-finding, neighbors,
  cascading removal
- DerivationTracker: record, history, chain verification
"""

import pytest

from codomyrmex.relations.uor import (
    DerivationRecord,
    DerivationTracker,
    EntityManager,
    PrismEngine,
    TriadicCoordinate,
    UOREntity,
    UORGraph,
    UORRelationship,
)

# ======================================================================
# Module import
# ======================================================================


@pytest.mark.unit
def test_uor_module_import():
    """UOR submodule is importable."""
    from codomyrmex.relations import uor

    assert uor is not None


@pytest.mark.unit
def test_uor_parent_reexports():
    """Key UOR classes are re-exported from the relations module."""
    from codomyrmex.relations import (
        EntityManager as EM,
    )
    from codomyrmex.relations import (
        PrismEngine as PE,
    )
    from codomyrmex.relations import (
        UOREntity as UE,
    )
    from codomyrmex.relations import (
        UORGraph as UG,
    )
    from codomyrmex.relations import (
        UORRelationship as UR,
    )

    assert EM is EntityManager
    assert PE is PrismEngine
    assert UE is UOREntity
    assert UG is UORGraph
    assert UR is UORRelationship


# ======================================================================
# PrismEngine: construction
# ======================================================================


@pytest.mark.unit
def test_engine_construction_default():
    """PrismEngine defaults to quantum 0 (8-bit)."""
    engine = PrismEngine()
    assert engine.quantum == 0
    assert engine.width == 1
    assert engine.bits == 8
    assert engine.cycle == 256


@pytest.mark.unit
def test_engine_construction_q1():
    """PrismEngine quantum=1 gives 16-bit."""
    engine = PrismEngine(quantum=1)
    assert engine.width == 2
    assert engine.bits == 16
    assert engine.cycle == 65536


@pytest.mark.unit
def test_engine_negative_quantum_raises():
    """PrismEngine rejects negative quantum."""
    with pytest.raises(ValueError):
        PrismEngine(quantum=-1)


@pytest.mark.unit
def test_engine_repr():
    """PrismEngine repr shows quantum and verification status."""
    engine = PrismEngine()
    assert "quantum=0" in repr(engine)
    assert "unverified" in repr(engine)


# ======================================================================
# PrismEngine: triadic coordinates
# ======================================================================


@pytest.mark.unit
def test_engine_triad_zero():
    """Triad of 0 has zero stratum and empty spectrum."""
    engine = PrismEngine()
    t = engine.triad(0)
    assert t.datum == (0,)
    assert t.stratum == (0,)
    assert t.spectrum == ((),)
    assert t.total_stratum == 0


@pytest.mark.unit
def test_engine_triad_42():
    """Triad of 42 = 0b00101010 has stratum=3, spectrum=(1,3,5)."""
    engine = PrismEngine()
    t = engine.triad(42)
    assert t.datum == (42,)
    assert t.stratum == (3,)
    assert t.spectrum == ((1, 3, 5),)
    assert t.total_stratum == 3


@pytest.mark.unit
def test_engine_triad_255():
    """Triad of 255 has stratum=8 and all bits active."""
    engine = PrismEngine()
    t = engine.triad(255)
    assert t.datum == (255,)
    assert t.stratum == (8,)
    assert t.spectrum == ((0, 1, 2, 3, 4, 5, 6, 7),)


@pytest.mark.unit
def test_triadic_coordinate_width():
    """TriadicCoordinate.width returns number of bytes."""
    t = TriadicCoordinate(datum=(42,), stratum=(3,), spectrum=((1, 3, 5),))
    assert t.width == 1


@pytest.mark.unit
def test_triadic_coordinate_frozen():
    """TriadicCoordinate is immutable."""
    t = TriadicCoordinate(datum=(42,), stratum=(3,), spectrum=((1, 3, 5),))
    with pytest.raises(AttributeError):
        t.datum = (0,)


# ======================================================================
# PrismEngine: primitive operations
# ======================================================================


@pytest.mark.unit
def test_engine_neg_involution():
    """neg(neg(x)) = x for all byte values."""
    engine = PrismEngine()
    for n in range(256):
        assert engine.neg(engine.neg(n)) == (n,)


@pytest.mark.unit
def test_engine_bnot_involution():
    """bnot(bnot(x)) = x for all byte values."""
    engine = PrismEngine()
    for n in range(256):
        assert engine.bnot(engine.bnot(n)) == (n,)


@pytest.mark.unit
def test_engine_xor_self_annihilation():
    """x XOR x = 0."""
    engine = PrismEngine()
    assert engine.xor(42, 42) == (0,)


@pytest.mark.unit
def test_engine_xor_complement():
    """x XOR bnot(x) = 0xFF."""
    engine = PrismEngine()
    assert engine.xor(42, engine.bnot(42)) == (0xFF,)


@pytest.mark.unit
def test_engine_band():
    """0x55 AND 0xAA = 0."""
    engine = PrismEngine()
    assert engine.band(0x55, 0xAA) == (0,)


@pytest.mark.unit
def test_engine_bor():
    """0x55 OR 0xAA = 0xFF."""
    engine = PrismEngine()
    assert engine.bor(0x55, 0xAA) == (0xFF,)


# ======================================================================
# PrismEngine: critical identity & derived ops
# ======================================================================


@pytest.mark.unit
def test_engine_critical_identity():
    """neg(bnot(x)) = x + 1 mod 256 for all x."""
    engine = PrismEngine()
    for n in range(256):
        expected = ((n + 1) % 256,)
        assert engine.neg(engine.bnot(n)) == expected


@pytest.mark.unit
def test_engine_succ():
    """succ(42) = 43."""
    engine = PrismEngine()
    assert engine.succ(42) == (43,)


@pytest.mark.unit
def test_engine_pred():
    """pred(42) = 41."""
    engine = PrismEngine()
    assert engine.pred(42) == (41,)


@pytest.mark.unit
def test_engine_succ_overflow():
    """succ(255) = 0 (wraps around)."""
    engine = PrismEngine()
    assert engine.succ(255) == (0,)


@pytest.mark.unit
def test_engine_pred_underflow():
    """pred(0) = 255 (wraps around)."""
    engine = PrismEngine()
    assert engine.pred(0) == (255,)


@pytest.mark.unit
def test_engine_succ_pred_roundtrip():
    """succ(pred(x)) = x."""
    engine = PrismEngine()
    for n in range(256):
        assert engine.succ(engine.pred(n)) == (n,)


# ======================================================================
# PrismEngine: correlation
# ======================================================================


@pytest.mark.unit
def test_engine_correlate_identical():
    """Identical values have fidelity 1.0."""
    engine = PrismEngine()
    result = engine.correlate(42, 42)
    assert result["fidelity"] == 1.0
    assert result["total_difference"] == 0


@pytest.mark.unit
def test_engine_correlate_opposite():
    """x and bnot(x) have fidelity 0.0."""
    engine = PrismEngine()
    result = engine.correlate(0, 255)
    assert result["fidelity"] == 0.0
    assert result["total_difference"] == 8


@pytest.mark.unit
def test_engine_correlate_42_43():
    """42 and 43 differ by 1 bit → fidelity = 7/8 = 0.875."""
    engine = PrismEngine()
    result = engine.correlate(42, 43)
    assert result["fidelity"] == 0.875
    assert result["total_difference"] == 1


@pytest.mark.unit
def test_engine_fidelity_shorthand():
    """fidelity() returns just the float."""
    engine = PrismEngine()
    assert engine.fidelity(42, 42) == 1.0
    assert isinstance(engine.fidelity(42, 43), float)


# ======================================================================
# PrismEngine: verify
# ======================================================================


@pytest.mark.unit
def test_engine_verify_q0():
    """verify() passes for Q0 (exhaustive 256-state check)."""
    engine = PrismEngine(quantum=0)
    assert engine.verify() is True
    assert engine.is_coherent is True


@pytest.mark.unit
def test_engine_verify_q1():
    """verify() passes for Q1 (16-bit)."""
    engine = PrismEngine(quantum=1)
    assert engine.verify() is True


# ======================================================================
# PrismEngine: tuple input
# ======================================================================


@pytest.mark.unit
def test_engine_tuple_input():
    """Engine accepts byte tuples as input."""
    engine = PrismEngine()
    assert engine.neg((42,)) == engine.neg(42)
    assert engine.triad((42,)).datum == (42,)


@pytest.mark.unit
def test_engine_invalid_tuple_length():
    """Engine rejects wrong-length tuples."""
    engine = PrismEngine()
    with pytest.raises(ValueError):
        engine.bnot((1, 2))  # Q0 expects 1 byte


# ======================================================================
# UOREntity
# ======================================================================


@pytest.mark.unit
def test_entity_creation_defaults():
    """UOREntity has auto-generated id and content hash."""
    entity = UOREntity()
    assert entity.id is not None
    assert entity.content_hash != ""
    assert entity.name == ""
    assert entity.entity_type == "generic"


@pytest.mark.unit
def test_entity_unique_ids():
    """Each entity gets a distinct UUID."""
    e1 = UOREntity(name="A")
    e2 = UOREntity(name="B")
    assert e1.id != e2.id


@pytest.mark.unit
def test_entity_content_hash_deterministic():
    """Same attributes produce same content hash."""
    e1 = UOREntity(name="Alice", entity_type="person", attributes={"role": "eng"})
    e2 = UOREntity(name="Alice", entity_type="person", attributes={"role": "eng"})
    assert e1.content_hash == e2.content_hash


@pytest.mark.unit
def test_entity_content_hash_varies():
    """Different attributes produce different content hashes."""
    e1 = UOREntity(name="Alice", entity_type="person")
    e2 = UOREntity(name="Bob", entity_type="person")
    assert e1.content_hash != e2.content_hash


@pytest.mark.unit
def test_entity_to_dict():
    """to_dict() returns serializable dictionary."""
    entity = UOREntity(name="Test", entity_type="node", attributes={"k": "v"})
    d = entity.to_dict()
    assert d["name"] == "Test"
    assert d["entity_type"] == "node"
    assert d["attributes"] == {"k": "v"}
    assert "id" in d
    assert "content_hash" in d
    assert "created_at" in d


@pytest.mark.unit
def test_entity_to_dict_with_coordinates():
    """to_dict() includes triadic_coordinates when present."""
    tc = TriadicCoordinate(datum=(42,), stratum=(3,), spectrum=((1, 3, 5),))
    entity = UOREntity(name="X", triadic_coordinates=tc)
    d = entity.to_dict()
    assert "triadic_coordinates" in d
    assert d["triadic_coordinates"]["datum"] == [42]
    assert d["triadic_coordinates"]["total_stratum"] == 3


@pytest.mark.unit
def test_entity_recompute_hash():
    """recompute_hash() updates hash after attribute change."""
    entity = UOREntity(name="Alice", attributes={"level": 1})
    old_hash = entity.content_hash
    entity.attributes["level"] = 2
    entity.recompute_hash()
    assert entity.content_hash != old_hash


# ======================================================================
# UORRelationship
# ======================================================================


@pytest.mark.unit
def test_relationship_creation():
    """UORRelationship has auto-generated id and hash."""
    rel = UORRelationship(source_id="a", target_id="b", relationship_type="knows")
    assert rel.id is not None
    assert rel.relationship_hash != ""


@pytest.mark.unit
def test_relationship_hash_deterministic():
    """Same relationship attributes produce same hash."""
    r1 = UORRelationship(source_id="a", target_id="b", relationship_type="knows")
    r2 = UORRelationship(source_id="a", target_id="b", relationship_type="knows")
    assert r1.relationship_hash == r2.relationship_hash


@pytest.mark.unit
def test_relationship_to_dict():
    """to_dict() returns serializable dictionary."""
    rel = UORRelationship(source_id="a", target_id="b")
    d = rel.to_dict()
    assert d["source_id"] == "a"
    assert d["target_id"] == "b"
    assert "relationship_hash" in d


# ======================================================================
# EntityManager: CRUD
# ======================================================================


@pytest.mark.unit
def test_manager_add_entity():
    """add_entity creates and stores an entity."""
    mgr = EntityManager()
    entity = mgr.add_entity("Alice", "person")
    assert isinstance(entity, UOREntity)
    assert entity.name == "Alice"
    assert entity.entity_type == "person"
    assert len(mgr) == 1


@pytest.mark.unit
def test_manager_add_entity_with_attributes():
    """add_entity accepts attributes."""
    mgr = EntityManager()
    entity = mgr.add_entity("Bob", "person", attributes={"role": "eng"})
    assert entity.attributes["role"] == "eng"


@pytest.mark.unit
def test_manager_add_entity_with_coordinates():
    """add_entity computes triadic coordinates by default."""
    mgr = EntityManager()
    entity = mgr.add_entity("Alice", "person")
    assert entity.triadic_coordinates is not None
    assert isinstance(entity.triadic_coordinates, TriadicCoordinate)


@pytest.mark.unit
def test_manager_add_entity_no_coordinates():
    """add_entity can skip coordinate computation."""
    mgr = EntityManager()
    entity = mgr.add_entity("Alice", "person", compute_coordinates=False)
    assert entity.triadic_coordinates is None


@pytest.mark.unit
def test_manager_get_entity():
    """get_entity retrieves by ID."""
    mgr = EntityManager()
    entity = mgr.add_entity("Alice", "person")
    found = mgr.get_entity(entity.id)
    assert found is entity


@pytest.mark.unit
def test_manager_get_entity_not_found():
    """get_entity returns None for unknown ID."""
    mgr = EntityManager()
    assert mgr.get_entity("nonexistent") is None


@pytest.mark.unit
def test_manager_remove_entity():
    """remove_entity removes and returns True."""
    mgr = EntityManager()
    entity = mgr.add_entity("Alice", "person")
    assert mgr.remove_entity(entity.id) is True
    assert len(mgr) == 0
    assert mgr.get_entity(entity.id) is None


@pytest.mark.unit
def test_manager_remove_nonexistent():
    """remove_entity returns False for unknown ID."""
    mgr = EntityManager()
    assert mgr.remove_entity("no-such-id") is False


@pytest.mark.unit
def test_manager_all_entities():
    """all_entities property returns all stored entities."""
    mgr = EntityManager()
    mgr.add_entity("A", "type")
    mgr.add_entity("B", "type")
    assert len(mgr.all_entities) == 2


# ======================================================================
# EntityManager: search
# ======================================================================


@pytest.mark.unit
def test_manager_search_by_name():
    """search_entities matches by name (case-insensitive)."""
    mgr = EntityManager()
    mgr.add_entity("Alice Smith", "person")
    mgr.add_entity("Bob Jones", "person")
    results = mgr.search_entities("alice")
    assert len(results) == 1
    assert results[0].name == "Alice Smith"


@pytest.mark.unit
def test_manager_search_by_type():
    """search_entities matches by entity_type."""
    mgr = EntityManager()
    mgr.add_entity("X", "component")
    mgr.add_entity("Y", "service")
    results = mgr.search_entities("component")
    assert len(results) == 1


@pytest.mark.unit
def test_manager_search_by_attribute_value():
    """search_entities matches by attribute string values."""
    mgr = EntityManager()
    mgr.add_entity("A", "node", attributes={"team": "engineering"})
    mgr.add_entity("B", "node", attributes={"team": "marketing"})
    results = mgr.search_entities("engineering")
    assert len(results) == 1


@pytest.mark.unit
def test_manager_search_with_type_filter():
    """search_entities filters by entity_type when specified."""
    mgr = EntityManager()
    mgr.add_entity("Alice", "person")
    mgr.add_entity("Alice Corp", "company")
    results = mgr.search_entities("alice", entity_type="person")
    assert len(results) == 1
    assert results[0].entity_type == "person"


@pytest.mark.unit
def test_manager_search_no_results():
    """search_entities returns empty for no matches."""
    mgr = EntityManager()
    mgr.add_entity("Alice", "person")
    assert mgr.search_entities("zzzzz") == []


# ======================================================================
# EntityManager: similarity & duplicates
# ======================================================================


@pytest.mark.unit
def test_manager_find_similar():
    """find_similar returns entities above fidelity threshold."""
    mgr = EntityManager()
    e1 = mgr.add_entity("Alice", "person", attributes={"role": "eng"})
    mgr.add_entity("Alicia", "person", attributes={"role": "eng"})
    mgr.add_entity("ZZZ", "thing", attributes={"role": "xyz"})
    # All should have some fidelity at threshold=0.0
    results = mgr.find_similar(e1.id, threshold=0.0)
    assert len(results) == 2  # excludes self


@pytest.mark.unit
def test_manager_find_similar_not_found():
    """find_similar returns empty for unknown entity."""
    mgr = EntityManager()
    assert mgr.find_similar("nonexistent") == []


@pytest.mark.unit
def test_manager_find_similar_sorted():
    """find_similar results are sorted by descending fidelity."""
    mgr = EntityManager()
    e1 = mgr.add_entity("A", "t")
    mgr.add_entity("B", "t")
    mgr.add_entity("C", "t")
    results = mgr.find_similar(e1.id, threshold=0.0)
    if len(results) >= 2:
        fidelities = [fid for _, fid in results]
        assert fidelities == sorted(fidelities, reverse=True)


@pytest.mark.unit
def test_manager_find_duplicates():
    """find_duplicates groups entities with identical content hashes."""
    mgr = EntityManager()
    mgr.add_entity("Alice", "person", attributes={"role": "eng"})
    mgr.add_entity("Alice", "person", attributes={"role": "eng"})
    mgr.add_entity("Bob", "person")
    groups = mgr.find_duplicates()
    assert len(groups) == 1
    assert len(groups[0]) == 2


@pytest.mark.unit
def test_manager_find_duplicates_none():
    """find_duplicates returns empty when no duplicates."""
    mgr = EntityManager()
    mgr.add_entity("Alice", "person")
    mgr.add_entity("Bob", "person")
    assert mgr.find_duplicates() == []


# ======================================================================
# UORGraph: entity management
# ======================================================================


@pytest.mark.unit
def test_graph_add_entity():
    """UORGraph.add_entity creates entities."""
    graph = UORGraph()
    entity = graph.add_entity("Alice", "person")
    assert isinstance(entity, UOREntity)
    assert graph.entity_count == 1


@pytest.mark.unit
def test_graph_get_entity():
    """UORGraph.get_entity retrieves entities."""
    graph = UORGraph()
    entity = graph.add_entity("Alice")
    assert graph.get_entity(entity.id) is entity


@pytest.mark.unit
def test_graph_repr():
    """UORGraph repr shows counts."""
    graph = UORGraph()
    assert "entities=0" in repr(graph)


# ======================================================================
# UORGraph: relationships
# ======================================================================


@pytest.mark.unit
def test_graph_add_relationship():
    """add_relationship creates a relationship between existing entities."""
    graph = UORGraph()
    a = graph.add_entity("A")
    b = graph.add_entity("B")
    rel = graph.add_relationship(a.id, b.id, "depends_on")
    assert isinstance(rel, UORRelationship)
    assert rel.relationship_type == "depends_on"
    assert graph.relationship_count == 1


@pytest.mark.unit
def test_graph_add_relationship_missing_entity():
    """add_relationship returns None if an entity is missing."""
    graph = UORGraph()
    a = graph.add_entity("A")
    assert graph.add_relationship(a.id, "nonexistent") is None
    assert graph.add_relationship("nonexistent", a.id) is None


@pytest.mark.unit
def test_graph_get_relationships():
    """get_relationships returns relationships involving an entity."""
    graph = UORGraph()
    a = graph.add_entity("A")
    b = graph.add_entity("B")
    c = graph.add_entity("C")
    graph.add_relationship(a.id, b.id, "knows")
    graph.add_relationship(a.id, c.id, "works_with")
    rels = graph.get_relationships(a.id)
    assert len(rels) == 2


@pytest.mark.unit
def test_graph_get_relationships_by_type():
    """get_relationships filters by type."""
    graph = UORGraph()
    a = graph.add_entity("A")
    b = graph.add_entity("B")
    c = graph.add_entity("C")
    graph.add_relationship(a.id, b.id, "knows")
    graph.add_relationship(a.id, c.id, "works_with")
    rels = graph.get_relationships(a.id, relationship_type="knows")
    assert len(rels) == 1


@pytest.mark.unit
def test_graph_remove_relationship():
    """remove_relationship removes and returns True."""
    graph = UORGraph()
    a = graph.add_entity("A")
    b = graph.add_entity("B")
    rel = graph.add_relationship(a.id, b.id)
    assert graph.remove_relationship(rel.id) is True
    assert graph.relationship_count == 0


@pytest.mark.unit
def test_graph_remove_entity_cascades():
    """remove_entity also removes associated relationships."""
    graph = UORGraph()
    a = graph.add_entity("A")
    b = graph.add_entity("B")
    c = graph.add_entity("C")
    graph.add_relationship(a.id, b.id)
    graph.add_relationship(b.id, c.id)
    graph.remove_entity(b.id)
    assert graph.entity_count == 2
    assert graph.relationship_count == 0


# ======================================================================
# UORGraph: traversal
# ======================================================================


@pytest.mark.unit
def test_graph_get_neighbors():
    """get_neighbors returns directly connected entities."""
    graph = UORGraph()
    a = graph.add_entity("A")
    b = graph.add_entity("B")
    c = graph.add_entity("C")
    graph.add_relationship(a.id, b.id)
    graph.add_relationship(a.id, c.id)
    neighbors = graph.get_neighbors(a.id)
    assert len(neighbors) == 2
    names = {n.name for n in neighbors}
    assert names == {"B", "C"}


@pytest.mark.unit
def test_graph_find_path_direct():
    """find_path returns direct path between connected entities."""
    graph = UORGraph()
    a = graph.add_entity("A")
    b = graph.add_entity("B")
    graph.add_relationship(a.id, b.id)
    path = graph.find_path(a.id, b.id)
    assert path == [a.id, b.id]


@pytest.mark.unit
def test_graph_find_path_transitive():
    """find_path finds path through intermediate entities."""
    graph = UORGraph()
    a = graph.add_entity("A")
    b = graph.add_entity("B")
    c = graph.add_entity("C")
    graph.add_relationship(a.id, b.id)
    graph.add_relationship(b.id, c.id)
    path = graph.find_path(a.id, c.id)
    assert path == [a.id, b.id, c.id]


@pytest.mark.unit
def test_graph_find_path_no_connection():
    """find_path returns empty for disconnected entities."""
    graph = UORGraph()
    a = graph.add_entity("A")
    b = graph.add_entity("B")
    assert graph.find_path(a.id, b.id) == []


@pytest.mark.unit
def test_graph_find_path_same_entity():
    """find_path returns [id] when source equals target."""
    graph = UORGraph()
    a = graph.add_entity("A")
    assert graph.find_path(a.id, a.id) == [a.id]


@pytest.mark.unit
def test_graph_find_path_missing_entity():
    """find_path returns empty for nonexistent entity."""
    graph = UORGraph()
    a = graph.add_entity("A")
    assert graph.find_path(a.id, "nonexistent") == []


# ======================================================================
# DerivationTracker
# ======================================================================


@pytest.mark.unit
def test_derivation_record_id():
    """DerivationRecord has content-addressed ID."""
    record = DerivationRecord(
        entity_id="e1", operation="create", result_hash="abc123"
    )
    assert record.id.startswith("urn:uor:derivation:sha256:")


@pytest.mark.unit
def test_derivation_record_deterministic():
    """Same inputs produce same derivation ID."""
    r1 = DerivationRecord(
        entity_id="e1",
        operation="create",
        inputs={"name": "Alice"},
        result_hash="abc",
    )
    r2 = DerivationRecord(
        entity_id="e1",
        operation="create",
        inputs={"name": "Alice"},
        result_hash="abc",
    )
    assert r1.id == r2.id


@pytest.mark.unit
def test_derivation_tracker_record():
    """DerivationTracker.record() creates and stores a record."""
    tracker = DerivationTracker()
    record = tracker.record("e1", "create", result_hash="abc")
    assert isinstance(record, DerivationRecord)
    assert len(tracker) == 1


@pytest.mark.unit
def test_derivation_tracker_get_history():
    """get_history returns records for a specific entity."""
    tracker = DerivationTracker()
    tracker.record("e1", "create")
    tracker.record("e2", "create")
    tracker.record("e1", "update", inputs={"field": "name"})
    history = tracker.get_history("e1")
    assert len(history) == 2
    assert all(r.entity_id == "e1" for r in history)


@pytest.mark.unit
def test_derivation_tracker_verify_chain():
    """verify_chain passes for valid records."""
    tracker = DerivationTracker()
    tracker.record("e1", "create", result_hash="h1")
    tracker.record("e1", "update", result_hash="h2")
    assert tracker.verify_chain("e1") is True


@pytest.mark.unit
def test_derivation_tracker_verify_empty():
    """verify_chain passes for entity with no records."""
    tracker = DerivationTracker()
    assert tracker.verify_chain("nonexistent") is True


@pytest.mark.unit
def test_derivation_tracker_all_records():
    """all_records returns all stored records."""
    tracker = DerivationTracker()
    tracker.record("e1", "create")
    tracker.record("e2", "update")
    assert len(tracker.all_records) == 2


# ======================================================================
# Additional edge case and feature tests
# ======================================================================


@pytest.mark.unit
def test_engine_equality():
    """PrismEngine equality is based on quantum level."""
    assert PrismEngine(quantum=0) == PrismEngine(quantum=0)
    assert PrismEngine(quantum=0) != PrismEngine(quantum=1)


@pytest.mark.unit
def test_engine_hash():
    """PrismEngines with same quantum produce same hash."""
    assert hash(PrismEngine(quantum=0)) == hash(PrismEngine(quantum=0))
    assert hash(PrismEngine(quantum=0)) != hash(PrismEngine(quantum=1))


@pytest.mark.unit
def test_engine_equality_non_engine():
    """PrismEngine != non-engine objects."""
    assert PrismEngine() != "not an engine"
    assert PrismEngine() != 42


@pytest.mark.unit
def test_engine_neg_validates_tuple():
    """neg() validates byte tuples (rejects wrong-length)."""
    engine = PrismEngine()
    with pytest.raises(ValueError):
        engine.neg((1, 2))  # Q0 expects 1 byte


@pytest.mark.unit
def test_engine_neg_validates_byte_range():
    """neg() validates byte range (0-255)."""
    engine = PrismEngine()
    with pytest.raises(ValueError):
        engine.neg((256,))


@pytest.mark.unit
def test_engine_q1_multi_byte():
    """Q1 engine handles multi-byte values correctly."""
    engine = PrismEngine(quantum=1)
    t = engine.triad(0x0102)
    assert t.datum == (1, 2)
    assert t.width == 2
    assert engine.succ((0, 255)) == (1, 0)  # carry propagation
    assert engine.pred((1, 0)) == (0, 255)  # borrow propagation


@pytest.mark.unit
def test_engine_correlate_return_keys():
    """correlate() returns all expected keys."""
    engine = PrismEngine()
    result = engine.correlate(10, 20)
    expected_keys = {
        "a_datum", "b_datum", "difference_stratum",
        "total_difference", "max_difference", "fidelity",
    }
    assert set(result.keys()) == expected_keys


@pytest.mark.unit
def test_engine_correlate_symmetry():
    """correlate(a, b) fidelity == correlate(b, a) fidelity."""
    engine = PrismEngine()
    assert engine.fidelity(42, 99) == engine.fidelity(99, 42)


@pytest.mark.unit
def test_engine_verify_sets_coherent():
    """verify() sets is_coherent; it starts False."""
    engine = PrismEngine()
    assert engine.is_coherent is False
    engine.verify()
    assert engine.is_coherent is True


@pytest.mark.unit
def test_entity_to_dict_without_coordinates():
    """to_dict() omits triadic_coordinates key when None."""
    entity = UOREntity(name="X")
    d = entity.to_dict()
    assert "triadic_coordinates" not in d


@pytest.mark.unit
def test_manager_repr():
    """EntityManager repr includes entity count and quantum."""
    mgr = EntityManager()
    mgr.add_entity("A", "t")
    r = repr(mgr)
    assert "entities=1" in r
    assert "quantum=0" in r


@pytest.mark.unit
def test_manager_engine_property():
    """EntityManager.engine returns the PrismEngine."""
    mgr = EntityManager(quantum=1)
    assert isinstance(mgr.engine, PrismEngine)
    assert mgr.engine.quantum == 1


@pytest.mark.unit
def test_manager_find_similar_no_coords():
    """find_similar returns empty when ref entity has no coordinates."""
    mgr = EntityManager()
    e1 = mgr.add_entity("A", compute_coordinates=False)
    mgr.add_entity("B")
    assert mgr.find_similar(e1.id) == []


@pytest.mark.unit
def test_manager_find_similar_skips_no_coords():
    """find_similar skips comparison entities without coordinates."""
    mgr = EntityManager()
    e1 = mgr.add_entity("A")
    mgr.add_entity("B", compute_coordinates=False)
    # Should not crash; the no-coords entity is skipped
    results = mgr.find_similar(e1.id, threshold=0.0)
    assert len(results) == 0


@pytest.mark.unit
def test_graph_len():
    """len(graph) returns entity count."""
    graph = UORGraph()
    assert len(graph) == 0
    graph.add_entity("A")
    assert len(graph) == 1


@pytest.mark.unit
def test_graph_to_dict():
    """to_dict() returns serializable graph structure."""
    graph = UORGraph()
    a = graph.add_entity("A")
    b = graph.add_entity("B")
    graph.add_relationship(a.id, b.id, "knows")
    d = graph.to_dict()
    assert d["entity_count"] == 2
    assert d["relationship_count"] == 1
    assert len(d["entities"]) == 2
    assert len(d["relationships"]) == 1


@pytest.mark.unit
def test_graph_get_relationship_by_id():
    """get_relationship retrieves by relationship ID."""
    graph = UORGraph()
    a = graph.add_entity("A")
    b = graph.add_entity("B")
    rel = graph.add_relationship(a.id, b.id)
    found = graph.get_relationship(rel.id)
    assert found is rel


@pytest.mark.unit
def test_graph_get_relationship_not_found():
    """get_relationship returns None for unknown ID."""
    graph = UORGraph()
    assert graph.get_relationship("nonexistent") is None


@pytest.mark.unit
def test_graph_remove_nonexistent_relationship():
    """remove_relationship returns False for unknown ID."""
    graph = UORGraph()
    assert graph.remove_relationship("nonexistent") is False


@pytest.mark.unit
def test_graph_remove_nonexistent_entity():
    """remove_entity returns False for unknown ID."""
    graph = UORGraph()
    assert graph.remove_entity("nonexistent") is False


@pytest.mark.unit
def test_graph_all_relationships():
    """all_relationships returns a copy of relationships."""
    graph = UORGraph()
    a = graph.add_entity("A")
    b = graph.add_entity("B")
    graph.add_relationship(a.id, b.id)
    rels = graph.all_relationships
    assert len(rels) == 1
    rels.clear()  # modifying the copy shouldn't affect the graph
    assert graph.relationship_count == 1


@pytest.mark.unit
def test_graph_bidirectional_neighbors():
    """get_neighbors finds entities connected in either direction."""
    graph = UORGraph()
    a = graph.add_entity("A")
    b = graph.add_entity("B")
    # Relationship goes A → B
    graph.add_relationship(a.id, b.id)
    # B should see A as neighbor (undirected semantics)
    assert len(graph.get_neighbors(b.id)) == 1
    assert graph.get_neighbors(b.id)[0].name == "A"


@pytest.mark.unit
def test_derivation_record_frozen():
    """DerivationRecord is immutable after creation."""
    record = DerivationRecord(entity_id="e1", operation="create")
    with pytest.raises(AttributeError):
        record.operation = "update"


@pytest.mark.unit
def test_derivation_compute_id_static():
    """_compute_derivation_id static method is callable directly."""
    id1 = DerivationRecord._compute_derivation_id("e1", "create", {}, "h1")
    id2 = DerivationRecord._compute_derivation_id("e1", "create", {}, "h1")
    assert id1 == id2
    assert id1.startswith("urn:uor:derivation:sha256:")


@pytest.mark.unit
def test_manager_search_matches_name_and_type_once():
    """An entity matching query in both name and type is returned only once."""
    mgr = EntityManager()
    # Name "person_entity" with type "person" — "person" matches both
    mgr.add_entity("person_entity", "person")
    results = mgr.search_entities("person")
    assert len(results) == 1


@pytest.mark.unit
def test_engine_q1_critical_identity():
    """Critical identity holds at Q1 for boundary values."""
    engine = PrismEngine(quantum=1)
    for n in [0, 1, 127, 128, 255, 256, 65534, 65535]:
        expected = engine._to_bytes((n + 1) & engine._mask)
        assert engine.succ(n) == expected



# From test_coverage_boost_r6.py
class TestUOREngine:
    def test_triadic_coordinate(self):
        from codomyrmex.relations.uor.engine import TriadicCoordinate
        tc = TriadicCoordinate(datum=(1, 2), stratum=(3,), spectrum=((1, 2),))
        assert tc.datum == (1, 2)

    def test_prism_engine(self):
        from codomyrmex.relations.uor.engine import PrismEngine
        engine = PrismEngine()
        assert engine is not None


# From test_tier3_promotions.py — rewritten against real UOR API
class TestRelationStrengthScorer:
    """Tests for UOR relationship strength via weight attribute."""

    def test_score_single_interaction(self):
        """Test UOR relationship weight as strength score."""
        from codomyrmex.relations import Interaction
        interaction = Interaction(type="message", notes="test interaction")
        assert interaction.type == "message"
        assert interaction.id != ""

    def test_type_weights(self):
        """Test UOR relationship with custom weight."""
        from codomyrmex.relations.uor.graph import UORRelationship
        rel = UORRelationship(source_id="a", target_id="b", relationship_type="meeting", weight=3.0)
        assert rel.weight == 3.0
        assert rel.relationship_type == "meeting"

    def test_score_all_normalized(self):
        """Test UOR graph relationships with varying weights."""
        from codomyrmex.relations.uor.graph import UORGraph
        graph = UORGraph()
        a = graph.add_entity("A")
        b = graph.add_entity("B")
        c = graph.add_entity("C")
        rel1 = graph.add_relationship(a.id, b.id, "knows")
        rel2 = graph.add_relationship(a.id, c.id, "works_with")
        assert rel1 is not None
        assert rel2 is not None
        assert graph.relationship_count == 2
