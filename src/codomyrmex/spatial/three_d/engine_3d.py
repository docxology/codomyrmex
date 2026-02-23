from dataclasses import dataclass, field
from typing import Any

from codomyrmex.logging_monitoring.logger_config import get_logger

"""Core 3D Engine for modeling and rendering."""

logger = get_logger(__name__)

@dataclass
class Vector3D:
    """3D vector representation."""

    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def __add__(self, other: "Vector3D") -> "Vector3D":
        """Add two vectors."""
        return Vector3D(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: "Vector3D") -> "Vector3D":
        """Subtract two vectors."""
        return Vector3D(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar: float) -> "Vector3D":
        """Multiply vector by scalar."""
        return Vector3D(self.x * scalar, self.y * scalar, self.z * scalar)


@dataclass
class Quaternion:
    """Quaternion for rotation."""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    w: float = 1.0


@dataclass
class Object3D:
    """3D Object representation."""
    name: str = "Object"
    position: Vector3D = field(default_factory=Vector3D)
    rotation: Quaternion = field(default_factory=Quaternion)
    scale: Vector3D = field(default_factory=lambda: Vector3D(1.0, 1.0, 1.0))
    animations: dict[str, Any] = field(default_factory=dict)

    def play_animation(self, name: str) -> None:
        """Play a specific animation."""
        if name in self.animations:
            logger.info(f"Playing animation: {name}")
            # Logic to update object transforms over time
        else:
            logger.warning(f"Animation not found: {name}")


class PhysicsEngine:
    """Basic physics simulation for 3D objects."""

    def __init__(self):
        """Initialize physics engine."""
        self.gravity = Vector3D(0.0, -9.81, 0.0)

    def update_physics(self, objects: list[Object3D], delta_time: float) -> None:
        """Update physics simulation."""
        for obj in objects:
            # Apply gravity
            # Simplistic Euler integration for demo
            obj.position.y += self.gravity.y * delta_time * delta_time * 0.5


@dataclass
class Light3D:
    """3D Light representation."""
    position: Vector3D = field(default_factory=Vector3D)
    color: tuple[float, float, float] = (1.0, 1.0, 1.0)
    intensity: float = 1.0


@dataclass
class Camera3D:
    """3D Camera representation."""
    position: Vector3D = field(default_factory=Vector3D)
    rotation: Quaternion = field(default_factory=Quaternion)
    field_of_view: float = 60.0
    near_plane: float = 0.1
    far_plane: float = 1000.0

    def look_at(self, target: Vector3D) -> None:
        """Point camera at target."""
        import math
        dx = target.x - self.position.x
        dy = target.y - self.position.y
        dz = target.z - self.position.z
        
        # Pitch and yaw calculation as functional fallback
        yaw = math.atan2(dx, dz)
        pitch = math.atan2(-dy, math.sqrt(dx*dx + dz*dz))
        
        # Approximate quaternion rotation from euler (yaw, pitch, roll=0)
        cy = math.cos(yaw * 0.5)
        sy = math.sin(yaw * 0.5)
        cp = math.cos(pitch * 0.5)
        sp = math.sin(pitch * 0.5)
        
        self.rotation.w = cy * cp
        self.rotation.x = cy * sp
        self.rotation.y = sy * cp
        self.rotation.z = -sy * sp


@dataclass
class Scene3D:
    """3D Scene representation."""
    objects: list[Object3D] = field(default_factory=list)
    lights: list[Light3D] = field(default_factory=list)
    camera: Camera3D = field(default_factory=Camera3D)
