# Agent Instructions for `codomyrmex.relations`

**Version**: v1.0.2 | **Status**: Active | **Last Updated**: February 2026

## Purpose

The Relations module provides three complementary subsystems for tracking entities and their connections: a CRM (Contact Relationship Management) engine for contact storage, tagging, and interaction logging; a social-network analysis toolkit with community detection, centrality metrics, and shortest-path search; and a UOR (Universal Object Reference) layer that gives every entity a content-addressed identity with PRISM triadic coordinates. Agents use this module to build, query, and score relationship graphs across the codomyrmex ecosystem.

## Active Components

| Component | Type | File | Status |
|-----------|------|------|--------|
| `Contact` | Dataclass | `crm/crm.py` | Active |
| `ContactManager` | Class | `crm/crm.py` | Active |
| `Interaction` | Dataclass | `crm/crm.py` | Active |
| `SocialGraph` | Class | `network_analysis/graph.py` | Active |
| `GraphMetrics` | Static utility | `network_analysis/graph.py` | Active |
| `PrismEngine` | Class | `uor/engine.py` | Active |
| `TriadicCoordinate` | Frozen dataclass | `uor/engine.py` | Active |
| `UOREntity` | Dataclass | `uor/entities.py` | Active |
| `UORRelationship` | Dataclass | `uor/entities.py` | Active |
| `EntityManager` | Class | `uor/` | Active |
| `DerivationRecord` | Dataclass | `uor/` | Active |
| `DerivationTracker` | Class | `uor/` | Active |
| `UORGraph` | Class | `uor/` | Active |
| `render_social_graph()` | Function | `visualization.py` | Active |
| `render_interaction_timeline()` | Function | `visualization.py` | Active |
| `contact_heatmap_data()` | Function | `visualization.py` | Active |
| `tag_co_occurrence()` | Function | `visualization.py` | Active |
| `network_summary_text()` | Function | `visualization.py` | Active |
| `export_contacts_csv()` | Function | `visualization.py` | Active |

## MCP Tools Available

| Tool | Description | Trust Level |
|------|-------------|-------------|
| `relations_score_strength` | Score pairwise relationship strength from interaction history with configurable decay (exponential, linear, step, none) | Safe (read-only) |

This is the only MCP tool exposed in `mcp_tools.py`. It accepts a source entity, target entity, interaction list, and decay parameters, returning a raw score and interaction count.

## Usage Guidelines

1. **Importing**: Import from the module root for all public types.

   ```python
   from codomyrmex.relations import (
       Contact, ContactManager, Interaction,
       SocialGraph, GraphMetrics,
       UOREntity, UORRelationship, PrismEngine, TriadicCoordinate,
   )
   ```

2. **Contact Management**: Use `ContactManager` for all CRUD operations. Always record `Interaction` events when engaging with contacts. Contacts support tagging via `contact.tags`.

3. **Social Graph**: Use `SocialGraph` for modeling entity relationships as an undirected weighted graph. Key methods:
   - `add_node()` / `add_edge()` -- build the graph
   - `find_communities()` -- label-propagation community detection
   - `calculate_centrality()` -- degree centrality scores
   - `shortest_path()` -- BFS shortest path between nodes
   - `get_influence_score()` -- weighted influence metric

4. **Graph Metrics**: `GraphMetrics` provides static methods: `density()`, `clustering_coefficient()`, and `degree_distribution()`.

5. **UOR Entities**: Use `UOREntity` for content-addressed entities with SHA256 hashing. Attribute mutations auto-recompute the content hash. `UORRelationship` links entities with typed, weighted, optionally bidirectional edges.

6. **PRISM Engine**: `PrismEngine` operates over the modular ring Z/(2^(8*(quantum+1)))Z with triadic coordinates (datum, stratum, spectrum). Use `verify()` to confirm algebraic coherence.

## Quick Verification

```bash
uv run python -c "from codomyrmex.relations import Contact, ContactManager, SocialGraph, GraphMetrics, UOREntity, PrismEngine; print('OK')"
uv run pytest src/codomyrmex/tests/unit/relations/ -v
```

## Operating Contracts

- Every `SocialGraph` edge is undirected: `add_edge(a, b)` creates both `a->b` and `b->a`.
- `UOREntity.content_hash` is recomputed automatically on `set_attribute()`, `remove_attribute()`, and `merge_attributes()`. Do not set `content_hash` manually.
- `PrismEngine.verify()` must be called before trusting algebraic operations at quantum levels above 0.
- The `relations_score_strength` MCP tool catches all exceptions internally and returns `{"status": "error"}` rather than raising.
- **Zero-Mock Policy**: Tests must use real `ContactManager`, `SocialGraph`, and `PrismEngine` instances. No mocking of storage, graph operations, or hash computation.

## Integration Points

- **visualization module**: `render_social_graph()` and related functions consume `ContactManager` to produce graph definitions, timelines, heatmaps, and CSV exports.
- **data_visualization module**: Not directly imported (circular-import avoidance), but graph data can be passed to the `data_visualization` charting pipeline.
- **cerebrum module**: Case-based reasoning can use `SocialGraph` centrality and community data as features.
- **networks module**: The general `networks` module provides lower-level graph primitives; `relations` builds domain-specific CRM and UOR semantics on top.

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | Primary Capabilities | Trust Level |
|-----------|-------------|---------------------|-------------|
| **Engineer** | Full | `relations_score_strength`; relationship scoring, entity link management | TRUSTED |
| **Architect** | Read + Design | `relations_score_strength`; relationship design, entity graph architecture | OBSERVED |
| **QATester** | Validation | `relations_score_strength`; relationship strength verification | OBSERVED |

### Engineer Agent
**Use Cases**: Scoring entity relationships during OBSERVE/THINK, building relationship graphs, computing link strength metrics.

### Architect Agent
**Use Cases**: Designing entity relationship models, reviewing relationship schema, graph architecture analysis.

### QATester Agent
**Use Cases**: Validating relationship scores during VERIFY, confirming entity linkage correctness.

## Navigation

- Module: `src/codomyrmex/relations/`
- PAI integration: [PAI.md](PAI.md)
- Specification: [SPEC.md](SPEC.md)
- Root bridge: [/PAI.md](../../../PAI.md)
- Parent: [../AGENTS.md](../AGENTS.md)
