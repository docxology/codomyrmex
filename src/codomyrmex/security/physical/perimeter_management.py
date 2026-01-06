"""Physical perimeter security management."""

from dataclasses import dataclass
from typing import List, Optional

from codomyrmex.logging_monitoring.logger_config import get_logger

logger = get_logger(__name__)


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
    
    def manage_access_points(self) -> List[AccessPoint]:
        """Get all access points."""
        return list(self.access_points.values())


def check_perimeter_security(
    manager: Optional[PerimeterManager] = None,
) -> dict:
    """Check perimeter security."""
    if manager is None:
        manager = PerimeterManager()
    return manager.check_perimeter_security()


def manage_access_points(
    manager: Optional[PerimeterManager] = None,
) -> List[AccessPoint]:
    """Manage access points."""
    if manager is None:
        manager = PerimeterManager()
    return manager.manage_access_points()


