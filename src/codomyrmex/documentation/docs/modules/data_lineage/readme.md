# Data Lineage Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

The `data_lineage` module provides comprehensive tracking and analysis of data flow within the Codomyrmex ecosystem. It enables tracing the origins of data assets (upstream), identifying downstream dependencies, and performing impact analysis for data changes.

## Features

- **Graph-based Lineage**: Uses a Directed Acyclic Graph (DAG) to represent relationships between data assets, transformations, and models.
- **Impact Analysis**: Automatically calculate the downstream impact of changing a data source, including affected models and dashboards.
- **Cycle Detection**: Ensure lineage remains a DAG with built-in cycle validation.
- **Visualization**: Export lineage graphs to DOT format for easy visualization.
- **Zero-Mock Integrity**: Designed for real execution and testing.

## Quick Start

```python
from codomyrmex.data_lineage import LineageTracker, ImpactAnalyzer

# Initialize tracker
tracker = LineageTracker()

# Register data assets
tracker.register_dataset("raw_users", "Raw User Data", location="s3://raw/users")
tracker.register_dataset("clean_users", "Clean User Data", location="s3://prod/users")

# Register transformation
tracker.register_transformation(
    id="user_cleaning",
    name="Clean User Records",
    inputs=["raw_users"],
    outputs=["clean_users"]
)

# Analyze impact of changes
analyzer = ImpactAnalyzer(tracker.graph)
impact = analyzer.analyze_change("raw_users")
print(f"Total affected nodes: {impact['total_affected']}")
```

## Directory Contents

- `__init__.py`: Package entry point and exports.
- `data_lineage.py`: High-level `DataLineage` orchestrator.
- `graph.py`: Core `LineageGraph` implementation.
- `models.py`: Data classes for nodes, edges, and assets.
- `tracker.py`: Lineage tracking and impact analysis logic.

## Testing

Run tests using pytest:
```bash
pytest src/codomyrmex/tests/unit/data_lineage/
```
