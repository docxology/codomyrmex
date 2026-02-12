# Data Lineage Module

**Version**: v0.1.0 | **Status**: Active

Data provenance and lineage tracking for datasets, transformations, and models.

## Installation

```bash
uv uv add codomyrmex
```

Or for development:

```bash
uv sync
```

## Key Exports

### Classes

- **`NodeType`** — Types of lineage nodes.
- **`EdgeType`** — Types of lineage edges.
- **`LineageNode`** — A node in the lineage graph.
- **`LineageEdge`** — An edge connecting two nodes.
- **`DataAsset`** — A data asset with lineage information.
- **`LineageGraph`** — Graph of data lineage relationships.
- **`LineageTracker`** — Tracks data lineage through transformations.
- **`ImpactAnalyzer`** — Analyzes impact of data changes.

## Quick Start

```python
from codomyrmex.data_lineage import (
    LineageGraph, LineageTracker, LineageNode, LineageEdge,
    NodeType, EdgeType, ImpactAnalyzer
)

# Build lineage graph
tracker = LineageTracker()

# Register datasets
tracker.register_dataset("raw_data", "Raw Customer Data", "/data/raw")
tracker.register_dataset("clean_data", "Cleaned Data", "/data/clean")

# Register transformation
tracker.register_transformation(
    id="etl_clean",
    name="Data Cleaning ETL",
    inputs=["raw_data"],
    outputs=["clean_data"]
)

# Query lineage
upstream = tracker.graph.get_upstream("clean_data")
print(f"Sources: {[n.name for n in upstream]}")

# Impact analysis
analyzer = ImpactAnalyzer(tracker.graph)
impact = analyzer.analyze_change("raw_data")
print(f"Risk level: {impact['risk_level']}")
print(f"Affected: {impact['total_affected']} nodes")
```

## Directory Structure

- `models.py` — Data models (LineageNode, LineageEdge, etc.)
- `graph.py` — Graph implementation (LineageGraph, DataAsset)
- `tracker.py` — Lineage tracking logic (LineageTracker, ImpactAnalyzer)
- `__init__.py` — Public API re-exports

## Exports

| Class | Description |
| :--- | :--- |
| `LineageGraph` | Graph of nodes and edges |
| `LineageTracker` | Track datasets and transformations |
| `LineageNode` | Node with id, type, version |
| `LineageEdge` | Edge with source, target, type |
| `DataAsset` | Data asset with schema and checksum |
| `ImpactAnalyzer` | Analyze change impact |
| `NodeType` | Enum: dataset, transformation, model, artifact |
| `EdgeType` | Enum: derived_from, produced_by, used_by, input_to |

## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k data_lineage -v
```

## Documentation

- [Module Documentation](../../../docs/modules/data_lineage/README.md)
- [Agent Guide](../../../docs/modules/data_lineage/AGENTS.md)
- [Specification](../../../docs/modules/data_lineage/SPEC.md)

## Navigation

- [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
