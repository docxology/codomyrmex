"""MCP tools for the data_lineage module.

Exposes data lineage tracking and impact analysis capabilities
as auto-discovered MCP tools.
"""

from __future__ import annotations

from typing import Any

from codomyrmex.model_context_protocol.decorators import mcp_tool

# Use a global instance to allow state across tool calls if desired,
# but usually the tools will just operate on a given state or return info.
# Here we'll manage a module-level singleton tracker for the tools.
_GLOBAL_LINEAGE: Any = None


def _get_tracker() -> Any:
    global _GLOBAL_LINEAGE
    if _GLOBAL_LINEAGE is None:
        from codomyrmex.data_lineage import DataLineage
        _GLOBAL_LINEAGE = DataLineage()
    return _GLOBAL_LINEAGE


@mcp_tool(
    category="data_lineage",
    description=(
        "Track a data lineage event (either a dataset or a transformation). "
        "For event_type='dataset', provide 'id' and 'name'. "
        "For event_type='transformation', provide 'id', 'name', 'inputs' (list of ids), and 'outputs' (list of ids)."
    ),
)
def data_lineage_track_event(
    event_type: str,
    event_id: str,
    name: str,
    inputs: list[str] | None = None,
    outputs: list[str] | None = None,
    location: str = "",
) -> dict[str, Any]:
    """Track a new lineage event.

    Args:
        event_type: Type of event ('dataset' or 'transformation').
        event_id: The ID of the dataset or transformation.
        name: The name of the dataset or transformation.
        inputs: List of input IDs (required if event_type='transformation').
        outputs: List of output IDs (required if event_type='transformation').
        location: Dataset location (optional, for event_type='dataset').

    Returns:
        A dictionary with the tracked node details.
    """
    lineage = _get_tracker()

    if event_type == "dataset":
        node = lineage.track("dataset", id=event_id, name=name, location=location)
        return node.to_dict()
    elif event_type == "transformation":
        inputs = inputs or []
        outputs = outputs or []
        node = lineage.track(
            "transformation",
            id=event_id,
            name=name,
            inputs=inputs,
            outputs=outputs,
        )
        return node.to_dict()
    else:
        raise ValueError(f"Unknown event type: {event_type}")


@mcp_tool(
    category="data_lineage",
    description="Analyze the downstream impact of changing a specific node in the data lineage graph.",
)
def data_lineage_analyze_impact(node_id: str) -> dict[str, Any]:
    """Analyze the impact of a lineage node.

    Args:
        node_id: The ID of the node to analyze.

    Returns:
        A dictionary containing impact analysis results.
    """
    lineage = _get_tracker()
    return lineage.analyze(node_id)


@mcp_tool(
    category="data_lineage",
    description="Get the original source nodes (origins) for a given node in the lineage graph.",
)
def data_lineage_get_origin(node_id: str) -> list[dict[str, Any]]:
    """Get the original source data nodes for a given node.

    Args:
        node_id: The ID of the node.

    Returns:
        A list of origin node dictionaries.
    """
    lineage = _get_tracker()
    origins = lineage.tracker.get_origin(node_id)
    return [n.to_dict() for n in origins]
