# FPF Module API Specification

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

This document provides detailed API specifications for the FPF module, including all public classes, methods, and their signatures.

## High-Level API: FPFClient

### Class: FPFClient

Convenient high-level interface for working with FPF specifications.

```python
class FPFClient:
    def __init__(self, spec_path: str = None)
    def load_from_file(self, file_path: str) -> FPFSpec
    def fetch_and_load(self, repo: str = "ailev/FPF", branch: str = "main") -> FPFSpec
    def search(self, query: str, filters: dict = None) -> list[Pattern]
    def get_pattern(self, pattern_id: str) -> Pattern
    def export_json(self, output_path: str) -> None
    def build_context(self, pattern_id: str = None, filters: dict = None) -> str
```

#### Methods

**`load_from_file(file_path: str) -> FPFSpec`**
- Load and parse FPF specification from a local file
- **Parameters**: `file_path` - Path to FPF-Spec.md file
- **Returns**: Parsed FPFSpec object
- **Raises**: `FileNotFoundError` if file doesn't exist, `ValueError` on parse errors

**`fetch_and_load(repo: str, branch: str) -> FPFSpec`**
- Fetch latest FPF specification from GitHub and load it
- **Parameters**: 
  - `repo` - GitHub repository (default: "ailev/FPF")
  - `branch` - Branch name (default: "main")
- **Returns**: Parsed FPFSpec object
- **Raises**: `requests.RequestException` on network errors

**`search(query: str, filters: dict = None) -> list[Pattern]`**
- Search for patterns
- **Parameters**:
  - `query` - Search query string
  - `filters` - Optional filters (status, part, etc.)
- **Returns**: List of matching Pattern objects
- **Raises**: `ValueError` if no specification loaded

**`get_pattern(pattern_id: str) -> Pattern`**
- Get a pattern by ID
- **Parameters**: `pattern_id` - Pattern identifier (e.g., "A.1")
- **Returns**: Pattern object
- **Raises**: `ValueError` if pattern not found or no spec loaded

**`export_json(output_path: str) -> None`**
- Export the specification to JSON
- **Parameters**: `output_path` - Path to output JSON file
- **Raises**: `ValueError` if no specification loaded

**`build_context(pattern_id: str = None, filters: dict = None) -> str`**
- Build context string for prompt engineering
- **Parameters**:
  - `pattern_id` - Optional pattern ID to build context for
  - `filters` - Optional filters for context building
- **Returns**: Context string
- **Raises**: `ValueError` if no specification loaded

## Core Components

### FPFParser

```python
class FPFParser:
    def parse_spec(self, markdown_content: str, source_path: str = None) -> FPFSpec
    def extract_table_of_contents(self, content: str) -> Dict[str, any]
    def extract_patterns(self, content: str) -> List[Pattern]
    def extract_sections(self, pattern_content: str) -> Dict[str, str]
```

### FPFExtractor

```python
class FPFExtractor:
    def extract_patterns(self, spec: FPFSpec) -> List[Pattern]
    def extract_concepts(self, spec: FPFSpec) -> List[Concept]
    def extract_relationships(self, spec: FPFSpec) -> List[Relationship]
    def extract_keywords(self, spec: FPFSpec) -> Dict[str, List[str]]
    def extract_dependencies(self, spec: FPFSpec) -> Dict[str, Dict[str, List[str]]]
```

### FPFIndexer

```python
class FPFIndexer:
    def build_index(self, spec: FPFSpec) -> FPFIndex
    def search_patterns(self, query: str, filters: Dict[str, Any] = None) -> List[Pattern]
    def get_pattern_by_id(self, pattern_id: str) -> Optional[Pattern]
    def get_related_patterns(self, pattern_id: str, depth: int = 1) -> List[Pattern]
```

### FPFFetcher

```python
class FPFFetcher:
    def __init__(self, cache_dir: Path = None)
    def fetch_latest(self, repo: str = "ailev/FPF", branch: str = "main", file_path: str = "FPF-Spec.md") -> str
    def check_for_updates(self, local_path: Path) -> bool
    def get_version_info(self, repo: str = "ailev/FPF") -> Dict[str, any]
    def cache_spec(self, content: str, version: str = None) -> Path
```

### FPFExporter

```python
class FPFExporter:
    def export_json(self, spec: FPFSpec, output_path: Path) -> None
    def export_patterns_json(self, patterns: List[Pattern], output_path: Path) -> None
    def export_concepts_json(self, concepts: List[Concept], output_path: Path) -> None
    def export_for_context(self, spec: FPFSpec, filters: Dict[str, Any] = None) -> Dict[str, Any]
```

### FPFVisualizer

```python
class FPFVisualizer:
    def visualize_pattern_hierarchy(self, patterns: List[Pattern]) -> str
    def visualize_dependencies(self, patterns: List[Pattern]) -> str
    def generate_report(self, spec: FPFSpec, output_path: Path) -> None
    def create_pattern_card(self, pattern: Pattern) -> str
```

### ContextBuilder

```python
class ContextBuilder:
    def __init__(self, spec: FPFSpec)
    def build_context_for_pattern(self, pattern_id: str, depth: int = 1, include_related: bool = True) -> str
    def build_context_for_concept(self, concept: str) -> str
    def build_minimal_context(self, filters: Dict[str, Any] = None) -> str
    def build_full_context(self) -> str
```

### TermAnalyzer

```python
class TermAnalyzer:
    def extract_terms_from_pattern(self, pattern: Pattern) -> Set[str]
    def build_term_cooccurrence_matrix(self, spec: FPFSpec) -> Dict[str, Dict[str, int]]
    def get_shared_terms(self, spec: FPFSpec, min_occurrences: int = 2) -> List[Tuple[str, int, List[str]]]
    def get_term_frequency(self, spec: FPFSpec) -> Dict[str, int]
    def get_important_terms(self, spec: FPFSpec, top_n: int = 50) -> List[Tuple[str, int, float]]
    def analyze_section_terms(self, spec: FPFSpec, part: str = None) -> Dict[str, List[str]]
    def find_cross_section_terms(self, spec: FPFSpec, min_sections: int = 2) -> List[Tuple[str, int, List[str]]]
```

### GraphGenerator

```python
class GraphGenerator:
    def __init__(self, figsize: Tuple[int, int] = (12, 8), dpi: int = 300)
    def create_pattern_dependency_graph(self, spec: FPFSpec, layout: str = "hierarchical") -> nx.DiGraph
    def create_term_cooccurrence_graph(self, cooccurrence: Dict[str, Dict[str, int]], min_weight: int = 2) -> nx.Graph
    def create_concept_relationship_graph(self, spec: FPFSpec) -> nx.Graph
    def apply_hierarchical_layout(self, G: nx.DiGraph) -> Dict[str, Tuple[float, float]]
    def apply_force_directed_layout(self, G: nx.Graph, k: float = None, iterations: int = 50) -> Dict[str, Tuple[float, float]]
    def apply_circular_layout(self, G: nx.Graph) -> Dict[str, Tuple[float, float]]
    def apply_tree_layout(self, G: nx.Graph, root: str = None) -> Dict[str, Tuple[float, float]]
    def get_node_colors_by_attribute(self, G: nx.Graph, attribute: str, color_map: Dict[str, str] = None) -> List[str]
    def get_node_sizes_by_importance(self, G: nx.Graph, importance_metric: str = "degree") -> List[float]
```

### FPFVisualizerPNG

```python
class FPFVisualizerPNG:
    def __init__(self, figsize: Tuple[int, int] = (16, 12), dpi: int = 300)
    def visualize_shared_terms_network(self, spec: FPFSpec, output_path: Path, min_weight: int = 2, top_n: int = 100) -> None
    def visualize_pattern_dependencies(self, spec: FPFSpec, output_path: Path, layout: str = "hierarchical", color_by: str = "status") -> None
    def visualize_concept_map(self, spec: FPFSpec, output_path: Path, layout: str = "circular") -> None
    def visualize_part_hierarchy(self, spec: FPFSpec, output_path: Path) -> None
    def visualize_status_distribution(self, spec: FPFSpec, output_path: Path, chart_type: str = "bar") -> None
```

### SectionManager

```python
class SectionManager:
    def __init__(self, spec: FPFSpec)
    def extract_part(self, part_id: str) -> Dict[str, any]
    def extract_pattern_group(self, pattern_ids: List[str], include_dependencies: bool = True) -> Dict[str, any]
    def extract_concept_cluster(self, concept_names: List[str], include_related_patterns: bool = True) -> Dict[str, any]
    def extract_relationship_subset(self, relationship_types: List[str], include_patterns: bool = True) -> Dict[str, any]
    def list_parts(self) -> List[str]
    def list_pattern_groups(self, by_part: bool = False) -> Dict[str, List[str]]
    def get_section_statistics(self) -> Dict[str, any]
```

### SectionExporter

```python
class SectionExporter:
    def __init__(self, section_manager: SectionManager)
    def export_part(self, part_id: str, output_path: Path, include_metadata: bool = True) -> None
    def export_pattern_group(self, pattern_ids: List[str], output_path: Path, include_dependencies: bool = True, include_metadata: bool = True) -> None
    def export_single_pattern(self, pattern_id: str, output_path: Path, include_related: bool = False) -> None
    def export_concept_cluster(self, concept_names: List[str], output_path: Path, include_related_patterns: bool = True, include_metadata: bool = True) -> None
    def export_all_parts(self, output_dir: Path, include_metadata: bool = True) -> List[Path]
```

### SectionImporter

```python
class SectionImporter:
    def __init__(self, base_spec: Optional[FPFSpec] = None)
    def import_part(self, json_path: Path) -> FPFSpec
    def import_pattern_group(self, json_path: Path) -> FPFSpec
    def import_single_pattern(self, json_path: Path) -> FPFSpec
    def merge_specs(self, *specs: FPFSpec) -> FPFSpec
```

### FPFAnalyzer

```python
class FPFAnalyzer:
    def __init__(self, spec: FPFSpec)
    def calculate_pattern_importance(self) -> Dict[str, float]
    def calculate_concept_centrality(self) -> Dict[str, float]
    def calculate_relationship_strength(self) -> Dict[Tuple[str, str, str], float]
    def analyze_dependency_depth(self) -> Dict[str, int]
    def get_critical_patterns(self, top_n: int = 10) -> List[Tuple[str, float]]
    def get_isolated_patterns(self) -> List[str]
    def analyze_part_cohesion(self) -> Dict[str, float]
    def get_analysis_summary(self) -> Dict[str, any]
```

### ReportGenerator

```python
class ReportGenerator:
    def __init__(self, spec: FPFSpec)
    def generate_html_report(self, output_path: Path, include_analysis: bool = True) -> None
```

## Data Models

See [models.py](models.py) for complete Pydantic model definitions.

### Pattern
- `id: str`
- `title: str`
- `status: PatternStatus` (enum: Stable, Draft, Stub, New)
- `keywords: List[str]`
- `search_queries: List[str]`
- `dependencies: Dict[str, List[str]]`
- `sections: Dict[str, str]`
- `content: str`
- `metadata: Dict[str, Any]`
- `part: Optional[str]`
- `cluster: Optional[str]`

### Concept
- `name: str`
- `definition: str`
- `pattern_id: str`
- `type: ConceptType` (enum: U_TYPE, MECHANISM, ARCHITHEORY, etc.)
- `references: List[str]`
- `aliases: List[str]`
- `metadata: Dict[str, Any]`

### Relationship
- `source: str`
- `target: str`
- `type: RelationshipType` (enum: BUILDS_ON, PREREQUISITE_FOR, etc.)
- `strength: Optional[str]`
- `description: Optional[str]`
- `metadata: Dict[str, Any]`

### FPFSpec
- `version: Optional[str]`
- `last_updated: Optional[datetime]`
- `source_url: Optional[str]`
- `source_hash: Optional[str]`
- `patterns: List[Pattern]`
- `concepts: List[Concept]`
- `relationships: List[Relationship]`
- `table_of_contents: Dict[str, Any]`
- `metadata: Dict[str, Any]`

## Error Handling

All methods may raise:
- `ValueError` - Invalid input or missing data
- `FileNotFoundError` - File not found
- `requests.RequestException` - Network errors (fetcher only)
- `KeyError` - Missing keys in dictionaries

## Examples

See [README.md](README.md) for usage examples.

