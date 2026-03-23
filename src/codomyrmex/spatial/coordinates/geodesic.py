"""Geodesic mesh generation and spherical geometry utilities.

Generates icosahedral meshes at configurable subdivision frequencies
and provides geodesic (great-circle) distance computation on spheres.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from codomyrmex.spatial.coordinates import Point3D


@dataclass
class IcosahedralMesh:
    """An icosahedral mesh with vertices and triangular faces.

    Attributes:
        vertices: list of 3D points on the unit sphere.
        faces: list of (i, j, k) index triples defining triangles.
        frequency: Subdivision frequency used to generate this mesh.
    """

    vertices: list[Point3D] = field(default_factory=list)
    faces: list[tuple[int, int, int]] = field(default_factory=list)
    frequency: int = 1

    @property
    def vertex_count(self) -> int:
        """Number of vertices."""
        return len(self.vertices)

    @property
    def face_count(self) -> int:
        """Number of triangular faces."""
        return len(self.faces)

    def to_dict(self) -> dict:
        """Serialize to JSON-compatible dict."""
        return {
            "vertex_count": self.vertex_count,
            "face_count": self.face_count,
            "frequency": self.frequency,
            "vertices": [v.to_tuple() for v in self.vertices],
            "faces": list(self.faces),
        }


def _project_to_sphere(point: Point3D, radius: float = 1.0) -> Point3D:
    """Project a point onto a sphere of given radius."""
    mag = point.magnitude()
    if mag < 1e-12:
        return Point3D(0.0, 0.0, radius)
    scale = radius / mag
    return Point3D(point.x * scale, point.y * scale, point.z * scale)


def generate_icosahedron(radius: float = 1.0) -> IcosahedralMesh:
    """Generate a base icosahedron with 12 vertices and 20 triangular faces.

    The icosahedron is inscribed in a sphere of the given radius,
    using the golden-ratio construction.

    Args:
        radius: Radius of the circumscribing sphere. Default 1.0.

    Returns:
        IcosahedralMesh with 12 vertices and 20 faces.
    """
    phi = (1.0 + math.sqrt(5.0)) / 2.0  # golden ratio

    # 12 vertices of a regular icosahedron (before normalization)
    raw = [
        Point3D(-1, phi, 0),
        Point3D(1, phi, 0),
        Point3D(-1, -phi, 0),
        Point3D(1, -phi, 0),
        Point3D(0, -1, phi),
        Point3D(0, 1, phi),
        Point3D(0, -1, -phi),
        Point3D(0, 1, -phi),
        Point3D(phi, 0, -1),
        Point3D(phi, 0, 1),
        Point3D(-phi, 0, -1),
        Point3D(-phi, 0, 1),
    ]

    vertices = [_project_to_sphere(v, radius) for v in raw]

    # 20 triangular faces (vertex indices, CCW winding)
    faces = [
        (0, 11, 5),
        (0, 5, 1),
        (0, 1, 7),
        (0, 7, 10),
        (0, 10, 11),
        (1, 5, 9),
        (5, 11, 4),
        (11, 10, 2),
        (10, 7, 6),
        (7, 1, 8),
        (3, 9, 4),
        (3, 4, 2),
        (3, 2, 6),
        (3, 6, 8),
        (3, 8, 9),
        (4, 9, 5),
        (2, 4, 11),
        (6, 2, 10),
        (8, 6, 7),
        (9, 8, 1),
    ]

    return IcosahedralMesh(vertices=vertices, faces=faces, frequency=1)


def subdivide_mesh(
    mesh: IcosahedralMesh,
    frequency: int = 2,
    radius: float = 1.0,
) -> IcosahedralMesh:
    """Subdivide an icosahedral mesh to create a geodesic sphere.

    Each triangle is subdivided recursively by splitting edges at
    midpoints and projecting new vertices onto the sphere. This is
    repeated (frequency - mesh.frequency) times.

    Args:
        mesh: Source mesh to subdivide.
        frequency: Target subdivision frequency (must be >= mesh.frequency).
        radius: Sphere radius for projection.

    Returns:
        A new IcosahedralMesh at the requested frequency.

    Raises:
        ValueError: If frequency < mesh.frequency.
    """
    if frequency < mesh.frequency:
        raise ValueError(
            f"Target frequency ({frequency}) must be >= "
            f"source frequency ({mesh.frequency})"
        )

    vertices = list(mesh.vertices)
    faces = list(mesh.faces)
    current_freq = mesh.frequency

    while current_freq < frequency:
        midpoint_cache: dict[tuple[int, int], int] = {}
        new_faces: list[tuple[int, int, int]] = []

        def _get_midpoint(i1: int, i2: int) -> int:
            """Get or create midpoint vertex between two vertices."""
            key = (min(i1, i2), max(i1, i2))
            if key in midpoint_cache:
                return midpoint_cache[key]

            p1 = vertices[i1]
            p2 = vertices[i2]
            mid = Point3D(
                (p1.x + p2.x) / 2.0,
                (p1.y + p2.y) / 2.0,
                (p1.z + p2.z) / 2.0,
            )
            mid = _project_to_sphere(mid, radius)
            idx = len(vertices)
            vertices.append(mid)
            midpoint_cache[key] = idx
            return idx

        for a, b, c in faces:
            ab = _get_midpoint(a, b)
            bc = _get_midpoint(b, c)
            ca = _get_midpoint(c, a)

            new_faces.append((a, ab, ca))
            new_faces.append((b, bc, ab))
            new_faces.append((c, ca, bc))
            new_faces.append((ab, bc, ca))

        faces = new_faces
        current_freq += 1

    return IcosahedralMesh(vertices=vertices, faces=faces, frequency=frequency)


def geodesic_distance(
    p1: Point3D,
    p2: Point3D,
    radius: float = 1.0,
) -> float:
    """Compute geodesic (great-circle) distance between two points on a sphere.

    Both points are projected onto the sphere before computing the arc length.

    Args:
        p1: First point.
        p2: Second point.
        radius: Sphere radius.

    Returns:
        Arc-length distance on the sphere surface.
    """
    # Normalize to unit sphere
    n1 = p1.normalize()
    n2 = p2.normalize()

    # Clamp dot product to [-1, 1] for numerical safety
    dot = max(-1.0, min(1.0, n1.dot(n2)))
    angle = math.acos(dot)

    return radius * angle


__all__ = [
    "IcosahedralMesh",
    "generate_icosahedron",
    "geodesic_distance",
    "subdivide_mesh",
]
