"""Quaternion mathematics for 3D/4D rotations.

Provides a pure-Python quaternion implementation supporting rotation
construction, composition, spherical linear interpolation (slerp),
and conversion to/from rotation matrices and axis-angle representation.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from codomyrmex.spatial.coordinates import Matrix4x4, Point3D


@dataclass(frozen=True)
class Quaternion:
    """Immutable unit quaternion for 3D rotation.

    Stored as (w, x, y, z) where w is the scalar part and (x, y, z)
    is the vector part.

    Attributes:
        w: Scalar component (cos(θ/2) for axis-angle).
        x: X component of rotation axis × sin(θ/2).
        y: Y component of rotation axis × sin(θ/2).
        z: Z component of rotation axis × sin(θ/2).
    """

    w: float = 1.0
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    # ── Construction ────────────────────────────────────────────────

    @classmethod
    def identity(cls) -> Quaternion:
        """Return the identity quaternion (no rotation)."""
        return cls(1.0, 0.0, 0.0, 0.0)

    @classmethod
    def from_axis_angle(
        cls,
        axis: tuple[float, float, float],
        angle: float,
    ) -> Quaternion:
        """Create quaternion from axis-angle representation.

        Args:
            axis: Unit rotation axis (x, y, z). Will be normalized.
            angle: Rotation angle in radians.

        Returns:
            Quaternion encoding the rotation.
        """
        ax, ay, az = axis
        mag = math.sqrt(ax * ax + ay * ay + az * az)
        if mag < 1e-12:
            return cls.identity()

        ax, ay, az = ax / mag, ay / mag, az / mag
        half = angle / 2.0
        s = math.sin(half)
        return cls(w=math.cos(half), x=ax * s, y=ay * s, z=az * s)

    @classmethod
    def from_euler(cls, roll: float, pitch: float, yaw: float) -> Quaternion:
        """Create quaternion from ZYX Euler angles (aerospace convention).

        Args:
            roll: Rotation about X axis (radians).
            pitch: Rotation about Y axis (radians).
            yaw: Rotation about Z axis (radians).

        Returns:
            Quaternion encoding the combined rotation.
        """
        cr, sr = math.cos(roll / 2), math.sin(roll / 2)
        cp, sp = math.cos(pitch / 2), math.sin(pitch / 2)
        cy, sy = math.cos(yaw / 2), math.sin(yaw / 2)

        return cls(
            w=cr * cp * cy + sr * sp * sy,
            x=sr * cp * cy - cr * sp * sy,
            y=cr * sp * cy + sr * cp * sy,
            z=cr * cp * sy - sr * sp * cy,
        )

    # ── Core operations ─────────────────────────────────────────────

    def norm(self) -> float:
        """Quaternion magnitude."""
        return math.sqrt(self.w**2 + self.x**2 + self.y**2 + self.z**2)

    def normalize(self) -> Quaternion:
        """Return normalized (unit) quaternion."""
        n = self.norm()
        if n < 1e-12:
            return Quaternion.identity()
        return Quaternion(self.w / n, self.x / n, self.y / n, self.z / n)

    def conjugate(self) -> Quaternion:
        """Return conjugate (inverse for unit quaternions)."""
        return Quaternion(self.w, -self.x, -self.y, -self.z)

    def inverse(self) -> Quaternion:
        """Return multiplicative inverse."""
        n2 = self.w**2 + self.x**2 + self.y**2 + self.z**2
        if n2 < 1e-24:
            raise ZeroDivisionError("Cannot invert zero quaternion")
        return Quaternion(self.w / n2, -self.x / n2, -self.y / n2, -self.z / n2)

    def __mul__(self, other: Quaternion) -> Quaternion:
        """Hamilton product: self * other."""
        return Quaternion(
            w=self.w * other.w - self.x * other.x - self.y * other.y - self.z * other.z,
            x=self.w * other.x + self.x * other.w + self.y * other.z - self.z * other.y,
            y=self.w * other.y - self.x * other.z + self.y * other.w + self.z * other.x,
            z=self.w * other.z + self.x * other.y - self.y * other.x + self.z * other.w,
        )

    def dot(self, other: Quaternion) -> float:
        """Dot product of two quaternions."""
        return self.w * other.w + self.x * other.x + self.y * other.y + self.z * other.z

    # ── Rotation application ────────────────────────────────────────

    def rotate_point(self, point: Point3D) -> Point3D:
        """Rotate a 3D point by this quaternion.

        Implements p' = q * p * q⁻¹ where p = (0, px, py, pz).

        Args:
            point: 3D point to rotate.

        Returns:
            Rotated 3D point.
        """
        p = Quaternion(0.0, point.x, point.y, point.z)
        rotated = self * p * self.conjugate()
        return Point3D(rotated.x, rotated.y, rotated.z)

    # ── Interpolation ───────────────────────────────────────────────

    def slerp(self, other: Quaternion, t: float) -> Quaternion:
        """Spherical linear interpolation between self and other.

        Args:
            other: Target quaternion.
            t: Interpolation parameter in [0, 1].

        Returns:
            Interpolated quaternion at parameter t.
        """
        dot = self.dot(other)

        # Ensure shortest path
        target = other
        if dot < 0.0:
            target = Quaternion(-other.w, -other.x, -other.y, -other.z)
            dot = -dot

        dot = min(1.0, dot)  # clamp

        if dot > 0.9995:
            # Linear interpolation for very close quaternions
            result = Quaternion(
                w=self.w + t * (target.w - self.w),
                x=self.x + t * (target.x - self.x),
                y=self.y + t * (target.y - self.y),
                z=self.z + t * (target.z - self.z),
            )
            return result.normalize()

        theta = math.acos(dot)
        sin_theta = math.sin(theta)

        s1 = math.sin((1.0 - t) * theta) / sin_theta
        s2 = math.sin(t * theta) / sin_theta

        return Quaternion(
            w=s1 * self.w + s2 * target.w,
            x=s1 * self.x + s2 * target.x,
            y=s1 * self.y + s2 * target.y,
            z=s1 * self.z + s2 * target.z,
        )

    # ── Conversion ──────────────────────────────────────────────────

    def to_axis_angle(self) -> tuple[tuple[float, float, float], float]:
        """Convert to axis-angle representation.

        Returns:
            Tuple of (axis, angle) where axis is (x, y, z) unit vector
            and angle is in radians.
        """
        q = self.normalize()
        # Clamp w for numerical safety
        w_clamped = max(-1.0, min(1.0, q.w))
        angle = 2.0 * math.acos(w_clamped)

        s = math.sqrt(1.0 - w_clamped * w_clamped)
        if s < 1e-12:
            return (1.0, 0.0, 0.0), 0.0

        return (q.x / s, q.y / s, q.z / s), angle

    def to_rotation_matrix(self) -> Matrix4x4:
        """Convert to a 4×4 rotation matrix.

        Returns:
            Matrix4x4 representing this rotation.
        """
        q = self.normalize()
        xx = q.x * q.x
        yy = q.y * q.y
        zz = q.z * q.z
        xy = q.x * q.y
        xz = q.x * q.z
        yz = q.y * q.z
        wx = q.w * q.x
        wy = q.w * q.y
        wz = q.w * q.z

        return Matrix4x4([
            [1 - 2 * (yy + zz), 2 * (xy - wz), 2 * (xz + wy), 0],
            [2 * (xy + wz), 1 - 2 * (xx + zz), 2 * (yz - wx), 0],
            [2 * (xz - wy), 2 * (yz + wx), 1 - 2 * (xx + yy), 0],
            [0, 0, 0, 1],
        ])

    def to_tuple(self) -> tuple[float, float, float, float]:
        """Return (w, x, y, z) tuple."""
        return (self.w, self.x, self.y, self.z)

    def to_dict(self) -> dict[str, float]:
        """Serialize to dictionary."""
        return {"w": self.w, "x": self.x, "y": self.y, "z": self.z}


__all__ = [
    "Quaternion",
]
