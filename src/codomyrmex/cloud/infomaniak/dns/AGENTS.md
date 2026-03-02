# Codomyrmex Agents -- src/codomyrmex/cloud/infomaniak/dns

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Provides DNS management for Infomaniak Public Cloud via the OpenStack Designate API. Handles DNS zones (create, update, delete), record sets (A, AAAA, CNAME, MX, TXT, etc.), and reverse DNS (PTR records) for floating IPs. Note: the DNS service is currently in BETA at Infomaniak.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `client.py` | `InfomaniakDNSClient` | Designate client extending `InfomaniakOpenStackBase`; `_service_name = "dns"` |
| `client.py` | `list_zones()` | List all DNS zones |
| `client.py` | `get_zone(zone_id)` | Get zone by ID or name |
| `client.py` | `create_zone(name, email, ttl, description)` | Create zone (auto-appends trailing dot to name) |
| `client.py` | `delete_zone(zone_id)` | Delete a DNS zone |
| `client.py` | `update_zone(zone_id, email, ttl, description)` | Update zone attributes |
| `client.py` | `list_records(zone_id)` | List all record sets in a zone |
| `client.py` | `get_record(zone_id, record_id)` | Get a specific record set |
| `client.py` | `create_record(zone_id, name, record_type, records, ttl, description)` | Create record set (auto-appends trailing dot) |
| `client.py` | `update_record(zone_id, record_id, records, ttl, description)` | Update record values/TTL |
| `client.py` | `delete_record(zone_id, record_id)` | Delete a record set |
| `client.py` | `list_ptr_records()` | List all PTR (reverse DNS) records |
| `client.py` | `set_reverse_dns(floating_ip, hostname, ttl, description)` | Set PTR record for a floating IP (resolves FIP via network API) |
| `client.py` | `get_reverse_dns(floating_ip)` | Get PTR record for a floating IP |
| `client.py` | `delete_reverse_dns(floating_ip)` | Delete PTR record for a floating IP |

## Operating Contracts

- Zone and record names must end with a trailing dot (`.`); `create_zone` and `create_record` auto-append it if missing.
- PTR operations (`set_reverse_dns`, `get_reverse_dns`, `delete_reverse_dns`) first resolve the floating IP address to an FIP ID via `self._conn.network.find_ip`.
- All errors are logged and methods return sentinel values rather than raising.
- The DNS service is BETA; API behavior may change.

## Integration Points

- **Depends on**: `codomyrmex.cloud.infomaniak.base.InfomaniakOpenStackBase`, `openstacksdk` (Designate and Neutron proxies)
- **Used by**: `codomyrmex.cloud.infomaniak` (parent)

## Navigation

- **Parent**: [infomaniak](../AGENTS.md)
- **Root**: [../../../../../README.md](../../../../../README.md)
