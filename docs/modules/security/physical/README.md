# Security Physical Submodule

**Version**: v0.1.0 | **Source**: [`src/codomyrmex/security/physical/`](../../../../src/codomyrmex/security/physical/)

## Overview

Physical security practices including access control, asset inventory management, surveillance monitoring, physical vulnerability scanning, and perimeter management. Organized across 5 component files, each conditionally imported.

## Components

| Source File | Classes / Functions | Availability Flag |
|-------------|--------------------|--------------------|
| `access_control.py` | `AccessControlSystem`, `check_access_permission()`, `grant_access()`, `revoke_access()` | `ACCESS_CONTROL_AVAILABLE` |
| `asset_inventory.py` | `AssetInventory`, `register_asset()`, `track_asset()`, `get_asset_status()` | `ASSET_INVENTORY_AVAILABLE` |
| `surveillance.py` | `SurveillanceMonitor`, `monitor_physical_access()`, `log_physical_event()` | `SURVEILLANCE_AVAILABLE` |
| `physical_vulnerability.py` | `PhysicalVulnerabilityScanner`, `assess_physical_security()`, `scan_physical_vulnerabilities()` | `PHYSICAL_VULNERABILITY_AVAILABLE` |
| `perimeter_management.py` | `PerimeterManager`, `check_perimeter_security()`, `manage_access_points()` | `PERIMETER_MANAGEMENT_AVAILABLE` |

## Exports (via top-level `security/__init__.py`)

When `PHYSICAL_AVAILABLE` is `True`, the following 17 symbols are re-exported:
- `AccessControlSystem`, `check_access_permission`, `grant_access`, `revoke_access`
- `AssetInventory`, `register_asset`, `track_asset`, `get_asset_status`
- `SurveillanceMonitor`, `monitor_physical_access`, `log_physical_event`
- `PhysicalVulnerabilityScanner`, `assess_physical_security`, `scan_physical_vulnerabilities`
- `PerimeterManager`, `check_perimeter_security`, `manage_access_points`

## Convenience Functions (12)

| Function | Description |
|----------|-------------|
| `check_access_permission()` | Check if access is permitted |
| `grant_access()` | Grant access to a resource |
| `revoke_access()` | Revoke access from a resource |
| `register_asset()` | Register a physical asset |
| `track_asset()` | Track asset location/status |
| `get_asset_status()` | Get current asset status |
| `monitor_physical_access()` | Monitor physical access events |
| `log_physical_event()` | Log a physical security event |
| `assess_physical_security()` | Run physical security assessment |
| `scan_physical_vulnerabilities()` | Scan for physical vulnerabilities |
| `check_perimeter_security()` | Check perimeter security status |
| `manage_access_points()` | Manage physical access points |

## Implementation Details

- Access control includes AccessLevel enum (5 levels from PUBLIC to TOP_SECRET) with full audit trail on grant/revoke operations
- Asset inventory includes AssetType enum (8 types) with update_status(), list_assets() filtering, and decommission_asset() methods
- Surveillance includes EventType enum (8 types) with get_events() multi-criteria filtering and get_recent_events()
- Perimeter management includes AccessPointType (8 types) and SecurityLevel (5 levels) enums with get_vulnerable_points() method
- Physical vulnerability scanner accepts optional references to other subsystems and performs real vulnerability checks (expired permissions, low-security access points, surveillance gaps, stale assets)

## Tests

[`src/codomyrmex/tests/unit/security/test_security_physical.py`](../../../../src/codomyrmex/tests/unit/security/test_security_physical.py)

## Navigation

- **Parent**: [Security Module](../README.md)
- **Source**: [`src/codomyrmex/security/physical/`](../../../../src/codomyrmex/security/physical/)
