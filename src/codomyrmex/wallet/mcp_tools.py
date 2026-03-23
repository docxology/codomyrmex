"""MCP tool definitions for the wallet module.

Exposes wallet creation, listing, and status checks as MCP tools.
Key management operations use the encryption module's KeyManager.
"""

from __future__ import annotations

from typing import Any

from codomyrmex.model_context_protocol.decorators import mcp_tool


def _get_wallet_manager(storage_path: str | None = None):
    """Lazy import and create a WalletManager."""
    from pathlib import Path

    from codomyrmex.wallet.core import WalletManager

    path = Path(storage_path) if storage_path else None
    return WalletManager(storage_path=path)


@mcp_tool(
    category="wallet",
    description="Create a new self-custody wallet for a user with secure key storage.",
)
def wallet_create(
    user_id: str,
    storage_path: str | None = None,
) -> dict[str, Any]:
    """Create a new wallet for the specified user.

    Args:
        user_id: Unique identifier for the wallet owner.
        storage_path: Optional directory for key storage.

    Returns:
        dict with keys: status, user_id, wallet_address
    """
    try:
        mgr = _get_wallet_manager(storage_path)
        address = mgr.create_wallet(user_id)
        return {
            "status": "success",
            "user_id": user_id,
            "wallet_address": address,
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="wallet",
    description="Check if a user has a wallet and return its address.",
)
def wallet_get_address(
    user_id: str,
    storage_path: str | None = None,
) -> dict[str, Any]:
    """Get a user's wallet address if it exists.

    Args:
        user_id: The user identifier.
        storage_path: Optional directory for key storage.

    Returns:
        dict with keys: status, user_id, has_wallet, wallet_address
    """
    try:
        mgr = _get_wallet_manager(storage_path)
        has = mgr.has_wallet(user_id)
        address = mgr.get_wallet_address(user_id)
        return {
            "status": "success",
            "user_id": user_id,
            "has_wallet": has,
            "wallet_address": address,
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="wallet",
    description="list all registered wallets mapping user IDs to addresses.",
)
def wallet_list(
    storage_path: str | None = None,
) -> dict[str, Any]:
    """list all registered wallets.

    Args:
        storage_path: Optional directory for key storage.

    Returns:
        dict with keys: status, wallets, count
    """
    try:
        mgr = _get_wallet_manager(storage_path)
        wallets = mgr.list_wallets()
        return {
            "status": "success",
            "wallets": wallets,
            "count": len(wallets),
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}
