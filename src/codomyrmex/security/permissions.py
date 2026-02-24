"""RBAC permission model.

Hierarchical role-based access control with admin > operator > viewer
inheritance and grant-based permission checks.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Permission(Enum):
    """Available permissions."""

    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    DELETE = "delete"
    ADMIN = "admin"


class Role(Enum):
    """Hierarchical roles (higher = more permissions)."""

    VIEWER = "viewer"
    OPERATOR = "operator"
    ADMIN = "admin"


_ROLE_HIERARCHY: dict[Role, set[Permission]] = {
    Role.VIEWER: {Permission.READ},
    Role.OPERATOR: {Permission.READ, Permission.WRITE, Permission.EXECUTE},
    Role.ADMIN: {Permission.READ, Permission.WRITE, Permission.EXECUTE, Permission.DELETE, Permission.ADMIN},
}


@dataclass
class Grant:
    """A permission grant to a principal.

    Attributes:
        principal: User or agent identifier.
        role: Assigned role.
        resource: Resource scope (empty = global).
        granted_by: Who granted this.
    """

    principal: str
    role: Role
    resource: str = ""
    granted_by: str = ""


class PermissionModel:
    """RBAC with hierarchical role inheritance.

    Example::

        model = PermissionModel()
        model.grant("alice", Role.OPERATOR)
        assert model.check("alice", Permission.WRITE)
        assert not model.check("alice", Permission.ADMIN)
    """

    def __init__(self) -> None:
        """Execute   Init   operations natively."""
        self._grants: dict[str, list[Grant]] = {}

    @property
    def principal_count(self) -> int:
        """Execute Principal Count operations natively."""
        return len(self._grants)

    def grant(
        self, principal: str, role: Role,
        resource: str = "", granted_by: str = "",
    ) -> None:
        """Grant a role to a principal."""
        g = Grant(
            principal=principal, role=role,
            resource=resource, granted_by=granted_by,
        )
        self._grants.setdefault(principal, []).append(g)

    def revoke(self, principal: str, role: Role, resource: str = "") -> bool:
        """Revoke a specific grant."""
        grants = self._grants.get(principal, [])
        for i, g in enumerate(grants):
            if g.role == role and g.resource == resource:
                grants.pop(i)
                return True
        return False

    def check(self, principal: str, permission: Permission, resource: str = "") -> bool:
        """Check if a principal has a permission.

        Args:
            principal: User or agent ID.
            permission: Required permission.
            resource: Resource scope.

        Returns:
            True if permission is granted.
        """
        grants = self._grants.get(principal, [])
        for g in grants:
            if resource and g.resource and g.resource != resource:
                continue
            role_perms = _ROLE_HIERARCHY.get(g.role, set())
            if permission in role_perms:
                return True
        return False

    def effective_permissions(self, principal: str, resource: str = "") -> set[Permission]:
        """Get all effective permissions for a principal."""
        perms: set[Permission] = set()
        for g in self._grants.get(principal, []):
            if resource and g.resource and g.resource != resource:
                continue
            perms |= _ROLE_HIERARCHY.get(g.role, set())
        return perms

    def list_grants(self, principal: str = "") -> list[Grant]:
        """List grants, optionally filtered by principal."""
        if principal:
            return list(self._grants.get(principal, []))
        return [g for grants in self._grants.values() for g in grants]

    def permission_matrix(self) -> dict[str, dict[str, bool]]:
        """Generate a permission matrix: principal → permission → bool."""
        matrix: dict[str, dict[str, bool]] = {}
        for principal in self._grants:
            perms = self.effective_permissions(principal)
            matrix[principal] = {p.value: p in perms for p in Permission}
        return matrix


__all__ = ["Grant", "Permission", "PermissionModel", "Role"]
