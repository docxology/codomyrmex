# Agent Guidelines - Data Lineage

## Module Overview

Data provenance and lineage tracking for datasets, transformations, and models.

## Key Classes

- **LineageGraph** — Graph of nodes and edges
- **LineageTracker** — Track datasets and transformations
- **LineageNode** — Node with id, type, version, metadata
- **LineageEdge** — Edge with source, target, type
- **ImpactAnalyzer** — Analyze change impact

## Agent Instructions

1. **Register all data sources** — Use `register_dataset()` for all inputs
2. **Track transformations** — Use `register_transformation()` with inputs/outputs
3. **Version everything** — Include version in node metadata
4. **Query before changes** — Use `get_downstream()` to check impact
5. **Export for audit** — Use `graph.to_dict()` for serialization

## Common Patterns

```python
from codomyrmex.data_lineage import LineageTracker, ImpactAnalyzer

tracker = LineageTracker()

# Register data pipeline
tracker.register_dataset("raw", "Raw Data", "/data/raw")
tracker.register_dataset("clean", "Clean Data", "/data/clean")
tracker.register_transformation(
    "etl", "ETL Job", inputs=["raw"], outputs=["clean"]
)

# Check impact before changing raw data
analyzer = ImpactAnalyzer(tracker.graph)
impact = analyzer.analyze_change("raw")
if impact["risk_level"] == "high":
    notify_stakeholders()
```

## Testing Patterns

```python
# Verify lineage tracking
tracker = LineageTracker()
tracker.register_dataset("a", "A", "/a")
tracker.register_dataset("b", "B", "/b")
tracker.register_transformation("t", "T", ["a"], ["b"])

upstream = tracker.graph.get_upstream("b")
assert len(upstream) == 2  # a and t
```

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
