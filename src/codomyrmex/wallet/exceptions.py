"""Wallet module exceptions."""

from codomyrmex.exceptions import CodomyrmexError


class WalletError(CodomyrmexError):
    """Base exception for wallet operations."""

    pass


class WalletNotFoundError(WalletError):
    """Raised when a wallet does not exist for the given user."""

    pass


class WalletKeyError(WalletError):
    """Raised when key storage or retrieval fails."""

    pass


class RitualError(WalletError):
    """Raised when a recovery ritual operation fails."""

    pass
