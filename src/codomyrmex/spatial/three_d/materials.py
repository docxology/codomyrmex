"""Materials and mesh loading primitives for the local 3D engine.

The engine is intentionally renderer-agnostic: these classes describe scene
data without importing an OpenGL, Vulkan, or native windowing backend.  That
makes them useful in headless tests and lets a renderer consume the same
validated data structure later.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .engine_3d import Vector3D


@dataclass
class Material3D:
    """Renderer-neutral surface properties for a 3D object."""

    name: str = "Material"
    diffuse_color: Vector3D = field(default_factory=lambda: Vector3D(1.0, 1.0, 1.0))
    specular_color: Vector3D = field(default_factory=lambda: Vector3D(1.0, 1.0, 1.0))
    shininess: float = 32.0
    texture_name: str | None = None

    def __post_init__(self) -> None:
        """Reject invalid material parameters before a renderer sees them."""
        if not self.name.strip():
            raise ValueError("Material name must not be empty")
        if not math.isfinite(self.shininess) or self.shininess < 0.0:
            raise ValueError("Material shininess must be a finite non-negative number")


@dataclass(frozen=True)
class MeshData:
    """Validated, renderer-neutral mesh geometry."""

    vertices: tuple[Vector3D, ...]
    faces: tuple[tuple[int, ...], ...] = ()

    def __post_init__(self) -> None:
        """Validate face indices against the immutable vertex collection."""
        vertex_count = len(self.vertices)
        for face in self.faces:
            if len(face) < 3:
                raise ValueError("Mesh faces must contain at least three indices")
            if any(index < 0 or index >= vertex_count for index in face):
                raise ValueError("Mesh face index is outside the vertex collection")


class MeshLoader:
    """Load a small, deterministic subset of OBJ and JSON mesh files.

    No renderer or optional graphics dependency is required.  OBJ files may
    contain vertex (``v``) and face (``f``) records; JSON files must contain a
    ``vertices`` list and may contain a ``faces`` list.  This deliberately
    narrow contract is sufficient for headless scene construction and gives
    callers a clear error for unsupported formats.
    """

    def load(self, path: str | Path) -> MeshData:
        """Load *path* and return validated mesh data."""
        mesh_path = Path(path)
        if not mesh_path.is_file():
            raise FileNotFoundError(mesh_path)
        suffix = mesh_path.suffix.lower()
        if suffix == ".obj":
            return self._load_obj(mesh_path)
        if suffix == ".json":
            return self._load_json(mesh_path)
        raise ValueError(f"Unsupported mesh format: {mesh_path.suffix or '<none>'}")

    @staticmethod
    def _vector(values: Any) -> Vector3D:
        if not isinstance(values, (list, tuple)) or len(values) != 3:
            raise ValueError("Mesh vertices must be three-element arrays")
        coordinates = tuple(float(value) for value in values)
        if not all(math.isfinite(value) for value in coordinates):
            raise ValueError("Mesh vertices must contain finite numbers")
        return Vector3D(*coordinates)

    def _load_json(self, path: Path) -> MeshData:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON mesh: {path}") from exc
        if not isinstance(payload, dict):
            raise ValueError("JSON mesh must contain an object")
        raw_vertices = payload.get("vertices")
        raw_faces = payload.get("faces", [])
        if not isinstance(raw_vertices, list) or not isinstance(raw_faces, list):
            raise ValueError("JSON mesh requires list-valued vertices and faces")
        vertices = tuple(self._vector(values) for values in raw_vertices)
        faces = tuple(
            tuple(int(index) for index in face)
            for face in raw_faces
            if isinstance(face, list)
        )
        if len(faces) != len(raw_faces):
            raise ValueError("JSON mesh faces must be lists of indices")
        return MeshData(vertices=vertices, faces=faces)

    def _load_obj(self, path: Path) -> MeshData:
        vertices: list[Vector3D] = []
        faces: list[tuple[int, ...]] = []
        for line_number, raw_line in enumerate(
            path.read_text(encoding="utf-8").splitlines(), start=1
        ):
            line = raw_line.split("#", 1)[0].strip()
            if not line:
                continue
            parts = line.split()
            if parts[0] == "v":
                if len(parts) != 4:
                    raise ValueError(f"Invalid OBJ vertex at line {line_number}")
                vertices.append(self._vector(parts[1:]))
            elif parts[0] == "f":
                if len(parts) < 4:
                    raise ValueError(
                        f"OBJ face needs three vertices at line {line_number}"
                    )
                indices: list[int] = []
                for token in parts[1:]:
                    raw_index = token.split("/", 1)[0]
                    try:
                        index = int(raw_index)
                    except ValueError as exc:
                        raise ValueError(
                            f"Invalid OBJ face index at line {line_number}"
                        ) from exc
                    indices.append(index - 1 if index > 0 else len(vertices) + index)
                faces.append(tuple(indices))
        return MeshData(vertices=tuple(vertices), faces=tuple(faces))


__all__ = ["Material3D", "MeshData", "MeshLoader"]
