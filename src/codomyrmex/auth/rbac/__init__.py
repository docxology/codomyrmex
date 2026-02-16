"""Role-based access control (RBAC) subpackage.

This subpackage provides the PermissionRegistry for managing roles,
permissions, and role inheritance hierarchies.
"""

from .permissions import PermissionRegistry

__all__ = [
    "PermissionRegistry",
]
