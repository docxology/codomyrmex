"""
Versioning Submodule

Skill version management and compatibility tracking.
"""

import logging
import re
from typing import Any

try:
    from codomyrmex.logging_monitoring.logger_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

__version__ = "0.1.0"


def parse_version(version_str: str) -> tuple[int, ...]:
    """Parse a semver-like version string into a tuple of ints."""
    parts = re.findall(r'\d+', version_str)
    return tuple(int(p) for p in parts)


class SkillVersionManager:
    """Manages skill versions and compatibility checking."""

    def __init__(self):
        """Initialize SkillVersionManager."""
        self._version_history: dict[str, list[str]] = {}

    def get_version(self, skill) -> str:
        """
        Get the current version of a skill.

        Args:
            skill: Skill instance or skill data dict

        Returns:
            Version string (defaults to '0.0.0' if not set)
        """
        if hasattr(skill, 'metadata'):
            return getattr(skill.metadata, 'version', '0.0.0')
        elif isinstance(skill, dict):
            return skill.get('version', '0.0.0')
        return '0.0.0'

    def check_compatibility(self, skill, required_version: str) -> dict[str, Any]:
        """
        Check if a skill's version is compatible with a required version.

        Uses simple semver major-version compatibility: versions are compatible
        if they share the same major version and the skill version >= required version.

        Args:
            skill: Skill instance or skill data dict
            required_version: Version string to check against

        Returns:
            Dict with 'compatible' (bool), 'current_version', 'required_version'
        """
        current = self.get_version(skill)
        current_parts = parse_version(current)
        required_parts = parse_version(required_version)

        # Same major version and current >= required
        compatible = (
            len(current_parts) > 0
            and len(required_parts) > 0
            and current_parts[0] == required_parts[0]
            and current_parts >= required_parts
        )

        return {
            "compatible": compatible,
            "current_version": current,
            "required_version": required_version,
        }

    def list_versions(self, skill_id: str) -> list[str]:
        """
        List known versions for a skill.

        Args:
            skill_id: Skill identifier

        Returns:
            List of version strings (may be empty if no history tracked)
        """
        return list(self._version_history.get(skill_id, []))

    def register_version(self, skill_id: str, version: str) -> None:
        """
        Register a version in the history for a skill.

        Args:
            skill_id: Skill identifier
            version: Version string to register
        """
        if skill_id not in self._version_history:
            self._version_history[skill_id] = []
        if version not in self._version_history[skill_id]:
            self._version_history[skill_id].append(version)
            logger.info(f"Registered version {version} for skill {skill_id}")


__all__ = ["SkillVersionManager", "parse_version"]
