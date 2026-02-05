# graph_rag

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Knowledge graph-enhanced Retrieval-Augmented Generation (RAG) with entity relationships. Provides an in-memory knowledge graph for storing entities and typed relationships, with neighbor traversal, BFS shortest-path finding, subgraph extraction, and text search. The `GraphRAGPipeline` retrieves structured graph context from queries and formats it as text for LLM consumption, combining entity/relationship knowledge with traditional document context.

## Key Exports

### Enums

- **`EntityType`** -- Types of entities: PERSON, ORGANIZATION, LOCATION, CONCEPT, EVENT, DOCUMENT, CUSTOM
- **`RelationType`** -- Types of relationships: IS_A, PART_OF, RELATED_TO, AUTHORED_BY, LOCATED_IN, OCCURRED_ON, REFERENCES, CUSTOM

### Data Classes

- **`Entity`** -- An entity in the knowledge graph with ID, name, type, properties, and optional embedding vector; provides a unique `key` property
- **`Relationship`** -- A weighted, directed relationship between two entities with type, properties, and a unique `key` property
- **`GraphContext`** -- Context retrieved from the knowledge graph for a query; contains matched entities, relationships, and paths; includes `to_text()` for generating LLM-ready text representation

### Services

- **`KnowledgeGraph`** -- Thread-safe in-memory knowledge graph; supports entity and relationship CRUD, bidirectional neighbor traversal, BFS shortest-path finding, subgraph extraction with optional neighbor expansion, and case-insensitive entity search by name
- **`GraphRAGPipeline`** -- RAG pipeline enhanced with knowledge graph context; extracts entities from queries via word matching and text search, expands to neighbors, collects inter-entity relationships, and combines graph context with document context for LLM prompts

## Directory Contents

- `__init__.py` -- Module implementation with knowledge graph, RAG pipeline, and data models
- `README.md` -- This file
- `AGENTS.md` -- Agent integration documentation
- `API_SPECIFICATION.md` -- Programmatic API specification
- `MCP_TOOL_SPECIFICATION.md` -- Model Context Protocol tool definitions
- `PAI.md` -- PAI integration notes
- `SPEC.md` -- Module specification
- `py.typed` -- PEP 561 type stub marker

## Navigation

- **Full Documentation**: [docs/modules/graph_rag/](../../../docs/modules/graph_rag/)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
