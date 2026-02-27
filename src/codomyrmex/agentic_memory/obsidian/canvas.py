"""JSON Canvas operations — parse, create, serialise, mutate.

Implements the `Obsidian JSON Canvas spec
<https://jsoncanvas.org/spec/1.0/>`_.
"""

from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any

from codomyrmex.agentic_memory.obsidian.models import (
    Canvas,
    CanvasEdge,
    CanvasNode,
)

# ── parse / create ───────────────────────────────────────────────────


def parse_canvas(path: str | Path) -> Canvas:
    """Read a ``.canvas`` JSON file into a ``Canvas`` object."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Canvas file not found: {path}")
    data = json.loads(path.read_text())
    canvas = canvas_from_dict(data)
    canvas.path = path
    return canvas


def create_canvas(
    path: str | Path,
    *,
    nodes: list[CanvasNode] | None = None,
    edges: list[CanvasEdge] | None = None,
) -> Canvas:
    """Create a new canvas file and return the ``Canvas`` object."""
    path = Path(path)
    canvas = Canvas(nodes=nodes or [], edges=edges or [], path=path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(canvas_to_dict(canvas), indent=2))
    return canvas


def save_canvas(canvas: Canvas, path: str | Path | None = None) -> Path:
    """Save a canvas to disk. Uses ``canvas.path`` if *path* is not given.

    Returns the path where the file was saved.
    """
    target = Path(path) if path else canvas.path
    if target is None:
        raise ValueError("No path specified for canvas")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(canvas_to_dict(canvas), indent=2))
    canvas.path = target
    return target


# ── serialisation ────────────────────────────────────────────────────


def canvas_to_dict(canvas: Canvas) -> dict[str, Any]:
    """Convert a ``Canvas`` to a JSON-serialisable dict.

    ``None``-valued optional fields are omitted.
    """
    nodes: list[dict[str, Any]] = []
    for n in canvas.nodes:
        d: dict[str, Any] = {
            "id": n.id, "type": n.type,
            "x": n.x, "y": n.y,
            "width": n.width, "height": n.height,
        }
        for key in ("text", "file", "url", "color", "label"):
            val = getattr(n, key, None)
            if val is not None:
                d[key] = val
        nodes.append(d)

    edges: list[dict[str, Any]] = []
    for e in canvas.edges:
        d = {"id": e.id, "fromNode": e.fromNode, "toNode": e.toNode}
        for key in ("fromSide", "toSide", "label", "color"):
            val = getattr(e, key, None)
            if val is not None:
                d[key] = val
        edges.append(d)

    return {"nodes": nodes, "edges": edges}


def canvas_from_dict(data: dict[str, Any]) -> Canvas:
    """Reconstruct a ``Canvas`` from a dict (e.g. from ``json.load``)."""
    nodes: list[CanvasNode] = []
    for nd in data.get("nodes", []):
        nodes.append(CanvasNode(
            id=nd["id"],
            type=nd["type"],
            x=nd.get("x", 0),
            y=nd.get("y", 0),
            width=nd.get("width", 250),
            height=nd.get("height", 140),
            text=nd.get("text"),
            file=nd.get("file"),
            url=nd.get("url"),
            color=nd.get("color"),
            label=nd.get("label"),
        ))

    edges: list[CanvasEdge] = []
    for ed in data.get("edges", []):
        edges.append(CanvasEdge(
            id=ed["id"],
            fromNode=ed.get("fromNode", ""),
            toNode=ed.get("toNode", ""),
            fromSide=ed.get("fromSide"),
            toSide=ed.get("toSide"),
            label=ed.get("label"),
            color=ed.get("color"),
        ))

    return Canvas(nodes=nodes, edges=edges)


# ── mutation helpers ─────────────────────────────────────────────────


def add_canvas_node(canvas: Canvas, node: CanvasNode) -> Canvas:
    """Append a node to the canvas (mutates in place, returns same object)."""
    canvas.nodes.append(node)
    return canvas


def add_canvas_edge(canvas: Canvas, edge: CanvasEdge) -> Canvas:
    """Append an edge to the canvas (mutates in place, returns same object)."""
    canvas.edges.append(edge)
    return canvas


def remove_canvas_node(canvas: Canvas, node_id: str) -> CanvasNode | None:
    """Remove a node and all its connected edges. Returns the removed node."""
    removed = None
    for i, n in enumerate(canvas.nodes):
        if n.id == node_id:
            removed = canvas.nodes.pop(i)
            break
    if removed:
        # Also remove connected edges
        canvas.edges = [
            e for e in canvas.edges
            if e.fromNode != node_id and e.toNode != node_id
        ]
    return removed


def remove_canvas_edge(canvas: Canvas, edge_id: str) -> CanvasEdge | None:
    """Remove an edge by ID. Returns the removed edge."""
    for i, e in enumerate(canvas.edges):
        if e.id == edge_id:
            return canvas.edges.pop(i)
    return None


def create_text_node(
    text: str,
    *,
    x: int = 0,
    y: int = 0,
    width: int = 250,
    height: int = 140,
    color: str | None = None,
) -> CanvasNode:
    """Create a text node with an auto-generated ID."""
    return CanvasNode(
        id=f"node-{uuid.uuid4().hex[:8]}",
        type="text",
        x=x, y=y, width=width, height=height,
        text=text, color=color,
    )


def create_file_node(
    file: str,
    *,
    x: int = 0,
    y: int = 0,
    width: int = 250,
    height: int = 140,
) -> CanvasNode:
    """Create a file-reference node with an auto-generated ID."""
    return CanvasNode(
        id=f"node-{uuid.uuid4().hex[:8]}",
        type="file",
        x=x, y=y, width=width, height=height,
        file=file,
    )


def create_link_node(
    url: str,
    *,
    x: int = 0,
    y: int = 0,
    width: int = 250,
    height: int = 140,
) -> CanvasNode:
    """Create a link node with an auto-generated ID."""
    return CanvasNode(
        id=f"node-{uuid.uuid4().hex[:8]}",
        type="link",
        x=x, y=y, width=width, height=height,
        url=url,
    )


def connect_nodes(
    from_id: str,
    to_id: str,
    *,
    from_side: str | None = None,
    to_side: str | None = None,
    label: str | None = None,
) -> CanvasEdge:
    """Create an edge between two nodes with an auto-generated ID."""
    return CanvasEdge(
        id=f"edge-{uuid.uuid4().hex[:8]}",
        fromNode=from_id,
        toNode=to_id,
        fromSide=from_side,
        toSide=to_side,
        label=label,
    )
