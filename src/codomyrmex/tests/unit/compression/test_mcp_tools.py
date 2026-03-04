"""Unit tests for the compression module's MCP tools."""

import base64

import pytest

from codomyrmex.compression.mcp_tools import (
    compression_compress_data,
    compression_decompress_data,
    compression_get_stats,
)


@pytest.mark.unit
class TestCompressionMCPTools:
    """Zero-mock tests for the compression MCP tools."""

    def test_compress_data_plain_text(self):
        """Test compression_compress_data with plain text input."""
        data = "Hello, world! " * 50
        result = compression_compress_data(data, format="gzip")

        assert "compressed_base64" in result
        assert result["format"] == "gzip"

        # Verify we can decompress it back to original
        compressed_bytes = base64.b64decode(result["compressed_base64"])
        from codomyrmex.compression import decompress

        decompressed_bytes = decompress(compressed_bytes, format="gzip")
        assert decompressed_bytes.decode("utf-8") == data

    def test_compress_data_base64_input(self):
        """Test compression_compress_data with base64 encoded input."""
        original_data = b"Some binary data \x00\x01\x02" * 10
        b64_input = base64.b64encode(original_data).decode("utf-8")

        result = compression_compress_data(b64_input, is_base64=True, format="gzip")

        assert "compressed_base64" in result

        compressed_bytes = base64.b64decode(result["compressed_base64"])
        from codomyrmex.compression import decompress

        decompressed_bytes = decompress(compressed_bytes, format="gzip")
        assert decompressed_bytes == original_data

    def test_compress_data_error(self):
        """Test compression_compress_data error handling."""
        # Unsupported format
        result = compression_compress_data("test", format="unknown_format")
        assert "error" in result

    def test_decompress_data_to_text(self):
        """Test compression_decompress_data returning text."""
        data = "Sample text for decompression test."
        from codomyrmex.compression import compress

        compressed_bytes = compress(data.encode("utf-8"), format="zlib")
        b64_compressed = base64.b64encode(compressed_bytes).decode("utf-8")

        result = compression_decompress_data(b64_compressed, format="zlib")

        assert "decompressed_text" in result
        assert result["decompressed_text"] == data

    def test_decompress_data_to_base64(self):
        """Test compression_decompress_data returning base64."""
        data = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
        from codomyrmex.compression import compress

        compressed_bytes = compress(data, format="zip")
        b64_compressed = base64.b64encode(compressed_bytes).decode("utf-8")

        result = compression_decompress_data(
            b64_compressed, format="zip", return_base64=True
        )

        assert "decompressed_base64" in result
        decompressed_bytes = base64.b64decode(result["decompressed_base64"])
        assert decompressed_bytes == data

    def test_decompress_data_binary_fallback(self):
        """Test compression_decompress_data falls back to base64 if not valid UTF-8."""
        # Create non-utf8 data
        data = bytes(range(256))
        from codomyrmex.compression import compress

        compressed_bytes = compress(data, format="gzip")
        b64_compressed = base64.b64encode(compressed_bytes).decode("utf-8")

        # We don't ask for base64, but it should fallback because it's not valid utf-8
        result = compression_decompress_data(b64_compressed, format="gzip")

        assert "decompressed_base64" in result
        assert "warning" in result
        decompressed_bytes = base64.b64decode(result["decompressed_base64"])
        assert decompressed_bytes == data

    def test_decompress_data_error(self):
        """Test compression_decompress_data error handling."""
        # Invalid base64
        result = compression_decompress_data("invalid_base64!!", format="gzip")
        assert "error" in result

    def test_get_stats_plain_text(self):
        """Test compression_get_stats with plain text."""
        data = "Highly compressible repeated text. " * 100
        result = compression_get_stats(data)

        assert "stats" in result
        stats = result["stats"]
        assert "gzip" in stats
        assert "zlib" in stats
        assert "zip" in stats

        # Check specific stats
        assert "compressed_size" in stats["gzip"] or "error" in stats["gzip"]

    def test_get_stats_base64_input(self):
        """Test compression_get_stats with base64 encoded input."""
        original_data = b"Random binary data " * 50
        b64_input = base64.b64encode(original_data).decode("utf-8")

        result = compression_get_stats(b64_input, is_base64=True)

        assert "stats" in result
        assert "gzip" in result["stats"]

    def test_get_stats_error(self):
        """Test compression_get_stats error handling."""
        # Invalid base64 when is_base64=True
        result = compression_get_stats("not valid base64!!!", is_base64=True)
        assert "error" in result

    def test_tool_metadata(self):
        """Test that the tools have correct metadata set by decorator."""
        # Note: @mcp_tool prepends 'codomyrmex.' to the name
        assert hasattr(compression_compress_data, "_mcp_tool_meta")
        assert compression_compress_data._mcp_tool_meta["category"] == "compression"
        assert (
            compression_compress_data._mcp_tool_meta["name"]
            == "codomyrmex.compression_compress_data"
        )

        assert hasattr(compression_decompress_data, "_mcp_tool_meta")
        assert compression_decompress_data._mcp_tool_meta["category"] == "compression"

        assert hasattr(compression_get_stats, "_mcp_tool_meta")
        assert compression_get_stats._mcp_tool_meta["category"] == "compression"
