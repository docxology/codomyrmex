"""Unit tests for the Codomyrmex compression module.

Tests for Compressor, ZstdCompressor, ParallelCompressor, and compression utilities.
"""

import os
import tempfile
import unittest

import pytest

from codomyrmex.compression import (
    Compressor,
    CompressionError,
    ZstdCompressor,
    ParallelCompressor,
    compress_data,
    decompress_data,
    auto_decompress,
    compress,
    decompress,
    get_compressor,
)


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

    def test_unsupported_format(self):
        """Test unsupported format raises error."""
        with pytest.raises(ValueError, match="Unsupported format"):
            Compressor("unsupported")

    def test_supported_formats(self):
        """Test SUPPORTED_FORMATS constant."""
        assert "gzip" in Compressor.SUPPORTED_FORMATS
        assert "zlib" in Compressor.SUPPORTED_FORMATS
        assert "zip" in Compressor.SUPPORTED_FORMATS


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


class TestZipCompression:
    """Tests for ZIP compression."""

    def test_zip_compression(self):
        """Test basic ZIP compression."""
        data = b"Hello, world!" * 100
        compressor = Compressor("zip")
        compressed = compressor.compress(data)
        decompressed = compressor.decompress(compressed)

        assert data == decompressed


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


class TestStreamCompression:
    """Tests for stream compression."""

    def test_compress_stream(self, tmp_path):
        """Test stream compression."""
        from io import BytesIO

        compressor = Compressor("gzip")
        input_stream = BytesIO(b"stream data " * 100)
        output_stream = BytesIO()

        compressor.compress_stream(input_stream, output_stream)

        # Output should have data
        assert output_stream.tell() > 0

    def test_decompress_stream(self, tmp_path):
        """Test stream decompression."""
        from io import BytesIO

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
        compressed = compress(data)
        decompressed = decompress(compressed)

        assert decompressed == data

    def test_get_compressor_function(self):
        """Test get_compressor convenience function."""
        compressor = get_compressor("zlib")

        assert isinstance(compressor, Compressor)
        assert compressor.format == "zlib"

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


class TestCompressionError:
    """Tests for CompressionError handling."""

    def test_decompression_error(self):
        """Test decompression of invalid data raises error."""
        compressor = Compressor("gzip")

        with pytest.raises(CompressionError):
            compressor.decompress(b"invalid compressed data")
