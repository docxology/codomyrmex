"""Integration tests for Hermes Semantic Canvas Parsing."""

import json
from pathlib import Path

from codomyrmex.agents.hermes.mcp_tools import hermes_parse_canvas


def test_hermes_parse_canvas_tool(tmp_path: Path) -> None:
    """Verify that the hermes_parse_canvas MCP tool correctly parses .canvas files."""
    vault_path = tmp_path / "canvas_vault"
    vault_path.mkdir(parents=True, exist_ok=True)

    canvas_file = vault_path / "architecture.canvas"

    # Create a real, valid Obsidian canvas JSON structure
    canvas_data = {
        "nodes": [
            {
                "id": "node1",
                "type": "text",
                "text": "Core Gateway",
                "x": 0,
                "y": 0,
                "width": 200,
                "height": 100,
            },
            {
                "id": "node2",
                "type": "file",
                "file": "Sessions/TestSession.md",
                "x": 300,
                "y": 0,
                "width": 200,
                "height": 100,
            },
        ],
        "edges": [
            {
                "id": "edge1",
                "fromNode": "node1",
                "fromSide": "right",
                "toNode": "node2",
                "toSide": "left",
                "label": "syncs to",
            }
        ],
    }

    canvas_file.write_text(json.dumps(canvas_data))

    # Execute the MCP tool
    result = hermes_parse_canvas(str(vault_path), "architecture.canvas")

    assert result["status"] == "success"

    nodes = result["nodes"]
    edges = result["edges"]

    assert len(nodes) == 2
    assert nodes[0]["id"] == "node1"
    assert nodes[0]["type"] == "text"
    assert nodes[0]["content"] == "Core Gateway"

    assert nodes[1]["id"] == "node2"
    assert nodes[1]["type"] == "file"
    assert nodes[1]["file"] == "Sessions/TestSession.md"

    assert len(edges) == 1
    assert edges[0]["fromNode"] == "node1"
    assert edges[0]["toNode"] == "node2"
    assert edges[0]["label"] == "syncs to"


def test_hermes_parse_canvas_missing_file(tmp_path: Path) -> None:
    """Verify hermes_parse_canvas handles missing files gracefully."""
    vault_path = tmp_path / "canvas_vault_missing"
    vault_path.mkdir(parents=True, exist_ok=True)

    result = hermes_parse_canvas(str(vault_path), "doesntexist.canvas")
    assert result["status"] == "error"
    assert "Canvas not found" in result["message"]
