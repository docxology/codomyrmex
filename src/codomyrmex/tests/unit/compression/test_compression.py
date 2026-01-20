"""Unit tests for the compression module."""

import unittest
from codomyrmex.compression import Compressor, ZstdCompressor, ParallelCompressor

class TestCompression(unittest.TestCase):
    def test_gzip_compression(self):
        data = b"Hello, world!" * 100
        compressor = Compressor("gzip")
        compressed = compressor.compress(data)
        decompressed = compressor.decompress(compressed)
        self.assertEqual(data, decompressed)
        self.assertTrue(len(compressed) < len(data))

    def test_zstd_compression(self):
        try:
            data = b"Hello, world!" * 100
            compressor = ZstdCompressor()
            compressed = compressor.compress(data)
            decompressed = compressor.decompress(compressed)
            self.assertEqual(data, decompressed)
        except ImportError:
            self.skipTest("zstandard not installed")

    def test_parallel_compression(self):
        data_list = [b"data1" * 100, b"data2" * 100]
        compressor = ParallelCompressor("gzip")
        compressed_list = compressor.compress_batch(data_list)
        decompressed_list = compressor.decompress_batch(compressed_list)
        self.assertEqual(data_list, decompressed_list)
