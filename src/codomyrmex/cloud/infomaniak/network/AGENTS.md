# Codomyrmex Agents -- src/codomyrmex/cloud/infomaniak/network

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Provides networking operations for Infomaniak Public Cloud via the OpenStack Neutron and Octavia APIs. Manages networks and subnets, routers with interface attachment, security groups with rules, floating IPs (allocate, associate, disassociate, release), and load balancers with listeners, pools, pool members, and health monitors.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `client.py` | `InfomaniakNetworkClient` | Neutron/Octavia client extending `InfomaniakOpenStackBase`; `_service_name = "network"` |
| `client.py` | `list_networks()` / `create_network()` / `delete_network()` | Network CRUD |
| `client.py` | `create_subnet(network_id, name, cidr, ...)` | Create subnet with DHCP and DNS config |
| `client.py` | `list_subnets()` / `get_subnet()` / `delete_subnet()` | Subnet operations |
| `client.py` | `list_routers()` / `create_router()` / `delete_router()` | Router lifecycle |
| `client.py` | `add_router_interface()` / `remove_router_interface()` | Attach/detach subnets to routers |
| `client.py` | `list_security_groups()` / `create_security_group()` / `delete_security_group()` | Security group lifecycle |
| `client.py` | `add_security_group_rule(...)` | Add ingress/egress rules with protocol/port/CIDR filters |
| `client.py` | `list_floating_ips()` / `allocate_floating_ip()` / `associate_floating_ip()` | Floating IP allocation and association |
| `client.py` | `disassociate_floating_ip()` / `release_floating_ip()` | Floating IP cleanup |
| `client.py` | `list_loadbalancers()` / `create_loadbalancer()` / `delete_loadbalancer()` | Octavia LB lifecycle |
| `client.py` | `list_listeners()` / `create_listener()` / `delete_listener()` | LB listener management |
| `client.py` | `list_pools()` / `create_pool()` / `delete_pool()` | LB pool management |
| `client.py` | `list_pool_members()` / `add_pool_member()` / `remove_pool_member()` | Pool member management |
| `client.py` | `list_health_monitors()` / `create_health_monitor()` / `delete_health_monitor()` | Health monitor management |

## Operating Contracts

- `create_router` optionally resolves an external network by name via `find_network` to set `external_gateway_info`.
- `allocate_floating_ip` resolves the external network name to an ID before allocation.
- `associate_floating_ip` and `disassociate_floating_ip` use `update_ip` to set/clear `port_id`.
- Load balancer operations use `self._conn.load_balancer.*` (Octavia proxy).
- All errors are logged and methods return sentinel values rather than raising.

## Integration Points

- **Depends on**: `codomyrmex.cloud.infomaniak.base.InfomaniakOpenStackBase`, `openstacksdk` (Neutron and Octavia proxies)
- **Used by**: `codomyrmex.cloud.infomaniak` (parent), DNS client (FIP resolution for PTR records), metering client (network usage)

## Navigation

- **Parent**: [infomaniak](../AGENTS.md)
- **Root**: [../../../../../README.md](../../../../../README.md)
