from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from codomyrmex.logging_monitoring import get_logger

"""Core 3D Engine for modeling and rendering."""

logger = get_logger(__name__)


@dataclass
class Vector3D:
    """3D vector representation."""

    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def __add__(self, other: Vector3D) -> Vector3D:
        """Add two vectors."""
        return Vector3D(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: Vector3D) -> Vector3D:
        """Subtract two vectors."""
        return Vector3D(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar: float) -> Vector3D:
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
    vertices: list[Vector3D] = field(default_factory=list)
    faces: list[tuple[int, ...]] = field(default_factory=list)
    material: Any | None = None

    def set_position(self, x: float, y: float, z: float) -> None:
        """Set the object position in world coordinates."""
        self.position = Vector3D(float(x), float(y), float(z))

    def play_animation(self, name: str) -> None:
        """Play a specific animation."""
        if name in self.animations:
            logger.info("Playing animation: %s", name)
            # Logic to update object transforms over time
        else:
            logger.warning("Animation not found: %s", name)


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
    name: str = "Light"

    def set_position(self, x: float, y: float, z: float) -> None:
        """Set the light position in world coordinates."""
        self.position = Vector3D(float(x), float(y), float(z))


@dataclass
class Camera3D:
    """3D Camera representation."""

    position: Vector3D = field(default_factory=Vector3D)
    rotation: Quaternion = field(default_factory=Quaternion)
    field_of_view: float = 60.0
    near_plane: float = 0.1
    far_plane: float = 1000.0
    name: str = "Camera"

    @property
    def fov(self) -> float:
        """Compatibility alias for the API specification's ``fov`` field."""
        return self.field_of_view

    @fov.setter
    def fov(self, value: float) -> None:
        self.field_of_view = float(value)

    def set_position(self, x: float, y: float, z: float) -> None:
        """Set the camera position in world coordinates."""
        self.position = Vector3D(float(x), float(y), float(z))

    def look_at(self, target: Vector3D) -> None:
        """Point camera at target."""
        import math

        dx = target.x - self.position.x
        dy = target.y - self.position.y
        dz = target.z - self.position.z

        # Pitch and yaw calculation as functional fallback
        yaw = math.atan2(dx, dz)
        pitch = math.atan2(-dy, math.sqrt(dx * dx + dz * dz))

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

    def add_object(self, obj: Object3D) -> None:
        """Add an object to the scene."""
        if not isinstance(obj, Object3D):
            raise TypeError("scene objects must be Object3D instances")
        self.objects.append(obj)

    def add_camera(self, camera: Camera3D) -> None:
        """Set the active scene camera."""
        if not isinstance(camera, Camera3D):
            raise TypeError("scene camera must be a Camera3D instance")
        self.camera = camera

    def add_light(self, light: Light3D) -> None:
        """Add a light to the scene."""
        if not isinstance(light, Light3D):
            raise TypeError("scene lights must be Light3D instances")
        self.lights.append(light)
