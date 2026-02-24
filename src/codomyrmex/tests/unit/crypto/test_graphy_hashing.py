"""Tests for codomyrmex.crypto.graphy.hashing."""

from __future__ import annotations

import warnings

import pytest

from codomyrmex.crypto.exceptions import HashError
from codomyrmex.crypto.graphy.hashing import (
    HashAlgorithm,
    hash_blake2b,
    hash_data,
    hash_md5,
    hash_sha256,
    hash_sha3_256,
    hash_sha512,
    verify_hash,
)


@pytest.mark.crypto
@pytest.mark.unit
class TestSHA256:
    """Test suite for SHA256."""
    def test_known_vector_empty(self) -> None:
        """Test functionality: known vector empty."""
        # SHA-256 of empty string
        expected = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        assert hash_sha256(b"") == expected

    def test_known_vector_abc(self) -> None:
        """Test functionality: known vector abc."""
        expected = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
        assert hash_sha256(b"abc") == expected

    def test_hex_length(self) -> None:
        """Test functionality: hex length."""
        result = hash_sha256(b"test data")
        assert len(result) == 64  # 32 bytes = 64 hex chars


@pytest.mark.crypto
@pytest.mark.unit
class TestSHA3_256:
    """Test suite for SHA3_256."""
    def test_known_vector_empty(self) -> None:
        """Test functionality: known vector empty."""
        # SHA-3-256 of empty string
        expected = "a7ffc6f8bf1ed76651c14756a061d662f580ff4de43b49fa82d80a4b80f8434a"
        assert hash_sha3_256(b"") == expected

    def test_hex_length(self) -> None:
        """Test functionality: hex length."""
        result = hash_sha3_256(b"test data")
        assert len(result) == 64


@pytest.mark.crypto
@pytest.mark.unit
class TestSHA512:
    """Test suite for SHA512."""
    def test_known_vector_empty(self) -> None:
        """Test functionality: known vector empty."""
        # SHA-512 of empty string
        expected = (
            "cf83e1357eefb8bdf1542850d66d8007d620e4050b5715dc83f4a921d36ce9ce"
            "47d0d13c5d85f2b0ff8318d2877eec2f63b931bd47417a81a538327af927da3e"
        )
        assert hash_sha512(b"") == expected

    def test_hex_length(self) -> None:
        """Test functionality: hex length."""
        result = hash_sha512(b"test data")
        assert len(result) == 128  # 64 bytes = 128 hex chars


@pytest.mark.crypto
@pytest.mark.unit
class TestBLAKE2b:
    """Test suite for BLAKE2b."""
    def test_default_digest_size(self) -> None:
        """Test functionality: default digest size."""
        result = hash_blake2b(b"test")
        assert len(result) == 64  # 32 bytes = 64 hex chars

    def test_custom_digest_size(self) -> None:
        """Test functionality: custom digest size."""
        result = hash_blake2b(b"test", digest_size=16)
        assert len(result) == 32  # 16 bytes = 32 hex chars

    def test_invalid_digest_size(self) -> None:
        """Test functionality: invalid digest size."""
        with pytest.raises(HashError, match="digest_size must be 1-64"):
            hash_blake2b(b"test", digest_size=0)

    def test_deterministic(self) -> None:
        """Test functionality: deterministic."""
        assert hash_blake2b(b"data") == hash_blake2b(b"data")


@pytest.mark.crypto
@pytest.mark.unit
class TestMD5:
    """Test suite for MD5."""
    def test_known_vector_empty(self) -> None:
        """Test functionality: known vector empty."""
        expected = "d41d8cd98f00b204e9800998ecf8427e"
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            assert hash_md5(b"") == expected

    def test_known_vector_abc(self) -> None:
        """Test functionality: known vector abc."""
        expected = "900150983cd24fb0d6963f7d28e17f72"
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            assert hash_md5(b"abc") == expected

    def test_deprecation_warning(self) -> None:
        """Test functionality: deprecation warning."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            hash_md5(b"test")
            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "MD5 is cryptographically broken" in str(w[0].message)


@pytest.mark.crypto
@pytest.mark.unit
class TestHashData:
    """Test suite for HashData."""
    def test_dispatch_sha256(self) -> None:
        """Test functionality: dispatch sha256."""
        assert hash_data(b"abc", "sha256") == hash_sha256(b"abc")

    def test_dispatch_sha3_256(self) -> None:
        """Test functionality: dispatch sha3 256."""
        assert hash_data(b"abc", "sha3_256") == hash_sha3_256(b"abc")

    def test_dispatch_sha512(self) -> None:
        """Test functionality: dispatch sha512."""
        assert hash_data(b"abc", "sha512") == hash_sha512(b"abc")

    def test_dispatch_blake2b(self) -> None:
        """Test functionality: dispatch blake2b."""
        assert hash_data(b"abc", "blake2b") == hash_blake2b(b"abc")

    def test_dispatch_md5(self) -> None:
        """Test functionality: dispatch md5."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            assert hash_data(b"abc", "md5") == hash_md5(b"abc")

    def test_default_is_sha256(self) -> None:
        """Test functionality: default is sha256."""
        assert hash_data(b"abc") == hash_sha256(b"abc")

    def test_unknown_algorithm(self) -> None:
        """Test functionality: unknown algorithm."""
        with pytest.raises(HashError, match="Unknown hash algorithm"):
            hash_data(b"abc", "whirlpool")


@pytest.mark.crypto
@pytest.mark.unit
class TestVerifyHash:
    """Test suite for VerifyHash."""
    def test_correct_hash_passes(self) -> None:
        """Test functionality: correct hash passes."""
        data = b"verify me"
        h = hash_sha256(data)
        assert verify_hash(data, h, "sha256") is True

    def test_wrong_hash_fails(self) -> None:
        """Test functionality: wrong hash fails."""
        data = b"verify me"
        assert verify_hash(data, "0" * 64, "sha256") is False

    def test_different_algorithm(self) -> None:
        """Test functionality: different algorithm."""
        data = b"algorithm test"
        h = hash_sha512(data)
        assert verify_hash(data, h, "sha512") is True

    def test_tampered_data_fails(self) -> None:
        """Test functionality: tampered data fails."""
        data = b"original"
        h = hash_sha256(data)
        assert verify_hash(b"modified", h, "sha256") is False


@pytest.mark.crypto
@pytest.mark.unit
class TestHashAlgorithmEnum:
    """Test suite for HashAlgorithmEnum."""
    def test_values(self) -> None:
        """Test functionality: values."""
        assert HashAlgorithm.SHA256.value == "sha256"
        assert HashAlgorithm.SHA3_256.value == "sha3_256"
        assert HashAlgorithm.SHA512.value == "sha512"
        assert HashAlgorithm.BLAKE2B.value == "blake2b"
        assert HashAlgorithm.MD5.value == "md5"
