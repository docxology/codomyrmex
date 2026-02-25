"""Tests for model_context_protocol.tools and decorators.

All tests use real filesystem operations - no mocks.
"""

import pytest

from codomyrmex.model_context_protocol.decorators import mcp_tool
from codomyrmex.model_context_protocol.tools import (
    analyze_python_file,
    list_directory,
    read_file,
    write_file,
)


@pytest.mark.unit
class TestMCPReadFile:
    """Tests for the read_file MCP tool."""

    def test_read_existing_file(self, tmp_path):
        """Test functionality: read existing file."""
        f = tmp_path / "hello.txt"
        f.write_text("hello world")
        result = read_file(str(f))
        assert result["success"] is True
        assert result["content"] == "hello world"
        assert result["lines"] >= 1
        assert result["size"] > 0

    def test_read_nonexistent_file(self):
        """Test functionality: read nonexistent file."""
        result = read_file("/nonexistent/path/file.txt")
        assert result["success"] is False
        assert "error" in result

    def test_read_file_exceeding_max_size(self, tmp_path):
        """Test functionality: read file exceeding max size."""
        f = tmp_path / "big.txt"
        f.write_bytes(b"x" * 2000)
        result = read_file(str(f), max_size=1000)
        assert result["success"] is False
        assert "too large" in result["error"].lower() or "large" in result["error"].lower()

    def test_read_multiline_file_counts_lines(self, tmp_path):
        """Test functionality: read multiline file counts lines."""
        f = tmp_path / "multiline.py"
        f.write_text("line1\nline2\nline3\n")
        result = read_file(str(f))
        assert result["success"] is True
        assert result["lines"] >= 3

    def test_read_returns_path_and_encoding(self, tmp_path):
        """Test functionality: read returns path and encoding."""
        f = tmp_path / "meta.txt"
        f.write_text("data")
        result = read_file(str(f))
        assert result["success"] is True
        assert "path" in result
        assert "encoding" in result
        assert result["encoding"] == "utf-8"

    def test_read_empty_file(self, tmp_path):
        """Test functionality: read empty file."""
        f = tmp_path / "empty.txt"
        f.write_text("")
        result = read_file(str(f))
        assert result["success"] is True
        assert result["content"] == ""
        assert result["size"] == 0


@pytest.mark.unit
class TestMCPWriteFile:
    """Tests for the write_file MCP tool."""

    def test_write_creates_file(self, tmp_path):
        """Test functionality: write creates file."""
        path = str(tmp_path / "output.txt")
        result = write_file(path, "written content")
        assert result["success"] is True
        from pathlib import Path
        assert Path(path).read_text() == "written content"

    def test_write_overwrites_existing_file(self, tmp_path):
        """Test functionality: write overwrites existing file."""
        f = tmp_path / "existing.txt"
        f.write_text("old content")
        result = write_file(str(f), "new content")
        assert result["success"] is True
        assert f.read_text() == "new content"

    def test_write_returns_bytes_written(self, tmp_path):
        """Test functionality: write returns bytes written."""
        content = "hello"
        path = str(tmp_path / "byte_count.txt")
        result = write_file(path, content)
        assert result["success"] is True
        assert result.get("bytes_written", result.get("size", 0)) >= len(content)

    def test_write_creates_parent_directories(self, tmp_path):
        """Test functionality: write creates parent directories."""
        path = str(tmp_path / "sub" / "dir" / "file.txt")
        result = write_file(path, "nested", create_dirs=True)
        assert result["success"] is True


@pytest.mark.unit
class TestMCPListDirectory:
    """Tests for the list_directory MCP tool."""

    def test_list_existing_directory(self, tmp_path):
        """Test functionality: list existing directory."""
        (tmp_path / "a.txt").write_text("a")
        (tmp_path / "b.txt").write_text("b")
        result = list_directory(str(tmp_path))
        assert result["success"] is True
        names = [item["name"] for item in result["items"]]
        assert "a.txt" in names
        assert "b.txt" in names

    def test_list_nonexistent_directory(self):
        """Test functionality: list nonexistent directory."""
        result = list_directory("/nonexistent/path")
        assert result["success"] is False

    def test_list_includes_item_metadata(self, tmp_path):
        """Test functionality: list includes item metadata."""
        (tmp_path / "test.py").write_text("x = 1")
        result = list_directory(str(tmp_path))
        assert result["success"] is True
        assert len(result["items"]) >= 1
        item = result["items"][0]
        assert "name" in item

    def test_list_with_pattern_filter(self, tmp_path):
        """Test functionality: list with pattern filter."""
        (tmp_path / "code.py").write_text("")
        (tmp_path / "readme.md").write_text("")
        result = list_directory(str(tmp_path), pattern="*.py")
        assert result["success"] is True
        names = [item["name"] for item in result["items"]]
        assert "code.py" in names
        assert "readme.md" not in names


@pytest.mark.unit
class TestMCPAnalyzePythonFile:
    """Tests for the analyze_python_file MCP tool."""

    def test_analyze_valid_python_file(self, tmp_path):
        """Test functionality: analyze valid python file."""
        f = tmp_path / "sample.py"
        f.write_text("def hello():\n    return 'world'\n\nx = hello()\n")
        result = analyze_python_file(str(f))
        assert result["success"] is True
        assert "functions" in result or "analysis" in result

    def test_analyze_nonexistent_file(self):
        """Test functionality: analyze nonexistent file."""
        result = analyze_python_file("/nonexistent/file.py")
        assert result["success"] is False

    def test_analyze_file_with_classes(self, tmp_path):
        """Test functionality: analyze file with classes."""
        f = tmp_path / "classes.py"
        f.write_text("class MyClass:\n    def method(self):\n        pass\n")
        result = analyze_python_file(str(f))
        assert result["success"] is True


@pytest.mark.unit
class TestMCPToolDecorator:
    """Tests for the @mcp_tool decorator."""

    def test_decorator_attaches_mcp_metadata(self):
        """Test functionality: decorator attaches mcp metadata."""
        @mcp_tool(category="test_category", description="A test tool")
        def sample_tool(a: int, b: str) -> str:
            """Sample docstring."""
            return b * a

        assert hasattr(sample_tool, "_mcp_tool")
        meta = sample_tool._mcp_tool
        assert "codomyrmex." in meta["name"]
        assert meta["category"] == "test_category"
        assert meta["description"] == "A test tool"

    def test_decorator_preserves_function_behavior(self):
        """Test functionality: decorator preserves function behavior."""
        @mcp_tool()
        def add(a: int, b: int) -> int:
            """Add two ints."""
            return a + b

        assert add(2, 3) == 5

    def test_decorator_auto_generates_schema(self):
        """Test functionality: decorator auto generates schema."""
        @mcp_tool()
        def greet(name: str, count: int = 1) -> str:
            """Say hello."""
            return f"Hello {name}" * count

        schema = greet._mcp_tool["schema"]
        assert schema["type"] == "object"
        assert "name" in schema["properties"]
        assert "name" in schema["required"]

    def test_decorator_uses_function_name_as_default(self):
        """Test functionality: decorator uses function name as default."""
        @mcp_tool()
        def my_tool_func():
            """Does something."""
            pass

        assert "my_tool_func" in my_tool_func._mcp_tool["name"]

    def test_decorator_uses_docstring_as_default_description(self):
        """Test functionality: decorator uses docstring as default description."""
        @mcp_tool()
        def documented():
            """This is the description."""
            pass

        assert documented._mcp_tool["description"] == "This is the description."

    def test_decorator_includes_module_info(self):
        """Test functionality: decorator includes module info."""
        @mcp_tool()
        def modular():
            """Test."""
            pass

        assert "module" in modular._mcp_tool
