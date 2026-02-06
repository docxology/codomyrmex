import math
from dataclasses import dataclass, field
from typing import Any

from codomyrmex.logging_monitoring import get_logger

"""Physical simulation engine for object interactions."""

logger = get_logger(__name__)
@dataclass
class Vector3D:
    """3D vector for physics calculations."""

    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def __add__(self, other: "Vector3D") -> "Vector3D":
        return Vector3D(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: "Vector3D") -> "Vector3D":
        return Vector3D(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar: float) -> "Vector3D":
        return Vector3D(self.x * scalar, self.y * scalar, self.z * scalar)

    def magnitude(self) -> float:
        """Calculate vector magnitude."""
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)

    def normalize(self) -> "Vector3D":
        """Normalize vector to unit length."""
        mag = self.magnitude()
        if mag == 0:
            return Vector3D(0, 0, 0)
        return Vector3D(self.x / mag, self.y / mag, self.z / mag)


@dataclass
class ForceField:
    """Represents a force field affecting objects."""

    position: Vector3D
    strength: float
    falloff: float = 2.0  # Inverse square falloff

    def calculate_force(self, object_position: Vector3D) -> Vector3D:
        """Calculate force on an object at given position."""
        direction = object_position - self.position
        distance = direction.magnitude()

        if distance == 0:
            return Vector3D(0, 0, 0)

        # Inverse square law
        force_magnitude = self.strength / (distance**self.falloff)
        force_direction = direction.normalize()

        return force_direction * force_magnitude


@dataclass
class Constraint:
    """Physical constraint between objects."""

    object1_id: str
    object2_id: str
    constraint_type: str
    parameters: dict[str, Any] = field(default_factory=dict)


class PhysicsSimulator:
    """Physics simulation engine."""

    def __init__(self):
        """  Init  .
            """
        self.gravity = Vector3D(0, -9.81, 0)
        self.force_fields: list[ForceField] = []
        self.constraints: list[Constraint] = []
        self.objects: dict[str, dict[str, Any]] = {}

    def add_force_field(self, force_field: ForceField) -> None:
        """Add a force field to the simulation."""
        self.force_fields.append(force_field)

    def add_constraint(self, constraint: Constraint) -> None:
        """Add a constraint to the simulation."""
        self.constraints.append(constraint)

    def register_object(
        self, object_id: str, mass: float, position: Vector3D, velocity: Vector3D = None
    ) -> None:
        """Register an object for physics simulation."""
        if velocity is None:
            velocity = Vector3D(0, 0, 0)

        self.objects[object_id] = {
            "mass": mass,
            "position": position,
            "velocity": velocity,
            "acceleration": Vector3D(0, 0, 0),
            "force": Vector3D(0, 0, 0),
        }

    def update_physics(self, delta_time: float) -> None:
        """Update physics simulation for one time step."""
        # Calculate forces
        self._calculate_forces()

        # Apply constraints
        self._apply_constraints()

        # Update positions and velocities
        self._integrate_motion(delta_time)

    def _calculate_forces(self) -> None:
        """Calculate forces acting on all objects."""
        # Reset forces to zero
        for obj_data in self.objects.values():
            obj_data["force"] = Vector3D(0, 0, 0)

        for _obj_id, obj_data in self.objects.items():
            total_force = Vector3D(0, 0, 0)

            # Add gravity
            total_force += self.gravity * obj_data["mass"]

            # Add force fields
            for force_field in self.force_fields:
                field_force = force_field.calculate_force(obj_data["position"])
                total_force += field_force

            obj_data["force"] = total_force

        # Apply spring forces
        self._apply_spring_constraints()

        # Calculate accelerations
        for obj_data in self.objects.values():
            obj_data["acceleration"] = obj_data["force"] * (1.0 / obj_data["mass"])

    def _apply_constraints(self) -> None:
        """Apply constraints between objects."""
        # Apply other constraints (not springs, as they're force-based)
        for constraint in self.constraints:
            if (
                constraint.constraint_type != "spring"
                and constraint.object1_id in self.objects
                and constraint.object2_id in self.objects
            ):
                obj1 = self.objects[constraint.object1_id]
                obj2 = self.objects[constraint.object2_id]

                # Simple distance constraint
                if constraint.constraint_type == "distance":
                    target_distance = constraint.parameters.get("distance", 1.0)
                    current_distance = (obj1["position"] - obj2["position"]).magnitude()

                    if current_distance != target_distance:
                        direction = (obj2["position"] - obj1["position"]).normalize()
                        correction = (
                            direction * (target_distance - current_distance) * 0.5
                        )

                        obj1["position"] += correction
                        obj2["position"] -= correction

    def _integrate_motion(self, delta_time: float) -> None:
        """Integrate motion using Verlet integration."""
        for obj_data in self.objects.values():
            # Verlet integration
            position = obj_data["position"]
            velocity = obj_data["velocity"]
            acceleration = obj_data["acceleration"]

            # Update velocity (v = v + a*dt)
            velocity += acceleration * delta_time

            # Update position (x = x + v*dt)
            position += velocity * delta_time

            obj_data["velocity"] = velocity
            obj_data["position"] = position

    def get_object_state(self, object_id: str) -> dict[str, Any] | None:
        """Get the current state of an object."""
        return self.objects.get(object_id)

    def set_object_position(self, object_id: str, position: Vector3D) -> bool:
        """Set the position of an object."""
        if object_id in self.objects:
            self.objects[object_id]["position"] = position
            return True
        return False

    def get_simulation_stats(self) -> dict[str, Any]:
        """Get simulation statistics."""
        total_kinetic = self.calculate_total_kinetic_energy()
        total_potential = self.calculate_total_potential_energy()

        return {
            "total_objects": len(self.objects),
            "force_fields": len(self.force_fields),
            "constraints": len(self.constraints),
            "total_force": sum(
                obj["force"].magnitude() for obj in self.objects.values()
            ),
            "average_velocity": (
                sum(obj["velocity"].magnitude() for obj in self.objects.values())
                / len(self.objects)
                if self.objects
                else 0
            ),
            "total_kinetic_energy": total_kinetic,
            "total_potential_energy": total_potential,
            "total_energy": total_kinetic + total_potential,
        }

    def calculate_kinetic_energy(self, object_id: str) -> float:
        """Calculate kinetic energy of a specific object."""
        if object_id not in self.objects:
            return 0.0

        obj = self.objects[object_id]
        velocity_magnitude = obj["velocity"].magnitude()
        return 0.5 * obj["mass"] * velocity_magnitude**2

    def calculate_potential_energy(self, object_id: str) -> float:
        """Calculate gravitational potential energy of a specific object."""
        if object_id not in self.objects:
            return 0.0

        obj = self.objects[object_id]
        # Use height above reference point (y = 0) for gravitational potential energy
        height = obj["position"].y
        return obj["mass"] * abs(self.gravity.y) * height

    def calculate_total_kinetic_energy(self) -> float:
        """Calculate total kinetic energy of all objects."""
        return sum(
            self.calculate_kinetic_energy(obj_id) for obj_id in self.objects.keys()
        )

    def calculate_total_potential_energy(self) -> float:
        """Calculate total potential energy of all objects."""
        total_pe = 0.0

        # Gravitational potential energy
        for obj_id in self.objects.keys():
            total_pe += self.calculate_potential_energy(obj_id)

        # Force field potential energy
        for obj_id, obj_data in self.objects.items():
            for force_field in self.force_fields:
                distance = (obj_data["position"] - force_field.position).magnitude()
                if distance > 0:
                    # Approximate potential energy for force fields
                    total_pe += -force_field.strength / (
                        distance ** (force_field.falloff - 1)
                    )

        return total_pe

    def apply_impulse(self, object_id: str, impulse: Vector3D) -> bool:
        """Apply an impulse (sudden change in momentum) to an object."""
        if object_id not in self.objects:
            return False

        obj = self.objects[object_id]
        # Change velocity by impulse/mass
        velocity_change = impulse * (1.0 / obj["mass"])
        obj["velocity"] += velocity_change
        return True

    def set_object_velocity(self, object_id: str, velocity: Vector3D) -> bool:
        """Set the velocity of an object."""
        if object_id in self.objects:
            self.objects[object_id]["velocity"] = velocity
            return True
        return False

    def add_spring_constraint(
        self,
        object1_id: str,
        object2_id: str,
        rest_length: float,
        spring_constant: float,
        damping: float = 0.1,
    ) -> bool:
        """Add a spring constraint between two objects."""
        if object1_id not in self.objects or object2_id not in self.objects:
            return False

        constraint = Constraint(
            object1_id=object1_id,
            object2_id=object2_id,
            constraint_type="spring",
            parameters={
                "rest_length": rest_length,
                "spring_constant": spring_constant,
                "damping": damping,
            },
        )
        self.add_constraint(constraint)
        return True

    def _apply_spring_constraints(self) -> None:
        """Apply spring constraints (called from _apply_constraints)."""
        for constraint in self.constraints:
            if constraint.constraint_type == "spring":
                if (
                    constraint.object1_id in self.objects
                    and constraint.object2_id in self.objects
                ):
                    obj1 = self.objects[constraint.object1_id]
                    obj2 = self.objects[constraint.object2_id]

                    # Spring parameters
                    rest_length = constraint.parameters.get("rest_length", 1.0)
                    k = constraint.parameters.get("spring_constant", 1.0)
                    damping = constraint.parameters.get("damping", 0.1)

                    # Calculate spring force
                    direction = obj2["position"] - obj1["position"]
                    current_length = direction.magnitude()

                    if current_length > 0:
                        spring_force_magnitude = k * (current_length - rest_length)
                        spring_direction = direction.normalize()
                        spring_force = spring_direction * spring_force_magnitude

                        # Add damping force
                        relative_velocity = obj2["velocity"] - obj1["velocity"]
                        damping_force = spring_direction * (
                            damping
                            * (
                                relative_velocity.x * spring_direction.x
                                + relative_velocity.y * spring_direction.y
                                + relative_velocity.z * spring_direction.z
                            )
                        )

                        total_force = spring_force + damping_force

                        # Apply forces (Newton's 3rd law)
                        obj1["force"] += total_force
                        obj2["force"] -= total_force

    def detect_collisions(self, collision_radius: float = 0.5) -> list[tuple[str, str]]:
        """Detect collisions between objects."""
        collisions = []
        object_ids = list(self.objects.keys())

        for i, obj1_id in enumerate(object_ids):
            for obj2_id in object_ids[i + 1 :]:
                obj1 = self.objects[obj1_id]
                obj2 = self.objects[obj2_id]

                distance = (obj1["position"] - obj2["position"]).magnitude()
                if distance <= collision_radius * 2:
                    collisions.append((obj1_id, obj2_id))

        return collisions

    def handle_elastic_collision(self, obj1_id: str, obj2_id: str) -> bool:
        """Handle elastic collision between two objects."""
        if obj1_id not in self.objects or obj2_id not in self.objects:
            return False

        obj1 = self.objects[obj1_id]
        obj2 = self.objects[obj2_id]

        m1, m2 = obj1["mass"], obj2["mass"]
        v1, v2 = obj1["velocity"], obj2["velocity"]

        # 1D elastic collision formulas (simplified)
        total_mass = m1 + m2

        new_v1 = v1 * ((m1 - m2) / total_mass) + v2 * (2 * m2 / total_mass)
        new_v2 = v1 * (2 * m1 / total_mass) + v2 * ((m2 - m1) / total_mass)

        obj1["velocity"] = new_v1
        obj2["velocity"] = new_v2

        return True


__all__ = ["Vector3D", "ForceField", "Constraint", "PhysicsSimulator"]
