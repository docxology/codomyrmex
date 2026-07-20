"""Shared HermesClient factory for MCP tool modules."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from codomyrmex.agents.hermes.hermes_client import HermesClient

_factory_override: Callable[..., HermesClient] | None = None


def _get_client(
    backend: str = "auto",
    model: str = "hermes3",
    timeout: int = 120,
) -> HermesClient:
    """Lazy-instantiate HermesClient with the given configuration."""
    if _factory_override is not None:
        return _factory_override(
            backend=backend,
            model=model,
            timeout=timeout,
        )

    from codomyrmex.agents.hermes.hermes_client import HermesClient

    return HermesClient(
        config={
            "hermes_backend": backend,
            "hermes_model": model,
            "hermes_timeout": timeout,
        }
    )


def _install_client_factory(factory: Callable[..., HermesClient] | None) -> None:
    """Test hook: replace client construction for all MCP tool modules."""
    global _factory_override
    _factory_override = factory
