# Codomyrmex Agents - src/codomyrmex/fpf/analysis

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

Analysis module for FPF (First Principles Framework) specifications. Provides intelligent analysis capabilities including pattern importance scoring, centrality analysis, relationship strength calculation, search indexing, and term/concept analysis across patterns. This module enables deep understanding of FPF structure and content.

## Active Components

- `analyzer.py` - Pattern and relationship analyzer (FPFAnalyzer)
- `indexer.py` - Search index builder (FPFIndexer)
- `term_analyzer.py` - Term and concept analysis across patterns (TermAnalyzer)
- `report_generator.py` - Report generation utilities

## Key Classes

### FPFAnalyzer (analyzer.py)
Analyzer for FPF specifications using graph-based metrics:
- `calculate_pattern_importance()`: Compute importance scores
  - Combines degree centrality (60%) and betweenness centrality (40%)
  - Uses dependency graph built from relationships
- `calculate_concept_centrality()`: Compute concept centrality scores
  - Based on shared pattern references between concepts
- `calculate_relationship_strength()`: Score relationship importance
  - Base weights by type (builds_on: 1.0, prerequisite_for: 0.9, etc.)
  - Adjusted by source/target pattern importance
- `analyze_dependency_depth()`: Calculate max dependency depth per pattern
  - Recursive traversal of predecessor relationships
- `get_critical_patterns()`: Return top-N patterns by importance
- `get_isolated_patterns()`: Find patterns with no dependencies
- `analyze_part_cohesion()`: Measure internal relationship density per part
  - Ratio of internal relationships to total possible
- `get_analysis_summary()`: Comprehensive summary with all metrics

Internal methods:
- `_build_dependency_graph()`: Create NetworkX DiGraph from relationships
- `_build_concept_graph()`: Create NetworkX Graph of concept connections

### FPFIndexer (indexer.py)
Indexer for FPF patterns and concepts:
- `build_index()`: Create comprehensive search index
  - Pattern index: pattern_id -> Pattern
  - Concept index: concept_name -> List[Concept]
  - Keyword index: keyword -> List[pattern_id]
  - Title index: word -> List[pattern_id]
  - Relationship graph: pattern_id -> List[related_id]
- `search_patterns()`: Search using query and optional filters
  - Filters: status, part, pattern_ids
- `get_pattern_by_id()`: Direct pattern lookup
- `get_related_patterns()`: Traverse relationship graph to depth

### TermAnalyzer (term_analyzer.py)
Analyzer for shared terms and variables across FPF sections:
- `extract_terms_from_pattern()`: Extract all terms from pattern
  - U.Types: `U\.([A-Z][a-zA-Z0-9]*)`
  - Variables: backtick-enclosed identifiers
  - CamelCase terms: multi-word capitalized names
  - Bold terms: `**Term**` or `*Term*`
  - Pattern keywords
- `build_term_cooccurrence_matrix()`: Build co-occurrence counts
  - Maps term pairs to number of shared patterns
- `get_shared_terms()`: Find terms appearing in multiple patterns
  - Returns (term, count, pattern_ids) sorted by frequency
- `get_term_frequency()`: Count term occurrences across all patterns
- `get_important_terms()`: Rank by frequency * distribution
  - Importance = frequency * (pattern_count / total_patterns)
- `analyze_section_terms()`: Group unique terms by part/section
- `find_cross_section_terms()`: Find terms spanning multiple parts
  - Returns (term, section_count, section_names)

Regular expression patterns:
- U.Type: `U\.([A-Z][a-zA-Z0-9]*)`
- Variable: `([A-Z][a-zA-Z0-9]*(?:\.[A-Z][a-zA-Z0-9]*)*)`
- CamelCase: `([A-Z][a-z]+(?:[A-Z][a-z]+)*)`
- Bold: `\*\*?([A-Z][a-zA-Z\s-]+?)\*\*?`

## Operating Contracts

- Maintain alignment between code, documentation, and configured workflows
- FPFAnalyzer requires FPFSpec with patterns and relationships populated
- Dependency graph uses only builds_on and prerequisite_for relationships
- Centrality calculations use NetworkX algorithms
- FPFIndexer builds indexes lazily on first build_index() call
- TermAnalyzer filters short terms (length <= 3) from CamelCase matches
- Ensure Model Context Protocol interfaces remain available for sibling agents
- Record outcomes in shared telemetry and update TODO queues when necessary

## Signposting

- **Core Module**: `../core/` - FPFParser, FPFExtractor, models providing input data
- **IO Module**: `../io/` - FPFFetcher, FPFExporter for data I/O
- **Visualization Module**: `../visualization/` - FPFVisualizer, GraphGenerator for rendering analysis
- **CEREBRUM Integration**: `../../cerebrum/fpf/` - Uses FPFAnalyzer and TermAnalyzer
- **Parent Directory**: [fpf](../README.md) - FPF package documentation
- **Project Root**: ../../../../README.md - Main project documentation
