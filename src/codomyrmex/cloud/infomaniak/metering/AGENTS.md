# Codomyrmex Agents -- src/codomyrmex/cloud/infomaniak/metering

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Provides resource usage metering and quota reporting for Infomaniak Public Cloud. Aggregates compute, storage, network, and object storage usage by querying the respective OpenStack APIs directly, and reports project-level quotas.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `client.py` | `InfomaniakMeteringClient` | Metering client extending `InfomaniakOpenStackBase`; `_service_name = "metering"` |
| `client.py` | `get_compute_usage(start, end)` | Aggregate compute usage (instance count, vcpus, ram, disk) by summing flavors |
| `client.py` | `get_storage_usage()` | Block storage summary (volume count, total GB, attached/unattached) |
| `client.py` | `get_network_usage()` | Network resource counts (networks, routers, security groups, floating IPs) |
| `client.py` | `get_object_storage_usage()` | Object storage summary (containers, objects, total bytes/GB) |
| `client.py` | `get_all_usage()` | Comprehensive usage across all four services with UTC timestamp |
| `client.py` | `list_resources_with_usage()` | Flat list of all resources (instances, volumes, floating IPs) with status |
| `client.py` | `get_compute_quotas()` | Project compute quotas (instances, cores, ram, key_pairs, server_groups) |
| `client.py` | `get_network_quotas()` | Project network quotas (networks, subnets, routers, floating_ips, security_groups) |
| `client.py` | `get_storage_quotas()` | Project storage quotas (volumes, gigabytes, snapshots, backups) |

## Operating Contracts

- `get_compute_usage` iterates all servers and resolves each flavor to sum vcpus, ram, and disk; this performs N+1 API calls (1 list + N get_flavor).
- `get_all_usage` combines all four per-service usage methods into a single dict with a UTC timestamp.
- `list_resources_with_usage` returns a heterogeneous list with `type` prefixes: `compute.instance`, `storage.volume`, `network.floating_ip`.
- Quota methods use `self._conn.current_project_id` to scope queries.
- All errors are logged and methods return empty dicts/lists rather than raising.

## Integration Points

- **Depends on**: `codomyrmex.cloud.infomaniak.base.InfomaniakOpenStackBase`, `openstacksdk` (Nova, Cinder, Neutron, Swift proxies)
- **Used by**: `codomyrmex.cloud.infomaniak` (parent), cost management module

## Navigation

- **Parent**: [infomaniak](../AGENTS.md)
- **Root**: [../../../../../README.md](../../../../../README.md)
