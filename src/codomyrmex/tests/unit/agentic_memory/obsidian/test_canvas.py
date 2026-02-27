"""Tests for Obsidian JSON Canvas support."""

import json

import pytest

from codomyrmex.agentic_memory.obsidian.canvas import (
    add_canvas_edge,
    add_canvas_node,
    canvas_from_dict,
    canvas_to_dict,
    create_canvas,
    parse_canvas,
)
from codomyrmex.agentic_memory.obsidian.models import (
    Canvas,
    CanvasEdge,
    CanvasNode,
)


class TestParseCanvas:
    """Test suite for ParseCanvas."""
    def test_parse_nodes(self, tmp_canvas_file):
        """Test functionality: parse nodes."""
        canvas = parse_canvas(tmp_canvas_file)
        assert len(canvas.nodes) == 4

    def test_parse_edges(self, tmp_canvas_file):
        """Test functionality: parse edges."""
        canvas = parse_canvas(tmp_canvas_file)
        assert len(canvas.edges) == 2
        assert canvas.edges[0].label == "references"

    def test_parse_node_types(self, tmp_canvas_file):
        """Test functionality: parse node types."""
        canvas = parse_canvas(tmp_canvas_file)
        types = {n.type for n in canvas.nodes}
        assert "text" in types
        assert "file" in types
        assert "link" in types

    def test_parse_text_node(self, tmp_canvas_file):
        """Test functionality: parse text node."""
        canvas = parse_canvas(tmp_canvas_file)
        text_nodes = [n for n in canvas.nodes if n.type == "text"]
        assert len(text_nodes) == 2
        assert text_nodes[0].text == "Hello World"

    def test_parse_file_not_found(self, tmp_path):
        """Test functionality: parse file not found."""
        with pytest.raises(FileNotFoundError):
            parse_canvas(tmp_path / "nonexistent.canvas")

    def test_parse_sets_path(self, tmp_canvas_file):
        """Test functionality: parse sets path."""
        canvas = parse_canvas(tmp_canvas_file)
        assert canvas.path == tmp_canvas_file


class TestCreateCanvas:
    """Test suite for CreateCanvas."""
    def test_create_basic(self, tmp_path):
        """Test functionality: create basic."""
        path = tmp_path / "new.canvas"
        nodes = [
            CanvasNode(id="n1", type="text", text="Test"),
        ]
        canvas = create_canvas(path, nodes=nodes)
        assert path.exists()
        assert len(canvas.nodes) == 1

    def test_create_roundtrip(self, tmp_path):
        """Test functionality: create roundtrip."""
        path = tmp_path / "roundtrip.canvas"
        nodes = [
            CanvasNode(id="n1", type="text", x=10, y=20, text="Hello"),
            CanvasNode(id="n2", type="file", file="test.md"),
        ]
        edges = [
            CanvasEdge(id="e1", fromNode="n1", toNode="n2"),
        ]
        create_canvas(path, nodes=nodes, edges=edges)

        # Re-read
        canvas2 = parse_canvas(path)
        assert len(canvas2.nodes) == 2
        assert len(canvas2.edges) == 1
        assert canvas2.nodes[0].text == "Hello"

    def test_create_empty(self, tmp_path):
        """Test functionality: create empty."""
        path = tmp_path / "empty.canvas"
        canvas = create_canvas(path)
        assert path.exists()
        data = json.loads(path.read_text())
        assert data["nodes"] == []
        assert data["edges"] == []


class TestCanvasSerialization:
    """Test suite for CanvasSerialization."""
    def test_to_dict(self):
        """Test functionality: to dict."""
        canvas = Canvas(
            nodes=[CanvasNode(id="n1", type="text", text="Hi")],
            edges=[],
        )
        d = canvas_to_dict(canvas)
        assert len(d["nodes"]) == 1
        assert d["nodes"][0]["text"] == "Hi"
        # Optional None fields should not be in dict
        assert "file" not in d["nodes"][0]

    def test_from_dict(self):
        """Test functionality: from dict."""
        data = {
            "nodes": [{"id": "n1", "type": "text", "x": 0, "y": 0, "width": 100, "height": 100, "text": "Test"}],
            "edges": [],
        }
        canvas = canvas_from_dict(data)
        assert len(canvas.nodes) == 1
        assert canvas.nodes[0].text == "Test"

    def test_roundtrip_dict(self):
        """Test functionality: roundtrip dict."""
        original = Canvas(
            nodes=[
                CanvasNode(id="n1", type="text", x=10, y=20, width=300, height=200, text="Content"),
                CanvasNode(id="n2", type="link", url="https://example.com"),
            ],
            edges=[
                CanvasEdge(id="e1", fromNode="n1", toNode="n2", fromSide="right", toSide="left"),
            ],
        )
        d = canvas_to_dict(original)
        restored = canvas_from_dict(d)
        assert len(restored.nodes) == 2
        assert restored.nodes[0].text == "Content"
        assert restored.edges[0].fromSide == "right"


class TestAddOperations:
    """Test suite for AddOperations."""
    def test_add_node(self):
        """Test functionality: add node."""
        canvas = Canvas()
        node = CanvasNode(id="new", type="text", text="Added")
        result = add_canvas_node(canvas, node)
        assert len(result.nodes) == 1
        assert result is canvas  # Same object

    def test_add_edge(self):
        """Test functionality: add edge."""
        canvas = Canvas(
            nodes=[
                CanvasNode(id="a", type="text"),
                CanvasNode(id="b", type="text"),
            ]
        )
        edge = CanvasEdge(id="e", fromNode="a", toNode="b")
        result = add_canvas_edge(canvas, edge)
        assert len(result.edges) == 1
