"""Backward-compatibility shim generator.

Auto-generates compatibility shims that forward old API calls
to their renamed or reorganized replacements.
"""

from __future__ import annotations

import functools
from dataclasses import dataclass, field
from typing import Any
from collections.abc import Callable


@dataclass
class ShimMapping:
    """A mapping from old API to new API.

    Attributes:
        old_name: Old function/tool name.
        new_name: New function/tool name.
        param_renames: Old param → new param mapping.
        version_from: Old version.
        version_to: New version.
    """

    old_name: str
    new_name: str
    param_renames: dict[str, str] = field(default_factory=dict)
    version_from: str = ""
    version_to: str = ""


class CompatShimGenerator:
    """Generate backward-compatibility shims.

    Creates wrapper functions that translate old API calls
    to new API signatures.

    Example::

        shim_gen = CompatShimGenerator()
        shim_gen.add_mapping(ShimMapping(
            old_name="search",
            new_name="search_code",
            param_renames={"q": "query"},
        ))
        shim = shim_gen.create_shim("search", target_fn=search_code)
    """

    def __init__(self) -> None:
        """Execute   Init   operations natively."""
        self._mappings: dict[str, ShimMapping] = {}
        self._shims: dict[str, Callable] = {}

    @property
    def mapping_count(self) -> int:
        """Execute Mapping Count operations natively."""
        return len(self._mappings)

    def add_mapping(self, mapping: ShimMapping) -> None:
        """Register a compatibility mapping."""
        self._mappings[mapping.old_name] = mapping

    def get_mapping(self, old_name: str) -> ShimMapping | None:
        """Look up a mapping by old name."""
        return self._mappings.get(old_name)

    def create_shim(
        self,
        old_name: str,
        target_fn: Callable,
    ) -> Callable:
        """Create a shim function that forwards to the new API.

        Args:
            old_name: Old function name.
            target_fn: New function to call.

        Returns:
            A wrapper that translates parameters.
        """
        mapping = self._mappings.get(old_name)
        if mapping is None:
            # No mapping → direct forward
            return target_fn

        @functools.wraps(target_fn)
        def shim(*args, **kwargs):
            """Execute Shim operations natively."""
            # Rename parameters
            translated_kwargs = {}
            for k, v in kwargs.items():
                new_key = mapping.param_renames.get(k, k)
                translated_kwargs[new_key] = v
            return target_fn(*args, **translated_kwargs)

        shim.__name__ = old_name
        shim.__qualname__ = old_name
        shim._is_compat_shim = True
        shim._shim_mapping = mapping
        self._shims[old_name] = shim
        return shim

    def get_shim(self, old_name: str) -> Callable | None:
        """Get a previously created shim."""
        return self._shims.get(old_name)

    def list_shims(self) -> list[str]:
        """List all created shim names."""
        return sorted(self._shims.keys())

    def translate_params(self, old_name: str, kwargs: dict[str, Any]) -> dict[str, Any]:
        """Translate parameters from old to new naming.

        Args:
            old_name: Old function name.
            kwargs: Parameters with old names.

        Returns:
            Parameters with new names.
        """
        mapping = self._mappings.get(old_name)
        if mapping is None:
            return kwargs

        translated = {}
        for k, v in kwargs.items():
            new_key = mapping.param_renames.get(k, k)
            translated[new_key] = v
        return translated


__all__ = ["CompatShimGenerator", "ShimMapping"]
