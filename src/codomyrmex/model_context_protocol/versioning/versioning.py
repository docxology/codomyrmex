"""API versioning and deprecation support.

Provides semantic versioning for MCP tools, deprecation
decorators, and version compatibility checking.
"""

from __future__ import annotations

import functools
import warnings
from collections.abc import Callable
from dataclasses import dataclass, field


@dataclass(frozen=True, order=True)
class APIVersion:
    """Semantic version for API endpoints.

    Attributes:
        major: Breaking changes.
        minor: Backward-compatible additions.
        patch: Bug fixes.
    """

    major: int = 1
    minor: int = 0
    patch: int = 0

    def __str__(self) -> str:
        """str ."""
        return f"v{self.major}.{self.minor}.{self.patch}"

    @classmethod
    def parse(cls, version_str: str) -> APIVersion:
        """Parse a version string like 'v1.2.3' or '1.2.3'."""
        cleaned = version_str.lstrip("v")
        parts = cleaned.split(".")
        return cls(
            major=int(parts[0]),
            minor=int(parts[1]) if len(parts) > 1 else 0,
            patch=int(parts[2]) if len(parts) > 2 else 0,
        )

    def is_compatible(self, other: APIVersion) -> bool:
        """Check if other version is backward-compatible."""
        return self.major == other.major and other >= self


@dataclass
class DeprecationInfo:
    """Deprecation metadata for an API element.

    Attributes:
        since: Version when deprecated.
        removal: Planned removal version.
        replacement: Suggested replacement.
        message: Human-readable deprecation message.
    """

    since: str = ""
    removal: str = ""
    replacement: str = ""
    message: str = ""


@dataclass
class VersionedTool:
    """Metadata for a versioned API tool.

    Attributes:
        name: Tool name.
        version: Current version.
        deprecated: Whether this version is deprecated.
        deprecation: Deprecation details (if applicable).
        introduced: Version when first introduced.
    """

    name: str
    version: APIVersion = field(default_factory=APIVersion)
    deprecated: bool = False
    deprecation: DeprecationInfo | None = None
    introduced: APIVersion = field(default_factory=APIVersion)


def versioned(version: str = "1.0.0", introduced: str = "1.0.0"):
    """Decorator to add version metadata to a function.

    Args:
        version: Current API version string.
        introduced: Version when the function was introduced.
    """
    def decorator(func: Callable) -> Callable:
        """decorator ."""
        func._api_version = APIVersion.parse(version)
        func._api_introduced = APIVersion.parse(introduced)
        func._api_deprecated = False

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            """wrapper ."""
            return func(*args, **kwargs)

        wrapper._api_version = func._api_version
        wrapper._api_introduced = func._api_introduced
        wrapper._api_deprecated = func._api_deprecated
        return wrapper

    return decorator


def deprecated(since: str = "", removal: str = "", replacement: str = "", message: str = ""):
    """Decorator to mark a function as deprecated.

    Emits a DeprecationWarning when called.

    Args:
        since: Version when deprecated.
        removal: Planned removal version.
        replacement: Suggested replacement.
        message: Custom deprecation message.
    """
    def decorator(func: Callable) -> Callable:
        """decorator ."""
        info = DeprecationInfo(
            since=since,
            removal=removal,
            replacement=replacement,
            message=message or f"{func.__name__} is deprecated since {since}",
        )
        func._deprecation_info = info
        func._api_deprecated = True

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            """wrapper ."""
            msg = info.message
            if info.replacement:
                msg += f". Use {info.replacement} instead"
            if info.removal:
                msg += f". Will be removed in {info.removal}"
            warnings.warn(msg, DeprecationWarning, stacklevel=2)
            return func(*args, **kwargs)

        wrapper._deprecation_info = info
        wrapper._api_deprecated = True
        if hasattr(func, "_api_version"):
            wrapper._api_version = func._api_version
        return wrapper

    return decorator


class CompatibilityMatrix:
    """Track version compatibility between components.

    Example::

        matrix = CompatibilityMatrix()
        matrix.add_compatible("tool_a", "v1.0", "v1.2")
        assert matrix.is_compatible("tool_a", "v1.0", "v1.2")
    """

    def __init__(self) -> None:
        """Initialize this instance."""
        self._compat: dict[str, list[tuple[APIVersion, APIVersion]]] = {}

    def add_compatible(self, tool: str, from_ver: str, to_ver: str) -> None:
        """Record that two versions are compatible."""
        if tool not in self._compat:
            self._compat[tool] = []
        self._compat[tool].append((
            APIVersion.parse(from_ver),
            APIVersion.parse(to_ver),
        ))

    def is_compatible(self, tool: str, ver_a: str, ver_b: str) -> bool:
        """Check if two versions are compatible."""
        a = APIVersion.parse(ver_a)
        b = APIVersion.parse(ver_b)

        # Same major version = compatible by default
        if a.major == b.major:
            return True

        # Check explicit entries
        pairs = self._compat.get(tool, [])
        for from_v, to_v in pairs:
            if (from_v == a and to_v == b) or (from_v == b and to_v == a):
                return True

        return False


__all__ = [
    "APIVersion",
    "CompatibilityMatrix",
    "DeprecationInfo",
    "VersionedTool",
    "deprecated",
    "versioned",
]
