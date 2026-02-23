# UOR Submodule — Functional Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Purpose

Provide content-addressed entity identity and structural similarity measurement by integrating the UOR Foundation's PRISM universal coordinate system into the Codomyrmex relations module.

## Functional Requirements

### FR-1: PRISM Engine

- **FR-1.1**: Operate over the modular ring Z/(2^(8*(quantum+1)))Z for arbitrary quantum levels
- **FR-1.2**: Provide primitive operations: neg (additive inverse), bnot (bitwise complement), xor, band, bor
- **FR-1.3**: Derive succ = neg ∘ bnot and pred = bnot ∘ neg from primitives
- **FR-1.4**: Compute triadic coordinates (datum, stratum, spectrum) for any value
- **FR-1.5**: Measure structural similarity via Hamming-distance fidelity ∈ [0.0, 1.0]
- **FR-1.6**: Verify algebraic coherence exhaustively at Q0, by sampling at higher quantum levels
- **FR-1.7**: Enforce the critical identity: neg(bnot(x)) = x + 1 mod 2^n

### FR-2: Entity Layer

- **FR-2.1**: Content-address entities via SHA256(name, type, attributes)
- **FR-2.2**: Attach optional triadic coordinates to entities
- **FR-2.3**: Content-address relationships via SHA256(source, target, type, attributes)
- **FR-2.4**: Provide serialization via `to_dict()`

### FR-3: Entity Manager

- **FR-3.1**: CRUD operations for entities (add, get, remove)
- **FR-3.2**: Case-insensitive text search on name, type, attributes
- **FR-3.3**: PRISM-based similarity search using triadic fidelity
- **FR-3.4**: Duplicate detection via identical content hashes

### FR-4: Graph

- **FR-4.1**: Relationship CRUD with entity existence validation
- **FR-4.2**: Cascading entity removal (clean up associated relationships)
- **FR-4.3**: BFS shortest path between entities
- **FR-4.4**: Neighbor discovery (entities connected by relationships)

### FR-5: Derivation Tracking

- **FR-5.1**: Append-only provenance log
- **FR-5.2**: Content-addressed derivation IDs (SHA256)
- **FR-5.3**: Per-entity history retrieval
- **FR-5.4**: Chain integrity verification

## Non-Functional Requirements

- **NFR-1**: Zero external dependencies (stdlib only)
- **NFR-2**: Follow ContactManager/SocialGraph patterns from existing submodules
- **NFR-3**: Deterministic content hashing (sorted keys, UTF-8 encoding)
- **NFR-4**: Immutable triadic coordinates (frozen dataclass)

## Navigation

- [README](README.md) | [API](API_SPECIFICATION.md) | [AGENTS](AGENTS.md) | [Parent](../SPEC.md)
