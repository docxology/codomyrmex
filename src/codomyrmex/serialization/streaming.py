"""Streaming serialization for large datasets.

Provides generators and iterators for serializing/deserializing
large datasets without loading everything into memory.
"""

from __future__ import annotations

import csv
import json
from collections.abc import Generator, Iterator
from pathlib import Path
from typing import Any


def stream_jsonl_write(path: Path, items: Iterator[dict[str, Any]],
                       flush_every: int = 100) -> int:
    """Stream-write items as JSON Lines.

    Args:
        path: Output file path.
        items: Iterator of dicts to serialize.
        flush_every: Flush to disk every N items.

    Returns:
        Number of items written.
    """
    count = 0
    with open(path, "w") as f:
        for item in items:
            f.write(json.dumps(item, default=str) + "\n")
            count += 1
            if count % flush_every == 0:
                f.flush()
    return count


def stream_jsonl_read(path: Path) -> Generator[dict[str, Any], None, None]:
    """Stream-read items from a JSON Lines file."""
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


def stream_csv_write(path: Path, items: Iterator[dict[str, Any]],
                     fieldnames: list[str] | None = None) -> int:
    """Stream-write dicts as CSV rows."""
    count = 0

    with open(path, "w", newline="") as f:
        writer: csv.DictWriter | None = None
        for item in items:
            if writer is None:
                fields = fieldnames or list(item.keys())
                writer = csv.DictWriter(f, fieldnames=fields)
                writer.writeheader()
            writer.writerow(item)
            count += 1
    return count


def stream_csv_read(path: Path) -> Generator[dict[str, str], None, None]:
    """Stream-read CSV rows as dicts."""
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield dict(row)


def chunked_json_write(path: Path, items: list[Any],
                       chunk_size: int = 1000) -> int:
    """Write a large list as JSON in chunks to manage memory."""
    with open(path, "w") as f:
        f.write("[\n")
        for i, item in enumerate(items):
            if i > 0:
                f.write(",\n")
            json.dump(item, f, default=str)
        f.write("\n]")
    return len(items)


class StreamBuffer:
    """Buffer for accumulating items before batch serialization."""

    def __init__(self, max_size: int = 1000,
                 flush_callback: Any = None) -> None:
        """Initialize this instance."""
        self._max_size = max_size
        self._buffer: list[Any] = []
        self._flush_callback = flush_callback
        self._total_flushed = 0

    def add(self, item: Any) -> None:
        """Add an item to the buffer, auto-flushing if full."""
        self._buffer.append(item)
        if len(self._buffer) >= self._max_size:
            self.flush()

    def flush(self) -> list[Any]:
        """Flush the buffer, returning all items."""
        items = self._buffer
        self._buffer = []
        self._total_flushed += len(items)
        if self._flush_callback and items:
            self._flush_callback(items)
        return items

    @property
    def pending(self) -> int:
        """pending ."""
        return len(self._buffer)

    @property
    def total_flushed(self) -> int:
        """total Flushed ."""
        return self._total_flushed
