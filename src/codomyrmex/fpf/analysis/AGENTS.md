# FPF Analysis -- Agent Coordination

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Analysis toolkit for First Principles Framework specifications. Provides graph-based pattern importance scoring, concept centrality analysis, term extraction, pattern search indexing, and HTML report generation.

## Key Components

| File | Class | Role |
|------|-------|------|
| `analyzer.py` | `FPFAnalyzer` | Graph-based analysis -- `calculate_pattern_importance()`, `calculate_concept_centrality()`, `calculate_relationship_strength()`, `analyze_dependency_depth()`, `get_critical_patterns()`, `get_isolated_patterns()`, `analyze_part_cohesion()`, `get_analysis_summary()` |
| `indexer.py` | `FPFIndexer` | Search index -- `build_index()`, `search_patterns()`, `get_pattern_by_id()`, `get_related_patterns()` |
| `report_generator.py` | `ReportGenerator` | HTML report -- `generate_report()` with overview, statistics, patterns, concepts, analysis, and terms sections |
| `term_analyzer.py` | `TermAnalyzer` | Term extraction via regex -- `extract_terms_from_pattern()`, `build_term_cooccurrence_matrix()`, `get_shared_terms()`, `get_term_frequency()`, `get_important_terms()`, `analyze_section_terms()`, `find_cross_section_terms()` |

## Agent Operating Contract

1. **Pattern importance** -- Instantiate `FPFAnalyzer(spec)` with an `FPFSpec`. Call `calculate_pattern_importance()` to get degree + betweenness centrality scores (weighted 60/40). Call `get_critical_patterns(top_n)` for ranked results.
2. **Dependency analysis** -- `analyze_dependency_depth()` returns max predecessor depth per pattern. `get_isolated_patterns()` returns patterns with zero in-degree and out-degree.
3. **Cohesion** -- `analyze_part_cohesion()` measures ratio of internal relationships to total possible per part/section.
4. **Search** -- Build an `FPFIndexer`, call `build_index(spec)` to create keyword, title, and relationship indexes. Then use `search_patterns(query, filters)` and `get_related_patterns(pattern_id, depth)`.
5. **Term analysis** -- `TermAnalyzer` extracts terms using four regex patterns: `U.Type`, backtick-enclosed variables, CamelCase identifiers, and bold markdown terms. Use `get_shared_terms(spec, min_occurrences)` to find cross-pattern terms and `find_cross_section_terms()` for cross-section analysis.
6. **Reporting** -- `ReportGenerator(spec).generate_report(output_path)` produces a self-contained HTML file with CSS styling, pattern tables, concept tables, importance rankings, cohesion scores, and shared term listings.

## Data Flow

```
FPFSpec --> FPFAnalyzer (networkx graphs) --> importance, centrality, depth, cohesion
FPFSpec --> FPFIndexer (keyword/title/relationship indexes) --> search results
FPFSpec --> TermAnalyzer (regex extraction) --> term frequency, co-occurrence, cross-section terms
FPFSpec --> ReportGenerator (uses FPFAnalyzer + TermAnalyzer) --> HTML report
```

## Dependencies

- **Internal**: `fpf.core.models` (`FPFSpec`, `FPFIndex`, `Pattern`)
- **External**: `networkx` (for `FPFAnalyzer` graph operations), `re` (for `TermAnalyzer`), `datetime`/`pathlib` (for `ReportGenerator`)

## Testing Guidance

- Build an `FPFSpec` with known patterns and relationships. Verify `calculate_pattern_importance()` returns scores in [0, 1].
- Test `FPFIndexer.search_patterns()` with keywords that match known pattern titles.
- Verify `TermAnalyzer.extract_terms_from_pattern()` finds CamelCase, U.Type, and backtick-enclosed terms.
- Confirm `ReportGenerator.generate_report()` writes valid HTML to the output path.
- No mocks -- use real `FPFSpec` objects with minimal pattern sets.

## Navigation

- **Parent**: [fpf/](../README.md)
- **Sibling**: [reasoning/](../reasoning/AGENTS.md)
- **Project root**: [../../../../README.md](../../../../README.md)
