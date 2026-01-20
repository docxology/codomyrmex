"""Permission registry for role-based access control (RBAC)."""

from typing import Dict, List, Set, Optional
import logging

logger = logging.getLogger(__name__)

class PermissionRegistry:
    """Manages roles and their associated permissions."""
    
    def __init__(self):
        self._roles: Dict[str, Set[str]] = {}
        self._role_hierarchy: Dict[str, Set[str]] = {}

    def register_role(self, role: str, permissions: List[str]):
        """Register a role with a list of direct permissions."""
        if role not in self._roles:
            self._roles[role] = set()
        self._roles[role].update(permissions)

    def add_inheritance(self, role: str, parent_role: str):
        """Make 'role' inherit all permissions from 'parent_role'."""
        if role not in self._role_hierarchy:
            self._role_hierarchy[role] = set()
        self._role_hierarchy[role].add(parent_role)

    def get_permissions(self, role: str) -> Set[str]:
        """Get all permissions for a role, including inherited ones."""
        permissions = self._roles.get(role, set()).copy()
        
        parents = self._role_hierarchy.get(role, set())
        for parent in parents:
            permissions.update(self.get_permissions(parent))
            
        return permissions

    def has_permission(self, role: str, permission: str) -> bool:
        """Check if a role has a specific permission."""
        return permission in self.get_permissions(role) or "admin" in self.get_permissions(role)
