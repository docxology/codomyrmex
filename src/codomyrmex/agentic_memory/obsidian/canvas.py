"""
Obsidian JSON Canvas Support.

Parse and create .canvas files following the JSON Canvas specification
(https://jsoncanvas.org/).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import Canvas, CanvasEdge, CanvasNode


def canvas_from_dict(data: dict[str, Any], path: Path | None = None) -> Canvas:
    """Deserialize a dict to a Canvas object.

    Args:
        data: JSON-compatible dict with 'nodes' and 'edges' arrays.
        path: Optional path this canvas was loaded from.

    Returns:
        Canvas object with typed nodes and edges.
    """
    nodes = []
    for node_data in data.get("nodes", []):
        nodes.append(
            CanvasNode(
                id=node_data.get("id", ""),
                type=node_data.get("type", "text"),
                x=node_data.get("x", 0),
                y=node_data.get("y", 0),
                width=node_data.get("width", 250),
                height=node_data.get("height", 140),
                text=node_data.get("text"),
                file=node_data.get("file"),
                url=node_data.get("url"),
                label=node_data.get("label"),
                color=node_data.get("color"),
            )
        )

    edges = []
    for edge_data in data.get("edges", []):
        edges.append(
            CanvasEdge(
                id=edge_data.get("id", ""),
                fromNode=edge_data.get("fromNode", ""),
                toNode=edge_data.get("toNode", ""),
                fromSide=edge_data.get("fromSide"),
                toSide=edge_data.get("toSide"),
                label=edge_data.get("label"),
                color=edge_data.get("color"),
            )
        )

    return Canvas(nodes=nodes, edges=edges, path=path)


def canvas_to_dict(canvas: Canvas) -> dict[str, Any]:
    """Serialize a Canvas to a JSON-compatible dict.

    Args:
        canvas: Canvas object to serialize.

    Returns:
        Dict ready for JSON serialization.
    """
    nodes = []
    for node in canvas.nodes:
        node_dict: dict[str, Any] = {
            "id": node.id,
            "type": node.type,
            "x": node.x,
            "y": node.y,
            "width": node.width,
            "height": node.height,
        }
        # Only include optional fields if set
        if node.text is not None:
            node_dict["text"] = node.text
        if node.file is not None:
            node_dict["file"] = node.file
        if node.url is not None:
            node_dict["url"] = node.url
        if node.label is not None:
            node_dict["label"] = node.label
        if node.color is not None:
            node_dict["color"] = node.color
        nodes.append(node_dict)

    edges = []
    for edge in canvas.edges:
        edge_dict: dict[str, Any] = {
            "id": edge.id,
            "fromNode": edge.fromNode,
            "toNode": edge.toNode,
        }
        if edge.fromSide is not None:
            edge_dict["fromSide"] = edge.fromSide
        if edge.toSide is not None:
            edge_dict["toSide"] = edge.toSide
        if edge.label is not None:
            edge_dict["label"] = edge.label
        if edge.color is not None:
            edge_dict["color"] = edge.color
        edges.append(edge_dict)

    return {"nodes": nodes, "edges": edges}


def parse_canvas(path: str | Path) -> Canvas:
    """Read and parse a .canvas file.

    Args:
        path: Path to the .canvas file.

    Returns:
        Canvas object with typed nodes and edges.

    Raises:
        FileNotFoundError: If file doesn't exist.
        json.JSONDecodeError: If file is not valid JSON.
    """
    canvas_path = Path(path)
    if not canvas_path.exists():
        raise FileNotFoundError(f"Canvas file not found: {path}")

    data = json.loads(canvas_path.read_text(encoding="utf-8"))
    return canvas_from_dict(data, path=canvas_path)


def create_canvas(
    path: str | Path,
    nodes: list[CanvasNode] | None = None,
    edges: list[CanvasEdge] | None = None,
) -> Canvas:
    """Create a new .canvas file.

    Args:
        path: Path for the new canvas file.
        nodes: List of canvas nodes.
        edges: List of canvas edges.

    Returns:
        The created Canvas object.
    """
    canvas_path = Path(path)
    canvas = Canvas(
        nodes=nodes or [],
        edges=edges or [],
        path=canvas_path,
    )

    data = canvas_to_dict(canvas)
    canvas_path.parent.mkdir(parents=True, exist_ok=True)
    canvas_path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    return canvas


def add_canvas_node(canvas: Canvas, node: CanvasNode) -> Canvas:
    """Add a node to an existing canvas.

    Args:
        canvas: The canvas to modify.
        node: The node to add.

    Returns:
        The modified canvas (same object).
    """
    canvas.nodes.append(node)
    return canvas


def add_canvas_edge(canvas: Canvas, edge: CanvasEdge) -> Canvas:
    """Add an edge to an existing canvas.

    Args:
        canvas: The canvas to modify.
        edge: The edge to add.

    Returns:
        The modified canvas (same object).
    """
    canvas.edges.append(edge)
    return canvas
