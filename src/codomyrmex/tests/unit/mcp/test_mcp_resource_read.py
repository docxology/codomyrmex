"""Zero-Mock tests for MCPBridge._handle_resource_read.

Tests file:// URI reading and non-file resource metadata fallback.
"""

import asyncio
import json

import pytest

from codomyrmex.llm.mcp import MCPBridge, MCPResource


def _run(coro):
    """Run an async coroutine synchronously."""
    return asyncio.get_event_loop().run_until_complete(coro)


@pytest.mark.unit
class TestMCPResourceRead:
    """Test suite for MCP resource read implementation."""

    def setup_method(self):
        self.bridge = MCPBridge()

    def test_read_file_resource(self, tmp_path):
        """Read a file:// resource returns file contents."""
        test_file = tmp_path / "readme.md"
        test_file.write_text("# Hello World\n\nThis is a test.")
        uri = f"file://{test_file}"

        self.bridge.register_resource(MCPResource(
            uri=uri,
            name="readme",
            description="Test readme file",
            mime_type="text/markdown",
        ))

        result = _run(self.bridge._handle_resource_read({"uri": uri}))
        assert "contents" in result
        assert len(result["contents"]) == 1
        assert result["contents"][0]["text"] == "# Hello World\n\nThis is a test."
        assert result["contents"][0]["mimeType"] == "text/markdown"

    def test_read_nonfile_resource_returns_metadata(self):
        """Non-file resources return JSON metadata as content."""
        uri = "codomyrmex://config/settings"
        self.bridge.register_resource(MCPResource(
            uri=uri,
            name="settings",
            description="Application settings",
        ))

        result = _run(self.bridge._handle_resource_read({"uri": uri}))
        assert "contents" in result
        content = json.loads(result["contents"][0]["text"])
        assert content["uri"] == uri
        assert content["name"] == "settings"

    def test_read_unregistered_resource_raises(self):
        """Reading an unregistered resource should raise ValueError."""
        with pytest.raises(ValueError, match="Resource not found"):
            _run(self.bridge._handle_resource_read({"uri": "file:///nonexistent"}))

    def test_read_file_resource_missing_file_raises(self, tmp_path):
        """A registered file:// resource pointing to a missing file should raise FileNotFoundError."""
        uri = f"file://{tmp_path}/ghost.txt"
        self.bridge.register_resource(MCPResource(uri=uri, name="ghost"))

        with pytest.raises(FileNotFoundError):
            _run(self.bridge._handle_resource_read({"uri": uri}))
