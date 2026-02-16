"""Tests for codomyrmex.crypto.graphy.mac."""

from __future__ import annotations

import os

import pytest

from codomyrmex.crypto.exceptions import CryptoError
from codomyrmex.crypto.graphy.mac import (
    compute_cmac,
    compute_hmac_sha256,
    compute_poly1305,
    verify_hmac_sha256,
)


DATA = b"The quick brown fox jumps over the lazy dog"


@pytest.fixture
def hmac_key() -> bytes:
    return os.urandom(32)


@pytest.fixture
def poly1305_key() -> bytes:
    return os.urandom(32)


@pytest.fixture
def aes_key() -> bytes:
    return os.urandom(16)


@pytest.mark.crypto
@pytest.mark.unit
class TestHMACSHA256:
    def test_compute(self, hmac_key: bytes) -> None:
        mac = compute_hmac_sha256(DATA, hmac_key)
        assert isinstance(mac, bytes)
        assert len(mac) == 32

    def test_deterministic(self, hmac_key: bytes) -> None:
        mac1 = compute_hmac_sha256(DATA, hmac_key)
        mac2 = compute_hmac_sha256(DATA, hmac_key)
        assert mac1 == mac2

    def test_different_data_different_mac(self, hmac_key: bytes) -> None:
        mac1 = compute_hmac_sha256(b"data1", hmac_key)
        mac2 = compute_hmac_sha256(b"data2", hmac_key)
        assert mac1 != mac2

    def test_different_keys_different_mac(self) -> None:
        k1 = os.urandom(32)
        k2 = os.urandom(32)
        mac1 = compute_hmac_sha256(DATA, k1)
        mac2 = compute_hmac_sha256(DATA, k2)
        assert mac1 != mac2

    def test_verify_valid(self, hmac_key: bytes) -> None:
        mac = compute_hmac_sha256(DATA, hmac_key)
        assert verify_hmac_sha256(DATA, hmac_key, mac) is True

    def test_verify_tampered_data(self, hmac_key: bytes) -> None:
        mac = compute_hmac_sha256(DATA, hmac_key)
        assert verify_hmac_sha256(b"tampered", hmac_key, mac) is False

    def test_verify_tampered_mac(self, hmac_key: bytes) -> None:
        mac = compute_hmac_sha256(DATA, hmac_key)
        tampered = bytearray(mac)
        tampered[0] ^= 0xFF
        assert verify_hmac_sha256(DATA, hmac_key, bytes(tampered)) is False

    def test_verify_wrong_key(self, hmac_key: bytes) -> None:
        mac = compute_hmac_sha256(DATA, hmac_key)
        wrong_key = os.urandom(32)
        assert verify_hmac_sha256(DATA, wrong_key, mac) is False

    def test_empty_data(self, hmac_key: bytes) -> None:
        mac = compute_hmac_sha256(b"", hmac_key)
        assert verify_hmac_sha256(b"", hmac_key, mac) is True


@pytest.mark.crypto
@pytest.mark.unit
class TestPoly1305:
    def test_compute(self, poly1305_key: bytes) -> None:
        tag = compute_poly1305(DATA, poly1305_key)
        assert isinstance(tag, bytes)
        assert len(tag) == 16

    def test_wrong_key_size(self) -> None:
        with pytest.raises(CryptoError, match="exactly 32-byte key"):
            compute_poly1305(DATA, b"\x00" * 16)

    def test_different_data_different_tags(self, poly1305_key: bytes) -> None:
        tag1 = compute_poly1305(b"msg1", poly1305_key)
        tag2 = compute_poly1305(b"msg2", poly1305_key)
        assert tag1 != tag2


@pytest.mark.crypto
@pytest.mark.unit
class TestCMAC:
    def test_compute_aes128(self, aes_key: bytes) -> None:
        tag = compute_cmac(DATA, aes_key)
        assert isinstance(tag, bytes)
        assert len(tag) == 16

    def test_compute_aes256(self) -> None:
        key = os.urandom(32)
        tag = compute_cmac(DATA, key)
        assert len(tag) == 16

    def test_deterministic(self, aes_key: bytes) -> None:
        tag1 = compute_cmac(DATA, aes_key)
        tag2 = compute_cmac(DATA, aes_key)
        assert tag1 == tag2

    def test_different_data(self, aes_key: bytes) -> None:
        tag1 = compute_cmac(b"data1", aes_key)
        tag2 = compute_cmac(b"data2", aes_key)
        assert tag1 != tag2

    def test_invalid_key_size(self) -> None:
        with pytest.raises(CryptoError):
            compute_cmac(DATA, b"\x00" * 15)  # Invalid AES key size
