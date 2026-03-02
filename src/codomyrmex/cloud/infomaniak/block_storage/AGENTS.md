# Codomyrmex Agents -- src/codomyrmex/cloud/infomaniak/block_storage

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Provides block storage operations for Infomaniak Public Cloud via the OpenStack Cinder API. Manages volumes (create, delete, extend, attach, detach), backups (create, restore, delete), and snapshots (create, delete, list).

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `client.py` | `InfomaniakVolumeClient` | Cinder client extending `InfomaniakOpenStackBase`; `_service_name = "block_storage"` |
| `client.py` | `list_volumes()` | List all block storage volumes as dicts |
| `client.py` | `get_volume(volume_id)` | Get details for a specific volume by UUID |
| `client.py` | `create_volume(size, name, ...)` | Create a new volume (size in GB, optional type/AZ/snapshot/image) |
| `client.py` | `delete_volume(volume_id, force)` | Delete a volume, optionally forcing if attached |
| `client.py` | `extend_volume(volume_id, new_size)` | Extend volume size (new_size must exceed current) |
| `client.py` | `attach_volume(volume_id, instance_id, device)` | Attach volume to compute instance via Nova API |
| `client.py` | `detach_volume(volume_id, instance_id)` | Detach volume by finding and removing the attachment |
| `client.py` | `list_backups()` | List volume backups |
| `client.py` | `create_backup(volume_id, name, ...)` | Create backup with optional incremental and force flags |
| `client.py` | `restore_backup(backup_id, volume_id, name)` | Restore backup to new or existing volume |
| `client.py` | `delete_backup(backup_id, force)` | Delete a backup |
| `client.py` | `list_snapshots()` | List volume snapshots |
| `client.py` | `create_snapshot(volume_id, name, ...)` | Create a volume snapshot |
| `client.py` | `delete_snapshot(snapshot_id, force)` | Delete a snapshot |

## Operating Contracts

- All methods return `None`, empty list, or `False` on failure rather than raising exceptions.
- All errors are logged via `logging` before returning failure values.
- `attach_volume` delegates to `self._conn.compute.create_volume_attachment` (Nova API).
- `detach_volume` iterates volume attachments to find the correct attachment ID before deletion.
- Volume dicts include: `id`, `name`, `status`, `size`, `volume_type`, `availability_zone`, `bootable`, `encrypted`, `attachments`, `created_at`.

## Integration Points

- **Depends on**: `codomyrmex.cloud.infomaniak.base.InfomaniakOpenStackBase`, `openstacksdk`
- **Used by**: `codomyrmex.cloud.infomaniak` (parent), metering client (storage usage queries)

## Navigation

- **Parent**: [infomaniak](../AGENTS.md)
- **Root**: [../../../../../README.md](../../../../../README.md)
