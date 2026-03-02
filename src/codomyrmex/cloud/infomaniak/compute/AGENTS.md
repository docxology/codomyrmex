# Codomyrmex Agents -- src/codomyrmex/cloud/infomaniak/compute

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Provides compute instance management for Infomaniak Public Cloud via the OpenStack Nova API. Handles instance lifecycle (create with wait_for_server, start, stop, reboot, delete), image listing, flavor enumeration, SSH keypair management, and availability zone discovery.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `client.py` | `InfomaniakComputeClient` | Nova client extending both `InfomaniakOpenStackBase` and `ComputeClient` ABC |
| `client.py` | `list_instances()` | List all compute instances |
| `client.py` | `get_instance(instance_id)` | Get instance details by UUID |
| `client.py` | `create_instance(name, flavor, image, network, ...)` | Create instance with flavor/image/network resolution and `wait_for_server` |
| `client.py` | `start_instance(instance_id)` | Start a stopped instance |
| `client.py` | `stop_instance(instance_id)` | Stop a running instance |
| `client.py` | `reboot_instance(instance_id, reboot_type)` | Reboot instance (SOFT or HARD) |
| `client.py` | `delete_instance(instance_id, force)` | Delete an instance |
| `client.py` | `terminate_instance(instance_id)` | ABC-compatible alias for `delete_instance(force=True)` |
| `client.py` | `list_images()` | List available images via Glance |
| `client.py` | `get_image(image_id)` | Get image details by ID or name |
| `client.py` | `list_flavors()` | List available flavors (vcpus, ram, disk) |
| `client.py` | `list_keypairs()` | List SSH key pairs |
| `client.py` | `create_keypair(name, public_key)` | Create or import SSH keypair (includes private_key if generated) |
| `client.py` | `delete_keypair(name)` | Delete SSH key pair |
| `client.py` | `list_availability_zones()` | List compute availability zones |

## Operating Contracts

- `create_instance` resolves flavor, image, and network by name/ID via `find_*` methods before creating; returns `None` if any resolution fails.
- `create_instance` calls `wait_for_server` to block until the instance reaches ACTIVE state.
- `terminate_instance` is an ABC-compatible alias that delegates to `delete_instance(force=True)`.
- Instance dicts include: `id`, `name`, `status`, `flavor`, `image`, `addresses`, `key_name`, `created_at`, `updated_at`, `availability_zone`, `security_groups`.
- All errors are logged and methods return sentinel values (`None`, `False`, `[]`) rather than raising.

## Integration Points

- **Depends on**: `codomyrmex.cloud.infomaniak.base.InfomaniakOpenStackBase`, `codomyrmex.cloud.common.ComputeClient`, `openstacksdk`
- **Used by**: `codomyrmex.cloud.infomaniak` (parent), block_storage client (attach/detach), metering client (compute usage)

## Navigation

- **Parent**: [infomaniak](../AGENTS.md)
- **Root**: [../../../../../README.md](../../../../../README.md)
