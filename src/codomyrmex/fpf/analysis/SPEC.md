# FPF Analysis -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## 1. Overview

Analysis toolkit for FPF (First Principles Framework) specifications. Four classes provide graph-based pattern analysis, search indexing, term extraction, and HTML report generation over `FPFSpec` objects.

## 2. FPFAnalyzer

Constructor: `FPFAnalyzer(spec: FPFSpec)`

Internally builds two lazy networkx graphs: `_dependency_graph` (DiGraph from `builds_on`/`prerequisite_for` relationships) and `_concept_graph` (Graph from shared pattern references).

| Method | Signature | Returns |
|--------|-----------|---------|
| `calculate_pattern_importance` | `() -> dict[str, float]` | Weighted combination: 0.6 * normalized degree centrality + 0.4 * normalized betweenness centrality |
| `calculate_concept_centrality` | `() -> dict[str, float]` | Degree centrality on concept co-occurrence graph |
| `calculate_relationship_strength` | `() -> dict[tuple[str, str, str], float]` | Base weight by relationship type * average source/target importance |
| `analyze_dependency_depth` | `() -> dict[str, int]` | Max predecessor chain length per node (cycle-safe via visited set) |
| `get_critical_patterns` | `(top_n: int = 10) -> list[tuple[str, float]]` | Top patterns sorted by importance descending |
| `get_isolated_patterns` | `() -> list[str]` | Nodes with in-degree 0 and out-degree 0 |
| `analyze_part_cohesion` | `() -> dict[str, float]` | Internal relationship count / n*(n-1) per part |
| `get_analysis_summary` | `() -> dict` | Aggregate of all metrics plus statistics (totals, averages) |

**Relationship type weights** for `calculate_relationship_strength()`:

| Type | Weight |
|------|--------|
| `builds_on` | 1.0 |
| `prerequisite_for` | 0.9 |
| `constrains` | 0.8 |
| `coordinates_with` | 0.7 |
| `refines` | 0.6 |
| `informs` | 0.5 |

## 3. FPFIndexer

Constructor: `FPFIndexer()`

| Method | Signature | Behavior |
|--------|-----------|----------|
| `build_index` | `(spec: FPFSpec) -> FPFIndex` | Builds 5 indexes: pattern_index, concept_index, keyword_index, title_index, relationship_graph (bidirectional) |
| `search_patterns` | `(query: str, filters: dict | None) -> list[Pattern]` | Delegates to `FPFIndex.search_patterns()` |
| `get_pattern_by_id` | `(pattern_id: str) -> Pattern | None` | Direct ID lookup |
| `get_related_patterns` | `(pattern_id: str, depth: int = 1) -> list[Pattern]` | Traverses relationship graph to specified depth |

**Indexing details**:
- Keywords: lowercased, mapped to pattern IDs.
- Title words: split on whitespace, common stop words excluded (`the`, `a`, `an`, `and`, `or`, `of`, `in`, `on`, `for`).
- Relationship graph: bidirectional -- if A depends on B, both A->B and B->A are indexed.

## 4. TermAnalyzer

Constructor: `TermAnalyzer()`

Four compiled regex patterns:
- `u_type_pattern`: `` `?U\.([A-Z][a-zA-Z0-9]*)`? `` -- extracts `U.Type` references
- `variable_pattern`: `` `([A-Z][a-zA-Z0-9]*(?:\.[A-Z][a-zA-Z0-9]*)*)` `` -- backtick-enclosed identifiers
- `term_pattern`: `\b([A-Z][a-z]+(?:[A-Z][a-z]+)*)\b` -- CamelCase terms (>3 chars)
- `keyword_pattern`: `\*\*?([A-Z][a-zA-Z\s-]+?)\*\*?` -- bold markdown terms (>2 chars)

| Method | Signature | Returns |
|--------|-----------|---------|
| `extract_terms_from_pattern` | `(pattern: Pattern) -> set[str]` | Union of all regex matches plus pattern keywords |
| `build_term_cooccurrence_matrix` | `(spec: FPFSpec) -> dict[str, dict[str, int]]` | Symmetric co-occurrence counts (shared pattern membership) |
| `get_shared_terms` | `(spec, min_occurrences) -> list[tuple[str, int, list[str]]]` | Terms appearing in >= min_occurrences patterns, sorted by count |
| `get_term_frequency` | `(spec) -> dict[str, int]` | Global term counts via `Counter` |
| `get_important_terms` | `(spec, top_n) -> list[tuple[str, int, float]]` | Importance = frequency * (pattern_coverage / total_patterns) |
| `analyze_section_terms` | `(spec, part) -> dict[str, list[str]]` | Terms grouped by part/section |
| `find_cross_section_terms` | `(spec, min_sections) -> list[tuple[str, int, list[str]]]` | Terms spanning >= min_sections parts |

## 5. ReportGenerator

Constructor: `ReportGenerator(spec: FPFSpec)` -- internally creates `FPFAnalyzer` and `TermAnalyzer`.

| Method | Signature | Behavior |
|--------|-----------|----------|
| `generate_report` | `(output_path: Path, include_analysis: bool = True)` | Writes self-contained HTML with embedded CSS |

**Report sections**: Overview, Statistics (status counts, avg importance), Patterns (sortable table), Top Concepts (first 50), Analysis (critical patterns, part cohesion), Shared Terms (top 20 cross-pattern terms).

## 6. Dependencies

- **Internal**: `fpf.core.models` (FPFSpec, FPFIndex, Pattern)
- **External**: `networkx`, `re`, `collections`, `datetime`, `pathlib`

## 7. Constraints

- `FPFAnalyzer` graph operations return empty dicts for specs with zero patterns.
- `calculate_relationship_strength()` recomputes `calculate_pattern_importance()` per call -- performance concern for large specs with many relationships.
- `FPFIndexer` requires `build_index()` before any search method; methods return empty results if index is not built.
- `ReportGenerator` creates parent directories via `mkdir(parents=True)`.

## Navigation

- **Parent**: [fpf/](../README.md)
- **Project root**: [../../../../README.md](../../../../README.md)
