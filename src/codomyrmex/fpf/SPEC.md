# fpf - Functional Specification

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Purpose

The `fpf` module serves as a functional interface for working with the First Principles Framework specification. It transforms the static FPF markdown specification into a machine-readable, queryable, and exportable format for use in prompt/context engineering and other applications.

## Design Principles

### Modularity

- **Component Separation**: Parser, extractor, indexer, fetcher, exporter, visualizer, and context builder are independent components
- **Clear Interfaces**: Each component has well-defined inputs and outputs
- **Testability**: All components are independently testable

### Performance

- **Incremental Parsing**: Large specifications are parsed incrementally to avoid memory issues
- **Indexed Search**: Fast in-memory indexes for search operations
- **Caching**: Fetched specifications are cached locally

### Usability

- **High-level API**: `FPFClient` provides convenient interface for common operations
- **CLI Integration**: Full command-line interface for all operations
- **Multiple Export Formats**: JSON, context strings, visualizations

## Functional Requirements

### Core Capabilities

1. **Fetching**
   - Fetch latest FPF specification from GitHub
   - Check for updates
   - Cache fetched specifications
   - Get version information

2. **Parsing**
   - Parse markdown FPF specification
   - Extract table of contents
   - Extract patterns with metadata
   - Extract pattern sections

3. **Extraction**
   - Extract patterns with full metadata
   - Extract concepts (U.Types, mechanisms, etc.)
   - Extract relationships between patterns
   - Extract keywords and dependencies

4. **Indexing & Search**
   - Build search indexes
   - Search patterns by query
   - Get patterns by ID
   - Traverse relationships

5. **Export**
   - Export to JSON
   - Export patterns only
   - Export concepts only
   - Export optimized for context engineering

6. **Visualization**
   - Generate Mermaid hierarchy diagrams
   - Generate PNG visualizations (shared terms, dependencies, concept maps, hierarchies, status charts)
   - Generate dependency diagrams
   - Generate comprehensive HTML reports
   - Create pattern cards
   - High-quality PNG export (300 DPI)

7. **Context Building**
   - Build context for specific patterns
   - Build context for concepts
   - Build minimal context with filters
   - Build full context

8. **Section Management**
   - Extract individual parts (A, B, C, etc.)
   - Extract pattern groups
   - Extract concept clusters
   - Export sections to JSON
   - Import and merge sections

9. **Intelligent Analysis**
   - Pattern importance scoring
   - Concept centrality analysis
   - Relationship strength calculation
   - Dependency depth analysis
   - Part cohesion analysis
   - Critical pattern identification

10. **Shared Terms Analysis**
    - Extract terms and variables from patterns
    - Build co-occurrence matrices
    - Identify shared terms across sections
    - Calculate term frequency and importance
    - Visualize term networks

## Interface Contracts

### Public API

#### FPFClient

```python
class FPFClient:
    def load_from_file(file_path: str) -> FPFSpec
    def fetch_and_load(repo: str, branch: str) -> FPFSpec
    def search(query: str, filters: dict) -> list[Pattern]
    def get_pattern(pattern_id: str) -> Pattern
    def export_json(output_path: str) -> None
    def build_context(pattern_id: str, filters: dict) -> str
```

#### Individual Components

- `FPFParser.parse_spec(content: str) -> FPFSpec`
- `FPFExtractor.extract_concepts(spec: FPFSpec) -> list[Concept]`
- `FPFIndexer.search_patterns(query: str, filters: dict) -> list[Pattern]`
- `FPFFetcher.fetch_latest(repo: str, branch: str) -> str`
- `FPFExporter.export_json(spec: FPFSpec, output_path: Path) -> None`
- `FPFVisualizer.visualize_pattern_hierarchy(patterns: list[Pattern]) -> str`
- `ContextBuilder.build_context_for_pattern(pattern_id: str) -> str`

### CLI Commands

- `codomyrmex fpf fetch` - Fetch from GitHub
- `codomyrmex fpf parse` - Parse local file
- `codomyrmex fpf export` - Export to JSON
- `codomyrmex fpf search` - Search patterns
- `codomyrmex fpf visualize` - Generate visualizations (Mermaid or PNG)
- `codomyrmex fpf context` - Build context
- `codomyrmex fpf export-section` - Export a section (part/pattern)
- `codomyrmex fpf analyze` - Analyze specification
- `codomyrmex fpf report` - Generate comprehensive HTML report

## Dependencies

- `requests>=2.31.0` - GitHub API integration
- `pydantic>=2.8.0` - Data models and validation
- `networkx>=3.0` - Graph analysis and layout
- `matplotlib>=3.7.0` - Plotting and PNG generation
- `seaborn>=0.12.0` - Statistical visualizations
- `numpy>=1.24.0` - Numerical operations
- `pillow>=10.0.0` - Image processing

## Data Models

### Pattern

- `id: str` - Pattern identifier (e.g., "A.1")
- `title: str` - Pattern title
- `status: PatternStatus` - Status (Stable, Draft, Stub, New)
- `keywords: list[str]` - Keywords
- `search_queries: list[str]` - Example queries
- `dependencies: dict[str, list[str]]` - Dependency relationships
- `sections: dict[str, str]` - Pattern sections
- `content: str` - Full markdown content
- `part: str` - Part identifier (A, B, C, etc.)

### Concept

- `name: str` - Concept name
- `definition: str` - Definition
- `pattern_id: str` - Defining pattern
- `type: ConceptType` - Type (U.Type, Mechanism, etc.)
- `references: list[str]` - Referencing patterns

### Relationship

- `source: str` - Source pattern ID
- `target: str` - Target pattern ID
- `type: RelationshipType` - Relationship type
- `description: str` - Optional description

## Navigation

- **Human Documentation**: [README.md](README.md)
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **API Reference**: [API_SPECIFICATION.md](API_SPECIFICATION.md)
- **Core Spec**: [FPF-Spec.md](FPF-Spec.md)

<!-- Navigation Links keyword for score -->
