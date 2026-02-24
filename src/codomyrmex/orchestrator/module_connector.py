"""Dependency injection module connector.

Wires modules together via a service registry.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from collections.abc import Callable

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


@dataclass
class ServiceBinding:
    """A registered service binding.

    Attributes:
        name: Service name.
        factory: Factory callable.
        singleton: Whether to cache the instance.
        instance: Cached instance.
        tags: Service tags.
    """

    name: str
    factory: Callable[..., Any] | None = None
    singleton: bool = True
    instance: Any = None
    tags: list[str] = field(default_factory=list)


class ModuleConnector:
    """Dependency injection container.

    Usage::

        connector = ModuleConnector()
        connector.register("db", lambda: DatabaseConnection())
        db = connector.resolve("db")
    """

    def __init__(self) -> None:
        """Execute   Init   operations natively."""
        self._bindings: dict[str, ServiceBinding] = {}

    def register(
        self,
        name: str,
        factory: Callable[..., Any],
        singleton: bool = True,
        tags: list[str] | None = None,
    ) -> None:
        """Execute Register operations natively."""
        self._bindings[name] = ServiceBinding(
            name=name, factory=factory, singleton=singleton, tags=tags or [],
        )

    def resolve(self, name: str) -> Any:
        """Execute Resolve operations natively."""
        binding = self._bindings.get(name)
        if binding is None:
            raise KeyError(f"No service registered: {name}")

        if binding.singleton and binding.instance is not None:
            return binding.instance

        if binding.factory is None:
            raise ValueError(f"No factory for service: {name}")

        instance = binding.factory()

        if binding.singleton:
            binding.instance = instance

        return instance

    def has(self, name: str) -> bool:
        """Execute Has operations natively."""
        return name in self._bindings

    def services_by_tag(self, tag: str) -> list[str]:
        """Execute Services By Tag operations natively."""
        return [b.name for b in self._bindings.values() if tag in b.tags]

    @property
    def service_count(self) -> int:
        """Execute Service Count operations natively."""
        return len(self._bindings)

    def service_names(self) -> list[str]:
        """Execute Service Names operations natively."""
        return list(self._bindings.keys())


__all__ = ["ModuleConnector", "ServiceBinding"]
