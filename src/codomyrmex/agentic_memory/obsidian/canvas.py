"""JSON Canvas operations — parse, create, serialise.

Implements the `Obsidian JSON Canvas spec
<https://jsoncanvas.org/spec/1.0/>`_.
"""

from __future__ import annotations

import json
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


# ── serialisation ────────────────────────────────────────────────────


def canvas_to_dict(canvas: Canvas) -> dict[str, Any]:
    """Convert a ``Canvas`` to a JSON-serialisable dict.

    ``None``-valued optional fields are omitted.
    """
    nodes: list[dict[str, Any]] = []
    for n in canvas.nodes:
        d: dict[str, Any] = {"id": n.id, "type": n.type, "x": n.x, "y": n.y, "width": n.width, "height": n.height}
        for key in ("text", "file", "url", "color"):
            val = getattr(n, key, None)
            if val is not None:
                d[key] = val
        nodes.append(d)

    edges: list[dict[str, Any]] = []
    for e in canvas.edges:
        d = {"id": e.id, "fromNode": e.fromNode, "toNode": e.toNode}
        for key in ("fromSide", "toSide", "label"):
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
