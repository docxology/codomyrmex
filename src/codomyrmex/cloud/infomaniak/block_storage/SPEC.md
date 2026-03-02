# Block Storage -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Wraps the OpenStack Cinder API for Infomaniak Public Cloud, providing volume lifecycle management, backup/restore workflows, and snapshot operations through a single `InfomaniakVolumeClient` class.

## Architecture

Single-class design. `InfomaniakVolumeClient` extends `InfomaniakOpenStackBase` and sets `_service_name = "block_storage"`. All operations delegate to `self._conn.block_storage.*` methods from `openstacksdk`, except attach/detach which use `self._conn.compute.*` (Nova volume attachment API).

## Key Methods

### Volume Operations

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `list_volumes` | (none) | `list[dict]` | List all volumes with full metadata |
| `get_volume` | `volume_id: str` | `dict or None` | Get volume by UUID |
| `create_volume` | `size: int, name: str, description, volume_type, availability_zone, snapshot_id, image_id, **kwargs` | `dict or None` | Create volume (size in GB) |
| `delete_volume` | `volume_id: str, force: bool = False` | `bool` | Delete volume |
| `extend_volume` | `volume_id: str, new_size: int` | `bool` | Extend to new_size GB |
| `attach_volume` | `volume_id: str, instance_id: str, device: str or None` | `bool` | Attach to instance via Nova |
| `detach_volume` | `volume_id: str, instance_id: str` | `bool` | Find and remove attachment |

### Backup Operations

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `list_backups` | (none) | `list[dict]` | List all backups |
| `create_backup` | `volume_id, name, description, incremental: bool, force: bool` | `dict or None` | Create backup |
| `restore_backup` | `backup_id, volume_id, name` | `dict or None` | Restore to new or existing volume |
| `delete_backup` | `backup_id: str, force: bool` | `bool` | Delete backup |

### Snapshot Operations

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `list_snapshots` | (none) | `list[dict]` | List all snapshots |
| `create_snapshot` | `volume_id, name, description, force: bool` | `dict or None` | Create snapshot |
| `delete_snapshot` | `snapshot_id: str, force: bool` | `bool` | Delete snapshot |

## Dependencies

- **Internal**: `codomyrmex.cloud.infomaniak.base.InfomaniakOpenStackBase`
- **External**: `openstacksdk` (Cinder and Nova proxies), `logging`

## Constraints

- `_volume_to_dict` converts OpenStack volume resources to plain dicts with `id`, `name`, `status`, `size`, `volume_type`, `availability_zone`, `bootable`, `encrypted`, `attachments`, `created_at`.
- `detach_volume` iterates `self._conn.compute.volume_attachments(instance_id)` to find the matching `volume_id`; returns `False` with a warning if the volume is not attached.
- All methods catch broad `Exception` to prevent SDK errors from propagating; failures are logged and sentinel values returned.

## Error Handling

- All methods follow the pattern: try/except with `logger.error` on failure, returning `None`, `False`, or `[]`.
- No exceptions are raised to callers; all errors are absorbed and logged.
