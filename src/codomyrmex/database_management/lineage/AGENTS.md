# Lineage — Agent Coordination

## Purpose

Provides data lineage tracking for AI agents, enabling them to trace data origins, map transformation pipelines, and assess the downstream impact of data changes through a directed acyclic graph.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `models.py` | `NodeType` | Enum for lineage node types: `DATASET`, `TRANSFORMATION`, `MODEL`, `ARTIFACT`, `EXTERNAL` |
| `models.py` | `EdgeType` | Enum for edge relationships: `DERIVED_FROM`, `PRODUCED_BY`, `USED_BY`, `INPUT_TO` |
| `models.py` | `LineageNode` | Dataclass representing a node with `id`, `name`, `node_type`, and `metadata` |
| `models.py` | `LineageEdge` | Dataclass representing a directed edge with `source_id`, `target_id`, `edge_type`, and `metadata` |
| `models.py` | `DataAsset` | Dataclass for tracked data assets with `name`, `location`, `schema`, and `tags` |
| `graph.py` | `LineageGraph` | Thread-safe directed graph with DFS-based `get_upstream`, `get_downstream`, and `get_path` traversals |
| `tracker.py` | `LineageTracker` | High-level API for registering datasets and transformations with automatic edge creation |
| `tracker.py` | `ImpactAnalyzer` | Analyses downstream impact of data changes, returning affected nodes and risk level |

## Operating Contracts

- Agents MUST register datasets before referencing them as transformation inputs or outputs.
- `LineageGraph` is thread-safe via `threading.Lock`; concurrent node/edge additions are supported.
- `get_upstream` and `get_downstream` accept an optional `max_depth` parameter to bound traversal scope.
- `ImpactAnalyzer.analyze_change` classifies risk as `"high"` when downstream models exist, `"medium"` for datasets, `"low"` otherwise.
- `LineageTracker.register_transformation` automatically creates `INPUT_TO` edges for inputs and `PRODUCED_BY` edges for outputs.
- `LineageGraph.to_dict` serializes the full graph to a dictionary for persistence or transfer.

## Integration Points

- **database_management/migration**: Migration steps may register as transformations in the lineage graph.
- **orchestrator**: Workflow DAGs can be reflected as lineage transformations for end-to-end traceability.
- **data_visualization**: Lineage graphs can be exported for visual rendering.

## Navigation

- **Parent**: [database_management/README.md](../README.md)
- **Siblings**: [backup/](../backup/), [migration/](../migration/)
- **RASP**: [README.md](README.md) | **AGENTS.md** | [SPEC.md](SPEC.md) | [PAI.md](PAI.md)
