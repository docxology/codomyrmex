"""
Unit tests for utils.hashing — Zero-Mock compliant.

Covers: content_hash (str, bytes, algorithms), file_hash (streaming),
dict_hash (deterministic, sort-key stability), ConsistentHash (ring,
add_node, remove_node, get_node, wrap-around, nodes property),
fingerprint (multi-arg stable output).
"""

import tempfile
from pathlib import Path

import pytest

from codomyrmex.utils.hashing import (
    ConsistentHash,
    content_hash,
    dict_hash,
    file_hash,
    fingerprint,
)

# ── content_hash ───────────────────────────────────────────────────────


@pytest.mark.unit
class TestContentHash:
    def test_string_returns_hex(self):
        result = content_hash("hello")
        assert isinstance(result, str)
        assert all(c in "0123456789abcdef" for c in result)

    def test_sha256_length(self):
        result = content_hash("hello", "sha256")
        assert len(result) == 64

    def test_md5_length(self):
        result = content_hash("hello", "md5")
        assert len(result) == 32

    def test_sha1_length(self):
        result = content_hash("hello", "sha1")
        assert len(result) == 40

    def test_bytes_input(self):
        result = content_hash(b"hello")
        assert len(result) == 64

    def test_str_and_bytes_same_result(self):
        assert content_hash("hello") == content_hash(b"hello")

    def test_deterministic(self):
        assert content_hash("abc") == content_hash("abc")

    def test_different_inputs_differ(self):
        assert content_hash("abc") != content_hash("abd")

    def test_empty_string(self):
        result = content_hash("")
        assert len(result) == 64

    def test_unicode_encoded_utf8(self):
        # Should not raise — utf-8 encode applied to str
        result = content_hash("héllo")
        assert len(result) == 64


# ── file_hash ──────────────────────────────────────────────────────────


@pytest.mark.unit
class TestFileHash:
    def test_matches_content_hash_sha256(self):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as f:
            f.write(b"test content")
            tmp_path = Path(f.name)
        try:
            result = file_hash(tmp_path)
            expected = content_hash(b"test content")
            assert result == expected
        finally:
            tmp_path.unlink()

    def test_md5_algorithm(self):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as f:
            f.write(b"data")
            tmp_path = Path(f.name)
        try:
            result = file_hash(tmp_path, algorithm="md5")
            assert len(result) == 32
        finally:
            tmp_path.unlink()

    def test_small_chunk_size_still_works(self):
        """chunk_size=1 forces many reads — same result as default."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as f:
            f.write(b"hello world")
            tmp_path = Path(f.name)
        try:
            normal = file_hash(tmp_path)
            small_chunk = file_hash(tmp_path, chunk_size=1)
            assert normal == small_chunk
        finally:
            tmp_path.unlink()

    def test_empty_file(self):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as f:
            tmp_path = Path(f.name)
        try:
            result = file_hash(tmp_path)
            assert isinstance(result, str)
            assert len(result) == 64
        finally:
            tmp_path.unlink()


# ── dict_hash ──────────────────────────────────────────────────────────


@pytest.mark.unit
class TestDictHash:
    def test_returns_hex(self):
        result = dict_hash({"a": 1})
        assert isinstance(result, str)
        assert len(result) == 64

    def test_deterministic(self):
        d = {"key": "value", "num": 42}
        assert dict_hash(d) == dict_hash(d)

    def test_key_order_independent(self):
        d1 = {"b": 2, "a": 1}
        d2 = {"a": 1, "b": 2}
        assert dict_hash(d1) == dict_hash(d2)

    def test_different_values_differ(self):
        assert dict_hash({"a": 1}) != dict_hash({"a": 2})

    def test_empty_dict(self):
        result = dict_hash({})
        assert len(result) == 64

    def test_md5_algorithm(self):
        result = dict_hash({"a": 1}, algorithm="md5")
        assert len(result) == 32

    def test_non_serializable_values_use_str(self):
        """default=str in json.dumps handles non-JSON values."""
        result = dict_hash({"dt": object()})
        assert isinstance(result, str)


# ── ConsistentHash ────────────────────────────────────────────────────


@pytest.mark.unit
class TestConsistentHash:
    def test_empty_ring_raises_on_get(self):
        ch = ConsistentHash()
        with pytest.raises(ValueError, match="No nodes"):
            ch.get_node("key")

    def test_single_node_always_returns_that_node(self):
        ch = ConsistentHash(nodes=["node1"])
        assert ch.get_node("any_key") == "node1"
        assert ch.get_node("another") == "node1"

    def test_nodes_property_returns_set_of_node_names(self):
        ch = ConsistentHash(nodes=["a", "b", "c"])
        assert ch.nodes == {"a", "b", "c"}

    def test_add_node(self):
        ch = ConsistentHash()
        ch.add_node("new_node")
        assert "new_node" in ch.nodes

    def test_remove_node(self):
        ch = ConsistentHash(nodes=["x", "y"])
        ch.remove_node("x")
        assert "x" not in ch.nodes
        assert "y" in ch.nodes

    def test_get_node_returns_valid_node(self):
        nodes = ["server1", "server2", "server3"]
        ch = ConsistentHash(nodes=nodes)
        result = ch.get_node("my_key")
        assert result in nodes

    def test_consistent_routing(self):
        """Same key always maps to same node (no randomness)."""
        ch = ConsistentHash(nodes=["a", "b", "c"], replicas=10)
        first = ch.get_node("test_key")
        for _ in range(5):
            assert ch.get_node("test_key") == first

    def test_many_keys_distribute_across_nodes(self):
        ch = ConsistentHash(nodes=["n1", "n2", "n3"], replicas=100)
        seen = {ch.get_node(f"key-{i}") for i in range(200)}
        # With 3 nodes and 100 replicas, all 3 should get traffic
        assert len(seen) >= 2

    def test_replicas_default_100(self):
        ch = ConsistentHash(nodes=["n1"])
        # 100 virtual nodes * 1 real node = 100 ring entries
        assert len(ch._ring) == 100

    def test_custom_replicas(self):
        ch = ConsistentHash(nodes=["n1"], replicas=5)
        assert len(ch._ring) == 5

    def test_wrap_around_handled(self):
        """When hash > all ring entries, idx wraps to 0."""
        ch = ConsistentHash(nodes=["only_node"], replicas=1)
        # Any key should still return the node
        result = ch.get_node("wrap_test_key_xxxx")
        assert result == "only_node"


# ── fingerprint ───────────────────────────────────────────────────────


@pytest.mark.unit
class TestFingerprint:
    def test_returns_hex_string(self):
        result = fingerprint("a", "b")
        assert isinstance(result, str)
        assert len(result) == 64

    def test_stable_across_calls(self):
        assert fingerprint("x", 1, True) == fingerprint("x", 1, True)

    def test_different_args_differ(self):
        assert fingerprint("a", "b") != fingerprint("b", "a")

    def test_single_arg(self):
        result = fingerprint("solo")
        assert len(result) == 64

    def test_numeric_args(self):
        result = fingerprint(1, 2, 3)
        assert len(result) == 64

    def test_no_args(self):
        """fingerprint() with no args → empty join → valid hash."""
        result = fingerprint()
        assert len(result) == 64
