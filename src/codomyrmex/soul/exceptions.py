"""Exception hierarchy for the soul module."""

from __future__ import annotations

from codomyrmex.exceptions.base import CodomyrmexError


class SoulError(CodomyrmexError):
    """Base exception for all soul module errors."""


class SoulImportError(SoulError):
    """soul-agent package is not installed.

    Install with: uv sync --extra soul
    """


class SoulMemoryError(SoulError):
    """Failed to read or write SOUL.md or MEMORY.md."""


class SoulProviderError(SoulError):
    """LLM provider call failed."""
