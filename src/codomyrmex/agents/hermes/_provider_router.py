"""Backward-compatible shim — implementation in ``provider_router_pkg/``."""

from codomyrmex.agents.hermes.provider_router_pkg import (
    ContextCompressor,
    MCPBridgeManager,
    ModelContextRegistry,
    ProviderRouter,
    UserModel,
    get_model_context_registry,
)

__all__ = [
    "ContextCompressor",
    "MCPBridgeManager",
    "ModelContextRegistry",
    "ProviderRouter",
    "UserModel",
    "get_model_context_registry",
]
