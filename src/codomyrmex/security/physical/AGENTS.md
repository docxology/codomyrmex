# Codomyrmex Agents — src/codomyrmex/security/physical

## Signposting
- **Parent**: [security](../AGENTS.md)
- **Self**: [Physical Security Agents](AGENTS.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

The Physical Security submodule provides physical security practices, access control systems, surveillance monitoring, physical asset protection, physical vulnerability assessment, and security perimeter management for the Codomyrmex platform.

This submodule handles the physical aspects of security, complementing digital and cognitive security measures to provide comprehensive security coverage.

## Module Overview

### Key Capabilities
- **Access Control**: Manage physical access permissions and authorization
- **Asset Inventory**: Track and manage physical assets
- **Surveillance**: Monitor physical access events and security incidents
- **Vulnerability Assessment**: Assess physical security vulnerabilities
- **Perimeter Management**: Manage security perimeter and access points

### Key Features
- Access permission management with expiration
- Physical asset registration and tracking
- Physical event logging and monitoring
- Physical vulnerability scanning
- Security perimeter configuration

## Function Signatures

### Access Control Functions

```python
def check_access_permission(
    user_id: str,
    resource: str,
    permission_type: str,
    access_control: Optional[AccessControlSystem] = None,
) -> bool
```

Check if a user has access permission to a resource.

**Parameters:**
- `user_id` (str): User identifier
- `resource` (str): Resource identifier
- `permission_type` (str): Type of permission (read, write, admin)
- `access_control` (Optional[AccessControlSystem]): Optional access control system instance

**Returns:** `bool` - True if user has permission, False otherwise

```python
def grant_access(
    user_id: str,
    resource: str,
    permission_type: str,
    expires_at: Optional[datetime] = None,
    access_control: Optional[AccessControlSystem] = None,
) -> AccessPermission
```

Grant access permission to a user.

**Parameters:**
- `user_id` (str): User identifier
- `resource` (str): Resource identifier
- `permission_type` (str): Type of permission (read, write, admin)
- `expires_at` (Optional[datetime]): Optional expiration datetime
- `access_control` (Optional[AccessControlSystem]): Optional access control system instance

**Returns:** `AccessPermission` - Created permission object

```python
def revoke_access(
    user_id: str,
    resource: str,
    access_control: Optional[AccessControlSystem] = None,
) -> bool
```

Revoke access permission for a user.

**Parameters:**
- `user_id` (str): User identifier
- `resource` (str): Resource identifier
- `access_control` (Optional[AccessControlSystem]): Optional access control system instance

**Returns:** `bool` - True if permission was revoked, False if not found

### Asset Inventory Functions

```python
def register_asset(
    asset_id: str,
    name: str,
    asset_type: str,
    location: str,
    inventory: Optional[AssetInventory] = None,
) -> PhysicalAsset
```

Register a new physical asset.

**Parameters:**
- `asset_id` (str): Unique asset identifier
- `name` (str): Asset name
- `asset_type` (str): Type of asset
- `location` (str): Asset location
- `inventory` (Optional[AssetInventory]): Optional asset inventory instance

**Returns:** `PhysicalAsset` - Registered asset object

```python
def track_asset(
    asset_id: str,
    location: Optional[str] = None,
    inventory: Optional[AssetInventory] = None,
) -> bool
```

Update asset tracking information.

**Parameters:**
- `asset_id` (str): Asset identifier
- `location` (Optional[str]): Optional new location
- `inventory` (Optional[AssetInventory]): Optional asset inventory instance

**Returns:** `bool` - True if tracking updated, False if asset not found

```python
def get_asset_status(
    asset_id: str,
    inventory: Optional[AssetInventory] = None,
) -> Optional[PhysicalAsset]
```

Get asset status and information.

**Parameters:**
- `asset_id` (str): Asset identifier
- `inventory` (Optional[AssetInventory]): Optional asset inventory instance

**Returns:** `Optional[PhysicalAsset]` - Asset object or None if not found

### Surveillance Functions

```python
def monitor_physical_access(
    location: str,
    user_id: str,
    monitor: Optional[SurveillanceMonitor] = None,
) -> PhysicalEvent
```

Monitor physical access event.

**Parameters:**
- `location` (str): Location where access occurred
- `user_id` (str): User identifier
- `monitor` (Optional[SurveillanceMonitor]): Optional surveillance monitor instance

**Returns:** `PhysicalEvent` - Logged physical event

```python
def log_physical_event(
    event_type: str,
    location: str,
    description: str,
    severity: str = "medium",
    monitor: Optional[SurveillanceMonitor] = None,
) -> PhysicalEvent
```

Log a physical security event.

**Parameters:**
- `event_type` (str): Type of event (access, movement, alarm, etc.)
- `location` (str): Event location
- `description` (str): Event description
- `severity` (str): Event severity (low, medium, high, critical)
- `monitor` (Optional[SurveillanceMonitor]): Optional surveillance monitor instance

**Returns:** `PhysicalEvent` - Logged physical event

### Physical Vulnerability Assessment Functions

```python
def scan_physical_vulnerabilities(
    location: str,
    scanner: Optional[PhysicalVulnerabilityScanner] = None,
) -> List[PhysicalVulnerability]
```

Scan for physical vulnerabilities at a location.

**Parameters:**
- `location` (str): Location to scan
- `scanner` (Optional[PhysicalVulnerabilityScanner]): Optional vulnerability scanner instance

**Returns:** `List[PhysicalVulnerability]` - List of identified vulnerabilities

```python
def assess_physical_security(
    location: str,
    scanner: Optional[PhysicalVulnerabilityScanner] = None,
) -> dict
```

Assess overall physical security at a location.

**Parameters:**
- `location` (str): Location to assess
- `scanner` (Optional[PhysicalVulnerabilityScanner]): Optional vulnerability scanner instance

**Returns:** `dict` - Assessment results with vulnerability counts and details

### Perimeter Management Functions

```python
def check_perimeter_security(
    manager: Optional[PerimeterManager] = None,
) -> dict
```

Check overall perimeter security status.

**Parameters:**
- `manager` (Optional[PerimeterManager]): Optional perimeter manager instance

**Returns:** `dict` - Perimeter security status with access point counts

```python
def manage_access_points(
    manager: Optional[PerimeterManager] = None,
) -> List[AccessPoint]
```

Get all access points.

**Parameters:**
- `manager` (Optional[PerimeterManager]): Optional perimeter manager instance

**Returns:** `List[AccessPoint]` - List of all access points

## Active Components

### Core Implementation
- `__init__.py` – Module initialization and public API exports
- `access_control.py` – Access control system management
- `asset_inventory.py` – Physical asset inventory management
- `surveillance.py` – Physical surveillance monitoring
- `physical_vulnerability.py` – Physical vulnerability assessment
- `perimeter_management.py` – Security perimeter management


### Additional Files
- `README.md` – Readme Md
- `SPEC.md` – Spec Md
- `__pycache__` –   Pycache  

## Operating Contracts

### Universal Physical Security Protocols

All physical security operations within the Codomyrmex platform must:

1. **Access Control**: Enforce least privilege principles
2. **Asset Tracking**: Maintain accurate asset inventory
3. **Event Logging**: Log all physical security events
4. **Vulnerability Assessment**: Regular physical security assessments
5. **Perimeter Security**: Monitor and manage access points

### Module-Specific Guidelines

#### Access Control
- Support permission expiration
- Track permission grants and revocations
- Support multiple permission types (read, write, admin)

#### Asset Inventory
- Register all physical assets
- Track asset locations
- Monitor asset status

#### Surveillance
- Log all physical access events
- Support multiple event types
- Categorize events by severity

## Related Modules
- **Security** (`../`) - Parent security module
- **Digital Security** (`../digital/`) - Digital security complement
- **Cognitive Security** (`../cognitive/`) - Cognitive security complement
- **Logging Monitoring** (`../../logging_monitoring/`) - Event logging integration

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)

### Module Documentation
- **Module Overview**: [README.md](README.md) - Complete module documentation

### Platform Navigation
- **Parent Directory**: [security](../README.md) - Security module overview
- **Project Root**: [README](../../../../README.md) - Main project documentation
- **Source Root**: [src](../../../../README.md) - Source code documentation

