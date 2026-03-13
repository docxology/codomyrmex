"""AABB scene graph with spatial queries.

Provides a hierarchical scene graph built on axis-aligned bounding boxes (AABB)
for efficient region queries, point containment tests, and ray casting.

Builds on :class:`~codomyrmex.spatial.three_d.engine_3d.Object3D` and
:class:`~codomyrmex.spatial.three_d.engine_3d.Vector3D`.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

from codomyrmex.logging_monitoring import get_logger
from codomyrmex.spatial.three_d.engine_3d import Object3D, Vector3D

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# AABB
# ---------------------------------------------------------------------------


@dataclass
class AABB:
    """Axis-aligned bounding box.

    Attributes:
        min_corner: Minimum corner of the box.
        max_corner: Maximum corner of the box.
    """

    min_corner: Vector3D = field(default_factory=lambda: Vector3D(0.0, 0.0, 0.0))
    max_corner: Vector3D = field(default_factory=lambda: Vector3D(1.0, 1.0, 1.0))

    # -- predicates ----------------------------------------------------------

    def contains(self, point: Vector3D) -> bool:
        """Return *True* if *point* is inside (or on the boundary of) this AABB."""
        return (
            self.min_corner.x <= point.x <= self.max_corner.x
            and self.min_corner.y <= point.y <= self.max_corner.y
            and self.min_corner.z <= point.z <= self.max_corner.z
        )

    def intersects(self, other: AABB) -> bool:
        """Return *True* if this AABB overlaps with *other*."""
        return (
            self.min_corner.x <= other.max_corner.x
            and self.max_corner.x >= other.min_corner.x
            and self.min_corner.y <= other.max_corner.y
            and self.max_corner.y >= other.min_corner.y
            and self.min_corner.z <= other.max_corner.z
            and self.max_corner.z >= other.min_corner.z
        )

    # -- metrics -------------------------------------------------------------

    def volume(self) -> float:
        """Compute the volume of the bounding box."""
        dx = max(0.0, self.max_corner.x - self.min_corner.x)
        dy = max(0.0, self.max_corner.y - self.min_corner.y)
        dz = max(0.0, self.max_corner.z - self.min_corner.z)
        return dx * dy * dz

    def center(self) -> Vector3D:
        """Return the center of the bounding box."""
        return Vector3D(
            (self.min_corner.x + self.max_corner.x) / 2,
            (self.min_corner.y + self.max_corner.y) / 2,
            (self.min_corner.z + self.max_corner.z) / 2,
        )

    # -- ray intersection ----------------------------------------------------

    def ray_intersect(self, origin: Vector3D, direction: Vector3D) -> float | None:
        """Slab-method ray–AABB intersection.

        Returns the parametric *t* of the nearest intersection, or *None* if
        the ray misses the box.
        """
        t_min = -math.inf
        t_max = math.inf

        for axis in ("x", "y", "z"):
            o = getattr(origin, axis)
            d = getattr(direction, axis)
            lo = getattr(self.min_corner, axis)
            hi = getattr(self.max_corner, axis)

            if abs(d) < 1e-12:
                if o < lo or o > hi:
                    return None
            else:
                t1 = (lo - o) / d
                t2 = (hi - o) / d
                if t1 > t2:
                    t1, t2 = t2, t1
                t_min = max(t_min, t1)
                t_max = min(t_max, t2)
                if t_min > t_max:
                    return None

        return t_min if t_min >= 0 else (t_max if t_max >= 0 else None)

    # -- serialization -------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "min": [self.min_corner.x, self.min_corner.y, self.min_corner.z],
            "max": [self.max_corner.x, self.max_corner.y, self.max_corner.z],
        }


# ---------------------------------------------------------------------------
# Scene Node
# ---------------------------------------------------------------------------


@dataclass
class SceneNode:
    """A node in the scene graph.

    Attributes:
        name: Human-readable label.
        obj: Optional attached 3D object.
        bounds: AABB for this node (world space).
        parent: Parent node (*None* for root).
        children: Child nodes.
    """

    name: str = "node"
    obj: Object3D | None = None
    bounds: AABB = field(default_factory=AABB)
    parent: SceneNode | None = field(default=None, repr=False)
    children: list[SceneNode] = field(default_factory=list)

    def add_child(self, child: SceneNode) -> None:
        """Attach *child* under this node."""
        child.parent = self
        self.children.append(child)

    def remove_child(self, child: SceneNode) -> bool:
        """Detach *child*. Returns *True* if found and removed."""
        if child in self.children:
            self.children.remove(child)
            child.parent = None
            return True
        return False

    @property
    def depth(self) -> int:
        """Distance from root."""
        d = 0
        node = self.parent
        while node is not None:
            d += 1
            node = node.parent
        return d

    def to_dict(self) -> dict[str, Any]:
        """Serialize this node (non-recursive)."""
        return {
            "name": self.name,
            "bounds": self.bounds.to_dict(),
            "children_count": len(self.children),
            "has_object": self.obj is not None,
        }


# ---------------------------------------------------------------------------
# Ray-cast hit
# ---------------------------------------------------------------------------


@dataclass
class RayHit:
    """Result of a ray cast against the scene graph."""

    node: SceneNode
    t: float  # parametric distance along ray

    def to_dict(self) -> dict[str, Any]:
        return {"node": self.node.name, "t": round(self.t, 6)}


# ---------------------------------------------------------------------------
# Scene Graph
# ---------------------------------------------------------------------------


class SceneGraph:
    """Hierarchical scene graph with AABB spatial queries.

    Usage::

        sg = SceneGraph()
        n = SceneNode("box", bounds=AABB(Vector3D(0,0,0), Vector3D(1,1,1)))
        sg.add_node(n)
        hits = sg.query_point(Vector3D(0.5, 0.5, 0.5))
        assert len(hits) == 1

    """

    def __init__(self) -> None:
        self._root = SceneNode(name="__root__")
        self._nodes: dict[str, SceneNode] = {}

    # -- mutators ------------------------------------------------------------

    def add_node(self, node: SceneNode, parent: SceneNode | None = None) -> None:
        """Add *node* to the graph under *parent* (or root)."""
        target = parent if parent is not None else self._root
        target.add_child(node)
        self._nodes[node.name] = node
        logger.debug("SceneGraph: added node '%s'", node.name)

    def remove_node(self, node: SceneNode) -> bool:
        """Remove *node* (and its subtree) from the graph."""
        if node.parent is not None:
            node.parent.remove_child(node)
        removed = self._collect_names(node)
        for name in removed:
            self._nodes.pop(name, None)
        return len(removed) > 0

    # -- queries -------------------------------------------------------------

    def query_region(self, region: AABB) -> list[SceneNode]:
        """Return all nodes whose AABB intersects *region*."""
        results: list[SceneNode] = []
        self._walk(self._root, lambda n: n.bounds.intersects(region), results)
        return results

    def query_point(self, point: Vector3D) -> list[SceneNode]:
        """Return all nodes whose AABB contains *point*."""
        results: list[SceneNode] = []
        self._walk(self._root, lambda n: n.bounds.contains(point), results)
        return results

    def ray_cast(self, origin: Vector3D, direction: Vector3D) -> list[RayHit]:
        """Cast a ray and return sorted hits (nearest first)."""
        hits: list[RayHit] = []
        for node in self._nodes.values():
            t = node.bounds.ray_intersect(origin, direction)
            if t is not None:
                hits.append(RayHit(node=node, t=t))
        hits.sort(key=lambda h: h.t)
        return hits

    # -- accessors -----------------------------------------------------------

    @property
    def root(self) -> SceneNode:
        """Return the root sentinel node."""
        return self._root

    @property
    def node_count(self) -> int:
        """Number of user-added nodes."""
        return len(self._nodes)

    def get_node(self, name: str) -> SceneNode | None:
        """Look up a node by name."""
        return self._nodes.get(name)

    # -- internals -----------------------------------------------------------

    @staticmethod
    def _walk(
        node: SceneNode,
        predicate: Any,
        results: list[SceneNode],
    ) -> None:
        """Depth-first walk collecting nodes matching *predicate*."""
        for child in node.children:
            if predicate(child):
                results.append(child)
            SceneGraph._walk(child, predicate, results)

    @staticmethod
    def _collect_names(node: SceneNode) -> list[str]:
        """Collect names of *node* and all descendants."""
        names = [node.name]
        for child in node.children:
            names.extend(SceneGraph._collect_names(child))
        return names


__all__ = [
    "AABB",
    "RayHit",
    "SceneGraph",
    "SceneNode",
]
