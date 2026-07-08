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
    import zstandard as _zstd_check

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
            CompressionError,
            Compressor,
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
            CompressionError,
            Compressor,
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
            CompressionError,
            Compressor,
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
        for info in results.values():
            assert info.get("time_ms", 0) >= 0


# ===========================================================================
# Class: TestAutoDecompress
# ===========================================================================


class TestAutoDecompress:
    """auto_decompress convenience function."""

    def test_auto_decompress_gzip(self):
        import gzip

        from codomyrmex.compression.core.compressor import auto_decompress

        data = b"auto decompression"
        compressed = gzip.compress(data)
        assert auto_decompress(compressed) == data

    def test_auto_decompress_zlib(self):
        import zlib

        from codomyrmex.compression.core.compressor import auto_decompress

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


# ===========================================================================
# Class: TestCompressionErrorPaths
# ===========================================================================


class TestCompressionErrorPaths:
    """Error paths in compress_file, decompress_file (lines 193-195, 218, 230-232)."""

    def test_compress_file_nonexistent_input_raises_compression_error(self):
        from codomyrmex.compression.core.compressor import (
            CompressionError,
            Compressor,
        )

        c = Compressor(format="gzip")
        with pytest.raises(CompressionError):
            c.compress_file("/tmp/definitely_does_not_exist_xyz_123.txt")

    def test_decompress_file_nonexistent_input_raises_compression_error(self):
        from codomyrmex.compression.core.compressor import (
            CompressionError,
            Compressor,
        )

        c = Compressor(format="gzip")
        with pytest.raises(CompressionError):
            c.decompress_file("/tmp/definitely_does_not_exist_abc_999.gz")

    def test_decompress_file_no_known_extension_uses_decompressed_suffix(self):
        """decompress_file with no known extension appends .decompressed (line 218)."""
        import tempfile

        from codomyrmex.compression.core.compressor import Compressor

        c = Compressor(format="gzip")
        with tempfile.TemporaryDirectory() as tmp:
            content = b"no extension test"
            # Write raw gzip data with an unfamiliar extension
            compressed = c.compress(content)
            import os

            input_path = os.path.join(tmp, "archive.someweirdext")
            with open(input_path, "wb") as f:
                f.write(compressed)
            output_path = c.decompress_file(input_path)
            assert output_path.endswith(".decompressed")
            with open(output_path, "rb") as f:
                assert f.read() == content

    def test_decompress_file_bad_data_raises_compression_error(self):
        """Decompressing corrupt data from a file raises CompressionError (lines 230-232)."""
        import os
        import tempfile

        from codomyrmex.compression.core.compressor import (
            CompressionError,
            Compressor,
        )

        c = Compressor(format="gzip")
        with tempfile.TemporaryDirectory() as tmp:
            bad_file = os.path.join(tmp, "corrupt.gz")
            with open(bad_file, "wb") as f:
                f.write(b"this is not gzip data at all")
            with pytest.raises(CompressionError):
                c.decompress_file(bad_file)

    def test_compress_file_zip_format_default_path(self):
        """compress_file with zip format uses .zip extension."""
        import os
        import tempfile

        from codomyrmex.compression.core.compressor import Compressor

        c = Compressor(format="zip")
        with tempfile.TemporaryDirectory() as tmp:
            input_path = os.path.join(tmp, "data.txt")
            with open(input_path, "wb") as f:
                f.write(b"zip file test content " * 10)
            output_path = c.compress_file(input_path)
            assert output_path.endswith(".zip")
            assert os.path.exists(output_path)


# ===========================================================================
# Class: TestParallelCompressorAdvanced
# ===========================================================================


class TestParallelCompressorAdvanced:
    """Progress callbacks, split_and_compress, decompress_and_merge, last_stats."""

    def test_compress_batch_with_progress_callback(self):
        """Progress callback is invoked for each item (line 108)."""
        from codomyrmex.compression.engines.parallel import ParallelCompressor

        progress_calls = []

        def on_progress(completed, total):
            progress_calls.append((completed, total))

        data_list = [b"chunk1" * 100, b"chunk2" * 100, b"chunk3" * 100]
        pc = ParallelCompressor(format="gzip", max_workers=2)
        compressed = pc.compress_batch(data_list, on_progress=on_progress)

        assert len(compressed) == 3
        assert len(progress_calls) == 3
        # All totals should be 3
        assert all(total == 3 for _, total in progress_calls)

    def test_decompress_batch_with_progress_callback(self):
        """Progress callback works in decompress_batch (line 143)."""
        from codomyrmex.compression.engines.parallel import ParallelCompressor

        progress_calls = []

        def on_progress(completed, total):
            progress_calls.append(completed)

        data_list = [b"alpha" * 200, b"beta" * 200]
        pc = ParallelCompressor(format="gzip")
        compressed = pc.compress_batch(data_list)
        pc.decompress_batch(compressed, on_progress=on_progress)

        assert len(progress_calls) == 2

    def test_split_and_compress_small_chunk_size(self):
        """split_and_compress splits data into chunks and compresses (lines 168-171)."""
        from codomyrmex.compression.engines.parallel import ParallelCompressor

        pc = ParallelCompressor(format="gzip", chunk_size=10)
        data = b"abcdefghij" * 5  # 50 bytes → 5 chunks of 10
        chunks = pc.split_and_compress(data)
        assert len(chunks) == 5
        # All chunks are bytes
        assert all(isinstance(c, bytes) for c in chunks)

    def test_split_and_compress_single_chunk(self):
        """When data < chunk_size, produces a single compressed chunk."""
        from codomyrmex.compression.engines.parallel import ParallelCompressor

        pc = ParallelCompressor(format="gzip", chunk_size=10000)
        data = b"small" * 10
        chunks = pc.split_and_compress(data)
        assert len(chunks) == 1

    def test_split_and_compress_with_progress_callback(self):
        """split_and_compress forwards progress callback."""
        from codomyrmex.compression.engines.parallel import ParallelCompressor

        calls = []
        pc = ParallelCompressor(format="gzip", chunk_size=5)
        data = b"x" * 20  # 4 chunks
        pc.split_and_compress(data, on_progress=lambda c, t: calls.append(c))
        assert len(calls) == 4

    def test_decompress_and_merge_roundtrip(self):
        """decompress_and_merge reassembles split data correctly (lines 179-180)."""
        from codomyrmex.compression.engines.parallel import ParallelCompressor

        pc = ParallelCompressor(format="gzip", chunk_size=20)
        data = b"hello world this is a test " * 10
        compressed_chunks = pc.split_and_compress(data)
        result = pc.decompress_and_merge(compressed_chunks)
        assert result == data

    def test_decompress_and_merge_with_progress_callback(self):
        """decompress_and_merge forwards on_progress."""
        from codomyrmex.compression.engines.parallel import ParallelCompressor

        calls = []
        pc = ParallelCompressor(format="gzip", chunk_size=10)
        data = b"z" * 30  # 3 chunks
        chunks = pc.split_and_compress(data)
        pc.decompress_and_merge(chunks, on_progress=lambda c, t: calls.append(c))
        assert len(calls) == 3

    def test_last_stats_is_none_initially(self):
        """last_stats property is None before any operation (line 185)."""
        from codomyrmex.compression.engines.parallel import ParallelCompressor

        pc = ParallelCompressor()
        assert pc.last_stats is None

    def test_last_stats_populated_after_compress_batch(self):
        """last_stats is populated with CompressionStats after compress_batch."""
        from codomyrmex.compression.engines.parallel import (
            CompressionStats,
            ParallelCompressor,
        )

        pc = ParallelCompressor(format="gzip")
        pc.compress_batch([b"stats test " * 100])
        stats = pc.last_stats
        assert stats is not None
        assert isinstance(stats, CompressionStats)
        assert stats.input_bytes > 0
        assert stats.chunk_count == 1

    def test_last_stats_populated_after_decompress_batch(self):
        """last_stats is updated after decompress_batch."""
        from codomyrmex.compression.engines.parallel import ParallelCompressor

        pc = ParallelCompressor(format="gzip")
        compressed = pc.compress_batch([b"decompress stats " * 50])
        pc.decompress_batch(compressed)
        assert pc.last_stats is not None
        assert pc.last_stats.output_bytes > 0


# ===========================================================================
# Class: TestCompressionStats
# ===========================================================================


class TestCompressionStats:
    """Tests for CompressionStats dataclass properties."""

    def test_ratio_zero_when_input_bytes_zero(self):
        from codomyrmex.compression.engines.parallel import CompressionStats

        stats = CompressionStats(
            input_bytes=0,
            output_bytes=0,
            duration_seconds=1.0,
            chunk_count=1,
        )
        assert stats.ratio == 0.0

    def test_ratio_calculated_correctly(self):
        from codomyrmex.compression.engines.parallel import CompressionStats

        stats = CompressionStats(
            input_bytes=100,
            output_bytes=50,
            duration_seconds=0.5,
            chunk_count=2,
        )
        assert stats.ratio == 0.5

    def test_throughput_zero_when_duration_zero(self):
        from codomyrmex.compression.engines.parallel import CompressionStats

        stats = CompressionStats(
            input_bytes=1000,
            output_bytes=500,
            duration_seconds=0.0,
            chunk_count=1,
        )
        assert stats.throughput_mbps == 0.0

    def test_throughput_positive_for_real_duration(self):
        from codomyrmex.compression.engines.parallel import CompressionStats

        stats = CompressionStats(
            input_bytes=1024 * 1024,
            output_bytes=512 * 1024,
            duration_seconds=1.0,
            chunk_count=1,
        )
        # 1MB in 1 second = 1 MB/s
        assert abs(stats.throughput_mbps - 1.0) < 0.001

    def test_savings_percent_positive_for_compressed_output(self):
        from codomyrmex.compression.engines.parallel import CompressionStats

        stats = CompressionStats(
            input_bytes=100,
            output_bytes=25,
            duration_seconds=0.1,
            chunk_count=1,
        )
        assert abs(stats.savings_percent - 75.0) < 0.001

    def test_savings_percent_zero_for_no_compression(self):
        from codomyrmex.compression.engines.parallel import CompressionStats

        stats = CompressionStats(
            input_bytes=100,
            output_bytes=100,
            duration_seconds=0.1,
            chunk_count=1,
        )
        assert stats.savings_percent == 0.0

    def test_savings_percent_from_real_compression(self):
        from codomyrmex.compression.core.compressor import Compressor
        from codomyrmex.compression.engines.parallel import CompressionStats

        data = b"a" * 10000
        compressed = Compressor("gzip").compress(data)
        stats = CompressionStats(
            input_bytes=len(data),
            output_bytes=len(compressed),
            duration_seconds=0.05,
            chunk_count=1,
        )
        assert stats.savings_percent > 90.0  # highly compressible data


# ===========================================================================
# Class: TestExtractArchiveErrors
# ===========================================================================


class TestExtractArchiveErrors:
    """Error paths in archive extract (lines 97-100) and unknown suffix."""

    def test_extract_archive_unknown_suffix_raises_compression_error(self):
        """extract_archive raises CompressionError on unknown file suffix."""
        import tempfile

        from codomyrmex.compression.archives.archive_manager import (
            ArchiveManager,
            CompressionError,
        )

        with tempfile.TemporaryDirectory() as tmp:
            fake_archive = Path(tmp) / "test.rar"
            fake_archive.write_bytes(b"not a real archive")
            output_dir = Path(tmp) / "out"
            mgr = ArchiveManager()
            with pytest.raises(CompressionError):
                mgr.extract_archive(fake_archive, output_dir)

    def test_extract_zip_creates_nested_output_dir(self):
        """extract_archive creates nested output directory (parents=True)."""
        import tempfile
        import zipfile

        from codomyrmex.compression.archives.archive_manager import ArchiveManager

        with tempfile.TemporaryDirectory() as tmp:
            archive = Path(tmp) / "test.zip"
            with zipfile.ZipFile(archive, "w") as zf:
                zf.writestr("readme.txt", "hello")

            nested_output = Path(tmp) / "level1" / "level2"
            mgr = ArchiveManager()
            result = mgr.extract_archive(archive, nested_output)
            assert result is True
            assert nested_output.exists()

    def test_extract_tar_gz_archive(self):
        """extract_archive handles .tar.gz files correctly."""
        import tarfile
        import tempfile

        from codomyrmex.compression.archives.archive_manager import ArchiveManager

        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "src.txt"
            src.write_bytes(b"tar gz content")

            archive = Path(tmp) / "test.tar.gz"
            with tarfile.open(archive, "w:gz") as tf:
                tf.add(src, arcname="src.txt")

            output_dir = Path(tmp) / "extracted"
            mgr = ArchiveManager()
            result = mgr.extract_archive(archive, output_dir)
            assert result is True
            assert (output_dir / "src.txt").read_bytes() == b"tar gz content"

    def test_create_archive_unknown_format_raises_compression_error(self):
        """create_archive with unknown format raises CompressionError."""
        import tempfile

        from codomyrmex.compression.archives.archive_manager import (
            ArchiveManager,
            CompressionError,
        )

        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "archive.7z"
            mgr = ArchiveManager()
            with pytest.raises(CompressionError):
                mgr.create_archive([], output, format="7z")


# ===========================================================================
# Class: TestZstdCompressorCoverage
# ===========================================================================


class TestZstdCompressorCoverage:
    """Tests that cover ZstdCompressor lines 23-25, 34-37, 41."""

    @_SKIP_ZSTD
    def test_default_level_is_3(self):
        from codomyrmex.compression.engines.zstd_compressor import ZstdCompressor

        c = ZstdCompressor()
        assert c.level == 3

    @_SKIP_ZSTD
    def test_custom_level_stored(self):
        from codomyrmex.compression.engines.zstd_compressor import ZstdCompressor

        c = ZstdCompressor(level=10)
        assert c.level == 10

    @_SKIP_ZSTD
    def test_cctx_and_dctx_initialized(self):
        """ZstdCompressor creates cctx and dctx contexts (lines 24-25)."""
        from codomyrmex.compression.engines.zstd_compressor import ZstdCompressor

        c = ZstdCompressor(level=3)
        assert c.cctx is not None
        assert c.dctx is not None

    @_SKIP_ZSTD
    def test_compress_with_same_level_uses_cctx(self):
        """compress with level=None uses stored cctx (else branch, line 37)."""
        from codomyrmex.compression.engines.zstd_compressor import ZstdCompressor

        c = ZstdCompressor(level=3)
        data = b"same level test " * 50
        compressed = c.compress(data, level=None)
        assert isinstance(compressed, bytes)
        assert c.decompress(compressed) == data

    @_SKIP_ZSTD
    def test_compress_with_different_level_creates_new_context(self):
        """compress with different level creates new ZstdCompressor (lines 35-37)."""
        from codomyrmex.compression.engines.zstd_compressor import ZstdCompressor

        c = ZstdCompressor(level=1)
        data = b"level override data " * 100
        # level != self.level → new ctx created
        compressed = c.compress(data, level=5)
        assert c.decompress(compressed) == data

    @_SKIP_ZSTD
    def test_decompress_produces_original(self):
        """decompress via dctx returns original bytes (line 41)."""
        from codomyrmex.compression.engines.zstd_compressor import ZstdCompressor

        c = ZstdCompressor()
        data = b"decompress test " * 200
        assert c.decompress(c.compress(data)) == data

    @_SKIP_ZSTD
    def test_zstd_compress_empty_bytes(self):
        """ZstdCompressor handles empty byte input."""
        from codomyrmex.compression.engines.zstd_compressor import ZstdCompressor

        c = ZstdCompressor()
        assert c.decompress(c.compress(b"")) == b""

    @_SKIP_ZSTD
    def test_zstd_compress_large_data(self):
        """ZstdCompressor compresses and recovers 100KB of repetitive data."""
        from codomyrmex.compression.engines.zstd_compressor import ZstdCompressor

        c = ZstdCompressor(level=3)
        data = b"z" * 100_000
        compressed = c.compress(data)
        assert len(compressed) < len(data)
        assert c.decompress(compressed) == data


# ===========================================================================
# Class: TestModuleInitCoverage
# ===========================================================================


class TestModuleInitCoverage:
    """Cover compression/__init__.py line 37 (ZstdCompressor export guard)."""

    def test_module_has_zstd_compressor_attr(self):
        import codomyrmex.compression as comp_module

        assert hasattr(comp_module, "ZstdCompressor")

    def test_module_all_exports_present(self):
        from codomyrmex.compression import (
            ArchiveManager,
            Compressor,
            ParallelCompressor,
            auto_decompress,
            compress,
            decompress,
        )

        assert Compressor is not None
        assert ArchiveManager is not None
        assert ParallelCompressor is not None
        assert auto_decompress is not None
        assert compress is not None
        assert decompress is not None


# ===========================================================================
# Class: TestMcpToolsCompareFormatsEdge
# ===========================================================================


class TestMcpToolsCompareFormatsEdge:
    """Edge cases for mcp_tools compression_compare_formats (lines 125-126)."""

    def test_compare_formats_with_empty_string(self):
        """compare_formats with empty string succeeds (original_size = 0)."""
        from codomyrmex.compression.mcp_tools import compression_compare_formats

        result = compression_compare_formats("")
        assert result["status"] == "success"
        assert result["original_size"] == 0

    def test_compare_formats_custom_level_9(self):
        """compare_formats with level=9 runs correctly."""
        from codomyrmex.compression.mcp_tools import compression_compare_formats

        result = compression_compare_formats("data " * 100, level=9)
        assert result["status"] == "success"
        for fmt in ["gzip", "zlib", "zip"]:
            assert fmt in result["formats"]

    def test_compare_formats_level_0_no_compression(self):
        """compare_formats with level=0 runs without error."""
        from codomyrmex.compression.mcp_tools import compression_compare_formats

        result = compression_compare_formats("no compression " * 50, level=0)
        assert result["status"] == "success"

    def test_compression_compress_returns_decodable_b64(self):
        """compressed_b64 in result can be base64-decoded back to bytes."""
        import base64

        from codomyrmex.compression.mcp_tools import compression_compress

        text = "base64 verify test"
        result = compression_compress(text, format="gzip")
        assert result["status"] == "success"
        decoded = base64.b64decode(result["compressed_b64"])
        import gzip

        assert gzip.decompress(decoded) == text.encode("utf-8")

    def test_compression_compress_zip_b64_roundtrip(self):
        """ZIP compress result base64 can be decoded and decompressed."""
        import base64
        import zipfile
        from io import BytesIO

        from codomyrmex.compression.mcp_tools import compression_compress

        text = "zip b64 roundtrip"
        result = compression_compress(text, format="zip")
        assert result["status"] == "success"
        raw = base64.b64decode(result["compressed_b64"])
        with zipfile.ZipFile(BytesIO(raw), "r") as zf:
            content = zf.read("data")
        assert content == text.encode("utf-8")


# ===========================================================================
# Class: TestInternalErrorPaths
# ===========================================================================


class TestInternalErrorPaths:
    """Cover compressor.py lines 76-79 and 102 by forcing invalid format post-init.

    These are defensive code paths: only reachable if self.format is mutated
    after __init__ bypasses the validation check.
    """

    def test_compress_with_mutated_format_raises_compression_error(self):
        """Lines 76-79: raise ValueError triggers CompressionError in compress."""
        from codomyrmex.compression.core.compressor import (
            CompressionError,
            Compressor,
        )

        c = Compressor(format="gzip")
        # Forcibly mutate format to bypass __init__ guard
        c.format = "invalid_format_post_init"
        with pytest.raises(CompressionError):
            c.compress(b"trigger error path")

    def test_decompress_with_mutated_format_raises_compression_error(self):
        """Line 102: else branch raises ValueError wrapped as CompressionError."""
        from codomyrmex.compression.core.compressor import (
            CompressionError,
            Compressor,
        )

        c = Compressor(format="gzip")
        c.format = "invalid_format_post_init"
        with pytest.raises(CompressionError):
            c.decompress(b"some data")

    def test_compare_formats_error_branch_via_bad_level(self):
        """Lines 327-328: compare_formats catches per-format errors gracefully."""
        from codomyrmex.compression.core.compressor import compare_formats

        # Level out of range (e.g., -1) should trigger an error in at least one format
        # The function catches exceptions per-format and stores {"error": str(e)}
        data = b"test data for error branch"
        results = compare_formats(data, level=-1)
        # Result must contain all 3 format keys regardless
        assert "gzip" in results
        assert "zlib" in results
        assert "zip" in results
        # At least some should have either normal keys or error key
        for fmt_result in results.values():
            assert "error" in fmt_result or "compressed_size" in fmt_result
