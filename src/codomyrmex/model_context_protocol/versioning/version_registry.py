"""Version registry for MCP tools.

Maintains a registry of all versioned tools, their deprecation
status, and generates migration guides.
"""

from __future__ import annotations

from dataclasses import dataclass

from .versioning import (
    APIVersion,
    DeprecationInfo,
    VersionedTool,
)


@dataclass
class MigrationStep:
    """A single migration step.

    Attributes:
        tool_name: Affected tool.
        from_version: Old version.
        to_version: New version.
        action: What to do (rename, update_params, etc.).
        details: Human-readable migration instructions.
    """

    tool_name: str
    from_version: str
    to_version: str
    action: str = ""
    details: str = ""


class VersionRegistry:
    """Registry of all versioned MCP tools.

    Tracks tool versions, deprecation status, and generates
    migration guides for version transitions.

    Example::

        registry = VersionRegistry()
        registry.register("search_code", version="1.0.0")
        registry.deprecate("search_code", since="1.0.0", removal="2.0.0")
    """

    def __init__(self) -> None:
        """Initialize this instance."""
        self._tools: dict[str, VersionedTool] = {}
        self._history: dict[str, list[VersionedTool]] = {}
        self._migrations: list[MigrationStep] = []

    @property
    def tool_count(self) -> int:
        """tool Count ."""
        return len(self._tools)

    def register(
        self,
        name: str,
        version: str = "1.0.0",
        introduced: str = "",
    ) -> None:
        """Register a versioned tool.

        Args:
            name: Tool name.
            version: Current version.
            introduced: Version when introduced.
        """
        tool = VersionedTool(
            name=name,
            version=APIVersion.parse(version),
            introduced=APIVersion.parse(introduced or version),
        )
        self._tools[name] = tool
        if name not in self._history:
            self._history[name] = []
        self._history[name].append(tool)

    def deprecate(
        self,
        name: str,
        since: str = "",
        removal: str = "",
        replacement: str = "",
    ) -> bool:
        """Mark a tool as deprecated.

        Args:
            name: Tool to deprecate.
            since: Deprecation version.
            removal: Planned removal version.
            replacement: Suggested replacement.

        Returns:
            True if tool found and deprecated.
        """
        tool = self._tools.get(name)
        if tool is None:
            return False

        tool.deprecated = True
        tool.deprecation = DeprecationInfo(
            since=since,
            removal=removal,
            replacement=replacement,
        )
        return True

    def is_deprecated(self, name: str) -> bool:
        """Check if a tool is deprecated."""
        tool = self._tools.get(name)
        return tool.deprecated if tool else False

    def get_tool(self, name: str) -> VersionedTool | None:
        """Get a tool by name."""
        return self._tools.get(name)

    def list_versions(self, name: str) -> list[APIVersion]:
        """List all known versions of a tool."""
        return [t.version for t in self._history.get(name, [])]

    def list_deprecated(self) -> list[str]:
        """List all deprecated tool names."""
        return [name for name, tool in self._tools.items() if tool.deprecated]

    def list_all(self) -> list[VersionedTool]:
        """List all registered tools."""
        return list(self._tools.values())

    def add_migration(
        self,
        tool_name: str,
        from_version: str,
        to_version: str,
        action: str,
        details: str = "",
    ) -> None:
        """Record a migration step."""
        self._migrations.append(MigrationStep(
            tool_name=tool_name,
            from_version=from_version,
            to_version=to_version,
            action=action,
            details=details,
        ))

    def migration_guide(self, from_ver: str = "", to_ver: str = "") -> list[MigrationStep]:
        """Get migration steps between versions."""
        if not from_ver and not to_ver:
            return list(self._migrations)

        filtered = []
        for step in self._migrations:
            if from_ver and step.from_version != from_ver:
                continue
            if to_ver and step.to_version != to_ver:
                continue
            filtered.append(step)
        return filtered

    def to_markdown(self) -> str:
        """Generate a markdown summary of the registry."""
        lines = ["# API Version Registry", ""]
        for tool in sorted(self._tools.values(), key=lambda t: t.name):
            status = "⚠️ DEPRECATED" if tool.deprecated else "✅"
            lines.append(f"- **{tool.name}** {tool.version} {status}")
            if tool.deprecated and tool.deprecation:
                dep = tool.deprecation
                if dep.replacement:
                    lines.append(f"  - Use `{dep.replacement}` instead")
                if dep.removal:
                    lines.append(f"  - Removal planned: {dep.removal}")
        return "\n".join(lines)


__all__ = ["MigrationStep", "VersionRegistry"]
