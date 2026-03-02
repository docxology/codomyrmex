"""Coordinate transformation utilities for embodied systems.

Provides 3D transformations (translation + Euler rotation), composition,
inverse, and point/vector transformation in right-hand coordinate frames.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Vec3:
    """Immutable 3D vector."""

    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def __add__(self, other: Vec3) -> Vec3:
        """add ."""
        return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: Vec3) -> Vec3:
        """sub ."""
        return Vec3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar: float) -> Vec3:
        """mul ."""
        return Vec3(self.x * scalar, self.y * scalar, self.z * scalar)

    def __rmul__(self, scalar: float) -> Vec3:
        """rmul ."""
        return self.__mul__(scalar)

    def length(self) -> float:
        """Euclidean length of the vector."""
        return math.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)

    def normalized(self) -> Vec3:
        """Return unit vector. Returns zero vector if length is ~0."""
        mag = self.length()
        if mag < 1e-12:
            return Vec3(0.0, 0.0, 0.0)
        return Vec3(self.x / mag, self.y / mag, self.z / mag)

    def dot(self, other: Vec3) -> float:
        """Dot product."""
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other: Vec3) -> Vec3:
        """Cross product (right-hand rule)."""
        return Vec3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x,
        )

    def to_tuple(self) -> tuple[float, float, float]:
        """to Tuple ."""
        return (self.x, self.y, self.z)

    def to_dict(self) -> dict[str, float]:
        """Return a dictionary representation of this object."""
        return {"x": self.x, "y": self.y, "z": self.z}


class Transform3D:
    """3D rigid-body transformation (translation + ZYX Euler rotation).

    Rotation order: yaw (Z) → pitch (Y) → roll (X), following aerospace convention.

    Attributes:
        translation: Translation vector (x, y, z).
        rotation: Euler angles (roll, pitch, yaw) in radians.
    """

    def __init__(
        self,
        translation: tuple[float, float, float] = (0.0, 0.0, 0.0),
        rotation: tuple[float, float, float] = (0.0, 0.0, 0.0),
    ) -> None:
        """
        Args:
            translation: (x, y, z) displacement.
            rotation: (roll, pitch, yaw) in radians.
        """
        self.translation = Vec3(*translation)
        self.rotation = rotation  # (roll, pitch, yaw)

    # ── Rotation matrix (ZYX Euler) ─────────────────────────────────

    def _rotation_matrix(self) -> list[list[float]]:
        """Compute the 3×3 rotation matrix from ZYX Euler angles."""
        roll, pitch, yaw = self.rotation
        cr, sr = math.cos(roll), math.sin(roll)
        cp, sp = math.cos(pitch), math.sin(pitch)
        cy, sy = math.cos(yaw), math.sin(yaw)

        return [
            [cy * cp, cy * sp * sr - sy * cr, cy * sp * cr + sy * sr],
            [sy * cp, sy * sp * sr + cy * cr, sy * sp * cr - cy * sr],
            [-sp, cp * sr, cp * cr],
        ]

    # ── Point/vector transformation ─────────────────────────────────

    def transform_point(self, point: tuple[float, float, float]) -> tuple[float, float, float]:
        """Apply rotation then translation to a 3D point.

        Args:
            point: (x, y, z) in the local frame.

        Returns:
            Transformed (x, y, z) in the world frame.
        """
        R = self._rotation_matrix()
        px, py, pz = point

        rx = R[0][0] * px + R[0][1] * py + R[0][2] * pz
        ry = R[1][0] * px + R[1][1] * py + R[1][2] * pz
        rz = R[2][0] * px + R[2][1] * py + R[2][2] * pz

        return (
            rx + self.translation.x,
            ry + self.translation.y,
            rz + self.translation.z,
        )

    def transform_vector(self, vector: tuple[float, float, float]) -> tuple[float, float, float]:
        """Apply rotation (no translation) to a direction vector."""
        R = self._rotation_matrix()
        vx, vy, vz = vector
        return (
            R[0][0] * vx + R[0][1] * vy + R[0][2] * vz,
            R[1][0] * vx + R[1][1] * vy + R[1][2] * vz,
            R[2][0] * vx + R[2][1] * vy + R[2][2] * vz,
        )

    # ── Composition ─────────────────────────────────────────────────

    def compose(self, other: Transform3D) -> Transform3D:
        """Compose two transforms: self ∘ other.

        Equivalent to applying ``other`` first, then ``self``.
        Uses matrix multiplication for rotation composition.
        """
        # Transform the other's translation through self's rotation+translation
        new_t = self.transform_point(other.translation.to_tuple())

        # Compose rotations via matrix multiplication
        Ra = self._rotation_matrix()
        Rb = other._rotation_matrix()
        Rc = [[sum(Ra[i][k] * Rb[k][j] for k in range(3)) for j in range(3)] for i in range(3)]

        # Extract Euler angles from composed rotation matrix
        new_pitch = -math.asin(max(-1.0, min(1.0, Rc[2][0])))
        cos_pitch = math.cos(new_pitch)
        if abs(cos_pitch) > 1e-9:
            new_roll = math.atan2(Rc[2][1] / cos_pitch, Rc[2][2] / cos_pitch)
            new_yaw = math.atan2(Rc[1][0] / cos_pitch, Rc[0][0] / cos_pitch)
        else:
            new_roll = 0.0
            new_yaw = math.atan2(-Rc[0][1], Rc[1][1])

        return Transform3D(
            translation=new_t,
            rotation=(new_roll, new_pitch, new_yaw),
        )

    def inverse(self) -> Transform3D:
        """Compute the inverse transform.

        T^{-1} undoes the effect of T: T.compose(T.inverse()) ≈ identity.
        """
        R = self._rotation_matrix()
        # Transpose = inverse for rotation matrices
        Rt = [[R[j][i] for j in range(3)] for i in range(3)]

        # Inverse translation: -R^T * t
        tx, ty, tz = self.translation.x, self.translation.y, self.translation.z
        new_tx = -(Rt[0][0] * tx + Rt[0][1] * ty + Rt[0][2] * tz)
        new_ty = -(Rt[1][0] * tx + Rt[1][1] * ty + Rt[1][2] * tz)
        new_tz = -(Rt[2][0] * tx + Rt[2][1] * ty + Rt[2][2] * tz)

        # Extract Euler angles from transposed rotation
        new_pitch = -math.asin(max(-1.0, min(1.0, Rt[2][0])))
        cos_pitch = math.cos(new_pitch)
        if abs(cos_pitch) > 1e-9:
            new_roll = math.atan2(Rt[2][1] / cos_pitch, Rt[2][2] / cos_pitch)
            new_yaw = math.atan2(Rt[1][0] / cos_pitch, Rt[0][0] / cos_pitch)
        else:
            new_roll = 0.0
            new_yaw = math.atan2(-Rt[0][1], Rt[1][1])

        return Transform3D(
            translation=(new_tx, new_ty, new_tz),
            rotation=(new_roll, new_pitch, new_yaw),
        )

    # ── Utilities ───────────────────────────────────────────────────

    @staticmethod
    def deg_to_rad(deg: float) -> float:
        """Convert degrees to radians."""
        return deg * math.pi / 180.0

    @staticmethod
    def rad_to_deg(rad: float) -> float:
        """Convert radians to degrees."""
        return rad * 180.0 / math.pi

    @classmethod
    def identity(cls) -> Transform3D:
        """Return the identity transform (no rotation, no translation)."""
        return cls()

    @classmethod
    def from_translation(cls, x: float, y: float, z: float) -> Transform3D:
        """Create a pure translation transform."""
        return cls(translation=(x, y, z))

    @classmethod
    def from_yaw(cls, yaw_rad: float) -> Transform3D:
        """Create a pure yaw (Z-axis) rotation transform."""
        return cls(rotation=(0.0, 0.0, yaw_rad))

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-compatible dict."""
        return {
            "translation": self.translation.to_dict(),
            "rotation": {"roll": self.rotation[0], "pitch": self.rotation[1], "yaw": self.rotation[2]},
        }

    def __repr__(self) -> str:
        """repr ."""
        t = self.translation
        r = self.rotation
        return (
            f"Transform3D(t=({t.x:.3f}, {t.y:.3f}, {t.z:.3f}), "
            f"r=({r[0]:.3f}, {r[1]:.3f}, {r[2]:.3f}))"
        )
