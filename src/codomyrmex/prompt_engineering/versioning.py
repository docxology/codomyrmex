"""
Prompt Version Tracking

Provides PromptVersion dataclass and VersionManager for tracking,
comparing, and managing prompt template versions over time.
"""

from __future__ import annotations

import difflib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

try:
    from codomyrmex.schemas import Result, ResultStatus
except ImportError:
    Result = None
    ResultStatus = None

from .templates import PromptTemplate


@dataclass
class PromptVersion:
    """
    A versioned snapshot of a prompt template.

    Captures the template content at a specific point in time along
    with a changelog describing what changed.
    """

    version: str
    template: PromptTemplate
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    changelog: str = ""
    author: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert version to dictionary representation."""
        return {
            "version": self.version,
            "template": self.template.to_dict(),
            "created_at": self.created_at.isoformat(),
            "changelog": self.changelog,
            "author": self.author,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PromptVersion":
        """Create a PromptVersion from a dictionary."""
        return cls(
            version=data["version"],
            template=PromptTemplate.from_dict(data["template"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            changelog=data.get("changelog", ""),
            author=data.get("author", ""),
            metadata=data.get("metadata", {}),
        )


def _parse_version(version_str: str) -> tuple[int, ...]:
    """Parse a semver-like version string into a tuple of integers."""
    parts = version_str.lstrip("v").split(".")
    result = []
    for part in parts:
        try:
            result.append(int(part))
        except ValueError:
            result.append(0)
    return tuple(result)


def _increment_version(version_str: str, bump: str = "patch") -> str:
    """
    Increment a version string by the specified bump level.

    Args:
        version_str: Current version (e.g., "1.2.3").
        bump: Level to bump - "major", "minor", or "patch".

    Returns:
        New version string.
    """
    parts = list(_parse_version(version_str))
    while len(parts) < 3:
        parts.append(0)

    if bump == "major":
        parts[0] += 1
        parts[1] = 0
        parts[2] = 0
    elif bump == "minor":
        parts[1] += 1
        parts[2] = 0
    else:
        parts[2] += 1

    return ".".join(str(p) for p in parts)


class VersionManager:
    """
    Manages version history for a collection of prompt templates.

    Tracks versions per template name, supports diffing between versions,
    and provides rollback capabilities.
    """

    def __init__(self) -> None:
        self._versions: dict[str, list[PromptVersion]] = {}

    def create_version(
        self,
        template: PromptTemplate,
        changelog: str = "",
        author: str = "",
        bump: str = "patch",
        version_override: str | None = None,
    ) -> PromptVersion:
        """
        Create a new version for a template.

        If versions already exist for this template name, the version
        number is auto-incremented from the latest. Otherwise, it starts
        at "1.0.0".

        Args:
            template: The template to version.
            changelog: Description of what changed.
            author: Who made the change.
            bump: Version bump level ("major", "minor", "patch").
            version_override: Explicit version string (overrides auto-increment).

        Returns:
            The newly created PromptVersion.
        """
        existing = self._versions.get(template.name, [])

        if version_override:
            new_version_str = version_override
        elif existing:
            latest = existing[-1]
            new_version_str = _increment_version(latest.version, bump)
        else:
            new_version_str = "1.0.0"

        # Update the template's version field to match
        template.version = new_version_str

        version = PromptVersion(
            version=new_version_str,
            template=template,
            changelog=changelog,
            author=author,
        )

        if template.name not in self._versions:
            self._versions[template.name] = []
        self._versions[template.name].append(version)

        return version

    def get_version(
        self, template_name: str, version: str | None = None
    ) -> PromptVersion:
        """
        Get a specific version of a template.

        Args:
            template_name: Name of the template.
            version: Version string. If None, returns the latest version.

        Returns:
            The matching PromptVersion.

        Raises:
            KeyError: If the template or version is not found.
        """
        if template_name not in self._versions:
            raise KeyError(f"No versions found for template '{template_name}'.")

        versions = self._versions[template_name]
        if not versions:
            raise KeyError(f"No versions found for template '{template_name}'.")

        if version is None:
            return versions[-1]

        for v in versions:
            if v.version == version:
                return v

        available = [v.version for v in versions]
        raise KeyError(
            f"Version '{version}' not found for template '{template_name}'. "
            f"Available: {available}"
        )

    def list_versions(self, template_name: str) -> list[PromptVersion]:
        """
        List all versions of a template in chronological order.

        Args:
            template_name: Name of the template.

        Returns:
            List of PromptVersion objects, oldest first.

        Raises:
            KeyError: If no versions exist for the template.
        """
        if template_name not in self._versions:
            raise KeyError(f"No versions found for template '{template_name}'.")
        return list(self._versions[template_name])

    def list_template_names(self) -> list[str]:
        """
        List all template names that have versions.

        Returns:
            Sorted list of template names.
        """
        return sorted(self._versions.keys())

    def diff(
        self,
        template_name: str,
        version_a: str,
        version_b: str,
    ) -> str:
        """
        Generate a unified diff between two versions of a template.

        Args:
            template_name: Name of the template.
            version_a: The 'from' version string.
            version_b: The 'to' version string.

        Returns:
            Unified diff string showing the changes between versions.

        Raises:
            KeyError: If either version is not found.
        """
        ver_a = self.get_version(template_name, version_a)
        ver_b = self.get_version(template_name, version_b)

        lines_a = ver_a.template.template_str.splitlines(keepends=True)
        lines_b = ver_b.template.template_str.splitlines(keepends=True)

        diff_lines = difflib.unified_diff(
            lines_a,
            lines_b,
            fromfile=f"{template_name} v{version_a}",
            tofile=f"{template_name} v{version_b}",
            lineterm="",
        )

        return "\n".join(diff_lines)

    def rollback(self, template_name: str, target_version: str) -> PromptVersion:
        """
        Create a new version that rolls back to a previous template state.

        Args:
            template_name: Name of the template.
            target_version: The version to roll back to.

        Returns:
            A new PromptVersion with the rolled-back template content.
        """
        target = self.get_version(template_name, target_version)

        # Create a copy of the old template
        rolled_back_template = PromptTemplate(
            name=target.template.name,
            template_str=target.template.template_str,
            variables=list(target.template.variables),
            metadata=dict(target.template.metadata),
        )

        return self.create_version(
            template=rolled_back_template,
            changelog=f"Rollback to version {target_version}",
            bump="patch",
        )

    def get_latest_version(self, template_name: str) -> PromptVersion:
        """
        Get the latest version of a template.

        Convenience method equivalent to get_version(name, None).

        Args:
            template_name: Name of the template.

        Returns:
            The latest PromptVersion.
        """
        return self.get_version(template_name, None)

    def version_count(self, template_name: str) -> int:
        """
        Get the number of versions for a template.

        Args:
            template_name: Name of the template.

        Returns:
            Number of versions, or 0 if template has no versions.
        """
        return len(self._versions.get(template_name, []))

    def export_history(self, template_name: str) -> list[dict[str, Any]]:
        """
        Export the full version history of a template as dictionaries.

        Args:
            template_name: Name of the template.

        Returns:
            List of version dictionaries in chronological order.
        """
        versions = self.list_versions(template_name)
        return [v.to_dict() for v in versions]


__all__ = [
    "PromptVersion",
    "VersionManager",
]
