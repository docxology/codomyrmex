# Codomyrmex Agents — src/codomyrmex/security/physical

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Physical security management covering access control with permission expiration, asset inventory with lifecycle tracking, surveillance event monitoring, perimeter access point management, and cross-system physical vulnerability scanning.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `access_control.py` | `AccessControlSystem` | Permission management: `grant_access()`, `revoke_access()`, `check_access()`, `list_permissions()` with expiration-aware checks |
| `access_control.py` | `AccessLevel` | Enum: `PUBLIC`, `RESTRICTED`, `CONFIDENTIAL`, `SECRET`, `TOP_SECRET` |
| `access_control.py` | `AccessPermission` | Dataclass with `user_id`, `resource`, `permission_type`, `granted_at`, optional `expires_at` |
| `asset_inventory.py` | `AssetInventory` | Asset lifecycle: `register_asset()`, `track_asset()`, `update_status()`, `list_assets()` (filterable by type/status), `decommission_asset()` |
| `asset_inventory.py` | `AssetType` | Enum: `SERVER`, `WORKSTATION`, `NETWORK_DEVICE`, `STORAGE`, `MOBILE_DEVICE`, `SECURITY_DEVICE`, `PERIPHERAL`, `OTHER` |
| `surveillance.py` | `SurveillanceMonitor` | Event logging: `log_event()`, `monitor_physical_access()`, `get_events()` (filterable), `get_recent_events()` |
| `surveillance.py` | `EventType` | Enum: `ACCESS`, `MOVEMENT`, `ALARM`, `INTRUSION`, `TAILGATING`, `MAINTENANCE`, `ENVIRONMENTAL`, `EMERGENCY` |
| `perimeter_management.py` | `PerimeterManager` | Access point registry: `register_access_point()`, `check_perimeter_security()`, `get_vulnerable_points()` |
| `perimeter_management.py` | `AccessPointType` | Enum: `DOOR`, `GATE`, `WINDOW`, `LOADING_DOCK`, `EMERGENCY_EXIT`, `ROOF_ACCESS`, `UNDERGROUND`, `VEHICLE_ENTRY` |
| `physical_vulnerability.py` | `PhysicalVulnerabilityScanner` | Cross-system scanner checking expired permissions, low-security access points, surveillance gaps, and stale assets (90-day threshold) |

## Operating Contracts

- `AccessControlSystem.check_access()` respects `expires_at` and grants access for `admin` permission type regardless of requested type.
- `AccessControlSystem` and `AssetInventory` maintain internal audit trails of grant/revoke actions.
- `PhysicalVulnerabilityScanner` accepts optional subsystem instances; missing subsystems are skipped (not errored).
- Stale asset threshold is hardcoded at 90 days in `PhysicalVulnerabilityScanner`.
- Global singleton instances available via `get_access_control_system()`, `get_asset_inventory()`, `get_perimeter_manager()`.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: `codomyrmex.logging_monitoring.core.logger_config`
- **Internal cross-deps**: `physical_vulnerability.py` imports from all four sibling modules
- **Used by**: Physical security dashboards, compliance audits

## Navigation

- **Parent**: [security](../README.md)
- **Root**: [Root](../../../../README.md)
