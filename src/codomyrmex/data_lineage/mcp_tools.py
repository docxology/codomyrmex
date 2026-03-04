"""MCP tool definitions for the data_lineage module.

Exposes data lineage tracking and impact analysis as MCP tools.
"""

from __future__ import annotations

from typing import Any

from codomyrmex.model_context_protocol.decorators import mcp_tool


def _get_data_lineage(config: dict[str, Any] | None = None):
    """Lazy import of DataLineage."""
    from codomyrmex.data_lineage.data_lineage import DataLineage

    return DataLineage(config)


def _get_lineage_graph():
    """Lazy import of LineageGraph."""
    from codomyrmex.data_lineage.graph import LineageGraph

    return LineageGraph


@mcp_tool(
    category="data_lineage",
    description=(
        "Track a data lineage event by registering a dataset or transformation "
        "in the lineage graph."
    ),
)
def data_lineage_track(
    event_type: str,
    node_id: str,
    name: str,
    inputs: list[str] | None = None,
    outputs: list[str] | None = None,
    location: str = "",
) -> dict[str, Any]:
    """Register a dataset or transformation in the lineage graph.

    Args:
        event_type: Type of event - 'dataset' or 'transformation'.
        node_id: Unique identifier for the node.
        name: Human-readable name for the node.
        inputs: List of input node IDs (required for transformations).
        outputs: List of output node IDs (required for transformations).
        location: Location of the dataset (for dataset events).

    Returns:
        dict with keys: status, node_id, node_type
    """
    if event_type not in ("dataset", "transformation"):
        return {"status": "error", "message": f"Unknown event_type: {event_type}. Use 'dataset' or 'transformation'."}
    try:
        lineage = _get_data_lineage()
        if event_type == "dataset":
            node = lineage.track(event_type, id=node_id, name=name, location=location)
        else:
            node = lineage.track(
                event_type,
                id=node_id,
                name=name,
                inputs=inputs or [],
                outputs=outputs or [],
            )
        return {
            "status": "success",
            "node_id": node.id,
            "node_type": node.node_type.value,
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="data_lineage",
    description="Analyze the downstream impact of changing a node in the lineage graph.",
)
def data_lineage_analyze_impact(node_id: str) -> dict[str, Any]:
    """Analyze the impact of changes to a specific node.

    Args:
        node_id: ID of the node to analyze impact for.

    Returns:
        dict with keys: status, source_node, total_affected, risk_level,
        affected_datasets, affected_models, affected_transformations
    """
    try:
        lineage = _get_data_lineage()
        # Register at least the source node so analyze doesn't fail
        lineage.tracker.register_dataset(node_id, node_id)
        result = lineage.analyze(node_id)
        return {
            "status": "success",
            "source_node": result["source_node"],
            "total_affected": result["total_affected"],
            "risk_level": result["risk_level"],
            "affected_datasets": result["affected_datasets"],
            "affected_models": result["affected_models"],
            "affected_transformations": result["affected_transformations"],
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="data_lineage",
    description="Validate a lineage graph for cycles and return graph statistics.",
)
def data_lineage_validate_graph() -> dict[str, Any]:
    """Create and validate a lineage graph, returning statistics.

    Returns:
        dict with keys: status, node_count, edge_count, has_cycles, leaf_nodes
    """
    try:
        GraphClass = _get_lineage_graph()
        graph = GraphClass()
        cycles = graph.validate_graph()
        return {
            "status": "success",
            "node_count": graph.node_count,
            "edge_count": graph.edge_count,
            "has_cycles": len(cycles) > 0,
            "cycle_nodes": cycles,
            "leaf_node_count": len(graph.get_leaf_nodes()),
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}
