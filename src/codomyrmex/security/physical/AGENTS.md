# Codomyrmex Agents — src/codomyrmex/security/physical

## Signposting
- **Parent**: [security](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose
Physical security including access control, asset inventory, perimeter management, physical vulnerability assessment, and surveillance. Focuses on physical security threats and infrastructure protection.

## Active Components
- `README.md` – Project file
- `SPEC.md` – Project file
- `__init__.py` – Module exports and public API
- `access_control.py` – Access control management
- `asset_inventory.py` – Asset inventory and tracking
- `perimeter_management.py` – Perimeter security management
- `physical_vulnerability.py` – Physical vulnerability assessment
- `surveillance.py` – Surveillance and monitoring

## Key Classes and Functions

### AccessControl (`access_control.py`)
- `AccessControl()` – Access control management
- `check_access(user: str, resource: str) -> bool` – Check access permissions
- `grant_access(user: str, resource: str) -> None` – Grant access

### AssetInventory (`asset_inventory.py`)
- `AssetInventory()` – Asset inventory and tracking
- `register_asset(asset: dict) -> str` – Register asset
- `get_asset(asset_id: str) -> dict` – Get asset information

### PerimeterManagement (`perimeter_management.py`)
- `PerimeterManagement()` – Perimeter security management
- `monitor_perimeter() -> Iterator[SecurityEvent]` – Monitor perimeter

### PhysicalVulnerability (`physical_vulnerability.py`)
- `PhysicalVulnerability()` – Physical vulnerability assessment
- `assess_vulnerability(location: str) -> VulnerabilityAssessment` – Assess physical vulnerability

### Surveillance (`surveillance.py`)
- `Surveillance()` – Surveillance and monitoring
- `monitor_area(area: str) -> Iterator[SurveillanceEvent]` – Monitor area

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **📁 Parent Directory**: [security](../README.md) - Parent directory documentation
- **🏠 Project Root**: [README](../../../../README.md) - Main project documentation