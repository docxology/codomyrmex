# Data Lineage — Functional Specification

**Module**: `codomyrmex.data_lineage`  
**Version**: v0.1.0  
**Status**: Active

## 1. Overview

Data provenance and lineage tracking.

## 2. Architecture

### Components

| Component | Type | Description |
|-----------|------|-------------|
| `NodeType` | Class | Types of lineage nodes. |
| `EdgeType` | Class | Types of lineage edges. |
| `LineageNode` | Class | A node in the lineage graph. |
| `LineageEdge` | Class | An edge connecting two nodes. |
| `DataAsset` | Class | A data asset with lineage information. |
| `LineageGraph` | Class | Graph of data lineage relationships. |
| `LineageTracker` | Class | Tracks data lineage through transformations. |
| `ImpactAnalyzer` | Class | Analyzes impact of data changes. |
| `key()` | Function | Get unique key. |
| `to_dict()` | Function | Convert to dictionary. |
| `key()` | Function | Get unique key. |
| `to_dict()` | Function | Convert to dictionary. |
| `compute_checksum()` | Function | Compute checksum of data. |

## 3. Dependencies

See `src/codomyrmex/data_lineage/__init__.py` for import dependencies.

## 4. Public API

```python
from codomyrmex.data_lineage import NodeType, EdgeType, LineageNode, LineageEdge, DataAsset
```

## 5. Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k data_lineage -v
```

## References

- [README.md](README.md) — Human-readable documentation
- [AGENTS.md](AGENTS.md) — Agent coordination guide
- [Source Code](../../../src/codomyrmex/data_lineage/)
