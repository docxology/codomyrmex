"""Tests for compression MCP tools."""

import base64

from codomyrmex.compression.mcp_tools import (
    compression_compare_formats,
    compression_compress,
    compression_detect_format,
)


class TestCompressionCompress:
    def test_returns_dict_with_status(self):
        result = compression_compress(data="hello world")
        assert isinstance(result, dict)
        assert "status" in result

    def test_gzip_compression_success(self):
        result = compression_compress(data="hello world", format="gzip")
        assert result["status"] == "success"
        assert result["original_size"] == len(b"hello world")
        assert result["compressed_size"] > 0
        assert "compressed_b64" in result

    def test_zlib_compression_success(self):
        result = compression_compress(data="hello world", format="zlib")
        assert result["status"] == "success"
        assert result["format"] == "zlib"

    def test_compression_ratio_is_float(self):
        result = compression_compress(data="aaaa" * 100, format="gzip")
        assert result["status"] == "success"
        assert isinstance(result["ratio"], float)
        assert result["ratio"] > 0

    def test_invalid_format_returns_error(self):
        result = compression_compress(data="hello", format="brotli")
        assert result["status"] == "error"
        assert "message" in result


class TestCompressionDetectFormat:
    def test_detects_gzip(self):
        compressed = compression_compress(data="test data", format="gzip")
        result = compression_detect_format(data_b64=compressed["compressed_b64"])
        assert result["status"] == "success"
        assert result["detected_format"] == "gzip"

    def test_detects_zlib(self):
        compressed = compression_compress(data="test data", format="zlib")
        result = compression_detect_format(data_b64=compressed["compressed_b64"])
        assert result["status"] == "success"
        assert result["detected_format"] == "zlib"

    def test_unknown_format_returns_none(self):
        raw_b64 = base64.b64encode(b"this is not compressed").decode("ascii")
        result = compression_detect_format(data_b64=raw_b64)
        assert result["status"] == "success"
        assert result["detected_format"] is None


class TestCompressionCompareFormats:
    def test_returns_dict_with_status(self):
        result = compression_compare_formats(data="hello world test data")
        assert isinstance(result, dict)
        assert result["status"] == "success"

    def test_all_formats_present(self):
        result = compression_compare_formats(data="hello world test data")
        formats = result["formats"]
        assert "gzip" in formats
        assert "zlib" in formats
        assert "zip" in formats

    def test_original_size_correct(self):
        data = "testing compression comparison"
        result = compression_compare_formats(data=data)
        assert result["original_size"] == len(data.encode("utf-8"))
