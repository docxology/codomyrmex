"""Parallel compression utilities with chunking, progress, and stats.

Provides:
- ParallelCompressor: compress/decompress batches concurrently
- Chunked compression: split large data into chunks for parallel processing
- Progress callback for long-running operations
- Compression statistics (ratio, throughput)
"""

from __future__ import annotations

import time
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass

from ..core.compressor import Compressor


@dataclass
class CompressionStats:
    """Statistics from a compression/decompression operation."""

    input_bytes: int
    output_bytes: int
    duration_seconds: float
    chunk_count: int

    @property
    def ratio(self) -> float:
        """Compression ratio (smaller = better compression)."""
        if self.input_bytes == 0:
            return 0.0
        return self.output_bytes / self.input_bytes

    @property
    def throughput_mbps(self) -> float:
        """Throughput in MB/s."""
        if self.duration_seconds == 0:
            return 0.0
        return (self.input_bytes / (1024 * 1024)) / self.duration_seconds

    @property
    def savings_percent(self) -> float:
        """Space savings as a percentage."""
        return (1.0 - self.ratio) * 100


class ParallelCompressor:
    """Compresses multiple data chunks in parallel with progress tracking.

    Args:
        format: Compression format (gzip, bz2, lzma).
        max_workers: Maximum concurrent threads.
        chunk_size: Size of chunks for split_and_compress (bytes).

    Example::

        pc = ParallelCompressor(format="gzip", max_workers=4)
        compressed = pc.compress_batch([b"data1", b"data2", b"data3"])
        decompressed = pc.decompress_batch(compressed)
    """

    def __init__(
        self,
        format: str = "gzip",
        max_workers: int = 4,
        chunk_size: int = 1024 * 1024,  # 1MB default chunks
    ) -> None:
        """Execute   Init   operations natively."""
        self.format = format
        self.max_workers = max_workers
        self.chunk_size = chunk_size
        self._last_stats: CompressionStats | None = None

    def compress_batch(
        self,
        data_list: list[bytes],
        on_progress: Callable[[int, int], None] | None = None,
    ) -> list[bytes]:
        """Compress a list of data blobs in parallel.

        Args:
            data_list: List of byte strings to compress.
            on_progress: Optional callback(completed, total) for progress tracking.

        Returns:
            List of compressed byte strings (same order as input).
        """
        start = time.time()
        compressor = Compressor(self.format)
        total = len(data_list)
        results: list[bytes | None] = [None] * total

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(compressor.compress, data): idx
                for idx, data in enumerate(data_list)
            }
            completed = 0
            for future in as_completed(futures):
                idx = futures[future]
                results[idx] = future.result()
                completed += 1
                if on_progress:
                    on_progress(completed, total)

        duration = time.time() - start
        input_total = sum(len(d) for d in data_list)
        output_total = sum(len(r) for r in results if r is not None)
        self._last_stats = CompressionStats(
            input_bytes=input_total,
            output_bytes=output_total,
            duration_seconds=duration,
            chunk_count=total,
        )
        return [r for r in results if r is not None]

    def decompress_batch(
        self,
        data_list: list[bytes],
        on_progress: Callable[[int, int], None] | None = None,
    ) -> list[bytes]:
        """Decompress a list of data blobs in parallel."""
        start = time.time()
        compressor = Compressor(self.format)
        total = len(data_list)
        results: list[bytes | None] = [None] * total

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(compressor.decompress, data): idx
                for idx, data in enumerate(data_list)
            }
            completed = 0
            for future in as_completed(futures):
                idx = futures[future]
                results[idx] = future.result()
                completed += 1
                if on_progress:
                    on_progress(completed, total)

        duration = time.time() - start
        self._last_stats = CompressionStats(
            input_bytes=sum(len(d) for d in data_list),
            output_bytes=sum(len(r) for r in results if r is not None),
            duration_seconds=duration,
            chunk_count=total,
        )
        return [r for r in results if r is not None]

    def split_and_compress(
        self,
        data: bytes,
        on_progress: Callable[[int, int], None] | None = None,
    ) -> list[bytes]:
        """Split large data into chunks and compress each in parallel.

        Args:
            data: Large byte string to compress.
            on_progress: Optional progress callback.

        Returns:
            List of compressed chunks. Decompress and concatenate to recover.
        """
        chunks = [
            data[i: i + self.chunk_size]
            for i in range(0, len(data), self.chunk_size)
        ]
        return self.compress_batch(chunks, on_progress=on_progress)

    def decompress_and_merge(
        self,
        compressed_chunks: list[bytes],
        on_progress: Callable[[int, int], None] | None = None,
    ) -> bytes:
        """Decompress chunks and merge back into a single byte string."""
        decompressed = self.decompress_batch(compressed_chunks, on_progress=on_progress)
        return b"".join(decompressed)

    @property
    def last_stats(self) -> CompressionStats | None:
        """Statistics from the most recent operation."""
        return self._last_stats
