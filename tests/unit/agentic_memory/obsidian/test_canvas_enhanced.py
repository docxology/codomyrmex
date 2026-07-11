"""Tests for enhanced canvas features.

Tests for save_canvas, remove_canvas_node/edge, factory functions
(create_text_node, create_file_node, create_link_node, connect_nodes),
Canvas.get_node/get_edge, label/color serialization.
"""

import json

import pytest

from codomyrmex.agentic_memory.obsidian.canvas import (
    canvas_from_dict,
    canvas_to_dict,
    connect_nodes,
    create_canvas,
    create_file_node,
    create_link_node,
    create_text_node,
    parse_canvas,
    remove_canvas_edge,
    remove_canvas_node,
    save_canvas,
)
from codomyrmex.agentic_memory.obsidian.models import Canvas, CanvasEdge, CanvasNode


class TestSaveCanvas:
    def test_save_to_path(self, tmp_path):
        canvas = Canvas(
            nodes=[CanvasNode(id="n1", type="text", text="Saved")],
            edges=[],
        )
        path = tmp_path / "saved.canvas"
        result = save_canvas(canvas, path)
        assert result == path
        assert path.exists()
        data = json.loads(path.read_text())
        assert data["nodes"][0]["text"] == "Saved"

    def test_save_to_canvas_path(self, tmp_path):
        path = tmp_path / "auto.canvas"
        canvas = create_canvas(path)
        canvas.nodes.append(CanvasNode(id="n1", type="text", text="Auto"))
        save_canvas(canvas)
        data = json.loads(path.read_text())
        assert len(data["nodes"]) == 1

    def test_save_no_path_raises(self):
        canvas = Canvas()
        canvas.path = None
        with pytest.raises(ValueError):
            save_canvas(canvas)


class TestRemoveCanvasNode:
    def test_remove_node(self):
        canvas = Canvas(
            nodes=[
                CanvasNode(id="a", type="text"),
                CanvasNode(id="b", type="text"),
            ],
            edges=[
                CanvasEdge(id="e1", fromNode="a", toNode="b"),
            ],
        )
        removed = remove_canvas_node(canvas, "a")
        assert removed is not None
        assert removed.id == "a"
        assert len(canvas.nodes) == 1
        # Edge should also be removed (cascading)
        assert len(canvas.edges) == 0

    def test_remove_nonexistent(self):
        canvas = Canvas(nodes=[CanvasNode(id="a", type="text")])
        removed = remove_canvas_node(canvas, "zzz")
        assert removed is None
        assert len(canvas.nodes) == 1


class TestRemoveCanvasEdge:
    def test_remove_edge(self):
        edge = CanvasEdge(id="e1", fromNode="a", toNode="b")
        canvas = Canvas(edges=[edge])
        removed = remove_canvas_edge(canvas, "e1")
        assert removed is not None
        assert removed.id == "e1"
        assert len(canvas.edges) == 0

    def test_remove_nonexistent_edge(self):
        canvas = Canvas(edges=[CanvasEdge(id="e1", fromNode="a", toNode="b")])
        removed = remove_canvas_edge(canvas, "zzz")
        assert removed is None
        assert len(canvas.edges) == 1


class TestCanvasFactories:
    def test_create_text_node(self):
        node = create_text_node("Hello", x=10, y=20, color="#ff0000")
        assert node.type == "text"
        assert node.text == "Hello"
        assert node.x == 10
        assert node.color == "#ff0000"
        assert node.id.startswith("node-")

    def test_create_file_node(self):
        node = create_file_node("notes/test.md", x=100, y=200)
        assert node.type == "file"
        assert node.file == "notes/test.md"

    def test_create_link_node(self):
        node = create_link_node("https://example.com")
        assert node.type == "link"
        assert node.url == "https://example.com"

    def test_connect_nodes(self):
        edge = connect_nodes("n1", "n2", from_side="right", to_side="left", label="ref")
        assert edge.fromNode == "n1"
        assert edge.toNode == "n2"
        assert edge.fromSide == "right"
        assert edge.label == "ref"
        assert edge.id.startswith("edge-")

    def test_unique_ids(self):
        n1 = create_text_node("A")
        n2 = create_text_node("B")
        assert n1.id != n2.id


class TestCanvasGetMethods:
    def test_get_node(self, tmp_canvas_file):
        canvas = parse_canvas(tmp_canvas_file)
        node = canvas.get_node("node-1")
        assert node is not None
        assert node.text == "Hello World"

    def test_get_node_not_found(self, tmp_canvas_file):
        canvas = parse_canvas(tmp_canvas_file)
        assert canvas.get_node("nonexistent") is None

    def test_get_edge(self, tmp_canvas_file):
        canvas = parse_canvas(tmp_canvas_file)
        edge = canvas.get_edge("edge-1")
        assert edge is not None
        assert edge.label == "references"

    def test_get_edge_not_found(self, tmp_canvas_file):
        canvas = parse_canvas(tmp_canvas_file)
        assert canvas.get_edge("nonexistent") is None


class TestColorLabelSerialization:
    def test_color_roundtrip(self, tmp_canvas_file):
        canvas = parse_canvas(tmp_canvas_file)
        # node-4 has color="#ff5555"
        colored = canvas.get_node("node-4")
        assert colored is not None
        assert colored.color == "#ff5555"

        # Serialize and re-parse
        d = canvas_to_dict(canvas)
        restored = canvas_from_dict(d)
        colored2 = restored.get_node("node-4")
        assert colored2 is not None
        assert colored2.color == "#ff5555"

    def test_label_not_serialized_when_none(self):
        node = CanvasNode(id="n1", type="text", text="No label")
        d = canvas_to_dict(Canvas(nodes=[node]))
        assert "label" not in d["nodes"][0]
