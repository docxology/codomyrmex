"""Backward-compatible shim — implementation in ``client_pkg/``."""

from codomyrmex.agents.hermes.client_pkg import (
    AUTO_HEAL_ALLOWLIST,
    AutoRetryException,
    HermesClient,
    HermesError,
)

__all__ = ["AUTO_HEAL_ALLOWLIST", "AutoRetryException", "HermesClient", "HermesError"]
