# Codomyrmex Agents — src/codomyrmex/auth/rbac

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Role-based access control (RBAC) with role-permission registration, role hierarchy (inheritance), multi-role user assignments, wildcard permission matching, and permission checks with audit logging.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `permissions.py` | `PermissionRegistry` | Central registry for roles, permissions, user assignments, and access checks |
| `permissions.py` | `PermissionCheck` | Audit record dataclass capturing user, role, permission, granted/denied, and timestamp |

## Operating Contracts

- Role hierarchy supports inheritance: child roles inherit all parent permissions (cycle-safe via visited set).
- Wildcard matching: `"files.*"` matches `"files.read"`; `"*"` matches everything; `"admin"` in permissions grants all.
- `check()` logs every access check (granted or denied) to the internal audit trail.
- Multi-role users are supported: permissions are the union of all assigned roles.
- Errors must be logged via `logging` before re-raising.

## Integration Points

- **Depends on**: Standard library only (`logging`, `time`, `dataclasses`)
- **Used by**: `auth` parent module, Trust Gateway, API authorization middleware

## Navigation

- **Parent**: [auth](../README.md)
- **Root**: [Root](../../../../README.md)
