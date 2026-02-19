# UOR Submodule — API Specification

**Version**: v0.1.7 | **Last Updated**: February 2026

## Module: `codomyrmex.relations.uor`

---

## `engine.TriadicCoordinate`

Frozen dataclass representing the three PRISM coordinates.

| Field | Type | Description |
|---|---|---|
| `datum` | `tuple[int, ...]` | Identity — value as big-endian bytes |
| `stratum` | `tuple[int, ...]` | Magnitude — Hamming weight per byte |
| `spectrum` | `tuple[tuple[int, ...], ...]` | Structure — active bit positions per byte |

**Properties**: `total_stratum: int`, `width: int`

---

## `engine.PrismEngine`

```python
PrismEngine(quantum: int = 0)
```

Computation engine over Z/(2^(8*(quantum+1)))Z.

### Primitive Operations

| Method | Signature | Description |
|---|---|---|
| `neg` | `(n: int \| tuple) → tuple[int, ...]` | Additive inverse (two's complement) |
| `bnot` | `(n: int \| tuple) → tuple[int, ...]` | Bitwise complement |
| `xor` | `(a, b) → tuple[int, ...]` | Bitwise XOR |
| `band` | `(a, b) → tuple[int, ...]` | Bitwise AND |
| `bor` | `(a, b) → tuple[int, ...]` | Bitwise OR |

### Derived Operations

| Method | Signature | Description |
|---|---|---|
| `succ` | `(n) → tuple[int, ...]` | Increment = neg(bnot(x)) |
| `pred` | `(n) → tuple[int, ...]` | Decrement = bnot(neg(x)) |

### Coordinates

| Method | Signature | Description |
|---|---|---|
| `stratum` | `(n) → tuple[int, ...]` | Popcount per byte |
| `spectrum` | `(n) → tuple[tuple[int, ...], ...]` | Active bits per byte |
| `triad` | `(n) → TriadicCoordinate` | Complete triadic coordinates |

### Correlation

| Method | Signature | Description |
|---|---|---|
| `correlate` | `(a, b) → dict` | Full Hamming-distance correlation |
| `fidelity` | `(a, b) → float` | Fidelity score only ∈ [0.0, 1.0] |

### Verification

| Method | Signature | Description |
|---|---|---|
| `verify` | `() → bool` | Verify algebraic coherence |

**Properties**: `is_coherent: bool`, `quantum: int`, `width: int`, `bits: int`

**Dunder**: `__eq__`, `__hash__` (equality by quantum level), `__repr__`

---

## `entities.UOREntity`

| Field | Type | Default |
|---|---|---|
| `id` | `str` | UUID4 |
| `name` | `str` | `""` |
| `entity_type` | `str` | `"generic"` |
| `attributes` | `dict[str, Any]` | `{}` |
| `content_hash` | `str` | SHA256 auto-computed |
| `triadic_coordinates` | `TriadicCoordinate \| None` | `None` |
| `created_at` | `str` | ISO timestamp |

**Methods**: `to_dict()`, `recompute_hash()`

---

## `entities.UORRelationship`

| Field | Type | Default |
|---|---|---|
| `id` | `str` | UUID4 |
| `source_id` | `str` | `""` |
| `target_id` | `str` | `""` |
| `relationship_type` | `str` | `"related"` |
| `attributes` | `dict[str, Any]` | `{}` |
| `relationship_hash` | `str` | SHA256 auto-computed |
| `created_at` | `str` | ISO timestamp |

**Methods**: `to_dict()`

---

## `manager.EntityManager`

```python
EntityManager(quantum: int = 0)
```

| Method | Signature | Returns |
|---|---|---|
| `add_entity` | `(name, entity_type, attributes, compute_coordinates)` | `UOREntity` |
| `get_entity` | `(entity_id: str)` | `UOREntity \| None` |
| `remove_entity` | `(entity_id: str)` | `bool` |
| `search_entities` | `(query: str, entity_type: str \| None)` | `list[UOREntity]` |
| `find_similar` | `(entity_id: str, threshold: float)` | `list[tuple[UOREntity, float]]` |
| `find_duplicates` | `()` | `list[list[UOREntity]]` |

**Properties**: `all_entities`, `engine`

---

## `graph.UORGraph`

```python
UORGraph(quantum: int = 0)
```

| Method | Signature | Returns |
|---|---|---|
| `add_entity` | `(name, entity_type, attributes, compute_coordinates)` | `UOREntity` |
| `get_entity` | `(entity_id: str)` | `UOREntity \| None` |
| `remove_entity` | `(entity_id: str)` | `bool` (cascades) |
| `add_relationship` | `(source_id, target_id, relationship_type, attributes)` | `UORRelationship \| None` |
| `get_relationship` | `(relationship_id: str)` | `UORRelationship \| None` |
| `get_relationships` | `(entity_id: str, relationship_type: str \| None)` | `list[UORRelationship]` |
| `remove_relationship` | `(relationship_id: str)` | `bool` |
| `get_neighbors` | `(entity_id: str)` | `list[UOREntity]` |
| `find_path` | `(source_id, target_id: str)` | `list[str]` |
| `to_dict` | `()` | `dict[str, Any]` |

**Properties**: `entity_count`, `relationship_count`, `all_relationships`, `manager`

**Dunder**: `__len__` (returns entity count), `__repr__`

---

## `derivation.DerivationRecord`

Frozen dataclass.

| Field | Type | Description |
|---|---|---|
| `id` | `str` | Content-addressed URN |
| `entity_id` | `str` | Related entity |
| `operation` | `str` | Operation name |
| `inputs` | `dict[str, Any]` | Input data |
| `result_hash` | `str` | Resulting state hash |
| `timestamp` | `str` | ISO timestamp |

**Static Methods**: `_compute_derivation_id(entity_id, operation, inputs, result_hash) → str`

---

## `derivation.DerivationTracker`

| Method | Signature | Returns |
|---|---|---|
| `record` | `(entity_id, operation, inputs, result_hash)` | `DerivationRecord` |
| `get_history` | `(entity_id: str)` | `list[DerivationRecord]` |
| `verify_chain` | `(entity_id: str)` | `bool` |

**Properties**: `all_records`

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [Parent](../API_SPECIFICATION.md)
