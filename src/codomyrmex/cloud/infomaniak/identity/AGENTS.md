# Codomyrmex Agents -- src/codomyrmex/cloud/infomaniak/identity

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Provides identity and authentication management for Infomaniak Public Cloud via the OpenStack Keystone API. Manages users, projects, application credentials (with one-time secret retrieval), roles, and EC2-style credentials for S3 access.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `client.py` | `InfomaniakIdentityClient` | Keystone client extending `InfomaniakOpenStackBase`; `_service_name = "identity"` |
| `client.py` | `get_current_user()` | Get the authenticated user's info |
| `client.py` | `get_user(user_id)` | Get a specific user by ID |
| `client.py` | `list_projects()` | List accessible projects |
| `client.py` | `get_current_project()` | Get the currently scoped project |
| `client.py` | `list_application_credentials()` | List app credentials for current user |
| `client.py` | `create_application_credential(name, ...)` | Create app credential (secret returned once only) |
| `client.py` | `get_application_credential(credential_id)` | Get app credential by ID (no secret) |
| `client.py` | `delete_application_credential(credential_id)` | Delete app credential |
| `client.py` | `list_roles()` | List available roles |
| `client.py` | `list_user_roles(project_id)` | List roles assigned to current user in project |
| `client.py` | `list_ec2_credentials()` | List EC2-style credentials (type == "ec2") |
| `client.py` | `create_ec2_credentials(project_id)` | Create EC2 credentials for S3 access |
| `client.py` | `delete_ec2_credentials(credential_id)` | Delete EC2 credentials |

## Operating Contracts

- `create_application_credential` returns a `secret` field that is only available at creation time; subsequent `get_application_credential` calls do not include it.
- User-scoped operations (`list_application_credentials`, `create_application_credential`, `list_ec2_credentials`, etc.) use `self._conn.current_user_id`.
- `list_user_roles` resolves role IDs to names via `self._conn.identity.get_role` for each assignment.
- EC2 credentials filter by `type == "ec2"` from the generic credentials endpoint.
- All errors are logged and methods return sentinel values rather than raising.

## Integration Points

- **Depends on**: `codomyrmex.cloud.infomaniak.base.InfomaniakOpenStackBase`, `openstacksdk` (Keystone proxy)
- **Used by**: `codomyrmex.cloud.infomaniak` (parent), object_storage client (EC2 creds for S3)

## Navigation

- **Parent**: [infomaniak](../AGENTS.md)
- **Root**: [../../../../../README.md](../../../../../README.md)
