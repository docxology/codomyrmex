# Agent Guidelines - Data Lineage

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Module Overview

The `data_lineage` module provides a graph-based framework for tracking data movement and transformations.

## Core Concepts

- **LineageNode**: Represents a data entity (Dataset, Transformation, Model, etc.).
- **LineageEdge**: Represents a relationship between nodes (Input to, Produced by, etc.).
- **LineageGraph**: The DAG containing all nodes and edges.
- **ImpactAnalyzer**: Tool for assessing the blast radius of changes.

## Best Practices for Agents

1. **Always use IDs**: When registering nodes, ensure IDs are unique across the ecosystem.
2. **Validate Before Export**: Always call `graph.validate_graph()` before using the graph for critical path analysis to ensure no cycles were introduced.
3. **Capture Metadata**: Use the `metadata` field to store environment-specific information like timestamps, row counts, or schema versions.
4. **Prefer Upstream Tracing**: When diagnosing data quality issues, use `get_origin()` to find the root source of the data.

## MCP Tools

The `mcp_tools.py` file exposes data lineage functionality to agents. Use these tools:
- `data_lineage_track_event`: Register a new dataset or transformation.
- `data_lineage_analyze_impact`: Get the impact radius of a node change.
- `data_lineage_get_origin`: Trace the lineage up to the original source node(s).

## Common Operations

### Tracing Upstream
```python
origins = tracker.get_origin("final_report_dataset")
for origin in origins:
    print(f"Report depends on: {origin.name}")
```

### Visualizing Subgraphs
```python
dot_output = tracker.graph.export_to_dot()
# Save to file or render
```

### Checking for Cycles
```python
cycles = tracker.graph.validate_graph()
if cycles:
    raise ValueError(f"Cycle detected involving nodes: {cycles}")
```

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | Primary Capabilities | Trust Level |
|-----------|-------------|---------------------|-------------|
| **Engineer** | Full | Registering nodes/edges, analyzing impact | TRUSTED |
| **Architect** | Read | Reviewing lineage topology | OBSERVED |
| **DataScientist**| Read/Write | Tracking model lineage | TRUSTED |

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
