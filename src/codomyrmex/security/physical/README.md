# physical

## Signposting
- **Parent**: [security](../README.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

Physical security including access control, asset inventory, perimeter management, physical vulnerability assessment, and surveillance. Focuses on physical security threats and infrastructure protection.

## Directory Contents
- `README.md` – File
- `SPEC.md` – File
- `__init__.py` – File
- `access_control.py` – File
- `asset_inventory.py` – File
- `perimeter_management.py` – File
- `physical_vulnerability.py` – File
- `surveillance.py` – File

## Navigation
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [security](../README.md)
- **Project Root**: [README](../../../../README.md)

## Getting Started

To use this module in your project, import the necessary components:

```python
from codomyrmex.security.physical import (
    AccessControlManager,
    AssetInventory,
    PerimeterManager,
)

# Manage access control
access_control = AccessControlManager()
access_control.grant_access(user_id="user123", resource="server_room")
has_access = access_control.check_access(user_id="user123", resource="server_room")

# Track assets
inventory = AssetInventory()
inventory.add_asset(asset_id="server_01", location="data_center", type="server")
assets = inventory.list_assets()

# Manage perimeter
perimeter = PerimeterManager()
perimeter.set_zone(zone_id="zone_1", access_level="restricted")
status = perimeter.get_zone_status("zone_1")
```

