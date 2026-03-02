"""Consistent hashing and content-addressable utilities.

Provides hash functions for content addressing, consistent hashing
for distributed systems, and fingerprinting utilities.
"""

from __future__ import annotations

import hashlib
import json
from bisect import bisect_right
from pathlib import Path
from typing import Any


def content_hash(data: str | bytes, algorithm: str = "sha256") -> str:
    """Compute content-addressable hash of data.

    Args:
        data: String or bytes to hash.
        algorithm: Hash algorithm (sha256, sha1, md5, blake2b).

    Returns:
        Hex digest string.
    """
    if isinstance(data, str):
        data = data.encode("utf-8")
    h = hashlib.new(algorithm)
    h.update(data)
    return h.hexdigest()


def file_hash(path: Path, algorithm: str = "sha256", chunk_size: int = 8192) -> str:
    """Compute hash of a file's contents, streaming to handle large files."""
    h = hashlib.new(algorithm)
    with open(path, "rb") as f:
        while chunk := f.read(chunk_size):
            h.update(chunk)
    return h.hexdigest()


def dict_hash(data: dict[str, Any], algorithm: str = "sha256") -> str:
    """Compute deterministic hash of a dictionary (sorted keys)."""
    serialized = json.dumps(data, sort_keys=True, default=str)
    return content_hash(serialized, algorithm)


class ConsistentHash:
    """Consistent hash ring for distributing items across nodes.

    Uses virtual nodes (replicas) for better distribution uniformity.
    """

    def __init__(self, nodes: list[str] | None = None, replicas: int = 100) -> None:
        """Initialize this instance."""
        self._replicas = replicas
        self._ring: list[int] = []
        self._node_map: dict[int, str] = {}
        for node in (nodes or []):
            self.add_node(node)

    def _hash(self, key: str) -> int:
        """hash ."""
        return int(hashlib.md5(key.encode()).hexdigest(), 16)

    def add_node(self, node: str) -> None:
        """Add a node to the ring."""
        for i in range(self._replicas):
            h = self._hash(f"{node}:{i}")
            self._ring.append(h)
            self._node_map[h] = node
        self._ring.sort()

    def remove_node(self, node: str) -> None:
        """Remove a node from the ring."""
        for i in range(self._replicas):
            h = self._hash(f"{node}:{i}")
            self._ring.remove(h)
            del self._node_map[h]

    def get_node(self, key: str) -> str:
        """Get the node responsible for a given key."""
        if not self._ring:
            raise ValueError("No nodes in the ring")
        h = self._hash(key)
        idx = bisect_right(self._ring, h)
        if idx >= len(self._ring):
            idx = 0
        return self._node_map[self._ring[idx]]

    @property
    def nodes(self) -> set[str]:
        """nodes ."""
        return set(self._node_map.values())


def fingerprint(*args: Any) -> str:
    """Create a stable fingerprint from multiple arguments."""
    parts = [str(a) for a in args]
    return content_hash("|".join(parts))
