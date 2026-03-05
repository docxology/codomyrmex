"""
Lifecycle scope management for dependency injection.

Provides the Scope enum defining object lifetimes.
ScopeContext lives in container.py to avoid an import cycle
(ScopeContext is a thin view onto Container and belongs there).

Scopes:
    SINGLETON - One instance for the entire container lifetime.
    TRANSIENT - A new instance on every resolve call.
    SCOPED    - One instance per ScopeContext; different contexts get different instances.
"""

from __future__ import annotations

import enum


class Scope(enum.Enum):
    """Defines the lifetime strategy for a registered service."""

    SINGLETON = "singleton"
    TRANSIENT = "transient"
    SCOPED = "scoped"

    @classmethod
    def from_string(cls, value: str) -> Scope:
        """Convert a string to a Scope enum member.

        Args:
            value: One of "singleton", "transient", or "scoped".

        Returns:
            The corresponding Scope enum member.

        Raises:
            ValueError: If the string does not match any scope.
        """
        try:
            return cls(value.lower())
        except ValueError:
            valid = ", ".join(s.value for s in cls)
            raise ValueError(
                f"Invalid scope '{value}'. Valid scopes: {valid}"
            ) from None
