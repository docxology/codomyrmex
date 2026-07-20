from __future__ import annotations

import math
from collections.abc import Iterable
from dataclasses import dataclass


@dataclass(frozen=True)
class Vec3:
    x: float
    y: float
    z: float

    def __add__(self, other: Vec3) -> Vec3:
        return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: Vec3) -> Vec3:
        return Vec3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar: float) -> Vec3:
        return Vec3(self.x * scalar, self.y * scalar, self.z * scalar)

    __rmul__ = __mul__

    def length(self) -> float:
        return math.sqrt(self.dot(self))

    def normalized(self) -> Vec3:
        length = self.length()
        if length == 0:
            return Vec3(0.0, 0.0, 0.0)
        return Vec3(self.x / length, self.y / length, self.z / length)

    def dot(self, other: Vec3) -> float:
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other: Vec3) -> Vec3:
        return Vec3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x,
        )

    def to_tuple(self) -> tuple[float, float, float]:
        return (self.x, self.y, self.z)

    def to_dict(self) -> dict[str, float]:
        return {"x": self.x, "y": self.y, "z": self.z}


class Transform3D:
    def __init__(
        self,
        translation: Vec3 | Iterable[float] = (0.0, 0.0, 0.0),
        rotation: tuple[float, float, float] = (0.0, 0.0, 0.0),
    ) -> None:
        self.translation = (
            translation
            if isinstance(translation, Vec3)
            else Vec3(*[float(value) for value in translation])
        )
        self.rotation = tuple(float(value) for value in rotation)

    @classmethod
    def identity(cls) -> Transform3D:
        return cls()

    @classmethod
    def from_translation(cls, x: float, y: float, z: float) -> Transform3D:
        return cls(translation=(x, y, z))

    @classmethod
    def from_yaw(cls, yaw: float) -> Transform3D:
        return cls(rotation=(0.0, 0.0, yaw))

    def transform_vector(
        self, vector: Vec3 | Iterable[float]
    ) -> tuple[float, float, float]:
        vec = vector if isinstance(vector, Vec3) else Vec3(*vector)
        return _mat_vec(_rotation_matrix(self.rotation), vec).to_tuple()

    def compose(self, other: Transform3D) -> Transform3D:
        self_matrix = _rotation_matrix(self.rotation)
        other_matrix = _rotation_matrix(other.rotation)
        matrix = _mat_mul(self_matrix, other_matrix)
        translated = _mat_vec(self_matrix, other.translation) + self.translation
        return Transform3D(translated, _matrix_to_euler(matrix))

    def inverse(self) -> Transform3D:
        matrix = _rotation_matrix(self.rotation)
        inverse_matrix = _transpose(matrix)
        inverse_translation = _mat_vec(inverse_matrix, self.translation * -1.0)
        return Transform3D(inverse_translation, _matrix_to_euler(inverse_matrix))

    def to_dict(self) -> dict[str, object]:
        roll, pitch, yaw = self.rotation
        return {
            "translation": self.translation.to_dict(),
            "rotation": {"roll": roll, "pitch": pitch, "yaw": yaw},
        }

    @staticmethod
    def rad_to_deg(radians: float) -> float:
        return math.degrees(radians)

    @staticmethod
    def deg_to_rad(degrees: float) -> float:
        return math.radians(degrees)

    def __repr__(self) -> str:
        return (
            "Transform3D("
            f"translation=({self.translation.x:.3f}, "
            f"{self.translation.y:.3f}, {self.translation.z:.3f}), "
            f"rotation={self.rotation!r})"
        )


def _rotation_matrix(rotation: tuple[float, float, float]) -> list[list[float]]:
    roll, pitch, yaw = rotation
    cr, sr = math.cos(roll), math.sin(roll)
    cp, sp = math.cos(pitch), math.sin(pitch)
    cy, sy = math.cos(yaw), math.sin(yaw)
    return [
        [cy * cp, cy * sp * sr - sy * cr, cy * sp * cr + sy * sr],
        [sy * cp, sy * sp * sr + cy * cr, sy * sp * cr - cy * sr],
        [-sp, cp * sr, cp * cr],
    ]


def _matrix_to_euler(matrix: list[list[float]]) -> tuple[float, float, float]:
    pitch = math.asin(max(-1.0, min(1.0, -matrix[2][0])))
    cp = math.cos(pitch)
    if abs(cp) > 1e-12:
        roll = math.atan2(matrix[2][1], matrix[2][2])
        yaw = math.atan2(matrix[1][0], matrix[0][0])
    else:
        roll = 0.0
        yaw = math.atan2(-matrix[0][1], matrix[1][1])
    return (roll, pitch, yaw)


def _mat_mul(left: list[list[float]], right: list[list[float]]) -> list[list[float]]:
    return [
        [
            sum(left[row][inner] * right[inner][col] for inner in range(3))
            for col in range(3)
        ]
        for row in range(3)
    ]


def _mat_vec(matrix: list[list[float]], vector: Vec3) -> Vec3:
    return Vec3(
        matrix[0][0] * vector.x + matrix[0][1] * vector.y + matrix[0][2] * vector.z,
        matrix[1][0] * vector.x + matrix[1][1] * vector.y + matrix[1][2] * vector.z,
        matrix[2][0] * vector.x + matrix[2][1] * vector.y + matrix[2][2] * vector.z,
    )


def _transpose(matrix: list[list[float]]) -> list[list[float]]:
    return [[matrix[col][row] for col in range(3)] for row in range(3)]
