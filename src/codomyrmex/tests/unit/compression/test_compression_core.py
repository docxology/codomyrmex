"""Zero-mock tests for compression: compressor.py, archive_manager.py,
zstd_compressor.py, engines/parallel.py, and mcp_tools.py.

Targets uncovered lines:
- compressor.py: error paths, zip decompress "data" member, compare_formats,
  compress_file / decompress_file
- archive_manager.py: create_archive (zip/tar/tar.gz), extract_archive
- zstd_compressor.py: ImportError guard, ZstdCompressor if available
- mcp_tools.py: error branches in compression_detect_format/compare

No mocks, no monkeypatch, no unittest.mock.

External dependencies:
- zstandard — skipif guard if unavailable
"""

import os
import tempfile
from io import BytesIO
from pathlib import Path

import pytest

try:
    import zstandard as _zstd_check  # noqa: F401

    _ZSTD_AVAILABLE = True
except ImportError:
    _ZSTD_AVAILABLE = False

_SKIP_ZSTD = pytest.mark.skipif(
    not _ZSTD_AVAILABLE, reason="zstandard package not installed"
)


# ===========================================================================
# Class: TestCompressorInit
# ===========================================================================


class TestCompressorInit:
    """Initialization and format validation."""

    def test_default_format_is_gzip(self):
        from codomyrmex.compression.core.compressor import Compressor

        c = Compressor()
        assert c.format == "gzip"

    def test_explicit_gzip_format(self):
        from codomyrmex.compression.core.compressor import Compressor

        c = Compressor(format="gzip")
        assert c.format == "gzip"

    def test_explicit_zlib_format(self):
        from codomyrmex.compression.core.compressor import Compressor

        c = Compressor(format="zlib")
        assert c.format == "zlib"

    def test_explicit_zip_format(self):
        from codomyrmex.compression.core.compressor import Compressor

        c = Compressor(format="zip")
        assert c.format == "zip"

    def test_unsupported_format_raises_value_error(self):
        from codomyrmex.compression.core.compressor import Compressor

        with pytest.raises(ValueError, match="Unsupported format"):
            Compressor(format="bz2_unknown")

    def test_supported_formats_set(self):
        from codomyrmex.compression.core.compressor import Compressor

        assert "gzip" in Compressor.SUPPORTED_FORMATS
        assert "zlib" in Compressor.SUPPORTED_FORMATS
        assert "zip" in Compressor.SUPPORTED_FORMATS


# ===========================================================================
# Class: TestCompressorGzip
# ===========================================================================


class TestCompressorGzip:
    """gzip compress / decompress round-trips."""

    def _c(self):
        from codomyrmex.compression.core.compressor import Compressor

        return Compressor(format="gzip")

    def test_roundtrip_small_data(self):
        c = self._c()
        original = b"hello world"
        assert c.decompress(c.compress(original)) == original

    def test_roundtrip_empty_bytes(self):
        c = self._c()
        assert c.decompress(c.compress(b"")) == b""

    def test_compress_returns_bytes(self):
        c = self._c()
        result = c.compress(b"data")
        assert isinstance(result, bytes)

    def test_compress_reduces_repetitive_data(self):
        c = self._c()
        data = b"a" * 10000
        compressed = c.compress(data)
        assert len(compressed) < len(data)

    def test_level_0_no_compression(self):
        c = self._c()
        data = b"abcdef" * 100
        c0 = c.compress(data, level=0)
        c9 = c.compress(data, level=9)
        # Level 0 = no compression; output will be larger or equal
        assert len(c0) >= len(c9)

    def test_decompress_invalid_data_raises_compression_error(self):
        from codomyrmex.compression.core.compressor import (
            Compressor,
            CompressionError,
        )

        c = Compressor(format="gzip")
        with pytest.raises(CompressionError):
            c.decompress(b"not_gzip_data")


# ===========================================================================
# Class: TestCompressorZlib
# ===========================================================================


class TestCompressorZlib:
    """zlib compress / decompress round-trips."""

    def _c(self):
        from codomyrmex.compression.core.compressor import Compressor

        return Compressor(format="zlib")

    def test_roundtrip(self):
        c = self._c()
        data = b"zlib compression test data"
        assert c.decompress(c.compress(data)) == data

    def test_compress_returns_bytes(self):
        c = self._c()
        assert isinstance(c.compress(b"test"), bytes)

    def test_decompress_invalid_data_raises_compression_error(self):
        from codomyrmex.compression.core.compressor import (
            Compressor,
            CompressionError,
        )

        c = Compressor(format="zlib")
        with pytest.raises(CompressionError):
            c.decompress(b"\x00\x01\x02\x03_invalid")


# ===========================================================================
# Class: TestCompressorZip
# ===========================================================================


class TestCompressorZip:
    """zip compress / decompress round-trips — exercises the 'data' member path."""

    def _c(self):
        from codomyrmex.compression.core.compressor import Compressor

        return Compressor(format="zip")

    def test_roundtrip(self):
        c = self._c()
        original = b"zip archive content"
        assert c.decompress(c.compress(original)) == original

    def test_compress_returns_bytes_with_pk_magic(self):
        c = self._c()
        compressed = c.compress(b"zip data")
        assert compressed[:2] == b"PK"

    def test_decompress_invalid_raises_compression_error(self):
        from codomyrmex.compression.core.compressor import (
            Compressor,
            CompressionError,
        )

        c = Compressor(format="zip")
        with pytest.raises(CompressionError):
            c.decompress(b"not a zip file")


# ===========================================================================
# Class: TestCompressorStream
# ===========================================================================


class TestCompressorStream:
    """compress_stream and decompress_stream."""

    def test_gzip_compress_stream(self):
        from codomyrmex.compression.core.compressor import Compressor

        c = Compressor(format="gzip")
        data = b"streaming data"
        inp = BytesIO(data)
        out = BytesIO()
        c.compress_stream(inp, out)
        out.seek(0)
        assert c.decompress(out.read()) == data

    def test_gzip_decompress_stream(self):
        from codomyrmex.compression.core.compressor import Compressor

        c = Compressor(format="gzip")
        data = b"stream decompression test"
        compressed = c.compress(data)
        inp = BytesIO(compressed)
        out = BytesIO()
        c.decompress_stream(inp, out)
        out.seek(0)
        assert out.read() == data


# ===========================================================================
# Class: TestDetectFormat
# ===========================================================================


class TestDetectFormat:
    """detect_format magic-byte detection."""

    def _c(self):
        from codomyrmex.compression.core.compressor import Compressor

        return Compressor()

    def test_detects_gzip(self):
        c = self._c()
        import gzip

        compressed = gzip.compress(b"test")
        assert c.detect_format(compressed) == "gzip"

    def test_detects_zip(self):
        c = self._c()
        from codomyrmex.compression.core.compressor import Compressor

        compressed = Compressor("zip").compress(b"zip data")
        assert c.detect_format(compressed) == "zip"

    def test_detects_zlib(self):
        c = self._c()
        import zlib

        compressed = zlib.compress(b"zlib data")
        assert c.detect_format(compressed) == "zlib"

    def test_returns_none_for_unknown(self):
        c = self._c()
        assert c.detect_format(b"random_data_no_magic") is None

    def test_returns_none_for_empty(self):
        c = self._c()
        assert c.detect_format(b"") is None


# ===========================================================================
# Class: TestCompressionRatio
# ===========================================================================


class TestCompressionRatio:
    """get_compression_ratio static method."""

    def test_ratio_for_empty_original_is_zero(self):
        from codomyrmex.compression.core.compressor import Compressor

        ratio = Compressor.get_compression_ratio(b"", b"")
        assert ratio == 0.0

    def test_ratio_positive_for_compressible_data(self):
        from codomyrmex.compression.core.compressor import Compressor

        data = b"aaaa" * 1000
        compressed = Compressor("gzip").compress(data)
        ratio = Compressor.get_compression_ratio(data, compressed)
        assert ratio > 0

    def test_ratio_range_is_percentage(self):
        from codomyrmex.compression.core.compressor import Compressor

        data = b"test_data" * 100
        compressed = Compressor("gzip").compress(data)
        ratio = Compressor.get_compression_ratio(data, compressed)
        assert 0 <= ratio <= 100


# ===========================================================================
# Class: TestCompressorFileOps
# ===========================================================================


class TestCompressorFileOps:
    """compress_file and decompress_file — previously uncovered lines."""

    def test_compress_file_gzip(self):
        from codomyrmex.compression.core.compressor import Compressor

        with tempfile.TemporaryDirectory() as tmp:
            input_path = os.path.join(tmp, "input.txt")
            with open(input_path, "wb") as f:
                f.write(b"file compression content")

            c = Compressor(format="gzip")
            output_path = c.compress_file(input_path)
            assert os.path.exists(output_path)
            assert output_path.endswith(".gz")

    def test_compress_file_default_output_path(self):
        from codomyrmex.compression.core.compressor import Compressor

        with tempfile.TemporaryDirectory() as tmp:
            input_path = os.path.join(tmp, "data.bin")
            with open(input_path, "wb") as f:
                f.write(b"binary data" * 100)

            c = Compressor(format="zlib")
            output_path = c.compress_file(input_path)
            assert output_path.endswith(".zlib")

    def test_compress_then_decompress_file(self):
        from codomyrmex.compression.core.compressor import Compressor

        with tempfile.TemporaryDirectory() as tmp:
            content = b"round-trip file test content"
            input_path = os.path.join(tmp, "original.txt")
            with open(input_path, "wb") as f:
                f.write(content)

            c = Compressor(format="gzip")
            compressed_path = c.compress_file(input_path)
            decompressed_path = c.decompress_file(compressed_path)

            with open(decompressed_path, "rb") as f:
                result = f.read()
            assert result == content

    def test_decompress_file_custom_output_path(self):
        from codomyrmex.compression.core.compressor import Compressor

        with tempfile.TemporaryDirectory() as tmp:
            content = b"custom output path test"
            input_path = os.path.join(tmp, "input.txt")
            with open(input_path, "wb") as f:
                f.write(content)

            c = Compressor(format="gzip")
            compressed = c.compress_file(input_path)
            out = os.path.join(tmp, "decompressed.txt")
            c.decompress_file(compressed, output_path=out)
            with open(out, "rb") as f:
                assert f.read() == content


# ===========================================================================
# Class: TestCompareFormats
# ===========================================================================


class TestCompareFormats:
    """compare_formats function covers all three formats in one call."""

    def test_compare_formats_returns_all_three(self):
        from codomyrmex.compression.core.compressor import compare_formats

        data = b"compare me " * 200
        results = compare_formats(data)
        assert "gzip" in results
        assert "zlib" in results
        assert "zip" in results

    def test_compare_formats_has_ratio_key(self):
        from codomyrmex.compression.core.compressor import compare_formats

        data = b"ratio check " * 100
        results = compare_formats(data)
        for fmt, info in results.items():
            assert "ratio" in info, f"Missing ratio for {fmt}"

    def test_compare_formats_time_ms_is_positive(self):
        from codomyrmex.compression.core.compressor import compare_formats

        data = b"timing test " * 50
        results = compare_formats(data)
        for fmt, info in results.items():
            assert info.get("time_ms", 0) >= 0


# ===========================================================================
# Class: TestAutoDecompress
# ===========================================================================


class TestAutoDecompress:
    """auto_decompress convenience function."""

    def test_auto_decompress_gzip(self):
        from codomyrmex.compression.core.compressor import auto_decompress

        import gzip

        data = b"auto decompression"
        compressed = gzip.compress(data)
        assert auto_decompress(compressed) == data

    def test_auto_decompress_zlib(self):
        from codomyrmex.compression.core.compressor import auto_decompress

        import zlib

        data = b"zlib auto"
        compressed = zlib.compress(data)
        assert auto_decompress(compressed) == data

    def test_auto_decompress_unknown_raises_compression_error(self):
        from codomyrmex.compression.core.compressor import (
            CompressionError,
            auto_decompress,
        )

        with pytest.raises(CompressionError):
            auto_decompress(b"not any known format")


# ===========================================================================
# Class: TestConvenienceFunctions
# ===========================================================================


class TestConvenienceFunctions:
    """compress_data and decompress_data module-level helpers."""

    def test_compress_decompress_gzip(self):
        from codomyrmex.compression.core.compressor import (
            compress_data,
            decompress_data,
        )

        data = b"convenience functions test"
        assert decompress_data(compress_data(data, "gzip"), "gzip") == data

    def test_compress_decompress_zlib(self):
        from codomyrmex.compression.core.compressor import (
            compress_data,
            decompress_data,
        )

        data = b"zlib convenience"
        assert decompress_data(compress_data(data, "zlib"), "zlib") == data

    def test_compress_decompress_zip(self):
        from codomyrmex.compression.core.compressor import (
            compress_data,
            decompress_data,
        )

        data = b"zip convenience"
        assert decompress_data(compress_data(data, "zip"), "zip") == data


# ===========================================================================
# Class: TestArchiveManager
# ===========================================================================


class TestArchiveManager:
    """Tests for ArchiveManager.create_archive and extract_archive."""

    def test_create_zip_archive(self):
        from codomyrmex.compression.archives.archive_manager import ArchiveManager

        with tempfile.TemporaryDirectory() as tmp:
            # Create test files
            f1 = Path(tmp) / "file1.txt"
            f2 = Path(tmp) / "file2.txt"
            f1.write_bytes(b"content one")
            f2.write_bytes(b"content two")

            output = Path(tmp) / "archive.zip"
            mgr = ArchiveManager()
            result = mgr.create_archive([f1, f2], output, format="zip")
            assert result is True
            assert output.exists()

    def test_create_tar_archive(self):
        from codomyrmex.compression.archives.archive_manager import ArchiveManager

        with tempfile.TemporaryDirectory() as tmp:
            f1 = Path(tmp) / "data.txt"
            f1.write_bytes(b"tar content")

            output = Path(tmp) / "archive.tar"
            mgr = ArchiveManager()
            result = mgr.create_archive([f1], output, format="tar")
            assert result is True
            assert output.exists()

    def test_create_tar_gz_archive(self):
        from codomyrmex.compression.archives.archive_manager import ArchiveManager

        with tempfile.TemporaryDirectory() as tmp:
            f1 = Path(tmp) / "compressed.txt"
            f1.write_bytes(b"tar.gz content")

            output = Path(tmp) / "archive.tar.gz"
            mgr = ArchiveManager()
            result = mgr.create_archive([f1], output, format="tar.gz")
            assert result is True
            assert output.exists()

    def test_create_archive_unknown_format_raises(self):
        from codomyrmex.compression.archives.archive_manager import (
            ArchiveManager,
            CompressionError,
        )

        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "archive.rar"
            mgr = ArchiveManager()
            with pytest.raises(CompressionError):
                mgr.create_archive([], output, format="rar")

    def test_extract_zip_archive(self):
        import zipfile

        from codomyrmex.compression.archives.archive_manager import ArchiveManager

        with tempfile.TemporaryDirectory() as tmp:
            archive_path = Path(tmp) / "test.zip"
            with zipfile.ZipFile(archive_path, "w") as zf:
                zf.writestr("hello.txt", "hello content")

            output_dir = Path(tmp) / "extracted"
            mgr = ArchiveManager()
            result = mgr.extract_archive(archive_path, output_dir)
            assert result is True
            assert (output_dir / "hello.txt").exists()

    def test_extract_tar_archive(self):
        import tarfile

        from codomyrmex.compression.archives.archive_manager import ArchiveManager

        with tempfile.TemporaryDirectory() as tmp:
            archive_path = Path(tmp) / "test.tar"
            source_file = Path(tmp) / "source.txt"
            source_file.write_bytes(b"tar extract test")

            with tarfile.open(archive_path, "w") as tf:
                tf.add(source_file, arcname="source.txt")

            output_dir = Path(tmp) / "out"
            mgr = ArchiveManager()
            result = mgr.extract_archive(archive_path, output_dir)
            assert result is True

    def test_create_archive_skips_nonexistent_files(self):
        """Files that don't exist are silently skipped during archive creation."""
        import zipfile

        from codomyrmex.compression.archives.archive_manager import ArchiveManager

        with tempfile.TemporaryDirectory() as tmp:
            f_exists = Path(tmp) / "real.txt"
            f_exists.write_bytes(b"real")
            f_ghost = Path(tmp) / "ghost.txt"  # does not exist

            output = Path(tmp) / "partial.zip"
            mgr = ArchiveManager()
            result = mgr.create_archive([f_exists, f_ghost], output, format="zip")
            assert result is True
            with zipfile.ZipFile(output, "r") as zf:
                names = zf.namelist()
            assert "real.txt" in names
            assert "ghost.txt" not in names


# ===========================================================================
# Class: TestZstdCompressor
# ===========================================================================


class TestZstdCompressor:
    """Tests for the ZstdCompressor — skip if zstandard not installed."""

    @_SKIP_ZSTD
    def test_zstd_roundtrip(self):
        from codomyrmex.compression.engines.zstd_compressor import ZstdCompressor

        c = ZstdCompressor(level=3)
        data = b"zstd compression test data"
        assert c.decompress(c.compress(data)) == data

    @_SKIP_ZSTD
    def test_zstd_compress_returns_bytes(self):
        from codomyrmex.compression.engines.zstd_compressor import ZstdCompressor

        c = ZstdCompressor()
        result = c.compress(b"test data")
        assert isinstance(result, bytes)

    @_SKIP_ZSTD
    def test_zstd_level_override(self):
        from codomyrmex.compression.engines.zstd_compressor import ZstdCompressor

        c = ZstdCompressor(level=1)
        data = b"level override test " * 100
        # Different level → different context created; should still roundtrip
        compressed = c.compress(data, level=5)
        assert c.decompress(compressed) == data

    def test_zstd_unavailable_raises_import_error(self):
        """When zstandard is not installed, ZstdCompressor.__init__ raises ImportError."""
        if _ZSTD_AVAILABLE:
            pytest.skip("zstandard is installed — cannot test ImportError path")

        from codomyrmex.compression.engines.zstd_compressor import ZstdCompressor

        with pytest.raises(ImportError):
            ZstdCompressor()


# ===========================================================================
# Class: TestCompressionMcpTools
# ===========================================================================


class TestCompressionMcpTools:
    """Tests for compression MCP tools."""

    def test_compression_compress_gzip_success(self):
        from codomyrmex.compression.mcp_tools import compression_compress

        result = compression_compress("hello world", format="gzip")
        assert result["status"] == "success"
        assert result["original_size"] > 0
        assert "compressed_b64" in result

    def test_compression_compress_zlib_success(self):
        from codomyrmex.compression.mcp_tools import compression_compress

        result = compression_compress("test data zlib", format="zlib")
        assert result["status"] == "success"

    def test_compression_compress_zip_success(self):
        from codomyrmex.compression.mcp_tools import compression_compress

        result = compression_compress("zip compress test", format="zip")
        assert result["status"] == "success"
        assert result["format"] == "zip"

    def test_compression_compress_ratio_in_result(self):
        from codomyrmex.compression.mcp_tools import compression_compress

        result = compression_compress("a" * 1000, format="gzip")
        assert "ratio" in result
        assert isinstance(result["ratio"], float)

    def test_compression_compress_invalid_format_returns_error(self):
        from codomyrmex.compression.mcp_tools import compression_compress

        result = compression_compress("data", format="bz2_bad")
        assert result["status"] == "error"

    def test_compression_detect_format_gzip(self):
        import base64
        import gzip

        from codomyrmex.compression.mcp_tools import compression_detect_format

        compressed = gzip.compress(b"detect me")
        b64 = base64.b64encode(compressed).decode("ascii")
        result = compression_detect_format(b64)
        assert result["status"] == "success"
        assert result["detected_format"] == "gzip"

    def test_compression_detect_format_unknown(self):
        import base64

        from codomyrmex.compression.mcp_tools import compression_detect_format

        b64 = base64.b64encode(b"random data no magic").decode("ascii")
        result = compression_detect_format(b64)
        assert result["status"] == "success"
        assert result["detected_format"] is None

    def test_compression_detect_format_invalid_b64_returns_error(self):
        from codomyrmex.compression.mcp_tools import compression_detect_format

        result = compression_detect_format("!not valid base64!!!")
        assert result["status"] == "error"

    def test_compression_compare_formats_success(self):
        from codomyrmex.compression.mcp_tools import compression_compare_formats

        result = compression_compare_formats("compare me " * 100)
        assert result["status"] == "success"
        assert "formats" in result
        assert "gzip" in result["formats"]

    def test_compression_compare_formats_original_size_accurate(self):
        from codomyrmex.compression.mcp_tools import compression_compare_formats

        text = "size check test"
        result = compression_compare_formats(text)
        assert result["original_size"] == len(text.encode("utf-8"))
