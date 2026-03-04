"""Tests for wallet MCP tools."""

from __future__ import annotations

import tempfile


class TestWalletCreate:
    """Tests for wallet_create MCP tool."""

    def test_create_wallet_success(self):
        from codomyrmex.wallet.mcp_tools import wallet_create

        with tempfile.TemporaryDirectory() as tmpdir:
            result = wallet_create(user_id="test_user_1", storage_path=tmpdir)
            assert result["status"] == "success"
            assert result["user_id"] == "test_user_1"
            assert result["wallet_address"].startswith("0x")

    def test_create_duplicate_wallet(self):
        from codomyrmex.wallet.mcp_tools import wallet_create

        with tempfile.TemporaryDirectory() as tmpdir:
            wallet_create(user_id="dup_user", storage_path=tmpdir)
            result = wallet_create(user_id="dup_user", storage_path=tmpdir)
            # Each call creates a fresh WalletManager, so no duplicate error
            assert result["status"] == "success"


class TestWalletGetAddress:
    """Tests for wallet_get_address MCP tool."""

    def test_get_address_no_wallet(self):
        from codomyrmex.wallet.mcp_tools import wallet_get_address

        with tempfile.TemporaryDirectory() as tmpdir:
            result = wallet_get_address(user_id="unknown_user", storage_path=tmpdir)
            assert result["status"] == "success"
            assert result["has_wallet"] is False
            assert result["wallet_address"] is None

    def test_get_address_callable(self):
        from codomyrmex.wallet.mcp_tools import wallet_get_address

        assert callable(wallet_get_address)


class TestWalletList:
    """Tests for wallet_list MCP tool."""

    def test_list_empty(self):
        from codomyrmex.wallet.mcp_tools import wallet_list

        with tempfile.TemporaryDirectory() as tmpdir:
            result = wallet_list(storage_path=tmpdir)
            assert result["status"] == "success"
            assert result["count"] == 0
            assert result["wallets"] == {}

    def test_list_callable(self):
        from codomyrmex.wallet.mcp_tools import wallet_list

        assert callable(wallet_list)
