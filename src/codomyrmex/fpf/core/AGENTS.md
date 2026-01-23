# Codomyrmex Agents - src/codomyrmex/fpf/core

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

Core module for FPF (First Principles Framework) specification processing. Provides parsing of FPF markdown specifications into structured data models, extraction of patterns, concepts, and relationships, and context building for prompt engineering. This module forms the foundation for all FPF analysis and integration capabilities.

## Active Components

- `parser.py` - FPF markdown parser (FPFParser)
- `extractor.py` - Pattern, concept, and relationship extractor (FPFExtractor)
- `context_builder.py` - Context builder for prompt engineering (ContextBuilder)
- `models.py` - Data models (FPFSpec, Pattern, Concept, Relationship, FPFIndex, enums)

## Key Classes

### FPFParser (parser.py)
Parser for FPF specification markdown files:
- `parse_spec()`: Parse complete FPF specification from markdown content
  - Extracts version, patterns, and table of contents
  - Returns FPFSpec object with all parsed data
- `extract_table_of_contents()`: Parse TOC structure with parts and sections
- `extract_patterns()`: Extract all patterns with headers, sections, metadata
- `extract_sections()`: Parse sections within a pattern's content
- `_extract_status()`: Determine pattern status (Stable, Draft, Stub, New)
- `_extract_pattern_metadata()`: Extract keywords, queries, dependencies

Pattern header regex: `^##\s+([A-Z]\.\d+(?:\.\d+)?(?:\.[A-Z])?)\s*[-–]\s*(.+)$`
Dependency types extracted: builds_on, prerequisite_for, coordinates_with, constrains

### FPFExtractor (extractor.py)
Extractor for FPF patterns, concepts, and relationships:
- `extract_patterns()`: Return patterns with enhanced metadata
- `extract_concepts()`: Extract U.Types, architheories, mechanisms, principles
  - `_extract_u_types()`: Find U.* type references
  - `_extract_other_concepts()`: Find named concepts by type
  - `_extract_definition()`: Get definition from pattern content
  - `_find_references()`: Find patterns referencing each concept
- `extract_relationships()`: Build relationship list from dependencies
  - Supports: BUILDS_ON, PREREQUISITE_FOR, COORDINATES_WITH, CONSTRAINS, REFINES, INFORMS, USED_BY
- `extract_keywords()`: Index keywords by pattern ID
- `extract_dependencies()`: Extract dependency graph

### ContextBuilder (context_builder.py)
Builder for prompt engineering contexts from FPF specifications:
- `build_context_for_pattern()`: Generate context string for specific pattern
  - Includes status, keywords, dependencies, problem/solution sections
  - Optionally includes related patterns up to specified depth
- `build_context_for_concept()`: Generate context for concept lookup
  - Matches concepts by name with type and definition
- `build_minimal_context()`: Compact context with pattern summaries
  - Supports filters by part, status, pattern_ids
- `build_full_context()`: Complete context with all patterns and concepts
- `_get_related_patterns()`: Traverse dependencies to find related patterns

### Data Models (models.py)

**FPFSpec**: Complete specification container
- `version`, `source_url`, `source_hash`, `last_updated`
- `patterns`: List of Pattern objects
- `concepts`: List of Concept objects
- `relationships`: List of Relationship objects
- `table_of_contents`, `metadata`
- `get_pattern_by_id()`, `get_concepts_by_pattern()`

**Pattern**: Individual FPF pattern
- `id`: Pattern identifier (e.g., "A.1", "B.2.3")
- `title`: Pattern title
- `status`: PatternStatus enum (STABLE, DRAFT, STUB, NEW)
- `part`: Part identifier (A, B, C, etc.)
- `content`: Full markdown content
- `sections`: Dictionary of section name to content
- `keywords`, `search_queries`, `dependencies`

**Concept**: Named concept extracted from patterns
- `name`, `definition`, `pattern_id`, `type`, `references`, `aliases`
- ConceptType: U_TYPE, ARCHITHEORY, MECHANISM, PRINCIPLE, OTHER

**Relationship**: Dependency between patterns
- `source`, `target`, `type`, `strength`, `description`
- RelationshipType: BUILDS_ON, PREREQUISITE_FOR, COORDINATES_WITH, etc.

**FPFIndex**: Search index for patterns and concepts
- `pattern_index`, `concept_index`, `keyword_index`
- `title_index`, `relationship_graph`
- `search_patterns()`, `get_pattern()`, `get_related_patterns()`

## Operating Contracts

- Maintain alignment between code, documentation, and configured workflows
- FPF markdown must follow standard pattern header format (## A.1 - Title)
- Pattern IDs follow format: Letter.Number[.Number][.Letter]
- Section names are normalized to lowercase with underscores
- Dependencies are extracted from bold markers (**Builds on:** etc.)
- Context strings are truncated for prompt size management
- Ensure Model Context Protocol interfaces remain available for sibling agents
- Record outcomes in shared telemetry and update TODO queues when necessary

## Signposting

- **Analysis Module**: `../analysis/` - FPFAnalyzer, FPFIndexer, TermAnalyzer for advanced analysis
- **IO Module**: `../io/` - FPFFetcher, FPFExporter, SectionManager for I/O operations
- **Visualization Module**: `../visualization/` - FPFVisualizer, GraphGenerator for rendering
- **CEREBRUM Integration**: `../../cerebrum/fpf/` - CEREBRUM methods applied to FPF
- **Parent Directory**: [fpf](../README.md) - FPF package documentation
- **Project Root**: ../../../../README.md - Main project documentation
