# data_lineage

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Data provenance and lineage tracking through a directed graph model. Tracks how datasets flow through transformations and into models, enabling upstream/downstream traversal, path finding between nodes, and change impact analysis. Useful for understanding data dependencies and assessing the blast radius of data changes.

## Key Exports

### Enums

- **`NodeType`** -- Types of lineage nodes: DATASET, TRANSFORMATION, MODEL, ARTIFACT, EXTERNAL
- **`EdgeType`** -- Types of lineage edges: DERIVED_FROM, PRODUCED_BY, USED_BY, INPUT_TO

### Data Classes

- **`LineageNode`** -- A node in the lineage graph with ID, name, type, version, and metadata; provides a unique `key` property and `to_dict()` serialization
- **`LineageEdge`** -- A directed edge connecting two nodes with source/target IDs, edge type, and metadata
- **`DataAsset`** -- A data asset with location, schema, row count, size, and checksum; includes `compute_checksum()` for SHA-256 hashing of raw data

### Services

- **`LineageGraph`** -- Thread-safe directed graph for lineage relationships; supports adding/querying nodes and edges, depth-limited upstream and downstream traversal via DFS, path finding between nodes, and full graph serialization
- **`LineageTracker`** -- High-level lineage tracking; registers datasets and transformations with explicit input/output relationships, and queries for data origins and downstream impact
- **`ImpactAnalyzer`** -- Analyzes the impact of changing a node; returns affected datasets, models, and transformations with a risk level classification (low/medium/high)

## Directory Contents

- `__init__.py` -- Module implementation with graph model, tracker, and impact analyzer
- `README.md` -- This file
- `AGENTS.md` -- Agent integration documentation
- `API_SPECIFICATION.md` -- Programmatic API specification
- `MCP_TOOL_SPECIFICATION.md` -- Model Context Protocol tool definitions
- `PAI.md` -- PAI integration notes
- `SPEC.md` -- Module specification
- `py.typed` -- PEP 561 type stub marker

## Navigation

- **Full Documentation**: [docs/modules/data_lineage/](../../../docs/modules/data_lineage/)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
