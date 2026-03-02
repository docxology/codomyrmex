from dataclasses import dataclass
from enum import Enum

from codomyrmex.logging_monitoring.core.logger_config import get_logger

"""Physical perimeter security management."""

logger = get_logger(__name__)

# Global singleton instance for functional wrappers
_GLOBAL_PERIMETER = None


def get_perimeter_manager() -> "PerimeterManager":
    """Get or create the global PerimeterManager instance."""
    global _GLOBAL_PERIMETER
    if _GLOBAL_PERIMETER is None:
        _GLOBAL_PERIMETER = PerimeterManager()
    return _GLOBAL_PERIMETER


class AccessPointType(Enum):
    """Types of physical access points."""
    DOOR = "door"
    GATE = "gate"
    WINDOW = "window"
    LOADING_DOCK = "loading_dock"
    EMERGENCY_EXIT = "emergency_exit"
    ROOF_ACCESS = "roof_access"
    UNDERGROUND = "underground"
    VEHICLE_ENTRY = "vehicle_entry"


class SecurityLevel(Enum):
    """Security levels for access points and perimeter zones."""
    MINIMAL = "minimal"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    MAXIMUM = "maximum"


@dataclass
class AccessPoint:
    """Represents a physical access point."""

    point_id: str
    location: str
    access_type: str  # door, gate, window, etc.
    security_level: str  # low, medium, high
    status: str  # active, inactive, maintenance


class PerimeterManager:
    """Manages physical perimeter security."""

    def __init__(self):

        self.access_points: dict[str, AccessPoint] = {}
        logger.info("PerimeterManager initialized")

    def register_access_point(
        self,
        point_id: str,
        location: str,
        access_type: str,
        security_level: str = "medium",
    ) -> AccessPoint:
        """Register a new access point."""
        point = AccessPoint(
            point_id=point_id,
            location=location,
            access_type=access_type,
            security_level=security_level,
            status="active",
        )
        self.access_points[point_id] = point
        logger.info(f"Registered access point {point_id} at {location}")
        return point

    def check_perimeter_security(self) -> dict:
        """Check overall perimeter security status."""
        total_points = len(self.access_points)
        active_points = sum(1 for p in self.access_points.values() if p.status == "active")

        status = {
            "total_access_points": total_points,
            "active_points": active_points,
            "inactive_points": total_points - active_points,
            "security_coverage": active_points / total_points if total_points > 0 else 0,
        }

        logger.info(f"Checked perimeter security: {active_points}/{total_points} active")
        return status

    def manage_access_points(self) -> list[AccessPoint]:
        """Get all access points."""
        return list(self.access_points.values())

    def get_vulnerable_points(self) -> list[AccessPoint]:
        """Return access points with low security level or non-active status."""
        return [
            point for point in self.access_points.values()
            if point.security_level == "low" or point.status != "active"
        ]


def check_perimeter_security(
    manager: PerimeterManager | None = None,
) -> dict:
    """Check perimeter security."""
    if manager is None:
        manager = get_perimeter_manager()
    return manager.check_perimeter_security()


def manage_access_points(
    manager: PerimeterManager | None = None,
) -> list[AccessPoint]:
    """Manage access points."""
    if manager is None:
        manager = get_perimeter_manager()
    return manager.manage_access_points()


