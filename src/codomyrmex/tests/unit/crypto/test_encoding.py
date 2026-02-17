"""Tests for the crypto encoding submodule.

Covers Base64, Base58, Base32, hex, and PEM encode/decode round-trips
plus edge cases and known test vectors.
"""

from __future__ import annotations

import pytest

from codomyrmex.crypto.encoding import (
    decode_base32,
    decode_base58,
    decode_base64,
    decode_hex,
    decode_pem,
    encode_base32,
    encode_base58,
    encode_base64,
    encode_hex,
    encode_pem,
    identify_pem_type,
    is_valid_hex,
)
from codomyrmex.crypto.exceptions import EncodingError


# -------------------------------------------------------------------------
# Base64
# -------------------------------------------------------------------------

@pytest.mark.unit
@pytest.mark.crypto
class TestBase64:
    """Base64 encode/decode tests."""

    def test_roundtrip(self) -> None:
        data = b"Hello, World!"
        assert decode_base64(encode_base64(data)) == data

    def test_empty(self) -> None:
        assert encode_base64(b"") == ""
        assert decode_base64("") == b""

    def test_binary_data(self) -> None:
        data = bytes(range(256))
        assert decode_base64(encode_base64(data)) == data

    def test_known_vector(self) -> None:
        # RFC 4648 test vectors
        assert encode_base64(b"f") == "Zg=="
        assert encode_base64(b"fo") == "Zm8="
        assert encode_base64(b"foo") == "Zm9v"
        assert encode_base64(b"foob") == "Zm9vYg=="
        assert encode_base64(b"fooba") == "Zm9vYmE="
        assert encode_base64(b"foobar") == "Zm9vYmFy"

    def test_decode_invalid_raises(self) -> None:
        with pytest.raises(EncodingError):
            decode_base64("!!!invalid!!!")


# -------------------------------------------------------------------------
# Base58 (Bitcoin alphabet)
# -------------------------------------------------------------------------

@pytest.mark.unit
@pytest.mark.crypto
class TestBase58:
    """Base58 encode/decode tests."""

    def test_empty_bytes(self) -> None:
        assert encode_base58(b"") == ""
        assert decode_base58("") == b""

    def test_single_zero_byte(self) -> None:
        # A leading 0x00 byte encodes as '1'
        assert encode_base58(b"\x00") == "1"
        assert decode_base58("1") == b"\x00"

    def test_multiple_leading_zeros(self) -> None:
        assert encode_base58(b"\x00\x00\x00") == "111"
        assert decode_base58("111") == b"\x00\x00\x00"

    def test_known_vector_hello(self) -> None:
        # "Hello World" in Base58 is "JxF12TrwUP45BMd"
        encoded = encode_base58(b"Hello World")
        assert encoded == "JxF12TrwUP45BMd"
        assert decode_base58(encoded) == b"Hello World"

    def test_roundtrip_binary(self) -> None:
        data = bytes(range(1, 256))
        assert decode_base58(encode_base58(data)) == data

    def test_roundtrip_with_leading_zeros(self) -> None:
        data = b"\x00\x00" + b"test data"
        assert decode_base58(encode_base58(data)) == data

    def test_decode_invalid_char_raises(self) -> None:
        with pytest.raises(EncodingError, match="Invalid Base58 character"):
            decode_base58("0OIl")  # These chars are not in the Bitcoin alphabet


# -------------------------------------------------------------------------
# Base32
# -------------------------------------------------------------------------

@pytest.mark.unit
@pytest.mark.crypto
class TestBase32:
    """Base32 encode/decode tests."""

    def test_roundtrip(self) -> None:
        data = b"Hello, World!"
        assert decode_base32(encode_base32(data)) == data

    def test_empty(self) -> None:
        assert encode_base32(b"") == ""
        assert decode_base32("") == b""

    def test_known_vector(self) -> None:
        # RFC 4648 test vectors
        assert encode_base32(b"f") == "MY======"
        assert encode_base32(b"fo") == "MZXQ===="
        assert encode_base32(b"foo") == "MZXW6==="
        assert encode_base32(b"foob") == "MZXW6YQ="
        assert encode_base32(b"fooba") == "MZXW6YTB"
        assert encode_base32(b"foobar") == "MZXW6YTBOI======"

    def test_decode_invalid_raises(self) -> None:
        with pytest.raises(EncodingError):
            decode_base32("!!!invalid!!!")


# -------------------------------------------------------------------------
# Hex
# -------------------------------------------------------------------------

@pytest.mark.unit
@pytest.mark.crypto
class TestHex:
    """Hexadecimal encode/decode tests."""

    def test_roundtrip(self) -> None:
        data = b"\xde\xad\xbe\xef"
        assert decode_hex(encode_hex(data)) == data

    def test_empty(self) -> None:
        assert encode_hex(b"") == ""
        assert decode_hex("") == b""

    def test_known_vector(self) -> None:
        assert encode_hex(b"\x00\xff") == "00ff"

    def test_decode_uppercase(self) -> None:
        assert decode_hex("DEADBEEF") == b"\xde\xad\xbe\xef"

    def test_decode_invalid_raises(self) -> None:
        with pytest.raises(EncodingError):
            decode_hex("xyz")

    def test_is_valid_hex_true(self) -> None:
        assert is_valid_hex("deadbeef") is True
        assert is_valid_hex("ABCDEF0123456789") is True
        assert is_valid_hex("") is True  # empty is technically valid hex

    def test_is_valid_hex_false(self) -> None:
        assert is_valid_hex("xyz") is False
        assert is_valid_hex("0xdead") is False  # prefix not valid for fromhex
        assert is_valid_hex("deadbee") is False  # odd length


# -------------------------------------------------------------------------
# PEM
# -------------------------------------------------------------------------

@pytest.mark.unit
@pytest.mark.crypto
class TestPEM:
    """PEM encode/decode/identify tests."""

    def test_roundtrip(self) -> None:
        data = b"This is test key material"
        label = "RSA PRIVATE KEY"
        pem = encode_pem(data, label)
        assert decode_pem(pem) == data

    def test_encode_format(self) -> None:
        data = b"short"
        pem = encode_pem(data, "CERTIFICATE")
        assert pem.startswith("-----BEGIN CERTIFICATE-----\n")
        assert pem.endswith("-----END CERTIFICATE-----\n")

    def test_line_wrapping(self) -> None:
        # Use data that produces > 64 chars of Base64
        data = b"A" * 100
        pem = encode_pem(data, "TEST")
        lines = pem.strip().split("\n")
        # Middle lines (not header/footer) should be <= 64 chars
        for line in lines[1:-1]:
            assert len(line) <= 64

    def test_identify_pem_type(self) -> None:
        pem = encode_pem(b"data", "EC PRIVATE KEY")
        assert identify_pem_type(pem) == "EC PRIVATE KEY"

    def test_identify_certificate(self) -> None:
        pem = encode_pem(b"cert data", "CERTIFICATE")
        assert identify_pem_type(pem) == "CERTIFICATE"

    def test_decode_no_markers_raises(self) -> None:
        with pytest.raises(EncodingError, match="missing BEGIN or END"):
            decode_pem("not a PEM string")

    def test_identify_no_header_raises(self) -> None:
        with pytest.raises(EncodingError, match="No PEM header"):
            identify_pem_type("just some text")

    def test_roundtrip_binary(self) -> None:
        data = bytes(range(256))
        pem = encode_pem(data, "BINARY DATA")
        assert decode_pem(pem) == data
