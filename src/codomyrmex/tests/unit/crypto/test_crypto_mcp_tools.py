"""Zero-mock tests for crypto.mcp_tools module.

Covers: hash_data, verify_hash, generate_key MCP tool functions.

Zero-mock policy: no unittest.mock, no MagicMock, no monkeypatch.
"""

import hashlib

import pytest

from codomyrmex.crypto.mcp_tools import generate_key, hash_data, verify_hash


# ==============================================================================
# hash_data
# ==============================================================================


@pytest.mark.unit
@pytest.mark.crypto
class TestHashData:
    """Tests for the hash_data MCP tool."""

    def test_sha256_default(self):
        result = hash_data("hello world")
        assert result["status"] == "success"
        assert result["algorithm"] == "sha256"
        assert len(result["digest"]) == 64  # SHA-256 = 32 bytes = 64 hex chars
        # Verify against stdlib
        expected = hashlib.sha256(b"hello world").hexdigest()
        assert result["digest"] == expected

    def test_sha384(self):
        result = hash_data("test", algorithm="sha384")
        assert result["status"] == "success"
        assert len(result["digest"]) == 96

    def test_sha512(self):
        result = hash_data("test", algorithm="sha512")
        assert result["status"] == "success"
        assert len(result["digest"]) == 128

    def test_sha3_256(self):
        result = hash_data("test", algorithm="sha3_256")
        assert result["status"] == "success"
        assert len(result["digest"]) == 64

    def test_blake2b(self):
        result = hash_data("test", algorithm="blake2b")
        assert result["status"] == "success"
        assert result["digest_length"] > 0

    def test_empty_string_hashes(self):
        result = hash_data("")
        assert result["status"] == "success"
        assert result["digest"] == hashlib.sha256(b"").hexdigest()

    def test_unsupported_algorithm_returns_error(self):
        result = hash_data("test", algorithm="md5")
        assert result["status"] == "error"
        assert "Unsupported algorithm" in result["message"]
        assert "md5" in result["message"]

    def test_unsupported_algorithm_sha1_returns_error(self):
        result = hash_data("test", algorithm="sha1")
        assert result["status"] == "error"

    def test_digest_length_field_matches_digest(self):
        result = hash_data("data", algorithm="sha256")
        assert result["digest_length"] == len(result["digest"])

    def test_deterministic_same_input(self):
        r1 = hash_data("consistent data")
        r2 = hash_data("consistent data")
        assert r1["digest"] == r2["digest"]

    def test_different_inputs_different_digests(self):
        r1 = hash_data("abc")
        r2 = hash_data("abd")
        assert r1["digest"] != r2["digest"]

    def test_unicode_input_encoded_as_utf8(self):
        result = hash_data("héllo wörld")
        assert result["status"] == "success"
        expected = hashlib.sha256("héllo wörld".encode("utf-8")).hexdigest()
        assert result["digest"] == expected

    def test_return_keys_present(self):
        result = hash_data("x")
        assert "status" in result
        assert "algorithm" in result
        assert "digest" in result
        assert "digest_length" in result


# ==============================================================================
# verify_hash
# ==============================================================================


@pytest.mark.unit
@pytest.mark.crypto
class TestVerifyHash:
    """Tests for the verify_hash MCP tool."""

    def _make_hash(self, data: str, algorithm: str = "sha256") -> str:
        h = hashlib.new(algorithm)
        h.update(data.encode("utf-8"))
        return h.hexdigest()

    def test_correct_hash_matches(self):
        expected = self._make_hash("hello")
        result = verify_hash("hello", expected)
        assert result["status"] == "success"
        assert result["match"] is True

    def test_wrong_hash_does_not_match(self):
        result = verify_hash("hello", "deadbeef" * 8)
        assert result["status"] == "success"
        assert result["match"] is False

    def test_correct_sha512_hash(self):
        expected = self._make_hash("data", "sha512")
        result = verify_hash("data", expected, algorithm="sha512")
        assert result["status"] == "success"
        assert result["match"] is True

    def test_algorithm_field_in_result(self):
        expected = self._make_hash("x")
        result = verify_hash("x", expected)
        assert result["algorithm"] == "sha256"

    def test_empty_string_verify(self):
        expected = self._make_hash("")
        result = verify_hash("", expected)
        assert result["match"] is True

    def test_tampered_data_fails(self):
        expected = self._make_hash("original")
        result = verify_hash("tampered", expected)
        assert result["match"] is False

    def test_unsupported_algorithm_returns_error(self):
        # Only algorithms not in hashlib.algorithms_available should error.
        # md5 is available in most environments, so use a clearly invalid one.
        result = verify_hash("data", "abc", algorithm="not_a_real_algo_xyz")
        assert result["status"] == "error"
        assert "message" in result

    def test_return_keys_present(self):
        result = verify_hash("x", "y")
        assert "status" in result
        assert "match" in result
        assert "algorithm" in result


# ==============================================================================
# generate_key
# ==============================================================================


@pytest.mark.unit
@pytest.mark.crypto
class TestGenerateKey:
    """Tests for the generate_key MCP tool."""

    def test_aes256_hex_default(self):
        result = generate_key()
        assert result["status"] == "success"
        assert result["algorithm"] == "aes256"
        assert result["encoding"] == "hex"
        assert result["key_bits"] == 256
        # 32 bytes -> 64 hex chars
        assert len(result["key"]) == 64
        # Valid hex string
        int(result["key"], 16)

    def test_aes128_hex(self):
        result = generate_key(algorithm="aes128")
        assert result["status"] == "success"
        assert result["key_bits"] == 128
        assert len(result["key"]) == 32  # 16 bytes = 32 hex chars

    def test_hmac256_hex(self):
        result = generate_key(algorithm="hmac256")
        assert result["status"] == "success"
        assert result["key_bits"] == 256
        assert len(result["key"]) == 64

    def test_aes256_base64(self):
        result = generate_key(algorithm="aes256", encoding="base64")
        assert result["status"] == "success"
        assert result["encoding"] == "base64"
        import base64

        raw = base64.b64decode(result["key"])
        assert len(raw) == 32

    def test_aes128_base64(self):
        result = generate_key(algorithm="aes128", encoding="base64")
        import base64

        raw = base64.b64decode(result["key"])
        assert len(raw) == 16

    def test_unsupported_algorithm_returns_error(self):
        result = generate_key(algorithm="rsa2048")
        assert result["status"] == "error"
        assert "Unsupported algorithm" in result["message"]

    def test_keys_are_unique(self):
        r1 = generate_key()
        r2 = generate_key()
        assert r1["key"] != r2["key"]

    def test_return_keys_present(self):
        result = generate_key()
        assert "status" in result
        assert "algorithm" in result
        assert "encoding" in result
        assert "key" in result
        assert "key_bits" in result
