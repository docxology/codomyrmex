"""Parallel compression utilities."""

from concurrent.futures import ThreadPoolExecutor

from .compressor import Compressor


class ParallelCompressor:
    """Compresses multiple data chunks in parallel."""

    def __init__(self, format: str = "gzip", max_workers: int = 4):
        self.format = format
        self.max_workers = max_workers

    def compress_batch(self, data_list: list[bytes]) -> list[bytes]:
        """Compress a list of data blobs in parallel."""
        compressor = Compressor(self.format)
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            return list(executor.map(compressor.compress, data_list))

    def decompress_batch(self, data_list: list[bytes]) -> list[bytes]:
        """Decompress a list of data blobs in parallel."""
        compressor = Compressor(self.format)
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            return list(executor.map(compressor.decompress, data_list))
