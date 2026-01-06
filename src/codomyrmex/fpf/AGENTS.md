# Codomyrmex Agents — src/codomyrmex/fpf

## Signposting
- **Parent**: [codomyrmex](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Key Artifacts**:
    - [Core Specification](FPF-Spec.md)
    - [API Specification](API_SPECIFICATION.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

This module provides functional capabilities for working with the First Principles Framework (FPF) specification. It can fetch, parse, analyze, and export FPF data for use in prompt/context engineering and other applications.

## Agent Instructions

### When to Use
- **Fetching FPF Specs**: Use `FPFFetcher` to get the latest specification from GitHub
- **Parsing FPF**: Use `FPFParser` to parse markdown into structured data
- **Extracting Patterns**: Use `FPFExtractor` to extract patterns, concepts, and relationships
- **Searching**: Use `FPFIndexer` to search and traverse relationships
- **Exporting**: Use `FPFExporter` to export to JSON or context formats
- **Visualizing**: Use `FPFVisualizer` to generate diagrams and reports
- **Context Building**: Use `ContextBuilder` for prompt engineering

### Capabilities

#### FPFFetcher
- `fetch_latest(repo: str, branch: str) -> str` - Fetch from GitHub
- `check_for_updates(local_path: Path) -> bool` - Check for updates
- `get_version_info(repo: str) -> dict` - Get version information
- `cache_spec(content: str, version: str) -> Path` - Cache specification

#### FPFParser
- `parse_spec(markdown_content: str, source_path: str) -> FPFSpec` - Parse full spec
- `extract_table_of_contents(content: str) -> dict` - Extract TOC
- `extract_patterns(content: str) -> list[Pattern]` - Extract patterns
- `extract_sections(pattern_content: str) -> dict` - Extract sections

#### FPFExtractor
- `extract_patterns(spec: FPFSpec) -> list[Pattern]` - Extract patterns
- `extract_concepts(spec: FPFSpec) -> list[Concept]` - Extract concepts
- `extract_relationships(spec: FPFSpec) -> list[Relationship]` - Extract relationships
- `extract_keywords(spec: FPFSpec) -> dict` - Extract keywords
- `extract_dependencies(spec: FPFSpec) -> dict` - Extract dependencies

#### FPFIndexer
- `build_index(spec: FPFSpec) -> FPFIndex` - Build search index
- `search_patterns(query: str, filters: dict) -> list[Pattern]` - Search patterns
- `get_pattern_by_id(pattern_id: str) -> Pattern` - Get pattern by ID
- `get_related_patterns(pattern_id: str, depth: int) -> list[Pattern]` - Get related patterns

#### FPFExporter
- `export_json(spec: FPFSpec, output_path: Path) -> None` - Export to JSON
- `export_patterns_json(patterns: list[Pattern], output_path: Path) -> None` - Export patterns
- `export_concepts_json(concepts: list[Concept], output_path: Path) -> None` - Export concepts
- `export_for_context(spec: FPFSpec, filters: dict) -> dict` - Export for context

#### FPFVisualizer
- `visualize_pattern_hierarchy(patterns: list[Pattern]) -> str` - Generate hierarchy diagram
- `visualize_dependencies(patterns: list[Pattern]) -> str` - Generate dependency diagram
- `generate_report(spec: FPFSpec, output_path: Path) -> None` - Generate report
- `create_pattern_card(pattern: Pattern) -> str` - Create pattern card

#### ContextBuilder
- `build_context_for_pattern(pattern_id: str, depth: int) -> str` - Build pattern context
- `build_context_for_concept(concept: str) -> str` - Build concept context
- `build_minimal_context(filters: dict) -> str` - Build minimal context
- `build_full_context() -> str` - Build full context

#### TermAnalyzer
- `extract_terms_from_pattern(pattern: Pattern) -> Set[str]` - Extract terms from pattern
- `build_term_cooccurrence_matrix(spec: FPFSpec) -> Dict` - Build co-occurrence matrix
- `get_shared_terms(spec: FPFSpec, min_occurrences: int) -> List[Tuple]` - Get shared terms
- `get_term_frequency(spec: FPFSpec) -> Dict[str, int]` - Get term frequencies
- `get_important_terms(spec: FPFSpec, top_n: int) -> List[Tuple]` - Get important terms
- `analyze_section_terms(spec: FPFSpec, part: str) -> Dict` - Analyze terms by section
- `find_cross_section_terms(spec: FPFSpec, min_sections: int) -> List[Tuple]` - Find cross-section terms

#### GraphGenerator
- `create_pattern_dependency_graph(spec: FPFSpec, layout: str) -> nx.DiGraph` - Create dependency graph
- `create_term_cooccurrence_graph(cooccurrence: Dict, min_weight: int) -> nx.Graph` - Create term graph
- `create_concept_relationship_graph(spec: FPFSpec) -> nx.Graph` - Create concept graph
- `apply_hierarchical_layout(G: nx.DiGraph) -> Dict` - Apply hierarchical layout
- `apply_force_directed_layout(G: nx.Graph, k: float, iterations: int) -> Dict` - Apply force-directed layout
- `apply_circular_layout(G: nx.Graph) -> Dict` - Apply circular layout
- `apply_tree_layout(G: nx.Graph, root: str) -> Dict` - Apply tree layout
- `get_node_colors_by_attribute(G: nx.Graph, attribute: str) -> List[str]` - Get node colors
- `get_node_sizes_by_importance(G: nx.Graph, metric: str) -> List[float]` - Get node sizes

#### FPFVisualizerPNG
- `visualize_shared_terms_network(spec: FPFSpec, output_path: Path, min_weight: int, top_n: int) -> None` - Generate shared terms network PNG
- `visualize_pattern_dependencies(spec: FPFSpec, output_path: Path, layout: str, color_by: str) -> None` - Generate dependency graph PNG
- `visualize_concept_map(spec: FPFSpec, output_path: Path, layout: str) -> None` - Generate concept map PNG
- `visualize_part_hierarchy(spec: FPFSpec, output_path: Path) -> None` - Generate part hierarchy PNG
- `visualize_status_distribution(spec: FPFSpec, output_path: Path, chart_type: str) -> None` - Generate status chart PNG

#### SectionManager
- `extract_part(part_id: str) -> Dict` - Extract part data
- `extract_pattern_group(pattern_ids: List[str], include_dependencies: bool) -> Dict` - Extract pattern group
- `extract_concept_cluster(concept_names: List[str], include_related_patterns: bool) -> Dict` - Extract concept cluster
- `extract_relationship_subset(relationship_types: List[str], include_patterns: bool) -> Dict` - Extract relationship subset
- `list_parts() -> List[str]` - List all parts
- `list_pattern_groups(by_part: bool) -> Dict` - List pattern groups
- `get_section_statistics() -> Dict` - Get section statistics

#### SectionExporter
- `export_part(part_id: str, output_path: Path, include_metadata: bool) -> None` - Export part to JSON
- `export_pattern_group(pattern_ids: List[str], output_path: Path, include_dependencies: bool, include_metadata: bool) -> None` - Export pattern group
- `export_single_pattern(pattern_id: str, output_path: Path, include_related: bool) -> None` - Export single pattern
- `export_concept_cluster(concept_names: List[str], output_path: Path, include_related_patterns: bool, include_metadata: bool) -> None` - Export concept cluster
- `export_all_parts(output_dir: Path, include_metadata: bool) -> List[Path]` - Export all parts

#### SectionImporter
- `import_part(json_path: Path) -> FPFSpec` - Import part from JSON
- `import_pattern_group(json_path: Path) -> FPFSpec` - Import pattern group
- `import_single_pattern(json_path: Path) -> FPFSpec` - Import single pattern
- `merge_specs(*specs: FPFSpec) -> FPFSpec` - Merge multiple specs

#### FPFAnalyzer
- `calculate_pattern_importance() -> Dict[str, float]` - Calculate pattern importance scores
- `calculate_concept_centrality() -> Dict[str, float]` - Calculate concept centrality
- `calculate_relationship_strength() -> Dict[Tuple, float]` - Calculate relationship strength
- `analyze_dependency_depth() -> Dict[str, int]` - Analyze dependency depths
- `get_critical_patterns(top_n: int) -> List[Tuple]` - Get critical patterns
- `get_isolated_patterns() -> List[str]` - Get isolated patterns
- `analyze_part_cohesion() -> Dict[str, float]` - Analyze part cohesion
- `get_analysis_summary() -> Dict` - Get comprehensive analysis summary

#### ReportGenerator
- `generate_html_report(output_path: Path, include_analysis: bool) -> None` - Generate HTML report

#### FPFClient (High-level API)
- `load_from_file(file_path: str) -> FPFSpec` - Load from file
- `fetch_and_load(repo: str, branch: str) -> FPFSpec` - Fetch and load
- `search(query: str, filters: dict) -> list[Pattern]` - Search
- `get_pattern(pattern_id: str) -> Pattern` - Get pattern
- `export_json(output_path: str) -> None` - Export JSON
- `build_context(pattern_id: str, filters: dict) -> str` - Build context

## Active Components

### Core Implementation
- `models.py` - Data models (Pattern, Concept, Relationship, FPFSpec, FPFIndex)
- `parser.py` - Markdown parsing
- `extractor.py` - Pattern/concept extraction
- `indexer.py` - Search and indexing
- `fetcher.py` - GitHub integration
- `exporter.py` - JSON export
- `visualizer.py` - Mermaid visualization generation
- `visualizer_png.py` - PNG visualization generation
- `term_analyzer.py` - Shared terms analysis
- `graph_generator.py` - Graph generation utilities
- `section_manager.py` - Section extraction and management
- `section_exporter.py` - Section-level export
- `section_importer.py` - Section-level import/merge
- `analyzer.py` - Intelligent analysis
- `report_generator.py` - HTML report generation
- `context_builder.py` - Context building
- `__init__.py` - Public API

### Tests
- `tests/test_parser.py` - Parser tests
- `tests/test_extractor.py` - Extractor tests
- `tests/test_indexer.py` - Indexer tests
- `tests/test_fetcher.py` - Fetcher tests


### Additional Files
- `API_SPECIFICATION.md` – Api Specification Md
- `FPF-Spec.md` – Fpf-Spec Md
- `MCP_TOOL_SPECIFICATION.md` – Mcp Tool Specification Md
- `README.md` – Readme Md
- `SPEC.md` – Spec Md
- `__pycache__` –   Pycache  
- `requirements.txt` – Requirements Txt
- `tests` – Tests

## Operating Contracts

### Data Models
- All models use Pydantic for validation
- Pattern IDs follow format: `A.1`, `A.2.1`, `B.3`, etc.
- Status values: Stable, Draft, Stub, New
- Relationships: builds_on, prerequisite_for, coordinates_with, constrains, etc.

### Error Handling
- Network errors in fetcher are raised as `requests.RequestException`
- Missing patterns raise `ValueError`
- Invalid file paths raise `FileNotFoundError`

### Performance
- Indexing is done once per specification load
- Search uses in-memory indexes for fast lookups
- Large specifications (>40K lines) are parsed incrementally

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)

### Module Documentation
- **Module Overview**: [README.md](README.md) - Complete module documentation
- **API Reference**: [API_SPECIFICATION.md](API_SPECIFICATION.md) - Detailed API specification (if applicable)

### Platform Navigation
- **Parent Directory**: [codomyrmex](../README.md) - Package overview
- **Project Root**: [README](../../../README.md) - Main project documentation
- **Source Root**: [src](../../README.md) - Source code documentation