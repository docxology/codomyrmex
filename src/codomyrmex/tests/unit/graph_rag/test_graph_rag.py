"""Unit tests for graph_rag module."""
import pytest


@pytest.mark.unit
class TestGraphRagImports:
    """Test suite for graph_rag module imports."""

    def test_module_imports(self):
        """Verify module can be imported without errors."""
        from codomyrmex import graph_rag
        assert graph_rag is not None

    def test_public_api_exists(self):
        """Verify expected public API is available."""
        from codomyrmex.graph_rag import __all__
        expected_exports = [
            "EntityType",
            "RelationType",
            "Entity",
            "Relationship",
            "GraphContext",
            "KnowledgeGraph",
            "GraphRAGPipeline",
        ]
        for export in expected_exports:
            assert export in __all__, f"Missing export: {export}"


@pytest.mark.unit
class TestEntityType:
    """Test suite for EntityType enum."""

    def test_entity_type_values(self):
        """Verify all entity types are available."""
        from codomyrmex.graph_rag import EntityType

        assert EntityType.PERSON.value == "person"
        assert EntityType.ORGANIZATION.value == "organization"
        assert EntityType.LOCATION.value == "location"
        assert EntityType.CONCEPT.value == "concept"
        assert EntityType.EVENT.value == "event"
        assert EntityType.DOCUMENT.value == "document"
        assert EntityType.CUSTOM.value == "custom"


@pytest.mark.unit
class TestRelationType:
    """Test suite for RelationType enum."""

    def test_relation_type_values(self):
        """Verify all relation types are available."""
        from codomyrmex.graph_rag import RelationType

        assert RelationType.IS_A.value == "is_a"
        assert RelationType.PART_OF.value == "part_of"
        assert RelationType.RELATED_TO.value == "related_to"
        assert RelationType.AUTHORED_BY.value == "authored_by"
        assert RelationType.LOCATED_IN.value == "located_in"


@pytest.mark.unit
class TestEntity:
    """Test suite for Entity dataclass."""

    def test_entity_creation(self):
        """Verify Entity can be created."""
        from codomyrmex.graph_rag import Entity, EntityType

        entity = Entity(
            id="anthropic",
            name="Anthropic",
            entity_type=EntityType.ORGANIZATION,
        )

        assert entity.id == "anthropic"
        assert entity.name == "Anthropic"
        assert entity.entity_type == EntityType.ORGANIZATION

    def test_entity_key_property(self):
        """Verify entity key generation."""
        from codomyrmex.graph_rag import Entity, EntityType

        entity = Entity(id="python", name="Python", entity_type=EntityType.CONCEPT)
        assert entity.key == "concept:python"

    def test_entity_to_dict(self):
        """Verify entity serialization."""
        from codomyrmex.graph_rag import Entity, EntityType

        entity = Entity(
            id="sf",
            name="San Francisco",
            entity_type=EntityType.LOCATION,
            properties={"country": "USA"},
        )

        result = entity.to_dict()
        assert result["id"] == "sf"
        assert result["entity_type"] == "location"
        assert result["properties"]["country"] == "USA"


@pytest.mark.unit
class TestRelationship:
    """Test suite for Relationship dataclass."""

    def test_relationship_creation(self):
        """Verify Relationship can be created."""
        from codomyrmex.graph_rag import Relationship, RelationType

        rel = Relationship(
            source_id="anthropic",
            target_id="sf",
            relation_type=RelationType.LOCATED_IN,
        )

        assert rel.source_id == "anthropic"
        assert rel.target_id == "sf"
        assert rel.weight == 1.0

    def test_relationship_key_property(self):
        """Verify relationship key generation."""
        from codomyrmex.graph_rag import Relationship, RelationType

        rel = Relationship(
            source_id="A",
            target_id="B",
            relation_type=RelationType.RELATED_TO,
        )
        assert rel.key == "A-related_to->B"


@pytest.mark.unit
class TestGraphContext:
    """Test suite for GraphContext dataclass."""

    def test_context_creation(self):
        """Verify GraphContext can be created."""
        from codomyrmex.graph_rag import Entity, EntityType, GraphContext

        context = GraphContext(
            query="Who is the CEO?",
            entities=[Entity(id="test", name="Test", entity_type=EntityType.PERSON)],
            relationships=[],
        )

        assert context.query == "Who is the CEO?"
        assert len(context.entities) == 1

    def test_context_entity_names(self):
        """Verify entity names property."""
        from codomyrmex.graph_rag import Entity, EntityType, GraphContext

        context = GraphContext(
            query="test",
            entities=[
                Entity(id="1", name="Alice", entity_type=EntityType.PERSON),
                Entity(id="2", name="Bob", entity_type=EntityType.PERSON),
            ],
            relationships=[],
        )

        assert context.entity_names == ["Alice", "Bob"]

    def test_context_to_text(self):
        """Verify text representation."""
        from codomyrmex.graph_rag import (
            Entity,
            EntityType,
            GraphContext,
            Relationship,
            RelationType,
        )

        context = GraphContext(
            query="test",
            entities=[Entity(id="py", name="Python", entity_type=EntityType.CONCEPT)],
            relationships=[Relationship("py", "lang", RelationType.IS_A)],
        )

        text = context.to_text()
        assert "Knowledge Graph Context" in text
        assert "Python" in text


@pytest.mark.unit
class TestKnowledgeGraph:
    """Test suite for KnowledgeGraph."""

    def test_graph_add_entity(self):
        """Verify entities can be added."""
        from codomyrmex.graph_rag import Entity, EntityType, KnowledgeGraph

        graph = KnowledgeGraph()
        entity = Entity(id="test", name="Test", entity_type=EntityType.CONCEPT)

        graph.add_entity(entity)

        assert graph.entity_count == 1
        assert graph.get_entity("test") is not None

    def test_graph_add_relationship(self):
        """Verify relationships can be added."""
        from codomyrmex.graph_rag import (
            Entity,
            EntityType,
            KnowledgeGraph,
            Relationship,
            RelationType,
        )

        graph = KnowledgeGraph()
        graph.add_entity(Entity(id="A", name="A", entity_type=EntityType.CONCEPT))
        graph.add_entity(Entity(id="B", name="B", entity_type=EntityType.CONCEPT))
        graph.add_relationship(Relationship("A", "B", RelationType.RELATED_TO))

        assert graph.relationship_count == 1

    def test_graph_get_neighbors(self):
        """Verify neighbor retrieval."""
        from codomyrmex.graph_rag import (
            Entity,
            EntityType,
            KnowledgeGraph,
            Relationship,
            RelationType,
        )

        graph = KnowledgeGraph()
        graph.add_entity(Entity(id="center", name="Center", entity_type=EntityType.CONCEPT))
        graph.add_entity(Entity(id="neighbor1", name="N1", entity_type=EntityType.CONCEPT))
        graph.add_entity(Entity(id="neighbor2", name="N2", entity_type=EntityType.CONCEPT))

        graph.add_relationship(Relationship("center", "neighbor1", RelationType.RELATED_TO))
        graph.add_relationship(Relationship("center", "neighbor2", RelationType.RELATED_TO))

        neighbors = graph.get_neighbors("center", direction="out")
        neighbor_ids = [n.id for n in neighbors]

        assert "neighbor1" in neighbor_ids
        assert "neighbor2" in neighbor_ids

    def test_graph_find_path(self):
        """Verify path finding."""
        from codomyrmex.graph_rag import (
            Entity,
            EntityType,
            KnowledgeGraph,
            Relationship,
            RelationType,
        )

        graph = KnowledgeGraph()
        graph.add_entity(Entity(id="A", name="A", entity_type=EntityType.CONCEPT))
        graph.add_entity(Entity(id="B", name="B", entity_type=EntityType.CONCEPT))
        graph.add_entity(Entity(id="C", name="C", entity_type=EntityType.CONCEPT))

        graph.add_relationship(Relationship("A", "B", RelationType.RELATED_TO))
        graph.add_relationship(Relationship("B", "C", RelationType.RELATED_TO))

        path = graph.find_path("A", "C")
        assert path == ["A", "B", "C"]

    def test_graph_search_entities(self):
        """Verify entity search."""
        from codomyrmex.graph_rag import Entity, EntityType, KnowledgeGraph

        graph = KnowledgeGraph()
        graph.add_entity(Entity(id="py", name="Python", entity_type=EntityType.CONCEPT))
        graph.add_entity(Entity(id="java", name="Java", entity_type=EntityType.CONCEPT))
        graph.add_entity(Entity(id="js", name="JavaScript", entity_type=EntityType.CONCEPT))

        results = graph.search_entities("Python")
        assert len(results) == 1
        assert results[0].id == "py"

    def test_graph_subgraph_extraction(self):
        """Verify subgraph extraction."""
        from codomyrmex.graph_rag import (
            Entity,
            EntityType,
            KnowledgeGraph,
            Relationship,
            RelationType,
        )

        graph = KnowledgeGraph()
        graph.add_entity(Entity(id="A", name="A", entity_type=EntityType.CONCEPT))
        graph.add_entity(Entity(id="B", name="B", entity_type=EntityType.CONCEPT))
        graph.add_entity(Entity(id="C", name="C", entity_type=EntityType.CONCEPT))
        graph.add_entity(Entity(id="D", name="D", entity_type=EntityType.CONCEPT))

        graph.add_relationship(Relationship("A", "B", RelationType.RELATED_TO))
        graph.add_relationship(Relationship("B", "C", RelationType.RELATED_TO))
        graph.add_relationship(Relationship("C", "D", RelationType.RELATED_TO))

        subgraph = graph.subgraph(["B"], include_neighbors=True)

        # Should include B and its neighbors A and C
        assert subgraph.entity_count >= 2


@pytest.mark.unit
class TestGraphRAGPipeline:
    """Test suite for GraphRAGPipeline."""

    def test_pipeline_creation(self):
        """Verify pipeline can be created."""
        from codomyrmex.graph_rag import GraphRAGPipeline, KnowledgeGraph

        graph = KnowledgeGraph()
        pipeline = GraphRAGPipeline(graph=graph)

        assert pipeline.graph is graph

    def test_pipeline_extract_entities(self):
        """Verify entity extraction from query."""
        from codomyrmex.graph_rag import (
            Entity,
            EntityType,
            GraphRAGPipeline,
            KnowledgeGraph,
        )

        graph = KnowledgeGraph()
        graph.add_entity(Entity(id="python", name="Python", entity_type=EntityType.CONCEPT))
        graph.add_entity(Entity(id="java", name="Java", entity_type=EntityType.CONCEPT))

        pipeline = GraphRAGPipeline(graph=graph)
        entities = pipeline.extract_entities("Tell me about Python programming")

        assert "python" in entities

    def test_pipeline_retrieve(self):
        """Verify context retrieval."""
        from codomyrmex.graph_rag import (
            Entity,
            EntityType,
            GraphRAGPipeline,
            KnowledgeGraph,
            Relationship,
            RelationType,
        )

        graph = KnowledgeGraph()
        graph.add_entity(Entity(id="ml", name="Machine Learning", entity_type=EntityType.CONCEPT))
        graph.add_entity(Entity(id="ai", name="Artificial Intelligence", entity_type=EntityType.CONCEPT))
        graph.add_relationship(Relationship("ml", "ai", RelationType.PART_OF))

        pipeline = GraphRAGPipeline(graph=graph)
        context = pipeline.retrieve("What is Machine Learning?")

        assert context.query == "What is Machine Learning?"
        assert len(context.entities) > 0

    def test_pipeline_combine_context(self):
        """Verify context combination."""
        from codomyrmex.graph_rag import (
            Entity,
            EntityType,
            GraphContext,
            GraphRAGPipeline,
            KnowledgeGraph,
        )

        graph = KnowledgeGraph()
        pipeline = GraphRAGPipeline(graph=graph)

        graph_context = GraphContext(
            query="test",
            entities=[Entity(id="1", name="Test", entity_type=EntityType.CONCEPT)],
            relationships=[],
        )

        text_context = "This is some document text."

        combined = pipeline.combine_context(graph_context, text_context)

        assert "Knowledge Graph Context" in combined
        assert "Document Context" in combined
        assert text_context in combined
