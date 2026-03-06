"""
Physical Security Submodule for Codomyrmex Security Module.

The Physical Security submodule provides physical security practices, access control,
surveillance monitoring, physical asset protection, and physical vulnerability assessment.
"""

try:
    from .access_control import (
        AccessControlSystem,
        check_access_permission,
        grant_access,
        revoke_access,
    )

    ACCESS_CONTROL_AVAILABLE = True
except ImportError:
    ACCESS_CONTROL_AVAILABLE = False

try:
    from .asset_inventory import (
        AssetInventory,
        get_asset_status,
        register_asset,
        track_asset,
    )

    ASSET_INVENTORY_AVAILABLE = True
except ImportError:
    ASSET_INVENTORY_AVAILABLE = False

try:
    from .surveillance import (
        SurveillanceMonitor,
        log_physical_event,
        monitor_physical_access,
    )

    SURVEILLANCE_AVAILABLE = True
except ImportError:
    SURVEILLANCE_AVAILABLE = False

try:
    from .physical_vulnerability import (
        PhysicalVulnerabilityScanner,
        assess_physical_security,
        scan_physical_vulnerabilities,
    )

    PHYSICAL_VULNERABILITY_AVAILABLE = True
except ImportError:
    PHYSICAL_VULNERABILITY_AVAILABLE = False

try:
    from .perimeter_management import (
        PerimeterManager,
        check_perimeter_security,
        manage_access_points,
    )

    PERIMETER_MANAGEMENT_AVAILABLE = True
except ImportError:
    PERIMETER_MANAGEMENT_AVAILABLE = False

__all__ = []

if ACCESS_CONTROL_AVAILABLE:
    __all__.extend(
        [
            "AccessControlSystem",
            "check_access_permission",
            "grant_access",
            "revoke_access",
        ]
    )

if ASSET_INVENTORY_AVAILABLE:
    __all__.extend(
        [
            "AssetInventory",
            "get_asset_status",
            "register_asset",
            "track_asset",
        ]
    )

if SURVEILLANCE_AVAILABLE:
    __all__.extend(
        [
            "SurveillanceMonitor",
            "log_physical_event",
            "monitor_physical_access",
        ]
    )

if PHYSICAL_VULNERABILITY_AVAILABLE:
    __all__.extend(
        [
            "PhysicalVulnerabilityScanner",
            "assess_physical_security",
            "scan_physical_vulnerabilities",
        ]
    )

if PERIMETER_MANAGEMENT_AVAILABLE:
    __all__.extend(
        [
            "PerimeterManager",
            "check_perimeter_security",
            "manage_access_points",
        ]
    )
