# Metering -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Provides resource usage aggregation and quota reporting for Infomaniak Public Cloud by querying Nova, Cinder, Neutron, and Swift APIs directly through `InfomaniakMeteringClient`.

## Architecture

Single-class design. `InfomaniakMeteringClient` extends `InfomaniakOpenStackBase` with `_service_name = "metering"`. Rather than using a dedicated metering API, it computes usage by listing resources from each OpenStack service and aggregating metrics in Python.

## Key Methods

### Usage Aggregation

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `get_compute_usage` | `start: datetime or None, end: datetime or None` | `dict` | Instance count, total vcpus/ram/disk by summing flavors |
| `get_storage_usage` | (none) | `dict` | Volume count, total GB, attached vs unattached |
| `get_network_usage` | (none) | `dict` | Counts of networks, routers, security groups, floating IPs (total and in-use) |
| `get_object_storage_usage` | (none) | `dict` | Container count, object count, total bytes and GB |
| `get_all_usage` | (none) | `dict` | All four services combined with UTC `timestamp` |
| `list_resources_with_usage` | (none) | `list[dict]` | Flat resource list with type prefix and status |

### Quota Reporting

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `get_compute_quotas` | (none) | `dict` | instances, cores, ram_mb, key_pairs, server_groups |
| `get_network_quotas` | (none) | `dict` | networks, subnets, routers, floating_ips, security_groups, security_group_rules |
| `get_storage_quotas` | (none) | `dict` | volumes, gigabytes, snapshots, backups |

## Dependencies

- **Internal**: `codomyrmex.cloud.infomaniak.base.InfomaniakOpenStackBase`
- **External**: `openstacksdk` (Nova, Cinder, Neutron, Swift proxies), `datetime`, `logging`

## Constraints

- `get_compute_usage` performs N+1 API calls: lists all servers, then calls `get_flavor` per server to resolve resource values. This can be slow for large instance counts.
- `get_network_usage` counts floating IPs in use by checking `fip.port_id` truthiness.
- `get_object_storage_usage` sums `container.count` and `container.bytes` across all Swift containers.
- `list_resources_with_usage` catches exceptions per-resource-type independently, so partial results are returned if one API fails.
- Quota methods use `self._conn.current_project_id` for project scoping.

## Error Handling

- Usage methods catch broad `Exception` per service and return empty dicts.
- `list_resources_with_usage` logs warnings (not errors) for per-type failures and continues collecting other resource types.
- Quota methods catch exceptions and return empty dicts.
