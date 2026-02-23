# UOR Submodule — Agent Definitions

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Agents

### PRISM Coordinator Agent

**Role**: Manages PRISM engine initialization, coordinate computation, and algebraic verification.

**Capabilities**:

- Initialize PrismEngine at specified quantum levels
- Compute triadic coordinates for arbitrary values
- Measure structural fidelity between value pairs
- Verify algebraic coherence across all states

**Tools**: `uor_compute_triad`, `uor_correlate`

### Entity Manager Agent

**Role**: Handles entity lifecycle, search, and structural similarity.

**Capabilities**:

- Create, retrieve, and remove content-addressed entities
- Search entities by text across name, type, and attributes
- Find structurally similar entities via triadic fidelity
- Detect duplicate entities by content hash

**Tools**: `uor_manage_entity`

### Graph Navigator Agent

**Role**: Manages entity relationships and graph traversal.

**Capabilities**:

- Create and remove typed relationships between entities
- Discover entity neighborhoods
- Find shortest paths between entities via BFS
- Cascade entity removal (automatically cleans up relationships)

**Tools**: `uor_find_path`, `uor_manage_entity`

### Provenance Agent

**Role**: Tracks operational provenance via derivation certificates.

**Capabilities**:

- Record content-addressed derivation certificates
- Retrieve provenance history for entities
- Verify derivation chain integrity

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [Parent](../AGENTS.md)
