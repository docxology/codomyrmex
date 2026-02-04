# Data Lineage Module Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The `data_lineage` module provides data provenance and lineage tracking through a directed graph model. It enables recording how data flows through transformations, tracing the origin of any dataset, and analyzing the downstream impact of changes. The module supports multiple node types (datasets, transformations, models, artifacts, external sources) connected by typed edges representing derivation, production, usage, and input relationships.

## Key Features

- **Directed lineage graph**: `LineageGraph` stores nodes and edges representing data flow with thread-safe operations
- **Multi-type node support**: Track datasets, transformations, models, artifacts, and external sources via `NodeType` enum
- **Typed edge relationships**: Express derivation, production, usage, and input relationships via `EdgeType` enum
- **Upstream tracing**: `get_upstream()` performs depth-first traversal to find all ancestor nodes of a given data asset
- **Downstream tracing**: `get_downstream()` finds all descendant nodes affected by changes to a source node
- **Path finding**: `get_path()` discovers the route between any two nodes in the lineage graph
- **Transformation registration**: `LineageTracker.register_transformation()` atomically creates a transformation node with input and output edges
- **Origin discovery**: `get_origin()` traces back to the original source datasets that have no further upstream dependencies
- **Impact analysis**: `ImpactAnalyzer` assesses the blast radius of data changes, categorizing affected datasets, models, and transformations with risk levels
- **Data asset tracking**: `DataAsset` dataclass with schema, row count, size, and SHA-256 checksum computation

## Key Components

| Component | Description |
|-----------|-------------|
| `NodeType` | Enum defining lineage node categories: DATASET, TRANSFORMATION, MODEL, ARTIFACT, EXTERNAL |
| `EdgeType` | Enum for relationship types: DERIVED_FROM, PRODUCED_BY, USED_BY, INPUT_TO |
| `LineageNode` | Dataclass representing a node in the lineage graph with id, name, type, version, and metadata |
| `LineageEdge` | Dataclass representing a directed edge between two nodes with source, target, and edge type |
| `DataAsset` | Dataclass for data assets with location, schema, row count, size, and checksum fields |
| `LineageGraph` | Core graph structure storing nodes and edges; provides upstream/downstream traversal and path finding |
| `LineageTracker` | High-level API for registering datasets and transformations with automatic edge creation |
| `ImpactAnalyzer` | Analyzes the downstream impact of changes to a node, returning affected counts and risk level |

## Quick Start

```python
from codomyrmex.data_lineage import (
    LineageGraph,
    LineageTracker,
    ImpactAnalyzer,
    LineageNode,
    LineageEdge,
    NodeType,
    EdgeType,
)

# Build lineage graph directly
graph = LineageGraph()
graph.add_node(LineageNode(id="raw_data", name="Raw Data", node_type=NodeType.DATASET))
graph.add_node(LineageNode(id="clean_data", name="Clean Data", node_type=NodeType.DATASET))
graph.add_node(LineageNode(id="model", name="ML Model", node_type=NodeType.MODEL))
graph.add_edge(LineageEdge("raw_data", "clean_data", EdgeType.DERIVED_FROM))
graph.add_edge(LineageEdge("clean_data", "model", EdgeType.INPUT_TO))

# Query lineage
upstream = graph.get_upstream("model")
print(f"Model depends on: {[n.name for n in upstream]}")

downstream = graph.get_downstream("raw_data")
print(f"Raw data affects: {[n.name for n in downstream]}")

path = graph.get_path("raw_data", "model")
print(f"Path: {' -> '.join(path)}")

# Use the higher-level tracker API
tracker = LineageTracker()
tracker.register_dataset("sales", "Sales Data", location="s3://bucket/sales.csv")
tracker.register_dataset("features", "Feature Set", location="s3://bucket/features.parquet")
tracker.register_transformation(
    id="feature_engineering",
    name="Feature Engineering",
    inputs=["sales"],
    outputs=["features"],
)

# Discover data origins
origins = tracker.get_origin("features")
print(f"Original sources: {[n.name for n in origins]}")

# Analyze impact of changes
analyzer = ImpactAnalyzer(tracker.graph)
impact = analyzer.analyze_change("sales")
print(f"Affects {impact['total_affected']} nodes, risk: {impact['risk_level']}")
```

## Related Modules

- [database_management](../database_management/) - Data persistence layer whose schemas may be tracked by lineage
- [logging_monitoring](../logging_monitoring/) - Centralized logging for lineage tracking events
- [orchestrator](../orchestrator/) - Workflow orchestration where transformation lineage is recorded

## Navigation

- **Source**: [src/codomyrmex/data_lineage/](../../../src/codomyrmex/data_lineage/)
- **Parent**: [docs/modules/](../README.md)
