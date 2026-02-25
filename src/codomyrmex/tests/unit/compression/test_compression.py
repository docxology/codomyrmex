"""Unit tests for the Codomyrmex compression module.

Comprehensive tests for Compressor, ZstdCompressor, ParallelCompressor,
ArchiveManager, compression utilities, format detection, streaming,
and file operations.
"""

import os
import unittest
from io import BytesIO

import pytest

from codomyrmex.compression import (
    ArchiveManager,
    Compressor,
    ParallelCompressor,
    ZstdCompressor,
    auto_decompress,
    compress,
    compress_data,
    compress_file,
    decompress,
    decompress_data,
    decompress_file,
    get_compressor,
)

# Import CompressionError from the actual source to match the raised exception class
from codomyrmex.compression.core.compressor import CompressionError


@pytest.mark.unit
class TestCompressionModuleImport:
    """Tests for compression module import."""

    def test_compression_module_import(self):
        """Test that compression module can be imported."""
        from codomyrmex import compression
        assert compression is not None

    def test_compression_module_exports(self):
        """Test compression module exports key components."""
        from codomyrmex import compression
        assert hasattr(compression, "Compressor")
        assert hasattr(compression, "CompressionError")
        assert hasattr(compression, "compress")
        assert hasattr(compression, "decompress")
        assert hasattr(compression, "ArchiveManager")


@pytest.mark.unit
class TestCompressor:
    """Tests for Compressor class."""

    def test_create_gzip_compressor(self):
        """Test creating a gzip compressor."""
        compressor = Compressor("gzip")
        assert compressor.format == "gzip"

    def test_create_zlib_compressor(self):
        """Test creating a zlib compressor."""
        compressor = Compressor("zlib")
        assert compressor.format == "zlib"

    def test_create_zip_compressor(self):
        """Test creating a zip compressor."""
        compressor = Compressor("zip")
        assert compressor.format == "zip"

    def test_default_format(self):
        """Test default format is gzip."""
        compressor = Compressor()
        assert compressor.format == "gzip"

    def test_unsupported_format(self):
        """Test unsupported format raises error."""
        with pytest.raises(ValueError, match="Unsupported format"):
            Compressor("unsupported")

    def test_supported_formats(self):
        """Test SUPPORTED_FORMATS constant."""
        assert "gzip" in Compressor.SUPPORTED_FORMATS
        assert "zlib" in Compressor.SUPPORTED_FORMATS
        assert "zip" in Compressor.SUPPORTED_FORMATS


@pytest.mark.unit
class TestGzipCompression(unittest.TestCase):
    """Tests for gzip compression."""

    def test_gzip_compression(self):
        """Test basic gzip compression."""
        data = b"Hello, world!" * 100
        compressor = Compressor("gzip")
        compressed = compressor.compress(data)
        decompressed = compressor.decompress(compressed)
        self.assertEqual(data, decompressed)
        self.assertTrue(len(compressed) < len(data))

    def test_gzip_compression_levels(self):
        """Test different gzip compression levels."""
        data = b"Compressible data " * 1000
        compressor = Compressor("gzip")

        level_1 = compressor.compress(data, level=1)
        level_9 = compressor.compress(data, level=9)

        # Higher level should produce smaller output (usually)
        self.assertTrue(len(level_9) <= len(level_1))

        # Both should decompress correctly
        self.assertEqual(compressor.decompress(level_1), data)
        self.assertEqual(compressor.decompress(level_9), data)

    def test_gzip_empty_data(self):
        """Test gzip compression of empty data."""
        compressor = Compressor("gzip")
        compressed = compressor.compress(b"")
        decompressed = compressor.decompress(compressed)
        self.assertEqual(decompressed, b"")

    def test_gzip_binary_data(self):
        """Test gzip compression of binary data."""
        data = bytes(range(256)) * 10
        compressor = Compressor("gzip")
        compressed = compressor.compress(data)
        decompressed = compressor.decompress(compressed)
        self.assertEqual(data, decompressed)

    def test_gzip_level_0(self):
        """Test gzip with level 0 (no compression)."""
        data = b"test data " * 100
        compressor = Compressor("gzip")
        compressed = compressor.compress(data, level=0)
        decompressed = compressor.decompress(compressed)
        self.assertEqual(data, decompressed)


@pytest.mark.unit
class TestZlibCompression:
    """Tests for zlib compression."""

    def test_zlib_compression(self):
        """Test basic zlib compression."""
        data = b"Hello, world!" * 100
        compressor = Compressor("zlib")
        compressed = compressor.compress(data)
        decompressed = compressor.decompress(compressed)

        assert data == decompressed
        assert len(compressed) < len(data)

    def test_zlib_compression_levels(self):
        """Test different zlib compression levels."""
        data = b"Compressible data " * 1000
        compressor = Compressor("zlib")

        level_1 = compressor.compress(data, level=1)
        level_9 = compressor.compress(data, level=9)

        assert compressor.decompress(level_1) == data
        assert compressor.decompress(level_9) == data

    def test_zlib_empty_data(self):
        """Test zlib compression of empty data."""
        compressor = Compressor("zlib")
        compressed = compressor.compress(b"")
        decompressed = compressor.decompress(compressed)
        assert decompressed == b""


@pytest.mark.unit
class TestZipCompression:
    """Tests for ZIP compression."""

    def test_zip_compression(self):
        """Test basic ZIP compression."""
        data = b"Hello, world!" * 100
        compressor = Compressor("zip")
        compressed = compressor.compress(data)
        decompressed = compressor.decompress(compressed)

        assert data == decompressed

    def test_zip_empty_data(self):
        """Test ZIP compression of empty data."""
        compressor = Compressor("zip")
        compressed = compressor.compress(b"")
        decompressed = compressor.decompress(compressed)
        assert decompressed == b""


@pytest.mark.unit
class TestZstdCompression(unittest.TestCase):
    """Tests for Zstandard compression."""

    def test_zstd_compression(self):
        """Test basic zstd compression."""
        try:
            data = b"Hello, world!" * 100
            compressor = ZstdCompressor()
            compressed = compressor.compress(data)
            decompressed = compressor.decompress(compressed)
            self.assertEqual(data, decompressed)
        except ImportError:
            self.skipTest("zstandard not installed")

    def test_zstd_compression_levels(self):
        """Test different zstd compression levels."""
        try:
            data = b"Compressible data " * 1000
            compressor = ZstdCompressor()
            compressed = compressor.compress(data, level=5)
            decompressed = compressor.decompress(compressed)
            self.assertEqual(data, decompressed)
        except ImportError:
            self.skipTest("zstandard not installed")


@pytest.mark.unit
class TestParallelCompressor(unittest.TestCase):
    """Tests for parallel compression."""

    def test_parallel_compression(self):
        """Test parallel compression of multiple items."""
        data_list = [b"data1" * 100, b"data2" * 100]
        compressor = ParallelCompressor("gzip")
        compressed_list = compressor.compress_batch(data_list)
        decompressed_list = compressor.decompress_batch(compressed_list)
        self.assertEqual(data_list, decompressed_list)

    def test_parallel_compression_empty_list(self):
        """Test parallel compression with empty list."""
        compressor = ParallelCompressor("gzip")
        result = compressor.compress_batch([])
        self.assertEqual(result, [])

    def test_parallel_compression_single_item(self):
        """Test parallel compression with single item."""
        data_list = [b"single item data" * 100]
        compressor = ParallelCompressor("gzip")
        compressed_list = compressor.compress_batch(data_list)
        decompressed_list = compressor.decompress_batch(compressed_list)
        self.assertEqual(data_list, decompressed_list)

    def test_parallel_compression_many_items(self):
        """Test parallel compression with many items."""
        data_list = [f"data item {i}".encode() * 100 for i in range(20)]
        compressor = ParallelCompressor("gzip")
        compressed_list = compressor.compress_batch(data_list)
        decompressed_list = compressor.decompress_batch(compressed_list)
        self.assertEqual(data_list, decompressed_list)

    def test_parallel_decompression_empty_list(self):
        """Test parallel decompression with empty list."""
        compressor = ParallelCompressor("gzip")
        result = compressor.decompress_batch([])
        self.assertEqual(result, [])


@pytest.mark.unit
class TestFormatDetection:
    """Tests for format detection."""

    def test_detect_gzip(self):
        """Test detecting gzip format."""
        compressor = Compressor("gzip")
        data = b"test data"
        compressed = compressor.compress(data)

        detected = compressor.detect_format(compressed)

        assert detected == "gzip"

    def test_detect_zlib(self):
        """Test detecting zlib format."""
        compressor = Compressor("zlib")
        data = b"test data"
        compressed = compressor.compress(data)

        detected = compressor.detect_format(compressed)

        assert detected == "zlib"

    def test_detect_zip(self):
        """Test detecting ZIP format."""
        compressor = Compressor("zip")
        data = b"test data"
        compressed = compressor.compress(data)

        detected = compressor.detect_format(compressed)

        assert detected == "zip"

    def test_detect_unknown(self):
        """Test detecting unknown format returns None."""
        compressor = Compressor("gzip")

        detected = compressor.detect_format(b"random data")

        assert detected is None

    def test_detect_short_data(self):
        """Test detecting format with very short data."""
        compressor = Compressor()
        detected = compressor.detect_format(b"a")
        assert detected is None

    def test_detect_empty_data(self):
        """Test detecting format with empty data."""
        compressor = Compressor()
        detected = compressor.detect_format(b"")
        assert detected is None


@pytest.mark.unit
class TestCompressionRatio:
    """Tests for compression ratio calculation."""

    def test_compression_ratio(self):
        """Test calculating compression ratio."""
        original = b"a" * 1000
        compressed = b"a" * 100

        ratio = Compressor.get_compression_ratio(original, compressed)

        assert ratio == 90.0  # 90% reduction

    def test_compression_ratio_empty(self):
        """Test compression ratio with empty data."""
        ratio = Compressor.get_compression_ratio(b"", b"")

        assert ratio == 0.0

    def test_compression_ratio_no_reduction(self):
        """Test compression ratio with no reduction."""
        original = b"data"
        compressed = b"data"

        ratio = Compressor.get_compression_ratio(original, compressed)

        assert ratio == 0.0

    def test_compression_ratio_negative(self):
        """Test compression ratio when compressed is larger."""
        original = b"a"
        compressed = b"aaaa"

        ratio = Compressor.get_compression_ratio(original, compressed)

        assert ratio < 0  # Negative ratio (expansion)

    def test_compression_ratio_actual_data(self):
        """Test compression ratio with actual compression."""
        data = b"compressible data " * 1000
        compressor = Compressor("gzip")
        compressed = compressor.compress(data)

        ratio = Compressor.get_compression_ratio(data, compressed)

        assert ratio > 0  # Should have positive compression


@pytest.mark.unit
class TestFileCompression:
    """Tests for file compression."""

    def test_compress_file(self, tmp_path):
        """Test compressing a file."""
        # Create input file
        input_file = tmp_path / "input.txt"
        input_file.write_bytes(b"test content " * 100)

        compressor = Compressor("gzip")
        output_path = compressor.compress_file(str(input_file))

        assert os.path.exists(output_path)
        assert output_path.endswith(".gz")

    def test_decompress_file(self, tmp_path):
        """Test decompressing a file."""
        # Create and compress file
        input_file = tmp_path / "input.txt"
        original_data = b"test content " * 100
        input_file.write_bytes(original_data)

        compressor = Compressor("gzip")
        compressed_path = compressor.compress_file(str(input_file))

        # Decompress
        decompressed_path = compressor.decompress_file(compressed_path)

        with open(decompressed_path, "rb") as f:
            decompressed_data = f.read()

        assert decompressed_data == original_data

    def test_compress_file_custom_output(self, tmp_path):
        """Test compressing a file with custom output path."""
        input_file = tmp_path / "input.txt"
        input_file.write_bytes(b"test content")

        output_file = tmp_path / "custom_output.gz"

        compressor = Compressor("gzip")
        result = compressor.compress_file(str(input_file), str(output_file))

        assert result == str(output_file)
        assert os.path.exists(output_file)

    def test_compress_file_zlib(self, tmp_path):
        """Test compressing a file with zlib."""
        input_file = tmp_path / "input.txt"
        input_file.write_bytes(b"test content " * 100)

        compressor = Compressor("zlib")
        output_path = compressor.compress_file(str(input_file))

        assert os.path.exists(output_path)
        assert output_path.endswith(".zlib")

    def test_decompress_file_removes_extension(self, tmp_path):
        """Test decompressing file removes .gz extension."""
        input_file = tmp_path / "input.txt"
        input_file.write_bytes(b"test content")

        compressor = Compressor("gzip")
        compressed_path = compressor.compress_file(str(input_file))

        decompressed_path = compressor.decompress_file(compressed_path)

        assert not decompressed_path.endswith(".gz")


@pytest.mark.unit
class TestStreamCompression:
    """Tests for stream compression."""

    def test_compress_stream(self, tmp_path):
        """Test stream compression."""
        compressor = Compressor("gzip")
        input_stream = BytesIO(b"stream data " * 100)
        output_stream = BytesIO()

        compressor.compress_stream(input_stream, output_stream)

        # Output should have data
        assert output_stream.tell() > 0

    def test_decompress_stream(self, tmp_path):
        """Test stream decompression."""
        original_data = b"stream data " * 100
        compressor = Compressor("gzip")

        # Compress first
        compressed = compressor.compress(original_data)

        # Decompress using stream
        input_stream = BytesIO(compressed)
        output_stream = BytesIO()
        compressor.decompress_stream(input_stream, output_stream)

        output_stream.seek(0)
        decompressed = output_stream.read()

        assert decompressed == original_data

    def test_stream_roundtrip(self):
        """Test stream compression roundtrip."""
        original_data = b"roundtrip stream data " * 100
        compressor = Compressor("gzip")

        # Compress
        input_stream = BytesIO(original_data)
        compressed_stream = BytesIO()
        compressor.compress_stream(input_stream, compressed_stream)

        # Decompress
        compressed_stream.seek(0)
        output_stream = BytesIO()
        compressor.decompress_stream(compressed_stream, output_stream)

        output_stream.seek(0)
        assert output_stream.read() == original_data


@pytest.mark.unit
class TestConvenienceFunctions:
    """Tests for module-level convenience functions."""

    def test_compress_function(self):
        """Test compress convenience function."""
        data = b"test data " * 100
        compressed = compress(data)

        assert len(compressed) < len(data)

    def test_decompress_function(self):
        """Test decompress convenience function."""
        data = b"test data " * 100
        compressed = compress(data, format="gzip")
        decompressed = decompress(compressed, format="gzip")

        assert decompressed == data

    def test_compress_with_format(self):
        """Test compress with format parameter."""
        data = b"test data " * 100
        compressed = compress(data, format="zlib")

        assert len(compressed) > 0

    def test_compress_with_level(self):
        """Test compress with level parameter."""
        data = b"test data " * 100
        compressed = compress(data, level=9)

        assert len(compressed) > 0

    def test_get_compressor_function(self):
        """Test get_compressor convenience function."""
        compressor = get_compressor("zlib")

        assert isinstance(compressor, Compressor)
        assert compressor.format == "zlib"

    def test_get_compressor_default(self):
        """Test get_compressor with default format."""
        compressor = get_compressor()

        assert isinstance(compressor, Compressor)
        assert compressor.format == "gzip"

    def test_compress_data_function(self):
        """Test compress_data convenience function."""
        data = b"test data"
        compressed = compress_data(data, format="gzip")

        assert len(compressed) > 0

    def test_decompress_data_function(self):
        """Test decompress_data convenience function."""
        data = b"test data " * 100
        compressed = compress_data(data)
        decompressed = decompress_data(compressed)

        assert decompressed == data

    def test_compress_file_function(self, tmp_path):
        """Test compress_file convenience function."""
        input_file = tmp_path / "input.txt"
        input_file.write_bytes(b"test content " * 100)

        output_path = compress_file(str(input_file))

        assert os.path.exists(output_path)

    def test_decompress_file_function(self, tmp_path):
        """Test decompress_file convenience function."""
        input_file = tmp_path / "input.txt"
        input_file.write_bytes(b"test content " * 100)

        compressed_path = compress_file(str(input_file))
        decompressed_path = decompress_file(compressed_path)

        assert os.path.exists(decompressed_path)

    def test_auto_decompress_gzip(self):
        """Test auto_decompress with gzip data."""
        data = b"test data " * 100
        compressed = compress_data(data, format="gzip")
        decompressed = auto_decompress(compressed)

        assert decompressed == data

    def test_auto_decompress_zlib(self):
        """Test auto_decompress with zlib data."""
        data = b"test data " * 100
        compressed = compress_data(data, format="zlib")
        decompressed = auto_decompress(compressed)

        assert decompressed == data

    def test_auto_decompress_unknown_format(self):
        """Test auto_decompress with unknown format raises error."""
        with pytest.raises(CompressionError):
            auto_decompress(b"random data")


@pytest.mark.unit
class TestArchiveManager:
    """Tests for ArchiveManager class."""

    def test_archive_manager_create(self):
        """Test creating an archive manager."""
        manager = ArchiveManager()
        assert manager is not None

    def test_create_zip_archive(self, tmp_path):
        """Test creating a ZIP archive."""
        # Create source files
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        file1.write_text("content 1")
        file2.write_text("content 2")

        output_archive = tmp_path / "archive.zip"
        manager = ArchiveManager()
        result = manager.create_archive([file1, file2], output_archive, format="zip")

        assert result is True
        assert output_archive.exists()

    def test_extract_zip_archive(self, tmp_path):
        """Test extracting a ZIP archive."""
        # Create source file and archive
        file1 = tmp_path / "file1.txt"
        file1.write_text("content 1")

        archive_path = tmp_path / "archive.zip"
        extract_path = tmp_path / "extracted"

        manager = ArchiveManager()
        manager.create_archive([file1], archive_path, format="zip")
        result = manager.extract_archive(archive_path, extract_path)

        assert result is True
        assert extract_path.exists()
        assert (extract_path / "file1.txt").exists()

    def test_create_tar_archive(self, tmp_path):
        """Test creating a TAR archive."""
        file1 = tmp_path / "file1.txt"
        file1.write_text("content 1")

        output_archive = tmp_path / "archive.tar"
        manager = ArchiveManager()
        result = manager.create_archive([file1], output_archive, format="tar")

        assert result is True
        assert output_archive.exists()

    def test_create_tar_gz_archive(self, tmp_path):
        """Test creating a TAR.GZ archive."""
        file1 = tmp_path / "file1.txt"
        file1.write_text("content 1")

        output_archive = tmp_path / "archive.tar.gz"
        manager = ArchiveManager()
        result = manager.create_archive([file1], output_archive, format="tar.gz")

        assert result is True
        assert output_archive.exists()

    def test_archive_multiple_files(self, tmp_path):
        """Test archiving multiple files."""
        files = []
        for i in range(5):
            f = tmp_path / f"file{i}.txt"
            f.write_text(f"content {i}")
            files.append(f)

        output_archive = tmp_path / "archive.zip"
        manager = ArchiveManager()
        result = manager.create_archive(files, output_archive, format="zip")

        assert result is True

    def test_archive_missing_files(self, tmp_path):
        """Test archiving with missing files."""
        existing_file = tmp_path / "existing.txt"
        existing_file.write_text("content")

        missing_file = tmp_path / "missing.txt"

        output_archive = tmp_path / "archive.zip"
        manager = ArchiveManager()
        result = manager.create_archive([existing_file, missing_file], output_archive, format="zip")

        assert result is True  # Should succeed, ignoring missing files

    def test_extract_creates_output_dir(self, tmp_path):
        """Test extract creates output directory if missing."""
        file1 = tmp_path / "file1.txt"
        file1.write_text("content")

        archive_path = tmp_path / "archive.zip"
        extract_path = tmp_path / "nested" / "output"

        manager = ArchiveManager()
        manager.create_archive([file1], archive_path, format="zip")
        result = manager.extract_archive(archive_path, extract_path)

        assert result is True
        assert extract_path.exists()


@pytest.mark.unit
class TestCompressionError:
    """Tests for CompressionError handling."""

    def test_decompression_error(self):
        """Test decompression of invalid data raises error."""
        compressor = Compressor("gzip")

        with pytest.raises(CompressionError):
            compressor.decompress(b"invalid compressed data")

    def test_compression_error_is_exception(self):
        """Test CompressionError is an exception."""
        error = CompressionError("Test error")
        assert isinstance(error, Exception)

    def test_compression_error_message(self):
        """Test CompressionError message."""
        error = CompressionError("Custom message")
        assert "Custom message" in str(error)


@pytest.mark.unit
class TestCompareFormats:
    """Tests for format comparison function."""

    def test_compare_formats(self):
        """Test compare_formats function."""
        from codomyrmex.compression.core.compressor import compare_formats

        data = b"test data " * 1000
        results = compare_formats(data)

        assert "gzip" in results
        assert "zlib" in results
        assert "zip" in results

    def test_compare_formats_contains_metrics(self):
        """Test compare_formats contains expected metrics."""
        from codomyrmex.compression.core.compressor import compare_formats

        data = b"test data " * 1000
        results = compare_formats(data)

        for fmt in ["gzip", "zlib", "zip"]:
            assert "compressed_size" in results[fmt] or "error" in results[fmt]

    def test_compare_formats_with_level(self):
        """Test compare_formats with custom level."""
        from codomyrmex.compression.core.compressor import compare_formats

        data = b"test data " * 1000
        results = compare_formats(data, level=9)

        assert "gzip" in results


@pytest.mark.unit
class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_compress_large_data(self):
        """Test compressing large data."""
        data = b"x" * (1024 * 1024)  # 1MB
        compressor = Compressor("gzip")
        compressed = compressor.compress(data)
        decompressed = compressor.decompress(compressed)

        assert decompressed == data

    def test_compress_incompressible_data(self):
        """Test compressing incompressible data (random bytes)."""
        import os
        data = os.urandom(1000)
        compressor = Compressor("gzip")
        compressed = compressor.compress(data)
        decompressed = compressor.decompress(compressed)

        assert decompressed == data

    def test_multiple_compressions(self):
        """Test multiple compression operations."""
        compressor = Compressor("gzip")
        data = b"test data"

        for _ in range(100):
            compressed = compressor.compress(data)
            decompressed = compressor.decompress(compressed)
            assert decompressed == data

    def test_very_small_data(self):
        """Test compressing very small data."""
        compressor = Compressor("gzip")
        data = b"x"
        compressed = compressor.compress(data)
        decompressed = compressor.decompress(compressed)

        assert decompressed == data

    def test_unicode_like_bytes(self):
        """Test compressing unicode-like byte sequences."""
        data = b"Hello World!"
        compressor = Compressor("gzip")
        compressed = compressor.compress(data)
        decompressed = compressor.decompress(compressed)

        assert decompressed == data
        assert decompressed.decode("utf-8") == "Hello World!"
