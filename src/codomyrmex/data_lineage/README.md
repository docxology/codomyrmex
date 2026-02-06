# Data Lineage Module

**Version**: v0.1.0 | **Status**: Active

Data provenance and lineage tracking for datasets, transformations, and models.

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

## Exports

| Class | Description |
|-------|-------------|
| `LineageGraph` | Graph of nodes and edges |
| `LineageTracker` | Track datasets and transformations |
| `LineageNode` | Node with id, type, version |
| `LineageEdge` | Edge with source, target, type |
| `DataAsset` | Data asset with schema and checksum |
| `ImpactAnalyzer` | Analyze change impact |
| `NodeType` | Enum: dataset, transformation, model, artifact |
| `EdgeType` | Enum: derived_from, produced_by, used_by, input_to |

## Navigation

- [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
