"""Geodesic Bounding Volume Hierarchy (BVH) for spatial partitioning.

Provides an O(log N) ray intersection over high-resolution geodesic meshes
like the IcosahedralMesh, leveraging AABB trees.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

from codomyrmex.spatial.three_d.engine_3d import Vector3D
from codomyrmex.spatial.three_d.scene_graph import AABB

if TYPE_CHECKING:
    from codomyrmex.spatial.coordinates import IcosahedralMesh, Point3D


@dataclass
class BVHNode:
    """A node in the Bounding Volume Hierarchy tree for efficient spatial queries."""

    bounds: AABB
    left: Optional[BVHNode] = None
    right: Optional[BVHNode] = None
    faces: Optional[list[int]] = None


def ray_triangle_intersect(
    origin: Vector3D, direction: Vector3D, v0: Point3D, v1: Point3D, v2: Point3D
) -> float | None:
    """Möller–Trumbore ray-triangle intersection algorithm."""
    epsilon = 1e-8
    edge1 = Vector3D(v1.x - v0.x, v1.y - v0.y, v1.z - v0.z)
    edge2 = Vector3D(v2.x - v0.x, v2.y - v0.y, v2.z - v0.z)

    h = Vector3D(
        direction.y * edge2.z - direction.z * edge2.y,
        direction.z * edge2.x - direction.x * edge2.z,
        direction.x * edge2.y - direction.y * edge2.x,
    )

    a = edge1.x * h.x + edge1.y * h.y + edge1.z * h.z
    if -epsilon < a < epsilon:
        return None

    f = 1.0 / a
    s = Vector3D(origin.x - v0.x, origin.y - v0.y, origin.z - v0.z)
    u = f * (s.x * h.x + s.y * h.y + s.z * h.z)
    if u < 0.0 or u > 1.0:
        return None

    q = Vector3D(
        s.y * edge1.z - s.z * edge1.y,
        s.z * edge1.x - s.x * edge1.z,
        s.x * edge1.y - s.y * edge1.x,
    )
    v = f * (direction.x * q.x + direction.y * q.y + direction.z * q.z)
    if v < 0.0 or u + v > 1.0:
        return None

    t = f * (edge2.x * q.x + edge2.y * q.y + edge2.z * q.z)
    if t > epsilon:
        return t
    return None


def _compute_face_centroid(mesh: IcosahedralMesh, face_idx: int) -> Vector3D:
    """Compute the geographic centroid of a single triangular face."""
    v0 = mesh.vertices[mesh.faces[face_idx][0]]
    v1 = mesh.vertices[mesh.faces[face_idx][1]]
    v2 = mesh.vertices[mesh.faces[face_idx][2]]
    return Vector3D(
        (v0.x + v1.x + v2.x) / 3.0,
        (v0.y + v1.y + v2.y) / 3.0,
        (v0.z + v1.z + v2.z) / 3.0,
    )


def _compute_bounds(mesh: IcosahedralMesh, face_indices: list[int]) -> AABB:
    """Compute an AABB encompassing the given faces."""
    if not face_indices:
        return AABB(Vector3D(0.0, 0.0, 0.0), Vector3D(0.0, 0.0, 0.0))

    min_x = min_y = min_z = float("inf")
    max_x = max_y = max_z = float("-inf")
    for f in face_indices:
        for vi in mesh.faces[f]:
            v = mesh.vertices[vi]
            min_x, max_x = min(min_x, v.x), max(max_x, v.x)
            min_y, max_y = min(min_y, v.y), max(max_y, v.y)
            min_z, max_z = min(min_z, v.z), max(max_z, v.z)

    return AABB(Vector3D(min_x, min_y, min_z), Vector3D(max_x, max_y, max_z))


def build_bvh(
    mesh: IcosahedralMesh, face_indices: list[int] | None = None, max_faces: int = 8
) -> BVHNode:
    """Recursively construct a Bounding Volume Hierarchy over a geodesic mesh.

    Args:
        mesh: The source spatial structural mesh.
        face_indices: Optional list of faces to partition (defaults to all).
        max_faces: The maximum number of triangles an AABB leaf node can hold.

    Returns:
        The root BVHNode containing the complete spatially-partitioned tree.
    """
    if face_indices is None:
        face_indices = list(range(len(mesh.faces)))

    bounds = _compute_bounds(mesh, face_indices)

    # Leaf node condition
    if len(face_indices) <= max_faces:
        return BVHNode(bounds=bounds, faces=face_indices)

    # Internal node: Split along longest spatial axis
    dx = bounds.max_corner.x - bounds.min_corner.x
    dy = bounds.max_corner.y - bounds.min_corner.y
    dz = bounds.max_corner.z - bounds.min_corner.z

    axis = 0 if dx > dy and dx > dz else (1 if dy > dz else 2)

    def axis_key(f_idx: int) -> float:
        c = _compute_face_centroid(mesh, f_idx)
        return c.x if axis == 0 else (c.y if axis == 1 else c.z)

    # Sort and bisect to maintain logarithmic depth
    face_indices.sort(key=axis_key)
    mid = len(face_indices) // 2

    # Safe fallback if split degenerate bounds occur
    if mid == 0 or mid == len(face_indices):
        return BVHNode(bounds=bounds, faces=face_indices)

    left = build_bvh(mesh, face_indices[:mid], max_faces)
    right = build_bvh(mesh, face_indices[mid:], max_faces)

    return BVHNode(bounds=bounds, left=left, right=right)


def ray_intersect_bvh(
    bvh: BVHNode, mesh: IcosahedralMesh, origin: Vector3D, direction: Vector3D
) -> float | None:
    """Traverse the Geodesic BVH to perform logarithmic-time collision detection.

    Args:
        bvh: The root or current testing Bounding Volume Hierarchy node.
        mesh: The structural mesh providing vertex coordinate data.
        origin: The start point of the ray cast.
        direction: The non-normalized direction vector of the ray.

    Returns:
        The parametric distance `t` to the closest intersecting triangle face,
        or None if no collision occurs.
    """
    # 1. Broad Phase AABB cull
    hit_t = bvh.bounds.ray_intersect(origin, direction)
    if hit_t is None:
        return None

    # 2. Narrow Phase leaf node
    if bvh.faces is not None:
        closest_t = float("inf")
        for f in bvh.faces:
            face = mesh.faces[f]
            v0, v1, v2 = mesh.vertices[face[0]], mesh.vertices[face[1]], mesh.vertices[face[2]]
            t = ray_triangle_intersect(origin, direction, v0, v1, v2)
            if t is not None and t < closest_t:
                closest_t = t
        return closest_t if closest_t != float("inf") else None

    # 3. Recursive branch traversal
    t_left = ray_intersect_bvh(bvh.left, mesh, origin, direction) if bvh.left else None
    t_right = ray_intersect_bvh(bvh.right, mesh, origin, direction) if bvh.right else None

    if t_left is not None and t_right is not None:
        return min(t_left, t_right)
    return t_left if t_left is not None else t_right
