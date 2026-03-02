# RBAC — Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Permission registry implementing role-based access control with hierarchical role inheritance, wildcard permission matching, and audit logging.

## Architecture

Single-class design with four internal stores: role-permission sets, role hierarchy graph, user-role assignments, and audit log. Permission resolution traverses the hierarchy recursively with cycle detection.

## Key Classes

### `PermissionRegistry`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `register_role` | `role: str, permissions: list[str] \| None` | `None` | Register a role with direct permissions |
| `add_inheritance` | `child: str, parent: str` | `None` | Make child inherit parent's permissions |
| `remove_role` | `role: str` | `bool` | Remove role and unassign from all users |
| `assign_role` | `user_id: str, role: str` | `None` | Assign a role to a user |
| `revoke_role` | `user_id: str, role: str` | `bool` | Revoke a role from a user |
| `get_permissions` | `role: str` | `set[str]` | Get all permissions for a role including inherited (cycle-safe) |
| `get_user_permissions` | `user_id: str` | `set[str]` | Get all effective permissions across all user roles |
| `has_permission` | `role: str, permission: str` | `bool` | Check if role has permission (with wildcards) |
| `check` | `user_id: str, permission: str, resource: str` | `bool` | Check user permission and log to audit trail |
| `list_roles` | none | `list[str]` | List all registered role names |

### `PermissionCheck` (dataclass)

| Field | Type | Description |
|-------|------|-------------|
| `user_id` | `str` | User who was checked |
| `role` | `str` | Role that matched (or comma-joined roles if denied) |
| `permission` | `str` | Permission that was checked |
| `granted` | `bool` | Whether access was granted |
| `resource` | `str` | Optional resource context |

## Dependencies

- **Internal**: None
- **External**: Standard library only (`logging`, `time`, `dataclasses`)

## Constraints

- Permissions are stored in-memory; no persistence.
- Wildcard matching supports `"perm.*"` (prefix) and `"*"` (global); does not support mid-string wildcards.
- `"admin"` in a role's permissions acts as a superuser grant.
- `get_permissions` uses a visited set to prevent infinite recursion on circular hierarchies.
- Zero-mock: real permission checks only, `NotImplementedError` for unimplemented paths.

## Error Handling

- `check()` never raises; returns `False` for unauthorized access and logs to audit trail.
- Role registration logged at INFO level.
