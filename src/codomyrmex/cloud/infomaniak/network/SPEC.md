# Network -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Wraps the OpenStack Neutron and Octavia APIs for Infomaniak Public Cloud networking. Provides full network topology management (networks, subnets, routers), security group configuration, floating IP lifecycle, and Layer 4/7 load balancing with listeners, pools, members, and health monitors.

## Architecture

Single-class design. `InfomaniakNetworkClient` extends `InfomaniakOpenStackBase` with `_service_name = "network"`. Core networking uses `self._conn.network.*` (Neutron proxy). Load balancer operations use `self._conn.load_balancer.*` (Octavia proxy).

## Key Methods

### Network and Subnet Operations

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `list_networks` | (none) | `list[dict]` | All networks (id, name, status, shared, external, subnets) |
| `create_network` | `name, description, is_shared, **kwargs` | `dict or None` | Create network |
| `delete_network` | `network_id: str` | `bool` | Delete network |
| `create_subnet` | `network_id, name, cidr, ip_version, gateway_ip, enable_dhcp, dns_nameservers, **kwargs` | `dict or None` | Create subnet |
| `list_subnets` | (none) | `list[dict]` | All subnets |
| `get_subnet` | `subnet_id: str` | `dict or None` | Subnet by ID |
| `delete_subnet` | `subnet_id: str` | `bool` | Delete subnet |

### Router Operations

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `list_routers` | (none) | `list[dict]` | All routers with gateway info |
| `create_router` | `name, external_network, **kwargs` | `dict or None` | Create with optional external gateway |
| `add_router_interface` | `router_id, subnet_id` | `bool` | Attach subnet |
| `remove_router_interface` | `router_id, subnet_id` | `bool` | Detach subnet |
| `delete_router` | `router_id: str` | `bool` | Delete router |

### Security Group and Floating IP Operations

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `list_security_groups` | (none) | `list[dict]` | All SGs with rule count |
| `create_security_group` | `name, description` | `dict or None` | Create SG |
| `add_security_group_rule` | `security_group_id, direction, protocol, port_range_min, port_range_max, remote_ip_prefix, ethertype, **kwargs` | `dict or None` | Add rule |
| `delete_security_group` | `security_group_id: str` | `bool` | Delete SG |
| `list_floating_ips` | (none) | `list[dict]` | All FIPs |
| `allocate_floating_ip` | `external_network: str` | `dict or None` | Allocate from external net |
| `associate_floating_ip` | `floating_ip_id, port_id` | `bool` | Associate to port |
| `disassociate_floating_ip` | `floating_ip_id: str` | `bool` | Clear port |
| `release_floating_ip` | `floating_ip_id: str` | `bool` | Deallocate FIP |

### Load Balancer Operations (Octavia)

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `list_loadbalancers` | (none) | `list[dict]` | All LBs |
| `create_loadbalancer` | `name, subnet_id, vip_address, **kwargs` | `dict or None` | Create LB |
| `delete_loadbalancer` | `loadbalancer_id, cascade: bool` | `bool` | Delete (cascade deletes children) |
| `create_listener` | `loadbalancer_id, name, protocol, port, **kwargs` | `dict or None` | Create listener |
| `create_pool` | `name, protocol, lb_algorithm, listener_id, loadbalancer_id, **kwargs` | `dict or None` | Create pool |
| `add_pool_member` | `pool_id, address, port, weight, name, subnet_id, **kwargs` | `dict or None` | Add member |
| `remove_pool_member` | `pool_id, member_id` | `bool` | Remove member |
| `create_health_monitor` | `pool_id, monitor_type, delay, timeout, max_retries, name, **kwargs` | `dict or None` | Create monitor |

## Dependencies

- **Internal**: `codomyrmex.cloud.infomaniak.base.InfomaniakOpenStackBase`
- **External**: `openstacksdk` (Neutron proxy, Octavia/Load Balancer proxy), `logging`

## Constraints

- `allocate_floating_ip` resolves external network name via `find_network`; fails if not found.
- `associate_floating_ip` sets `port_id` via `update_ip`; `disassociate_floating_ip` clears it with `port_id=None`.
- `delete_loadbalancer` supports `cascade=True` to remove all child resources (listeners, pools, members, monitors).
- Health monitor types include HTTP, HTTPS, PING, TCP as supported by Octavia.

## Error Handling

- All methods catch `Exception`, log via `logger.error`, and return sentinel values.
- No exceptions propagate to callers.
