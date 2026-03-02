# Compute -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Wraps the OpenStack Nova API for Infomaniak Public Cloud, providing full instance lifecycle management, image and flavor enumeration, SSH keypair operations, and availability zone discovery through `InfomaniakComputeClient`.

## Architecture

Single-class design. `InfomaniakComputeClient` extends both `InfomaniakOpenStackBase` (connection management) and `ComputeClient` ABC (interface contract). Sets `_service_name = "compute"`. Uses `self._conn.compute.*` for Nova operations and `self._conn.image.*` for Glance image queries.

## Key Methods

### Instance Operations

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `list_instances` | (none) | `list[dict]` | List all servers |
| `get_instance` | `instance_id: str` | `dict or None` | Get server by UUID |
| `create_instance` | `name, flavor, image, network, key_name, security_groups, user_data, availability_zone, **kwargs` | `dict or None` | Create and wait for ACTIVE |
| `start_instance` | `instance_id: str` | `bool` | Start stopped instance |
| `stop_instance` | `instance_id: str` | `bool` | Stop running instance |
| `reboot_instance` | `instance_id: str, reboot_type: str = "SOFT"` | `bool` | SOFT or HARD reboot |
| `delete_instance` | `instance_id: str, force: bool = False` | `bool` | Delete instance |
| `terminate_instance` | `instance_id: str` | `bool` | Alias for `delete_instance(force=True)` |

### Image and Flavor Operations

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `list_images` | (none) | `list[dict]` | List images via Glance |
| `get_image` | `image_id: str` | `dict or None` | Get image by ID or name |
| `list_flavors` | (none) | `list[dict]` | List flavors (vcpus, ram, disk) |

### Keypair and AZ Operations

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `list_keypairs` | (none) | `list[dict]` | List SSH key pairs |
| `create_keypair` | `name: str, public_key: str or None` | `dict or None` | Create/import keypair |
| `delete_keypair` | `name: str` | `bool` | Delete keypair |
| `list_availability_zones` | (none) | `list[dict]` | List AZs with availability state |

## Dependencies

- **Internal**: `codomyrmex.cloud.infomaniak.base.InfomaniakOpenStackBase`, `codomyrmex.cloud.common.ComputeClient`
- **External**: `openstacksdk` (Nova, Glance, Neutron proxies), `logging`

## Constraints

- `create_instance` resolves flavor, image, and network via `find_flavor`, `find_image`, `find_network` before calling `create_server`; any resolution failure returns `None` immediately.
- `create_instance` blocks on `wait_for_server` until instance reaches ACTIVE state.
- `_server_to_dict` extracts `security_groups` as a name list via list comprehension on `server.security_groups`.
- `create_keypair` conditionally includes `private_key` in the return dict only if the server generated one (i.e., no `public_key` was provided).

## Error Handling

- All methods catch `Exception`, log via `logger.error`, and return sentinel values.
- No exceptions propagate to callers.
