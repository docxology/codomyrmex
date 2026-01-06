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
    AccessControlSystem = None
    check_access_permission = None
    grant_access = None
    revoke_access = None
    ACCESS_CONTROL_AVAILABLE = False

try:
    from .asset_inventory import (
        AssetInventory,
        register_asset,
        track_asset,
        get_asset_status,
    )
    ASSET_INVENTORY_AVAILABLE = True
except ImportError:
    AssetInventory = None
    register_asset = None
    track_asset = None
    get_asset_status = None
    ASSET_INVENTORY_AVAILABLE = False

try:
    from .surveillance import (
        SurveillanceMonitor,
        monitor_physical_access,
        log_physical_event,
    )
    SURVEILLANCE_AVAILABLE = True
except ImportError:
    SurveillanceMonitor = None
    monitor_physical_access = None
    log_physical_event = None
    SURVEILLANCE_AVAILABLE = False

try:
    from .physical_vulnerability import (
        PhysicalVulnerabilityScanner,
        assess_physical_security,
        scan_physical_vulnerabilities,
    )
    PHYSICAL_VULNERABILITY_AVAILABLE = True
except ImportError:
    PhysicalVulnerabilityScanner = None
    assess_physical_security = None
    scan_physical_vulnerabilities = None
    PHYSICAL_VULNERABILITY_AVAILABLE = False

try:
    from .perimeter_management import (
        PerimeterManager,
        check_perimeter_security,
        manage_access_points,
    )
    PERIMETER_MANAGEMENT_AVAILABLE = True
except ImportError:
    PerimeterManager = None
    check_perimeter_security = None
    manage_access_points = None
    PERIMETER_MANAGEMENT_AVAILABLE = False

__all__ = []

if ACCESS_CONTROL_AVAILABLE:
    __all__.extend([
        "AccessControlSystem",
        "check_access_permission",
        "grant_access",
        "revoke_access",
    ])

if ASSET_INVENTORY_AVAILABLE:
    __all__.extend([
        "AssetInventory",
        "register_asset",
        "track_asset",
        "get_asset_status",
    ])

if SURVEILLANCE_AVAILABLE:
    __all__.extend([
        "SurveillanceMonitor",
        "monitor_physical_access",
        "log_physical_event",
    ])

if PHYSICAL_VULNERABILITY_AVAILABLE:
    __all__.extend([
        "PhysicalVulnerabilityScanner",
        "assess_physical_security",
        "scan_physical_vulnerabilities",
    ])

if PERIMETER_MANAGEMENT_AVAILABLE:
    __all__.extend([
        "PerimeterManager",
        "check_perimeter_security",
        "manage_access_points",
    ])


