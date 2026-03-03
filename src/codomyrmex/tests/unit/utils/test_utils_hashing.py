"""Unit tests for content and file hashing utilities."""

import hashlib
import tempfile
from pathlib import Path

import pytest


@pytest.mark.unit
class TestHashContent:
    """Tests for hash_content function."""

    def test_hash_string(self):
        """Test hashing a string."""
        from codomyrmex.utils import hash_content

        result = hash_content("test content")

        assert len(result) == 64  # SHA256 hex length
        assert result.isalnum()

    def test_hash_bytes(self):
        """Test hashing bytes."""
        from codomyrmex.utils import hash_content

        result = hash_content(b"test content")

        assert len(result) == 64

    def test_different_algorithms(self):
        """Test different hash algorithms."""
        from codomyrmex.utils import hash_content

        sha256 = hash_content("test", algorithm="sha256")
        sha512 = hash_content("test", algorithm="sha512")
        md5 = hash_content("test", algorithm="md5")

        assert len(sha256) == 64
        assert len(sha512) == 128
        assert len(md5) == 32

    def test_same_input_same_hash(self):
        """Test same input produces same hash."""
        from codomyrmex.utils import hash_content

        hash1 = hash_content("identical")
        hash2 = hash_content("identical")

        assert hash1 == hash2

    def test_different_input_different_hash(self):
        """Test different input produces different hash."""
        from codomyrmex.utils import hash_content

        hash1 = hash_content("content1")
        hash2 = hash_content("content2")

        assert hash1 != hash2

    def test_hash_empty_string(self):
        """Test hashing empty string."""
        from codomyrmex.utils import hash_content

        result = hash_content("")

        assert len(result) == 64  # SHA256 always produces 64 char hex


@pytest.mark.unit
class TestHashFile:
    """Tests for hash_file function."""

    def test_hash_existing_file(self, tmp_path):
        """Test hashing an existing file."""
        from codomyrmex.utils import hash_file

        test_file = tmp_path / "test.txt"
        test_file.write_text("file content")

        result = hash_file(test_file)

        assert result is not None
        assert len(result) == 64

    def test_hash_nonexistent_file(self):
        """Test hashing non-existent file returns None."""
        from codomyrmex.utils import hash_file

        result = hash_file("/nonexistent/file.txt")

        assert result is None

    def test_hash_file_string_path(self, tmp_path):
        """Test hashing with string path."""
        from codomyrmex.utils import hash_file

        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        result = hash_file(str(test_file))

        assert result is not None

    def test_hash_file_different_algorithms(self, tmp_path):
        """Test hashing file with different algorithms."""
        from codomyrmex.utils import hash_file

        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        sha256 = hash_file(test_file, algorithm="sha256")
        md5 = hash_file(test_file, algorithm="md5")

        assert len(sha256) == 64
        assert len(md5) == 32

    def test_hash_file_same_content_same_hash(self, tmp_path):
        """Test same file content produces same hash."""
        from codomyrmex.utils import hash_file

        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        file1.write_text("identical content")
        file2.write_text("identical content")

        hash1 = hash_file(file1)
        hash2 = hash_file(file2)

        assert hash1 == hash2


# From test_coverage_boost.py
class TestContentHash:
    """Tests for content_hash function."""

    def test_sha256_default(self):
        from codomyrmex.utils.hashing import content_hash

        expected = hashlib.sha256(b"hello").hexdigest()
        assert content_hash("hello") == expected

    def test_md5_algorithm(self):
        from codomyrmex.utils.hashing import content_hash

        expected = hashlib.md5(b"hello").hexdigest()
        assert content_hash("hello", "md5") == expected

    def test_bytes_input(self):
        from codomyrmex.utils.hashing import content_hash

        expected = hashlib.sha256(b"\x00\x01\x02").hexdigest()
        assert content_hash(b"\x00\x01\x02") == expected


# From test_coverage_boost.py
class TestFileHash:
    """Tests for file_hash function."""

    def test_file_hash_matches_content_hash(self):
        from codomyrmex.utils.hashing import content_hash, file_hash

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("test content")
            f.flush()
            path = Path(f.name)

        expected = content_hash("test content")
        assert file_hash(path) == expected
        path.unlink()


# From test_coverage_boost.py
class TestDictHash:
    """Tests for dict_hash function."""

    def test_deterministic(self):
        from codomyrmex.utils.hashing import dict_hash

        d = {"b": 2, "a": 1}
        assert dict_hash(d) == dict_hash({"a": 1, "b": 2})

    def test_different_dicts_differ(self):
        from codomyrmex.utils.hashing import dict_hash

        assert dict_hash({"a": 1}) != dict_hash({"a": 2})


# From test_coverage_boost.py
class TestConsistentHash:
    """Tests for ConsistentHash ring."""

    def test_single_node(self):
        from codomyrmex.utils.hashing import ConsistentHash

        ring = ConsistentHash(["node-a"])
        assert ring.get_node("any-key") == "node-a"

    def test_multiple_nodes(self):
        from codomyrmex.utils.hashing import ConsistentHash

        ring = ConsistentHash(["a", "b", "c"])
        assert ring.nodes == {"a", "b", "c"}
        node = ring.get_node("test-key")
        assert node in {"a", "b", "c"}

    def test_consistency(self):
        from codomyrmex.utils.hashing import ConsistentHash

        ring = ConsistentHash(["a", "b", "c"])
        results = [ring.get_node("stable-key") for _ in range(100)]
        assert len(set(results)) == 1  # Same key -> same node

    def test_add_remove_node(self):
        from codomyrmex.utils.hashing import ConsistentHash

        ring = ConsistentHash(["a", "b"])
        ring.add_node("c")
        assert "c" in ring.nodes
        ring.remove_node("a")
        assert "a" not in ring.nodes

    def test_empty_ring_raises(self):
        from codomyrmex.utils.hashing import ConsistentHash

        ring = ConsistentHash()
        with pytest.raises(ValueError, match="No nodes"):
            ring.get_node("key")


# From test_coverage_boost.py
class TestFingerprint:
    """Tests for fingerprint function."""

    def test_stable(self):
        from codomyrmex.utils.hashing import fingerprint

        fp1 = fingerprint("a", 1, True)
        fp2 = fingerprint("a", 1, True)
        assert fp1 == fp2

    def test_different_args_differ(self):
        from codomyrmex.utils.hashing import fingerprint

        assert fingerprint("a", 1) != fingerprint("a", 2)
