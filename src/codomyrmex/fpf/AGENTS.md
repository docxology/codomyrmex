# Codomyrmex Agents — src/codomyrmex/fpf

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

The First Principles Framework (FPF) module provides functionality for prompt and context engineering based on the FPF specification. It enables fetching, parsing, analyzing, indexing, and visualizing FPF patterns for use in AI-assisted code generation and reasoning tasks. The module supports loading specifications from local files or fetching from remote repositories, building searchable indexes, extracting concepts and relationships, and generating visualizations of pattern hierarchies.

## Active Components

### Core Infrastructure

- `core/` - Core parsing and extraction components
  - Key Classes: `FPFParser`, `FPFExtractor`, `ContextBuilder`
  - Key Functions: `parse_spec()`, `extract_concepts()`, `extract_relationships()`
  - Key Models: `FPFSpec`, `Pattern`, `Concept`, `Relationship`
- `__init__.py` - Module entry point with `FPFClient` high-level interface

### Analysis Components

- `analysis/` - Analysis and indexing components
  - Key Classes: `FPFIndexer`, `FPFAnalyzer`, `TermAnalyzer`, `ReportGenerator`
  - Key Functions: `build_index()`, `search_patterns()`, `get_related_patterns()`

### I/O Components

- `io/` - Input/output and fetching components
  - Key Classes: `FPFFetcher`, `FPFExporter`, `SectionManager`, `SectionImporter`, `SectionExporter`
  - Key Functions: `fetch_latest()`, `export_json()`, `cache_spec()`

### Visualization Components

- `visualization/` - Visualization and reporting
  - Key Classes: `FPFVisualizer`, `FPFVisualizerPNG`, `GraphGenerator`
  - Key Functions: `visualize_pattern_hierarchy()`, `visualize_dependencies()`, `generate_report()`

## Key Classes and Functions

| Class/Function | Module | Purpose |
| :--- | :--- | :--- |
| `FPFClient` | `__init__` | High-level client for FPF operations |
| `FPFParser` | core | Parses FPF specification markdown into structured data |
| `FPFExtractor` | core | Extracts concepts, relationships, and metadata |
| `FPFIndexer` | analysis | Builds search indexes for patterns and concepts |
| `FPFFetcher` | io | Fetches specifications from GitHub repositories |
| `FPFExporter` | io | Exports specifications to JSON format |
| `FPFVisualizer` | visualization | Generates Mermaid diagrams of pattern hierarchies |
| `ContextBuilder` | core | Builds context strings for prompt engineering |
| `FPFSpec` | core/models | Data model representing the full specification |
| `Pattern` | core/models | Data model for individual FPF patterns |
| `Concept` | core/models | Data model for extracted concepts |
| `Relationship` | core/models | Data model for pattern relationships |
| `parse_spec()` | FPFParser | Parse markdown content into FPFSpec |
| `extract_concepts()` | FPFExtractor | Extract concepts from specification |
| `build_index()` | FPFIndexer | Build searchable index from specification |
| `search_patterns()` | FPFIndexer | Search patterns by query and filters |

## Operating Contracts

1. **Logging**: All components use `logging_monitoring` for structured logging
2. **Data Models**: Use Pydantic-style dataclasses for all data structures
3. **Caching**: FPFFetcher caches fetched specifications locally
4. **Error Handling**: Raise descriptive exceptions with context
5. **MCP Compatibility**: Module exposes MCP-compatible tool specifications

## Integration Points

- **logging_monitoring** - All components log via centralized logger
- **model_context_protocol** - MCP tool specifications for FPF operations
- **agents** - FPF provides context building for AI agents
- **cerebrum** - Integration with reasoning engine for pattern analysis

## Signposting

### Document Hierarchy

- **Self**: [AGENTS.md](AGENTS.md)
- **Parent**: [src/codomyrmex/AGENTS.md](../AGENTS.md)
- **Project Root**: [../../../AGENTS.md](../../../AGENTS.md)

### Sibling Modules

| Module | AGENTS.md | Purpose |
| :--- | :--- | :--- |
| cerebrum | [../cerebrum/AGENTS.md](../cerebrum/AGENTS.md) | Reasoning engine |
| agents | [../agents/AGENTS.md](../agents/AGENTS.md) | AI agent integrations |
| spatial | [../spatial/AGENTS.md](../spatial/AGENTS.md) | 3D/4D spatial modeling |
| skills | [../skills/AGENTS.md](../skills/AGENTS.md) | Skills management |
| llm | [../llm/AGENTS.md](../llm/AGENTS.md) | LLM infrastructure |

### Child Directories

| Directory | Purpose |
| :--- | :--- |
| core/ | Parsing, extraction, and data models |
| analysis/ | Indexing and analysis components |
| io/ | Fetching, exporting, and section management |
| visualization/ | Diagram generation and reporting |

### Related Documentation

- [README.md](README.md) - User documentation
- [SPEC.md](SPEC.md) - Functional specification
- [API_SPECIFICATION.md](API_SPECIFICATION.md) - API documentation
- [FPF-Spec.md](FPF-Spec.md) - FPF specification reference
- [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md) - MCP tool specs
