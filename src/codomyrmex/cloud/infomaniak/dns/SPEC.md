# DNS -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Wraps the OpenStack Designate API for Infomaniak Public Cloud DNS management. Provides zone CRUD, record set management for all standard DNS types, and reverse DNS (PTR) record management tied to floating IPs.

## Architecture

Single-class design. `InfomaniakDNSClient` extends `InfomaniakOpenStackBase` with `_service_name = "dns"`. Zone and record operations use `self._conn.dns.*`. PTR operations additionally use `self._conn.network.find_ip` to resolve floating IP addresses to OpenStack FIP IDs.

## Key Methods

### Zone Operations

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `list_zones` | (none) | `list[dict]` | List all zones (id, name, email, status, type, ttl) |
| `get_zone` | `zone_id: str` | `dict or None` | Find zone by ID or name |
| `create_zone` | `name, email, ttl: int = 3600, description` | `dict or None` | Create zone (auto-appends trailing dot) |
| `delete_zone` | `zone_id: str` | `bool` | Delete zone |
| `update_zone` | `zone_id, email, ttl, description` | `bool` | Update zone attributes |

### Record Set Operations

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `list_records` | `zone_id: str` | `list[dict]` | List records (id, name, type, records, ttl, status) |
| `get_record` | `zone_id, record_id` | `dict or None` | Get specific record set |
| `create_record` | `zone_id, name, record_type, records: list[str], ttl, description` | `dict or None` | Create record (auto-appends dot) |
| `update_record` | `zone_id, record_id, records, ttl, description` | `bool` | Update record values |
| `delete_record` | `zone_id, record_id` | `bool` | Delete record set |

### Reverse DNS (PTR) Operations

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `list_ptr_records` | (none) | `list[dict]` | List all PTR records |
| `set_reverse_dns` | `floating_ip, hostname, ttl, description` | `dict or None` | Set PTR for floating IP |
| `get_reverse_dns` | `floating_ip: str` | `dict or None` | Get PTR for floating IP |
| `delete_reverse_dns` | `floating_ip: str` | `bool` | Delete PTR for floating IP |

## Dependencies

- **Internal**: `codomyrmex.cloud.infomaniak.base.InfomaniakOpenStackBase`
- **External**: `openstacksdk` (Designate proxy, Neutron proxy for FIP resolution), `logging`

## Constraints

- Zone and record names in DNS must end with a trailing dot (RFC 1035). `create_zone` and `create_record` auto-append it if missing.
- PTR operations resolve floating IP address strings to OpenStack FIP IDs via `self._conn.network.find_ip`; the operation fails if the FIP is not found.
- The DNS service is marked BETA at Infomaniak; API endpoints may change.
- Supported record types include A, AAAA, CNAME, MX, TXT, and others supported by Designate.

## Error Handling

- All methods catch `Exception`, log via `logger.error`, and return sentinel values.
- No exceptions propagate to callers.
