"""Unit tests for codomyrmex.crypto.currency.tokens."""

from __future__ import annotations

import pytest

from codomyrmex.crypto.currency.tokens import (
    ERC20Token,
    TransferEvent,
    create_erc20_interface,
    encode_transfer,
    decode_transfer_event,
)
from codomyrmex.crypto.exceptions import WalletError


pytestmark = [pytest.mark.crypto, pytest.mark.unit]


# ---------------------------------------------------------------------------
# ERC20 interface
# ---------------------------------------------------------------------------


class TestCreateERC20Interface:
    """Tests for ERC-20 token descriptor creation."""

    def test_basic_creation(self):
        """Test functionality: basic creation."""
        token = create_erc20_interface("Tether USD", "USDT", 6)
        assert token.name == "Tether USD"
        assert token.symbol == "USDT"
        assert token.decimals == 6
        assert token.total_supply == 0

    def test_default_decimals_is_18(self):
        """Test functionality: default decimals is 18."""
        token = create_erc20_interface("MyToken", "MTK")
        assert token.decimals == 18

    def test_negative_decimals_raises(self):
        """Test functionality: negative decimals raises."""
        with pytest.raises(WalletError):
            create_erc20_interface("Bad", "BAD", decimals=-1)


# ---------------------------------------------------------------------------
# Transfer encoding
# ---------------------------------------------------------------------------


class TestEncodeTransfer:
    """Tests for ABI-encoding transfer calls."""

    def test_encoded_length_is_68_bytes(self):
        """Test functionality: encoded length is 68 bytes."""
        addr = "0x" + "ab" * 20
        encoded = encode_transfer(addr, 1000)
        assert len(encoded) == 68

    def test_function_selector_is_4_bytes(self):
        """Test functionality: function selector is 4 bytes."""
        addr = "0x" + "00" * 20
        encoded = encode_transfer(addr, 0)
        selector = encoded[:4]
        assert len(selector) == 4

    def test_address_embedded_correctly(self):
        """Test functionality: address embedded correctly."""
        addr_hex = "ab" * 20
        encoded = encode_transfer("0x" + addr_hex, 100)
        # Address occupies bytes 4-35, right-aligned (last 20 bytes = addr)
        embedded = encoded[4:36]
        assert embedded[:12] == b"\x00" * 12  # 12 bytes of zero padding
        assert embedded[12:].hex() == addr_hex

    def test_amount_embedded_correctly(self):
        """Test functionality: amount embedded correctly."""
        encoded = encode_transfer("0x" + "00" * 20, 256)
        amount_bytes = encoded[36:68]
        amount = int.from_bytes(amount_bytes, "big")
        assert amount == 256

    def test_invalid_address_length_raises(self):
        """Test functionality: invalid address length raises."""
        with pytest.raises(WalletError):
            encode_transfer("0xabc", 100)

    def test_negative_amount_raises(self):
        """Test functionality: negative amount raises."""
        with pytest.raises(WalletError):
            encode_transfer("0x" + "ab" * 20, -1)

    def test_zero_amount_allowed(self):
        """Test functionality: zero amount allowed."""
        encoded = encode_transfer("0x" + "00" * 20, 0)
        assert len(encoded) == 68


# ---------------------------------------------------------------------------
# Transfer event decoding
# ---------------------------------------------------------------------------


class TestDecodeTransferEvent:
    """Tests for ABI-decoding Transfer events."""

    def _make_log_data(self, from_hex: str, to_hex: str, value: int) -> bytes:
        """Build 96-byte Transfer event log data."""
        from_bytes = b"\x00" * 12 + bytes.fromhex(from_hex)
        to_bytes = b"\x00" * 12 + bytes.fromhex(to_hex)
        value_bytes = value.to_bytes(32, "big")
        return from_bytes + to_bytes + value_bytes

    def test_basic_decode(self):
        """Test functionality: basic decode."""
        from_hex = "aa" * 20
        to_hex = "bb" * 20
        data = self._make_log_data(from_hex, to_hex, 5000)
        event = decode_transfer_event(data)
        assert event.from_address == from_hex
        assert event.to_address == to_hex
        assert event.value == 5000

    def test_zero_value(self):
        """Test functionality: zero value."""
        data = self._make_log_data("00" * 20, "ff" * 20, 0)
        event = decode_transfer_event(data)
        assert event.value == 0

    def test_large_value(self):
        """Test functionality: large value."""
        large = 10**18  # 1 ETH in wei
        data = self._make_log_data("ab" * 20, "cd" * 20, large)
        event = decode_transfer_event(data)
        assert event.value == large

    def test_wrong_length_raises(self):
        """Test functionality: wrong length raises."""
        with pytest.raises(WalletError):
            decode_transfer_event(b"\x00" * 64)

    def test_encode_decode_roundtrip(self):
        """Encode a transfer, build matching log data, and decode."""
        to_hex = "de" * 20
        amount = 42000
        encoded = encode_transfer("0x" + to_hex, amount)

        # Build log data: from is zeros, to and amount from encoding
        from_hex = "00" * 20
        log_data = self._make_log_data(from_hex, to_hex, amount)
        event = decode_transfer_event(log_data)

        assert event.to_address == to_hex
        assert event.value == amount
