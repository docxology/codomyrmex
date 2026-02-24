"""
Permissions Submodule

Skill capability permissions and access control.
"""

import logging
from typing import Any

try:
    from codomyrmex.logging_monitoring.core.logger_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

__version__ = "0.1.0"


class SkillPermissionManager:
    """Manages permissions and access control for skills."""

    def __init__(self):
        """Initialize SkillPermissionManager."""
        self._permissions: dict[str, set[str]] = {}  # skill_id -> set of granted actions

    def check_permission(self, skill_id: str, action: str) -> bool:
        """
        Check if an action is permitted for a skill.

        Args:
            skill_id: Skill identifier
            action: Action to check (e.g. 'execute', 'modify', 'delete')

        Returns:
            True if the action is permitted
        """
        allowed = self._permissions.get(skill_id, set())
        return action in allowed

    def grant(self, skill_id: str, permission: str) -> None:
        """
        Grant a permission to a skill.

        Args:
            skill_id: Skill identifier
            permission: Permission/action to grant
        """
        if skill_id not in self._permissions:
            self._permissions[skill_id] = set()
        self._permissions[skill_id].add(permission)
        logger.info(f"Granted '{permission}' permission to skill {skill_id}")

    def revoke(self, skill_id: str, permission: str) -> bool:
        """
        Revoke a permission from a skill.

        Args:
            skill_id: Skill identifier
            permission: Permission/action to revoke

        Returns:
            True if the permission was found and revoked
        """
        if skill_id in self._permissions and permission in self._permissions[skill_id]:
            self._permissions[skill_id].discard(permission)
            logger.info(f"Revoked '{permission}' permission from skill {skill_id}")
            return True
        return False

    def list_permissions(self, skill_id: str) -> list[str]:
        """
        List all permissions granted to a skill.

        Args:
            skill_id: Skill identifier

        Returns:
            List of permission strings
        """
        return sorted(self._permissions.get(skill_id, set()))

    def grant_all(self, skill_id: str, permissions: list[str]) -> None:
        """
        Grant multiple permissions at once.

        Args:
            skill_id: Skill identifier
            permissions: List of permissions to grant
        """
        for perm in permissions:
            self.grant(skill_id, perm)

    def revoke_all(self, skill_id: str) -> None:
        """
        Revoke all permissions from a skill.

        Args:
            skill_id: Skill identifier
        """
        if skill_id in self._permissions:
            self._permissions[skill_id].clear()
            logger.info(f"Revoked all permissions from skill {skill_id}")


__all__ = ["SkillPermissionManager"]
