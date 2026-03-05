"""Permission registry for role-based access control (RBAC).

Provides:
- Role→permission registration with hierarchy (inheritance)
- User→role assignment with multi-role support
- Wildcard permission matching (e.g. "files.*" matches "files.read")
- Permission check with audit logging
- Resource-scoped permissions (e.g. "project:123:write")
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


@dataclass
class PermissionCheck:
    """Record of a permission check for audit."""

    user_id: str
    role: str
    permission: str
    granted: bool
    timestamp: float = field(default_factory=time.time)
    resource: str = ""


class PermissionRegistry:
    """Manages roles, permissions, user assignments, and access checks.

    Supports:
    - Role hierarchy (child inherits parent's permissions)
    - Wildcard matching ("files.*" grants "files.read", "files.write")
    - Multi-role users
    - Audit trail of permission checks
    """

    def __init__(self) -> None:
        self._roles: dict[str, set[str]] = {}
        self._role_hierarchy: dict[str, set[str]] = {}
        self._user_roles: dict[str, set[str]] = {}
        self._audit_log: list[PermissionCheck] = []

    # ── Role management ─────────────────────────────────────────────

    def register_role(self, role: str, permissions: list[str] | None = None) -> None:
        """Register a role with direct permissions."""
        if role not in self._roles:
            self._roles[role] = set()
        if permissions:
            self._roles[role].update(permissions)
        logger.info(
            "Registered role '%s' with %d permissions", role, len(self._roles[role])
        )

    def add_inheritance(self, child: str, parent: str) -> None:
        """Make child role inherit all permissions from parent role."""
        if child not in self._roles:
            self.register_role(child)
        if parent not in self._roles:
            self.register_role(parent)
        self._role_hierarchy.setdefault(child, set()).add(parent)
        logger.debug("Role inheritance added: %s -> %s", child, parent)

    def remove_role(self, role: str) -> bool:
        """Remove a role and unassign from all users."""
        if role not in self._roles:
            return False
        del self._roles[role]
        self._role_hierarchy.pop(role, None)
        # Remove from other roles' hierarchies
        for parents in self._role_hierarchy.values():
            parents.discard(role)
        # Unassign from users
        for user_roles in self._user_roles.values():
            user_roles.discard(role)
        return True

    def list_roles(self) -> list[str]:
        """List all registered role names."""
        return sorted(self._roles.keys())

    # ── User assignment ─────────────────────────────────────────────

    def assign_role(self, user_id: str, role: str) -> None:
        """Assign a role to a user."""
        if role not in self._roles:
            self.register_role(role)
        self._user_roles.setdefault(user_id, set()).add(role)
        logger.info("Assigned role '%s' to user '%s'", role, user_id)

    def revoke_role(self, user_id: str, role: str) -> bool:
        """Revoke a role from a user."""
        if user_id in self._user_roles:
            if role in self._user_roles[user_id]:
                self._user_roles[user_id].discard(role)
                logger.info("Revoked role '%s' from user '%s'", role, user_id)
                return True
        return False

    def get_user_roles(self, user_id: str) -> set[str]:
        """Get all roles assigned to a user."""
        return self._user_roles.get(user_id, set()).copy()

    # ── Permission resolution ───────────────────────────────────────

    def get_permissions(self, role: str, _visited: set[str] | None = None) -> set[str]:
        """Get all permissions for a role, including inherited (cycle-safe)."""
        if _visited is None:
            _visited = set()
        if role in _visited:
            return set()
        _visited.add(role)

        permissions = self._roles.get(role, set()).copy()
        for parent in self._role_hierarchy.get(role, set()):
            permissions.update(self.get_permissions(parent, _visited))
        return permissions

    def get_user_permissions(self, user_id: str) -> set[str]:
        """Get all effective permissions for a user across all assigned roles."""
        perms: set[str] = set()
        for role in self._user_roles.get(user_id, set()):
            perms.update(self.get_permissions(role))
        return perms

    @staticmethod
    def _matches(permission: str, requested: str) -> bool:
        """Check if a registered permission matches a requested permission.

        Supports wildcards: "files.*" matches "files.read".
        """
        if permission == "*" or permission == requested:
            return True
        if permission.endswith(".*"):
            prefix = permission[:-1]  # "files."
            if requested.startswith(prefix):
                return True
        return False

    def has_permission(self, role: str, permission: str) -> bool:
        """Check if a role has a specific permission (with wildcards)."""
        permissions = self.get_permissions(role)
        if "*" in permissions or "admin" in permissions:
            return True
        for p in permissions:
            if self._matches(p, permission):
                return True
        return False

    # ── User-level check with audit ─────────────────────────────────

    def check(self, user_id: str, permission: str, resource: str = "") -> bool:
        """Check if a user has a permission. Logs to audit trail.

        Args:
            user_id: The user to check.
            permission: The permission string.
            resource: Optional resource context.

        Returns:
            True if any of the user's roles grant the permission.
        """
        roles = self._user_roles.get(user_id, set())

        # Check all assigned roles
        for role in roles:
            if self.has_permission(role, permission):
                self._audit_log.append(
                    PermissionCheck(
                        user_id=user_id,
                        role=role,
                        permission=permission,
                        granted=True,
                        resource=resource,
                    )
                )
                return True

        # Failed check
        self._audit_log.append(
            PermissionCheck(
                user_id=user_id,
                role=",".join(roles) if roles else "none",
                permission=permission,
                granted=False,
                resource=resource,
            )
        )
        return False

    @property
    def audit_log(self) -> list[PermissionCheck]:
        return list(self._audit_log)

    @property
    def role_count(self) -> int:
        return len(self._roles)

    @property
    def user_count(self) -> int:
        return len(self._user_roles)
