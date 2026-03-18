# Data Lineage Specification

**Version**: v1.2.3 | **Status**: Active | **Last Updated**: March 2026

## Overview

Tracks data lineage through transformations with graph-based analysis. Models data assets, transformations, and dependencies as a directed graph for impact analysis and provenance tracking.

## Functional Requirements

1. Model data assets as LineageNode with NodeType classification (source, transformation, sink)
2. Track transformation relationships as LineageEdge with EdgeType metadata
3. Graph-based impact analysis to determine all downstream consumers of a data asset


## Interface

```python
from codomyrmex.data_lineage import LineageTracker, ImpactAnalyzer, LineageGraph

tracker = LineageTracker()
tracker.add_asset(DataAsset(name="raw_users", node_type=NodeType.SOURCE))
tracker.add_transformation(source="raw_users", target="clean_users")
analyzer = ImpactAnalyzer(tracker.graph)
impact = analyzer.analyze("raw_users")
```

## Exports

NodeType, EdgeType, LineageNode, LineageEdge, DataAsset, LineageGraph, LineageTracker, ImpactAnalyzer, DataLineage, create_data_lineage

## Navigation

- [Source README](../../src/codomyrmex/data_lineage/README.md) | [AGENTS.md](AGENTS.md)
