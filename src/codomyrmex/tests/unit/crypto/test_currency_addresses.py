"""Unit tests for codomyrmex.crypto.currency.addresses."""

from __future__ import annotations

import pytest
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization

from codomyrmex.crypto.currency.addresses import (
    generate_bitcoin_address,
    validate_bitcoin_address,
    generate_ethereum_address,
    validate_ethereum_address,
    checksum_ethereum_address,
)
from codomyrmex.crypto.exceptions import WalletError


pytestmark = [pytest.mark.crypto, pytest.mark.unit]


@pytest.fixture()
def secp256k1_keys():
    """Generate a secp256k1 key pair and return compressed/uncompressed public keys."""
    private_key = ec.generate_private_key(ec.SECP256K1())
    public_key = private_key.public_key()
    compressed = public_key.public_bytes(
        serialization.Encoding.X962,
        serialization.PublicFormat.CompressedPoint,
    )
    uncompressed = public_key.public_bytes(
        serialization.Encoding.X962,
        serialization.PublicFormat.UncompressedPoint,
    )
    return compressed, uncompressed


# ---------------------------------------------------------------------------
# Bitcoin address generation
# ---------------------------------------------------------------------------


class TestBitcoinAddress:
    """Tests for Bitcoin P2PKH address generation and validation."""

    def test_mainnet_address_starts_with_1(self, secp256k1_keys):
        compressed, _ = secp256k1_keys
        addr = generate_bitcoin_address(compressed, network="mainnet")
        assert addr.startswith("1"), f"Mainnet address should start with '1', got {addr}"

    def test_testnet_address_starts_with_m_or_n(self, secp256k1_keys):
        compressed, _ = secp256k1_keys
        addr = generate_bitcoin_address(compressed, network="testnet")
        assert addr[0] in ("m", "n"), f"Testnet address should start with 'm' or 'n', got {addr}"

    def test_address_length_reasonable(self, secp256k1_keys):
        compressed, _ = secp256k1_keys
        addr = generate_bitcoin_address(compressed)
        # Bitcoin addresses are typically 25-34 characters
        assert 25 <= len(addr) <= 34, f"Unexpected address length: {len(addr)}"

    def test_generated_address_validates(self, secp256k1_keys):
        compressed, _ = secp256k1_keys
        addr = generate_bitcoin_address(compressed)
        assert validate_bitcoin_address(addr) is True

    def test_unknown_network_raises(self, secp256k1_keys):
        compressed, _ = secp256k1_keys
        with pytest.raises(WalletError):
            generate_bitcoin_address(compressed, network="dogecoin")

    def test_tampered_address_fails_validation(self, secp256k1_keys):
        compressed, _ = secp256k1_keys
        addr = generate_bitcoin_address(compressed)
        # Flip a character in the middle
        chars = list(addr)
        mid = len(chars) // 2
        chars[mid] = "A" if chars[mid] != "A" else "B"
        tampered = "".join(chars)
        assert validate_bitcoin_address(tampered) is False

    def test_empty_string_fails_validation(self):
        assert validate_bitcoin_address("") is False

    def test_random_string_fails_validation(self):
        assert validate_bitcoin_address("not_a_bitcoin_address") is False


# ---------------------------------------------------------------------------
# Ethereum address generation
# ---------------------------------------------------------------------------


class TestEthereumAddress:
    """Tests for Ethereum address generation and EIP-55 checksum."""

    def test_address_starts_with_0x(self, secp256k1_keys):
        _, uncompressed = secp256k1_keys
        addr = generate_ethereum_address(uncompressed)
        assert addr.startswith("0x")

    def test_address_is_42_chars(self, secp256k1_keys):
        _, uncompressed = secp256k1_keys
        addr = generate_ethereum_address(uncompressed)
        assert len(addr) == 42

    def test_generated_address_validates(self, secp256k1_keys):
        _, uncompressed = secp256k1_keys
        addr = generate_ethereum_address(uncompressed)
        assert validate_ethereum_address(addr) is True

    def test_stripped_64_byte_key_accepted(self, secp256k1_keys):
        _, uncompressed = secp256k1_keys
        # Strip the 0x04 prefix
        stripped = uncompressed[1:]
        assert len(stripped) == 64
        addr = generate_ethereum_address(stripped)
        assert validate_ethereum_address(addr)

    def test_wrong_key_length_raises(self):
        with pytest.raises(WalletError):
            generate_ethereum_address(b"\x00" * 32)


class TestEthereumValidation:
    """Tests for Ethereum address validation."""

    def test_all_lowercase_valid(self):
        addr = "0x" + "a" * 40
        assert validate_ethereum_address(addr) is True

    def test_all_uppercase_valid(self):
        addr = "0x" + "A" * 40
        assert validate_ethereum_address(addr) is True

    def test_no_0x_prefix_invalid(self):
        assert validate_ethereum_address("a" * 40) is False

    def test_short_address_invalid(self):
        assert validate_ethereum_address("0x" + "a" * 39) is False

    def test_long_address_invalid(self):
        assert validate_ethereum_address("0x" + "a" * 41) is False

    def test_non_hex_invalid(self):
        assert validate_ethereum_address("0x" + "g" * 40) is False


class TestChecksumEthereumAddress:
    """Tests for EIP-55 checksum encoding."""

    def test_produces_0x_prefix(self):
        addr = checksum_ethereum_address("0x" + "ab" * 20)
        assert addr.startswith("0x")
        assert len(addr) == 42

    def test_idempotent(self):
        raw = "0x" + "ab" * 20
        first = checksum_ethereum_address(raw)
        second = checksum_ethereum_address(first)
        assert first == second

    def test_checksummed_validates(self):
        raw = "0x" + "de" * 20
        checksummed = checksum_ethereum_address(raw)
        assert validate_ethereum_address(checksummed)

    def test_invalid_length_raises(self):
        with pytest.raises(WalletError):
            checksum_ethereum_address("0xabc")
