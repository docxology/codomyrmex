"""
Coordinate transformation utilities for spatial modeling.

Provides coordinate system conversions and transformations.
"""

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Union


class CoordinateSystem(Enum):
    """Supported coordinate systems."""
    CARTESIAN = "cartesian"
    SPHERICAL = "spherical"
    CYLINDRICAL = "cylindrical"
    GEOGRAPHIC = "geographic"  # lat/lon
    UTM = "utm"

@dataclass
class Point3D:
    """A point in 3D space."""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def __add__(self, other: 'Point3D') -> 'Point3D':
        """Return sum with other."""
        return Point3D(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: 'Point3D') -> 'Point3D':
        """Return difference from other."""
        return Point3D(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar: float) -> 'Point3D':
        """Return product with other."""
        return Point3D(self.x * scalar, self.y * scalar, self.z * scalar)

    def __truediv__(self, scalar: float) -> 'Point3D':
        """Return true division result."""
        return Point3D(self.x / scalar, self.y / scalar, self.z / scalar)

    def magnitude(self) -> float:
        """Calculate the magnitude (length) of the vector."""
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)

    def normalize(self) -> 'Point3D':
        """Return a unit vector."""
        mag = self.magnitude()
        if mag == 0:
            return Point3D(0, 0, 0)
        return self / mag

    def dot(self, other: 'Point3D') -> float:
        """Dot product."""
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other: 'Point3D') -> 'Point3D':
        """Cross product."""
        return Point3D(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x,
        )

    def distance_to(self, other: 'Point3D') -> float:
        """Euclidean distance to another point."""
        return (self - other).magnitude()

    def to_tuple(self) -> tuple[float, float, float]:
        """Convert to tuple."""
        return (self.x, self.y, self.z)

    @classmethod
    def from_tuple(cls, t: tuple[float, float, float]) -> 'Point3D':
        """Create from tuple."""
        return cls(t[0], t[1], t[2])

@dataclass
class SphericalCoord:
    """Spherical coordinates (r, theta, phi)."""
    r: float = 0.0      # radius
    theta: float = 0.0  # azimuthal angle (0 to 2π)
    phi: float = 0.0    # polar angle (0 to π)

    def to_cartesian(self) -> Point3D:
        """Convert to Cartesian coordinates."""
        x = self.r * math.sin(self.phi) * math.cos(self.theta)
        y = self.r * math.sin(self.phi) * math.sin(self.theta)
        z = self.r * math.cos(self.phi)
        return Point3D(x, y, z)

    @classmethod
    def from_cartesian(cls, point: Point3D) -> 'SphericalCoord':
        """Create from Cartesian coordinates."""
        r = point.magnitude()
        if r == 0:
            return cls(0, 0, 0)

        theta = math.atan2(point.y, point.x)
        phi = math.acos(point.z / r)
        return cls(r, theta, phi)

@dataclass
class CylindricalCoord:
    """Cylindrical coordinates (r, theta, z)."""
    r: float = 0.0      # radius in xy-plane
    theta: float = 0.0  # azimuthal angle
    z: float = 0.0      # height

    def to_cartesian(self) -> Point3D:
        """Convert to Cartesian coordinates."""
        x = self.r * math.cos(self.theta)
        y = self.r * math.sin(self.theta)
        return Point3D(x, y, self.z)

    @classmethod
    def from_cartesian(cls, point: Point3D) -> 'CylindricalCoord':
        """Create from Cartesian coordinates."""
        r = math.sqrt(point.x**2 + point.y**2)
        theta = math.atan2(point.y, point.x)
        return cls(r, theta, point.z)

@dataclass
class GeographicCoord:
    """Geographic coordinates (latitude, longitude, altitude)."""
    lat: float = 0.0       # latitude in degrees (-90 to 90)
    lon: float = 0.0       # longitude in degrees (-180 to 180)
    alt: float = 0.0       # altitude in meters

    EARTH_RADIUS = 6371000  # meters

    def to_cartesian(self) -> Point3D:
        """Convert to ECEF Cartesian coordinates."""
        lat_rad = math.radians(self.lat)
        lon_rad = math.radians(self.lon)
        r = self.EARTH_RADIUS + self.alt

        x = r * math.cos(lat_rad) * math.cos(lon_rad)
        y = r * math.cos(lat_rad) * math.sin(lon_rad)
        z = r * math.sin(lat_rad)

        return Point3D(x, y, z)

    @classmethod
    def from_cartesian(cls, point: Point3D) -> 'GeographicCoord':
        """Create from ECEF Cartesian coordinates."""
        r = point.magnitude()
        if r == 0:
            return cls(0, 0, -cls.EARTH_RADIUS)

        lat = math.degrees(math.asin(point.z / r))
        lon = math.degrees(math.atan2(point.y, point.x))
        alt = r - cls.EARTH_RADIUS

        return cls(lat, lon, alt)

    def distance_to(self, other: 'GeographicCoord') -> float:
        """Calculate great circle distance using Haversine formula."""
        lat1 = math.radians(self.lat)
        lat2 = math.radians(other.lat)
        dlat = lat2 - lat1
        dlon = math.radians(other.lon - self.lon)

        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))

        return self.EARTH_RADIUS * c

    def bearing_to(self, other: 'GeographicCoord') -> float:
        """Calculate initial bearing to another point (in degrees)."""
        lat1 = math.radians(self.lat)
        lat2 = math.radians(other.lat)
        dlon = math.radians(other.lon - self.lon)

        x = math.sin(dlon) * math.cos(lat2)
        y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)

        bearing = math.degrees(math.atan2(x, y))
        return (bearing + 360) % 360

@dataclass
class Matrix4x4:
    """4x4 transformation matrix."""
    data: list[list[float]] = field(default_factory=lambda: [
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1],
    ])

    @classmethod
    def identity(cls) -> 'Matrix4x4':
        """Create identity matrix."""
        return cls()

    @classmethod
    def translation(cls, tx: float, ty: float, tz: float) -> 'Matrix4x4':
        """Create translation matrix."""
        return cls([
            [1, 0, 0, tx],
            [0, 1, 0, ty],
            [0, 0, 1, tz],
            [0, 0, 0, 1],
        ])

    @classmethod
    def scale(cls, sx: float, sy: float, sz: float) -> 'Matrix4x4':
        """Create scaling matrix."""
        return cls([
            [sx, 0, 0, 0],
            [0, sy, 0, 0],
            [0, 0, sz, 0],
            [0, 0, 0, 1],
        ])

    @classmethod
    def rotation_x(cls, angle: float) -> 'Matrix4x4':
        """Create rotation matrix around X axis (angle in radians)."""
        c, s = math.cos(angle), math.sin(angle)
        return cls([
            [1, 0, 0, 0],
            [0, c, -s, 0],
            [0, s, c, 0],
            [0, 0, 0, 1],
        ])

    @classmethod
    def rotation_y(cls, angle: float) -> 'Matrix4x4':
        """Create rotation matrix around Y axis."""
        c, s = math.cos(angle), math.sin(angle)
        return cls([
            [c, 0, s, 0],
            [0, 1, 0, 0],
            [-s, 0, c, 0],
            [0, 0, 0, 1],
        ])

    @classmethod
    def rotation_z(cls, angle: float) -> 'Matrix4x4':
        """Create rotation matrix around Z axis."""
        c, s = math.cos(angle), math.sin(angle)
        return cls([
            [c, -s, 0, 0],
            [s, c, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1],
        ])

    def __mul__(self, other: 'Matrix4x4') -> 'Matrix4x4':
        """Matrix multiplication."""
        result = [[0] * 4 for _ in range(4)]

        for i in range(4):
            for j in range(4):
                for k in range(4):
                    result[i][j] += self.data[i][k] * other.data[k][j]

        return Matrix4x4(result)

    def transform_point(self, point: Point3D) -> Point3D:
        """Transform a 3D point."""
        x = self.data[0][0]*point.x + self.data[0][1]*point.y + self.data[0][2]*point.z + self.data[0][3]
        y = self.data[1][0]*point.x + self.data[1][1]*point.y + self.data[1][2]*point.z + self.data[1][3]
        z = self.data[2][0]*point.x + self.data[2][1]*point.y + self.data[2][2]*point.z + self.data[2][3]
        w = self.data[3][0]*point.x + self.data[3][1]*point.y + self.data[3][2]*point.z + self.data[3][3]

        if w != 0 and w != 1:
            return Point3D(x/w, y/w, z/w)
        return Point3D(x, y, z)

class CoordinateTransformer:
    """Utility class for coordinate transformations."""

    @staticmethod
    def cartesian_to_spherical(point: Point3D) -> SphericalCoord:
        """Convert Cartesian to spherical coordinates."""
        return SphericalCoord.from_cartesian(point)

    @staticmethod
    def spherical_to_cartesian(coord: SphericalCoord) -> Point3D:
        """Convert spherical to Cartesian coordinates."""
        return coord.to_cartesian()

    @staticmethod
    def cartesian_to_cylindrical(point: Point3D) -> CylindricalCoord:
        """Convert Cartesian to cylindrical coordinates."""
        return CylindricalCoord.from_cartesian(point)

    @staticmethod
    def cylindrical_to_cartesian(coord: CylindricalCoord) -> Point3D:
        """Convert cylindrical to Cartesian coordinates."""
        return coord.to_cartesian()

    @staticmethod
    def geographic_to_cartesian(coord: GeographicCoord) -> Point3D:
        """Convert geographic to ECEF Cartesian coordinates."""
        return coord.to_cartesian()

    @staticmethod
    def cartesian_to_geographic(point: Point3D) -> GeographicCoord:
        """Convert ECEF Cartesian to geographic coordinates."""
        return GeographicCoord.from_cartesian(point)

    @staticmethod
    def degrees_to_radians(degrees: float) -> float:
        """Convert degrees to radians."""
        return math.radians(degrees)

    @staticmethod
    def radians_to_degrees(radians: float) -> float:
        """Convert radians to degrees."""
        return math.degrees(radians)

__all__ = [
    "CoordinateSystem",
    "Point3D",
    "SphericalCoord",
    "CylindricalCoord",
    "GeographicCoord",
    "Matrix4x4",
    "CoordinateTransformer",
]
