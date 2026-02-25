"""Tests for codomyrmex.crypto.graphy.kdf."""

from __future__ import annotations

import pytest

from codomyrmex.crypto.graphy.kdf import (
    DerivedKey,
    derive_argon2id,
    derive_hkdf,
    derive_pbkdf2,
    derive_scrypt,
)

FIXED_SALT = b"\x00" * 16
PASSWORD = b"correct horse battery staple"


@pytest.mark.crypto
@pytest.mark.unit
class TestPBKDF2:
    """Test suite for PBKDF2."""
    def test_basic_derivation(self) -> None:
        """Test functionality: basic derivation."""
        result = derive_pbkdf2(PASSWORD, salt=FIXED_SALT, iterations=1000)
        assert isinstance(result, DerivedKey)
        assert len(result.key) == 32
        assert result.salt == FIXED_SALT
        assert result.algorithm == "pbkdf2_sha256"
        assert result.parameters["iterations"] == 1000

    def test_deterministic_with_fixed_salt(self) -> None:
        """Test functionality: deterministic with fixed salt."""
        r1 = derive_pbkdf2(PASSWORD, salt=FIXED_SALT, iterations=1000)
        r2 = derive_pbkdf2(PASSWORD, salt=FIXED_SALT, iterations=1000)
        assert r1.key == r2.key

    def test_different_passwords_different_keys(self) -> None:
        """Test functionality: different passwords different keys."""
        r1 = derive_pbkdf2(b"password1", salt=FIXED_SALT, iterations=1000)
        r2 = derive_pbkdf2(b"password2", salt=FIXED_SALT, iterations=1000)
        assert r1.key != r2.key

    def test_different_salts_different_keys(self) -> None:
        """Test functionality: different salts different keys."""
        r1 = derive_pbkdf2(PASSWORD, salt=b"\x00" * 16, iterations=1000)
        r2 = derive_pbkdf2(PASSWORD, salt=b"\x01" * 16, iterations=1000)
        assert r1.key != r2.key

    def test_different_iterations_different_keys(self) -> None:
        """Test functionality: different iterations different keys."""
        r1 = derive_pbkdf2(PASSWORD, salt=FIXED_SALT, iterations=1000)
        r2 = derive_pbkdf2(PASSWORD, salt=FIXED_SALT, iterations=2000)
        assert r1.key != r2.key

    def test_auto_salt_generation(self) -> None:
        """Test functionality: auto salt generation."""
        result = derive_pbkdf2(PASSWORD, iterations=1000)
        assert len(result.salt) == 16
        # Salt should be random each time
        result2 = derive_pbkdf2(PASSWORD, iterations=1000)
        assert result.salt != result2.salt

    def test_custom_key_length(self) -> None:
        """Test functionality: custom key length."""
        result = derive_pbkdf2(PASSWORD, salt=FIXED_SALT, iterations=1000, key_length=64)
        assert len(result.key) == 64
        assert result.parameters["key_length"] == 64


@pytest.mark.crypto
@pytest.mark.unit
class TestScrypt:
    """Test suite for Scrypt."""
    def test_basic_derivation(self) -> None:
        """Test functionality: basic derivation."""
        result = derive_scrypt(PASSWORD, salt=FIXED_SALT, n=2**14, r=8, p=1)
        assert isinstance(result, DerivedKey)
        assert len(result.key) == 32
        assert result.algorithm == "scrypt"

    def test_deterministic_with_fixed_salt(self) -> None:
        """Test functionality: deterministic with fixed salt."""
        r1 = derive_scrypt(PASSWORD, salt=FIXED_SALT, n=2**14, r=8, p=1)
        r2 = derive_scrypt(PASSWORD, salt=FIXED_SALT, n=2**14, r=8, p=1)
        assert r1.key == r2.key

    def test_different_passwords_different_keys(self) -> None:
        """Test functionality: different passwords different keys."""
        r1 = derive_scrypt(b"pw1", salt=FIXED_SALT, n=2**14, r=8, p=1)
        r2 = derive_scrypt(b"pw2", salt=FIXED_SALT, n=2**14, r=8, p=1)
        assert r1.key != r2.key

    def test_different_params_different_keys(self) -> None:
        """Test functionality: different params different keys."""
        r1 = derive_scrypt(PASSWORD, salt=FIXED_SALT, n=2**14, r=8, p=1)
        r2 = derive_scrypt(PASSWORD, salt=FIXED_SALT, n=2**15, r=8, p=1)
        assert r1.key != r2.key

    def test_auto_salt(self) -> None:
        """Test functionality: auto salt."""
        result = derive_scrypt(PASSWORD, n=2**14, r=8, p=1)
        assert len(result.salt) == 16


@pytest.mark.crypto
@pytest.mark.unit
class TestArgon2id:
    """Test suite for Argon2id."""
    def test_basic_derivation(self) -> None:
        """Test functionality: basic derivation."""
        result = derive_argon2id(PASSWORD, salt=FIXED_SALT)
        assert isinstance(result, DerivedKey)
        assert len(result.key) == 32
        # Algorithm is either argon2id or argon2id_fallback_scrypt
        assert result.algorithm.startswith("argon2id")

    def test_deterministic_with_fixed_salt(self) -> None:
        """Test functionality: deterministic with fixed salt."""
        r1 = derive_argon2id(PASSWORD, salt=FIXED_SALT)
        r2 = derive_argon2id(PASSWORD, salt=FIXED_SALT)
        assert r1.key == r2.key

    def test_different_passwords_different_keys(self) -> None:
        """Test functionality: different passwords different keys."""
        r1 = derive_argon2id(b"pw1", salt=FIXED_SALT)
        r2 = derive_argon2id(b"pw2", salt=FIXED_SALT)
        assert r1.key != r2.key

    def test_auto_salt(self) -> None:
        """Test functionality: auto salt."""
        result = derive_argon2id(PASSWORD)
        assert len(result.salt) == 16


@pytest.mark.crypto
@pytest.mark.unit
class TestHKDF:
    """Test suite for HKDF."""
    def test_basic_derivation(self) -> None:
        """Test functionality: basic derivation."""
        ikm = b"\x0b" * 32
        info = b"test info"
        key = derive_hkdf(ikm, info=info, salt=FIXED_SALT)
        assert isinstance(key, bytes)
        assert len(key) == 32

    def test_deterministic(self) -> None:
        """Test functionality: deterministic."""
        ikm = b"\x0b" * 32
        info = b"context"
        k1 = derive_hkdf(ikm, info=info, salt=FIXED_SALT)
        k2 = derive_hkdf(ikm, info=info, salt=FIXED_SALT)
        assert k1 == k2

    def test_different_info_different_keys(self) -> None:
        """Test functionality: different info different keys."""
        ikm = b"\x0b" * 32
        k1 = derive_hkdf(ikm, info=b"context-a", salt=FIXED_SALT)
        k2 = derive_hkdf(ikm, info=b"context-b", salt=FIXED_SALT)
        assert k1 != k2

    def test_custom_length(self) -> None:
        """Test functionality: custom length."""
        key = derive_hkdf(b"\x0b" * 32, info=b"info", length=64)
        assert len(key) == 64

    def test_no_salt(self) -> None:
        """Test functionality: no salt."""
        key = derive_hkdf(b"\x0b" * 32, info=b"info")
        assert len(key) == 32
