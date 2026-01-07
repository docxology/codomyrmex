# Codomyrmex Agents — src/codomyrmex/fpf

## Signposting
- **Parent**: [codomyrmex](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - [tests](tests/AGENTS.md)
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose
Functional interface for working with the First Principles Framework specification. Transforms the static FPF markdown specification into a machine-readable, queryable, and exportable format for use in prompt/context engineering and other applications. Provides fetching, parsing, extraction, indexing, search, export, and visualization capabilities.

## Active Components
- `API_SPECIFICATION.md` – Detailed API specification
- `FPF-Spec.md` – FPF specification document
- `MCP_TOOL_SPECIFICATION.md` – MCP tool specification
- `README.md` – Project file
- `SPEC.md` – Project file
- `__init__.py` – Module exports and public API
- `analyzer.py` – FPF specification analysis
- `context_builder.py` – Context string building for prompts
- `exporter.py` – Export to various formats
- `extractor.py` – Extract patterns, concepts, relationships
- `fetcher.py` – Fetch from GitHub
- `graph_generator.py` – Generate relationship graphs
- `indexer.py` – Build search indexes
- `models.py` – Data models (FPFSpec, Pattern, Concept, Relationship)
- `parser.py` – Parse markdown specification
- `report_generator.py` – Generate analysis reports
- `requirements.txt` – Project file
- `section_exporter.py` – Export sections
- `section_importer.py` – Import sections
- `section_manager.py` – Section management
- `term_analyzer.py` – Term analysis
- `tests/` – Directory containing tests components
- `visualizer.py` – Visualization
- `visualizer_png.py` – PNG visualization

## Key Classes and Functions

### FPFClient (`__init__.py`)
- `FPFClient(spec_path: str = None)` – High-level client for working with FPF specifications
- `load_from_file(file_path: str) -> FPFSpec` – Load and parse from local file
- `fetch_and_load(repo: str = "ailev/FPF", branch: str = "main") -> FPFSpec` – Fetch from GitHub and load
- `search(query: str, filters: dict = None) -> list[Pattern]` – Search for patterns
- `get_pattern(pattern_id: str) -> Pattern` – Get pattern by ID
- `export_json(output_path: str) -> None` – Export to JSON
- `build_context(pattern_id: str = None, filters: dict = None) -> str` – Build context string

### FPFParser (`parser.py`)
- `FPFParser()` – Parse markdown FPF specification
- `parse_spec(content: str, source_path: str = None) -> FPFSpec` – Parse specification content

### FPFExtractor (`extractor.py`)
- `FPFExtractor()` – Extract patterns, concepts, relationships
- `extract_concepts(spec: FPFSpec) -> list[Concept]` – Extract concepts
- `extract_relationships(spec: FPFSpec) -> list[Relationship]` – Extract relationships

### FPFIndexer (`indexer.py`)
- `FPFIndexer()` – Build search indexes
- `build_index(spec: FPFSpec) -> None` – Build search index
- `search_patterns(query: str, filters: dict = None) -> list[Pattern]` – Search patterns
- `get_pattern_by_id(pattern_id: str) -> Optional[Pattern]` – Get pattern by ID

### FPFFetcher (`fetcher.py`)
- `FPFFetcher()` – Fetch from GitHub
- `fetch_latest(repo: str, branch: str) -> str` – Fetch latest specification

### FPFExporter (`exporter.py`)
- `FPFExporter()` – Export to various formats
- `export_json(spec: FPFSpec, output_path: Path) -> None` – Export to JSON

### ContextBuilder (`context_builder.py`)
- `ContextBuilder(spec: FPFSpec)` – Build context strings for prompts
- `build_context_for_pattern(pattern_id: str) -> str` – Build context for pattern
- `build_minimal_context(filters: dict) -> str` – Build minimal context
- `build_full_context() -> str` – Build full context

### FPFVisualizer (`visualizer.py`)
- `FPFVisualizer()` – Visualize FPF specifications
- `visualize_patterns(patterns: list[Pattern]) -> str` – Visualize patterns
- `visualize_relationships(spec: FPFSpec) -> str` – Visualize relationships

### Data Models (`models.py`)
- `FPFSpec` – Complete FPF specification
- `Pattern` – Pattern with metadata
- `Concept` – Concept (U.Type, mechanism, etc.)
- `Relationship` – Relationship between patterns
- `PatternStatus` (Enum) – Pattern status
- `ConceptType` (Enum) – Concept type
- `RelationshipType` (Enum) – Relationship type

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **📁 Parent Directory**: [codomyrmex](../README.md) - Parent directory documentation
- **🏠 Project Root**: [README](../../../README.md) - Main project documentation