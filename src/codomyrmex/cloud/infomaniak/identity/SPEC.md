# Identity -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Wraps the OpenStack Keystone API for Infomaniak Public Cloud identity management. Provides user and project queries, application credential lifecycle (with one-time secret), role enumeration, and EC2-style credential management for S3-compatible object storage access.

## Architecture

Single-class design. `InfomaniakIdentityClient` extends `InfomaniakOpenStackBase` with `_service_name = "identity"`. All operations delegate to `self._conn.identity.*` methods. User-scoped operations reference `self._conn.current_user_id` and `self._conn.current_project_id`.

## Key Methods

### User and Project Operations

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `get_current_user` | (none) | `dict` | Current authenticated user (id, name, email, domain_id, is_enabled) |
| `get_user` | `user_id: str` | `dict or None` | User by ID |
| `list_projects` | (none) | `list[dict]` | Accessible projects |
| `get_current_project` | (none) | `dict` | Currently scoped project |

### Application Credential Operations

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `list_application_credentials` | (none) | `list[dict]` | List for current user |
| `create_application_credential` | `name, description, expires_at, roles: list[str], unrestricted: bool` | `dict or None` | Create (includes one-time `secret`) |
| `get_application_credential` | `credential_id: str` | `dict or None` | Get by ID (no secret) |
| `delete_application_credential` | `credential_id: str` | `bool` | Delete credential |

### Role Operations

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `list_roles` | (none) | `list[dict]` | Available roles (id, name, description) |
| `list_user_roles` | `project_id: str or None` | `list[dict]` | Roles for current user in project |

### EC2 Credential Operations

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `list_ec2_credentials` | (none) | `list[dict]` | EC2-style creds (access key, project_id) |
| `create_ec2_credentials` | `project_id: str or None` | `dict or None` | Create (access + secret keys) |
| `delete_ec2_credentials` | `credential_id: str` | `bool` | Delete EC2 creds |

## Dependencies

- **Internal**: `codomyrmex.cloud.infomaniak.base.InfomaniakOpenStackBase`
- **External**: `openstacksdk` (Keystone proxy), `logging`

## Constraints

- Application credential `secret` is only returned at creation time; Keystone does not store it retrievably.
- `list_user_roles` performs N+1 queries: one `role_assignments` call, then `get_role` per assignment to resolve names.
- EC2 credentials are filtered from the generic `identity.credentials` endpoint by `type == "ec2"`.
- `create_ec2_credentials` passes a placeholder JSON blob; Keystone generates the actual access/secret pair.

## Error Handling

- All methods catch `Exception`, log via `logger.error`, and return sentinel values (`None`, `{}`, `[]`, `False`).
- No exceptions propagate to callers.
