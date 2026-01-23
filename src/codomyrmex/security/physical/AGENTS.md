# Codomyrmex Agents — src/codomyrmex/security/physical

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

Provides physical security management capabilities including access control systems, asset inventory tracking, perimeter security management, surveillance monitoring, and physical vulnerability assessment.

## Active Components

- `access_control.py` - Access permission management with `AccessControlSystem`
- `asset_inventory.py` - Physical asset tracking with `AssetInventory`
- `perimeter_management.py` - Perimeter security with `PerimeterManager`
- `surveillance.py` - Event monitoring with `SurveillanceMonitor`
- `physical_vulnerability.py` - Vulnerability scanning with `PhysicalVulnerabilityScanner`
- `__init__.py` - Module exports with conditional availability

## Key Classes and Functions

### access_control.py
- **`AccessControlSystem`** - Manages physical access permissions:
  - `grant_access(user_id, resource, permission_type, expires_at)` - Grant access permission.
  - `revoke_access(user_id, resource)` - Revoke access permission.
  - `check_access(user_id, resource, permission_type)` - Check if user has access.
- **`AccessPermission`** - Dataclass with user_id, resource, permission_type, granted_at, expires_at.
- **Convenience Functions**: `check_access_permission()`, `grant_access()`, `revoke_access()`.
- **Global Singleton**: `get_access_control_system()` returns shared instance.

### asset_inventory.py
- **`AssetInventory`** - Manages physical asset tracking:
  - `register_asset(asset_id, name, asset_type, location)` - Register new asset.
  - `track_asset(asset_id, location)` - Update asset location and last checked time.
  - `get_asset_status(asset_id)` - Get current asset status.
- **`PhysicalAsset`** - Dataclass with asset_id, name, asset_type, location, status, registered_at, last_checked.
- **Convenience Functions**: `register_asset()`, `track_asset()`, `get_asset_status()`.

### perimeter_management.py
- **`PerimeterManager`** - Manages physical perimeter security:
  - `register_access_point(point_id, location, access_type, security_level)` - Register access point.
  - `check_perimeter_security()` - Check overall perimeter status with coverage metrics.
  - `manage_access_points()` - Get all registered access points.
- **`AccessPoint`** - Dataclass with point_id, location, access_type (door, gate, window), security_level, status.
- **Convenience Functions**: `check_perimeter_security()`, `manage_access_points()`.

### surveillance.py
- **`SurveillanceMonitor`** - Monitors physical security events:
  - `log_event(event_type, location, description, severity)` - Log a physical event.
  - `monitor_physical_access(location, user_id)` - Monitor and log physical access.
- **`PhysicalEvent`** - Dataclass with event_id, event_type (access, movement, alarm), location, timestamp, description, severity.
- **Convenience Functions**: `monitor_physical_access()`, `log_physical_event()`.

### physical_vulnerability.py
- **`PhysicalVulnerabilityScanner`** - Scans for physical security vulnerabilities:
  - `scan_vulnerabilities(location)` - Scan location for vulnerabilities.
  - `assess_physical_security(location)` - Comprehensive security assessment with counts by severity.
- **`PhysicalVulnerability`** - Dataclass with vulnerability_id, location, vulnerability_type, severity, description, recommendation.
- **Convenience Functions**: `scan_physical_vulnerabilities()`, `assess_physical_security()`.

## Operating Contracts

- Access permissions support expiration times for temporary access.
- Permission types include: read, write, admin (admin grants all access).
- Asset status values: active, inactive, maintenance, lost.
- Security levels for access points: low, medium, high.
- Event severities: low, medium, high, critical.
- Global singleton instances available for convenient functional API usage.
- All components log operations for audit trail.

## Signposting

- **Dependencies**: None (pure Python implementation).
- **Parent Directory**: [security](../README.md) - Parent module documentation.
- **Related Modules**:
  - `digital/` - Digital security controls.
  - `cognitive/` - Human factor security.
  - `theory/` - Security frameworks and best practices.
- **Project Root**: [../../../../README.md](../../../../README.md) - Main project documentation.
