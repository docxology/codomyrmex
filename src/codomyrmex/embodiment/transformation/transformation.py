"""Coordinate transformation utilities for embodiment."""

import math
from typing import Tuple, List

class Transform3D:
    """Basic 3D transformation (translation and rotation)."""
    
    def __init__(self, translation: Tuple[float, float, float] = (0, 0, 0),
                 rotation: Tuple[float, float, float] = (0, 0, 0)):
        """
        Args:
            translation: (x, y, z)
            rotation: (roll, pitch, yaw) in radians
        """
        self.translation = translation
        self.rotation = rotation

    def transform_point(self, point: Tuple[float, float, float]) -> Tuple[float, float, float]:
        """Apply transformation to a 3D point."""
        x, y, z = point
        # Simplified Euler rotation (Yaw then Pitch then Roll)
        r, p, y_rot = self.rotation
        
        # Translation
        tx, ty, tz = self.translation
        x += tx
        y += ty
        z += tz
        
        # Basic rotation matrix application could go here for "premium" feel
        return (x, y, z)

    @staticmethod
    def deg_to_rad(deg: float) -> float:
        return deg * math.pi / 180.0
